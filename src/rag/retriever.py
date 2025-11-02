# ==========================================
# 📘 Phase 1: RAG 시스템 기초 구현
# 📍 Step 1~2: PGVector 기반 Retriever 및 기본 검색 로직
# ------------------------------------------
# - OpenAI Embeddings 초기화 (embeddings.py)
# - VectorStore (PGVector) 연동 (vector_store.py)
# - similarity / MMR 검색 지원
# - MultiQueryRetriever(쿼리 확장) 통합 (Phase 2)
# - 메타데이터 필터 검색 제공 (년도/카테고리 등)
# ==========================================

import os
import hashlib
from typing import List, Dict, Any, Optional, Tuple

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
# ---------- MultiQueryRetriever 임포트(버전 호환) ----------
# - 프로젝트 환경에서 확인된 안정 경로: langchain_classic.retrievers
# - 환경에 따라 다를 수 있으므로 필요 시 대체 경로 사용 가능
from langchain_classic.retrievers import MultiQueryRetriever # 권장
# 대체: 신/구버전 경로 탐색 (필요 시 확장)
# from langchain.retrievers.multi_query import MultiQueryRetriever # type: ignore

from .vector_store import get_pgvector_store


# ---------- 상수/환경 ----------
COLLECTION_CHUNKS = os.getenv("PGV_COLLECTION_CHUNKS", "paper_chunks")
DEFAULT_LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5")

# ---------- 유틸: 문서 중복 제거 ----------
def _dedup_docs(docs: List[Document]) -> List[Document]:
    """
    문서 리스트에서 page_content+metadata 기준으로 중복 제거.
    - 동일 문장이 다양한 쿼리에서 재탐색되는 경우 중복을 줄여 최종 k개 품질 확보.
    """
    seen = set()
    uniq: List[Document] = []
    for d in docs:
        key = hashlib.md5((d.page_content + str(d.metadata)).encode("utf-8")).hexdigest()
        if key not in seen:
            seen.add(key)
            uniq.append(d)
    return uniq

class RAGRetriever:
    """
    RAG 검색용 Retriever 집합 클래스
    - PGVector VectorStore를 기반으로 similarity/MMR 검색 제공
    - MultiQueryRetriever로 쿼리 확장(Phase 2)
    - 메타데이터 필터 검색 지원


    Parameters
    ----------
    collection_name : str
        pgvector 컬렉션명 (기본: paper_chunks)
    search_type : str
        "similarity" 또는 "mmr"
    k : int
        최종 반환 문서 수
    fetch_k : int
        MMR 후보 수 (search_type="mmr"일 때 사용)
    lambda_mult : float
        MMR 관련성/다양성 균형 (0~1)
    llm_model : Optional[str]
        MultiQuery에 사용할 LLM 이름 (기본 환경변수 LLM_MODEL)
    llm_temperature : float
        LLM temperature
    """

    # ---------- 초기화 ----------
    def __init__(
        self,
        collection_name: str = COLLECTION_CHUNKS,
        search_type: str = "mmr",
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        llm_model: Optional[str] = None,
        llm_temperature: float = 0.0,
    ):
        # VectorStore 준비
        self.vectorstore = get_pgvector_store(collection_name)


        # 검색 파라미터 보관
        self.search_type = search_type
        self.k = k
        self.fetch_k = fetch_k
        self.lambda_mult = lambda_mult


        # Base retriever 구성
        self._retriever = self._build_retriever()


        # LLM/MQR 설정 (없으면 자동 폴백)
        self.llm_model = llm_model or DEFAULT_LLM_MODEL
        self.llm_temperature = llm_temperature
        self._multi_query_retriever: Optional[MultiQueryRetriever] = None # type: ignore
        self._maybe_build_multiquery()


        # ---------- 내부: retriever 구성 ----------
    def _build_retriever(self):
        if self.search_type == "mmr":
            return self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": self.k,
                    "fetch_k": self.fetch_k,
                    "lambda_mult": self.lambda_mult,
                },
            )
        # 기본: similarity
        return self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.k},
        )

    # ---------- 내부: MultiQueryRetriever 구성 (있으면 사용) ----------
    def _maybe_build_multiquery(self):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or MultiQueryRetriever is None:
        self._multi_query_retriever = None
        return
    try:
        llm = ChatOpenAI(model=self.llm_model, temperature=self.llm_temperature)
        base = self.vectorstore.as_retriever(
            search_type=self.search_type,
            search_kwargs={
                "k": self.k,
                **(
                    {"fetch_k": self.fetch_k, "lambda_mult": self.lambda_mult}
                    if self.search_type == "mmr"
                    else {}
                ),
            },
        )
        self._multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=base,
            llm=llm,
        )
    except Exception:
        # LLM/네트워크 문제 등 발생 시 폴백
        self._multi_query_retriever = None

    # ---------- 공개 API: 기본 검색 ----------
    def invoke(self, query: str) -> List[Document]:
        """기본 검색 실행 (현재 설정된 search_type 사용)."""
        return self._retriever.invoke(query)

    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """VectorStore 유사도 검색 (상위 k)."""
        k = k or self.k
        return self.vectorstore.similarity_search(query, k=k)

    def similarity_search_with_score(self, query: str, k: Optional[int] = None) -> List[Tuple[Document, float]]:
        """유사도 검색 + 점수 반환."""
        k = k or self.k
        return self.vectorstore.similarity_search_with_score(query, k=k)

    # ---------- 공개 API: 모드 전환 ----------
    def set_mode(self, search_type: str = "similarity"):
        """런타임 검색 모드 전환 (similarity/MMR)."""
        self.search_type = search_type
        self._retriever = self._build_retriever()
        self._maybe_build_multiquery()

    # ---------- 공개 API: 필터 검색 ----------
    def search_with_filter(self, query: str, filter_dict: Dict[str, Any], k: Optional[int] = None):
        """메타데이터 필터와 함께 검색 (예: 연도/저자/카테고리)."""
        k = k or self.k
        filtered = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k, "filter": filter_dict},
        )
        return filtered.invoke(query)

    # ---------- 공개 API: 멀티쿼리 검색 ----------
    def multi_query_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        LLM으로 쿼리를 확장하여 병렬 검색 후 중복 제거.
        - API Key/LLM 문제로 MultiQuery가 비활성화된 경우 base retriever로 폴백.
        """
        k = k or self.k
        if not self._multi_query_retriever:
            return self._retriever.invoke(query)


        docs = self._multi_query_retriever.invoke(query)
        docs = _dedup_docs(docs)
        return docs[:k]