# 담당역할_05-1: Text-to-SQL 도구 구현

## 문서 정보
- **작성일**: 2025-11-04
- **작성자**: 최현화[팀장]
- **프로젝트명**: 논문 리뷰 챗봇 (AI Agent + RAG)
- **팀명**: 연결의 민족
- **담당 기능**: Text-to-SQL 도구, 자연어 → SQL 변환, 논문 통계 조회

---

## 담당자 정보

**담당자**: 신준엽

**역할**: Text-to-SQL 도구 구현 및 AI Agent 통합

---

## 담당 업무 개요

이 역할은 자연어 질문을 SQL 쿼리로 변환하여 논문 통계 정보를 조회하는 **Text-to-SQL 도구**를 구현하는 것을 담당합니다. 사용자가 "2024년에 발표된 논문 개수는?"과 같은 자연어 질문을 하면 자동으로 SQL 쿼리를 생성하고 실행하여 결과를 Markdown 형식으로 반환합니다.

### 주요 책임

1. **Text-to-SQL 도구 구현** (`src/tools/text2sql.py`)
   - LangChain Tool 정의
   - Few-shot 프롬프트 설계
   - SQL 쿼리 생성 (GPT-5o-mini)
   - 보안 및 안전성 강화 (화이트리스트, 금지 패턴)

2. **데이터베이스 연동**
   - PostgreSQL 연결
   - SQL 쿼리 실행
   - 결과 포맷팅 (Markdown 표)

3. **로깅 시스템**
   - query_logs 테이블에 실행 기록 저장
   - 성공/실패 여부, 응답 시간 기록

---

## 참여 기간 및 우선순위

### 참여 기간
- **구현 기간**: 2025-11-01 ~ 2025-11-04 (4일)
- **통합 및 검증**: 2025-11-04 (1일)

### 우선순위
1. **최우선 (Day 1-2)**: Text-to-SQL 도구 구현
   - LangChain Tool 정의
   - Few-shot 프롬프트 설계
   - SQL 생성 및 실행

2. **우선 (Day 3)**: 보안 및 안전성 강화
   - 화이트리스트 방식 (허용 테이블, 컬럼)
   - 금지 패턴 필터링
   - EXPLAIN 안전 점검

3. **선택 (Day 4)**: AI Agent 통합
   - Agent graph에 text2sql 노드 추가
   - 라우팅 프롬프트 업데이트

---

## 세부 업무 및 구현 내용

### 1. Text-to-SQL 도구 구현

**파일 경로**: `src/tools/text2sql.py`

#### 1.1 LangChain Tool 정의

```python
from langchain.tools import tool

@tool(name="text2sql", return_direct=False)
def text2sql(query: str) -> str:
    """
    자연어 질문을 SQL 쿼리로 변환하여 논문 통계 정보를 조회합니다.

    Args:
        query (str): 자연어 질문

    Returns:
        str: 쿼리 결과 (Markdown 형식)
    """
    # 구현 내용
    pass
```

#### 1.2 Few-shot 프롬프트 설계

**5개 예시**:
1. "2024년에 발표된 논문 개수는?" → `SELECT COUNT(*) FROM papers WHERE EXTRACT(YEAR FROM publish_date)=2024;`
2. "카테고리별 논문 수 보여줘" → `SELECT category, COUNT(*) FROM papers GROUP BY category ORDER BY count DESC;`
3. "가장 많이 인용된 논문 Top 5는?" → `SELECT title, citation_count FROM papers ORDER BY citation_count DESC LIMIT 5;`
4. "arXiv에서 가져온 논문 개수는?" → `SELECT COUNT(*) FROM papers WHERE source='arXiv';`
5. "최근 1년간 발표된 AI 관련 논문은?" → `SELECT COUNT(*) FROM papers WHERE category ILIKE '%AI%' AND publish_date >= NOW() - INTERVAL '1 year';`

#### 1.3 보안 및 안전성

```python
# 화이트리스트 방식
ALLOWED_TABLES = {"papers"}
ALLOWED_COLUMNS = {
    "paper_id", "title", "authors", "publish_date",
    "source", "url", "category", "citation_count",
    "abstract", "created_at", "updated_at"
}

# 금지 패턴
FORBIDDEN_PATTERNS = [
    r"\bDROP\b", r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b",
    r"\bCREATE\b", r"\bALTER\b", r"\bGRANT\b", r"\bREVOKE\b",
    r"--", r";.*SELECT", r"UNION"
]

# SELECT/WITH 쿼리만 허용
if not re.match(r"^\s*(SELECT|WITH)", sql, re.IGNORECASE):
    raise ValueError("SELECT 또는 WITH 쿼리만 허용됩니다")
```

#### 1.4 SQL 실행 및 결과 반환

