# Case Law Knowledge Base System

## Overview

The Case Law System provides **actual Indian legal judgments** to support authoritative legal analysis. Instead of relying only on general legal knowledge, LexMind AI now cites real cases with proper citations, holdings, and reasoning.

## Features

### 1. **Actual Case Database**
- Real Indian Supreme Court and High Court judgments
- Structured case data: facts, issues, holdings, reasoning
- Proper legal citations (e.g., "2010 3 SCC 1")
- Precedents cited in each judgment

### 2. **Intelligent Case Search**
- Semantic search using embeddings
- Filter by legal area (Contract Law, Arbitration, IP, etc.)
- Filter by court (Supreme Court, High Courts)
- Relevance scoring

### 3. **Integration with Legal RAG**
- Automatically includes relevant cases in answers
- Combines document analysis + case law
- Proper attribution with citations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query                                │
│         "What happens in software contract breach?"          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Legal RAG Service                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Document   │  │  Case Law    │  │   General    │      │
│  │   Context    │  │   Database   │  │  Knowledge   │      │
│  │  (ChromaDB)  │  │  (ChromaDB)  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Legal LLM Service                           │
│         Generates structured answer with citations           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Response                                  │
│  Answer + Explanation + Sources (with case citations)        │
└─────────────────────────────────────────────────────────────┘
```

## Database Structure

### Case Data Schema
```python
{
    "case_name": "Trimex International v. Vedanta Aluminium",
    "citation": "(2010) 3 SCC 1",
    "court": "Supreme Court of India",
    "date": "2010-01-08",
    "judges": ["Justice Dalveer Bhandari", "Justice Harjit Singh Bedi"],
    "legal_areas": ["Arbitration", "Contract Law", "Force Majeure"],
    "facts": "Summary of case facts...",
    "issues": ["Legal issue 1", "Legal issue 2"],
    "holdings": ["Court's decision 1", "Court's decision 2"],
    "reasoning": "Court's reasoning...",
    "precedents_cited": ["Case 1", "Case 2"],
    "full_text": "Complete judgment text..."
}
```

### Storage
- **ChromaDB Collection**: `indian_case_law` (for semantic search)
- **JSON Files**: `backend/case_law_db/full_texts/{case_id}.json` (for full text)

## Usage

### 1. Populate Database

```bash
cd backend
python scripts/populate_case_law.py
```

This seeds the database with 5 landmark Indian cases:
- Satyam Computer Services v. Upaid Systems (Software Licensing)
- Trimex International v. Vedanta Aluminium (Force Majeure)
- Afcons Infrastructure v. Cherian Varkey (Arbitration Limitation)
- BSNL v. Motorola India (Technology Contract Breach)
- Kailash Nath Associates v. DDA (Limitation of Liability)

### 2. Search Case Law (API)

**Endpoint**: `POST /api/query/search-case-law`

```json
{
  "query": "software contract breach remedies",
  "legal_area": "Contract Law",
  "court": "Supreme Court of India",
  "top_k": 5
}
```

**Response**:
```json
{
  "message": "Found 2 relevant case(s)",
  "cases": [
    {
      "case_name": "BSNL v. Motorola India",
      "citation": "(2009) 2 SCC 337",
      "court": "Supreme Court of India",
      "date": "2009-02-06",
      "legal_areas": ["Contract Law", "Telecommunications"],
      "issues": ["What constitutes material breach?"],
      "holdings": ["Failure to meet deadlines constitutes material breach"],
      "relevance_score": 0.87,
      "excerpt": "...",
      "case_id": "case_20260427_BSNL_v_Motorola"
    }
  ]
}
```

### 3. Get Case Details

**Endpoint**: `GET /api/query/case-law/{case_id}`

Returns complete judgment including full text, reasoning, and precedents cited.

### 4. Database Statistics

**Endpoint**: `GET /api/query/case-law-stats`

```json
{
  "total_cases": 5,
  "courts": ["Supreme Court of India", "Delhi High Court"],
  "legal_areas": ["Contract Law", "Arbitration", "Software Licensing", ...],
  "last_updated": "2026-04-27T..."
}
```

### 5. Automatic Integration

When asking legal questions via `/api/query/ask`, case law is automatically included:

```json
{
  "query": "What are remedies for software contract breach?",
  "doc_id": null
}
```

Response includes:
- Document context (if available)
- **Relevant case law with citations**
- General legal knowledge
- Structured answer with confidence level

## Adding More Cases

### Manual Addition

```python
from backend.services.case_law_service import get_case_law_service

