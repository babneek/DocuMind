from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
from pathlib import Path
# Add parent directory to path so we can import from root-level modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.postgres import get_db
from models.document import Document
from database.vector_db import VectorDB
from .auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/documents", tags=["Documents"])
vector_db = VectorDB()

@router.get("/")
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    List all uploaded documents for the current user.
    """
    docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    return docs

@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete a document for the current user.
    """
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found or access denied")
        
    vector_db.delete_by_metadata({"doc_id": doc_id})
    db.delete(doc)
    db.commit()
    
    return {"message": "Document deleted successfully"}
