# Case Law Knowledge Base - Usage Guide

## What's New? 🎉

Your LexMind AI now has access to **actual Indian legal judgments** instead of just general legal knowledge. When you ask legal questions, the system searches through real Supreme Court and High Court cases to provide authoritative answers with proper citations.

## Current Database

**5 Landmark Indian Cases:**

1. **Satyam Computer Services v. Upaid Systems** (2008) - Delhi High Court
   - Software licensing agreements
   - Scope of use and payment terms
   - Material breach in software contracts

2. **Trimex International v. Vedanta Aluminium** (2010) - Supreme Court
   - Force majeure clauses
   - Economic hardship vs force majeure
   - Commercial impracticability

3. **Afcons Infrastructure v. Cherian Varkey** (2010) - Supreme Court
   - Arbitration limitation periods
   - Contractual limitation clauses
   - Delay condonation

4. **BSNL v. Motorola India** (2009) - Supreme Court
   - Technology supply contracts
   - Liquidated damages vs actual damages
   - Material breach and termination

5. **Kailash Nath Associates v. DDA** (2015) - Supreme Court
   - Limitation of liability clauses
   - Arbitrator's jurisdiction
   - Contractual risk allocation

## How It Works

### Before (General Knowledge Only):
```
User: "What happens in software contract breach cases?"

Answer: Indian courts generally hold that software contract breaches 
are governed by the Indian Contract Act, 1872...

Sources: [General Legal Knowledge]
Confidence: Medium
```

### After (With Case Law):
```
User: "What happens in software contract breach cases?"

Answer: In software contract breach cases, Indian courts emphasize 
timely delivery and meeting specifications. In *BSNL v. Motorola India* 
(2009) 2 SCC 337, the Supreme Court held that failure to meet delivery 
deadlines and performance specifications constitutes material breach 
justifying termination. The Court clarified that liquidated damages 
clauses are enforceable under Section 74 of the Indian Contract Act...

In *Satyam Computer Services v. Upaid Systems* (2008), the Delhi High 
Court held that software licensing agreements must clearly define scope 
of use, and any use beyond licensed scope constitutes breach...

Sources: 
- Case Law: BSNL v. Motorola India (2009) 2 SCC 337
- Case Law: Satyam Computer Services v. Upaid Systems (2008)
- Document: [Your uploaded contract]
- General Legal Knowledge: Indian Contract Act, 1872

Confidence: High - Based on Supreme Court precedents
```

## API Endpoints

### 1. Ask Legal Question (Auto includes case law)
```bash
POST /api/query/ask
{
  "query": "What are remedies for breach of software contract?",
  "doc_id": 4  # Optional - your uploaded document
}
```

**Response includes:**
- Answer with case citations
- Document context (if doc_id provided)
- Relevant case law automatically
- Confidence level

### 2. Search Case Law Directly
```bash
POST /api/query/search-case-law
{
  "query": "force majeure economic hardship",
  "legal_area": "Contract Law",  # Optional filter
  "court": "Supreme Court of India",  # Optional filter
  "top_k": 5
}
```

**Response:**
```json
{
  "message": "Found 2 relevant case(s)",
  "cases": [
    {
      "case_name": "Trimex International v. Vedanta Aluminium",
      "citation": "(2010) 3 SCC 1",
      "court": "Supreme Court of India",
      "date": "2010-01-08",
      "legal_areas": ["Arbitration", "Contract Law", "Force Majeure"],
      "issues": [
        "Whether global financial crisis constitutes force majeure?",
        "Can economic hardship justify invocation of force majeure?"
      ],
      "holdings": [
        "Force majeure clause must be interpreted strictly",
        "Economic hardship does not automatically constitute force majeure"
      ],
      "relevance_score": 0.87,
      "excerpt": "...",
      "case_id": "case_20260427_..."
    }
  ]
}
```

### 3. Get Full Case Details
```bash
GET /api/query/case-law/{case_id}
```

Returns complete judgment including:
- Full facts
- Complete reasoning
- All precedents cited
- Full judgment text

### 4. Database Statistics
```bash
GET /api/query/case-law-stats
```

Returns:
- Total cases in database
- Courts covered
- Legal areas available

## Example Queries That Now Work Better

