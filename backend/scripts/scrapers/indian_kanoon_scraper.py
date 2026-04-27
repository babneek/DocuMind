"""
Indian Kanoon Scraper
Scrapes legal cases from indiankanoon.org (free legal database)
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class IndianKanoonScraper:
    """Scrape cases from Indian Kanoon"""
    
    BASE_URL = "https://indiankanoon.org"
    SEARCH_URL = f"{BASE_URL}/search/"
    
    def __init__(self, delay=2):
        """
        Args:
            delay: Delay between requests in seconds (be polite!)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_cases(self, query: str, num_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for cases on Indian Kanoon
        
        Args:
            query: Search query (e.g., "software contract breach")
            num_results: Number of results to fetch
        
        Returns:
            List of case dictionaries
        """
        cases = []
        
        try:
            # Search
            params = {"formInput": query}
            response = self.session.get(self.SEARCH_URL, params=params, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all result divs
            results = soup.find_all('div', class_='result')
            
            logger.info(f"Found {len(results)} search results for '{query}'")
            
            for i, result in enumerate(results[:num_results]):
                try:
                    # Extract case link and title
                    link_tag = result.find('a', class_='result_title')
                    if not link_tag:
                        continue
                    
                    case_url = link_tag.get('href', '')
                    case_title = link_tag.get_text(strip=True)
                    
                    if not case_url:
                        continue
                    
                    logger.info(f"Fetching case {i+1}/{num_results}: {case_title[:50]}...")
                    
                    # Fetch full case details
                    case_data = self.fetch_case_details(case_url)
                    if case_data:
                        case_data['search_query'] = query
                        cases.append(case_data)
                    
                    # Be polite - delay between requests
                    time.sleep(self.delay)
                    
                except Exception as e:
                    logger.error(f"Error processing result {i}: {str(e)}")
                    continue
            
            logger.info(f"Successfully fetched {len(cases)} cases")
            return cases
            
        except Exception as e:
            logger.error(f"Error searching Indian Kanoon: {str(e)}")
            return []
    
    def fetch_case_details(self, case_url: str) -> Dict[str, Any]:
        """
        Fetch full case details from case page
        
        Args:
            case_url: Relative URL of the case (e.g., "/doc/123456/")
        
        Returns:
            Dictionary with case details
        """
        try:
            full_url = f"{self.BASE_URL}{case_url}" if not case_url.startswith('http') else case_url
            
            response = self.session.get(full_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract case name
            case_name = ""
            title_tag = soup.find('h1', class_='doc_title')
            if title_tag:
                case_name = title_tag.get_text(strip=True)
            
            # Extract citation
            citation = ""
            citation_tag = soup.find('div', class_='doc_citations')
            if citation_tag:
                citation = citation_tag.get_text(strip=True)
            
            # Extract court and date
            court = ""
            date = ""
            author_tag = soup.find('div', class_='doc_author')
            if author_tag:
                author_text = author_tag.get_text()
                # Try to extract court name and date
                court_match = re.search(r'(Supreme Court|High Court[^,]*)', author_text)
                if court_match:
                    court = court_match.group(1).strip()
                
                date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', author_text)
                if date_match:
                    date = date_match.group(1).strip()
            
            # Extract judgment text
            full_text = ""
            judgment_div = soup.find('div', class_='judgments')
            if judgment_div:
                # Remove script and style tags
                for script in judgment_div(['script', 'style']):
                    script.decompose()
                full_text = judgment_div.get_text(separator='\n', strip=True)
            
            # Extract judges (if available)
            judges = []
            bench_tag = soup.find('div', class_='doc_bench')
            if bench_tag:
                judges_text = bench_tag.get_text()
                # Simple extraction - can be improved
                judges = [j.strip() for j in judges_text.split(',') if j.strip()]
            
            case_data = {
                "case_name": case_name,
                "citation": citation,
                "court": court,
                "date": date,
                "judges": judges,
                "full_text": full_text,
                "url": full_url,
                "source": "Indian Kanoon"
            }
            
            logger.info(f"Fetched: {case_name[:50]}...")
            return case_data
            
        except Exception as e:
            logger.error(f"Error fetching case details from {case_url}: {str(e)}")
            return None
    
    def fetch_by_citation(self, citation: str) -> Dict[str, Any]:
        """
        Fetch a specific case by citation
        
        Args:
            citation: Case citation (e.g., "2010 3 SCC 1")
        
        Returns:
            Case dictionary or None
        """
        results = self.search_cases(citation, num_results=1)
        return results[0] if results else None
    
    def fetch_landmark_cases(self, category: str, num_cases: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch landmark cases for a specific category
        
        Args:
            category: Legal category (e.g., "Contract Law")
            num_cases: Number of cases to fetch
        
        Returns:
            List of landmark cases
        """
        # Search with "Supreme Court" to get landmark cases
        query = f"{category} Supreme Court landmark"
        return self.search_cases(query, num_results=num_cases)


if __name__ == "__main__":
    # Test the scraper
    logging.basicConfig(level=logging.INFO)
    
    scraper = IndianKanoonScraper(delay=2)
    
    print("Testing Indian Kanoon Scraper...")
    print("="*60)
    
    # Test search
    cases = scraper.search_cases("software contract", num_results=3)
    
    print(f"\nFetched {len(cases)} cases:")
    for i, case in enumerate(cases, 1):
        print(f"\n{i}. {case['case_name'][:80]}")
        print(f"   Citation: {case['citation']}")
        print(f"   Court: {case['court']}")
        print(f"   Text length: {len(case['full_text'])} chars")
