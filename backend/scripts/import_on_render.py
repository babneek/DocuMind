"""
Run this script on Render to import cases directly on the server
Can be triggered via API endpoint or Render shell
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bulk_import_cases import BulkCaseImporter
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("Starting case import on Render...")
    
    importer = BulkCaseImporter()
    
    # Import foundation cases (100 cases)
    importer.import_foundation_cases()
    
    print("Import complete! Cases are now available in production.")

if __name__ == "__main__":
    main()
