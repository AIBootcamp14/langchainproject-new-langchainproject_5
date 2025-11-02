# ==========================================
# 📘 Phase 1: 인덱싱/시드 스크립트 (논문)
# 📍 Step 2: papers → paper_chunks 컬렉션 시딩
# ------------------------------------------
# - papers 테이블에서 title/authors/abstract 추출
# - Document化 후 PGVector에 upsert
# - 검색 정확도 향상을 위한 기본 메타 삽입
# ==========================================

import os
import psycopg2
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings

# ---------- 환경/커넥션 ----------

def _env(primary: str, alt: str, default=None):
    return os.getenv(primary) or os.getenv(alt) or default

def _pg_conn_str() -> str:
    user = _env("POSTGRES_USER", "PGUSER", "postgres")
    password = _env("POSTGRES_PASSWORD", "PGPASSWORD", "postgres")
    host = _env("POSTGRES_HOST", "PGHOST", "localhost")
    port = _env("POSTGRES_PORT", "PGPORT", "5432")
    db = _env("POSTGRES_DB", "PGDATABASE", "papers")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

def main():
    """papers 테이블에서 초록 기반으로 paper_chunks 컬렉션을 시드."""
    load_dotenv()  # .env 로드
    conn_str = _pg_conn_str()

    # 1) PostgreSQL에서 논문 메타(초록) 가져오기
    pg = psycopg2.connect(conn_str)
    cur = pg.cursor()
    # 초록이 있는 논문 10개 정도만
    cur.execute("""
        SELECT paper_id, title, authors, COALESCE(abstract, '') AS abstract
        FROM papers
        WHERE abstract IS NOT NULL AND abstract <> ''
        ORDER BY paper_id ASC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    pg.close()

    if not rows:
        print("[seed] papers 테이블에 초록(abstract)이 없습니다. 최소 1개 이상 넣어주세요.")
        return

    # 2) 문서 리스트 구성
    docs = []
    for paper_id, title, authors, abstract in rows:
        # 검색에 잘 잡히도록 title + abstract 결합
        content = f"Title: {title}\nAuthors: {authors}\n\nAbstract:\n{abstract}"
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "paper_id": paper_id,
                    "title": title,
                    "authors": authors,
                    "section": "Abstract",
                    # 연도 필터 예시용: publish_date에서 연도를 뽑아 metadata로 넣고 싶다면
                    # 별도 쿼리에서 year를 가져와 추가해도 됩니다.
                },
            )
        )

    # 3) 임베딩 & 벡터스토어 초기화
    embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))

    # 최신 langchain-postgres 시그니처: connection=, embeddings=
    vectorstore = PGVector(
        collection_name=os.getenv("PGV_COLLECTION_CHUNKS", "paper_chunks"),
        embeddings=embeddings,
        connection=conn_str,
        use_jsonb=True,
    )

    # 4) 문서 추가 (테이블/컬렉션이 없으면 자동 생성)
    ids = vectorstore.add_documents(docs)
    print(f"[seed] upserted {len(ids)} docs into collection '{os.getenv('PGV_COLLECTION_CHUNKS', 'paper_chunks')}'")

if __name__ == "__main__":
    main()

