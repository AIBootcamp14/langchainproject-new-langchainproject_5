# ==========================================
# 📘 VectorStore 통합 모듈
# ------------------------------------------
# - PGVector VectorStore 생성 및 관리
# - get_pgvector_store() 팩토리 함수
# - configs/db_config.yaml 설정 사용
# ==========================================

# ------------------------- 표준 라이브러리 ------------------------- #
import os
from typing import Optional

# ------------------------- 서드파티 라이브러리 ------------------------- #
from langchain_postgres.vectorstores import PGVector

# ------------------------- 프로젝트 모듈 ------------------------- #
from .embeddings import get_embeddings
from src.utils.config_loader import get_postgres_connection_string


# ==================== 환경 유틸리티 ==================== #

def _env(primary: str, alt: str, default: Optional[str] = None) -> Optional[str]:
    """
    환경변수 읽기 헬퍼 함수

    Args:
        primary: 우선순위 환경변수명
        alt: 대체 환경변수명
        default: 기본값

    Returns:
        환경변수 값
    """
    return os.getenv(primary) or os.getenv(alt) or default


def _pg_conn_str() -> str:
    """
    PostgreSQL 연결 문자열 생성

    configs/db_config.yaml 설정을 우선 사용하고,
    없으면 환경변수로 폴백

    Returns:
        PostgreSQL 연결 문자열
    """
    try:
        # configs/db_config.yaml 사용 (권장)
        return get_postgres_connection_string()
    except Exception:
        # 환경변수 폴백
        user = _env("POSTGRES_USER", "PGUSER", "postgres")
        password = _env("POSTGRES_PASSWORD", "PGPASSWORD", "postgres")
        host = _env("POSTGRES_HOST", "PGHOST", "localhost")
        port = _env("POSTGRES_PORT", "PGPORT", "5432")
        db = _env("POSTGRES_DB", "PGDATABASE", "papers")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# ==================== VectorStore 생성기 ==================== #

def get_pgvector_store(
    collection_name: str,
    embedding_model: Optional[str] = None,
    connection_string: Optional[str] = None,
) -> PGVector:
    """
    PGVector VectorStore 인스턴스를 생성하여 반환

    Args:
        collection_name: pgvector 컬렉션명 (예: 'paper_chunks')
        embedding_model: 임베딩 모델명 (기본: text-embedding-3-small)
        connection_string: 명시 연결 문자열 (미지정 시 configs/db_config.yaml 기반)

    Returns:
        PGVector 인스턴스
    """
    # PostgreSQL 연결 문자열 가져오기
    conn = connection_string or _pg_conn_str()

    # OpenAI Embeddings 초기화
    embeddings = get_embeddings(embedding_model)

    # PGVector VectorStore 생성
    return PGVector(
        collection_name=collection_name,
        embeddings=embeddings,
        connection=conn,
        use_jsonb=True,
    )
