# ==========================================
# 📘 Phase 1: Embeddings 초기화
# 📍 Step 1: OpenAI Embeddings 팩토리
# ------------------------------------------
# - 기본 모델: text-embedding-3-small
# - 환경변수로 모델 전환 허용 (EMBEDDING_MODEL)
# ==========================================

import os
from typing import Optional

from langchain_openai import OpenAIEmbeddings


DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

def get_embeddings(model: Optional[str] = None) -> OpenAIEmbeddings:
    """
    OpenAIEmbeddings 인스턴스 생성.
    Parameters
    ----------
    model_name : Optional[str]
    사용할 임베딩 모델명. 미지정 시 환경변수(EMBEDDING_MODEL) 또는 기본값 사용.
    """
    model_name = model or DEFAULT_EMBEDDING_MODEL
    # OpenAIEmbeddings는 내부적으로 OPENAI_API_KEY 읽음
    return OpenAIEmbeddings(model=model_name)

