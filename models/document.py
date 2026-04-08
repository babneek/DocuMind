from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.postgres import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    pageindex_doc_id = Column(String, nullable=True) # For Vectorless RAG
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="processing") # processing, ready, error

    # Relationships
    owner = relationship("User", back_populates="documents")
    chunks = relationship("ChunkMetadata", back_populates="document")

class ChunkMetadata(Base):
    """
    Metadata for chunks stored in Postgres (to match vector DB highlights).
    """
    __tablename__ = "chunk_metadata"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    text = Column(Text)
    chunk_index = Column(Integer)

    # Relationships
    document = relationship("Document", back_populates="chunks")
