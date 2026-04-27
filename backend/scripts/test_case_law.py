"""
Test script to demonstrate case law search functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.case_law_service import get_case_law_service
import json

def test_case_law_search():
    """Test various case law searches"""
    
    service = get_case_law_service()
    
    print("="*80)
    print("CASE LAW DATABASE TEST")
    print("="*80)
    print()
    
    # Test 1: Database stats
    print("📊 DATABASE STATISTICS")
    print("-" * 80)
    stats = service.get_database_stats()
    print(f"Total Cases: {stats['total_cases']}")
    print(f"Courts: {', '.join(stats['courts'])}")
    print(f"Legal Areas: {', '.join(stats['legal_areas'])}")
    print()
    
    # Test 2: Search for software contract breach
    print("🔍 TEST 1: Software Contract Breach")
    print("-" * 80)
    query1 = "software contract breach remedies damages"
    cases1 = service.search_cases(query1, top_k=3)
    print(f"Query: '{query1}'")
    print(f"Found {len(cases1)} relevant case(s):\n")
    
    for i, case in enumerate(cases1, 1):
        print(f"{i}. {case['case_name']}")
        print(f"   Citation: {case['citation']}")
        print(f"   Court: {case['court']}")
        print(f"   Relevance: {case['relevance_score']:.2%}")
        print(f"   Key Holding: {case['holdings'][0] if case['holdings'] else 'N/A'}")
        print()
    
    # Test 3: Search for force majeure
    print("🔍 TEST 2: Force Majeure")
    print("-" * 80)
    query2 = "force majeure economic hardship market conditions"
    cases2 = service.search_cases(query2, legal_area="Contract Law", top_k=2)
    print(f"Query: '{query2}'")
    print(f"Filter: Contract Law")
    print(f"Found {len(cases2)} relevant case(s):\n")
    
    for i, case in enumerate(cases2, 1):
        print(f"{i}. {case['case_name']}")
        print(f"   Citation: {case['citation']}")
        print(f"   Date: {case['date']}")
        print(f"   Relevance: {case['relevance_score']:.2%}")
        print(f"   Issues: {' | '.join(case['issues'][:2])}")
        print()
    
    # Test 4: Search for arbitration
    print("🔍 TEST 3: Arbitration Limitation")
    print("-" * 80)
    query3 = "arbitration limitation period delay"
    cases3 = service.search_cases(query3, legal_area="Arbitration", top_k=2)
    print(f"Query: '{query3}'")
    print(f"Filter: Arbitration")
    print(f"Found {len(cases3)} relevant case(s):\n")
    
    for i, case in enumerate(cases3, 1):
        print(f"{i}. {case['case_name']}")
        print(f"   Citation: {case['citation']}")
        print(f"   Court: {case['court']}")
        print(f"   Relevance: {case['relevance_score']:.2%}")
        print()
    
    # Test 5: Get full case details
    if cases1:
        print("📄 TEST 4: Full Case Details")
        print("-" * 80)
        case_id = cases1[0]['case_id']
        full_case = service.get_case_by_id(case_id)
        print(f"Case ID: {case_id}")
        print(f"Case Name: {full_case['case_name']}")
        print(f"Citation: {full_case['citation']}")
        print(f"\nFacts (excerpt):")
        print(full_case['facts'][:300] + "...")
        print(f"\nReasoning (excerpt):")
        print(full_case['reasoning'][:300] + "...")
        print(f"\nPrecedents Cited:")
        for prec in full_case['precedents_cited']:
            print(f"  - {prec}")
        print()
    
    # Test 6: Filter by Supreme Court only
    print("🔍 TEST 5: Supreme Court Cases Only")
    print("-" * 80)
    query4 = "contract breach liability"
    cases4 = service.search_cases(query4, court="Supreme Court of India", top_k=5)
    print(f"Query: '{query4}'")
    print(f"Filter: Supreme Court of India")
    print(f"Found {len(cases4)} relevant case(s):\n")
    
    for i, case in enumerate(cases4, 1):
        print(f"{i}. {case['case_name']} - {case['citation']}")
    print()
    
    print("="*80)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*80)


if __name__ == "__main__":
    test_case_law_search()
