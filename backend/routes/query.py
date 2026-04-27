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
from backend.services.legal_knowledge_service import LegalKnowledgeService
from backend.services.case_law_service import get_case_law_service
from backend.database.vector_db import VectorDB
from .auth import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/api/query", tags=["Query"])

vector_db = VectorDB()
llm_service = LLMService()
rag_service = RAGService(llm_service, vector_db)       # legacy fallback
legal_rag = LegalRAGService(vector_db)                 # legal-aware service
legal_knowledge = LegalKnowledgeService()              # legal knowledge base
case_law_service = get_case_law_service()              # actual case law database
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

class PrecedentSearchRequest(BaseModel):
    query: str
    legal_area: Optional[str] = None  # contract, arbitration, IP, etc.
    top_k: int = 5

class CaseLawSearchRequest(BaseModel):
    query: str
    legal_area: Optional[str] = None
    court: Optional[str] = None  # e.g., "Supreme Court of India"
    top_k: int = 5


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


@router.post("/search-precedents")
async def search_precedents(
    request: PrecedentSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search legal knowledge base for relevant precedents and case law.
    Returns analysis of what courts generally say about similar cases.
    """
    result = legal_knowledge.search_precedents(
        query=request.query,
        legal_area=request.legal_area,
        top_k=request.top_k
    )
    return result


@router.post("/search-case-law")
async def search_case_law(
    request: CaseLawSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search actual Indian case law database for relevant judgments.
    Returns real cases with citations, holdings, and reasoning.
    
    Example queries:
    - "software contract breach remedies"
    - "force majeure in supply contracts"
    - "limitation of liability clauses"
    """
    try:
        cases = case_law_service.search_cases(
            query=request.query,
            legal_area=request.legal_area,
            court=request.court,
            top_k=request.top_k
        )
        
        if not cases:
            return {
                "message": "No relevant cases found. Try broadening your search terms.",
                "cases": [],
                "query": request.query
            }
        
        # Format cases for frontend
        formatted_cases = []
        for case in cases:
            formatted_cases.append({
                "case_name": case['case_name'],
                "citation": case['citation'],
                "court": case['court'],
                "date": case['date'],
                "legal_areas": case['legal_areas'],
                "issues": case['issues'],
                "holdings": case['holdings'],
                "relevance_score": case['relevance_score'],
                "excerpt": case['excerpt'],
                "case_id": case['case_id']
            })
        
        return {
            "message": f"Found {len(formatted_cases)} relevant case(s)",
            "cases": formatted_cases,
            "query": request.query,
            "filters": {
                "legal_area": request.legal_area,
                "court": request.court
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Case law search failed: {str(e)}")


@router.get("/case-law/{case_id}")
async def get_case_details(
    case_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get full details of a specific case by ID.
    Returns complete judgment text, reasoning, and precedents cited.
    """
    try:
        case_data = case_law_service.get_case_by_id(case_id)
        
        if not case_data:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return {
            "case": case_data,
            "case_id": case_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve case: {str(e)}")


@router.get("/case-law-stats")
async def get_case_law_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about the case law database.
    Returns total cases, courts covered, and legal areas.
    """
    try:
        # Initialize service if needed
        service = get_case_law_service()
        stats = service.get_database_stats()
        return stats
    except Exception as e:
        import traceback
        print(f"Error getting case law stats: {str(e)}")
        print(traceback.format_exc())
        # Return empty stats instead of error
        return {
            "total_cases": 0,
            "courts": [],
            "legal_areas": [],
            "categories": {},
            "importance_distribution": {
                "Landmark": 0,
                "Important": 0,
                "Regular": 0
            },
            "last_updated": "",
            "error": str(e)
        }


@router.get("/case-law-health")
async def case_law_health_check():
    """
    Health check for case law system (no auth required for debugging)
    """
    try:
        import os
        service = get_case_law_service()
        stats = service.get_database_stats()
        
        # Check database path
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "case_law_db")
        db_exists = os.path.exists(db_path)
        
        return {
            "status": "healthy",
            "database_path": db_path,
            "database_exists": db_exists,
            "total_cases": stats.get("total_cases", 0),
            "service_initialized": True
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "service_initialized": False
        }


@router.post("/admin/import-cases")
async def trigger_case_import(
    mode: str = "foundation",  # foundation or domain
    domain: str = None,  # Contract Law, Corporate Law, etc.
    cases_count: int = 10,  # Number of cases to import
    current_user: User = Depends(get_current_user)
):
    """
    ADMIN ONLY: Import REAL cases from Indian Kanoon for selected domain
    
    Modes:
    - foundation: Import cases from all domains (10 cases per domain)
    - domain: Import cases for specific domain only
    
    Available domains:
    - Contract Law
    - Corporate Law
    - Intellectual Property
    - Employment Law
    - Real Estate
    - Arbitration
    - Cyber Law
    - Tax Law
    - Banking & Finance
    - Consumer Protection
    """
    try:
        import threading
        
        # Domain to search query mapping
        DOMAIN_QUERIES = {
            "Contract Law": "contract breach Supreme Court India",
            "Corporate Law": "company director shareholder Supreme Court India",
            "Intellectual Property": "patent trademark copyright Supreme Court India",
            "Employment Law": "employment termination labor Supreme Court India",
            "Real Estate": "property land lease Supreme Court India",
            "Arbitration": "arbitration award Supreme Court India",
            "Cyber Law": "cyber crime data protection Supreme Court India",
            "Tax Law": "income tax GST Supreme Court India",
            "Banking & Finance": "banking loan SARFAESI Supreme Court India",
            "Consumer Protection": "consumer defective product Supreme Court India"
        }
        
        def run_import():
            """Run import in background"""
            try:
                import sys
                from pathlib import Path
                backend_dir = Path(__file__).parent.parent
                sys.path.insert(0, str(backend_dir))
                sys.path.insert(0, str(backend_dir / "scripts"))
                
                from scrapers.indian_kanoon_scraper import IndianKanoonScraper
                from services.case_categorizer import get_case_categorizer
                
                print(f"Starting real case import - mode: {mode}, domain: {domain}")
                
                scraper = IndianKanoonScraper(delay=1)  # Faster for UI
                categorizer = get_case_categorizer()
                
                # Determine which domains to import
                if mode == "foundation":
                    domains_to_import = list(DOMAIN_QUERIES.keys())
                    cases_per_domain = max(1, cases_count // len(domains_to_import))
                elif mode == "domain" and domain:
                    domains_to_import = [domain]
                    cases_per_domain = cases_count
                else:
                    print("Invalid mode or missing domain")
                    return
                
                total_added = 0
                
                for import_domain in domains_to_import:
                    query = DOMAIN_QUERIES.get(import_domain)
                    if not query:
                        continue
                    
                    print(f"\n{'='*60}")
                    print(f"Importing {import_domain} cases...")
                    print(f"{'='*60}")
                    
                    try:
                        # Scrape cases from Indian Kanoon
                        raw_cases = scraper.search_cases(query, num_results=cases_per_domain)
                        print(f"Fetched {len(raw_cases)} cases from Indian Kanoon")
                        
                        for raw_case in raw_cases:
                            try:
                                # Check for duplicates
                                if case_law_service.is_duplicate(
                                    raw_case.get('case_name', ''),
                                    raw_case.get('citation', '')
                                ):
                                    print(f"  ⊘ Duplicate: {raw_case['case_name'][:60]}...")
                                    continue
                                
                                # Auto-categorize using LLM
                                print(f"  🤖 Categorizing: {raw_case['case_name'][:60]}...")
                                metadata = categorizer.categorize_case(
                                    raw_case.get('full_text', ''),
                                    raw_case.get('case_name', ''),
                                    raw_case.get('citation', '')
                                )
                                
                                # Merge data
                                case_data = {
                                    "case_name": raw_case.get('case_name', 'Unknown'),
                                    "citation": raw_case.get('citation', ''),
                                    "court": raw_case.get('court', ''),
                                    "date": raw_case.get('date', ''),
                                    "judges": raw_case.get('judges', []),
                                    "category": metadata.get('category', import_domain),
                                    "subcategory": metadata.get('subcategory', ''),
                                    "legal_areas": metadata.get('legal_areas', [import_domain]),
                                    "jurisdiction": "India",
                                    "importance": metadata.get('importance', 'Regular'),
                                    "facts": raw_case.get('full_text', '')[:500] + "...",
                                    "issues": [metadata.get('issues_summary', 'See full text')],
                                    "holdings": [metadata.get('holdings_summary', 'See full text')],
                                    "reasoning": raw_case.get('full_text', '')[500:1000] + "...",
                                    "precedents_cited": [],
                                    "full_text": raw_case.get('full_text', ''),
                                    "source": "Indian Kanoon (Auto-imported)",
                                    "url": raw_case.get('url', '')
                                }
                                
                                # Add to database
                                case_id = case_law_service.add_case(case_data)
                                print(f"  ✓ Added: {case_data['case_name'][:60]}... [{metadata['category']}]")
                                total_added += 1
                                
                            except Exception as e:
                                print(f"  ✗ Error processing case: {str(e)}")
                                continue
                        
                    except Exception as e:
                        print(f"Error importing {import_domain}: {str(e)}")
                        continue
                
                print(f"\n{'='*60}")
                print(f"Import complete! Added {total_added} real cases")
                print(f"{'='*60}")
                
            except Exception as e:
                import traceback
                print(f"Import error: {str(e)}")
                print(traceback.format_exc())
        
        # Start import in background thread
        thread = threading.Thread(target=run_import, daemon=True)
        thread.start()
        
        return {
            "message": f"Importing REAL cases from Indian Kanoon in background",
            "note": f"Scraping and categorizing {cases_count} cases. This will take 2-5 minutes. Check back later.",
            "mode": mode,
            "domain": domain,
            "cases_count": cases_count,
            "source": "Indian Kanoon"
        }
    
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"Error: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/admin/available-domains")
async def get_available_domains_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Get list of available domains for import"""
    try:
        domains = [
            {"name": "Contract Law", "case_count": 10, "sample_cases": ["Contract breach cases", "Specific performance"]},
            {"name": "Corporate Law", "case_count": 10, "sample_cases": ["Company disputes", "Director liability"]},
            {"name": "Intellectual Property", "case_count": 10, "sample_cases": ["Patent cases", "Trademark infringement"]},
            {"name": "Employment Law", "case_count": 10, "sample_cases": ["Wrongful termination", "Labor disputes"]},
            {"name": "Real Estate", "case_count": 10, "sample_cases": ["Property disputes", "RERA cases"]},
            {"name": "Arbitration", "case_count": 10, "sample_cases": ["Arbitration awards", "Enforcement"]},
            {"name": "Cyber Law", "case_count": 10, "sample_cases": ["Cyber crimes", "Data protection"]},
            {"name": "Tax Law", "case_count": 10, "sample_cases": ["Income tax", "GST disputes"]},
            {"name": "Banking & Finance", "case_count": 10, "sample_cases": ["Banking disputes", "Loan recovery"]},
            {"name": "Consumer Protection", "case_count": 10, "sample_cases": ["Consumer disputes", "Defective products"]},
        ]
        
        return {
            "domains": domains,
            "total_domains": len(domains),
            "note": "These are real cases scraped from Indian Kanoon"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