service = get_case_law_service()

case_data = {
    "case_name": "Your Case Name",
    "citation": "2024 SCC 123",
    "court": "Supreme Court of India",
    "date": "2024-01-15",
    "judges": ["Justice Name"],
    "legal_areas": ["Contract Law"],
    "facts": "...",
    "issues": ["..."],
    "holdings": ["..."],
    "reasoning": "...",
    "precedents_cited": ["..."],
    "full_text": "..."
}

case_id = service.add_case(case_data)
print(f"Added case: {case_id}")
```

### Bulk Import (Future)

Planned integrations:
- **Indian Kanoon API**: Scrape judgments automatically
- **SCC Online**: Import from subscription
- **Manual Upload**: Upload PDF judgments with OCR
- **Web Scraping**: High Court websites

## Benefits Over General Knowledge

| Feature | General Knowledge | Case Law Database |
|---------|------------------|-------------------|
| **Authority** | Generic principles | Actual court decisions |
| **Citations** | "Generally courts say..." | "In *BSNL v. Motorola* (2009) 2 SCC 337..." |
| **Specificity** | Broad statements | Specific holdings and reasoning |
| **Precedent Value** | Low | High (binding/persuasive) |
| **Confidence** | Medium | High (backed by actual cases) |
| **Verifiability** | Hard to verify | Can be looked up |

## Example Comparison

### Before (General Knowledge):
```
Answer: Indian courts generally hold that software contract breaches 
are governed by the Indian Contract Act, 1872...

Sources: [General Legal Knowledge]
Confidence: Medium
```

### After (With Case Law):
```
Answer: In software contract breach cases, Indian courts emphasize 
timely delivery and meeting specifications. In *BSNL v. Motorola India* 
(2009) 2 SCC 337, the Supreme Court held that failure to meet delivery 
deadlines and performance specifications constitutes material breach 
justifying termination...

Sources: 
- Case Law: BSNL v. Motorola India (2009) 2 SCC 337
- Case Law: Satyam Computer Services v. Upaid Systems (2008)
- General Legal Knowledge: Indian Contract Act, 1872

Confidence: High - Based on Supreme Court precedents
```

## Future Enhancements

1. **Automated Case Scraping**: Integrate with Indian Kanoon API
2. **Citation Network**: Map relationships between cases
3. **Temporal Analysis**: Track how legal principles evolved
4. **Jurisdiction Mapping**: State-specific High Court variations
5. **Case Summarization**: AI-generated case summaries
6. **Precedent Strength**: Calculate binding vs persuasive value
7. **Conflict Detection**: Identify conflicting judgments
8. **Update Alerts**: Notify when new relevant cases are decided

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/query/ask` | POST | Ask legal question (auto includes case law) |
| `/api/query/search-case-law` | POST | Search case law database |
| `/api/query/case-law/{case_id}` | GET | Get full case details |
| `/api/query/case-law-stats` | GET | Database statistics |

## Maintenance

### Backup Database
```bash
# Backup ChromaDB
cp -r backend/case_law_db backend/case_law_db_backup_$(date +%Y%m%d)

# Backup full texts
tar -czf case_law_texts_$(date +%Y%m%d).tar.gz backend/case_law_db/full_texts/
```

### Update Cases
```bash
python backend/scripts/populate_case_law.py  # Re-run to add new cases
```

### Clear Database
```bash
rm -rf backend/case_law_db  # Will be recreated on next run
```

## Legal Disclaimer

This case law database is for informational purposes only. While we strive for accuracy:
- Cases may be summarized or excerpted
- Legal principles evolve over time
- Always verify citations with official sources
- Consult qualified legal professionals for advice

---

**Status**: ✅ Implemented and Ready
**Last Updated**: April 27, 2026
**Cases in Database**: 5 landmark Indian judgments
**Next Steps**: Populate with more cases, integrate with Indian Kanoon API
