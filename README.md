# RAG Chatbot (Starter)

A plain retrieval-augmented-generation chatbot: upload a document, ask questions
about it, get answers grounded in the retrieved chunks. Built as the foundation
for a resume-vs-job-description analyzer.

This is a restructured version of the original `RAGchatbot` prototype
(Gradio + ChromaDB + Grok) — same LLM (Grok via xAI) and same local embedding
model (`all-MiniLM-L6-v2`), but rebuilt on FastAPI + Postgres/pgvector so it's
a proper client/server app with a real database behind it.

## ⚠️ Security note
The original repo has a `.env` file committed to a **public** GitHub repo.
If that file contains a real `XAI_API_KEY` (or any other secret), treat it as
compromised:
1. Rotate/regenerate the key at https://console.x.ai
2. Remove `.env` from git tracking: `git rm --cached .env`
3. Add `.env` to `.gitignore` (a `.gitignore` isn't retroactive — the old key
   is still visible in the repo's commit history even after you delete the
   file, which is why rotating the key matters more than deleting the file).

## Stack
- **Backend**: FastAPI (Python)
- **Database**: Postgres + pgvector (via Docker) — replaces ChromaDB
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`, run locally (free, no API cost)
- **LLM**: Grok (`grok-4.3`) via xAI's OpenAI-compatible API
- **Frontend**: Plain HTML/JS (no build step needed) — can later be swapped for the repo's Gradio UI or a React app

## Project structure
```
project/
├── docker-compose.yml       # Postgres + pgvector container
├── backend/
│   ├── main.py                  # FastAPI app: chat + resume analyzer endpoints
│   ├── rag.py                     # chunking, embeddings, Grok calls, similarity matching
│   ├── database.py                # Postgres connection + queries
│   ├── init.sql                   # schema (chat tables + analyzer tables)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── index.html               # simple chat UI
```

## Setup

1. **Start the database**
   ```bash
   docker compose up -d
   ```
   Spins up Postgres with pgvector and runs `init.sql` automatically on first
   boot (creates the `documents` and `chat_history` tables, with a 384-dim
   vector column matching `all-MiniLM-L6-v2`).

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env   # then add your XAI_API_KEY
   ```
   First run will download the embedding model (~90MB) from HuggingFace —
   that's a one-time cost.

3. **Run the API**
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Check it's alive: `curl http://localhost:8000/health`

4. **Open the frontend**
   Open `frontend/index.html` directly in your browser (or serve it with
   `python -m http.server` from the `frontend/` folder). Upload a PDF or .txt
   file, then start asking questions about it.

## How it works

**Plain chat (RAG)**
1. `/ingest` — extracts text from the uploaded file, splits it into
   overlapping chunks, embeds each chunk locally with `all-MiniLM-L6-v2`, and
   stores chunk + embedding in Postgres via pgvector.
2. `/chat` — embeds your question the same way, finds the most similar
   stored chunks using cosine similarity (pgvector's `<=>` operator), and
   passes those chunks as context to Grok to generate a grounded answer.
3. Every turn is logged to `chat_history`, including which document chunks
   were used — useful later for evaluating retrieval quality.

**Resume-vs-job-description analyzer**
1. `POST /resumes` (multipart file upload) — extracts and chunks the resume,
   embeds each chunk, stores it in `resumes` / `resume_chunks`.
2. `POST /job-postings` (JSON body: `{title, text}`) — same treatment for a
   pasted job description, stored in `job_postings` / `job_posting_chunks`.
3. `POST /analyze` (JSON body: `{resume_id, job_posting_id}`) — pulls both
   sets of chunk embeddings back out of Postgres, computes a full
   resume-chunk × JD-chunk cosine similarity matrix in Python (not another
   pgvector query — this is a small, dense comparison, not a large-corpus
   search), then:
   - averages each resume chunk's *best* match into a single 0–100
     **overall score**
   - flags resume bullets whose best match was still weak
     (`weak_resume_chunks`)
   - flags JD requirements no resume bullet covered well
     (`uncovered_jd_chunks`)
   - sends those specific weak/uncovered pairs to Grok, asking for concrete
     rewrite suggestions (grounded in the actual mismatch, not generic advice)
   - stores everything in `analyses`, which is the table the future
     Snowflake pipeline will read from

Try it from the "Resume analyzer" tab in `frontend/index.html`.

## Roadmap: Snowflake analytics pipeline (next)
Postgres stays the live app database — it's the right tool for small,
frequent reads/writes on every analysis. Snowflake gets added *behind* it as
an analytics warehouse, fed by a sync pipeline. This is the OLTP → OLAP
pattern real data engineering teams build:

- **Sync script** (`scripts/sync_to_snowflake.py`, not yet built): queries
  `analyses` (joined with `resumes`/`job_postings`) for rows created since
  the last run — an incremental extract using `created_at` as a watermark —
  and loads them into Snowflake via `snowflake-connector-python`.
- **Snowflake schema**: not a 1:1 copy of Postgres — a small dimensional
  model. A fact table (`fct_analyses`: one row per analysis, with score and
  timestamps) plus dimension tables (`dim_resumes`, `dim_job_postings`).
  Good practice for star-schema design.
- **Scheduling**: a GitHub Actions workflow on a cron trigger, calling the
  sync script — free, and it's the same CI/CD mechanism you'd use to
  auto-deploy the app later.
- **What you'd query once data accumulates**: average score improvement
  per user across repeated analyses, most frequently uncovered JD
  requirements across all users, score distribution by job title.
- **Cloud deploy** (app itself, separate from the analytics side):
  containerize `backend/` with a `Dockerfile`, push to GCP Cloud Run, point
  `DATABASE_URL` at a Neon Postgres instance, deploy `frontend/` to Vercel.

## Notes
- The embedding dimension in `init.sql` (384) matches `all-MiniLM-L6-v2`.
  If you switch embedding models, update the `VECTOR(384)` column to match.
- CORS is wide open (`allow_origins=["*"]`) for local dev — lock this down
  before deploying publicly.
- Grok model name (`grok-4.3`) and endpoint are carried over from the
  original `chatbot.py` — double check the current model name/pricing at
  https://docs.x.ai before deploying, since model availability changes.
