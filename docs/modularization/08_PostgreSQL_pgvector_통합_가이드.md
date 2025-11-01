# 08. PostgreSQL + pgvector 통합 솔루션 가이드

## 문서 정보
- **작성일**: 2025-11-01
- **프로젝트명**: 논문 리뷰 챗봇 (AI Agent + RAG)
- **팀명**: 연결의 민족
- **목적**: PostgreSQL + pgvector 통합 솔루션 완벽 가이드

---

## 목차
1. [개요](#1-개요)
2. [필수 패키지 설치](#2-필수-패키지-설치)
3. [PostgreSQL 설치 및 설정](#3-postgresql-설치-및-설정)
4. [pgvector Extension 설치](#4-pgvector-extension-설치)
5. [환경 변수 설정](#5-환경-변수-설정)
6. [데이터베이스 생성](#6-데이터베이스-생성)
7. [스키마 생성](#7-스키마-생성)
8. [Python에서 DB 연결](#8-python에서-db-연결)
9. [RDBMS CRUD 작업](#9-rdbms-crud-작업)
10. [pgvector 벡터 검색](#10-pgvector-벡터-검색)
11. [백업 및 복구](#11-백업-및-복구)
12. [트러블슈팅](#12-트러블슈팅)

---

## 1. 개요

### 1.1 PostgreSQL + pgvector란?

**PostgreSQL**은 강력한 오픈소스 관계형 데이터베이스입니다.
**pgvector**는 PostgreSQL에서 벡터 임베딩을 저장하고 유사도 검색을 수행할 수 있게 해주는 확장 기능입니다.

### 1.2 왜 통합 솔루션인가?

기존에는 관계형 데이터(논문 메타데이터)와 벡터 데이터(임베딩)를 별도의 DB에 저장했습니다:
- **관계형 데이터**: PostgreSQL
- **벡터 데이터**: Chroma, Pinecone, Qdrant 등

**통합 솔루션의 장점**:
- 하나의 DB에서 관계형 + 벡터 검색 모두 처리
- 운영 및 유지보수 간소화
- 트랜잭션 일관성 보장
- Langchain과 완벽한 통합

### 1.3 프로젝트 데이터 구조

```
PostgreSQL (papers DB)
├── papers 테이블 (관계형)             # 논문 메타데이터
├── glossary 테이블 (관계형)           # 용어집
├── query_logs 테이블 (관계형)         # 사용자 질의 로그
├── paper_chunks (pgvector)          # 논문 본문 청크 임베딩
├── paper_abstracts (pgvector)       # 논문 초록 임베딩
└── glossary_embeddings (pgvector)   # 용어집 임베딩
```

---

## 2. 필수 패키지 설치

### 2.1 requirements.txt 업데이트

프로젝트 루트의 `requirements.txt` 파일에 다음 패키지를 추가합니다:

```txt
# ------------------------- PostgreSQL 및 pgvector ------------------------- #
psycopg2-binary==2.9.9                # PostgreSQL 어댑터
pgvector==0.2.3                       # pgvector Python 클라이언트

# ------------------------- Langchain PostgreSQL ------------------------- #
langchain-postgres==0.0.1             # Langchain PostgreSQL 통합

# ------------------------- Database 유틸리티 ------------------------- #
python-dotenv==1.0.0                  # 환경 변수 관리
```

### 2.2 pip 설치 명령어

```bash
# ------------------------- 가상 환경 활성화 ------------------------- #
# 방식 1
source venv/bin/activate              # Linux/Mac
# venv\Scripts\activate               # Windows

# 방식 2
pyenv activate langchain_py3_11_9

# ------------------------- 패키지 설치 ------------------------- #
pip install -r requirements.txt

# 또는 개별 설치
pip install psycopg2-binary==2.9.9
pip install pgvector==0.2.3
pip install langchain-postgres==0.0.1
pip install python-dotenv==1.0.0
```

### 2.3 설치 확인

```bash
# Python에서 import 테스트
python -c "import psycopg2; print('psycopg2 설치 완료')"
python -c "import pgvector; print('pgvector 설치 완료')"
```

---

## 3. PostgreSQL 설치 및 설정

### 3.1 PostgreSQL 15+ 설치

#### Linux (Ubuntu/Debian)

```bash
# ---------------------- PostgreSQL 패키지 저장소 추가 ---------------------- #
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# ---------------------- 패키지 업데이트 및 설치 ---------------------- #
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15

# ---------------------- PostgreSQL 서비스 시작 ---------------------- #
sudo systemctl start postgresql
sudo systemctl enable postgresql          # 부팅 시 자동 시작

# ---------------------- 설치 확인 ---------------------- #
psql --version                            # PostgreSQL 버전 확인
```

#### macOS (Homebrew)

```bash
# ---------------------- Homebrew로 PostgreSQL 설치 ---------------------- #
brew install postgresql@15

# ---------------------- PostgreSQL 서비스 시작 ---------------------- #
brew services start postgresql@15

# ---------------------- 설치 확인 ---------------------- #
psql --version
```

#### Windows

1. [PostgreSQL 공식 사이트](https://www.postgresql.org/download/windows/) 접속
2. Windows용 설치 프로그램 다운로드
3. 설치 마법사 실행
4. 설치 경로 및 비밀번호 설정
5. Port 5432 (기본값) 사용

### 3.2 PostgreSQL 사용자 생성 및 설정

**중요**: 이 단계는 반드시 먼저 완료해야 합니다!

```bash
# ---------------------- postgres 사용자로 접속 ---------------------- #
sudo -u postgres psql

# ---------------------- langchain 사용자 생성 ---------------------- #
# .env 파일의 POSTGRES_USER, POSTGRES_PASSWORD와 동일하게 설정
CREATE USER langchain WITH PASSWORD 'dusrufdmlalswhr';

# ---------------------- 데이터베이스 생성 권한 부여 ---------------------- #
ALTER USER langchain CREATEDB;

# ---------------------- 슈퍼유저 권한 부여 (개발 환경) ---------------------- #
ALTER USER langchain WITH SUPERUSER;

# ---------------------- 사용자 생성 확인 ---------------------- #
\du

# ---------------------- 출력 예시 ---------------------- #
#                                   List of roles
#  Role name |                         Attributes
# -----------+------------------------------------------------------------
#  langchain | Superuser, Create DB
#  postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS

# ---------------------- 종료 ---------------------- #
\q
```

**확인**: langchain 사용자가 목록에 나타나야 합니다.

---

## 4. pgvector Extension 설치

### 4.1 pgvector 소스 설치

```bash
# ---------------------- 필수 패키지 설치 ---------------------- #
sudo apt install build-essential git postgresql-server-dev-15

# ---------------------- pgvector GitHub 저장소 클론 ---------------------- #
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector

# ---------------------- 컴파일 및 설치 ---------------------- #
make
sudo make install

# ---------------------- PostgreSQL 재시작 ---------------------- #
sudo systemctl restart postgresql
```

### 4.2 Extension 활성화

**방법 1: postgres 관리자로 활성화 (권장)**

```bash
# ---------------------- postgres 사용자로 접속 ---------------------- #
sudo -u postgres psql

# ---------------------- vector extension 생성 ---------------------- #
CREATE EXTENSION vector;

# ---------------------- Extension 확인 ---------------------- #
\dx

# ---------------------- 출력 예시 ---------------------- #
#                  List of installed extensions
#   Name   | Version |   Schema   |         Description
# ---------+---------+------------+------------------------------
#  plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
#  vector  | 0.5.0   | public     | vector data type and ivfflat...

# ---------------------- 종료 ---------------------- #
\q
```

**방법 2: langchain 사용자로 활성화**

```bash
# ---------------------- langchain 사용자로 접속 ---------------------- #
psql -U langchain -d postgres -h localhost

# 비밀번호 입력 프롬프트:
# Password for user langchain: dusrufdmlalswhr

# ---------------------- vector extension 생성 ---------------------- #
CREATE EXTENSION vector;

# ---------------------- Extension 확인 ---------------------- #
\dx

# ---------------------- 종료 ---------------------- #
\q
```

**참고**: `-h localhost`를 추가하면 TCP/IP 연결을 사용하여 비밀번호 인증이 정상 작동합니다.

---

## 5. 환경 변수 설정

### 5.1 .env 파일 확인

프로젝트 루트의 `.env` 파일에 데이터베이스 연결 정보가 설정되어 있습니다:

```bash
# ==================== PostgreSQL 설정 ==================== #
POSTGRES_USER=langchain
POSTGRES_PASSWORD=dusrufdmlalswhr
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=papers
```

### 5.2 실제 값으로 변경

```bash
# .env 파일 편집
vi .env

# 예시 (실제 값으로 변경)
POSTGRES_USER=langchain
POSTGRES_PASSWORD=dusrufdmlalswhr
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=papers
```

### 5.3 환경 변수 로드 테스트

```python
# ------------------------- 표준 라이브러리 ------------------------- #
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 확인
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")
```

---

## 6. 데이터베이스 생성

### 6.1 papers 데이터베이스 생성

```bash
# ---------------------- PostgreSQL 접속 ---------------------- #
psql -U langchain -d postgres

# ---------------------- papers 데이터베이스 생성 ---------------------- #
CREATE DATABASE papers;

# ---------------------- 데이터베이스 확인 ---------------------- #
\l

# ---------------------- 출력 예시 ---------------------- #
#      Name       |  Owner   | Encoding | Collate | Ctype
# ----------------+----------+----------+---------+---------
#  papers         | langchain | UTF8     | en_US.UTF-8 | en_US.UTF-8
#  postgres       | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8

# ---------------------- papers DB로 전환 ---------------------- #
\c papers

# ---------------------- vector extension 활성화 ---------------------- #
CREATE EXTENSION vector;

# ---------------------- Extension 확인 ---------------------- #
\dx

# ---------------------- 종료 ---------------------- #
\q
```

### 6.2 Python 스크립트로 자동 생성

**파일 경로**: `scripts/init_database.py`

```python
# scripts/init_database.py

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
```

**실행:**

```bash
python scripts/init_database.py
```

---

## 7. 스키마 생성

### 7.1 SQL 스크립트 파일 작성

**파일 경로**: `database/schema.sql`

```sql
-- database/schema.sql

-- ==================== pgvector Extension 활성화 ==================== --
CREATE EXTENSION IF NOT EXISTS vector;


-- ==================== papers 테이블 (논문 메타데이터) ==================== --
CREATE TABLE IF NOT EXISTS papers (
    paper_id SERIAL PRIMARY KEY,                        -- 논문 고유 ID
    title VARCHAR(500) NOT NULL,                        -- 논문 제목
    authors TEXT,                                       -- 저자 목록 (JSON 또는 TEXT)
    publish_date DATE,                                  -- 발표 날짜
    source VARCHAR(100),                                -- 출처 (arXiv, IEEE, ACL 등)
    url TEXT UNIQUE,                                    -- 논문 URL (중복 방지)
    category VARCHAR(100),                              -- 카테고리 (cs.AI, cs.CL, cs.CV 등)
    citation_count INT DEFAULT 0,                       -- 인용 수
    abstract TEXT,                                      -- 논문 초록
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- 생성 시간
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- 수정 시간
);

-- ---------------------- papers 테이블 인덱스 ---------------------- --
CREATE INDEX IF NOT EXISTS idx_papers_title ON papers USING GIN (to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_papers_category ON papers(category);
CREATE INDEX IF NOT EXISTS idx_papers_publish_date ON papers(publish_date DESC);
CREATE INDEX IF NOT EXISTS idx_papers_created_at ON papers(created_at DESC);


-- ==================== glossary 테이블 (용어집) ==================== --
CREATE TABLE IF NOT EXISTS glossary (
    term_id SERIAL PRIMARY KEY,                         -- 용어 고유 ID
    term VARCHAR(200) NOT NULL UNIQUE,                  -- 용어
    definition TEXT NOT NULL,                           -- 기본 정의
    easy_explanation TEXT,                              -- Easy 모드 설명
    hard_explanation TEXT,                              -- Hard 모드 설명
    category VARCHAR(100),                              -- 카테고리 (ML, NLP, CV, RL 등)
    difficulty_level VARCHAR(20),                       -- 난이도 (beginner, intermediate, advanced)
    related_terms TEXT[],                               -- 관련 용어 배열
    examples TEXT,                                      -- 사용 예시
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- 생성 시간
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- 수정 시간
);

-- ---------------------- glossary 테이블 인덱스 ---------------------- --
CREATE INDEX IF NOT EXISTS idx_glossary_term ON glossary(term);
CREATE INDEX IF NOT EXISTS idx_glossary_category ON glossary(category);
CREATE INDEX IF NOT EXISTS idx_glossary_difficulty ON glossary(difficulty_level);


-- ==================== query_logs 테이블 (사용자 질의 로그) ==================== --
CREATE TABLE IF NOT EXISTS query_logs (
    log_id SERIAL PRIMARY KEY,                          -- 로그 고유 ID
    user_query TEXT NOT NULL,                           -- 사용자 질문
    difficulty_mode VARCHAR(20),                        -- 난이도 모드 (easy, hard)
    tool_used VARCHAR(50),                              -- 사용된 도구명
    response TEXT,                                      -- 생성된 응답
    response_time_ms INT,                               -- 응답 시간 (밀리초)
    success BOOLEAN DEFAULT TRUE,                       -- 성공 여부
    error_message TEXT,                                 -- 오류 메시지 (있는 경우)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- 생성 시간
);

-- ---------------------- query_logs 테이블 인덱스 ---------------------- --
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_logs_tool_used ON query_logs(tool_used);
CREATE INDEX IF NOT EXISTS idx_query_logs_success ON query_logs(success);
```

### 7.2 스크립트 실행

```bash
# ---------------------- SQL 스크립트 실행 ---------------------- #
psql -U langchain -d papers -f database/schema.sql

# ---------------------- 출력 예시 ---------------------- #
# CREATE EXTENSION
# CREATE TABLE
# CREATE INDEX
# CREATE INDEX
# ...
```

### 7.3 테이블 확인

```bash
# ---------------------- PostgreSQL 접속 ---------------------- #
psql -U langchain -d papers

# ---------------------- 테이블 목록 확인 ---------------------- #
\dt

# ---------------------- 출력 예시 ---------------------- #
#          List of relations
#  Schema |    Name     | Type  |     Owner
# --------+-------------+-------+----------------
#  public | glossary    | table | langchain
#  public | papers      | table | langchain
#  public | query_logs  | table | langchain

# ---------------------- papers 테이블 구조 확인 ---------------------- #
\d papers

# ---------------------- 종료 ---------------------- #
\q
```

---

## 8. Python에서 DB 연결

### 8.1 config_loader를 활용한 DB 연결

**설정 파일 구조**:
```
.env (환경 변수)
  ↓
configs/db_config.yaml (설정 파일, ${VAR} 형태로 환경 변수 참조)
  ↓
src/utils/config_loader.py (YAML 로드 및 환경 변수 치환)
  ↓
src/utils/db.py (Connection Pool)
```

### 8.2 Connection Pool 구현

**파일 경로**: `src/utils/db.py`

```python
# src/utils/db.py

# ------------------------- 서드파티 라이브러리 ------------------------- #
import psycopg2
from psycopg2 import pool

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.utils.config_loader import get_db_config


# ==================== PostgreSQL Connection Pool ==================== #
class PostgreSQLConnectionPool:
    """
    PostgreSQL 연결 풀 관리 클래스

    configs/db_config.yaml 설정 파일을 사용하여 연결합니다.
    """

    def __init__(self, min_connections=1, max_connections=10):
        """
        연결 풀 초기화

        Args:
            min_connections: 최소 연결 수
            max_connections: 최대 연결 수
        """
        # configs/db_config.yaml에서 설정 로드
        db_config = get_db_config()
        pg_config = db_config['postgresql']

        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=min_connections,                        # 최소 연결 수
            maxconn=max_connections,                        # 최대 연결 수
            host=pg_config['host'],
            port=pg_config['port'],
            database=pg_config['database'],
            user=pg_config['user'],
            password=pg_config['password']
        )

    # ---------------------- 연결 가져오기 ---------------------- #
    def get_connection(self):
        """
        연결 풀에서 연결 가져오기

        Returns:
            psycopg2 connection 객체
        """
        return self.connection_pool.getconn()

    # ---------------------- 연결 반환 ---------------------- #
    def put_connection(self, connection):
        """
        연결을 풀에 반환

        Args:
            connection: psycopg2 connection 객체
        """
        self.connection_pool.putconn(connection)

    # ---------------------- 연결 풀 종료 ---------------------- #
    def close_all_connections(self):
        """
        모든 연결 종료
        """
        self.connection_pool.closeall()


# ==================== 전역 연결 풀 인스턴스 ==================== #
connection_pool = PostgreSQLConnectionPool()


# ==================== 간단한 쿼리 실행 함수 ==================== #
def execute_query(query, params=None, fetch=False):
    """
    SQL 쿼리 실행 (INSERT, UPDATE, DELETE, SELECT)

    Args:
        query: SQL 쿼리문
        params: 쿼리 파라미터 (선택)
        fetch: True면 결과 반환, False면 None

    Returns:
        fetch=True: 조회 결과 리스트
        fetch=False: None
    """
    conn = connection_pool.get_connection()          # 연결 가져오기
    cursor = conn.cursor()

    try:
        # 쿼리 실행
        cursor.execute(query, params)
        conn.commit()                                # 트랜잭션 커밋

        # 결과 조회
        if fetch:
            result = cursor.fetchall()               # 모든 결과 가져오기
            return result
        else:
            return None

    except Exception as e:
        conn.rollback()                              # 오류 발생 시 롤백
        raise e

    finally:
        cursor.close()
        connection_pool.put_connection(conn)        # 연결 반환
```

### 8.2 연결 테스트

```python
# test_db_connection.py

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.utils.db import execute_query

# ---------------------- PostgreSQL 버전 확인 ---------------------- #
result = execute_query("SELECT version()", fetch=True)
print(f"PostgreSQL 버전: {result[0][0]}")

# ---------------------- papers 테이블 개수 확인 ---------------------- #
result = execute_query("SELECT COUNT(*) FROM papers", fetch=True)
print(f"papers 테이블 레코드 수: {result[0][0]}")
```

**실행:**

```bash
python test_db_connection.py
```

---

## 9. RDBMS CRUD 작업

### 9.1 CREATE (삽입)

#### 9.1.1 단일 논문 삽입

```python
# ------------------------- 프로젝트 모듈 ------------------------- #
from src.utils.db import execute_query

# ---------------------- 논문 데이터 삽입 ---------------------- #
def insert_paper(title, authors, publish_date, source, url, category, abstract):
    """
    papers 테이블에 논문 데이터 삽입

    Args:
        title: 논문 제목
        authors: 저자 목록
        publish_date: 발표 날짜 (YYYY-MM-DD)
        source: 출처 (arXiv, IEEE 등)
        url: 논문 URL
        category: 카테고리
        abstract: 초록

    Returns:
        삽입된 paper_id
    """
    query = """
        INSERT INTO papers (title, authors, publish_date, source, url, category, abstract)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
        RETURNING paper_id;
    """

    params = (title, authors, publish_date, source, url, category, abstract)
    result = execute_query(query, params, fetch=True)

    if result:
        paper_id = result[0][0]
        print(f"✅ 논문 삽입 완료: paper_id = {paper_id}")
        return paper_id
    else:
        print("ℹ️ 이미 존재하는 논문입니다 (URL 중복)")
        return None


# ---------------------- 사용 예시 ---------------------- #
insert_paper(
    title="Attention Is All You Need",
    authors="Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin",
    publish_date="2017-06-12",
    source="arXiv",
    url="https://arxiv.org/abs/1706.03762",
    category="cs.CL",
    abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks..."
)
```

#### 9.1.2 여러 논문 일괄 삽입

```python
# ---------------------- 여러 논문 일괄 삽입 ---------------------- #
def insert_papers_batch(papers_data):
    """
    여러 논문을 일괄 삽입

    Args:
        papers_data: 논문 데이터 리스트 (딕셔너리)

    Returns:
        삽입된 paper_id 리스트
    """
    paper_ids = []

    for paper in papers_data:
        paper_id = insert_paper(
            title=paper['title'],
            authors=paper['authors'],
            publish_date=paper['publish_date'],
            source=paper.get('source', 'arXiv'),
            url=paper['url'],
            category=paper.get('category', 'cs.AI'),
            abstract=paper.get('abstract', '')
        )

        if paper_id:
            paper_ids.append(paper_id)

    print(f"✅ 총 {len(paper_ids)}개 논문 삽입 완료")
    return paper_ids


# ---------------------- 사용 예시 ---------------------- #
papers = [
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers",
        "authors": "Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova",
        "publish_date": "2018-10-11",
        "url": "https://arxiv.org/abs/1810.04805",
        "category": "cs.CL",
        "abstract": "We introduce BERT..."
    },
    {
        "title": "GPT-3: Language Models are Few-Shot Learners",
        "authors": "Tom B. Brown, Benjamin Mann, Nick Ryder, et al.",
        "publish_date": "2020-05-28",
        "url": "https://arxiv.org/abs/2005.14165",
        "category": "cs.CL",
        "abstract": "Recent work has demonstrated..."
    }
]

insert_papers_batch(papers)
```

### 9.2 READ (조회)

#### 9.2.1 전체 논문 조회

```python
# ---------------------- 전체 논문 조회 ---------------------- #
def get_all_papers(limit=10):
    """
    모든 논문 조회

    Args:
        limit: 조회할 최대 개수

    Returns:
        논문 데이터 리스트
    """
    query = """
        SELECT paper_id, title, authors, publish_date, source, category
        FROM papers
        ORDER BY created_at DESC
        LIMIT %s;
    """

    result = execute_query(query, (limit,), fetch=True)

    # 출력
    for row in result:
        print(f"[{row[0]}] {row[1]} ({row[3]})")

    return result


# ---------------------- 사용 예시 ---------------------- #
get_all_papers(limit=5)
```

#### 9.2.2 특정 논문 조회 (paper_id)

```python
# ---------------------- 특정 논문 조회 ---------------------- #
def get_paper_by_id(paper_id):
    """
    paper_id로 특정 논문 조회

    Args:
        paper_id: 논문 ID

    Returns:
        논문 데이터 (딕셔너리)
    """
    query = """
        SELECT paper_id, title, authors, publish_date, source, url, category, abstract
        FROM papers
        WHERE paper_id = %s;
    """

    result = execute_query(query, (paper_id,), fetch=True)

    if result:
        row = result[0]
        paper_data = {
            "paper_id": row[0],
            "title": row[1],
            "authors": row[2],
            "publish_date": row[3],
            "source": row[4],
            "url": row[5],
            "category": row[6],
            "abstract": row[7]
        }
        return paper_data
    else:
        print(f"ℹ️ paper_id {paper_id}에 해당하는 논문이 없습니다")
        return None


# ---------------------- 사용 예시 ---------------------- #
paper = get_paper_by_id(1)
print(f"제목: {paper['title']}")
print(f"저자: {paper['authors']}")
```

#### 9.2.3 키워드 검색

```python
# ---------------------- 제목으로 논문 검색 ---------------------- #
def search_papers_by_title(keyword):
    """
    제목에 키워드가 포함된 논문 검색

    Args:
        keyword: 검색 키워드

    Returns:
        검색 결과 리스트
    """
    query = """
        SELECT paper_id, title, authors, publish_date
        FROM papers
        WHERE title ILIKE %s
        ORDER BY publish_date DESC;
    """

    # ILIKE: 대소문자 구분 없는 검색
    result = execute_query(query, (f"%{keyword}%",), fetch=True)

    # 출력
    for row in result:
        print(f"[{row[0]}] {row[1]} ({row[3]})")

    return result


# ---------------------- 사용 예시 ---------------------- #
search_papers_by_title("Transformer")
```

### 9.3 UPDATE (수정)

```python
# ---------------------- 논문 인용 수 업데이트 ---------------------- #
def update_citation_count(paper_id, citation_count):
    """
    논문 인용 수 업데이트

    Args:
        paper_id: 논문 ID
        citation_count: 새로운 인용 수
    """
    query = """
        UPDATE papers
        SET citation_count = %s, updated_at = CURRENT_TIMESTAMP
        WHERE paper_id = %s;
    """

    execute_query(query, (citation_count, paper_id))
    print(f"✅ paper_id {paper_id}의 인용 수를 {citation_count}로 업데이트 완료")


# ---------------------- 사용 예시 ---------------------- #
update_citation_count(paper_id=1, citation_count=5000)
```

### 9.4 DELETE (삭제)

```python
# ---------------------- 논문 삭제 ---------------------- #
def delete_paper(paper_id):
    """
    특정 논문 삭제

    Args:
        paper_id: 논문 ID
    """
    query = """
        DELETE FROM papers
        WHERE paper_id = %s;
    """

    execute_query(query, (paper_id,))
    print(f"✅ paper_id {paper_id} 삭제 완료")


# ---------------------- 사용 예시 ---------------------- #
delete_paper(paper_id=100)
```

---

## 10. pgvector 벡터 검색

### 10.1 Langchain PGVector 설정

```python
# src/rag/vector_store.py

# ------------------------- 표준 라이브러리 ------------------------- #
import os

# ------------------------- 서드파티 라이브러리 ------------------------- #
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.utils.config_loader import get_postgres_connection_string, get_model_config


# ==================== PGVector VectorStore 초기화 ==================== #
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
        # configs/model_config.yaml에서 모델 설정 로드
        model_config = get_model_config()
        embedding_config = model_config['embeddings']

        # OpenAI Embeddings 초기화
        self.embeddings = OpenAIEmbeddings(
            model=embedding_config['model'],
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # configs/db_config.yaml에서 PostgreSQL 연결 문자열 가져오기
        self.connection_string = get_postgres_connection_string()

        # PGVector VectorStore 초기화
        self.vectorstore = PGVector(
            collection_name=collection_name,                # 컬렉션 이름
            embedding_function=self.embeddings,             # 임베딩 함수
            connection_string=self.connection_string        # DB 연결 문자열
        )

    # ---------------------- 문서 추가 ---------------------- #
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

    # ---------------------- 유사도 검색 (Similarity Search) ---------------------- #
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

    # ---------------------- MMR 검색 (다양성) ---------------------- #
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

    # ---------------------- 유사도 점수 포함 검색 ---------------------- #
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
```

### 10.2 벡터 검색 예제

```python
# ---------------------- PaperVectorStore 인스턴스 생성 ---------------------- #
vector_store = PaperVectorStore(collection_name="paper_chunks")

# ---------------------- 유사도 검색 ---------------------- #
query = "What is the transformer architecture?"
docs = vector_store.similarity_search(query, k=5)

# 검색 결과 출력
for i, doc in enumerate(docs, 1):
    print(f"[{i}] {doc.page_content[:200]}...")
    print(f"    메타데이터: {doc.metadata}")
    print()

# ---------------------- MMR 검색 (다양성) ---------------------- #
docs = vector_store.mmr_search(query, k=5, lambda_mult=0.5)

# ---------------------- 유사도 점수 포함 검색 ---------------------- #
docs_with_scores = vector_store.similarity_search_with_score(query, k=5)
```

---

## 11. 백업 및 복구

### 11.1 전체 데이터베이스 백업

```bash
# ---------------------- 전체 DB 백업 ---------------------- #
pg_dump -U langchain -d papers -F c -f backup_papers_$(date +%Y%m%d_%H%M%S).dump

# -F c: Custom 포맷 (압축 및 병렬 복구 지원)
# -f: 출력 파일명
```

### 11.2 특정 테이블만 백업

```bash
# ---------------------- papers 테이블만 백업 ---------------------- #
pg_dump -U langchain -d papers -t papers -F c -f papers_backup.dump

# ---------------------- glossary 테이블만 백업 ---------------------- #
pg_dump -U langchain -d papers -t glossary -F c -f glossary_backup.dump
```

### 11.3 데이터베이스 복원

```bash
# ---------------------- 새 데이터베이스 생성 ---------------------- #
createdb -U langchain papers_restored

# ---------------------- 백업 파일 복원 ---------------------- #
pg_restore -U langchain -d papers_restored backup_papers_20251101_120000.dump

# ---------------------- 복원 확인 ---------------------- #
psql -U langchain -d papers_restored -c "SELECT COUNT(*) FROM papers"
```

### 11.4 자동 백업 스크립트

```bash
# scripts/backup_database.sh

#!/bin/bash

# ==================== PostgreSQL 자동 백업 스크립트 ==================== #

# 환경 변수 로드
source .env

# 백업 디렉토리 생성
BACKUP_DIR="backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 전체 DB 백업
pg_dump -U $POSTGRES_USER -d $POSTGRES_DB -F c -f "$BACKUP_DIR/papers_full_$(date +%H%M%S).dump"

echo "✅ 백업 완료: $BACKUP_DIR"

# 7일 이상 된 백업 파일 삭제
find backups/ -type f -mtime +7 -delete
```

**실행:**

```bash
chmod +x scripts/backup_database.sh
./scripts/backup_database.sh
```

---

## 12. 트러블슈팅

### 12.1 PostgreSQL 연결 오류

**문제:**
```
psycopg2.OperationalError: could not connect to server
```

**해결:**
```bash
# PostgreSQL 실행 확인
sudo systemctl status postgresql

# PostgreSQL 시작
sudo systemctl start postgresql

# 연결 테스트
psql -U langchain -d papers -h localhost
```

### 12.2 pgvector Extension 오류

**문제:**
```
ERROR: extension "vector" is not available
```

**해결:**
```bash
# pgvector 재설치
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make clean
make
sudo make install

# PostgreSQL 재시작
sudo systemctl restart postgresql

# Extension 생성
psql -U langchain -d papers -c "CREATE EXTENSION vector;"
```

### 12.3 권한 오류

**문제:**
```
ERROR: permission denied for table papers
```

**해결:**
```bash
# PostgreSQL 접속
psql -U postgres -d papers

# 권한 부여
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO langchain;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO langchain;

# 종료
\q
```

### 12.4 Langchain PGVector 연결 오류

**문제:**
```
ImportError: cannot import name 'PGVector' from 'langchain_postgres'
```

**해결:**
```bash
# langchain-postgres 재설치
pip uninstall langchain-postgres
pip install langchain-postgres==0.0.1

# 또는 최신 버전 설치
pip install langchain-postgres --upgrade
```

---

## 마무리

이제 PostgreSQL + pgvector 통합 솔루션을 완벽하게 설정하고 사용할 수 있습니다!

### 다음 단계

1. **논문 데이터 수집**: `scripts/collect_arxiv_papers.py` 실행
2. **PDF 처리**: `src/data/document_loader.py` 실행
3. **임베딩 생성 및 저장**: `src/data/embeddings.py` 실행
4. **벡터 검색 테스트**: RAG 도구 구현

### 참고 문서

- [11_데이터베이스_설계.md](../PRD/11_데이터베이스_설계.md)
- [담당역할_03_박재홍_논문데이터수집.md](../roles/담당역할_03_박재홍_논문데이터수집.md)
- PostgreSQL 공식 문서: https://www.postgresql.org/docs/
- pgvector GitHub: https://github.com/pgvector/pgvector
- Langchain PGVector: https://python.langchain.com/docs/integrations/vectorstores/pgvector
