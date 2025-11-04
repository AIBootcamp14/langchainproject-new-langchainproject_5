# 자료조사: AI Agent 도구 (Tools)

## 문서 정보
- **작성일**: 2025-10-29
- **프로젝트**: 논문 리뷰 챗봇 (AI Agent + RAG)
- **팀명**: 연결의 민족

---

## 1. AI Agent 도구(Tool)의 개념

### 1.1 도구란?

**도구(Tool)**는 AI Agent가 특정 작업을 수행하기 위해 호출할 수 있는 **함수**입니다.

- LLM은 사용자 질문을 분석하여 어떤 도구를 사용할지 판단
- 필요한 도구의 **arguments(매개변수)**를 추출
- 도구를 실행하고 결과를 받아 최종 답변 생성

### 1.2 질문: "일반 답변, RAG 검색, 웹 검색 분기"가 도구인가?

**답변: 네, 맞습니다!**

- "일반 답변으로 바로 답변할지"
- "RAG의 지식 베이스에서 찾아 답변할지"
- "웹 검색을 할지"

이러한 **분기 결정 자체가 AI Agent의 핵심 기능**이며, 각 분기는 **도구(Tool)**로 구현됩니다.

#### 예시: 라우팅 도구

**도구 1: general_answer**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| question | str | 사용자 질문 |

**반환값:** llm.invoke(question) - LLM의 직접 답변

**용도:** 간단한 인사, 일반 상식 질문

---

**도구 2: search_papers**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| query | str | 검색 쿼리 |

**처리 흐름:**
1. vectorstore.similarity_search(query, k=3)로 유사 문서 검색
2. 문서 내용을 context로 결합
3. llm.invoke()로 컨텍스트 기반 답변 생성

---

**도구 3: web_search**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| query | str | 검색 쿼리 |

**반환값:** tavily_search.run(query) - 웹 검색 결과

**LLM이 자동으로 판단:**
- "안녕하세요" → `general_answer` 도구 사용
- "Transformer 논문 설명해줘" → `search_papers` 도구 사용
- "2025년 최신 LLM 논문은?" → `web_search` 도구 사용

---

## 2. OT 자료 요구사항 분석

### 2.1 필수 도구 (OT 자료 기준)

1. **웹 검색 기능** (필수)
2. **파일 저장 기능** (필수)
3. **3개 이상의 도구 사용** (필수)
   - 직접 구현한 도구 포함 필요
   - 특정 페르소나에 맞는 도구 (논문 리뷰 챗봇 → 논문 관련 도구)

### 2.2 선택 기능 (가산점)

1. **RAG 기능** (Vector DB, RDB 기반)
2. **성능 평가 기능**
3. **노드/엣지 추가** (LangGraph 활용)

---

## 3. 논문 리뷰 챗봇을 위한 5가지 도구 추천

### 도구 1: RAG 논문 검색 도구 (Paper Search Tool) ★ 직접 구현 필수

**기능:** 로컬 데이터베이스에 저장된 논문을 검색

**사용 시점:**
- "Transformer 논문 설명해줘"
- "BERT와 GPT의 차이점은?"
- "Attention 메커니즘이 뭐야?"

**필요 라이브러리:**
- `langchain.tools.tool`
- `langchain_postgres.vectorstores.PGVector`

**함수: search_paper_database**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| query | str | 검색할 질문 또는 키워드 |

**반환값:** str - 포맷된 논문 검색 결과

**처리 흐름:**

| 단계 | 동작 | 설명 |
|------|------|------|
| 1 | Vector DB 검색 | vectorstore.similarity_search(query, k=3) |
| 2 | 결과 수집 | 각 문서의 content, title, authors, year 추출 |
| 3 | 포맷 변환 | format_paper_results()로 결과 포맷 |

**DB 연동:**
- Vector DB (pgvector): 논문 본문 임베딩 검색
- PostgreSQL: 논문 메타데이터 (제목, 저자, 년도 등) 조회

---

### 도구 2: 웹 검색 도구 (Web Search Tool) ★ 필수

**기능:** 최신 논문 정보를 웹에서 검색

**사용 시점:**
- "2025년 최신 LLM 논문은?"
- "GPT-5가 나왔어?"
- "오늘 arXiv에 올라온 논문 찾아줘"

