# ==========================================
# 📘 Embeddings 통합 모듈
# ------------------------------------------
# - OpenAI Embeddings 팩토리 함수
# - configs/model_config.yaml 설정 사용
# ==========================================

# ------------------------- 표준 라이브러리 ------------------------- #
import os
from typing import Optional

# ------------------------- 서드파티 라이브러리 ------------------------- #
from langchain_openai import OpenAIEmbeddings


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
