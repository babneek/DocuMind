from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database.postgres import get_db
from backend.models.document import Document
from backend.services.legal_rag_service import LegalRAGService
from backend.services.rag_service import RAGService
from backend.services.llm_service import LLMService
from backend.services.cache_service import get_cache_manager
from backend.database.vector_db import VectorDB
from .auth import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/api/query", tags=["Query"])

vector_db = VectorDB()
llm_service = LLMService()
rag_service = RAGService(llm_service, vector_db)       # legacy fallback
legal_rag = LegalRAGService(vector_db)                 # legal-aware service
cache_manager = get_cache_manager()


# ── Pydantic models ──────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    doc_id: Optional[int] = None

class SummarizeRequest(BaseModel):
    doc_id: int

class ClauseRequest(BaseModel):
    doc_id: int
    clause_type: str  # e.g. "termination clause", "indemnity clause"

class RiskRequest(BaseModel):
    doc_id: int

class CompareRequest(BaseModel):
    doc_id_1: int
    doc_id_2: int

class ExtractionRequest(BaseModel):
    doc_id: int
    schema_description: str


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_doc_or_403(doc_id: int, user_id: int, db: Session) -> Document:
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user_id).first()
    if not doc:
        raise HTTPException(status_code=403, detail="Document not found or access denied")
    return doc


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/ask")
async def ask_question(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Legal RAG: Ask any legal question about uploaded documents.
    Returns structured legal answer with citations and confidence level.
    """
    cached = cache_manager.get_response(request.query, request.doc_id)
    if cached:
        print(f"[CACHE] Returning cached legal response")
        return cached

    pageindex_id = None
    doc_names = []

    if request.doc_id:
        doc = get_doc_or_403(request.doc_id, current_user.id, db)
        pageindex_id = doc.pageindex_doc_id
        doc_names = [doc.file_name]
        filter_meta = {"doc_id": request.doc_id}
    else:
        user_docs = db.query(Document).filter(Document.user_id == current_user.id).all()
        if not user_docs:
            return {
                "answer": "**Answer:** No documents found.\n\n**Explanation:** You have not uploaded any legal documents yet. Please upload a document to begin analysis.\n\n**Sources:** None\n\n**Confidence:** Low",
                "sources": [],
                "context_used": False
            }
        doc_ids = [d.id for d in user_docs]
        doc_names = [d.file_name for d in user_docs]
        filter_meta = {"doc_id": {"$in": doc_ids}}

    result = legal_rag.ask_legal_question(
        request.query,
        filter_metadata=filter_meta,
        pageindex_doc_id=pageindex_id,
        doc_names=doc_names
    )

    cache_manager.set_response(request.query, result, request.doc_id)
    return result


@router.post("/summarize")
async def summarize(
    request: SummarizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a structured legal summary of a document."""
    doc = get_doc_or_403(request.doc_id, current_user.id, db)
    result = legal_rag.summarize_legal_document(
        filter_metadata={"doc_id": request.doc_id},
        doc_name=doc.file_name
    )
    return result


@router.post("/extract-clause")
async def extract_clause(
    request: ClauseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Extract and analyze a specific clause from a legal document."""
    doc = get_doc_or_403(request.doc_id, current_user.id, db)
    result = legal_rag.extract_clause(
        filter_metadata={"doc_id": request.doc_id},
        clause_type=request.clause_type,
        doc_name=doc.file_name
    )
    return result


@router.post("/analyze-risks")
async def analyze_risks(
    request: RiskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Perform a legal risk analysis on a document."""
    doc = get_doc_or_403(request.doc_id, current_user.id, db)
    result = legal_rag.analyze_risks(
        filter_metadata={"doc_id": request.doc_id},
        doc_name=doc.file_name
    )
    return result


@router.post("/compare")
async def compare_documents(
    request: CompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare two legal documents side by side."""
    doc1 = get_doc_or_403(request.doc_id_1, current_user.id, db)
    doc2 = get_doc_or_403(request.doc_id_2, current_user.id, db)
    result = legal_rag.compare_documents(
        filter1={"doc_id": request.doc_id_1}, name1=doc1.file_name,
        filter2={"doc_id": request.doc_id_2}, name2=doc2.file_name
    )
    return result


@router.post("/extract")
async def extract(
    request: ExtractionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Extract structured data from a document (legacy endpoint)."""
    get_doc_or_403(request.doc_id, current_user.id, db)
    filter_meta = {"doc_id": request.doc_id}
    data = rag_service.extract_structured_from_document(request.schema_description, filter_metadata=filter_meta)
    return {"data": data}