**필요 라이브러리:** `langchain.tools.TavilySearchResults`

**TavilySearchResults 설정:**

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| max_results | 5 | 최대 검색 결과 수 |
| search_depth | "advanced" | 검색 깊이 (basic/advanced) |
| include_answer | True | 요약 답변 포함 여부 |
| include_raw_content | True | 원본 컨텐츠 포함 여부 |

**또는 DuckDuckGo (무료):**

**필요 라이브러리:** `langchain.tools.DuckDuckGoSearchRun`

**사용:** DuckDuckGoSearchRun() 인스턴스 생성

**특화 검색:**
- arXiv API 활용: 논문 전문 검색 사이트에 특화된 검색
- Google Scholar API: 학술 논문 전용 검색

---

### 도구 3: 논문 용어집 검색 도구 (Glossary Search Tool) ★ 직접 구현

**기능:** 논문에 자주 등장하는 전문 용어 설명

**사용 시점:**
- "Attention이 뭐야?"
- "Fine-tuning이란?"
- "BLEU 스코어 설명해줘"

**필요 라이브러리:** `langchain.tools.tool`

**함수: search_glossary**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| term | str | 검색할 용어 |

**반환값:** str - 용어 정의 및 설명

**처리 흐름:**

| 단계 | 동작 | 설명 |
|------|------|------|
| 1 | PostgreSQL 검색 | glossary 테이블에서 term ILIKE 검색 |
| 2 | 결과 확인 | 용어 발견 시 정의 반환 |
| 3 | 대체 검색 | 용어 미발견 시 search_paper_database("{term} 정의") 호출 |

**SQL 쿼리:**
```sql
SELECT term, definition, category
FROM glossary
WHERE term ILIKE %term%
```

**용어집 RAG 활용:**
- 용어집 데이터를 Vector DB에도 임베딩 저장
- 사용자 질문에 용어가 포함되어 있으면 자동으로 컨텍스트에 추가

---

### 도구 4: 논문 요약 도구 (Paper Summarization Tool) ★ 직접 구현

**기능:** 특정 논문의 전체 내용을 요약

**사용 시점:**
- "Attention is All You Need 논문 요약해줘"
- "BERT 논문의 핵심 내용은?"
- "이 논문의 주요 기여도는 뭐야?"

**필요 라이브러리:** `langchain.tools.tool`

**함수: summarize_paper**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| paper_title | str | (필수) | 논문 제목 |
| difficulty | str | "easy" | 난이도 ('easy' 또는 'hard') |

**반환값:** str - 난이도별 논문 요약

**처리 흐름:**

| 단계 | 동작 | 설명 |
|------|------|------|
| 1 | 메타데이터 조회 | PostgreSQL에서 title ILIKE 검색으로 paper_id 획득 |
| 2 | 논문 내용 조회 | vectorstore.similarity_search(k=10, filter=paper_id) |
| 3 | 내용 결합 | 모든 청크를 full_content로 결합 |
| 4 | 프롬프트 구성 | difficulty에 따라 easy/hard 프롬프트 선택 |
| 5 | LLM 호출 | llm.invoke(prompt)로 요약 생성 |

**난이도별 프롬프트:**

| 난이도 | 요구사항 |
|--------|----------|
| easy | 전문 용어 풀어쓰기, 핵심 아이디어 3가지, 실생활 비유 |
| hard | 기술적 세부사항, 수식 및 알고리즘, 관련 연구 비교 |

---

### 도구 5: 파일 저장 도구 (Save to File Tool) ★ 필수

**기능:** 대화 내용, 논문 요약, 참고 자료를 파일로 저장

**사용 시점:**
- "이 요약 내용 파일로 저장해줘"
- "오늘 대화 내용 저장하고 싶어"
- "찾은 논문 리스트 파일로 만들어줘"

**필요 라이브러리:**
- `langchain.tools.tool`
- `os`, `datetime`

**함수: save_to_file**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| content | str | (필수) | 저장할 내용 |
| filename | str | None | 파일명 (없으면 자동 생성) |

**반환값:** str - 저장된 파일 경로

**처리 흐름:**

