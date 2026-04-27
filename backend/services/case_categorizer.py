"""
AI-powered case categorization service
Uses LLM to automatically categorize and extract metadata from legal cases
"""

import json
import logging
from typing import Dict, Any
from .llm_service import LLMService

logger = logging.getLogger(__name__)

class CaseCategorizer:
    """Automatically categorize legal cases using LLM"""
    
    # Legal category definitions
    CATEGORIES = {
        "Contract Law": ["contract", "agreement", "breach", "performance", "consideration"],
        "Corporate Law": ["company", "director", "shareholder", "corporate", "board"],
        "Intellectual Property": ["patent", "trademark", "copyright", "IP", "infringement"],
        "Employment Law": ["employment", "termination", "wages", "labor", "employee"],
        "Real Estate": ["property", "land", "lease", "title", "real estate"],
        "Arbitration": ["arbitration", "arbitrator", "award", "arbitral"],
        "Cyber Law": ["cyber", "data", "privacy", "internet", "electronic"],
        "Tax Law": ["tax", "income tax", "gst", "revenue", "assessment"],
        "Banking & Finance": ["bank", "loan", "finance", "securities", "credit"],
        "Consumer Protection": ["consumer", "defective", "service deficiency", "unfair trade"],
        "Criminal Law": ["criminal", "offence", "prosecution", "accused", "conviction"],
        "Constitutional Law": ["constitution", "fundamental rights", "article", "writ"]
    }
    
    def __init__(self):
        self.llm = LLMService()
    
    def categorize_case(self, case_text: str, case_name: str, citation: str = "") -> Dict[str, Any]:
        """
        Automatically categorize a case and extract metadata
        
        Args:
            case_text: Full or partial judgment text
            case_name: Name of the case
            citation: Citation (if available)
        
        Returns:
            Dictionary with category, subcategory, legal areas, importance, etc.
        """
        try:
            # Truncate text for LLM (use first 3000 chars)
            excerpt = case_text[:3000] if len(case_text) > 3000 else case_text
            
            prompt = f"""You are a legal expert analyzing Indian court judgments. Analyze this case and extract structured metadata.

Case Name: {case_name}
Citation: {citation}

Case Text (excerpt):
{excerpt}

Analyze this case and return ONLY a valid JSON object with this exact structure:
{{
    "category": "one of: Contract Law, Corporate Law, Intellectual Property, Employment Law, Real Estate, Arbitration, Cyber Law, Tax Law, Banking & Finance, Consumer Protection, Criminal Law, Constitutional Law",
    "subcategory": "specific subcategory (e.g., 'Software Contracts', 'Trademark Infringement')",
    "legal_areas": ["area1", "area2", "area3"],
    "importance": "one of: Landmark, Important, Regular",
    "key_principles": ["principle1", "principle2"],
    "applicable_acts": ["Act name 1", "Act name 2"],
    "issues_summary": "brief summary of main legal issues",
    "holdings_summary": "brief summary of court's main holdings"
}}

Rules:
- Choose the MOST relevant category
- Be specific in subcategory
- List 2-5 legal areas
- Landmark = Supreme Court precedent-setting case
- Important = High Court important decision or SC regular case
- Regular = routine case
- Return ONLY valid JSON, no other text"""

            response = self.llm.generate_response(prompt)
            
            # Parse JSON response
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            metadata = json.loads(response)
            
            logger.info(f"Categorized case: {case_name} -> {metadata['category']}")
            return metadata
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response was: {response}")
            # Return default categorization
            return self._default_categorization(case_text, case_name)
        except Exception as e:
            logger.error(f"Error categorizing case: {str(e)}")
            return self._default_categorization(case_text, case_name)
    
    def _default_categorization(self, case_text: str, case_name: str) -> Dict[str, Any]:
        """Fallback categorization using keyword matching"""
        case_lower = (case_text + " " + case_name).lower()
        
        # Find best matching category
        best_category = "General"
        best_score = 0
        
        for category, keywords in self.CATEGORIES.items():
            score = sum(1 for keyword in keywords if keyword in case_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        return {
            "category": best_category,
            "subcategory": "General",
            "legal_areas": [best_category],
            "importance": "Regular",
            "key_principles": [],
            "applicable_acts": [],
            "issues_summary": "Auto-categorized based on keywords",
            "holdings_summary": "See full case text"
        }
    
    def extract_structured_data(self, case_text: str) -> Dict[str, Any]:
        """
        Extract structured data from case text
        
        Returns:
            Dictionary with parties, dates, amounts, etc.
        """
        try:
            excerpt = case_text[:4000] if len(case_text) > 4000 else case_text
            
            prompt = f"""Extract structured data from this legal case.

Case Text:
{excerpt}

Return ONLY a valid JSON object:
{{
    "parties": {{
        "appellant": "name",
        "respondent": "name"
    }},
    "court": "court name",
    "judges": ["judge1", "judge2"],
    "date": "YYYY-MM-DD or empty string",
    "citation": "citation or empty string",
    "case_type": "Civil/Criminal/Constitutional",
    "bench_strength": 1,
    "key_dates": ["date1", "date2"],
    "monetary_amounts": ["amount1", "amount2"]
}}

Return ONLY valid JSON."""

            response = self.llm.generate_response(prompt)
            
            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {str(e)}")
            return {}


# Singleton instance
_categorizer = None

def get_case_categorizer() -> CaseCategorizer:
    """Get or create CaseCategorizer singleton"""
    global _categorizer
    if _categorizer is None:
        _categorizer = CaseCategorizer()
    return _categorizer
