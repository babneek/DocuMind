"""
Quick Import: 100 Foundation Cases
Imports 100 high-quality landmark cases across all major categories
Estimated time: 30-45 minutes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bulk_import_cases import BulkCaseImporter
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    LEXMIND AI - CASE LAW IMPORTER                           ║
║                                                                              ║
║                    Importing 100 Foundation Cases                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

This will import approximately 100 landmark Indian legal cases across:
  • Contract Law (20 cases)
  • Corporate Law (15 cases)
  • Intellectual Property (15 cases)
  • Employment Law (10 cases)
  • Real Estate (10 cases)
  • Arbitration (10 cases)
  • Cyber Law (10 cases)
  • Tax Law (5 cases)
  • Banking & Finance (5 cases)

Estimated time: 30-45 minutes
Source: Indian Kanoon (free legal database)

The system will:
  1. Search for landmark cases in each category
  2. Fetch full judgment text
  3. Auto-categorize using AI
  4. Extract metadata (issues, holdings, etc.)
  5. Check for duplicates
  6. Add to your case law database

Press Ctrl+C to cancel at any time.
""")
    
    input("Press Enter to start import...")
    
    print("\n🚀 Starting import...\n")
    
    importer = BulkCaseImporter()
    importer.import_foundation_cases()
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                         IMPORT COMPLETE! ✓                                  ║
║                                                                              ║
║  Your case law database is now populated with landmark Indian cases.        ║
║                                                                              ║
║  Next steps:                                                                 ║
║    1. Test the system: python scripts/test_case_law.py                      ║
║    2. Check stats: GET /api/query/case-law-stats                            ║
║    3. Search cases: POST /api/query/search-case-law                         ║
║                                                                              ║
║  To import more cases:                                                       ║
║    python scripts/bulk_import_cases.py --mode full                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
