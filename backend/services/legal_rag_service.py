"""
Legal RAG Service — Hybrid retrieval with legal-structured output.
Combines vector search + PageIndex + legal LLM for traceable legal answers.
"""

from backend.services.legal_llm_service import LegalLLMService
from backend.services.vectorless_rag_service import VectorlessRAGService
from backend.database.vector_db import VectorDB


class LegalRAGService:
    def __init__(self, vector_db: VectorDB):
        self.legal_llm = LegalLLMService()
        self.vector_db = vector_db
        self.vectorless_rag = None

    def _get_vectorless_rag(self):
        if self.vectorless_rag is None:
            self.vectorless_rag = VectorlessRAGService()
        return self.vectorless_rag

    def ask_legal_question(
        self,
        question: str,
        filter_metadata: dict = None,
        pageindex_doc_id: str = None,
        doc_names: list[str] = None
    ) -> dict:
        """
        Hybrid Legal RAG:
        1. PageIndex (structural/tree-based) retrieval if available
        2. ChromaDB vector (semantic) retrieval
        3. Legal LLM generates structured legal answer with citations
        """
        all_contexts = []
        sources = []

        # 1. Vectorless / PageIndex retrieval (structural, page-level)
        if pageindex_doc_id:
            print(f"[LegalRAG] PageIndex retrieval for doc: {pageindex_doc_id}")
            try:
                pi_contexts = self._get_vectorless_rag().retrieve_context(pageindex_doc_id, question)
                if pi_contexts:
                    all_contexts.extend(pi_contexts)
                    sources.append({
                        "type": "document",
                        "mode": "structural",
                        "doc_id": pageindex_doc_id,
                        "count": len(pi_contexts)
                    })
                    print(f"[LegalRAG] PageIndex returned {len(pi_contexts)} blocks")
            except Exception as e:
                print(f"[LegalRAG] PageIndex failed: {e}")

        # 2. Vector / semantic retrieval
        print(f"[LegalRAG] Vector retrieval...")
        hits = self.vector_db.query(question, top_k=8, filter_metadata=filter_metadata)
        if hits:
            for hit in hits:
                all_contexts.append(hit["content"])
                sources.append({
                    "type": "document",
                    "mode": "semantic",
                    "doc_id": hit["metadata"].get("doc_id"),
                    "chunk_index": hit["metadata"].get("chunk_index"),
                    "relevance_score": round(1 - hit.get("distance", 0), 3)
                })

        if not all_contexts:
            # No document context — answer from general legal knowledge
            print("[LegalRAG] No document context found, using general legal knowledge")
            answer = self.legal_llm.answer_general_legal_question(question)
            return {
                "answer": answer,
                "sources": [{"type": "general_knowledge", "note": "No uploaded documents matched this query"}],
                "context_used": False
            }

        # Deduplicate
        unique_contexts = list(dict.fromkeys(all_contexts))
        context_str = "\n\n---\n\n".join(unique_contexts)
        print(f"[LegalRAG] Generating legal answer from {len(unique_contexts)} context blocks")

        answer = self.legal_llm.answer_legal_question(question, context_str, doc_names=doc_names)

        return {
            "answer": answer,
            "sources": sources,
            "context_used": True,
            "context_blocks": len(unique_contexts)
        }

    def summarize_legal_document(self, filter_metadata: dict, doc_name: str = "Document") -> dict:
        """Generate a structured legal summary of a document."""
        hits = self.vector_db.query("", top_k=15, filter_metadata=filter_metadata)
        if not hits:
            return {"summary": "Document not found or empty.", "doc_name": doc_name}

        full_text = "\n\n".join([hit["content"] for hit in hits])
        summary = self.legal_llm.summarize_legal_document(full_text[:12000], doc_name=doc_name)
        return {"summary": summary, "doc_name": doc_name}

    def extract_clause(self, filter_metadata: dict, clause_type: str, doc_name: str = "Document") -> dict:
        """Extract a specific clause from a document."""
        hits = self.vector_db.query(clause_type, top_k=10, filter_metadata=filter_metadata)
        if not hits:
            return {"result": "Document not found or clause not located.", "clause_type": clause_type}

        full_text = "\n\n".join([hit["content"] for hit in hits])
        result = self.legal_llm.extract_clause(full_text[:12000], clause_type, doc_name=doc_name)
        return {"result": result, "clause_type": clause_type, "doc_name": doc_name}

    def analyze_risks(self, filter_metadata: dict, doc_name: str = "Document") -> dict:
        """Perform legal risk analysis on a document."""
        hits = self.vector_db.query("risk liability obligation penalty", top_k=15, filter_metadata=filter_metadata)
        if not hits:
            return {"analysis": "Document not found or empty.", "doc_name": doc_name}

        full_text = "\n\n".join([hit["content"] for hit in hits])
        analysis = self.legal_llm.analyze_risks(full_text[:12000], doc_name=doc_name)
        return {"analysis": analysis, "doc_name": doc_name}

    def compare_documents(
        self,
        filter1: dict, name1: str,
        filter2: dict, name2: str
    ) -> dict:
        """Compare two legal documents."""
        hits1 = self.vector_db.query("", top_k=10, filter_metadata=filter1)
        hits2 = self.vector_db.query("", top_k=10, filter_metadata=filter2)

        if not hits1 or not hits2:
            return {"comparison": "One or both documents not found.", "doc1": name1, "doc2": name2}

        text1 = "\n\n".join([h["content"] for h in hits1])
        text2 = "\n\n".join([h["content"] for h in hits2])

        comparison = self.legal_llm.compare_documents(text1, name1, text2, name2)
        return {"comparison": comparison, "doc1": name1, "doc2": name2}
