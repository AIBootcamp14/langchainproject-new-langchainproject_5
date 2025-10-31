# ==========================================
# 📘 Phase 3: 용어집 시스템 구현
# 📍 Step 5: 용어집 도구(@tool) + 하이브리드 검색
# ------------------------------------------
# - @tool: search_glossary (hybrid/sql/vector)
# - PostgreSQL(ILIKE/필터) + PGVector(유사도) 병합
# - 난이도 모드(easy/hard/auto)로 설명 선택
# ==========================================

import os
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

# ---------- 환경/커넥션 ----------
def _env(primary: str, alt: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(primary) or os.getenv(alt) or default

def _pg_conn_str() -> str:
    user = _env("POSTGRES_USER", "PGUSER", "postgres")
    password = _env("POSTGRES_PASSWORD", "PGPASSWORD", "postgres")
    host = _env("POSTGRES_HOST", "PGHOST", "localhost")
    port = _env("POSTGRES_PORT", "PGPORT", "5432")
    db = _env("POSTGRES_DB", "PGDATABASE", "papers")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

def _get_glossary_vectorstore() -> PGVector:
    """용어집 전용 VectorStore 초기화."""
    conn_str = _pg_conn_str()
    collection = os.getenv("PGV_COLLECTION_GLOSSARY", "glossary_embeddings")
    embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    return PGVector(
        collection_name=collection,
        embeddings=embeddings,
        connection=conn_str,
        use_jsonb=True,
    )

# ---------- SQL 1차 조회 ----------

def _fetch_glossary_sql(
    query: Optional[str],
    category: Optional[str],
    difficulty: Optional[str],
    limit: int,
) -> List[Dict[str, Any]]:
    conn = psycopg2.connect(_pg_conn_str())
    try:
        where = []
        params: List[Any] = []
        if query:
            where.append("(term ILIKE %s OR definition ILIKE %s OR easy_explanation ILIKE %s OR hard_explanation ILIKE %s)")
            like = f"%{query}%"
            params.extend([like, like, like, like])
        if category:
            where.append("category = %s")
            params.append(category)
        if difficulty:
            where.append("difficulty_level = %s")
            params.append(difficulty)

        sql = """
            SELECT term_id, term, definition, easy_explanation, hard_explanation,
                   category, difficulty_level, related_terms, examples, created_at, updated_at
            FROM glossary
        """
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY term_id ASC LIMIT %s"
        params.append(limit)

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()

# ---------- Vector 2차 조회 ----------

def _vector_search_glossary(query: str, k: int) -> List[Tuple[Document, float]]:
    vs = _get_glossary_vectorstore()
    pairs = vs.similarity_search_with_score(query, k=k)
    # pairs: List[Tuple[Document, score(float)]]
    return pairs

# ---------- 결과 포맷/설명 선택 ----------

def _pick_explanation(row: Dict[str, Any], difficulty_mode: str) -> str:
    """난이도 모드에 맞는 설명 선택."""
    if difficulty_mode == "easy":
        return row.get("easy_explanation") or row.get("definition") or ""
    if difficulty_mode == "hard":
        return row.get("hard_explanation") or row.get("definition") or ""
    # auto: difficulty_level 보고 우선순위 선택
    level = (row.get("difficulty_level") or "").lower()
    if level in ("beginner", "intermediate") and row.get("easy_explanation"):
        return row["easy_explanation"]
    if level == "advanced" and row.get("hard_explanation"):
        return row["hard_explanation"]
    return row.get("easy_explanation") or row.get("hard_explanation") or row.get("definition") or ""

def _format_glossary_md(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "관련 용어를 찾을 수 없습니다."
    out: List[str] = ["## 용어집 검색 결과\n"]
    for i, r in enumerate(items, 1):
        out.append(f"### {i}. {r.get('term','(term)')}")
        out.append(f"- **카테고리**: {r.get('category','')}")
        out.append(f"- **난이도**: {r.get('difficulty_level','')}")
        if r.get("score") is not None:
            out.append(f"- **유사도 점수(낮을수록 유사)**: {r['score']:.4f}")
        if r.get("related_terms"):
            out.append(f"- **연관 용어**: {', '.join(r['related_terms']) if isinstance(r['related_terms'], list) else r['related_terms']}")
        if r.get("examples"):
            out.append(f"- **예시**: {r['examples']}")
        if r.get("definition"):
            out.append(f"- **정의**: {r['definition']}")
        if r.get("explanation"):
            out.append(f"\n{r['explanation']}\n")
        out.append("\n---\n")
    return "\n".join(out)

# ---------- @tool: 용어집 검색 ----------
@tool
def search_glossary(
    query: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: str = "auto",  # 'easy' | 'hard' | 'auto'
    mode: str = "hybrid",      # 'hybrid' | 'sql' | 'vector'
    top_k: int = 5,
    with_scores: bool = True,
) -> str:
    """
    용어집 검색 도구 (하이브리드/SQL/Vector 지원).
    - SQL: ILIKE + 필터
    - Vector: glossary_embeddings 컬렉션
    - hybrid: 두 결과 병합 후 dedup
    """
    items: List[Dict[str, Any]] = []

    if mode in ("hybrid", "vector") and query:
        try:
            vector_pairs = _vector_search_glossary(query, k=top_k)
            for doc, score in vector_pairs:
                md = doc.metadata or {}
                row = {
                    "term": md.get("term") or md.get("title") or "",
                    "category": md.get("category"),
                    "difficulty_level": md.get("difficulty_level"),
                    "related_terms": md.get("related_terms"),
                    "examples": md.get("examples"),
                    "definition": md.get("definition"),
                    "explanation": _pick_explanation(md, difficulty),
                    "score": float(score) if with_scores else None,
                }
                items.append(row)
        except Exception:
            # 벡터 인덱스가 비어 있거나 컬렉션 미생성 시 조용히 패스 (hybrid면 SQL로 보완)
            pass

    if mode in ("hybrid", "sql"):
        sql_rows = _fetch_glossary_sql(
            query=query,
            category=category,
            difficulty=(difficulty if difficulty in ("beginner", "intermediate", "advanced") else None),
            limit=top_k,
        )
        for r in sql_rows:
            items.append({
                "term": r.get("term"),
                "category": r.get("category"),
                "difficulty_level": r.get("difficulty_level"),
                "related_terms": r.get("related_terms"),
                "examples": r.get("examples"),
                "definition": r.get("definition"),
                "explanation": _pick_explanation(r, difficulty),
                "score": None,
            })

    # 간단 dedup (term, definition)
    seen = set()
    uniq: List[Dict[str, Any]] = []
    for it in items:
        key = (it.get("term"), it.get("definition"))
        if key not in seen:
            seen.add(key)
            uniq.append(it)

    # top_k 보장
    return _format_glossary_md(uniq[:top_k])



