"""
Case Tracker Service
Fetches live case status, hearing dates from eCourts India
Supports: District Courts (CNR), High Courts, Supreme Court
"""

import requests
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

# eCourts India API (webapi.ecourtsindia.com) - paid but reliable
# Surepass API - alternative paid option
# We'll use the official eCourts scraping approach as fallback

ECOURTS_BASE = "https://services.ecourts.gov.in/ecourtindia_v6"
HCSERVICES_BASE = "https://hcservices.ecourts.gov.in/hcservices"

# Optional: Surepass API key (paid, ~₹0.50/call)
SUREPASS_API_KEY = os.getenv("SUREPASS_API_KEY", "")
SUREPASS_BASE = "https://kyc-api.surepass.io/api/v1"

# Optional: webapi.ecourtsindia.com (paid)
ECOURTS_API_KEY = os.getenv("ECOURTS_API_KEY", "")
ECOURTS_API_BASE = "https://webapi.ecourtsindia.com/api/v1"


class CaseTrackerService:
    """
    Tracks live case status and hearing dates from Indian courts.
    
    Supports:
    - District Courts via CNR number (16-digit alphanumeric)
    - High Courts via case number
    - Supreme Court via case number
    
    Data Sources (in priority order):
    1. webapi.ecourtsindia.com (if API key available)
    2. Surepass API (if API key available)
    3. Direct eCourts scraping (free, may be rate-limited)
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        })
    
    def get_case_by_cnr(self, cnr_number: str) -> Dict[str, Any]:
        """
        Get case details by CNR number (16-digit, e.g., DLHC010123456789)
        
        CNR Format: STATECOURTNO + YEAR + SEQUENCE
        Example: DLHC010123456789 (Delhi High Court)
        
        Returns full case details including hearing dates
        """
        cnr_number = cnr_number.strip().upper().replace("-", "").replace(" ", "")
        
        # Try paid API first if key available
        if ECOURTS_API_KEY:
            result = self._fetch_from_ecourts_api(cnr_number)
            if result:
                return result
        
        if SUREPASS_API_KEY:
            result = self._fetch_from_surepass(cnr_number)
            if result:
                return result
        
        # Fallback: direct eCourts scraping
        return self._fetch_from_ecourts_direct(cnr_number)
    
    def get_case_by_number(
        self,
        case_type: str,
        case_number: str,
        year: str,
        court: str = "delhi_hc"
    ) -> Dict[str, Any]:
        """
        Get case by case number (for High Courts / Supreme Court)
        
        Args:
            case_type: e.g., "CO", "CS", "W.P.(C)", "CRL.A."
            case_number: e.g., "448"
            year: e.g., "2022"
            court: "delhi_hc", "bombay_hc", "supreme_court", etc.
        """
        try:
            if court == "supreme_court":
                return self._fetch_sc_case(case_type, case_number, year)
            else:
                return self._fetch_hc_case(case_type, case_number, year, court)
        except Exception as e:
            logger.error(f"Error fetching case: {str(e)}")
            return {"error": str(e), "success": False}
    
    def get_upcoming_hearings(
        self,
        cnr_number: str,
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """
        Get all upcoming hearings for a case within next N days
        
        Args:
            cnr_number: CNR number of the case
            days_ahead: Number of days to look ahead (7, 30, 90)
        
        Returns:
            Dict with today's hearings, this week, this month
        """
        case_data = self.get_case_by_cnr(cnr_number)
        
        if "error" in case_data:
            return case_data
        
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        month_end = today + timedelta(days=days_ahead)
        
        # Extract next hearing date
        next_hearing = case_data.get("next_hearing_date")
        history = case_data.get("hearing_history", [])
        
        result = {
            "cnr_number": cnr_number,
            "case_title": case_data.get("case_title", ""),
            "case_status": case_data.get("case_status", ""),
            "court": case_data.get("court", ""),
            "judge": case_data.get("judge", ""),
            "today": [],
            "this_week": [],
            "this_month": [],
            "next_hearing": next_hearing,
            "all_upcoming": []
        }
        
        # Check if next hearing falls in our windows
        if next_hearing:
            try:
                hearing_date = datetime.strptime(next_hearing, "%Y-%m-%d").date()
                
                hearing_entry = {
                    "date": next_hearing,
                    "purpose": case_data.get("case_stage", "Hearing"),
                    "court_number": case_data.get("court_number", ""),
                    "judge": case_data.get("judge", "")
                }
                
                if hearing_date == today:
                    result["today"].append(hearing_entry)
                
                if today <= hearing_date <= week_end:
                    result["this_week"].append(hearing_entry)
                
                if today <= hearing_date <= month_end:
                    result["this_month"].append(hearing_entry)
                    result["all_upcoming"].append(hearing_entry)
                    
            except (ValueError, TypeError):
                pass
        
        # Add history for context
        result["hearing_history"] = history[-5:] if history else []
        
        return result
    
    def _fetch_from_ecourts_api(self, cnr_number: str) -> Optional[Dict]:
        """Fetch from webapi.ecourtsindia.com (paid API)"""
        try:
            url = f"{ECOURTS_API_BASE}/case-detail"
            headers = {"Authorization": f"Bearer {ECOURTS_API_KEY}"}
            params = {"cnr": cnr_number}
            
            response = self.session.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_ecourts_api_response(data)
            
        except Exception as e:
            logger.error(f"eCourts API error: {str(e)}")
        
        return None
    
    def _fetch_from_surepass(self, cnr_number: str) -> Optional[Dict]:
        """Fetch from Surepass API (paid, ~₹0.50/call)"""
        try:
            url = f"{SUREPASS_BASE}/court/ecourt-cnr-search"
            headers = {
                "Authorization": f"Bearer {SUREPASS_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {"cnr_number": cnr_number}
            
            response = self.session.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return self._normalize_surepass_response(data)
            
        except Exception as e:
            logger.error(f"Surepass API error: {str(e)}")
        
        return None
    
    def _fetch_from_ecourts_direct(self, cnr_number: str) -> Dict[str, Any]:
        """
        Direct fetch from eCourts website (free, no API key needed)
        Uses the public eCourts case status endpoint
        """
        try:
            # eCourts public endpoint for CNR search
            url = f"{ECOURTS_BASE}/index.php"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': ECOURTS_BASE,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            payload = {
                'cino': cnr_number,
                'ajax_req': 'true',
                'app_token': self._get_app_token()
            }
            
            response = self.session.post(
                f"{ECOURTS_BASE}/?p=cnr_search/searchByCNR",
                data=payload,
                headers=headers,
                timeout=20
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return self._normalize_ecourts_direct_response(data, cnr_number)
                except Exception:
                    # Parse HTML response
                    return self._parse_ecourts_html(response.text, cnr_number)
            
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "cnr_number": cnr_number,
                "message": "Could not fetch case data. Please check the CNR number."
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out",
                "cnr_number": cnr_number,
                "message": "eCourts server is slow. Please try again."
            }
        except Exception as e:
            logger.error(f"Direct eCourts fetch error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cnr_number": cnr_number,
                "message": "Failed to fetch case data."
            }
    
    def _fetch_hc_case(
        self,
        case_type: str,
        case_number: str,
        year: str,
        court: str
    ) -> Dict[str, Any]:
        """Fetch High Court case status"""
        try:
            # Map court to HC services URL
            court_urls = {
                "delhi_hc": "https://hcservices.ecourts.gov.in/hcservices/cases_qry.php",
                "bombay_hc": "https://bombayhighcourt.nic.in/",
                "madras_hc": "https://hcmadras.tn.nic.in/",
            }
            
            base_url = court_urls.get(court, court_urls["delhi_hc"])
            
            params = {
                "court_code": self._get_court_code(court),
                "case_type": case_type,
                "case_no": case_number,
                "rgyear": year,
                "ajax_req": "true"
            }
            
            response = self.session.get(base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                return self._normalize_hc_response(response.json(), case_type, case_number, year)
            
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "case_number": f"{case_type}/{case_number}/{year}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _fetch_sc_case(
        self,
        case_type: str,
        case_number: str,
        year: str
    ) -> Dict[str, Any]:
        """Fetch Supreme Court case status"""
        try:
            url = "https://www.sci.gov.in/case-status-case-no/"
            
            params = {
                "case_type": case_type,
                "case_no": case_number,
                "year": year
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            return {
                "success": True,
                "court": "Supreme Court of India",
                "case_number": f"{case_type}/{case_number}/{year}",
                "source_url": f"https://www.sci.gov.in/case-status-case-no/?case_type={case_type}&case_no={case_number}&year={year}",
                "message": "Please visit the Supreme Court website for live status"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_app_token(self) -> str:
        """Get eCourts app token (required for API calls)"""
        try:
            response = self.session.get(ECOURTS_BASE, timeout=10)
            # Extract token from response
            import re
            match = re.search(r'app_token["\s:=]+([a-f0-9]{64})', response.text)
            if match:
                return match.group(1)
        except Exception:
            pass
        return "0a0a2b592082b381177a1dedd4ee4a5c1416898e8699a10a2ccaa3db6902dcd0"
    
    def _get_court_code(self, court: str) -> str:
        """Map court name to eCourts court code"""
        codes = {
            "delhi_hc": "1",
            "bombay_hc": "2",
            "madras_hc": "3",
            "calcutta_hc": "4",
            "karnataka_hc": "5",
            "allahabad_hc": "6",
            "gujarat_hc": "7",
            "rajasthan_hc": "8",
            "punjab_hc": "9",
            "kerala_hc": "10"
        }
        return codes.get(court, "1")
    
    def _normalize_surepass_response(self, data: Dict) -> Dict[str, Any]:
        """Normalize Surepass API response to standard format"""
        cnr_details = data.get("data", {}).get("cnr_details", {})
        case_details = cnr_details.get("case_details", {})
        case_status = cnr_details.get("case_status", {})
        history = cnr_details.get("case_history_details", [])
        
        petitioner = cnr_details.get("petitioner_and_advocate_details", {})
        respondents = cnr_details.get("respondent_and_advocate_details", [])
        
        return {
            "success": True,
            "source": "surepass",
            "cnr_number": data.get("data", {}).get("cnr_number", ""),
            "case_type": case_details.get("case_type", ""),
            "filing_number": case_details.get("filing_number", ""),
            "filing_date": case_details.get("filing_date", ""),
            "registration_number": case_details.get("registration_number", ""),
            "registration_date": case_details.get("registration_date", ""),
            "first_hearing_date": case_status.get("first_hearing_date", ""),
            "next_hearing_date": case_status.get("next_hearing_date", ""),
            "case_stage": case_status.get("case_stage", ""),
            "court_number": case_status.get("court_number_and_judge", ""),
            "judge": case_status.get("court_number_and_judge", ""),
            "decision_date": case_status.get("decision_date"),
            "nature_of_disposal": case_status.get("nature_of_disposal", ""),
            "petitioner": petitioner.get("petitioner", "") if isinstance(petitioner, dict) else str(petitioner),
            "petitioner_advocate": petitioner.get("advocate", "") if isinstance(petitioner, dict) else "",
            "respondents": respondents if isinstance(respondents, list) else [str(respondents)],
            "hearing_history": [
                {
                    "date": h.get("business_on_date", ""),
                    "next_date": h.get("hearing_date", ""),
                    "purpose": h.get("purpose_of_hearing", ""),
                    "judge": h.get("judge", "")
                }
                for h in history
            ],
            "case_title": f"{petitioner.get('petitioner', 'Unknown') if isinstance(petitioner, dict) else 'Unknown'} vs {respondents[0] if respondents else 'Unknown'}"
        }
    
    def _normalize_ecourts_api_response(self, data: Dict) -> Dict[str, Any]:
        """Normalize webapi.ecourtsindia.com response"""
        return {
            "success": True,
            "source": "ecourts_api",
            **data
        }
    
    def _normalize_ecourts_direct_response(self, data: Dict, cnr: str) -> Dict[str, Any]:
        """Normalize direct eCourts response"""
        return {
            "success": True,
            "source": "ecourts_direct",
            "cnr_number": cnr,
            **data
        }
    
    def _normalize_hc_response(self, data: Dict, case_type: str, case_number: str, year: str) -> Dict[str, Any]:
        """Normalize High Court response"""
        return {
            "success": True,
            "source": "hc_services",
            "case_number": f"{case_type}/{case_number}/{year}",
            **data
        }
    
    def _parse_ecourts_html(self, html: str, cnr: str) -> Dict[str, Any]:
        """Parse HTML response from eCourts as fallback"""
        from bs4 import BeautifulSoup
        import re
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            result = {
                "success": True,
                "source": "ecourts_html",
                "cnr_number": cnr
            }
            
            # Extract case details table
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        if 'next hearing' in key or 'next date' in key:
                            result['next_hearing_date'] = value
                        elif 'case status' in key or 'status' in key:
                            result['case_status'] = value
                        elif 'petitioner' in key:
                            result['petitioner'] = value
                        elif 'respondent' in key:
                            result['respondent'] = value
                        elif 'judge' in key:
                            result['judge'] = value
                        elif 'case type' in key:
                            result['case_type'] = value
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"HTML parse error: {str(e)}",
                "cnr_number": cnr
            }


# Singleton
_tracker = None

def get_case_tracker() -> CaseTrackerService:
    global _tracker
    if _tracker is None:
        _tracker = CaseTrackerService()
    return _tracker