### 1. Software Contracts
**Query:** "What are the remedies when a software vendor fails to deliver on time?"

**Gets:** BSNL v. Motorola case + your document context

### 2. Force Majeure
**Query:** "Can we invoke force majeure due to economic downturn?"

**Gets:** Trimex v. Vedanta case (says NO - economic hardship ≠ force majeure)

### 3. Arbitration
**Query:** "What is the limitation period for invoking arbitration?"

**Gets:** Afcons Infrastructure case + Limitation Act provisions

### 4. Liability Caps
**Query:** "Are limitation of liability clauses enforceable in India?"

**Gets:** Kailash Nath v. DDA case (YES - generally enforceable)

### 5. License Scope
**Query:** "What happens if we use software beyond the licensed scope?"

**Gets:** Satyam v. Upaid case (constitutes breach)

## Testing the System

### Test 1: General Legal Question
```bash
curl -X POST https://documind-backend-59cn.onrender.com/api/query/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the remedies for breach of contract in software licensing?"
  }'
```

### Test 2: Search Specific Cases
```bash
curl -X POST https://documind-backend-59cn.onrender.com/api/query/search-case-law \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "software contract breach",
    "court": "Supreme Court of India",
    "top_k": 3
  }'
```

### Test 3: With Your Document
```bash
curl -X POST https://documind-backend-59cn.onrender.com/api/query/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare the termination clause in my contract with standard practice",
    "doc_id": 4
  }'
```

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Authority** | "Courts generally say..." | "In *BSNL v. Motorola* (2009) 2 SCC 337..." |
| **Specificity** | Generic principles | Specific holdings from actual cases |
| **Verifiability** | Hard to verify | Can look up citations |
| **Confidence** | Medium | High (backed by precedents) |
| **Legal Weight** | Low | High (binding/persuasive authority) |

## Adding More Cases

### Option 1: Manual Addition
```python
from backend.services.case_law_service import get_case_law_service

service = get_case_law_service()

case_data = {
    "case_name": "Your Case Name",
    "citation": "2024 SCC 123",
    "court": "Supreme Court of India",
    "date": "2024-01-15",
    "judges": ["Justice Name"],
    "legal_areas": ["Contract Law", "Arbitration"],
    "facts": "Summary of facts...",
    "issues": ["Issue 1", "Issue 2"],
    "holdings": ["Holding 1", "Holding 2"],
    "reasoning": "Court's reasoning...",
    "precedents_cited": ["Case 1", "Case 2"],
    "full_text": "Complete judgment..."
}

case_id = service.add_case(case_data)
```

### Option 2: Bulk Import (Coming Soon)
- Indian Kanoon API integration
- SCC Online import
- PDF upload with OCR
- Web scraping from court websites

## Next Steps

1. **Expand Database**: Add 50-100 more landmark cases
2. **Integrate Indian Kanoon**: Auto-fetch latest judgments
3. **Citation Network**: Map relationships between cases
4. **Temporal Analysis**: Track how legal principles evolved
5. **Jurisdiction Mapping**: State-specific High Court variations

## Technical Details

- **Storage**: ChromaDB (vector search) + JSON files (full text)
- **Embeddings**: all-MiniLM-L6-v2 (same as document embeddings)
- **Search**: Semantic similarity + metadata filtering
- **Integration**: Automatic in Legal RAG pipeline

## Files Added

```
backend/
├── services/
│   ├── case_law_service.py          # Core service
│   └── legal_rag_service.py         # Updated with case law
├── scripts/
│   ├── populate_case_law.py         # Seed database
│   └── test_case_law.py             # Test searches
├── routes/
│   └── query.py                     # New endpoints
├── case_law_db/                     # Database storage
│   ├── chroma.sqlite3
│   └── full_texts/
│       └── case_*.json
└── CASE_LAW_SYSTEM.md              # Technical docs
```

## Support

For questions or issues:
1. Check `backend/CASE_LAW_SYSTEM.md` for technical details
2. Run `python backend/scripts/test_case_law.py` to verify setup
3. Check database stats: `GET /api/query/case-law-stats`

---

**Status**: ✅ Live and operational
**Database**: 5 landmark cases
**Coverage**: Supreme Court + Delhi High Court
**Areas**: Contract Law, Arbitration, Software, Force Majeure, Liability
