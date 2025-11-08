# RAG 논문 검색 도구 아키텍처

## 📋 문서 정보
- **작성일**: 2025-11-07
- **작성자**: 최현화[팀장]
- **프로젝트명**: 논문 리뷰 챗봇 (AI Agent + RAG)
- **팀명**: 연결의 민족
- **문서 버전**: 1.0

---

## 📑 목차
1. [도구 개요](#도구-개요)
2. [도구 실행 조건](#도구-실행-조건)
3. [도구 자동 전환 및 Fallback](#도구-자동-전환-및-fallback)
4. [단순 흐름 아키텍처](#단순-흐름-아키텍처)
5. [상세 기능 동작 흐름도](#상세-기능-동작-흐름도)
6. [동작 설명](#동작-설명)
7. [사용 예시](#사용-예시)
8. [핵심 포인트](#핵심-포인트)
9. [참고 정보](#참고-정보)

---

## 📌 도구 개요

### 목적과 역할

RAG 논문 검색 도구는 PostgreSQL + pgvector 기반의 벡터 데이터베이스에서 사용자 질문과 관련된 논문을 검색하는 핵심 도구입니다.

**핵심 역할:**
- 사용자 질문을 벡터로 변환하여 유사한 논문 청크 검색
- PostgreSQL Full-Text Search와 pgvector 검색을 결합한 하이브리드 검색
- 검색 결과를 난이도별 프롬프트로 LLM에 전달하여 자연스러운 답변 생성

**사용 데이터:**
- **PostgreSQL 테이블**: `papers` (논문 메타데이터: 제목, 저자, 출판일, URL, 카테고리, 인용수, 초록 등)
- **pgvector 컬렉션**: `paper_chunks` (논문 본문 청크의 1536차원 임베딩)
- **임베딩 모델**: OpenAI `text-embedding-3-small`

**검색 메커니즘:**
- 벡터 검색 (70% 가중치): pgvector similarity/MMR 검색 + MultiQueryRetriever로 쿼리 확장
- 키워드 검색 (30% 가중치): PostgreSQL Full-Text Search (title, abstract 대상)
- 하이브리드 점수 병합으로 최종 Top-K 논문 선정

---

## 📋 도구 실행 조건

### 언제 실행되는가?

**1. 사용자가 논문 검색을 명시적으로 요청할 때**
- "RAG 관련 논문 찾아줘"
- "Transformer 논문 검색해줘"
- "BERT 모델 논문 있어?"

**2. 시간 관련 키워드가 없을 때 (중요!)**
- ✅ 실행: "Transformer 논문 찾아줘" (시간 키워드 없음)
- ❌ 건너뜀: "최신 Transformer 논문 찾아줘" (시간 키워드 있음 → Web 논문 검색 도구로 우선 실행)

**3. 패턴 매칭 우선순위**

`configs/multi_request_patterns.yaml`에서 정의된 패턴:

```yaml
- keywords: [논문, 찾]
  exclude_keywords: [저장, 요약, 인용, 많은, 상위, 통계, 몇]
  tools: [search_paper]
  priority: 140
```

**실행 조건 검증:**
1. `keywords`에 모든 키워드 포함 (`논문`, `찾`) → AND 조건
2. `exclude_keywords`에 해당 키워드 없음 → 제외 조건
3. 우선순위 140으로 다른 패턴보다 우선 매칭

---

## 🔄 도구 자동 전환 및 Fallback

### Fallback Chain 흐름

```
사용자 논문 검색 요청 (시간 키워드 없음)
  ↓
[1] RAG 논문 검색 도구 실행
  ├─ 성공 → 검색 결과 반환 → END
  └─ 실패 (데이터베이스에서 찾지 못함)
      ↓
[2] Web 논문 검색 도구로 자동 전환
  ├─ 성공 → 검색 결과 반환 → END
  └─ 실패 (웹 검색 실패)
      ↓
[3] 일반 답변 도구로 최종 전환
  └─ LLM이 직접 논문 지식 기반 답변 생성 → END
```

### Fallback 트리거 조건

**실패 감지 패턴** (`src/agent/failure_detector.py`):

```python
FAILURE_PATTERNS = [
    "관련 논문을 찾을 수 없습니다",      # ← RAG 검색 실패 메시지
    "데이터베이스에서 찾지 못했습니다",   # ← search_paper_node 실패 메시지
    "검색 결과가 없습니다",
    "검색된 논문이 없습니다",
]
```

**유사도 임계값 검증** (`src/tools/search_paper.py:89-101`):

```python
SIMILARITY_THRESHOLD = 0.5  # pgvector cosine distance (낮을수록 유사)

# 모든 결과의 유사도가 낮으면 (score > 0.5) 실패 처리
if not has_relevant_result:
    return "관련 논문을 찾을 수 없습니다."
```

### Fallback Chain 설정

**`configs/model_config.yaml` 설정:**

```yaml
fallback_chain:
  enabled: true
  max_retries: 3
  priorities:
    paper_search:
      - search_paper   # 1순위: RAG DB 검색
      - web_search     # 2순위: 웹 검색
      - general        # 3순위: 일반 답변
```

---

## 🎨 단순 흐름 아키텍처

```mermaid
graph TB
    subgraph MainFlow["📋 RAG 논문 검색 도구 전체 흐름"]
        direction TB

        subgraph Input["🔸 입력 & 라우팅"]
            direction LR
            Start([▶️ 사용자 질문]) --> KeywordCheck{시간 키워드<br/>검출?}
            KeywordCheck -->|최신/최근 있음| SkipRAG[❌ RAG 건너뜀<br/>→ Web 검색]
            KeywordCheck -->|시간 키워드 없음| PatternMatch[패턴 매칭<br/>논문+찾]
            PatternMatch --> ToolSelect[🔧 search_paper<br/>도구 선택]
        end

        subgraph Search["🔹 하이브리드 검색"]
            direction LR
            VectorSearch[벡터 검색<br/>paper_chunks] --> Merge[점수 병합<br/>가중치 적용]
            KeywordSearch[키워드 검색<br/>papers 테이블] --> Merge
            Merge --> TopK[Top-5 논문<br/>선정]
        end

        subgraph Generation["🔺 답변 생성"]
            direction LR
            PromptLoad[난이도별<br/>프롬프트 로드] --> LLMCall[LLM 호출<br/>OpenAI/Solar]
            LLMCall --> FinalAnswer[✅ 최종 답변]
        end

        subgraph Fallback["🔶 Fallback 처리"]
            direction LR
            CheckResult{검색<br/>성공?}
            CheckResult -->|실패| WebSearch[Web 논문 검색]
            WebSearch --> CheckWeb{성공?}
            CheckWeb -->|실패| GeneralAnswer[일반 답변<br/>도구]
            CheckWeb -->|성공| End2([✅ 완료])
            GeneralAnswer --> End3([✅ 완료])
        end

        %% 단계 간 연결
        Input --> Search
        Search --> CheckResult
        CheckResult -->|성공| Generation
        Generation --> End1([✅ 완료])
        CheckResult -->|실패 감지| Fallback
    end

    %% 메인 워크플로우 배경
    style MainFlow fill:#fffde7,stroke:#f9a825,stroke-width:4px,color:#000

    %% Subgraph 스타일
    style Input fill:#e0f7fa,stroke:#006064,stroke-width:3px,color:#000
    style Search fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style Generation fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000
    style Fallback fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000

    %% 노드 스타일 (입력 - 청록 계열)
    style Start fill:#4db6ac,stroke:#00695c,stroke-width:3px,color:#000
    style KeywordCheck fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style SkipRAG fill:#ef9a9a,stroke:#c62828,stroke-width:2px,color:#000
    style PatternMatch fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style ToolSelect fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000

    %% 노드 스타일 (검색 - 보라 계열)
    style VectorSearch fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style KeywordSearch fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style Merge fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px,color:#000
    style TopK fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px,color:#000

    %% 노드 스타일 (생성 - 녹색 계열)
    style PromptLoad fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style LLMCall fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style FinalAnswer fill:#66bb6a,stroke:#1b5e20,stroke-width:2px,color:#000

    %% 노드 스타일 (Fallback - 주황 계열)
    style CheckResult fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style WebSearch fill:#ffb74d,stroke:#e65100,stroke-width:2px,color:#000
    style CheckWeb fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style GeneralAnswer fill:#ffb74d,stroke:#e65100,stroke-width:2px,color:#000

    %% 종료 노드
    style End1 fill:#66bb6a,stroke:#2e7d32,stroke-width:3px,color:#000
    style End2 fill:#66bb6a,stroke:#2e7d32,stroke-width:3px,color:#000
    style End3 fill:#66bb6a,stroke:#2e7d32,stroke-width:3px,color:#000
```

---

## 🔍 상세 기능 동작 흐름도

```mermaid
graph TB
    subgraph MainFlow["📋 RAG 논문 검색 도구 상세 실행 흐름"]
        direction TB

        subgraph Init["🔸 초기화 & 라우팅"]
            direction LR
            A[main.py] --> B[ui/app.py<br/>initialize_agent]
            B --> C[src/agent/graph.py<br/>create_agent_graph]
            C --> D[src/agent/nodes.py<br/>router_node]
            D --> E{패턴 매칭}
            E -->|매칭 성공| F[multi_request_patterns.yaml<br/>priority: 140]
            E -->|매칭 실패| G[LLM 라우팅<br/>routing_prompts.json]
            F --> H[tool_choice =<br/>'search_paper']
            G --> H
        end

        subgraph ToolExec["🔹 도구 실행"]
            direction LR
            I[src/agent/nodes.py<br/>search_paper_node] --> J[refined_query 또는<br/>question 추출]
            J --> K[src/tools/search_paper.py<br/>search_paper_database]
            K --> L[src/rag/retriever.py<br/>RAGRetriever 초기화]
            L --> M[src/database/vector_store.py<br/>get_pgvector_store]
        end

        subgraph VectorSearch["🔺 벡터 검색"]
            direction LR
            N[MultiQueryRetriever<br/>쿼리 확장] --> O[src/llm/client.py<br/>LLMClient.invoke]
            O --> P[3-5개 쿼리 생성]
            P --> Q[pgvector 컬렉션<br/>paper_chunks 검색]
            Q --> R[유사도 점수<br/>계산 및 정규화]
        end

        subgraph KeywordSearch["🔶 키워드 검색"]
            direction LR
            S[_keyword_search<br/>함수 호출] --> T[영어 키워드 추출<br/>정규식 처리]
            T --> U[PostgreSQL<br/>Full-Text Search]
            U --> V[papers 테이블<br/>title/abstract ILIKE]
            V --> W[키워드 점수<br/>계산]
        end

        subgraph Merge["🔷 하이브리드 병합"]
            direction LR
            X[벡터 점수<br/>× 0.7] --> Z[최종 점수<br/>병합]
            Y[키워드 점수<br/>× 0.3] --> Z
            Z --> AA[점수 기준<br/>정렬]
            AA --> AB[Top-5 논문<br/>선정]
        end

        subgraph MetaFetch["💾 메타데이터 조회"]
            direction LR
            AC[_fetch_paper_meta<br/>함수 호출] --> AD[PostgreSQL<br/>papers 테이블]
            AD --> AE[SELECT paper_id,<br/>title, authors,<br/>publish_date,<br/>url, category,<br/>citation_count]
            AE --> AF[메타데이터<br/>병합]
        end

        subgraph AnswerGen["✨ 답변 생성"]
            direction LR
            AG[난이도 확인<br/>easy/hard] --> AH[prompts/tool_prompts.json<br/>프롬프트 로드]
            AH --> AI[2개 수준 답변 생성<br/>elementary+beginner<br/>또는<br/>intermediate+advanced]
            AI --> AJ[src/llm/client.py<br/>LLMClient.invoke]
            AJ --> AK[최종 답변<br/>final_answer]
        end

        subgraph FailureCheck["⚠️ 실패 감지"]
            direction LR
            AL{유사도 임계값<br/>검증} -->|score > 0.5| AM[실패 메시지<br/>'관련 논문을<br/>찾을 수 없습니다']
            AL -->|score ≤ 0.5| AN[성공]
            AM --> AO[src/agent/failure_detector.py<br/>is_failed 검증]
            AO --> AP[tool_status =<br/>'failed']
            AP --> AQ[src/agent/nodes.py<br/>fallback_router_node]
        end

        %% 단계 간 연결
        Init --> ToolExec
        ToolExec --> VectorSearch
        ToolExec --> KeywordSearch
        VectorSearch --> Merge
        KeywordSearch --> Merge
        Merge --> MetaFetch
        MetaFetch --> FailureCheck
        FailureCheck --> AnswerGen
    end

    %% 메인 워크플로우 배경
    style MainFlow fill:#fffde7,stroke:#f9a825,stroke-width:4px,color:#000

    %% Subgraph 스타일
    style Init fill:#e0f7fa,stroke:#006064,stroke-width:3px,color:#000
    style ToolExec fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    style VectorSearch fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style KeywordSearch fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000
    style Merge fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000
    style MetaFetch fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000
    style AnswerGen fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000
    style FailureCheck fill:#fce4ec,stroke:#880e4f,stroke-width:3px,color:#000

    %% 노드 스타일 (초기화 - 청록 계열)
    style A fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style B fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style C fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style D fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style E fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style F fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style G fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style H fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000

    %% 노드 스타일 (도구 실행 - 파랑 계열)
    style I fill:#90caf9,stroke:#1976d2,stroke-width:2px,color:#000
    style J fill:#81d4fa,stroke:#0288d1,stroke-width:2px,color:#000
    style K fill:#64b5f6,stroke:#1976d2,stroke-width:2px,color:#000
    style L fill:#90caf9,stroke:#1976d2,stroke-width:2px,color:#000
    style M fill:#81d4fa,stroke:#0288d1,stroke-width:2px,color:#000

    %% 노드 스타일 (벡터 검색 - 보라 계열)
    style N fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style O fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px,color:#000
    style P fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style Q fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px,color:#000
    style R fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000

    %% 노드 스타일 (키워드 검색 - 주황 계열)
    style S fill:#ffcc80,stroke:#f57c00,stroke-width:2px,color:#000
    style T fill:#ffb74d,stroke:#f57c00,stroke-width:2px,color:#000
    style U fill:#ffa726,stroke:#ef6c00,stroke-width:2px,color:#000
    style V fill:#ffcc80,stroke:#f57c00,stroke-width:2px,color:#000
    style W fill:#ffb74d,stroke:#f57c00,stroke-width:2px,color:#000

    %% 노드 스타일 (병합 - 녹색 계열)
    style X fill:#a5d6a7,stroke:#388e3c,stroke-width:2px,color:#000
    style Y fill:#a5d6a7,stroke:#388e3c,stroke-width:2px,color:#000
    style Z fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style AA fill:#66bb6a,stroke:#1b5e20,stroke-width:2px,color:#000
    style AB fill:#66bb6a,stroke:#1b5e20,stroke-width:2px,color:#000

    %% 노드 스타일 (메타데이터 - 파랑 계열)
    style AC fill:#90caf9,stroke:#0d47a1,stroke-width:2px,color:#000
    style AD fill:#64b5f6,stroke:#1565c0,stroke-width:2px,color:#000
    style AE fill:#42a5f5,stroke:#0d47a1,stroke-width:2px,color:#000
    style AF fill:#2196f3,stroke:#01579b,stroke-width:2px,color:#000

    %% 노드 스타일 (답변 생성 - 빨강 계열)
    style AG fill:#ef9a9a,stroke:#c62828,stroke-width:2px,color:#000
    style AH fill:#e57373,stroke:#c62828,stroke-width:2px,color:#000
    style AI fill:#ef5350,stroke:#b71c1c,stroke-width:2px,color:#000
    style AJ fill:#e57373,stroke:#c62828,stroke-width:2px,color:#000
    style AK fill:#ef9a9a,stroke:#c62828,stroke-width:2px,color:#000

    %% 노드 스타일 (실패 감지 - 핑크 계열)
    style AL fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style AM fill:#f48fb1,stroke:#880e4f,stroke-width:2px,color:#000
    style AN fill:#a5d6a7,stroke:#388e3c,stroke-width:2px,color:#000
    style AO fill:#f48fb1,stroke:#880e4f,stroke-width:2px,color:#000
    style AP fill:#f48fb1,stroke:#880e4f,stroke-width:2px,color:#000
    style AQ fill:#f48fb1,stroke:#880e4f,stroke-width:2px,color:#000

    %% 연결선 스타일 (초기화)
    linkStyle 0,1,2,3,4,5,6,7 stroke:#006064,stroke-width:2px

    %% 연결선 스타일 (도구 실행)
    linkStyle 8,9,10,11 stroke:#1976d2,stroke-width:2px

    %% 연결선 스타일 (벡터 검색)
    linkStyle 12,13,14,15 stroke:#7b1fa2,stroke-width:2px

    %% 연결선 스타일 (키워드 검색)
    linkStyle 16,17,18,19 stroke:#e65100,stroke-width:2px

    %% 연결선 스타일 (병합)
    linkStyle 20,21,22,23 stroke:#2e7d32,stroke-width:2px

    %% 연결선 스타일 (메타데이터)
    linkStyle 24,25,26 stroke:#1565c0,stroke-width:2px

    %% 연결선 스타일 (답변 생성)
    linkStyle 27,28,29,30 stroke:#c62828,stroke-width:2px

    %% 연결선 스타일 (실패 감지)
    linkStyle 31,32,33,34,35 stroke:#880e4f,stroke-width:2px

    %% 단계 간 연결 (회색)
    linkStyle 36,37,38,39,40,41,42 stroke:#616161,stroke-width:3px
```

---

### 전체 흐름 요약 표

| 단계 | 파일명 | 메서드명 | 동작 설명 | 입력 | 출력 | DB 사용 |
|------|--------|----------|-----------|------|------|---------|
| 1 | `main.py` | - | Streamlit 서버 시작 | - | - | 없음 |
| 2 | `ui/app.py` | `initialize_agent()` | Agent 그래프 초기화 | - | agent_executor | 없음 |
| 3 | `src/agent/graph.py` | `create_agent_graph()` | LangGraph 상태 머신 생성 | exp_manager | CompiledGraph | 없음 |
| 4 | `src/agent/nodes.py` | `router_node()` | 질문 분석 및 도구 선택 | state (question) | state (tool_choice) | 없음 |
| 5 | `configs/multi_request_patterns.yaml` | - | 패턴 매칭 (키워드 기반) | question | tool_pipeline | 없음 |
| 6 | `src/agent/nodes.py` | `search_paper_node()` | 도구 노드 실행 | state (question, difficulty) | state (final_answer) | 없음 |
| 7 | `src/tools/search_paper.py` | `search_paper_database()` | @tool 함수 호출 | query, top_k, ... | Markdown 문자열 | papers, paper_chunks |
| 8 | `src/rag/retriever.py` | `RAGRetriever.__init__()` | Retriever 초기화 | collection_name | RAGRetriever | pgvector 연결 |
| 9 | `src/database/vector_store.py` | `get_pgvector_store()` | PGVector 연결 | collection_name | PGVector 객체 | paper_chunks |
| 10 | `src/rag/retriever.py` | `multi_query_search()` | LLM 쿼리 확장 + 검색 | query, k | List[Document] | paper_chunks |
| 11 | `src/llm/client.py` | `LLMClient.invoke()` | LLM 쿼리 확장 | query | 3-5개 쿼리 | 없음 |
| 12 | `src/tools/search_paper.py` | `_keyword_search()` | PostgreSQL Full-Text Search | query, top_k | List[Dict] | papers (title, abstract) |
| 13 | `src/tools/search_paper.py` | `search_paper_database()` (병합) | 하이브리드 점수 병합 | vector_results, keyword_results | List[Dict] | 없음 |
| 14 | `src/tools/search_paper.py` | `_fetch_paper_meta()` | 메타데이터 조회 | paper_ids | Dict[int, Dict] | papers (all columns) |
| 15 | `src/tools/search_paper.py` | `_format_markdown()` | 결과 포맷팅 + 임계값 검증 | results | Markdown 문자열 | 없음 |
| 16 | `src/agent/nodes.py` | `search_paper_node()` (답변 생성) | 난이도별 프롬프트 로드 | difficulty | system_prompt | 없음 |
| 17 | `prompts/tool_prompts.json` | - | JSON 프롬프트 로드 | tool, level | prompt 문자열 | 없음 |
| 18 | `src/llm/client.py` | `LLMClient.invoke()` | LLM 답변 생성 | messages | response.content | 없음 |
| 19 | `src/agent/failure_detector.py` | `is_failed()` | 실패 패턴 감지 | final_answer | (is_failed, reason) | 없음 |
| 20 | `src/agent/nodes.py` | `fallback_router_node()` | Fallback 다음 도구 선택 | state (failed_tools) | state (tool_choice) | 없음 |

---

## 📖 동작 설명

### 단계별 상세 설명

#### 1단계: 초기화 & 라우팅

**파일**: `main.py` → `ui/app.py` → `src/agent/graph.py` → `src/agent/nodes.py`

**동작 설명:**
1. 사용자가 Streamlit UI에 질문 입력
2. `ui/app.py`의 `initialize_agent()` 함수가 Agent 그래프 초기화
3. `src/agent/graph.py`의 `create_agent_graph()`가 LangGraph 상태 머신 생성
4. `src/agent/nodes.py`의 `router_node()` 함수가 질문 분석하여 도구 선택

**입력**: 사용자 질문 (예: "RAG 관련 논문 찾아줘")
**출력**: `tool_choice = "search_paper"`

**DB 사용**: 없음

**왜 이렇게 동작하는가?**
- LangGraph는 상태 기반 워크플로우 엔진으로, 각 단계를 노드로 정의하고 조건부 엣지로 연결합니다.
- Router 노드가 먼저 실행되어 사용자 질문을 분석하고 적절한 도구를 선택하는 것이 효율적입니다.

---

#### 2단계: 패턴 매칭

**파일**: `configs/multi_request_patterns.yaml`
**메서드**: `src/agent/nodes.py:84-200` (router_node 함수 내)

**동작 설명:**
1. YAML 파일에서 22개 패턴을 우선순위 순서대로 로드
2. 사용자 질문에서 키워드 추출
3. AND 로직: `keywords`에 모든 키워드 포함 확인
4. OR 로직: `any_of_keywords`에 하나라도 포함 확인
5. 제외 로직: `exclude_keywords`에 해당 키워드 없음 확인
6. 매칭 성공 시 `tool_pipeline` 설정

**예시:**
```python
# 질문: "RAG 관련 논문 찾아줘"
keywords_match = ("논문" in question) and ("찾" in question)  # True
exclude_match = any(kw in question for kw in ["저장", "요약", "인용", ...])  # False

if keywords_match and not exclude_match:
    state["tool_choice"] = "search_paper"
    state["tool_pipeline"] = ["search_paper"]
```

**입력**: 사용자 질문
**출력**: `tool_choice`, `tool_pipeline`

**DB 사용**: 없음

**실패 시 처리:**
- 패턴 매칭 실패 시 LLM 라우팅으로 전환 (`routing_prompts.json` 사용)

---

#### 3단계: 도구 노드 실행

**파일**: `src/agent/nodes.py`
**메서드**: `search_paper_node(state, exp_manager)` (라인 420-572)

**동작 설명:**
1. 상태에서 질문 추출: `refined_query` 우선, 없으면 `question` 사용 (Multi-turn 지원)
2. 난이도 추출: `difficulty` ("easy" 또는 "hard")
3. 도구별 Logger 생성 (ExperimentManager)
4. `search_paper_database` @tool 함수 호출

**입력**: AgentState (question, refined_query, difficulty)
**출력**: AgentState (final_answer, final_answers, tool_result)

**DB 사용**: 아직 없음 (다음 단계에서 DB 접근)

**왜 refined_query를 우선하는가?**
- Multi-turn 대화에서 대명사("관련", "그거", "이거")를 구체적인 명사로 변환한 쿼리가 `refined_query`에 저장됩니다.
- 예: "Vision Transformer가 뭐야?" → "관련 논문 찾아줘" (refined_query: "Vision Transformer 관련 논문 찾아줘")

---

#### 4단계: RAGRetriever 초기화

**파일**: `src/rag/retriever.py`
**메서드**: `RAGRetriever.__init__()` (라인 90-120)

**동작 설명:**
1. `src/database/vector_store.py`의 `get_pgvector_store()` 호출
2. pgvector 컬렉션 `paper_chunks` 연결
3. LangChain VectorStore 객체 생성
4. MultiQueryRetriever 초기화 (LLM 쿼리 확장용)

**입력**: collection_name="paper_chunks", search_type="similarity", k=5
**출력**: RAGRetriever 인스턴스

**DB 사용**:
- PostgreSQL 연결 문자열 생성: `postgresql://user:pass@host:port/papers`
- pgvector 확장 활성화 확인

---

#### 5단계: 벡터 검색 (MultiQuery)

**파일**: `src/rag/retriever.py`
**메서드**: `multi_query_search(query, k)` (라인 209-221)

**동작 설명:**
1. MultiQueryRetriever가 LLM을 사용하여 원본 쿼리를 3-5개로 확장
   - 예: "RAG 관련 논문" → ["RAG 논문", "Retrieval Augmented Generation 연구", "RAG 시스템 논문"]
2. 각 쿼리로 pgvector에서 similarity 검색 수행
3. 중복 제거 (`_dedup_docs` 함수)
4. Top-K 논문 반환

**입력**: query="RAG 관련 논문 찾아줘", k=5
**출력**: List[Document] (최대 5개)

**DB 사용**:
- **pgvector 컬렉션**: `paper_chunks`
- **검색 방식**: Cosine similarity (L2 distance)
- **메타데이터**: paper_id, title, authors, section, publish_date

**점수 정규화:**
```python
# distance → 유사도 점수 변환 (낮을수록 유사)
normalized_score = 1.0 / (1.0 + float(distance))
```

---

#### 6단계: 키워드 검색 (PostgreSQL Full-Text)

**파일**: `src/tools/search_paper.py`
**메서드**: `_keyword_search(query, top_k)` (라인 146-238)

**동작 설명:**
1. 사용자 질문에서 영어 키워드 추출 (정규식 사용)
   - 괄호 안 영어 우선: `"RAG (Retrieval-Augmented Generation)"` → `"Retrieval-Augmented Generation"`
   - 3글자 이상 영어 단어 추출: `["RAG", "Retrieval", "Augmented", "Generation"]`
2. 가장 긴 키워드 사용 (더 구체적)
3. PostgreSQL `ILIKE` 쿼리로 title, abstract 검색

**SQL 쿼리:**
```sql
SELECT
    paper_id, title, abstract, authors, publish_date, category, citation_count, url,
    (
        CASE WHEN title ILIKE %query% THEN 2.0 ELSE 0.0 END +
        CASE WHEN abstract ILIKE %query% THEN 1.0 ELSE 0.0 END
    ) AS keyword_score
FROM papers
WHERE title ILIKE %query% OR abstract ILIKE %query%
ORDER BY keyword_score DESC, citation_count DESC
LIMIT 5
```

**입력**: query="RAG 관련 논문 찾아줘", top_k=5
**출력**: List[Dict] (paper_id, title, abstract, keyword_score 등)

**DB 사용**:
- **테이블**: `papers`
- **컬럼**: `title`, `abstract`, `authors`, `publish_date`, `category`, `citation_count`, `url`
- **인덱스**: GIN Full-Text Search 인덱스 사용

**점수 계산:**
- title 매칭: 2.0점
- abstract 매칭: 1.0점
- 최대 3.0점

---

#### 7단계: 하이브리드 점수 병합

**파일**: `src/tools/search_paper.py`
**메서드**: `search_paper_database()` (라인 339-412)

**동작 설명:**
1. 벡터 검색 점수와 키워드 검색 점수를 가중치로 결합
2. `configs/model_config.yaml`에서 가중치 로드
   - 벡터 검색: 70%
   - 키워드 검색: 30%
3. 각 논문(paper_id)별 최종 점수 계산
4. 점수 기준 정렬 (높은 순)
5. Top-K 논문 선정

**가중치 적용 공식:**
```python
final_score = (vector_normalized_score × 0.7) + (keyword_normalized_score × 0.3)
```

**입력**: vector_results, keyword_results, weights
**출력**: List[Dict] (paper_id, title, authors, ..., score)

**DB 사용**: 없음 (이미 조회한 데이터 병합)

**왜 하이브리드 검색을 사용하는가?**
- 벡터 검색: 의미적 유사도 (semantic similarity) → 동의어, 유사 표현 감지
- 키워드 검색: 정확한 용어 매칭 → 특정 논문 제목이나 저자명 검색
- 두 방식을 결합하면 검색 품질이 향상됩니다.

---

#### 8단계: 메타데이터 조회

**파일**: `src/tools/search_paper.py`
**메서드**: `_fetch_paper_meta(paper_ids)` (라인 42-72)

**동작 설명:**
1. 벡터 검색 결과에서 `paper_id` 목록 추출
2. PostgreSQL `papers` 테이블에서 메타데이터 일괄 조회
3. `paper_id`를 키로 하는 딕셔너리 반환

**SQL 쿼리:**
```sql
SELECT paper_id, title, authors, publish_date, url, category, citation_count
FROM papers
WHERE paper_id = ANY(ARRAY[1, 5, 12, 23, 45])
```

**입력**: paper_ids=[1, 5, 12, 23, 45]
**출력**: Dict[int, Dict] (paper_id → {title, authors, ...})

**DB 사용**:
- **테이블**: `papers`
- **컬럼**: `paper_id`, `title`, `authors`, `publish_date`, `url`, `category`, `citation_count`

**왜 별도로 조회하는가?**
- pgvector 컬렉션에는 임베딩과 기본 메타데이터만 저장됩니다.
- 상세한 메타데이터(인용수, 카테고리 등)는 PostgreSQL 테이블에 있어 별도 조회가 필요합니다.

---

#### 9단계: 유사도 임계값 검증

**파일**: `src/tools/search_paper.py`
**메서드**: `_format_markdown(results)` (라인 75-122)

**동작 설명:**
1. 검색 결과의 유사도 점수 확인
2. 임계값: `SIMILARITY_THRESHOLD = 0.5` (cosine distance 기준)
3. 모든 결과의 점수가 0.5 초과 (유사도 낮음)이면 실패 처리
4. 실패 시 `"관련 논문을 찾을 수 없습니다."` 반환

**검증 로직:**
```python
has_relevant_result = False
for r in results:
    score = r.get("score")
    if score is not None and score <= 0.5:  # 유사도 높음
        has_relevant_result = True
        break

if not has_relevant_result:
    return "관련 논문을 찾을 수 없습니다."
```

**입력**: results (검색 결과 리스트)
**출력**: 성공 시 Markdown 문자열, 실패 시 "관련 논문을 찾을 수 없습니다."

**DB 사용**: 없음

**실패 시 처리:**
- 이 메시지는 `src/agent/failure_detector.py`의 `FAILURE_PATTERNS`에 등록되어 있어 Fallback 트리거됩니다.

---

#### 10단계: 난이도별 답변 생성

**파일**: `src/agent/nodes.py`
**메서드**: `search_paper_node()` (라인 487-556)

**동작 설명:**
1. 난이도에 따라 2개 수준 선택
   - easy: ["elementary", "beginner"]
   - hard: ["intermediate", "advanced"]
2. 각 수준별로 `prompts/tool_prompts.json`에서 프롬프트 로드
3. LLM 호출하여 답변 생성 (2번)
4. 두 번째 수준의 답변을 `final_answer`로 설정

**프롬프트 구성:**
```python
system_prompt = get_tool_prompt("search_paper", level)  # JSON 로드
user_content = f"""[논문 검색 결과]
{raw_results}

[질문]
{question}

위 검색 결과를 바탕으로 질문에 답변해주세요."""

messages = [
    SystemMessage(content=system_prompt),
    HumanMessage(content=user_content)
]

response = llm_client.llm.invoke(messages)
```

**입력**: raw_results (Markdown), question, difficulty
**출력**: final_answers (Dict), final_answer (str)

**DB 사용**: 없음

**왜 2개 수준으로 생성하는가?**
- 사용자 경험 향상: 같은 질문에 대해 쉬운 버전과 어려운 버전 제공
- A/B 테스트 및 품질 평가를 위한 다양한 답변 생성

---

#### 11단계: 실패 감지 및 Fallback

**파일**: `src/agent/failure_detector.py`, `src/agent/nodes.py`
**메서드**: `is_failed()`, `fallback_router_node()`

**동작 설명:**
1. `search_paper_node`가 `final_answer`를 상태에 저장
2. `src/agent/tool_wrapper.py`의 `wrap_tool_node()`가 자동으로 실패 감지
3. `failure_detector.is_failed()`가 `final_answer`에서 실패 패턴 매칭
4. 실패 감지 시 `tool_status = "failed"` 설정
5. `src/agent/graph.py`의 `check_pipeline_or_fallback()`가 Fallback 필요 판단
6. `fallback_router_node()`가 Fallback Chain에서 다음 도구 선택

**Fallback Chain 순회:**
```python
# model_config.yaml에서 로드
fallback_chain = ["search_paper", "web_search", "general"]
failed_tools = ["search_paper"]  # 실패한 도구 기록

# 다음 도구 선택
for tool in fallback_chain:
    if tool not in failed_tools:
        next_tool = tool  # "web_search"
        break
```

**입력**: state (tool_status, failed_tools, fallback_chain)
**출력**: state (tool_choice = "web_search")

**DB 사용**: 없음

**실패 시 처리:**
- `web_search` 도구 실행
- `web_search`도 실패 시 `general` 도구 실행 (최종 Fallback)

---

### 전체 흐름 요약 표

| 단계 | 파일명 | 메서드명 | 동작 설명 | 입력 | 출력 | DB 사용 |
|------|--------|----------|-----------|------|------|---------|
| 1 | `main.py` | - | Streamlit 서버 시작 | - | - | 없음 |
| 2 | `ui/app.py` | `initialize_agent()` | Agent 그래프 초기화 | - | agent_executor | 없음 |
| 3 | `src/agent/graph.py` | `create_agent_graph()` | LangGraph 상태 머신 생성 | exp_manager | CompiledGraph | 없음 |
| 4 | `src/agent/nodes.py` | `router_node()` | 질문 분석 및 도구 선택 | state (question) | state (tool_choice) | 없음 |
| 5 | `configs/multi_request_patterns.yaml` | - | 패턴 매칭 (키워드 기반) | question | tool_pipeline | 없음 |
| 6 | `src/agent/nodes.py` | `search_paper_node()` | 도구 노드 실행 | state (question, difficulty) | state (final_answer) | 없음 |
| 7 | `src/tools/search_paper.py` | `search_paper_database()` | @tool 함수 호출 | query, top_k, ... | Markdown 문자열 | papers, paper_chunks |
| 8 | `src/rag/retriever.py` | `RAGRetriever.__init__()` | Retriever 초기화 | collection_name | RAGRetriever | pgvector 연결 |
| 9 | `src/database/vector_store.py` | `get_pgvector_store()` | PGVector 연결 | collection_name | PGVector 객체 | paper_chunks |
| 10 | `src/rag/retriever.py` | `multi_query_search()` | LLM 쿼리 확장 + 검색 | query, k | List[Document] | paper_chunks |
| 11 | `src/llm/client.py` | `LLMClient.invoke()` | LLM 쿼리 확장 | query | 3-5개 쿼리 | 없음 |
| 12 | `src/tools/search_paper.py` | `_keyword_search()` | PostgreSQL Full-Text Search | query, top_k | List[Dict] | papers (title, abstract) |
| 13 | `src/tools/search_paper.py` | `search_paper_database()` (병합) | 하이브리드 점수 병합 | vector_results, keyword_results | List[Dict] | 없음 |
| 14 | `src/tools/search_paper.py` | `_fetch_paper_meta()` | 메타데이터 조회 | paper_ids | Dict[int, Dict] | papers (all columns) |
| 15 | `src/tools/search_paper.py` | `_format_markdown()` | 결과 포맷팅 + 임계값 검증 | results | Markdown 문자열 | 없음 |
| 16 | `src/agent/nodes.py` | `search_paper_node()` (답변 생성) | 난이도별 프롬프트 로드 | difficulty | system_prompt | 없음 |
| 17 | `prompts/tool_prompts.json` | - | JSON 프롬프트 로드 | tool, level | prompt 문자열 | 없음 |
| 18 | `src/llm/client.py` | `LLMClient.invoke()` | LLM 답변 생성 | messages | response.content | 없음 |
| 19 | `src/agent/failure_detector.py` | `is_failed()` | 실패 패턴 감지 | final_answer | (is_failed, reason) | 없음 |
| 20 | `src/agent/nodes.py` | `fallback_router_node()` | Fallback 다음 도구 선택 | state (failed_tools) | state (tool_choice) | 없음 |

---

## 💡 사용 예시

### 예시 1: 성공적인 논문 검색

**사용자 질문:**
```
RAG 관련 논문 찾아줘
```

**실행 흐름:**
1. 패턴 매칭: `keywords: [논문, 찾]` → `search_paper` 도구 선택
2. 벡터 검색: MultiQuery로 3개 쿼리 생성
   - "RAG 논문"
   - "Retrieval Augmented Generation 연구"
   - "RAG 시스템 논문"
3. 키워드 검색: PostgreSQL에서 "Retrieval-Augmented Generation" 검색
4. 하이브리드 병합: 벡터 70% + 키워드 30%
5. Top-5 논문 선정
6. 메타데이터 조회 및 Markdown 포맷팅
7. LLM 답변 생성 (easy 난이도: elementary + beginner)

**출력 예시:**
```markdown
## 검색된 논문

### 1. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
- **저자**: Patrick Lewis, Ethan Perez, ...
- **출판일**: 2020-05-22
- **카테고리**: cs.CL
- **인용수**: 1250
- **URL**: https://arxiv.org/abs/2005.11401
- **섹션**: 본문
- **유사도 점수(낮을수록 유사)**: 0.2345

RAG는 사전 학습된 언어 모델과 외부 지식 베이스를 결합하여 지식 집약적인 NLP 작업의 성능을 향상시키는 방법입니다. 이 논문에서는 DPR(Dense Passage Retrieval)을 사용하여...

---

### 2. In-Context Retrieval-Augmented Language Models
- **저자**: Ori Ram, Yoav Levine, ...
(계속)
```

**LLM 최종 답변 (beginner 수준):**
```
RAG(Retrieval-Augmented Generation)는 대규모 언어 모델의 한계를 극복하기 위한 방법입니다.
위에서 찾은 논문들은 RAG의 핵심 개념과 다양한 응용 사례를 다루고 있습니다.

첫 번째 논문인 "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"는
RAG의 기본 개념을 제시한 논문으로, 외부 지식 베이스에서 관련 정보를 검색하여 답변의
정확성을 높이는 방법을 설명합니다.

두 번째 논문인 "In-Context Retrieval-Augmented Language Models"는 문맥 내에서
정보를 검색하는 방식으로 RAG를 개선한 연구입니다.

이러한 논문들은 RAG 시스템을 이해하고 구현하는 데 중요한 참고 자료가 될 것입니다.
```

---

### 예시 2: 검색 실패 → Fallback 작동

**사용자 질문:**
```
XYZ123 알고리즘 논문 찾아줘
```

**실행 흐름:**
1. 패턴 매칭: `keywords: [논문, 찾]` → `search_paper` 도구 선택
2. 벡터 검색: "XYZ123" 키워드로 검색 → 유사도 점수 모두 0.8 이상 (낮은 유사도)
3. 키워드 검색: PostgreSQL에서 "XYZ123" 검색 → 결과 없음
4. 유사도 임계값 검증: 모든 점수 > 0.5 → 실패
5. 반환 메시지: `"관련 논문을 찾을 수 없습니다."`
6. 실패 감지: `failure_detector.is_failed()` → True
7. Fallback 실행: `web_search` 도구로 전환
8. Web 검색 시도: Tavily API로 "XYZ123 알고리즘 논문" 검색
9. 성공 시 웹 결과 반환, 실패 시 `general` 도구로 최종 전환

**Fallback 타임라인:**
```python
[
    {
        "timestamp": "2025-11-07T14:30:15",
        "event": "fallback",
        "from_tool": "search_paper",
        "to_tool": "web_search",
        "failure_reason": "패턴 감지: 관련 논문을 찾을 수 없습니다",
        "retry_count": 1
    }
]
```

---

### 예시 3: 시간 키워드로 Web 검색 우선 실행

**사용자 질문:**
```
최신 Transformer 논문 찾아줘
```

**실행 흐름:**
1. 패턴 매칭: `keywords: [최신]` → `web_search` 도구 우선 선택 (priority: 140)
2. RAG 논문 검색 도구는 **건너뜀** (시간 키워드 감지)
3. Tavily API로 웹 검색 수행
4. 최신 arXiv 논문 또는 뉴스 기사 검색
5. 성공 시 웹 결과 반환

**왜 건너뛰는가?**
- RAG 데이터베이스는 정적 데이터로, 최신 정보(1-2주 이내)를 반영하지 못합니다.
- 시간 관련 키워드("최신", "최근", "트렌드")가 있으면 Web 검색이 더 적합합니다.

---

## 🔍 핵심 포인트

### 하이브리드 검색의 장점

**1. 의미적 검색 (벡터 검색 70%)**
- 동의어, 유사 표현 감지
- 예: "RAG" = "Retrieval-Augmented Generation"
- pgvector cosine similarity로 유사도 측정

**2. 정확한 검색 (키워드 검색 30%)**
- 특정 논문 제목, 저자명 정확 매칭
- PostgreSQL Full-Text Search 사용
- 인용수 기준 2차 정렬

**3. 가중치 조정 가능**
- `configs/model_config.yaml`에서 도구별 가중치 설정
- search_paper: vector 70% + keyword 30%
- glossary: vector 50% + keyword 50%

### Fallback Chain의 중요성

**왜 Fallback이 필요한가?**
- RAG DB는 제한된 데이터셋 (arXiv 논문 1000편)
- 사용자 질문이 DB에 없는 논문일 수 있음
- 실패 시 자동으로 Web 검색 또는 LLM 답변으로 전환

**Fallback 우선순위:**
1. search_paper (가장 빠르고 정확)
2. web_search (최신 정보 포함)
3. general (LLM 지식 기반, 항상 성공)

### MultiQuery의 효과

**왜 쿼리를 확장하는가?**
- 사용자 질문이 짧거나 모호할 수 있음
- 예: "RAG 논문" → 너무 짧음
- MultiQuery로 3-5개 변형 생성:
  - "RAG 논문"
  - "Retrieval-Augmented Generation 연구"
  - "RAG 시스템 구현 논문"
  - "RAG 모델 아키텍처"

**검색 품질 향상:**
- 다양한 각도에서 검색하여 누락 방지
- 중복 제거로 Top-K 품질 보장

---

## 📚 참고 정보

### 관련 파일 목록

**핵심 파일:**
- `src/tools/search_paper.py`: RAG 논문 검색 도구 구현
- `src/rag/retriever.py`: RAGRetriever 클래스
- `src/database/vector_store.py`: PGVector 연결
- `src/agent/nodes.py`: search_paper_node 구현
- `configs/multi_request_patterns.yaml`: 패턴 매칭 규칙

**설정 파일:**
- `configs/model_config.yaml`: LLM, RAG, Fallback 설정
- `configs/db_config.yaml`: PostgreSQL 연결 정보
- `prompts/tool_prompts.json`: 난이도별 프롬프트

**데이터베이스:**
- PostgreSQL 테이블: `papers`
- pgvector 컬렉션: `paper_chunks`

### DB 스키마

**papers 테이블:**
```sql
CREATE TABLE papers (
    paper_id SERIAL PRIMARY KEY,
    arxiv_id VARCHAR(64),
    title TEXT NOT NULL,
    authors TEXT,
    publish_date DATE,
    source VARCHAR(32),
    url TEXT UNIQUE,
    category TEXT,
    citation_count INT,
    abstract TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_papers_title ON papers USING gin (to_tsvector('simple', title));
CREATE INDEX idx_papers_category ON papers (category);
CREATE INDEX idx_papers_date ON papers (publish_date);
```

**paper_chunks 컬렉션 (pgvector):**
- 벡터 차원: 1536 (OpenAI text-embedding-3-small)
- 메타데이터: paper_id, title, authors, section, publish_date
- 검색 방식: cosine distance (L2 norm)

---

**작성일**: 2025-11-07
**버전**: 1.0