```python
def _run_query(conn, sql):
    """SQL 실행 및 결과 반환"""
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    return rows, columns

def _to_markdown_table(rows, columns):
    """결과를 Markdown 표로 변환"""
    if not rows:
        return "결과가 없습니다."

    # 헤더
    table = "| " + " | ".join(columns) + " |\n"
    table += "| " + " | ".join(["---"] * len(columns)) + " |\n"

    # 데이터
    for row in rows:
        table += "| " + " | ".join(str(val) for val in row) + " |\n"

    return table
```

---

### 2. 로깅 시스템

**파일 경로**: `src/tools/text2sql.py`

```python
def _log_query(query, sql, success, error_msg=None):
    """쿼리 실행 기록 저장"""
    conn = _get_conn()
    cursor = conn.cursor()

    # query_logs 테이블 생성 (없을 경우)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            log_id SERIAL PRIMARY KEY,
            user_query TEXT NOT NULL,
            generated_sql TEXT,
            success BOOLEAN DEFAULT TRUE,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 로그 삽입
    cursor.execute("""
        INSERT INTO query_logs (user_query, generated_sql, success, error_message)
        VALUES (%s, %s, %s, %s)
    """, (query, sql, success, error_msg))

    conn.commit()
    cursor.close()
    conn.close()
```

---

### 3. AI Agent 통합 (최현화 작업)

#### 3.1 Agent Nodes 추가

**파일**: `src/agent/nodes.py`

```python
from src.tools.text2sql import text2sql

def text2sql_node(state: AgentState, exp_manager=None):
    """
    Text-to-SQL 노드: 자연어 질문을 SQL로 변환하여 논문 통계 조회

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스

    Returns:
        AgentState: 업데이트된 상태
    """
    question = state["question"]

    if exp_manager:
        exp_manager.logger.write(f"Text-to-SQL 노드 실행: {question}")

    # Text-to-SQL 도구 호출
    result = text2sql.run(question)

    if exp_manager:
        exp_manager.logger.write(f"SQL 실행 완료: {len(result)} 글자")

    state["final_answer"] = result
    return state
```

#### 3.2 Agent Graph 등록

**파일**: `src/agent/graph.py`

```python
from src.agent.nodes import text2sql_node

def create_agent_graph(exp_manager=None):
    workflow = StateGraph(AgentState)

    # exp_manager 바인딩
    text2sql_with_exp = partial(text2sql_node, exp_manager=exp_manager)

    # 노드 추가
    workflow.add_node("text2sql", text2sql_with_exp)

    # 조건부 엣지 설정
    workflow.add_conditional_edges(
        "router",
        route_to_tool,
        {
            ...,
            "text2sql": "text2sql"
        }
    )

    # 종료 엣지 설정
    workflow.add_edge("text2sql", END)

    return workflow.compile()
```

#### 3.3 라우팅 프롬프트 업데이트

**파일**: `prompts/routing_prompts.json`

```json
{
  "routing_prompt": "...기존 내용...\n\n6. **text2sql** (논문 통계 정보 조회)\n   - 사용 시기: 논문 통계, 개수, 순위, 분포 조회\n   - 키워드: \"개수\", \"몇 편\", \"순위\", \"Top\", \"평균\", \"분포\", \"카테고리별\"\n   - 예시:\n     * \"2024년에 발표된 논문 개수는?\"\n     * \"카테고리별 논문 수 보여줘\"\n     * \"가장 많이 인용된 논문 Top 5는?\"\n",
  "few_shot_examples": [
    ...,
    {
      "question": "2024년에 발표된 논문 개수는?",
      "tool": "text2sql",
      "reason": "통계 정보 조회 (개수)"
    },
    {
      "question": "카테고리별 논문 수 보여줘",
      "tool": "text2sql",
      "reason": "분포 통계 조회"
    },
    {
      "question": "가장 많이 인용된 논문 Top 5는?",
      "tool": "text2sql",
      "reason": "순위 통계 조회"
    }
  ]
}
```

---

## 참고 PRD 문서

아래 PRD 문서들을 참고하여 구현하세요:

1. **[05_추가선택기능_구현.md](../issues/05_추가선택기능_구현.md)** ⭐⭐⭐
   - Text-to-SQL 구현 가이드
   - 보안 및 안전성 요구사항

2. **[담당역할_05_추가선택기능.md](./담당역할_05_추가선택기능.md)** ⭐⭐⭐
   - Text-to-SQL 도구 상세 설명 (21-192줄)
   - 예제 코드 및 사용법

3. **[11_데이터베이스_설계.md](../PRD/11_데이터베이스_설계.md)** ⭐⭐
   - papers 테이블 스키마
   - 컬럼 목록 및 데이터 타입

---

## 협업 방법

### 다른 담당자와의 협업

#### 1. 최현화 (AI Agent 메인) - Agent 통합
- **협업 내용**: Text-to-SQL 도구를 AI Agent에 통합
- **타이밍**: text2sql.py 구현 완료 후
- **전달 사항**:
  - text2sql Tool 객체 사용법
  - 라우팅 키워드 (통계, 개수, 순위, 분포)
  - 예시 질문 목록

---

## 구현 체크리스트

