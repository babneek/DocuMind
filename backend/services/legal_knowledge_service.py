"""
Legal Knowledge Base Service - Search legal precedents and case law
"""

from backend.database.vector_db import VectorDB
from backend.services.legal_llm_service import LegalLLMService


class LegalKnowledgeService:
    def __init__(self):
        # Separate vector DB for legal knowledge base
        self.knowledge_db = VectorDB(persist_directory="backend/legal_knowledge_db")
        self.legal_llm = LegalLLMService()
    
    def search_precedents(self, query: str, legal_area: str = None, top_k: int = 5) -> dict:
        """
        Search legal knowledge base for relevant precedents and case law.
        
        Args:
            query: Legal question or topic
            legal_area: Filter by area (contract, arbitration, IP, etc.)
            top_k: Number of results to return
        """
        filter_meta = {"legal_area": legal_area} if legal_area else None
        
        hits = self.knowledge_db.query(query, top_k=top_k, filter_metadata=filter_meta)
        
        if not hits:
            return {
                "precedents": [],
                "summary": "No relevant precedents found in the knowledge base.",
                "recommendation": "Consider consulting a legal database like Manupatra or SCC Online."
            }
        
        # Extract precedent information
        precedents = []
        for hit in hits:
            precedents.append({
                "case_name": hit["metadata"].get("case_name", "Unknown"),
                "citation": hit["metadata"].get("citation", "N/A"),
                "court": hit["metadata"].get("court", "N/A"),
                "year": hit["metadata"].get("year", "N/A"),
                "legal_area": hit["metadata"].get("legal_area", "N/A"),
                "excerpt": hit["content"][:500],
                "relevance_score": round(1 - hit.get("distance", 0), 3)
            })
        
        # Generate analysis using LLM
        context = "\n\n---\n\n".join([
            f"Case: {p['case_name']} ({p['citation']})\nCourt: {p['court']}\nExcerpt: {p['excerpt']}"
            for p in precedents
        ])
        
        analysis_prompt = f"""Based on the following legal precedents, provide a comprehensive analysis:

Query: {query}

Precedents:
{context}

Provide:
1. **Common Legal Principles** - What do courts generally say about this issue?
2. **Key Precedents** - Most relevant cases and their holdings
3. **Judicial Trends** - How has the law evolved?
4. **Practical Guidance** - What should parties expect in similar cases?

Format your response professionally with clear sections."""

        analysis = self.legal_llm._call(
            system_msg="You are a legal research assistant analyzing case law and precedents.",
            user_msg=analysis_prompt,
            max_tokens=2000
        )
        
        return {
            "precedents": precedents,
            "analysis": analysis,
            "total_found": len(precedents)
        }
    
    def add_precedent(self, case_data: dict) -> bool:
        """
        Add a legal precedent to the knowledge base.
        
        case_data should include:
        - case_name: str
        - citation: str
        - court: str
        - year: int
        - legal_area: str (contract, arbitration, IP, etc.)
        - full_text: str
        - summary: str
        """
        try:
            # Chunk the full text
            from backend.services.ingestion_service import IngestionService
            ingestion = IngestionService()
            chunks = ingestion.chunk_by_sections(case_data["full_text"], chunk_size=1000)
            
            # Prepare metadata
            metadatas = [{
                "case_name": case_data["case_name"],
                "citation": case_data["citation"],
                "court": case_data["court"],
                "year": case_data["year"],
                "legal_area": case_data["legal_area"],
                "chunk_index": i
            } for i in range(len(chunks))]
            
            ids = [f"{case_data['citation']}_chunk_{i}" for i in range(len(chunks))]
            
            self.knowledge_db.add_documents(chunks, metadatas, ids)
            return True
        except Exception as e:
            print(f"[LegalKnowledge] Error adding precedent: {e}")
            return False
