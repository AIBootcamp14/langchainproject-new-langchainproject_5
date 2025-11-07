# 이중 요청: Web 논문 검색 → 저장 아키텍처

## 📋 문서 정보
- **작성일**: 2025-11-07
- **작성자**: 최현화[팀장]
- **프로젝트명**: 논문 리뷰 챗봇 (AI Agent + RAG)
- **팀명**: 연결의 민족
- **문서 버전**: 1.0

---

## 📑 목차
1. [시나리오 개요](#시나리오-개요)
2. [사용자 요청 분석](#사용자-요청-분석)
3. [도구 자동 전환 및 Fallback](#도구-자동-전환-및-fallback)
4. [단순 흐름 아키텍처](#단순-흐름-아키텍처)
5. [상세 기능 동작 흐름도](#상세-기능-동작-흐름도)
6. [전체 흐름 요약 표](#전체-흐름-요약-표)
7. [동작 설명 (초보 개발자용)](#동작-설명-초보-개발자용)
8. [실행 예시](#실행-예시)
9. [핵심 포인트](#핵심-포인트)

---

## 📌 시나리오 개요

### 다중 요청의 목적

사용자가 **최신 논문**을 웹에서 검색한 후 바로 파일로 저장까지 원하는 경우, RAG DB를 건너뛰고 Web 검색부터 시작하여 저장까지 순차적으로 실행합니다.

**실행되는 도구 순서:**
```
[키워드 감지: '최신', '최근']
  ↓
RAG 논문 검색 건너뜀 (최신성 제한적)
  ↓
1단계: web_search (Tavily API로 최신 논문 검색)
  ↓ 실패 시
2단계: general (일반 답변 - LLM 지식 기반)
  ↓ 성공 시
3단계: save_file (파일 저장)
```

**사용자 요청 예시:**
- "**최신** AI 논문 찾아서 저장해줘"
- "**최근** Transformer 논문 검색해서 저장해줘"
- "**2024년** LLM 연구 찾아서 저장해줘"

**⚠️ 중요: '최신', '최근', 연도(2024년 등) + '저장' 키워드가 반드시 포함되어야 합니다.**

---

## 📋 사용자 요청 분석

### 정확한 사용자 질문 예시

**예시 1: "최신 AI 논문 찾아서 저장해줘"**
- **키워드 분석**:
  - `최신`: ✅ **시간 키워드 포함** → RAG 건너뛰고 Web 검색 우선
  - `논문`: 논문 검색 필요
  - `저장`: 파일 저장 작업 필요

**예시 2: "최근 Transformer 연구 검색해서 저장해줘"**
- **키워드 분석**:
  - `최근`: ✅ **시간 키워드 포함** → RAG 건너뛰고 Web 검색 우선
  - `Transformer`: 검색 쿼리
  - `검색`, `저장`: 검색 후 저장 작업

**예시 3: "Transformer 논문 찾아서 저장해줘" (시간 키워드 없음)**
- **키워드 분석**:
  - 시간 키워드 없음 → RAG 논문 검색 우선 (본 문서의 시나리오와 다름)
  - 이 경우 `search_paper → save_file` 파이프라인 적용

### 도구 선택 근거

**패턴 매칭 방식 (src/agent/nodes.py:75-130)**

`configs/multi_request_patterns.yaml` 파일의 패턴을 기반으로 자동 감지:

```yaml
# 논문 저장 패턴 (기본)
- keywords:
  - 논문
  - 찾
  - 저장
  exclude_keywords:
  - 요약
  tools:
  - search_paper
  - save_file
  description: 논문 검색 후 저장
  priority: 110
```

**매칭 로직:**
1. 질문에 `논문` AND `찾` AND `저장` 키워드 모두 포함
2. 제외 키워드 (`요약`) 없음
3. 자동으로 2단계 파이프라인 설정: `[search_paper, save_file]`

**⚠️ 핵심 차이점: 시간 키워드 감지 시 RAG 건너뛰기**

**시간 키워드 감지 로직 (src/agent/router.py 또는 nodes.py):**
- **시간 키워드 목록**: `최신`, `최근`, `2024년`, `2023년`, `올해`, `작년`, `latest`, `recent`
- **동작 방식**:
  1. 질문에 시간 키워드가 포함되어 있는지 확인
  2. 시간 키워드가 있으면 `tool_pipeline`에서 `search_paper` 제거
  3. `web_search`를 첫 번째 도구로 추가
  4. 파이프라인: `[web_search, general, save_file]`로 변경

**AgentState 설정 (시간 키워드 있음):**
```python
# 시간 키워드 감지 전 (기본)
state["tool_pipeline"] = ["search_paper", "save_file"]

# 시간 키워드 감지 후 (RAG 건너뜀)
state["tool_pipeline"] = ["web_search", "general", "save_file"]
state["tool_choice"] = "web_search"  # 첫 번째 도구
state["pipeline_index"] = 1
state["routing_method"] = "pattern_based_with_temporal_keyword"
state["routing_reason"] = "시간 키워드 감지: RAG 건너뛰고 Web 검색 우선"
state["pipeline_description"] = "순차 실행: web_search → general → save_file"
```

---

## 🔄 도구 자동 전환 및 Fallback

### 전체 흐름도

```
사용자: "최신 AI 논문 찾아서 저장해줘"
**중요**: '최신' 키워드 포함 → RAG 건너뛰고 Web 검색이 첫 번째 도구
↓
키워드 감지 ('최신' 포함) → RAG 논문 검색 건너뜀
↓
[1단계] Web 논문 검색 (web_search) - 첫 번째 도구로 실행
├─ 성공 → Tavily API로 최신 논문 발견, 2단계로
└─ 실패 → 일반 답변 도구 (LLM이 최신 논문 검색)
    └─ 2단계로
↓
[2단계] 저장 도구 (save_file)
├─ 성공 → 저장 완료 메시지
└─ 실패 → 오류 메시지
```

### 키워드 감지 상세 로직

**시간 키워드 감지가 도구 선택에 미치는 영향:**

1. **질문 분석 단계 (src/agent/nodes.py:router_node)**
   - 질문에서 시간 키워드 추출
   - 시간 키워드 목록: `['최신', '최근', '2024년', '2023년', '올해', '작년']`

2. **파이프라인 조정 (src/agent/nodes.py:117-129)**
   ```python
   # 시간 키워드 감지
   temporal_keywords = ['최신', '최근', '올해', '작년', '2024', '2023', 'latest', 'recent']
   has_temporal = any(kw in question for kw in temporal_keywords)

   if has_temporal:
       # RAG 검색 제거, Web 검색 추가
       if 'search_paper' in state["tool_pipeline"]:
           state["tool_pipeline"].remove('search_paper')

       # web_search가 없으면 추가
       if 'web_search' not in state["tool_pipeline"]:
           state["tool_pipeline"].insert(0, 'web_search')
           # general fallback 추가
           if 'general' not in state["tool_pipeline"]:
               state["tool_pipeline"].insert(1, 'general')

       state["tool_choice"] = state["tool_pipeline"][0]  # web_search

       if exp_manager:
           exp_manager.logger.write(f"시간 키워드 감지: RAG 건너뜀, Web 검색 우선")
   ```

3. **RAG를 건너뛰는 이유:**
   - RAG DB는 수동으로 업데이트되는 정적 데이터
   - 최신성이 제한적 (DB 업데이트 시점에 따라 다름)
   - Web 검색(Tavily API)은 실시간 최신 정보 제공

### Fallback 체인

**1단계 Fallback: web_search → general**
- web_search 실패 시 (API 오류, 검색 결과 없음)
- general 도구가 LLM 지식 기반으로 최신 논문 설명
- src/tools/web_search.py:76-81 참조

**2단계: 저장은 Fallback 없음**
- save_file은 항상 실행 (성공/실패만 판단)
- 저장 실패 시 오류 메시지 반환

---

## 📊 단순 흐름 아키텍처

### 워크플로우 다이어그램

```mermaid
graph TB
    subgraph MainFlow["📋 Web 논문 검색 → 저장 워크플로우"]
        direction TB

        subgraph Init["🔸 초기화 단계"]
            direction LR
            Start([사용자 질문]) --> A[키워드 감지<br/>최신/최근/연도]
            A --> B{시간 키워드<br/>포함?}
        end

        subgraph Step1["🔹 1단계: Web 논문 검색"]
            direction LR
            D[Tavily API<br/>웹 검색] --> E{검색<br/>성공?}
            E -->|성공| F[논문 결과<br/>저장]
            E -->|실패| G[일반 답변<br/>Fallback]
        end

        subgraph Step2["🔸 2단계: 파일 저장"]
            direction LR
            H[final_answers<br/>확인] --> I{답변<br/>존재?}
            I -->|4개 수준| J[난이도별<br/>4개 파일 저장]
            I -->|1개| K[단일<br/>파일 저장]
        end

        subgraph Output["🔹 출력 단계"]
            direction LR
            M[저장 완료<br/>메시지] --> End([최종 답변])
        end

        %% 단계 간 연결
        Init --> Step1
        Step1 --> Step2
        Step2 --> Output
    end

    %% 스타일 정의
    style MainFlow fill:#fffde7,stroke:#f57f17,stroke-width:3px,color:#000

    style Init fill:#e0f7fa,stroke:#006064,stroke-width:2px,color:#000
    style Step1 fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#000
    style Step2 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style Output fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000

    %% 노드 스타일 (초기화 - 청록)
    style Start fill:#b2ebf2,stroke:#00838f,stroke-width:2px,color:#000
    style A fill:#b2ebf2,stroke:#00838f,stroke-width:2px,color:#000
    style B fill:#b2ebf2,stroke:#00838f,stroke-width:2px,color:#000

    %% 노드 스타일 (1단계 - 파랑)
    style D fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style E fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style F fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style G fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000

    %% 노드 스타일 (2단계 - 보라)
    style H fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px,color:#000
    style I fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px,color:#000
    style J fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px,color:#000
    style K fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px,color:#000

    %% 노드 스타일 (출력 - 파랑)
    style M fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style End fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000

    %% 연결선 스타일 (초기화 0~1)
    linkStyle 0 stroke:#00838f,stroke-width:2px
    linkStyle 1 stroke:#00838f,stroke-width:2px

    %% 연결선 스타일 (1단계 2~5)
    linkStyle 2 stroke:#1565c0,stroke-width:2px
    linkStyle 3 stroke:#1565c0,stroke-width:2px
    linkStyle 4 stroke:#1565c0,stroke-width:2px
    linkStyle 5 stroke:#d84315,stroke-width:2px

    %% 연결선 스타일 (2단계 6~9)
    linkStyle 6 stroke:#6a1b9a,stroke-width:2px
    linkStyle 7 stroke:#6a1b9a,stroke-width:2px
    linkStyle 8 stroke:#6a1b9a,stroke-width:2px

    %% 연결선 스타일 (출력 9~10)
    linkStyle 9 stroke:#1565c0,stroke-width:2px

    %% 단계 간 연결 (회색 11~13)
    linkStyle 11 stroke:#616161,stroke-width:3px
    linkStyle 12 stroke:#616161,stroke-width:3px
    linkStyle 13 stroke:#616161,stroke-width:3px
```

---

## 🔍 상세 기능 동작 흐름도

### 전체 실행 흐름 (파일 및 메서드 단위)

```mermaid
graph TB
    subgraph MainFlow["📋 Web 논문 검색 → 저장 상세 흐름"]
        direction TB

        subgraph Init["🔸 초기화"]
            direction LR
            Start([main.py<br/>사용자 입력]) --> A[main.py<br/>create_agent<br/>Agent 생성]
            A --> B[agent.invoke<br/>question 전달]
        end

        subgraph Pattern["🔹 패턴 매칭"]
            direction LR
            C[nodes.py<br/>router_node<br/>라우터 실행] --> D[multi_request_patterns.yaml<br/>패턴 로드]
            D --> E{논문+저장<br/>패턴 매칭?}
            E -->|매칭| F[tool_pipeline 설정<br/>search_paper→save_file]
            F --> G{시간 키워드<br/>포함?}
            G -->|있음| H[search_paper 제거<br/>web_search 추가]
            G -->|없음| I[기본 파이프라인<br/>유지]
        end

        subgraph WebSearch["🔸 Web 검색"]
            direction LR
            J[nodes.py<br/>도구 선택<br/>tool_choice=web_search] --> K[web_search.py<br/>web_search_node<br/>노드 실행]
            K --> L[TavilySearchResults<br/>API 호출]
            L --> M{검색<br/>성공?}
            M -->|성공| N[arXiv 논문<br/>자동 저장]
            N --> O[LLMClient<br/>결과 정리]
            M -->|실패| P[Fallback<br/>general_answer_node]
        end

        subgraph Router2["🔹 라우터 2"]
            direction LR
            Q[nodes.py<br/>router_node<br/>재실행] --> R{pipeline_index<br/>< 파이프라인 길이?}
            R -->|Yes| S[tool_choice<br/>= save_file]
        end

        subgraph Save["🔸 파일 저장"]
            direction LR
            T[nodes.py<br/>도구 선택<br/>tool_choice=save_file] --> U[save_file.py<br/>save_file_node<br/>노드 실행]
            U --> V{final_answers<br/>존재?}
            V -->|4개 수준| W[난이도별<br/>4개 파일 저장]
            V -->|없음| X[tool_result<br/>단일 파일 저장]
            W --> Y[타임스탬프<br/>파일명 생성]
            X --> Y
        end

        subgraph Output["🔹 출력"]
            direction LR
            Z[저장 경로<br/>메시지 생성] --> End([main.py<br/>최종 답변])
        end

        %% 단계 간 연결
        Init --> Pattern
        Pattern --> WebSearch
        WebSearch --> Router2
        Router2 --> Save
        Save --> Output
    end

    %% 스타일 정의
    style MainFlow fill:#fffde7,stroke:#f57f17,stroke-width:3px,color:#000

    style Init fill:#e0f7fa,stroke:#006064,stroke-width:2px,color:#000
    style Pattern fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#000
    style WebSearch fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style Router2 fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style Save fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style Output fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000

    %% 노드 스타일 (초기화 - 청록)
    style Start fill:#b2ebf2,stroke:#00838f,stroke-width:2px,color:#000
    style A fill:#b2ebf2,stroke:#00838f,stroke-width:2px,color:#000
    style B fill:#b2ebf2,stroke:#00838f,stroke-width:2px,color:#000

    %% 노드 스타일 (패턴 - 파랑)
    style C fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style D fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style E fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style F fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style G fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style H fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style I fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000

    %% 노드 스타일 (Web 검색 - 보라)
    style J fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px,color:#000
    style K fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px,color:#000
    style L fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px,color:#000
    style M fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px,color:#000
    style N fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px,color:#000
    style O fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px,color:#000
    style P fill:#ffccbc,stroke:#d84315,stroke-width:2px,color:#000

    %% 노드 스타일 (라우터2 - 주황)
    style Q fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    style R fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000
    style S fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000

    %% 노드 스타일 (저장 - 핑크)
    style T fill:#f8bbd0,stroke:#ad1457,stroke-width:2px,color:#000
    style U fill:#f8bbd0,stroke:#ad1457,stroke-width:2px,color:#000
    style V fill:#f8bbd0,stroke:#ad1457,stroke-width:2px,color:#000
    style W fill:#f8bbd0,stroke:#ad1457,stroke-width:2px,color:#000
    style X fill:#f8bbd0,stroke:#ad1457,stroke-width:2px,color:#000
    style Y fill:#f8bbd0,stroke:#ad1457,stroke-width:2px,color:#000

    %% 노드 스타일 (출력 - 파랑)
    style Z fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000
    style End fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#000

    %% 연결선 스타일 (초기화 0~2)
    linkStyle 0 stroke:#00838f,stroke-width:2px
    linkStyle 1 stroke:#00838f,stroke-width:2px

    %% 연결선 스타일 (패턴 2~8)
    linkStyle 2 stroke:#1565c0,stroke-width:2px
    linkStyle 3 stroke:#1565c0,stroke-width:2px
    linkStyle 4 stroke:#1565c0,stroke-width:2px
    linkStyle 5 stroke:#1565c0,stroke-width:2px
    linkStyle 6 stroke:#1565c0,stroke-width:2px
    linkStyle 7 stroke:#1565c0,stroke-width:2px
    linkStyle 8 stroke:#1565c0,stroke-width:2px

    %% 연결선 스타일 (Web 검색 9~15)
    linkStyle 9 stroke:#6a1b9a,stroke-width:2px
    linkStyle 10 stroke:#6a1b9a,stroke-width:2px
    linkStyle 11 stroke:#6a1b9a,stroke-width:2px
    linkStyle 12 stroke:#6a1b9a,stroke-width:2px
    linkStyle 13 stroke:#6a1b9a,stroke-width:2px
    linkStyle 14 stroke:#6a1b9a,stroke-width:2px
    linkStyle 15 stroke:#d84315,stroke-width:2px

    %% 연결선 스타일 (라우터2 16~18)
    linkStyle 16 stroke:#e65100,stroke-width:2px
    linkStyle 17 stroke:#e65100,stroke-width:2px

    %% 연결선 스타일 (저장 18~23)
    linkStyle 18 stroke:#ad1457,stroke-width:2px
    linkStyle 19 stroke:#ad1457,stroke-width:2px
    linkStyle 20 stroke:#ad1457,stroke-width:2px
    linkStyle 21 stroke:#ad1457,stroke-width:2px
    linkStyle 22 stroke:#ad1457,stroke-width:2px
    linkStyle 23 stroke:#ad1457,stroke-width:2px

    %% 연결선 스타일 (출력 24~25)
    linkStyle 24 stroke:#1565c0,stroke-width:2px

    %% 단계 간 연결 (회색 26~30)
    linkStyle 26 stroke:#616161,stroke-width:3px
    linkStyle 27 stroke:#616161,stroke-width:3px
    linkStyle 28 stroke:#616161,stroke-width:3px
    linkStyle 29 stroke:#616161,stroke-width:3px
    linkStyle 30 stroke:#616161,stroke-width:3px
```

---

## 📋 전체 흐름 요약 표

| 단계 | 도구명 | 파일명 | 메서드명 | 동작 설명 | 입력 | 출력 | Fallback | 세션 저장 |
|------|--------|--------|----------|-----------|------|------|----------|----------|
| 0 | 초기화 | main.py | create_agent | Agent 생성 | question, difficulty | agent | 없음 | messages |
| 0-1 | 라우터 | nodes.py | router_node | 질문 분석 및 도구 선택 | question | tool_choice, tool_pipeline | 없음 | routing_method |
| 0-2 | 패턴 매칭 | nodes.py | router_node | 시간 키워드 감지 | question | tool_pipeline 조정 | 없음 | routing_reason |
| 1 | Web 검색 | web_search.py | web_search_node | Tavily API로 최신 논문 검색 | question | final_answers (2개 수준) | general_answer | final_answers, tool_result |
| 1-F | 일반 답변 | general_answer.py | general_answer_node | LLM 지식 기반 답변 | question | final_answers (2개 수준) | 없음 | final_answers |
| 2 | 파일 저장 | save_file.py | save_file_node | 난이도별 파일 저장 | final_answers | 저장 경로 메시지 | 없음 | save_counter |

**설명:**
- **0-2 단계**: 시간 키워드(`최신`, `최근`) 감지 시 `search_paper`를 파이프라인에서 제거하고 `web_search` 추가
- **1단계**: Tavily API로 웹 검색, arXiv 논문 자동 저장 (src/tools/web_search.py:84-111)
- **1-F**: web_search 실패 시 general_answer가 LLM 지식 기반으로 답변
- **2단계**: final_answers(4개 수준) 또는 tool_result(1개)를 파일로 저장, 타임스탬프 기반 파일명 생성

---

## 💡 동작 설명 (초보 개발자용)

### 1. 키워드 감지가 도구 선택에 미치는 영향

**문제: 왜 RAG를 건너뛰나요?**

사용자가 "**최신** AI 논문 찾아서 저장해줘"라고 질문하면:

1. **패턴 매칭**:
   - `논문` + `찾` + `저장` 키워드 감지
   - 기본 파이프라인 설정: `[search_paper, save_file]`

2. **시간 키워드 감지**:
   - `최신` 키워드 발견
   - `search_paper`는 PostgreSQL RAG DB를 검색 (정적 데이터)
   - RAG DB는 수동 업데이트이므로 최신성 보장 어려움
   - **결론**: `search_paper` 제거, `web_search` 및 `general` 추가

3. **조정된 파이프라인**:
   - `[web_search, general, save_file]`
   - Tavily API는 실시간 웹 크롤링으로 최신 정보 제공

### 2. RAG를 건너뛰는 이유와 과정

**RAG (Retrieval-Augmented Generation):**
- PostgreSQL `papers` 테이블에 저장된 논문 검색
- pgvector `paper_chunks` 컬렉션에서 임베딩 검색
- **장점**: 정확한 논문 원문 기반 답변
- **단점**: DB 업데이트 시점 이후 논문은 검색 불가

**Web Search (Tavily API):**
- 실시간 웹 크롤링
- arXiv, Google Scholar, 학술 사이트 검색
- **장점**: 최신 논문 즉시 검색 가능
- **단점**: 논문 전문이 아닌 초록/요약만 제공

**건너뛰기 과정 (src/agent/nodes.py:router_node):**
```python
# 1. 시간 키워드 감지
temporal_keywords = ['최신', '최근', '올해', '작년', '2024', '2023']
has_temporal = any(kw in question for kw in temporal_keywords)

# 2. 파이프라인 조정
if has_temporal:
    if 'search_paper' in state["tool_pipeline"]:
        state["tool_pipeline"].remove('search_paper')

    if 'web_search' not in state["tool_pipeline"]:
        state["tool_pipeline"].insert(0, 'web_search')

    if 'general' not in state["tool_pipeline"]:
        state["tool_pipeline"].insert(1, 'general')

    state["tool_choice"] = state["tool_pipeline"][0]  # web_search

    if exp_manager:
        exp_manager.logger.write("시간 키워드 감지: RAG 건너뜀, Web 검색 우선")
```

### 3. Web 검색 실행 과정

**단계별 실행 (src/tools/web_search.py):**

1. **Tavily API 초기화** (web_search.py:44-57)
   ```python
   search_tool = TavilySearchResults(
       max_results=5,
       api_key=os.getenv("TAVILY_API_KEY")
   )
   ```

2. **웹 검색 실행** (web_search.py:60-73)
   ```python
   search_results = search_tool.invoke({"query": question})
   # 결과: [{"title": "...", "content": "...", "url": "..."}, ...]
   ```

3. **arXiv 논문 자동 저장** (web_search.py:84-111)
   - 검색 결과 URL에서 `arxiv.org` 포함 여부 확인
   - arXiv URL 발견 시 자동으로 논문 다운로드 + DB 저장
   ```python
   for result in search_results:
       url = result.get('url', '')
       if 'arxiv.org' in url:
           arxiv_handler.process_arxiv_paper(url)
   ```

4. **LLM 결과 정리** (web_search.py:119-198)
   - 검색 결과를 난이도별로 정리
   - easy 모드: Solar-pro2 (한국어 특화)
   - hard 모드: GPT-5 (기술적 정확도)

### 4. 파일 저장 실행 과정

**저장 우선순위 (src/tools/save_file.py:68-149):**

1. **final_answers (우선순위 0)** - 난이도별 4개 파일
   ```python
   final_answers = state.get("final_answers", {})
   # {"elementary": "...", "beginner": "...", "intermediate": "...", "advanced": "..."}

   for level, content in final_answers.items():
       filename = f"{timestamp}_response_{save_counter}_{level}.md"
       # 저장: 20251107_143052_response_1_elementary.md
   ```

2. **tool_result (우선순위 1)** - 단일 파일
   ```python
   tool_result = state.get("tool_result", "")
   if tool_result:
       filename = f"{timestamp}_response_{save_counter}.md"
   ```

3. **final_answer (우선순위 2)** - 호환성
4. **messages (우선순위 3)** - 마지막 메시지

**파일명 형식:**
```
날짜_시간_response_번호_수준.md
예: 20251107_143052_response_1_beginner.md
```

---

## 📝 실행 예시

### 예시 1: 최신 AI 논문 저장

**사용자 질문:**
```
최신 AI 논문 찾아서 저장해줘
```

**1단계: 키워드 감지 과정**
```
[라우터 노드]
- 키워드 감지: ['최신', 'AI', '논문', '찾', '저장']
- 시간 키워드: '최신' ✅
- 패턴 매칭: 논문 + 찾 + 저장 → [search_paper, save_file]
- 시간 키워드로 인한 조정: search_paper 제거, web_search/general 추가
- 최종 파이프라인: [web_search, general, save_file]
- tool_choice: web_search
```

**2단계: 1단계 실행 결과 (Web 검색)**
```
[Web 검색 노드 - web_search.py]
Tavily API 호출: "최신 AI 논문"

검색 결과 5개:
1. [arXiv] "Attention Is All You Need" (2024년 개정판)
   URL: https://arxiv.org/abs/1706.03762
   → arXiv 자동 저장 완료

2. [Google Scholar] "GPT-4 Technical Report"
   URL: https://arxiv.org/abs/2303.08774
   → arXiv 자동 저장 완료

3. [arXiv] "LLaMA: Open and Efficient Foundation Language Models"
   ...

LLM 정리 (Solar-pro2):
"최신 AI 논문으로는 Transformer 아키텍처의 개정판과 GPT-4 기술 보고서가 있습니다.
Transformer는 self-attention 메커니즘으로 시퀀스 모델링의 혁신을 가져왔으며..."

final_answers 저장:
- elementary: "AI는 컴퓨터가 사람처럼 생각하는 기술입니다..."
- beginner: "최신 AI 논문으로는 Transformer와 GPT-4가 있습니다..."
- intermediate: "Transformer 아키텍처는 self-attention으로..."
- advanced: "제안된 아키텍처는 encoder-decoder 구조를 유지하되..."

tool_result에 저장 ✅
```

**3단계: 2단계 실행 결과 (파일 저장)**
```
[파일 저장 노드 - save_file.py]
final_answers 확인: 4개 수준 존재 ✅

저장 카운터 증가: 0 → 1
타임스탬프 생성: 20251107_143052

파일 저장:
1. 20251107_143052_response_1_elementary.md (초등학생용)
2. 20251107_143052_response_1_beginner.md (초급자용)
3. 20251107_143052_response_1_intermediate.md (중급자용)
4. 20251107_143052_response_1_advanced.md (고급자용)

저장 완료 ✅
```

**최종 출력:**
```
난이도별 답변이 각각 저장되었습니다.
저장된 파일:
- 초등학생용(8-13세): outputs/20251107_143052_response_1_elementary.md
- 초급자용(14-22세): outputs/20251107_143052_response_1_beginner.md
- 중급자용(23-30세): outputs/20251107_143052_response_1_intermediate.md
- 고급자용(30세 이상): outputs/20251107_143052_response_1_advanced.md
```

### 예시 2: 최근 Transformer 연구 저장

**사용자 질문:**
```
최근 Transformer 연구 검색해서 저장해줘
```

**키워드 감지:**
- 시간 키워드: `최근` ✅
- 검색 키워드: `Transformer`, `검색`
- 작업 키워드: `저장`

**파이프라인:**
```
[web_search, general, save_file]
```

**실행 결과:**
```
1. Web 검색: Tavily API로 "최근 Transformer 연구" 검색
   → arXiv 논문 3개 자동 저장

2. 파일 저장: final_answers 4개 수준을 각각 파일로 저장
   → 타임스탬프 기반 파일명 4개 생성

3. 최종 출력: 저장 완료 메시지 + 파일 경로 4개
```

### 예시 3: 시간 키워드 없는 경우 (비교)

**사용자 질문:**
```
Transformer 논문 찾아서 저장해줘
```

**키워드 감지:**
- 시간 키워드 없음 ❌
- 검색 키워드: `Transformer`, `논문`, `찾`
- 작업 키워드: `저장`

**파이프라인:**
```
[search_paper, save_file]
```

**차이점:**
- RAG 검색 우선 실행
- PostgreSQL `papers` 테이블에서 먼저 검색
- DB에 논문이 있으면 Web 검색 건너뜀
- DB에 논문이 없으면 Web 검색으로 Fallback

---

## 🎯 핵심 포인트

### 1. 시간 키워드 감지의 중요성

**시간 키워드 목록:**
- 한국어: `최신`, `최근`, `올해`, `작년`, `2024년`, `2023년`
- 영어: `latest`, `recent`, `2024`, `2023`

**감지 위치:**
- src/agent/nodes.py:router_node 함수
- 패턴 매칭 후 파이프라인 조정 단계

### 2. RAG vs Web 검색 선택 기준

| 구분 | RAG 검색 (search_paper) | Web 검색 (web_search) |
|------|--------------------------|------------------------|
| 데이터 소스 | PostgreSQL papers 테이블 | Tavily API (실시간 웹) |
| 최신성 | 제한적 (DB 업데이트 시점) | 실시간 최신 정보 |
| 정확도 | 높음 (논문 전문 기반) | 중간 (초록/요약 기반) |
| 선택 기준 | 시간 키워드 없음 | 시간 키워드 있음 |
| Fallback | web_search | general |

### 3. 파일 저장 우선순위

**저장 데이터 우선순위:**
1. **final_answers** (난이도별 4개 파일) - 가장 우선
2. **tool_result** (단일 파일)
3. **final_answer** (호환성)
4. **messages** (마지막 메시지)

### 4. 난이도별 파일 저장

**파일 저장 형식 (final_answers 존재 시):**
```
20251107_143052_response_1_elementary.md
20251107_143052_response_1_beginner.md
20251107_143052_response_1_intermediate.md
20251107_143052_response_1_advanced.md
```

**파일명 구성:**
- 날짜: `20251107` (YYYYMMDD)
- 시간: `143052` (HHMMSS)
- 타입: `response`
- 번호: `1` (세션별 누적 번호)
- 수준: `elementary`, `beginner`, `intermediate`, `advanced`

### 5. arXiv 논문 자동 저장

**자동 저장 로직 (src/tools/web_search.py:84-111):**
- Web 검색 결과 URL에서 `arxiv.org` 감지
- ArxivPaperHandler로 자동 다운로드 + DB 저장
- 이후 같은 논문 요청 시 RAG DB에서 바로 조회 가능

### 6. 난이도별 모델 선택

**모델 설정 (configs/model_config.yaml):**
- **easy 모드**: Solar-pro2 (한국어 특화, 비용 절감)
- **hard 모드**: GPT-5 (기술적 정확도, 상세 설명)

**수준 매핑:**
- easy: elementary (8-13세) + beginner (14-22세)
- hard: intermediate (23-30세) + advanced (30세 이상)

---

**문서 버전**: 1.0
**최종 수정일**: 2025-11-07
