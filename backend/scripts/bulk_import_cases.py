"""
Bulk Case Import System
Automatically scrapes, categorizes, and imports cases from multiple sources
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
from typing import List, Dict, Any
from datetime import datetime

# Import scrapers with correct path
from scrapers.indian_kanoon_scraper import IndianKanoonScraper

# Import services - use absolute imports
import sys
from pathlib import Path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.case_law_service import get_case_law_service
from services.case_categorizer import get_case_categorizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'bulk_import_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BulkCaseImporter:
    """Bulk import cases from multiple sources with auto-categorization"""
    
    # Define search queries for each category
    CATEGORY_QUERIES = {
        "Contract Law": [
            "contract breach Supreme Court",
            "specific performance contract",
            "frustration of contract",
            "breach of warranty",
            "liquidated damages contract"
        ],
        "Corporate Law": [
            "company law Supreme Court",
            "director liability",
            "shareholder dispute",
            "oppression mismanagement",
            "corporate governance"
        ],
        "Intellectual Property": [
            "patent infringement Supreme Court",
            "trademark infringement",
            "copyright infringement",
            "passing off",
            "trade secret"
        ],
        "Employment Law": [
            "wrongful termination Supreme Court",
            "industrial dispute",
            "retrenchment compensation",
            "unfair labor practice",
            "workmen compensation"
        ],
        "Real Estate": [
            "property dispute Supreme Court",
            "specific performance sale",
            "lease agreement dispute",
            "title dispute property",
            "RERA dispute"
        ],
        "Arbitration": [
            "arbitration award Supreme Court",
            "arbitration clause enforcement",
            "arbitral tribunal jurisdiction",
            "setting aside arbitral award",
            "foreign arbitral award"
        ],
        "Cyber Law": [
            "cyber crime Supreme Court",
            "data protection privacy",
            "information technology act",
            "electronic evidence",
            "intermediary liability"
        ],
        "Tax Law": [
            "income tax Supreme Court",
            "GST dispute",
            "tax evasion penalty",
            "advance ruling tax",
            "capital gains tax"
        ],
        "Banking & Finance": [
            "banking dispute Supreme Court",
            "loan recovery",
            "negotiable instruments",
            "SARFAESI Act",
            "insolvency bankruptcy"
        ],
        "Consumer Protection": [
            "consumer dispute Supreme Court",
            "defective product",
            "service deficiency",
            "unfair trade practice",
            "consumer forum"
        ]
    }
    
    def __init__(self):
        self.scraper = IndianKanoonScraper(delay=2)
        self.case_service = get_case_law_service()
        self.categorizer = get_case_categorizer()
        
        self.stats = {
            "total_fetched": 0,
            "total_added": 0,
            "duplicates_skipped": 0,
            "errors": 0,
            "by_category": {}
        }
    
    def import_category(self, category: str, cases_per_query: int = 5) -> int:
        """
        Import cases for a specific category
        
        Args:
            category: Legal category name
            cases_per_query: Number of cases to fetch per search query
        
        Returns:
            Number of cases successfully imported
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Importing {category} cases...")
        logger.info(f"{'='*80}\n")
        
        queries = self.CATEGORY_QUERIES.get(category, [])
        if not queries:
            logger.warning(f"No queries defined for category: {category}")
            return 0
        
        added_count = 0
        
        for query in queries:
            logger.info(f"Searching: '{query}'")
            
            try:
                # Fetch cases from Indian Kanoon
                raw_cases = self.scraper.search_cases(query, num_results=cases_per_query)
                self.stats["total_fetched"] += len(raw_cases)
                
                for raw_case in raw_cases:
                    try:
                        # Check for duplicates
                        if self.case_service.is_duplicate(
                            raw_case.get('case_name', ''),
                            raw_case.get('citation', '')
                        ):
                            logger.info(f"  ⊘ Duplicate: {raw_case['case_name'][:60]}...")
                            self.stats["duplicates_skipped"] += 1
                            continue
                        
                        # Auto-categorize using LLM
                        logger.info(f"  🤖 Categorizing: {raw_case['case_name'][:60]}...")
                        metadata = self.categorizer.categorize_case(
                            raw_case.get('full_text', ''),
                            raw_case.get('case_name', ''),
                            raw_case.get('citation', '')
                        )
                        
                        # Extract structured data
                        structured_data = self.categorizer.extract_structured_data(
                            raw_case.get('full_text', '')
                        )
                        
                        # Merge all data
                        case_data = self._merge_case_data(raw_case, metadata, structured_data)
                        
                        # Add to database
                        case_id = self.case_service.add_case(case_data)
                        
                        logger.info(f"  ✓ Added: {case_data['case_name'][:60]}... [{metadata['category']}]")
                        added_count += 1
                        self.stats["total_added"] += 1
                        
                        # Update category stats
                        cat = metadata['category']
                        self.stats["by_category"][cat] = self.stats["by_category"].get(cat, 0) + 1
                        
                    except Exception as e:
                        logger.error(f"  ✗ Error processing case: {str(e)}")
                        self.stats["errors"] += 1
                        continue
                
                # Small delay between queries
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error with query '{query}': {str(e)}")
                self.stats["errors"] += 1
                continue
        
        logger.info(f"\n{category}: Added {added_count} cases\n")
        return added_count
    
    def import_all_categories(self, cases_per_query: int = 5):
        """
        Import cases for all categories
        
        Args:
            cases_per_query: Number of cases to fetch per search query
        """
        start_time = time.time()
        
        logger.info("\n" + "="*80)
        logger.info("BULK CASE IMPORT - STARTING")
        logger.info("="*80 + "\n")
        
        for category in self.CATEGORY_QUERIES.keys():
            try:
                self.import_category(category, cases_per_query)
            except Exception as e:
                logger.error(f"Failed to import {category}: {str(e)}")
                continue
        
        elapsed_time = time.time() - start_time
        
        # Print final statistics
        self._print_final_stats(elapsed_time)
    
    def import_foundation_cases(self):
        """
        Import foundation set of 100 most important cases
        Focuses on landmark Supreme Court cases
        """
        logger.info("\n" + "="*80)
        logger.info("IMPORTING FOUNDATION CASES (100 Landmark Cases)")
        logger.info("="*80 + "\n")
        
        # Import fewer but higher quality cases per category
        priority_categories = [
            "Contract Law",
            "Corporate Law",
            "Intellectual Property",
            "Employment Law",
            "Real Estate",
            "Arbitration"
        ]
        
        for category in priority_categories:
            self.import_category(category, cases_per_query=3)
    
    def _merge_case_data(
        self,
        raw_case: Dict[str, Any],
        metadata: Dict[str, Any],
        structured_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge data from different sources into final case structure"""
        
        # Extract issues and holdings from full text (simplified)
        full_text = raw_case.get('full_text', '')
        issues = self._extract_issues(full_text, metadata.get('issues_summary', ''))
        holdings = self._extract_holdings(full_text, metadata.get('holdings_summary', ''))
        
        return {
            "case_name": raw_case.get('case_name', 'Unknown'),
            "citation": raw_case.get('citation', ''),
            "court": structured_data.get('court', raw_case.get('court', '')),
            "date": structured_data.get('date', raw_case.get('date', '')),
            "judges": structured_data.get('judges', raw_case.get('judges', [])),
            "category": metadata.get('category', 'General'),
            "subcategory": metadata.get('subcategory', ''),
            "legal_areas": metadata.get('legal_areas', []),
            "jurisdiction": "India",
            "importance": metadata.get('importance', 'Regular'),
            "facts": self._extract_facts(full_text),
            "issues": issues,
            "holdings": holdings,
            "reasoning": self._extract_reasoning(full_text),
            "precedents_cited": self._extract_precedents(full_text),
            "full_text": full_text,
            "source": "Indian Kanoon (Auto-imported)",
            "url": raw_case.get('url', '')
        }
    
    def _extract_issues(self, full_text: str, summary: str) -> List[str]:
        """Extract legal issues from case text"""
        if summary:
            return [summary]
        # Simplified extraction - look for common patterns
        issues = []
        if "issue" in full_text.lower()[:2000]:
            # Extract first few sentences after "issue"
            issues.append("See full case text for detailed issues")
        return issues if issues else ["Legal issues as per case text"]
    
    def _extract_holdings(self, full_text: str, summary: str) -> List[str]:
        """Extract court holdings from case text"""
        if summary:
            return [summary]
        return ["See full case text for detailed holdings"]
    
    def _extract_facts(self, full_text: str) -> str:
        """Extract case facts"""
        # Take first 500 characters as facts summary
        return full_text[:500] + "..." if len(full_text) > 500 else full_text
    
    def _extract_reasoning(self, full_text: str) -> str:
        """Extract court's reasoning"""
        # Take middle portion as reasoning
        mid_point = len(full_text) // 2
        return full_text[mid_point:mid_point+500] + "..."
    
    def _extract_precedents(self, full_text: str) -> List[str]:
        """Extract cited precedents"""
        # Look for common citation patterns
        import re
        citations = re.findall(r'\d{4}\s+\d+\s+SCC\s+\d+', full_text)
        return list(set(citations))[:5]  # Return up to 5 unique citations
    
    def _print_final_stats(self, elapsed_time: float):
        """Print final import statistics"""
        logger.info("\n" + "="*80)
        logger.info("BULK IMPORT COMPLETE")
        logger.info("="*80)
        logger.info(f"\nTotal Time: {elapsed_time/60:.1f} minutes")
        logger.info(f"Total Fetched: {self.stats['total_fetched']}")
        logger.info(f"Total Added: {self.stats['total_added']}")
        logger.info(f"Duplicates Skipped: {self.stats['duplicates_skipped']}")
        logger.info(f"Errors: {self.stats['errors']}")
        
        logger.info("\nCases by Category:")
        for category, count in sorted(self.stats['by_category'].items()):
            logger.info(f"  {category}: {count}")
        
        # Get database stats
        db_stats = self.case_service.get_database_stats()
        logger.info(f"\nTotal Cases in Database: {db_stats['total_cases']}")
        logger.info("="*80 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk import legal cases')
    parser.add_argument(
        '--mode',
        choices=['foundation', 'full', 'category'],
        default='foundation',
        help='Import mode: foundation (100 cases), full (500+ cases), or category'
    )
    parser.add_argument(
        '--category',
        type=str,
        help='Specific category to import (use with --mode category)'
    )
    parser.add_argument(
        '--cases-per-query',
        type=int,
        default=5,
        help='Number of cases to fetch per search query'
    )
    
    args = parser.parse_args()
    
    importer = BulkCaseImporter()
    
    if args.mode == 'foundation':
        importer.import_foundation_cases()
    elif args.mode == 'full':
        importer.import_all_categories(cases_per_query=args.cases_per_query)
    elif args.mode == 'category':
        if not args.category:
            print("Error: --category required with --mode category")
            return
        importer.import_category(args.category, cases_per_query=args.cases_per_query)


if __name__ == "__main__":
    main()
