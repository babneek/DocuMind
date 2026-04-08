"""
DocuMind RAG Benchmark Suite
Automated testing and validation of RAG system accuracy, latency, and reliability
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Tuple
import statistics

BASE_URL = "http://localhost:8000/api"

# Test credentials
TEST_EMAIL = "benchmark@test.com"
TEST_PASSWORD = "benchmark_password_123"

class BenchmarkQuery:
    def __init__(self, question: str, category: str, must_include: List[str], nice_to_have: List[str] = None):
        self.question = question
        self.category = category  # easy, medium, hard, edge_case
        self.must_include = must_include  # Critical facts that must be in answer
        self.nice_to_have = nice_to_have or []
        self.response = None
        self.latency = 0
        self.score = 0

class BenchmarkSuite:
    def __init__(self):
        self.token = None
        self.doc_id = None
        self.queries: List[BenchmarkQuery] = []
        self.results = {
            "easy": [],
            "medium": [],
            "hard": [],
            "edge_case": []
        }
        
    def setup(self):
        """Authenticate and get/set up test document"""
        print("[SETUP] Initializing benchmark suite...")
        
        # Sign up / login
        try:
            signup_resp = requests.post(
                f"{BASE_URL}/auth/signup",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
            )
            if signup_resp.status_code == 400 and "already registered" in signup_resp.text:
                # Already registered, login instead
                login_resp = requests.post(
                    f"{BASE_URL}/auth/login",
                    data={"username": TEST_EMAIL, "password": TEST_PASSWORD}
                )
                self.token = login_resp.json()["access_token"]
                print(f"[AUTH] Logged in as {TEST_EMAIL}")
            else:
                self.token = signup_resp.json()["access_token"]
                print(f"[AUTH] Signed up new user: {TEST_EMAIL}")
        except Exception as e:
            print(f"[ERROR] Auth failed: {e}")
            return False
        
        # Get or upload test document
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            docs = requests.get(f"{BASE_URL}/documents/", headers=headers).json()
            
            if docs and len(docs) > 0:
                self.doc_id = docs[0]["id"]
                print(f"[SETUP] Using existing document: {docs[0]['file_name']}")
            else:
                # Try to upload the smaller test document for faster testing
                test_file = "test_financial_report_small.txt"
                if not os.path.exists(test_file):
                    test_file = "test_financial_report.txt"
                
                print(f"[SETUP] No documents found. Uploading {test_file}...")
                with open(test_file, "rb") as f:
                    files = {"file": f}
                    upload_resp = requests.post(
                        f"{BASE_URL}/upload/",
                        headers={"Authorization": f"Bearer {self.token}"},
                        files=files
                    )
                    if upload_resp.status_code == 200:
                        self.doc_id = upload_resp.json().get("id")
                        print(f"[SETUP] Document uploaded successfully: {self.doc_id}")
                        time.sleep(3)  # Wait for indexing to complete
                    else:
                        print(f"[SETUP] Upload failed: {upload_resp.status_code}")
                        return False
        except FileNotFoundError:
            print("[ERROR] test_financial_report.txt not found in current directory")
            return False
        except Exception as e:
            print(f"[ERROR] Document lookup/upload failed: {e}")
            return False
        
        print("[SETUP] ✓ Benchmark suite initialized")
        return True
    
    def add_query(self, question: str, category: str, must_include: List[str], nice_to_have: List[str] = None):
        """Add a benchmark query"""
        self.queries.append(BenchmarkQuery(question, category, must_include, nice_to_have))
    
    def load_default_queries(self):
        """Load comprehensive benchmark query set"""
        queries = [
            # EASY - Single fact lookups
            ("What was TechCorp's total revenue in FY2025?", "easy",
                ["2.45 billion", "$2,450,000,000", "18.5%"], ["year-over-year"]),
            
            ("What was the company's net income in FY2025?", "easy",
                ["$487 million", "487,000,000", "25.2%"], ["increase"]),
            
            ("What is the company's current ratio?", "easy",
                ["2.0x", "2.0"], []),
            
            ("How much cash does the company have?", "easy",
                ["$520 million", "$520,000,000"], ["equivalents"]),
            
            # MEDIUM - Multi-part analysis
            ("Compare the company's gross margin and operating margin. What drove the difference?", "medium",
                ["45%", "25%", "operating expenses", "operating expense"], 
                ["R&D", "Sales & Marketing", "General & Administrative"]),
            
            ("Which business segment had the fastest growth rate?", "medium",
                ["28%", "Support & Services"], ["fastest", "growth"]),
            
            ("What were the main risk factors described in the report?", "medium",
                ["Market Risks", "Operational Risks", "Strategic Risks"],
                ["competition", "talent retention", "customer concentration"]),
            
            ("How much operating cash flow did the company generate, and what were the biggest outflows?", "medium",
                ["$623 million", "Capital Expenditure", "Acquisitions", "Debt Repayment"],
                ["245 million", "120 million", "155 million"]),
            
            # HARD - Cross-section reasoning
            ("Which geographic region had the highest growth rate, and how did it compare to others?", "hard",
                ["Mexico", "28%", "Canada", "22%", "United States", "16%"],
                ["North America"]),
            
            ("Analyze the company's debt position relative to its equity and cash position. Is it healthy?", "hard",
                ["0.58x", "Debt-to-Equity", "980 million", "1,225 billion", "healthy", "below"],
                ["interest coverage", "strong liquidity"]),
            
            ("What is driving revenue growth across different segments, and which has momentum?", "hard",
                ["SaaS", "25%", "Support", "28%", "Cloud", "enterprise adoption"],
                ["Infrastructure", "IoT"]),
            
            ("Based on the financial metrics, what is TechCorp's strategic position?", "hard",
                ["strong", "profitable", "growth", "cash generation", "returns"],
                ["margin expansion", "international"]),
            
            # EDGE CASES - Tricky/complex
            ("What is the Board's plan for dividends?", "edge_case",
                ["quarterly dividend increase", "$0.175", "FY2026"],
                ["$0.69"]),
            
            ("What percentage of revenue comes from the top 10 customers?", "edge_case",
                ["22%", "concentration", "risk"],
                ["top 10"]),
            
            ("What is the expected revenue for FY2026 and what is driving it?", "edge_case",
                ["2,868 billion", "$2.868 billion", "17%", "Cloud", "43%"],
                ["AI/ML", "IoT"]),
        ]
        
        for q, cat, must, nice in queries:
            self.add_query(q, cat, must, nice)
        
        print(f"[SETUP] Loaded {len(self.queries)} benchmark queries")
    
    def score_response(self, query: BenchmarkQuery) -> float:
        """
        Score a response based on presence of required facts
        Returns: 0-100 score
        """
        if not query.response:
            return 0
        
        response_lower = query.response.lower()
        
        # Check must_include items
        must_found = sum(1 for item in query.must_include if item.lower() in response_lower)
        must_score = (must_found / len(query.must_include)) * 80  # 80% weight to must_have
        
        # Check nice_to_have items
        nice_score = 0
        if query.nice_to_have:
            nice_found = sum(1 for item in query.nice_to_have if item.lower() in response_lower)
            nice_score = (nice_found / len(query.nice_to_have)) * 20  # 20% weight to nice_to_have
        
        final_score = min(100, must_score + nice_score)
        return final_score
    
    def run_benchmark(self):
        """Execute all benchmark queries"""
        print("\n[BENCHMARK] Starting query execution...")
        print(f"[BENCHMARK] Total queries: {len(self.queries)}\n")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        latencies = []
        
        for idx, query in enumerate(self.queries, 1):
            print(f"[Q{idx}] [{query.category.upper()}] {query.question[:60]}...", end=" ")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{BASE_URL}/query/ask",
                    headers=headers,
                    json={"query": query.question, "doc_id": self.doc_id}
                )
                query.latency = (time.time() - start_time) * 1000  # ms
                latencies.append(query.latency)
                
                if response.status_code == 200:
                    query.response = response.json().get("answer", "")
                    query.score = self.score_response(query)
                    self.results[query.category].append(query.score)
                    
                    status = "✓" if query.score >= 80 else "⚠" if query.score >= 60 else "✗"
                    print(f"{status} Score: {query.score:.1f}% | Latency: {query.latency:.0f}ms")
                else:
                    print(f"✗ Error: {response.status_code}")
                    self.results[query.category].append(0)
            
            except Exception as e:
                print(f"✗ Exception: {str(e)[:50]}")
                self.results[query.category].append(0)
        
        return latencies
    
    def generate_report(self, latencies: List[float]):
        """Generate comprehensive benchmark report"""
        print("\n" + "="*70)
        print("BENCHMARK REPORT - DocuMind RAG System")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Overall accuracy
        all_scores = []
        for scores in self.results.values():
            all_scores.extend(scores)
        
        overall_accuracy = statistics.mean(all_scores) if all_scores else 0
        print(f"\nOVERALL ACCURACY: {overall_accuracy:.1f}%")
        print(f"Previous Baseline: 75.0%")
        print(f"Improvement: +{overall_accuracy - 75:.1f}%\n")
        
        # Category breakdown
        print("CATEGORY BREAKDOWN:")
        print("-" * 70)
        for category in ["easy", "medium", "hard", "edge_case"]:
            scores = self.results[category]
            if scores:
                avg = statistics.mean(scores)
                min_s = min(scores)
                max_s = max(scores)
                print(f"  {category.upper():12} | Avg: {avg:5.1f}% | Min: {min_s:5.1f}% | Max: {max_s:5.1f}% | N={len(scores)}")
        
        # Latency analysis
        print("\nLATENCY ANALYSIS:")
        print("-" * 70)
        if latencies:
            print(f"  Mean:      {statistics.mean(latencies):6.0f} ms")
            print(f"  Median:    {statistics.median(latencies):6.0f} ms")
            print(f"  Std Dev:   {statistics.stdev(latencies) if len(latencies) > 1 else 0:6.0f} ms")
            print(f"  Min:       {min(latencies):6.0f} ms")
            print(f"  Max:       {max(latencies):6.0f} ms")
            print(f"  P95:       {sorted(latencies)[int(len(latencies)*0.95)]:6.0f} ms")
        
        # Pass/Fail counts
        print("\nQUALITY METRICS:")
        print("-" * 70)
        excellent = sum(1 for s in all_scores if s >= 90)
        good = sum(1 for s in all_scores if 80 <= s < 90)
        fair = sum(1 for s in all_scores if 60 <= s < 80)
        poor = sum(1 for s in all_scores if s < 60)
        total = len(all_scores)
        
        print(f"  Excellent (90-100%): {excellent:2d}/{total} ({excellent/total*100:5.1f}%)")
        print(f"  Good (80-89%):       {good:2d}/{total} ({good/total*100:5.1f}%)")
        print(f"  Fair (60-79%):       {fair:2d}/{total} ({fair/total*100:5.1f}%)")
        print(f"  Poor (<60%):         {poor:2d}/{total} ({poor/total*100:5.1f}%)")
        
        # Failed queries
        failed = [(q.question, q.score) for q in self.queries if q.score < 70]
        if failed:
            print("\nFAILED QUERIES (Score < 70%):")
            print("-" * 70)
            for q, score in failed[:5]:
                print(f"  [{score:.0f}%] {q[:65]}")
            if len(failed) > 5:
                print(f"  ... and {len(failed) - 5} more")
        
        # Summary recommendation
        print("\nRECOMMENDATION:")
        print("-" * 70)
        if overall_accuracy >= 90:
            print("  ✓ EXCELLENT - System is production-ready")
        elif overall_accuracy >= 80:
            print("  ✓ GOOD - System performing well, minor improvements needed")
        elif overall_accuracy >= 70:
            print("  ⚠ FAIR - System needs optimization before production")
        else:
            print("  ✗ POOR - System requires significant improvements")
        
        print("\n" + "="*70)
        
        # Save to file
        report_file = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_accuracy": overall_accuracy,
            "latency_stats": {
                "mean": statistics.mean(latencies) if latencies else 0,
                "median": statistics.median(latencies) if latencies else 0,
                "min": min(latencies)  if latencies else 0,
                "max": max(latencies) if latencies else 0,
            },
            "category_results": {cat: {"scores": scores, "avg": statistics.mean(scores) if scores else 0} 
                                for cat, scores in self.results.items()},
            "queries_count": len(self.queries),
        }
        
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)
        print(f"Report saved to: {report_file}")

def main():
    print("\n" + "="*70)
    print("DocuMind RAG System - Automated Benchmark Suite")
    print("="*70)
    
    # Initialize
    suite = BenchmarkSuite()
    if not suite.setup():
        print("[ERROR] Setup failed. Exiting.")
        return
    
    # Load and run queries
    suite.load_default_queries()
    latencies = suite.run_benchmark()
    
    # Generate report
    suite.generate_report(latencies)

if __name__ == "__main__":
    main()
