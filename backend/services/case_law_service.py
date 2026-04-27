"""
Case Law Knowledge Base Service
Manages actual legal judgments and precedents for authoritative answers
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class CaseLawService:
    """Service for managing and searching legal case law database"""
    
    def __init__(self):
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ChromaDB for case law
            db_path = os.path.join(os.path.dirname(__file__), "..", "case_law_db")
            os.makedirs(db_path, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create collection for case law
            try:
                self.collection = self.chroma_client.get_collection("indian_case_law")
                logger.info("Loaded existing case law collection")
            except:
                self.collection = self.chroma_client.create_collection(
                    name="indian_case_law",
                    metadata={"description": "Indian legal judgments and precedents"}
                )
                logger.info("Created new case law collection")
            
            logger.info("CaseLawService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing CaseLawService: {str(e)}")
            raise
    
    def add_case(self, case_data: Dict[str, Any]) -> str:
        """
        Add a legal case to the knowledge base
        
        Args:
            case_data: Dictionary containing:
                - case_name: str (e.g., "Tech Innovations vs Global Software")
                - citation: str (e.g., "2024 SCC 123")
                - court: str (e.g., "Supreme Court of India")
                - date: str (YYYY-MM-DD)
                - judges: List[str]
                - category: str (e.g., "Contract Law", "Corporate Law") [NEW]
                - subcategory: str (e.g., "Software Contracts") [NEW]
                - legal_areas: List[str] (e.g., ["Contract Law", "Arbitration"])
                - jurisdiction: str (e.g., "India") [NEW]
                - importance: str ("Landmark"/"Important"/"Regular") [NEW]
                - facts: str (summary of facts)
                - issues: List[str] (legal issues addressed)
                - holdings: List[str] (court's decisions)
                - reasoning: str (court's reasoning)
                - precedents_cited: List[str] (cases cited)
                - full_text: str (complete judgment text)
                - source: str (e.g., "Indian Kanoon", "Manual") [NEW]
        
        Returns:
            case_id: Unique identifier for the case
        """
        try:
            case_id = f"case_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{case_data['case_name'][:20].replace(' ', '_')}"
            
            # Create searchable text combining key elements
            searchable_text = f"""
            Case: {case_data['case_name']}
            Citation: {case_data.get('citation', 'N/A')}
            Court: {case_data.get('court', 'N/A')}
            Legal Areas: {', '.join(case_data.get('legal_areas', []))}
            
            Facts: {case_data.get('facts', '')}
            
            Issues: {' | '.join(case_data.get('issues', []))}
            
            Holdings: {' | '.join(case_data.get('holdings', []))}
            
            Reasoning: {case_data.get('reasoning', '')}
            """
            
            # Generate embedding
            embedding = self.embedding_model.encode(searchable_text).tolist()
            
            # Store in ChromaDB
            self.collection.add(
                ids=[case_id],
                embeddings=[embedding],
                documents=[searchable_text],
                metadatas=[{
                    "case_name": case_data['case_name'],
                    "citation": case_data.get('citation', ''),
                    "court": case_data.get('court', ''),
                    "date": case_data.get('date', ''),
                    "category": case_data.get('category', 'General'),
                    "subcategory": case_data.get('subcategory', ''),
                    "jurisdiction": case_data.get('jurisdiction', 'India'),
                    "importance": case_data.get('importance', 'Regular'),
                    "judges": json.dumps(case_data.get('judges', [])),
                    "legal_areas": json.dumps(case_data.get('legal_areas', [])),
                    "issues": json.dumps(case_data.get('issues', [])),
                    "holdings": json.dumps(case_data.get('holdings', [])),
                    "precedents_cited": json.dumps(case_data.get('precedents_cited', [])),
                    "source": case_data.get('source', 'Manual'),
                    "full_text_length": len(case_data.get('full_text', ''))
                }]
            )
            
            # Store full text separately (for detailed retrieval)
            full_text_path = f"backend/case_law_db/full_texts/{case_id}.json"
            os.makedirs(os.path.dirname(full_text_path), exist_ok=True)
            with open(full_text_path, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Added case: {case_data['case_name']} (ID: {case_id})")
            return case_id
            
        except Exception as e:
            logger.error(f"Error adding case: {str(e)}")
            raise
    
    def search_cases(
        self,
        query: str,
        legal_area: Optional[str] = None,
        court: Optional[str] = None,
        category: Optional[str] = None,
        importance: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant cases based on query
        
        Args:
            query: Natural language query or legal issue
            legal_area: Filter by legal area (e.g., "Contract Law")
            court: Filter by court (e.g., "Supreme Court of India")
            category: Filter by category (e.g., "Contract Law", "Corporate Law")
            importance: Filter by importance ("Landmark", "Important", "Regular")
            top_k: Number of results to return
        
        Returns:
            List of relevant cases with metadata and excerpts
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Build filter - ChromaDB uses exact match for strings
            where_filter = None
            if court:
                where_filter = {"court": court}
            elif category:
                where_filter = {"category": category}
            elif importance:
                where_filter = {"importance": importance}
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k * 2,  # Get more for post-filtering
                where=where_filter
            )
            
            # Format results
            cases = []
            for i in range(len(results['ids'][0])):
                case_id = results['ids'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                # Filter by legal area in post-processing
                if legal_area:
                    legal_areas = json.loads(metadata.get('legal_areas', '[]'))
                    if legal_area not in legal_areas:
                        continue
                
                # Load full case data
                full_text_path = f"backend/case_law_db/full_texts/{case_id}.json"
                full_case_data = {}
                if os.path.exists(full_text_path):
                    with open(full_text_path, 'r', encoding='utf-8') as f:
                        full_case_data = json.load(f)
                
                cases.append({
                    "case_id": case_id,
                    "case_name": metadata['case_name'],
                    "citation": metadata['citation'],
                    "court": metadata['court'],
                    "date": metadata['date'],
                    "category": metadata.get('category', 'General'),
                    "subcategory": metadata.get('subcategory', ''),
                    "importance": metadata.get('importance', 'Regular'),
                    "legal_areas": json.loads(metadata['legal_areas']),
                    "issues": json.loads(metadata['issues']),
                    "holdings": json.loads(metadata['holdings']),
                    "relevance_score": 1 - distance,
                    "excerpt": results['documents'][0][i][:500] + "...",
                    "full_case_data": full_case_data
                })
                
                if len(cases) >= top_k:
                    break
            
            logger.info(f"Found {len(cases)} relevant cases for query: {query[:50]}...")
            return cases
            
        except Exception as e:
            logger.error(f"Error searching cases: {str(e)}")
            return []
    
    def get_case_by_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full case data by ID"""
        try:
            full_text_path = f"backend/case_law_db/full_texts/{case_id}.json"
            if os.path.exists(full_text_path):
                with open(full_text_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error retrieving case {case_id}: {str(e)}")
            return None
    
    def get_cases_by_citation(self, citation: str) -> List[Dict[str, Any]]:
        """Find cases by citation (e.g., "2024 SCC 123")"""
        try:
            results = self.collection.get(
                where={"citation": citation}
            )
            
            cases = []
            for i, case_id in enumerate(results['ids']):
                full_case_data = self.get_case_by_id(case_id)
                if full_case_data:
                    cases.append(full_case_data)
            
            return cases
        except Exception as e:
            logger.error(f"Error finding cases by citation: {str(e)}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the case law database"""
        try:
            count = self.collection.count()
            
            # Get all metadata to analyze
            all_cases = self.collection.get()
            
            courts = set()
            legal_areas = set()
            categories = {}
            importance_counts = {"Landmark": 0, "Important": 0, "Regular": 0}
            
            for metadata in all_cases['metadatas']:
                courts.add(metadata.get('court', 'Unknown'))
                areas = json.loads(metadata.get('legal_areas', '[]'))
                legal_areas.update(areas)
                
                # Count by category
                category = metadata.get('category', 'General')
                categories[category] = categories.get(category, 0) + 1
                
                # Count by importance
                importance = metadata.get('importance', 'Regular')
                importance_counts[importance] = importance_counts.get(importance, 0) + 1
            
            return {
                "total_cases": count,
                "courts": list(courts),
                "legal_areas": list(legal_areas),
                "categories": categories,
                "importance_distribution": importance_counts,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {"total_cases": 0, "error": str(e)}
    
    def is_duplicate(self, case_name: str, citation: str) -> bool:
        """Check if a case already exists in the database"""
        try:
            # Search by citation (most reliable)
            if citation:
                results = self.collection.get(
                    where={"citation": citation}
                )
                if results['ids']:
                    return True
            
            # Search by case name similarity
            if case_name:
                results = self.collection.query(
                    query_embeddings=[self.embedding_model.encode(case_name).tolist()],
                    n_results=1
                )
                if results['ids'] and results['ids'][0]:
                    # Check if very similar (distance < 0.1)
                    if results['distances'][0][0] < 0.1:
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking duplicate: {str(e)}")
            return False


# Singleton instance
_case_law_service = None

def get_case_law_service() -> CaseLawService:
    """Get or create CaseLawService singleton"""
    global _case_law_service
    if _case_law_service is None:
        _case_law_service = CaseLawService()
    return _case_law_service