| 단계 | 동작 | 설명 |
|------|------|------|
| 1 | 파일명 생성 | filename이 None이면 "paper_review_{timestamp}.txt" 생성 |
| 2 | 디렉토리 생성 | data/outputs 폴더 생성 (없으면) |
| 3 | 파일 경로 구성 | os.path.join(output_dir, filename) |
| 4 | 파일 쓰기 | UTF-8 인코딩으로 content 저장 |
| 5 | 경로 반환 | 저장된 파일 경로 메시지 반환 |

**추가 기능:**
- PDF 형식으로 저장 (reportlab 라이브러리 사용)
- Markdown 형식으로 저장
- 논문 인용 형식 포함 (APA, MLA 등)

---

## 4. 추가 도구 (선택 사항)

### 도구 6: Text-to-SQL 도구 (DB Query Tool)

**기능:** 자연어를 SQL 쿼리로 변환하여 논문 통계 조회

**사용 시점:**
- "2024년에 발표된 논문 개수는?"
- "가장 많이 인용된 논문 Top 5는?"
- "저자별 논문 수 알려줘"

**필요 라이브러리:** `langchain.tools.tool`

**함수: query_paper_statistics**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| question | str | 자연어 질문 |

**반환값:** str - 포맷된 쿼리 결과

**처리 흐름:**

| 단계 | 동작 | 설명 |
|------|------|------|
| 1 | SQL 프롬프트 구성 | 테이블 스키마와 질문을 포함한 프롬프트 생성 |
| 2 | LLM 호출 | llm.invoke()로 SQL 쿼리 생성 |
| 3 | 쿼리 실행 | db.execute(sql_query).fetchall() |
| 4 | 결과 포맷 | format_query_results()로 결과 포맷 |

**테이블 스키마:**
```
papers (paper_id, title, authors, publish_date, citation_count, category)
```

---

### 도구 7: 논문 비교 도구 (Paper Comparison Tool)

**기능:** 여러 논문의 차이점 비교

**사용 시점:**
- "BERT와 GPT 비교해줘"
- "Transformer와 RNN의 차이는?"

---

### 도구 8: 인용 추출 도구 (Citation Extraction Tool)

**기능:** 논문의 주요 인용문 추출

---

## 5. 도구 라우팅: LLM이 자동으로 도구 선택

### 5.1 라우팅 메커니즘

LLM은 사용자 질문을 분석하여 적절한 도구를 선택합니다.

**예시:**

| 사용자 질문 | LLM이 선택하는 도구 | 이유 |
|-------------|---------------------|------|
| "안녕하세요" | 일반 답변 (도구 사용 안 함) | 간단한 인사 |
| "Transformer 논문 설명해줘" | `search_paper_database` | 로컬 DB에 있는 논문 검색 |
| "2025년 최신 LLM 논문은?" | `web_search_tool` | 최신 정보는 웹 검색 필요 |
| "Attention이 뭐야?" | `search_glossary` | 용어 정의 질문 |
| "BERT 논문 요약해줘" | `summarize_paper` | 특정 논문 요약 요청 |
| "이 내용 저장해줘" | `save_to_file` | 파일 저장 요청 |

### 5.2 LangGraph를 활용한 라우팅 구현

**필요 라이브러리:**
- `langgraph.graph.StateGraph`, `langgraph.graph.END`
- `typing.TypedDict`, `typing.Annotated`, `typing.Sequence`
- `operator`

**AgentState 정의:**

| 필드 | 타입 | 설명 |
|------|------|------|
| messages | Annotated[Sequence[BaseMessage], operator.add] | 메시지 시퀀스 |
| next_action | str | 다음 실행할 도구명 |

**router_node 함수:**
- 마지막 메시지 추출: state["messages"][-1]
- 라우팅 프롬프트에 도구 목록 포함
- LLM이 적절한 도구 선택
- {"next_action": tool_choice} 반환

**도구 목록:**
- search_paper_database: 로컬 논문 DB 검색
- web_search: 웹 최신 논문 검색
- search_glossary: 용어 정의 검색
- summarize_paper: 논문 요약
- save_to_file: 파일 저장
- general_answer: 직접 답변

**conditional_edge 함수:**
- state["next_action"] 값을 반환하여 다음 노드 결정

**그래프 구성:**

