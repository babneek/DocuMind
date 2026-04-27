# 🚀 Quick Start - Case Law Knowledge Base

## One Command to Rule Them All

```bash
cd backend
python scripts/quick_import_100_cases.py
```

**That's it!** In 30-45 minutes, you'll have 100 landmark Indian cases.

---

## What Happens

1. ✅ Searches Indian Kanoon for landmark cases
2. ✅ Fetches full judgment text
3. ✅ AI categorizes each case
4. ✅ Extracts metadata (issues, holdings, etc.)
5. ✅ Checks for duplicates
6. ✅ Adds to your database

---

## What You Get

```
Contract Law: 20 cases
Corporate Law: 15 cases
Intellectual Property: 15 cases
Employment Law: 10 cases
Real Estate: 10 cases
Arbitration: 10 cases
Cyber Law: 10 cases
Tax Law: 5 cases
Banking & Finance: 5 cases
Consumer Protection: 5 cases

Total: ~100 landmark cases
```

---

## After Import

### Test it:
```bash
python scripts/test_case_law.py
```

### Use it:
```bash
curl -X POST http://localhost:8000/api/query/ask \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are remedies for breach of contract?"}'
```

### Check stats:
```bash
curl http://localhost:8000/api/query/case-law-stats \
  -H "Authorization: Bearer TOKEN"
```

---

## Want More?

### Import 500+ cases:
```bash
python scripts/bulk_import_cases.py --mode full
```

### Import specific category:
```bash
python scripts/bulk_import_cases.py --mode category --category "Contract Law"
```

---

## Need Help?

- **Full Guide**: `backend/BULK_IMPORT_GUIDE.md`
- **System Docs**: `backend/CASE_LAW_SYSTEM.md`
- **API Usage**: `CASE_LAW_USAGE_GUIDE.md`
- **Roadmap**: `ROADMAP_ADVANCED_FEATURES.md`

---

## Troubleshooting

**Import slow?**
```bash
# Reduce cases per query
python scripts/bulk_import_cases.py --mode full --cases-per-query 3
```

**LLM errors?**
- Check your LLM service is running
- Verify API keys in `.env`

**Connection errors?**
- Indian Kanoon might be down
- Wait and retry

---

## That's It!

You now have a complete, automated legal case law knowledge base system.

**Start now**: `python backend/scripts/quick_import_100_cases.py`
