from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import shutil
import os
import sys
from pathlib import Path
# Add parent directory to path so we can import from root-level modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.postgres import get_db, SessionLocal
from models.document import Document
from services.ingestion_service import IngestionService
from database.vector_db import VectorDB
from .auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/upload", tags=["Upload"])
ingestion_service = IngestionService()
vector_db = VectorDB()


def _get_pageindex_service():
    from services.pageindex_service import PageIndexService
    return PageIndexService()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process a document for the current user.
    """
    file_location = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file.filename}")
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    doc_record = Document(
        user_id=current_user.id,
        file_name=file.filename,
        file_type=file.content_type or "text/plain",
        status="processing"
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)
    
    background_tasks.add_task(process_document_task, doc_record.id, file_location)
    
    return {"id": doc_record.id, "filename": file.filename, "status": "processing"}

async def process_document_task(doc_id: int, file_location: str):
    print(f"[Worker] Processing document {doc_id} at {file_location}")
    ext = os.path.splitext(file_location)[1].lower()
    
    text = ""
    try:
        if ext == ".pdf":
             text = ingestion_service.extract_text_from_pdf(file_location)
        elif ext == ".docx":
            text = ingestion_service.extract_text_from_docx(file_location)
        elif ext == ".epub":
            text = ingestion_service.extract_text_from_epub(file_location)
        else:
            with open(file_location, "r", encoding="utf-8") as f:
                text = f.read()

        chunks = ingestion_service.chunk_by_sections(text)
        metadatas = [{"doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
        ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
        vector_db.add_documents(chunks, metadatas, ids)
        
        pageindex_id = None
        if ext == ".pdf":
            try:
                print(f"[Worker] Indexing document with PageIndex: {file_location}")
                pageindex_service = _get_pageindex_service()
                pageindex_id = pageindex_service.index_document(file_location)
                print(f"[Worker] PageIndex local doc id: {pageindex_id}")
            except Exception as pi_err:
                print(f"[Warn] PageIndex indexing failed: {pi_err}")

        with SessionLocal() as db:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.status = "ready"
                if pageindex_id:
                    doc.pageindex_doc_id = pageindex_id
                db.commit()
    except Exception as e:
        print(f"[Error] Task failed for {doc_id}: {e}")
        with SessionLocal() as db:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.status = f"error: {str(e)[:50]}"
                db.commit()