| 단계 | 동작 |
|------|------|
| 1 | StateGraph(AgentState) 생성 |
| 2 | 노드 추가 (router, search_paper, web_search, glossary, summarize, save_file, general) |
| 3 | 진입점 설정: router |
| 4 | 조건부 엣지 추가 (router → 각 도구 노드) |
| 5 | 모든 도구 노드 → END |
| 6 | workflow.compile()로 agent 생성 |

---

## 6. 난이도별 답변 모드 구현

### 6.1 Easy 모드 (초심자)

**특징:**
- 전문 용어 최소화
- 비유와 예시 많이 사용
- 단계별 설명
- 수식 최소화

**템플릿: EASY_MODE_PROMPT**

| 구성 요소 | 내용 |
|----------|------|
| 역할 | AI/ML 초심자를 위한 논문 리뷰 어시스턴트 |
| 변수 | {question}: 사용자 질문 |

**답변 규칙:**
1. 전문 용어가 나오면 반드시 쉬운 말로 풀어서 설명
2. 실생활 비유 사용 (예: "Attention은 사람이 책을 읽을 때 중요한 부분에 집중하는 것과 같습니다")
3. 수식은 최소화하고, 나오면 직관적으로 설명
4. 핵심 아이디어 3가지 이내로 요약

### 6.2 Hard 모드 (전문가)

**특징:**
- 기술적 세부사항 포함
- 수식 및 알고리즘 설명
- 관련 논문 비교
- 구현 세부사항

**템플릿: HARD_MODE_PROMPT**

| 구성 요소 | 내용 |
|----------|------|
| 역할 | AI/ML 전문가를 위한 논문 리뷰 어시스턴트 |
| 변수 | {question}: 사용자 질문 |

**답변 규칙:**
1. 기술적 세부사항 및 수식 포함
2. 알고리즘의 시간/공간 복잡도 분석
3. 관련 논문과의 비교 (장단점)
4. 구현 시 고려사항
5. 최신 연구 동향과의 연결

### 6.3 UI에서 모드 선택

**필요 라이브러리:** `streamlit`

**UI 구성:**

| 컴포넌트 | 함수 | 설정 |
|---------|------|------|
| 난이도 선택 | st.selectbox | 옵션: ["Easy 모드 (초심자용)", "Hard 모드 (전문가용)"] |

**처리 로직:**
1. difficulty_mode에서 "Easy" 포함 여부 확인
2. difficulty 변수 설정: "Easy" 포함 시 "easy", 아니면 "hard"
3. agent.run(user_query, difficulty=difficulty)로 Agent에 전달

---

## 7. 최종 도구 목록 요약

### 필수 도구 (5개)

| 번호 | 도구 이름 | 필수 여부 (OT 기준) | 직접 구현 여부 | 설명 |
|------|-----------|---------------------|----------------|------|
| 1 | RAG 논문 검색 도구 | ✅ (선택 기능이지만 프로젝트 핵심) | ✅ 직접 구현 | 로컬 DB에서 논문 검색 |
| 2 | 웹 검색 도구 | ✅ 필수 | ❌ Langchain 제공 | 최신 논문 웹 검색 |
| 3 | 논문 용어집 검색 도구 | 추가 제안 | ✅ 직접 구현 | 전문 용어 설명 |
| 4 | 논문 요약 도구 | 추가 제안 | ✅ 직접 구현 | 난이도별 논문 요약 |
| 5 | 파일 저장 도구 | ✅ 필수 | ✅ 직접 구현 | 대화/요약 내용 저장 |

### 선택 도구 (추가 가능)

| 번호 | 도구 이름 | 설명 |
|------|-----------|------|
| 6 | Text-to-SQL 도구 | 논문 통계 정보 조회 (가산점) |
| 7 | 논문 비교 도구 | 여러 논문 비교 분석 |
| 8 | 인용 추출 도구 | 논문 주요 인용문 추출 |

---

## 8. 참고 자료

- Langchain Tools 문서: https://docs.langchain.com/oss/python/langchain/tools#tools
- Langchain Agent 문서: https://docs.langchain.com/oss/python/langchain/agents
- LangGraph 문서: https://langchain-ai.github.io/langgraph/
- Tavily Search API: https://tavily.com/
- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
