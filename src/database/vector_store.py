# ==========================================
# 📘 VectorStore 통합 모듈
# ------------------------------------------
# - PGVector VectorStore 생성 및 관리
# - PaperVectorStore 클래스 (검색 메서드 포함)
# - get_pgvector_store() 팩토리 함수
# - configs/db_config.yaml 설정 사용
# ==========================================

# ------------------------- 표준 라이브러리 ------------------------- #
import os
from typing import Optional

# ------------------------- 서드파티 라이브러리 ------------------------- #
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

# ------------------------- 프로젝트 모듈 ------------------------- #
from .embeddings import get_embeddings
from src.utils.config_loader import get_postgres_connection_string, get_model_config


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


# ==================== PaperVectorStore 클래스 ==================== #

class PaperVectorStore:
    """
    논문 벡터 검색을 위한 PGVector 클래스

    configs/db_config.yaml 및 configs/model_config.yaml 설정을 사용합니다.
    """

    def __init__(self, collection_name="paper_chunks"):
        """
        PGVector VectorStore 초기화

        Args:
            collection_name: 컬렉션 이름 (paper_chunks, paper_abstracts, glossary_embeddings)
        """
        # -------------- configs/model_config.yaml에서 모델 설정 로드 -------------- #
        model_config = get_model_config()
        embedding_config = model_config['embeddings']

        # -------------- OpenAI Embeddings 초기화 -------------- #
        self.embeddings = OpenAIEmbeddings(
            model=embedding_config['model'],
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # -------------- configs/db_config.yaml에서 PostgreSQL 연결 문자열 가져오기 -------------- #
        self.connection_string = get_postgres_connection_string()

        # -------------- PGVector VectorStore 초기화 -------------- #
        self.vectorstore = PGVector(
            collection_name=collection_name,                # 컬렉션 이름
            embeddings=self.embeddings,                     # 임베딩 함수
            connection=self.connection_string               # DB 연결 문자열
        )

    # ==================== 문서 추가 ==================== #
    def add_documents(self, documents):
        """
        Document 리스트를 벡터 DB에 추가

        Args:
            documents: Langchain Document 리스트

        Returns:
            추가된 문서 ID 리스트
        """
        ids = self.vectorstore.add_documents(documents)
        print(f"✅ {len(ids)}개 문서 추가 완료")
        return ids

    # ==================== 유사도 검색 (Similarity Search) ==================== #
    def similarity_search(self, query, k=5):
        """
        유사도 검색 (Cosine Similarity)

        Args:
            query: 검색 쿼리
            k: 반환할 문서 개수

        Returns:
            유사한 Document 리스트
        """
        docs = self.vectorstore.similarity_search(query, k=k)
        print(f"✅ {len(docs)}개 유사 문서 검색 완료")
        return docs

    # ==================== MMR 검색 (다양성) ==================== #
    def mmr_search(self, query, k=5, fetch_k=20, lambda_mult=0.5):
        """
        MMR (Maximal Marginal Relevance) 검색

        Args:
            query: 검색 쿼리
            k: 반환할 문서 개수
            fetch_k: 초기 검색 문서 개수
            lambda_mult: 다양성 파라미터 (0~1, 0: 다양성 최대, 1: 유사도 최대)

        Returns:
            다양한 Document 리스트
        """
        docs = self.vectorstore.max_marginal_relevance_search(
            query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult
        )
        print(f"✅ {len(docs)}개 다양한 문서 검색 완료")
        return docs

    # ==================== 유사도 점수 포함 검색 ==================== #
    def similarity_search_with_score(self, query, k=5):
        """
        유사도 점수와 함께 검색

        Args:
            query: 검색 쿼리
            k: 반환할 문서 개수

        Returns:
            (Document, 유사도 점수) 튜플 리스트
        """
        docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)

        # 출력
        for doc, score in docs_with_scores:
            print(f"유사도 점수: {score:.4f}")
            print(f"내용: {doc.page_content[:100]}...")
            print()

        return docs_with_scores
