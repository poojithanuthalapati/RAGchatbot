import os
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
from contextlib import contextmanager

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://rag_user:rag_password@localhost:5432/rag_db",
)


@contextmanager
def get_conn():
    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)  # lets embedding columns come back as numpy arrays
    try:
        yield conn
    finally:
        conn.close()


def insert_document_chunks(source: str, chunks: list[str], embeddings: list[list[float]]):
    """Store a batch of (chunk, embedding) pairs for a given source document."""
    rows = [
        (source, idx, chunk, embedding)
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    with get_conn() as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO documents (source, chunk_index, content, embedding)
                VALUES %s
                """,
                rows,
                template="(%s, %s, %s, %s)",
            )
        conn.commit()


def search_similar_chunks(query_embedding: list[float], top_k: int = 4):
    """Return the top_k most similar document chunks to the query embedding."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, source, content, 1 - (embedding <=> %s::vector) AS similarity
                FROM documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_embedding, query_embedding, top_k),
            )
            rows = cur.fetchall()
    return [
        {"id": r[0], "source": r[1], "content": r[2], "similarity": float(r[3])}
        for r in rows
    ]


def save_chat_turn(session_id: str, role: str, content: str, retrieved_doc_ids: list[int] | None = None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat_history (session_id, role, content, retrieved_doc_ids)
                VALUES (%s, %s, %s, %s)
                """,
                (session_id, role, content, retrieved_doc_ids),
            )
        conn.commit()


# ============================================================
# Resume-vs-job-description analyzer
# ============================================================

def insert_resume(session_id: str, filename: str, raw_text: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO resumes (session_id, filename, raw_text)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (session_id, filename, raw_text),
            )
            resume_id = cur.fetchone()[0]
        conn.commit()
    return resume_id


def insert_resume_chunks(resume_id: int, chunks: list[str], embeddings: list[list[float]]):
    rows = [(resume_id, idx, chunk, emb) for idx, (chunk, emb) in enumerate(zip(chunks, embeddings))]
    with get_conn() as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO resume_chunks (resume_id, chunk_index, content, embedding)
                VALUES %s
                """,
                rows,
                template="(%s, %s, %s, %s)",
            )
        conn.commit()


def insert_job_posting(session_id: str, title: str | None, raw_text: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO job_postings (session_id, title, raw_text)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (session_id, title, raw_text),
            )
            job_posting_id = cur.fetchone()[0]
        conn.commit()
    return job_posting_id


def insert_job_posting_chunks(job_posting_id: int, chunks: list[str], embeddings: list[list[float]]):
    rows = [(job_posting_id, idx, chunk, emb) for idx, (chunk, emb) in enumerate(zip(chunks, embeddings))]
    with get_conn() as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO job_posting_chunks (job_posting_id, chunk_index, content, embedding)
                VALUES %s
                """,
                rows,
                template="(%s, %s, %s, %s)",
            )
        conn.commit()


def get_resume_chunks(resume_id: int) -> list[dict]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, chunk_index, content, embedding
                FROM resume_chunks
                WHERE resume_id = %s
                ORDER BY chunk_index
                """,
                (resume_id,),
            )
            rows = cur.fetchall()
    return [{"id": r[0], "chunk_index": r[1], "content": r[2], "embedding": r[3]} for r in rows]


def get_job_posting_chunks(job_posting_id: int) -> list[dict]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, chunk_index, content, embedding
                FROM job_posting_chunks
                WHERE job_posting_id = %s
                ORDER BY chunk_index
                """,
                (job_posting_id,),
            )
            rows = cur.fetchall()
    return [{"id": r[0], "chunk_index": r[1], "content": r[2], "embedding": r[3]} for r in rows]


def insert_analysis(
    resume_id: int,
    job_posting_id: int,
    overall_score: float,
    weak_resume_chunks: list[dict],
    uncovered_jd_chunks: list[dict],
    suggestions: list[dict],
) -> int:
    import json

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO analyses
                    (resume_id, job_posting_id, overall_score, weak_resume_chunks, uncovered_jd_chunks, suggestions)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    resume_id,
                    job_posting_id,
                    overall_score,
                    json.dumps(weak_resume_chunks),
                    json.dumps(uncovered_jd_chunks),
                    json.dumps(suggestions),
                ),
            )
            analysis_id = cur.fetchone()[0]
        conn.commit()
    return analysis_id
