# ------------------------- 표준 라이브러리 ------------------------- #
import os
from dotenv import load_dotenv

# ------------------------- 서드파티 라이브러리 ------------------------- #
import psycopg2
from psycopg2 import sql

# .env 파일 로드
load_dotenv()


# ---------------------- 데이터베이스 생성 함수 ---------------------- #
def create_database():
    """
    papers 데이터베이스 생성
    """
    # PostgreSQL 기본 DB(postgres)에 연결
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database="postgres"                      # 기본 DB
    )
    conn.autocommit = True                      # 자동 커밋 활성화
    cursor = conn.cursor()

    try:
        # papers DB 생성 (이미 존재하면 건너뛰기)
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'papers'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(os.getenv("POSTGRES_DB"))
            ))
            print(f"✅ 데이터베이스 '{os.getenv('POSTGRES_DB')}' 생성 완료")
        else:
            print(f"ℹ️ 데이터베이스 '{os.getenv('POSTGRES_DB')}'가 이미 존재합니다")

    finally:
        cursor.close()
        conn.close()


# ---------------------- pgvector Extension 활성화 ---------------------- #
def enable_pgvector():
    """
    pgvector extension 활성화
    """
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB")       # papers DB
    )
    cursor = conn.cursor()

    try:
        # vector extension 생성
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        print("✅ pgvector extension 활성화 완료")

    finally:
        cursor.close()
        conn.close()


# ---------------------- 메인 실행부 ---------------------- #
if __name__ == "__main__":
    print("=" * 50)
    print("PostgreSQL 데이터베이스 초기화 시작")
    print("=" * 50)

    # 데이터베이스 생성
    create_database()

    # pgvector Extension 활성화
    enable_pgvector()

    print("=" * 50)
    print("데이터베이스 초기화 완료")
    print("=" * 50)