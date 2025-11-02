# ==========================================
# 📘 Phase 3: 인덱싱/시드 스크립트 (용어집)
# 📍 Step 6: glossary → glossary_embeddings 시딩
# ------------------------------------------
# - glossary 테이블에서 term/definition/easy/hard/examples 추출
# - Document化 후 PGVector에 upsert
# ==========================================

import os

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

def _env(primary: str, alt: str, default=None):
    return os.getenv(primary) or os.getenv(alt) or default

def _pg_conn_str() -> str:
    user = _env("POSTGRES_USER", "PGUSER", "postgres")
    password = _env("POSTGRES_PASSWORD", "PGPASSWORD", "postgres")
    host = _env("POSTGRES_HOST", "PGHOST", "localhost")
    port = _env("POSTGRES_PORT", "PGPORT", "5432")
    db = _env("POSTGRES_DB", "PGDATABASE", "papers")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

def main():
    """glossary 테이블을 glossary_embeddings 컬렉션으로 시드."""
    load_dotenv()
    
    conn = psycopg2.connect(_pg_conn_str())
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT term_id, term, definition, easy_explanation, hard_explanation,
                       category, difficulty_level, related_terms, examples
                FROM glossary
                ORDER BY term_id ASC
                LIMIT 200
            """)
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        print("[seed_glossary] glossary 테이블이 비어 있습니다.")
        return

    docs = []
    for r in rows:
        content = (
            f"Term: {r['term']}\n"
            f"Definition: {r.get('definition','')}\n\n"
            f"Easy: {r.get('easy_explanation','')}\n"
            f"Hard: {r.get('hard_explanation','')}\n"
            f"Examples: {r.get('examples','')}\n"
        )
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "term_id": r["term_id"],
                    "term": r["term"],
                    "definition": r.get("definition"),
                    "easy_explanation": r.get("easy_explanation"),
                    "hard_explanation": r.get("hard_explanation"),
                    "category": r.get("category"),
                    "difficulty_level": r.get("difficulty_level"),
                    "related_terms": r.get("related_terms"),
                    "examples": r.get("examples"),
                },
            )
        )

    embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    vs = PGVector(
        collection_name=os.getenv("PGV_COLLECTION_GLOSSARY", "glossary_embeddings"),
        embeddings=embeddings,
        connection=_pg_conn_str(),
        use_jsonb=True,
    )
    ids = vs.add_documents(docs)
    print(f"[seed_glossary] upserted {len(ids)} docs to '{os.getenv('PGV_COLLECTION_GLOSSARY','glossary_embeddings')}'")

if __name__ == "__main__":
    main()


