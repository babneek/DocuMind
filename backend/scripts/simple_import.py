"""
Simple import script that works on Render
Run this directly: python backend/scripts/simple_import.py
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

print("Starting simple case law import...")
print(f"Backend directory: {backend_dir}")

try:
    # Import the populate script which has the 5 manual cases
    from scripts.populate_case_law import populate_database
    
    print("\nImporting 5 foundation cases...")
    populate_database()
    
    print("\n✅ Import complete!")
    print("You now have 5 landmark cases in your database.")
    print("\nTo import more cases, run the bulk import locally:")
    print("  python backend/scripts/quick_import_100_cases.py")
    
except Exception as e:
    import traceback
    print(f"\n❌ Error: {str(e)}")
    print(traceback.format_exc())
    sys.exit(1)
