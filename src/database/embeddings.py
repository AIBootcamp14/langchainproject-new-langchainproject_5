# ==========================================
# 📘 Embeddings 통합 모듈
# ------------------------------------------
# - OpenAI Embeddings 팩토리 함수
# - PaperEmbeddingManager 클래스 (Vector DB 저장)
# - configs/model_config.yaml 설정 사용
# ==========================================

# ------------------------- 표준 라이브러리 ------------------------- #
import logging
import os
import time
from typing import Dict, List, Optional

# ------------------------- 서드파티 라이브러리 ------------------------- #
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.utils.config_loader import get_postgres_connection_string, get_model_config

logger = logging.getLogger(__name__)


# ==================== 기본값 설정 ==================== #

DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


# ==================== OpenAI Embeddings 팩토리 ==================== #

def get_embeddings(model: Optional[str] = None) -> OpenAIEmbeddings:
    """
    OpenAIEmbeddings 인스턴스 생성

    Args:
        model: 사용할 임베딩 모델명 (미지정 시 환경변수(EMBEDDING_MODEL) 또는 기본값 사용)

    Returns:
        OpenAIEmbeddings 인스턴스

    사용 모델:
    - text-embedding-3-small: 1536차원, 비용 효율적
    - text-embedding-3-large: 3072차원, 높은 정확도

    참고:
    - OpenAIEmbeddings는 내부적으로 OPENAI_API_KEY 환경변수를 읽음
    - configs/model_config.yaml의 embeddings.model 설정 우선 사용 권장
    """
    # 모델명 결정 (파라미터 > 환경변수 > 기본값)
    model_name = model or DEFAULT_EMBEDDING_MODEL

    # OpenAI Embeddings 인스턴스 생성
    return OpenAIEmbeddings(model=model_name)


# ==================== PaperEmbeddingManager 클래스 ==================== #

class PaperEmbeddingManager:
    """
    논문 임베딩 및 Vector DB 저장 클래스

    LangChain PGVector를 사용하여 PostgreSQL(pgvector)에 문서를 적재합니다.
    """

    def __init__(self, collection_name: str = "paper_chunks") -> None:
        """
        PaperEmbeddingManager 초기화

        Args:
            collection_name: pgvector 컬렉션명 (기본값: paper_chunks)
        """
        # -------------- config_loader로 모델 설정 로드 -------------- #
        model_config = get_model_config()
        embedding_config = model_config['embeddings']

        # -------------- OpenAI Embeddings 초기화 -------------- #
        self.embeddings = OpenAIEmbeddings(
            model=embedding_config['model'],
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        # -------------- config_loader로 PostgreSQL 연결 문자열 가져오기 -------------- #
        conn = get_postgres_connection_string()

        # -------------- PGVector VectorStore 초기화 -------------- #
        self.vectorstore = PGVector(
            collection_name=collection_name,
            connection=conn,
            embeddings=self.embeddings,
        )

    def add_documents(self, documents: List[Document], batch_size: int = 50) -> int:
        """
        문서 리스트를 배치로 나누어 Vector DB에 저장

        Args:
            documents: 저장할 Document 리스트
            batch_size: 배치 크기 (기본값: 50)

        Returns:
            저장된 문서 수
        """
        total = 0
        num_batches = (len(documents) + batch_size - 1) // batch_size

        logger.info(f"Starting to add {len(documents)} documents in {num_batches} batches")

        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            batch_num = i // batch_size + 1

            try:
                self.vectorstore.add_documents(batch)
                total += len(batch)
                logger.info(f"Batch {batch_num}/{num_batches}: Added {len(batch)} documents (total: {total})")

                # Rate Limit 대응: 배치 간 대기
                if i + batch_size < len(documents):
                    time.sleep(0.1)  # 100ms 대기

            except Exception as e:
                logger.error(f"Batch {batch_num}/{num_batches} failed: {e}")
                # Rate Limit 오류 시 더 긴 대기
                if "rate limit" in str(e).lower() or "429" in str(e):
                    logger.warning("Rate limit detected, waiting 5 seconds...")
                    time.sleep(5)
                continue

        logger.info(f"Completed: {total}/{len(documents)} documents added")
        return total

    def add_documents_with_paper_id(
        self,
        documents: List[Document],
        paper_id_mapping: Dict[str, int],
        batch_size: int = 50
    ) -> int:
        """
        문서 리스트를 paper_id 메타데이터와 함께 배치로 저장

        Args:
            documents: 저장할 Document 리스트 (metadata에 'arxiv_id' 또는 'entry_id' 포함)
            paper_id_mapping: arxiv_id → paper_id 매핑 딕셔너리
            batch_size: 배치 크기 (기본값: 50)

        Returns:
            저장된 문서 수
        """
        # 메타데이터에 paper_id 추가
        enriched_docs = []
        for doc in documents:
            # arxiv_id 추출
            arxiv_id = doc.metadata.get("arxiv_id")
            if not arxiv_id:
                # entry_id에서 추출
                entry_id = doc.metadata.get("entry_id", "")
                arxiv_id = entry_id.split("/")[-1] if entry_id else None

            # paper_id 매핑
            if arxiv_id and arxiv_id in paper_id_mapping:
                doc.metadata["paper_id"] = paper_id_mapping[arxiv_id]
                enriched_docs.append(doc)
            else:
                logger.warning(f"Paper ID not found for arxiv_id: {arxiv_id}, skipping document")

        logger.info(f"Enriched {len(enriched_docs)}/{len(documents)} documents with paper_id")

        # 배치 저장 실행
        return self.add_documents(enriched_docs, batch_size=batch_size)