### Phase 1: Text-to-SQL 도구 구현 (우선순위 1)
- [x] `src/tools/text2sql.py` 파일 생성
- [x] LangChain Tool 정의
- [x] Few-shot 프롬프트 설계 (5개 예시)
- [x] SQL 쿼리 생성 (OpenAI GPT-5o-mini)
- [x] DB 연결 및 쿼리 실행
- [x] 결과 포맷팅 (Markdown 표)

### Phase 2: 보안 및 안전성 강화 (우선순위 2)
- [x] 화이트리스트 방식 구현
  - [x] 허용 테이블: papers
  - [x] 허용 컬럼: 11개
- [x] 금지 패턴 필터링
  - [x] DROP, INSERT, UPDATE, DELETE 금지
  - [x] CREATE, ALTER, GRANT, REVOKE 금지
  - [x] 주석(-), UNION 금지
- [x] SELECT/WITH 쿼리만 허용
- [x] EXPLAIN 안전 점검

### Phase 3: 로깅 시스템 (우선순위 3)
- [x] query_logs 테이블 생성
- [x] 쿼리 실행 기록 저장
  - [x] user_query, generated_sql 저장
  - [x] success, error_message 저장
  - [x] created_at 타임스탬프

### Phase 4: AI Agent 통합 (최현화 작업)
- [x] `src/agent/nodes.py`에 text2sql_node 추가
- [x] `src/agent/graph.py`에 노드 등록
- [x] 조건부 엣지 설정
- [x] 라우팅 프롬프트 업데이트 (`prompts/routing_prompts.json`)

### Phase 5: 테스트 및 문서화
- [x] 단위 테스트 (5개 예시 질문)
- [x] 보안 테스트 (금지 패턴 차단)
- [x] 통합 테스트 (Agent와 연동)
- [x] 사용법 문서화

---

## 규칙 및 주의사항

### 1. 보안 규칙
- **화이트리스트 방식**: 허용된 테이블과 컬럼만 사용
- **SELECT/WITH 전용**: 데이터 조회 쿼리만 허용
- **금지 패턴 차단**: DROP, INSERT, UPDATE, DELETE 등 금지
- **EXPLAIN 검증**: 쿼리 실행 전 안전성 점검

### 2. 코드 품질
- 모든 함수에 한글 주석 작성 (docs/rules/annotate_style.md 준수)
- 섹션 구분선 사용 (등호 20개, 대시 22개)
- 함수별 상세 설명
- 로직 블록별 설명

### 3. 에러 처리
- SQL 생성 실패 시 사용자 친화적 메시지
- DB 연결 실패 시 재시도 로직
- 쿼리 실행 오류 시 상세 에러 메시지

### 4. 성능 고려사항
- 쿼리에 LIMIT 자동 추가 (최대 100행)
- Connection Pool 사용 (psycopg2.pool)
- 응답 시간 목표: p95 ≤ 3000ms

---

## 예상 결과물

### 1. 파일 구조

```
src/
└── tools/
    └── text2sql.py                # Text-to-SQL 도구 (신규)

prompts/
└── routing_prompts.json           # 라우팅 프롬프트 (업데이트)
```

### 2. 사용 예시

**기본 사용:**
```python
from src.tools.text2sql import text2sql

# 테스트 실행
result = text2sql.run("2024년에 발표된 논문 개수는?")
print(result)
```

**출력 예시:**
```markdown
**질문**: 2024년에 발표된 논문 개수는?

**생성된 SQL**:
\`\`\`sql
SELECT COUNT(*) AS paper_count FROM papers WHERE EXTRACT(YEAR FROM publish_date)=2024;
\`\`\`

**결과**:

| paper_count |
| --- |
| 42 |
```

---

## 추가 참고 사항

### 1. Few-shot 프롬프트 예시

```python
_FEW_SHOTS = [
    ("2024년에 발표된 논문 개수는?", "SELECT COUNT(*) FROM papers WHERE EXTRACT(YEAR FROM publish_date)=2024;"),
    ("카테고리별 논문 수 보여줘", "SELECT category, COUNT(*) FROM papers GROUP BY category ORDER BY count DESC;"),
    ("가장 많이 인용된 논문 Top 5는?", "SELECT title, citation_count FROM papers ORDER BY citation_count DESC LIMIT 5;"),
    ("arXiv에서 가져온 논문 개수는?", "SELECT COUNT(*) FROM papers WHERE source='arXiv';"),
    ("최근 1년간 발표된 AI 관련 논문은?", "SELECT COUNT(*) FROM papers WHERE category ILIKE '%AI%' AND publish_date >= NOW() - INTERVAL '1 year';"),
]
```

### 2. 환경 변수 설정

`.env` 파일:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=papers

TEXT2SQL_MODEL=gpt-5o-mini
OPENAI_API_KEY=your_openai_key
```

---

## 완료 일자

- **구현 완료**: 2025-11-04
- **통합 완료**: 2025-11-04
- **검증 완료**: 2025-11-04
