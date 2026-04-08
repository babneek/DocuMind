# DocuMind AI 🧠

**Enterprise Document Intelligence & Agent Platform**

DocuMind AI is a scalable, enterprise-grade platform for document intelligence. It allows you to ingest, process, and query massive amounts of documents using State-of-the-Art LLMs and RAG (Retrieval-Augmented Generation).

---

## 🚀 Features

- **Multi-Document Upload:** PDF, DOCX, EPUB, and TXT support.
- **FastAPI Backend:** Robust, async API for enterprise integrations.
- **RAG Architecture:** Vector search with ChromaDB and Sentence Transformers.
- **AI Agents:** Search, Summary, and Extraction agents out-of-the-box.
- **Premium React Frontend:** Modern, high-performance UI with glassmorphism and real-time dashboard.
- **Structured Data Extraction:** Extract JSON fields from complex contracts.

---

## 🏗️ Architecture

- **Frontend:** React + Vite + Framer Motion
- **Backend:** FastAPI
- **Database:** PostgreSQL (Metadata), ChromaDB (Vectors)
- **Worker:** Celery + Redis (for background processing)
- **AI:** OpenAI / OpenRouter (LLM), Sentence Transformers (Embeddings)

---

## 🛠️ Getting Started

### 1. Setup Environment
Ensure you have Python 3.10+ and Node.js installed.
```bash
# Create venv
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install deps
pip install -r requirements.txt
```

### 2. Configure `.env`
Create a `.env` file in the root:
```env
OPENAI_API_KEY=your_openai_or_openrouter_key
GROQ_API_KEY=your_groq_api_key  # Optional: for high-speed inference
DATABASE_URL=sqlite:///./documind.db  # Use Postgres for production
```

### 3. Run the Platform

**Start the Backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Start the Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📂 Project Structure

```text
/backend          # FastAPI App
/frontend         # React App (Vite)
/services         # Core RAG & LLM logic
/database         # DB adapters
/models           # SQLAlchemy models
/workers          # Background tasks
```

---

## 🛡️ License
MIT License. Created by babneek.