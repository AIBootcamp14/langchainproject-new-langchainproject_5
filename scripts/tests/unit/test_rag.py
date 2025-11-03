# ==========================================
# 🧪 테스트 스위트 (Phase 1~3 핵심 검증)
# ------------------------------------------
# - Retriever: similarity/MMR/with_scores/필터
# - MultiQuery: 쿼리 확장 검색 (환경에 따라 폴백 허용)
# - Tools: search_paper_database / search_glossary 스모크
# ==========================================

import os
import pytest

from langchain_core.documents import Document

from src.rag.retriever import RAGRetriever
from src.tools.search_paper import search_paper_database
from src.tools.glossary import search_glossary

# ---------- 환경 스위치 ----------
QUERY = os.getenv("TEST_QUERY", "Transformer architecture")
REQUIRE_RESULTS = os.getenv("REQUIRE_RESULTS", "0") == "1"
REQUIRE_RESULTS_MQ = os.getenv("REQUIRE_RESULTS_MQ", "0") == "1"
REQUIRE_TOOL = os.getenv("REQUIRE_TOOL", "0") == "1"
REQUIRE_GLOSSARY = os.getenv("REQUIRE_GLOSSARY", "0") == "1"


# ---------- Phase 1: 기본 Retriever ----------

def test_tool_search_glossary_sql_only():
    md = search_glossary.invoke({
        "query": "Transformer",
        "category": None,
        "difficulty": "auto",
        "mode": "sql",
        "top_k": 3,
        "with_scores": False,
    })
    assert isinstance(md, str)
    if REQUIRE_GLOSSARY:
        assert "용어집 검색 결과" in md

def test_tool_search_glossary_vector_or_hybrid():
    md = search_glossary.invoke({
        "query": "Attention",
        "category": None,
        "difficulty": "easy",
        "mode": "hybrid",  # vector 인덱스 없으면 SQL로 폴백
        "top_k": 3,
        "with_scores": True,
    })
    assert isinstance(md, str)

def test_tool_search_paper_database_smoke():
    md = search_paper_database.invoke({
        "query": os.getenv("TEST_QUERY", "Attention"),
        "year_gte": None,
        "author": None,
        "category": None,
        "top_k": 3,
        "with_scores": True,
        "use_multi_query": True,
        "search_mode": "similarity",
    })
    assert isinstance(md, str)
    if REQUIRE_TOOL:
        assert "검색된 논문" in md

def test_tool_search_with_filters():
    md = search_paper_database.invoke({
        "query": os.getenv("TEST_QUERY", "Attention"),
        "year_gte": 2017,
        "author": None,
        "category": None,
        "top_k": 2,
        "with_scores": False,
        "use_multi_query": False,
        "search_mode": "similarity",
    })
    assert isinstance(md, str)

def test_multiquery_retriever():
    r = RAGRetriever(search_type="similarity", k=5)
    docs = r.multi_query_search(os.getenv("TEST_QUERY", "Attention"))
    assert isinstance(docs, list)
    if docs:
        assert isinstance(docs[0], Document)
    if REQUIRE_RESULTS_MQ:
        assert len(docs) > 0, "No results returned in MultiQuery mode."

def test_similarity_with_score_threshold():
    r = RAGRetriever(search_type="similarity", k=3)
    pairs = r.similarity_search_with_score(os.getenv("TEST_QUERY", "Attention"), k=3)
    assert isinstance(pairs, list)
    if pairs:
        doc, score = pairs[0]
        assert isinstance(score, float)
        # 점수 분포가 설치/데이터에 따라 달라질 수 있으니 강한 단정 대신 약한 가드만
        assert score >= 0.0


def test_similarity_search_smoke_print():
    r = RAGRetriever(search_type="similarity", k=3)
    docs = r.similarity_search(os.getenv("TEST_QUERY", "Attention"), k=3)
    # 스모크 체크
    assert isinstance(docs, list)
    if docs:
        top = docs[0]
        # 핵심 메타 확인(있으면 좋음)
        _ = top.metadata.get("paper_id")
        _ = top.metadata.get("title")
        # 디버깅용 출력 (pytest -q면 보통 숨겨지지만 실패 시 출력됨)
        print("\nTOP DOC TITLE:", top.metadata.get("title"))
        print("TOP DOC PREVIEW:", top.page_content[:120])


@pytest.mark.order(1)
def test_retriever_similarity_mode():
    r = RAGRetriever(search_type="similarity", k=5)
    docs = r.invoke(QUERY)
    assert isinstance(docs, list)
    if docs:
        assert isinstance(docs[0], Document)
    if REQUIRE_RESULTS:
        assert len(docs) > 0, "No results returned in similarity mode."

@pytest.mark.order(2)
def test_similarity_search_with_score_api():
    r = RAGRetriever(search_type="similarity", k=5)
    docs_scores = r.similarity_search_with_score(QUERY, k=3)
    assert isinstance(docs_scores, list)
    if docs_scores:
        doc, score = docs_scores[0]
        assert isinstance(doc, Document)
        assert isinstance(score, float)
    if REQUIRE_RESULTS:
        assert len(docs_scores) > 0, "No results returned with scores."

@pytest.mark.order(3)
def test_retriever_mmr_mode():
    r = RAGRetriever(search_type="mmr", k=5, fetch_k=20, lambda_mult=0.5)
    docs = r.invoke(QUERY)
    assert isinstance(docs, list)
    if docs:
        assert isinstance(docs[0], Document)
    if REQUIRE_RESULTS:
        assert len(docs) > 0, "No results returned in MMR mode."

@pytest.mark.order(4)
def test_metadata_filter_path():
    r = RAGRetriever(search_type="similarity", k=5)
    # 예: 년도 메타데이터가 인덱싱되어 있다고 가정
    docs = r.search_with_filter(QUERY, {"year": {"$gte": 2018}}, k=3)
    assert isinstance(docs, list)
    if docs:
        assert isinstance(docs[0], Document)

