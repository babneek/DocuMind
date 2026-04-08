from services.llm_service import LLMService
from services.vectorless_rag_service import VectorlessRAGService
from database.vector_db import VectorDB

class RAGService:
    def __init__(self, llm_service: LLMService, vector_db: VectorDB):
        self.llm_service = llm_service
        self.vector_db = vector_db
        self.vectorless_rag = None

    def _get_vectorless_rag(self):
        if self.vectorless_rag is None:
            self.vectorless_rag = VectorlessRAGService()
        return self.vectorless_rag

    def ask_document_question(self, question: str, filter_metadata: dict = None, pageindex_doc_id: str = None):
        """
        Perform Hybrid RAG: Retrieve context from both Vector (Semantic) and Vectorless (Structural) in parallel.
        """
        all_contexts = []
        sources = []

        # 1. Vectorless Retrieval (PageIndex - Reasoning/Tree based) is primary when available.
        if pageindex_doc_id:
            print(f"[RAG] Retrieving Vectorless context for {pageindex_doc_id}")
            pi_contexts = self._get_vectorless_rag().retrieve_context(pageindex_doc_id, question)
            if pi_contexts:
                all_contexts.extend(pi_contexts)
                sources.append({"doc_id": pageindex_doc_id, "mode": "vectorless", "count": len(pi_contexts)})
                print(f"[RAG] PageIndex returned {len(pi_contexts)} context blocks, using it first.")
            else:
                print("[RAG] PageIndex returned no context, falling back to vector retrieval.")

        # 2. Traditional Vector Retrieval (ChromaDB - Semantic similarity)
        print(f"[RAG] Retrieving Vector contexts...")
        hits = self.vector_db.query(question, top_k=5, filter_metadata=filter_metadata)
        if hits:
            vector_contexts = [hit["content"] for hit in hits]
            all_contexts.extend(vector_contexts)
            sources.extend([{"doc_id": hit["metadata"].get("doc_id"), "mode": "vector", "distance": hit.get("distance")} for hit in hits])

        if not all_contexts:
            return {"answer": "No relevant information found in any index.", "sources": []}
            
        # Deduplicate and merge
        unique_contexts = list(set(all_contexts))
        context_str = "\n\n---\n\n".join(unique_contexts)
        
        # Step 2: Generate answer using unified context
        print(f"[RAG] Generating answer from {len(unique_contexts)} context blocks")
        answer = self.llm_service.answer_question(question, context_str)
        return {
            "answer": answer,
            "sources": sources
        }

    def summarize_document(self, filter_metadata: dict):
        """
        Summarize a document given its fragments.
        """
        # For simplicity, retrieve the first few chunks or all if small
        hits = self.vector_db.query("", top_k=10, filter_metadata=filter_metadata) # Get chunks
        if not hits:
            return "Document not found or empty."
            
        full_text = "\n\n".join([hit["content"] for hit in hits])
        return self.llm_service.generate_summary(full_text[:10000]) # Cap for context limit

    def extract_structured_from_document(self, schema_description: str, filter_metadata: dict):
        """
        Extract structured data from a document.
        """
        hits = self.vector_db.query("", top_k=10, filter_metadata=filter_metadata)
        if not hits:
            return "Document not found or empty."
            
        full_text = "\n\n".join([hit["content"] for hit in hits])
        return self.llm_service.extract_structured_data(full_text[:10000], schema_description)
