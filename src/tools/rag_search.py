# ==========================================
# 📘 Phase 2: 고급 검색 기능 + 도구 레이어
# 📍 Step 4: RAG 검색 도구(@tool) 구현
# ------------------------------------------
# - @tool: search_paper_database
# - 검색 모드 선택 (similarity/MMR), MultiQuery 옵션
# - 메타데이터 필터(year/author/category)
# - PostgreSQL 메타 조회 → 결과 합성 → Markdown 반환
# ==========================================

import os
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor
from langchain_core.tools import tool
from langchain_core.documents import Document

from src.rag.retriever import RAGRetriever


# ---------- 내부 유틸: 환경/DB ----------

def _env(primary: str, alt: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(primary) or os.getenv(alt) or default

def _pg_conn_str() -> str:
    user = _env("POSTGRES_USER", "PGUSER", "postgres")
    password = _env("POSTGRES_PASSWORD", "PGPASSWORD", "postgres")
    host = _env("POSTGRES_HOST", "PGHOST", "localhost")
    port = _env("POSTGRES_PORT", "PGPORT", "5432")
    db = _env("POSTGRES_DB", "PGDATABASE", "papers")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

def _fetch_paper_meta(paper_ids: List[int]) -> Dict[int, Dict[str, Any]]:
    """
    papers 테이블에서 ID 목록에 해당하는 메타데이터를 일괄 조회.
    - title/authors/publish_date/url/category/citation_count
    - 결과: {paper_id: {...}}
    """
    if not paper_ids:
        return {}
    conn = psycopg2.connect(_pg_conn_str())
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT paper_id, title, authors, publish_date, url, category, citation_count
                FROM papers
                WHERE paper_id = ANY(%s)
                """,
                (paper_ids,),
            )
            rows = cur.fetchall()
            out: Dict[int, Dict[str, Any]] = {}
            for row in rows:
                out[row["paper_id"]] = dict(row)
            return out
    finally:
        conn.close()

def _format_markdown(results: List[Dict[str, Any]]) -> str:
    """검색 결과를 Markdown 문자열로 변환."""
    if not results:
        return "관련 논문을 찾을 수 없습니다."

    lines: List[str] = ["## 검색된 논문\n"]
    for i, r in enumerate(results, 1):
        score_str = f"{r['score']:.4f}" if r.get("score") is not None else "N/A"

        lines.append(f"### {i}. {r.get('title','(Untitled)')}")
        lines.append(f"- **저자**: {r.get('authors','')}")
        lines.append(f"- **출판일**: {r.get('publish_date','')}")
        lines.append(f"- **카테고리**: {r.get('category','')}")
        lines.append(f"- **인용수**: {r.get('citation_count','')}")
        lines.append(f"- **URL**: {r.get('url','')}")
        lines.append(f"- **섹션**: {r.get('section','본문')}")
        lines.append(f"- **유사도 점수(낮을수록 유사)**: {score_str}\n")

        preview = (r.get("content") or "")[:600]
        if preview:
            lines.append(preview + ("..." if len(r.get("content","")) > 600 else ""))
        lines.append("\n---\n")

    return "\n".join(lines)

def _build_filter(year_gte: Optional[int], author: Optional[str], category: Optional[str]) -> Dict[str, Any]:
    """VectorStore 메타데이터 필터 구성.
    - 연도 이상, 저자 부분일치, 카테고리 매치 등
    """
    f: Dict[str, Any] = {}
    if year_gte is not None:
        # 메타데이터에 'year' 키가 있다고 가정 (인덱싱 시 넣어두면 좋음)
        f["year"] = {"$gte": int(year_gte)}
    if author:
        # 간단 매칭: author 문자열이 metadata.authors에 포함된 레코드
        f["authors"] = {"$ilike": f"%{author}%"}  # langchain-postgres가 ILIKE류를 지원
    if category:
        f["category"] = category
    return f

# ---------- @tool: 논문 검색 ----------
@tool
def search_paper_database(
    query: str,
    year_gte: Optional[int] = None,
    author: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 5,
    with_scores: bool = True,
    use_multi_query: bool = True,
    search_mode: str = "mmr",  # "similarity" | "mmr"
) -> str:
    """
    논문 VectorDB + PostgreSQL 메타데이터를 함께 조회하여 결과를 반환.

    Parameters
    ----------
    query : str
        사용자 질의
    year_gte : Optional[int]
        특정 연도 이상 필터 (예: 2020)
    author : Optional[str]
        저자 부분일치 필터
    category : Optional[str]
        카테고리 필터 (예: 'cs.CL')
    top_k : int
        반환할 문서 수
    with_scores : bool
        유사도 점수 포함 여부
    use_multi_query : bool
        MultiQuery(LLM 쿼리 확장) 사용 여부
    search_mode : str
        "similarity" 또는 "mmr"
    """

    # Retriever 준비
    r = RAGRetriever(search_type=search_mode, k=top_k)

    # 2) 검색 실행 (필터/멀티쿼리 처리)
    filter_dict = _build_filter(year_gte, author, category)
    docs: List[Document] = []
    pairs: List[Tuple[Document, float]] = []

    if any(filter_dict.values()):
        # 메타데이터 필터가 있으면 similarity + filter로 수행
        docs = r.search_with_filter(query, filter_dict, k=top_k)
        if with_scores:
            # 점수 필요 시, filter는 retriever 경로로만 가능하므로
            # 점수는 별도 재계산이 필요합니다 → 간단히 None 처리
            pairs = [(d, None) for d in docs]  # type: ignore
    else:
        if use_multi_query:
            docs = r.multi_query_search(query, k=top_k)
            if with_scores:
                # 멀티쿼리는 여러 쿼리로 묶였으니, 점수 재계산 시 단일 쿼리 기준 근사값으로 계산
                pairs = r.similarity_search_with_score(query, k=len(docs) or top_k)
        else:
            if with_scores:
                pairs = r.similarity_search_with_score(query, k=top_k)
                docs = [d for d, _ in pairs]
            else:
                docs = r.similarity_search(query, k=top_k)

    # paper_id 메타로 PostgreSQL 메타데이터 조회
    paper_ids = []
    for d in docs:
        pid = d.metadata.get("paper_id")
        if isinstance(pid, int):
            paper_ids.append(pid)
        else:
            # 혹시 str이면 int 로 변환 시도
            try:
                paper_ids.append(int(pid))
            except Exception:
                pass
    meta_map = _fetch_paper_meta(list(set(paper_ids)))

    # 결과 합성
    score_map: Dict[str, float] = {}
    if with_scores and pairs:
        for d, s in pairs:
            # langchain-postgres에서 score는 float (거리) — 낮을수록 유사
            if s is None:
                continue
            score_map[id(d)] = float(s)

    results: List[Dict[str, Any]] = []
    for d in docs:
        pid = d.metadata.get("paper_id")
        meta = meta_map.get(pid, {}) if pid is not None else {}
        results.append({
            "paper_id": pid,
            "title": meta.get("title") or d.metadata.get("title"),
            "authors": meta.get("authors") or d.metadata.get("authors"),
            "publish_date": meta.get("publish_date") or d.metadata.get("publish_date"),
            "url": meta.get("url") or d.metadata.get("url"),
            "category": meta.get("category") or d.metadata.get("category"),
            "citation_count": meta.get("citation_count"),
            "section": d.metadata.get("section", "본문"),
            "content": d.page_content,
            "score": score_map.get(id(d)) if with_scores else None,
        })

    # Markdown 포맷으로 반환
    return _format_markdown(results)









