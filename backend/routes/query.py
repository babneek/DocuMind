from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys
from pathlib import Path
# Add parent directory to path so we can import from root-level modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.postgres import get_db
from models.document import Document
from services.rag_service import RAGService
from services.llm_service import LLMService
from services.cache_service import get_cache_manager
from database.vector_db import VectorDB
from .auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/query", tags=["Query"])

llm_service = LLMService()
vector_db = VectorDB()
rag_service = RAGService(llm_service, vector_db)
cache_manager = get_cache_manager()

class QueryRequest(BaseModel):
    query: str
    doc_id: int = None

class SummarizeRequest(BaseModel):
    doc_id: int

class ExtractionRequest(BaseModel):
    doc_id: int
    schema_description: str

def check_doc_access(doc_id: int, user_id: int, db: Session):
    if doc_id:
        doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user_id).first()
        if not doc:
            raise HTTPException(status_code=403, detail="Document access denied")
    return True

@router.post("/ask")
async def ask_question(request: QueryRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    RAG: Ask a question about documents for current user with response caching.
    """
    # Check cache first
    cached_response = cache_manager.get_response(request.query, request.doc_id)
    if cached_response:
        print(f"[CACHE] Returning cached response for query: {request.query[:50]}...")
        return cached_response
    
    pageindex_id = None
    if request.doc_id:
        doc = db.query(Document).filter(Document.id == request.doc_id).first()
        if doc and doc.pageindex_doc_id:
            pageindex_id = doc.pageindex_doc_id
            
    # Filter by current user's documents if not scoped to one doc
    if not request.doc_id:
        # Get all user doc IDs
        user_doc_ids = [d.id for d in db.query(Document.id).filter(Document.user_id == current_user.id).all()]
        if not user_doc_ids:
            return {"answer": "You have no documents uploaded to search from.", "sources": []}
        filter_meta = {"doc_id": {"$in": user_doc_ids}}
    else:
        filter_meta = {"doc_id": request.doc_id}
        
    result = rag_service.ask_document_question(request.query, filter_metadata=filter_meta, pageindex_doc_id=pageindex_id)
    
    # Cache the response
    cache_manager.set_response(request.query, result, request.doc_id)
    
    return result

@router.post("/summarize")
async def summarize(request: SummarizeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_doc_access(request.doc_id, current_user.id, db)
    filter_meta = {"doc_id": request.doc_id}
    summary = rag_service.summarize_document(filter_metadata=filter_meta)
    return {"summary": summary}

@router.post("/extract")
async def extract(request: ExtractionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_doc_access(request.doc_id, current_user.id, db)
    filter_meta = {"doc_id": request.doc_id}
    data = rag_service.extract_structured_from_document(request.schema_description, filter_metadata=filter_meta)
    return {"data": data}
