# ==========================================
# 📘 Phase 1: VectorStore 연결부
# 📍 Step 1: PGVector 인스턴스 생성 유틸
# ------------------------------------------
# - 환경변수(POSTGRES_* / PG*) 동시 지원
# - OpenAI Embeddings 주입 (embeddings.py)
# - 최신 시그니처(connection, embeddings, use_jsonb)
# ==========================================

import os
from typing import Optional

from langchain_postgres.vectorstores import PGVector

from .embeddings import get_embeddings

# ---------- 환경 유틸 ----------

def _env(primary: str, alt: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(primary) or os.getenv(alt) or default

def _pg_conn_str() -> str:
    """PostgreSQL 연결 문자열 생성."""
    user = _env("POSTGRES_USER", "PGUSER", "postgres")
    password = _env("POSTGRES_PASSWORD", "PGPASSWORD", "postgres")
    host = _env("POSTGRES_HOST", "PGHOST", "localhost")
    port = _env("POSTGRES_PORT", "PGPORT", "5432")
    db = _env("POSTGRES_DB", "PGDATABASE", "papers")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

# ---------- VectorStore 생성기 ----------

def get_pgvector_store(
    collection_name: str,
    embedding_model: Optional[str] = None,
    connection_string: Optional[str] = None,
) -> PGVector:
    """
    PGVector VectorStore 인스턴스를 생성하여 반환.
    - collection_name: pgvector 컬렉션명 (예: 'paper_chunks')
    - embedding_model: 임베딩 모델명 (기본: text-embedding-3-small)
    - connection_string: 명시 연결 문자열(미지정 시 환경변수 기반)
    """
    conn = connection_string or _pg_conn_str()
    embeddings = get_embeddings(embedding_model)
    return PGVector(
        collection_name=collection_name,
        embeddings=embeddings,
        connection=conn,
        use_jsonb=True,
    )

