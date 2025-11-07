# 이중 요청: RAG 용어집 검색 → 일반 답변 아키텍처

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

사용자가 AI 용어의 기본 정의를 검색한 후, LLM이 추가로 더 자세한 설명이나 보충 정보를 제공하는 경우입니다. 용어집에서 간단한 정의를 제공하고, 이어서 LLM이 심화 내용을 추가합니다.

**실행되는 도구 순서:**
```
1단계: glossary (RAG 용어집 검색)
  ↓ 성공 또는 실패 모두
2단계: general (일반 답변 - LLM 추가 설명)
```

**사용자 요청 예시:**
- "Self-Attention의 시간 복잡도는?"
- "Transformer의 성능은?"
- "BERT의 특징은?"
- "GPT의 장점은?"
- "배치 정규화란?"

---

## 📋 사용자 요청 분석

### 정확한 사용자 질문 예시
```
"Self-Attention의 시간 복잡도는?"
```

### 도구 선택 근거

**패턴 매칭 기반 자동 감지:**

1. **키워드 분석:**
   - `keywords: []` → 특정 필수 키워드 없음
   - `any_of_keywords: ["은?", "는?", "의?", "이란?"]` → 단순 질문 패턴
   - `exclude_keywords: ["논문", "최신", "저장", "검색", "찾", "요약"]` → 복잡한 요청 제외

2. **우선순위:**
   - Priority: 145 (2-도구 패턴)

3. **선택된 도구:**
   - `tools: [glossary, general]`

**결정 로직:**
```python
# src/agent/nodes.py - router_node()
if any(keyword in question for keyword in ["은?", "는?", "의?", "이란?"]):
    if not any(ex in question for ex in ["논문", "최신", "저장", "검색", "찾", "요약"]):
        # glossary → general 파이프라인 설정
        tool_pipeline = ["glossary", "general"]
```

---

## 🔄 도구 자동 전환 및 Fallback

### 전체 흐름

```
사용자: "Self-Attention의 시간 복잡도는?"
↓
[0단계] 라우팅
├─ multi_request_patterns.yaml 패턴 매칭
├─ tool_pipeline: [glossary, general]
└─ pipeline_index: 1 (첫 도구 실행 준비)
↓
[1단계] RAG 용어집 검색 (glossary)
├─ glossary 테이블에서 하이브리드 검색 (SQL + Vector)
├─ 성공 → 기본 정의 발견, tool_result에 저장
└─ 실패 → tool_result: "관련 용어를 찾을 수 없습니다"
↓
[2단계] 일반 답변 (general) ← 항상 실행
├─ 1단계 결과를 참고하여 추가 설명
├─ LLM이 더 자세한 답변 생성
└─ 성공 → final_answers에 저장
```

### 특징: Fallback 없이 순차 실행

이 시나리오는 **Fallback이 아닌 보완적 실행**입니다:

```python
# 1단계 성공 시:
glossary → "Self-Attention은 입력 시퀀스 내의 각 토큰이..."
   ↓
general → "위 정의를 바탕으로 시간 복잡도를 설명하면, O(n²)입니다..."

# 1단계 실패 시:
glossary → "관련 용어를 찾을 수 없습니다"
   ↓
general → "Self-Attention의 시간 복잡도는 O(n²)로, 시퀀스 길이에 제곱으로 증가합니다..."
```

**차이점:**
- **Fallback 패턴 (03번 문서):** 1단계 실패 시에만 2단계 실행
- **보완 패턴 (이 문서):** 1단계 성공/실패와 무관하게 2단계 항상 실행

---

## 📊 단순 흐름 아키텍처

```mermaid
graph TB
    subgraph MainFlow["📋 RAG 용어집 검색 → 일반 답변 파이프라인"]
        direction TB

        subgraph Init["🔸 초기화 & 라우팅"]
            direction LR
            Start([▶️ 시작]) --> A[사용자 질문:<br/>Self-Attention의 시간 복잡도는?]
            A --> B[router_node<br/>패턴 매칭]
            B --> C[Pipeline 설정<br/>2단계 파이프라인]
        end

        subgraph Step1["🔹 1단계: RAG 용어집 검색"]
            direction LR
            D[glossary 실행<br/>PostgreSQL + pgvector] --> E{검색 성공?<br/>결과 있음?}
            E -->|Yes| F[용어 정의 획득<br/>💾 tool_result]
            E -->|No| G[검색 실패<br/>결과 없음]
        end

        subgraph Step2["✨ 2단계: 일반 답변 (추가 설명)"]
            direction LR
            H[general 실행<br/>LLM 지식 기반] --> I{1단계 결과<br/>참고?}
            I -->|있음| J[기본 정의 + 추가 설명<br/>💾 final_answers]
            I -->|없음| K[LLM 자체 설명<br/>💾 final_answers]
        end

        subgraph Output["💡 3단계: 최종 출력"]
            direction LR
            L[난이도별 답변<br/>2개 수준] --> M[UI 렌더링<br/>답변 표시]
            M --> End([✅ 완료])
        end

        %% 단계 간 연결
        Init --> Step1
        Step1 --> Step2
        Step2 --> Output
    end

    %% 메인 워크플로우 배경
    style MainFlow fill:#fffde7,stroke:#f9a825,stroke-width:4px,color:#000

    %% Subgraph 스타일
    style Init fill:#e0f7fa,stroke:#006064,stroke-width:3px,color:#000
    style Step1 fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style Step2 fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000
    style Output fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000

    %% 노드 스타일 (초기화 - 청록 계열)
    style Start fill:#4db6ac,stroke:#00695c,stroke-width:3px,color:#000
    style A fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style B fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style C fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000

    %% 노드 스타일 (1단계 - 보라 계열)
    style D fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style E fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style F fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px,color:#000
    style G fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000

    %% 노드 스타일 (2단계 - 녹색 계열)
    style H fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style I fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style J fill:#66bb6a,stroke:#1b5e20,stroke-width:2px,color:#000
    style K fill:#66bb6a,stroke:#1b5e20,stroke-width:2px,color:#000

    %% 노드 스타일 (출력 - 파랑 계열)
    style L fill:#90caf9,stroke:#1976d2,stroke-width:2px,color:#000
    style M fill:#64b5f6,stroke:#1976d2,stroke-width:2px,color:#000
    style End fill:#66bb6a,stroke:#2e7d32,stroke-width:3px,color:#000

    %% 연결선 스타일 (초기화 - 청록 0~2)
    linkStyle 0 stroke:#006064,stroke-width:2px
    linkStyle 1 stroke:#006064,stroke-width:2px
    linkStyle 2 stroke:#006064,stroke-width:2px

    %% 연결선 스타일 (1단계 - 보라 3~5)
    linkStyle 3 stroke:#7b1fa2,stroke-width:2px
    linkStyle 4 stroke:#7b1fa2,stroke-width:2px
    linkStyle 5 stroke:#7b1fa2,stroke-width:2px

    %% 연결선 스타일 (2단계 - 녹색 6~8)
    linkStyle 6 stroke:#2e7d32,stroke-width:2px
    linkStyle 7 stroke:#2e7d32,stroke-width:2px
    linkStyle 8 stroke:#2e7d32,stroke-width:2px

    %% 연결선 스타일 (출력 - 파랑 9~10)
    linkStyle 9 stroke:#1565c0,stroke-width:2px
    linkStyle 10 stroke:#1565c0,stroke-width:2px

    %% 단계 간 연결 (회색 11~13)
    linkStyle 11 stroke:#616161,stroke-width:3px
    linkStyle 12 stroke:#616161,stroke-width:3px
    linkStyle 13 stroke:#616161,stroke-width:3px
```

---

## 🔧 상세 기능 동작 흐름도

```mermaid
graph TB
    subgraph MainFlow["📋 RAG 용어집 검색 → 일반 답변 상세 흐름"]
        direction TB

        subgraph Init["🔸 초기화"]
            direction LR
            A[main.py] --> B[chat_interface.py]
            B --> C[AgentState 초기화]
            C --> D[router_node 호출]
        end

        subgraph Pattern["🔹 패턴 매칭"]
            direction LR
            E[multi_request_patterns.yaml] --> F{키워드 매칭<br/>단순 질문?}
            F -->|Yes| G[tool_pipeline 설정<br/>2단계 파이프라인]
            F -->|No| H[LLM 라우팅]
            H --> G
        end

        subgraph Glossary["🔺 RAG 용어집 검색"]
            direction LR
            I[glossary_node] --> J[용어 추출<br/>extract_term_from_question]
            J --> K[SQL 검색<br/>glossary 테이블 ILIKE]
            K --> L[Vector 검색<br/>glossary_embeddings]
            L --> M[하이브리드 병합<br/>50% + 50%]
            M --> N{검색 결과<br/>있음?}
            N -->|Yes| O[💾 tool_result<br/>용어 정의]
            N -->|No| P[tool_result:<br/>결과 없음]
        end

        subgraph Router["🔷 Pipeline Router"]
            direction LR
            Q[check_pipeline] --> R[pipeline_router<br/>다음 도구: general]
        end

        subgraph General["✨ 일반 답변"]
            direction LR
            S[general_answer_node] --> T{tool_result<br/>참고?}
            T -->|있음| U[용어 정의 기반<br/>추가 설명]
            T -->|없음| V[LLM 자체 설명<br/>전체 답변]
            U --> W[난이도 매핑<br/>easy 또는 hard]
            V --> W
            W --> X[LLM 호출 2회<br/>Solar-pro2 또는 GPT-5]
            X --> Y[💾 final_answers<br/>2개 수준]
        end

        subgraph Output["💡 최종 출력"]
            direction LR
            Z[chat_interface.py] --> AA[난이도별 답변 표시<br/>elementary + beginner 또는<br/>intermediate + advanced]
            AA --> AB([✅ 완료])
        end

        %% 단계 간 연결
        Init --> Pattern
        Pattern --> Glossary
        Glossary --> Router
        Router --> General
        General --> Output
    end

    %% 메인 워크플로우 배경
    style MainFlow fill:#fffde7,stroke:#f9a825,stroke-width:4px,color:#000

    %% Subgraph 스타일
    style Init fill:#e0f7fa,stroke:#006064,stroke-width:3px,color:#000
    style Pattern fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    style Glossary fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style Router fill:#fce4ec,stroke:#880e4f,stroke-width:3px,color:#000
    style General fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000
    style Output fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#000

    %% 노드 스타일 (초기화 - 청록 계열)
    style A fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style B fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style C fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style D fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000

    %% 노드 스타일 (패턴 - 파랑 계열)
    style E fill:#90caf9,stroke:#1976d2,stroke-width:2px,color:#000
    style F fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style G fill:#64b5f6,stroke:#1976d2,stroke-width:2px,color:#000
    style H fill:#90caf9,stroke:#1976d2,stroke-width:2px,color:#000

    %% 노드 스타일 (용어집 검색 - 보라 계열)
    style I fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style J fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style K fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style L fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style M fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px,color:#000
    style N fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style O fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px,color:#000
    style P fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000

    %% 노드 스타일 (Router - 핑크 계열)
    style Q fill:#f8bbd0,stroke:#880e4f,stroke-width:2px,color:#000
    style R fill:#f48fb1,stroke:#880e4f,stroke-width:2px,color:#000

    %% 노드 스타일 (일반 답변 - 녹색 계열)
    style S fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style T fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style U fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style V fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style W fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style X fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style Y fill:#66bb6a,stroke:#1b5e20,stroke-width:2px,color:#000

    %% 노드 스타일 (출력 - 파랑 계열)
    style Z fill:#90caf9,stroke:#1976d2,stroke-width:2px,color:#000
    style AA fill:#64b5f6,stroke:#1976d2,stroke-width:2px,color:#000
    style AB fill:#66bb6a,stroke:#2e7d32,stroke-width:3px,color:#000

    %% 연결선 스타일 (초기화 0~2)
    linkStyle 0 stroke:#006064,stroke-width:2px
    linkStyle 1 stroke:#006064,stroke-width:2px
    linkStyle 2 stroke:#006064,stroke-width:2px

    %% 연결선 스타일 (패턴 3~6)
    linkStyle 3 stroke:#01579b,stroke-width:2px
    linkStyle 4 stroke:#01579b,stroke-width:2px
    linkStyle 5 stroke:#01579b,stroke-width:2px
    linkStyle 6 stroke:#01579b,stroke-width:2px

    %% 연결선 스타일 (용어집 검색 7~13)
    linkStyle 7 stroke:#7b1fa2,stroke-width:2px
    linkStyle 8 stroke:#7b1fa2,stroke-width:2px
    linkStyle 9 stroke:#7b1fa2,stroke-width:2px
    linkStyle 10 stroke:#7b1fa2,stroke-width:2px
    linkStyle 11 stroke:#7b1fa2,stroke-width:2px
    linkStyle 12 stroke:#7b1fa2,stroke-width:2px
    linkStyle 13 stroke:#7b1fa2,stroke-width:2px

    %% 연결선 스타일 (Router 14)
    linkStyle 14 stroke:#880e4f,stroke-width:2px

    %% 연결선 스타일 (일반 답변 15~19)
    linkStyle 15 stroke:#2e7d32,stroke-width:2px
    linkStyle 16 stroke:#2e7d32,stroke-width:2px
    linkStyle 17 stroke:#2e7d32,stroke-width:2px
    linkStyle 18 stroke:#2e7d32,stroke-width:2px
    linkStyle 19 stroke:#2e7d32,stroke-width:2px

    %% 연결선 스타일 (출력 20~21)
    linkStyle 20 stroke:#1565c0,stroke-width:2px
    linkStyle 21 stroke:#1565c0,stroke-width:2px

    %% 단계 간 연결 (회색 22~26)
    linkStyle 22 stroke:#616161,stroke-width:3px
    linkStyle 23 stroke:#616161,stroke-width:3px
    linkStyle 24 stroke:#616161,stroke-width:3px
    linkStyle 25 stroke:#616161,stroke-width:3px
    linkStyle 26 stroke:#616161,stroke-width:3px
```

---

## 📋 전체 흐름 요약 표

| 단계 | 도구명 | 파일명 | 메서드명 | 동작 설명 | 입력 | 출력 | Fallback | 세션 저장 |
|------|--------|--------|----------|-----------|------|------|----------|----------|
| 0 | 라우팅 | src/agent/nodes.py | router_node() | 패턴 매칭으로 다중 요청 감지 | question: "Self-Attention의 시간 복잡도는?" | tool_pipeline: [glossary, general], tool_choice: glossary | 없음 | tool_pipeline, pipeline_index=1 |
| 1 | RAG 용어집 검색 | src/tools/glossary.py | glossary_node() | PostgreSQL + pgvector 하이브리드 검색 (50% + 50%) | question, difficulty | tool_result: 용어 정의 (성공) 또는 "관련 용어를 찾을 수 없습니다" (실패), final_answers: {elementary, beginner} 또는 {intermediate, advanced} | 없음 | tool_result, final_answers |
| 2 | 일반 답변 | src/tools/general_answer.py | general_answer_node() | LLM 자체 지식 + 1단계 결과 참고하여 추가 설명 | question, difficulty, (tool_result 참고) | final_answers: {elementary, beginner} 또는 {intermediate, advanced} | 없음 | final_answers, final_answer |

**Pipeline Index 변화:**
- 초기: `pipeline_index = 1` (첫 도구 실행 후)
- glossary 실행 → `pipeline_index = 2` (다음 도구 준비)
- general 실행 → `pipeline_index = 2` (종료)

**특징:**
- **Fallback 없음**: 1단계 성공/실패와 무관하게 2단계 항상 실행
- **보완적 실행**: 1단계 결과를 참고하여 2단계가 추가 설명 제공
- **tool_result 참고**: general_answer_node()가 이전 tool_result를 읽어서 컨텍스트 활용 (선택적)

---

## 🔍 동작 설명 (초보 개발자용)

### 1단계: RAG 용어집 검색

**파일:** `src/tools/glossary.py`

**동작:** 03번 문서와 동일 (하이브리드 검색 50% + 50%)

**차이점:**
- 이 시나리오에서는 **검색 실패 시에도 Fallback 없이 바로 2단계 진행**
- `tool_status`는 `success` 또는 `failed`로 설정되지만, 파이프라인은 계속 진행

### 2단계: 일반 답변 (추가 설명)

**파일:** `src/tools/general_answer.py`

**동작 과정:**

1. **이전 결과 참고 (선택적):**
   ```python
   # general_answer_node()
   question = state["question"]
   tool_result = state.get("tool_result", "")  # 1단계 결과 (있으면)

   # 프롬프트 구성 시 tool_result 포함 여부는 구현에 따름
   # 현재는 question만 사용하지만, 확장 가능
   ```

2. **난이도별 모델 선택:**
   ```python
   # configs/model_config.yaml - hybrid_strategy
   if difficulty == "easy":
       provider = "solar"
       model = "solar-pro2"      # 한국어 특화
   elif difficulty == "hard":
       provider = "openai"
       model = "gpt-5"           # 기술적 정확도
   ```

3. **두 수준 답변 생성:**
   ```python
   level_mapping = {
       "easy": ["elementary", "beginner"],
       "hard": ["intermediate", "advanced"]
   }

   for level in ["elementary", "beginner"]:  # easy 모드 예시
       system_prompt = get_tool_prompt("general_answer", level)
       messages = [
           SystemMessage(content=system_prompt),
           HumanMessage(content=question)
       ]
       response = llm.invoke(messages)
       final_answers[level] = response.content
   ```

4. **최종 답변 저장:**
   ```python
   state["final_answers"] = final_answers
   state["final_answer"] = final_answers["beginner"]  # 두 번째 수준
   ```

### 보완적 실행 로직

**1단계 성공 시:**
```python
# glossary_node()
tool_result = "Self-Attention은 입력 시퀀스 내의 각 토큰이..."

# general_answer_node()
# LLM이 tool_result를 참고하여 추가 설명
# (현재 구현은 question만 사용하지만, tool_result 활용 가능)
question = "Self-Attention의 시간 복잡도는?"
# LLM 답변: "Self-Attention의 시간 복잡도는 O(n²)입니다. 각 토큰이 모든 다른 토큰과..."
```

**1단계 실패 시:**
```python
# glossary_node()
tool_result = "관련 용어를 찾을 수 없습니다"

# general_answer_node()
# LLM이 자체 지식으로 전체 답변
question = "Self-Attention의 시간 복잡도는?"
# LLM 답변: "Self-Attention의 시간 복잡도는 O(n²)입니다. 시퀀스 길이 n에 대해 각 토큰이..."
```

---

## 💡 실행 예시

### 예시 1: 용어집 검색 성공 + 일반 답변 추가

**입력:**
```
사용자: "Self-Attention의 시간 복잡도는?"
난이도: easy
```

**1단계 실행 (glossary):**
```markdown
## 용어집 검색 결과

### 1. Self-Attention
- **카테고리**: Attention Mechanism
- **난이도**: intermediate
- **유사도 점수(낮을수록 유사)**: 0.1523
- **연관 용어**: Transformer, Multi-Head Attention, Query-Key-Value
- **정의**: 입력 시퀀스 내의 각 토큰이 다른 모든 토큰과의 관계를 학습하는 메커니즘

Self-Attention은 Transformer 아키텍처의 핵심으로, 각 토큰이 시퀀스 내 다른 토큰들과의
관련성을 계산하여 가중치를 부여합니다.
```

**2단계 실행 (general):**
```python
# Solar-pro2 모델로 추가 설명 생성
question = "Self-Attention의 시간 복잡도는?"

final_answers = {
    "elementary": """Self-Attention의 시간 복잡도는 O(n²)입니다.

    시퀀스 길이가 n일 때, 각 토큰이 다른 모든 토큰과 비교해야 하므로
    n × n번의 계산이 필요합니다.""",

    "beginner": """Self-Attention의 시간 복잡도는 O(n²)입니다.

    위 용어 정의에서 설명했듯이, Self-Attention은 각 토큰이 다른 모든 토큰과의
    관계를 학습합니다. 시퀀스 길이가 n이면:
    - 각 토큰마다 n개의 다른 토큰과 계산
    - 총 n개 토큰 × n개 비교 = O(n²)

    예를 들어, 문장이 10개 단어면 10×10=100번,
    100개 단어면 100×100=10,000번 계산합니다."""
}
```

**최종 출력:**
```
[elementary 답변]
Self-Attention의 시간 복잡도는 O(n²)입니다.

시퀀스 길이가 n일 때, 각 토큰이 다른 모든 토큰과 비교해야 하므로
n × n번의 계산이 필요합니다.

[beginner 답변]
Self-Attention의 시간 복잡도는 O(n²)입니다.

위 용어 정의에서 설명했듯이, Self-Attention은 각 토큰이 다른 모든 토큰과의
관계를 학습합니다. 시퀀스 길이가 n이면:
- 각 토큰마다 n개의 다른 토큰과 계산
- 총 n개 토큰 × n개 비교 = O(n²)

예를 들어, 문장이 10개 단어면 10×10=100번,
100개 단어면 100×100=10,000번 계산합니다.
```

### 예시 2: 용어집 검색 실패 + 일반 답변으로 보완

**입력:**
```
사용자: "XYZ알고리즘의 특징은?"
난이도: easy
```

**1단계 실행 (glossary):**
```
검색 결과: "관련 용어를 찾을 수 없습니다"
tool_result: "관련 용어를 찾을 수 없습니다"
```

**2단계 실행 (general):**
```python
# Solar-pro2 모델로 전체 답변 생성
question = "XYZ알고리즘의 특징은?"

final_answers = {
    "elementary": """XYZ알고리즘은 데이터를 효율적으로 처리하는 방법입니다.

    주요 특징:
    - 빠른 처리 속도
    - 적은 메모리 사용
    - 다양한 데이터 타입 지원""",

    "beginner": """XYZ알고리즘의 주요 특징은 다음과 같습니다:

    1. 시간 복잡도: O(n log n)으로 효율적입니다
    2. 공간 복잡도: 추가 메모리를 최소화합니다
    3. 안정성: 동일한 값의 순서를 유지합니다
    4. 적용 범위: 다양한 데이터 구조에 적용 가능합니다"""
}
```

**최종 출력:**
```
[elementary 답변]
XYZ알고리즘은 데이터를 효율적으로 처리하는 방법입니다.

주요 특징:
- 빠른 처리 속도
- 적은 메모리 사용
- 다양한 데이터 타입 지원

[beginner 답변]
XYZ알고리즘의 주요 특징은 다음과 같습니다:

1. 시간 복잡도: O(n log n)으로 효율적입니다
2. 공간 복잡도: 추가 메모리를 최소화합니다
3. 안정성: 동일한 값의 순서를 유지합니다
4. 적용 범위: 다양한 데이터 구조에 적용 가능합니다
```

### 예시 3: Hard 모드 - 기술적 상세 설명

**입력:**
```
사용자: "Transformer의 성능은?"
난이도: hard
```

**1단계 실행 (glossary):**
```markdown
## 용어집 검색 결과

### 1. Transformer
- **카테고리**: Neural Network Architecture
- **난이도**: advanced
- **정의**: Self-Attention 메커니즘을 사용하는 sequence-to-sequence 모델

Transformer는 2017년 "Attention Is All You Need" 논문에서 제안된
Self-Attention 기반 아키텍처입니다.
```

**2단계 실행 (general):**
```python
# GPT-5 모델로 기술적 상세 설명 생성
level_mapping["hard"] = ["intermediate", "advanced"]

final_answers = {
    "intermediate": """Transformer의 성능은 다음과 같은 측면에서 우수합니다:

    1. 병렬 처리: RNN과 달리 시퀀스를 병렬로 처리하여 학습 속도 향상
    2. 장거리 의존성: Self-Attention으로 먼 거리의 토큰 관계도 효과적으로 학습
    3. 범용성: NLP, Vision, Multi-modal 등 다양한 도메인에 적용 가능

    주요 벤치마크:
    - WMT 2014 EN-DE: BLEU 28.4 (당시 SOTA)
    - WMT 2014 EN-FR: BLEU 41.0""",

    "advanced": """Transformer 아키텍처의 성능 특성:

    **계산 복잡도:**
    - Self-Attention: O(n²·d) (시퀀스 길이 n, 차원 d)
    - Feed-Forward: O(n·d·d_ff) (d_ff는 hidden dimension)

    **성능 지표:**
    1. 번역 품질 (BLEU):
       - WMT 2014 EN-DE: 28.4 (이전 SOTA 대비 +2.0)
       - WMT 2014 EN-FR: 41.0 (단일 모델 SOTA)

    2. 학습 효율성:
       - 8 P100 GPU에서 3.5일 (Base 모델)
       - RNN/LSTM 대비 5~10배 빠른 학습

    3. 파라미터 효율성:
       - Base: 65M parameters
       - Big: 213M parameters
       - 파라미터 대비 성능이 RNN보다 우수

    **장점:**
    - 병렬화 가능: GPU 활용도 극대화
    - 해석 가능성: Attention weight 시각화
    - 전이 학습: Pre-training + Fine-tuning 전략

    **한계:**
    - 시퀀스 길이에 제곱으로 증가하는 메모리
    - 긴 시퀀스 처리 시 계산 비용 증가"""
}
```

**최종 출력:**
```
[intermediate 답변]
Transformer의 성능은 다음과 같은 측면에서 우수합니다:

1. 병렬 처리: RNN과 달리 시퀀스를 병렬로 처리하여 학습 속도 향상
2. 장거리 의존성: Self-Attention으로 먼 거리의 토큰 관계도 효과적으로 학습
3. 범용성: NLP, Vision, Multi-modal 등 다양한 도메인에 적용 가능

주요 벤치마크:
- WMT 2014 EN-DE: BLEU 28.4 (당시 SOTA)
- WMT 2014 EN-FR: BLEU 41.0

[advanced 답변]
Transformer 아키텍처의 성능 특성:

**계산 복잡도:**
- Self-Attention: O(n²·d) (시퀀스 길이 n, 차원 d)
- Feed-Forward: O(n·d·d_ff) (d_ff는 hidden dimension)

**성능 지표:**
1. 번역 품질 (BLEU):
   - WMT 2014 EN-DE: 28.4 (이전 SOTA 대비 +2.0)
   - WMT 2014 EN-FR: 41.0 (단일 모델 SOTA)

2. 학습 효율성:
   - 8 P100 GPU에서 3.5일 (Base 모델)
   - RNN/LSTM 대비 5~10배 빠른 학습
...
```

---

## 🎯 핵심 포인트

### 1. Fallback vs 보완적 실행

**Fallback 패턴 (03번 문서):**
```
glossary 성공 → save_file
glossary 실패 → general → save_file
```

**보완 패턴 (이 문서):**
```
glossary 성공/실패 → general (항상 실행)
```

**차이점:**
| 구분 | Fallback 패턴 | 보완 패턴 |
|------|---------------|-----------|
| 2단계 실행 조건 | 1단계 실패 시에만 | 항상 실행 |
| 목적 | 대체 수단 제공 | 추가 설명 제공 |
| tool_status 영향 | 있음 (failed일 때만) | 없음 (무시) |
| 결과 결합 | 대체 (OR) | 보완 (AND) |

### 2. Pipeline Router 동작

```python
# src/agent/graph.py - pipeline_router()
def pipeline_router(state: AgentState, exp_manager=None):
    tool_pipeline = state.get("tool_pipeline", [])
    pipeline_index = state.get("pipeline_index", 0)

    # 보완 패턴: tool_status와 무관하게 다음 도구 실행
    if pipeline_index < len(tool_pipeline):
        next_tool = tool_pipeline[pipeline_index]
        state["tool_choice"] = next_tool
        state["pipeline_index"] = pipeline_index + 1

    return state
```

**Fallback 패턴과의 차이:**
- Fallback: `check_pipeline_or_fallback()`에서 `tool_status` 확인
- 보완: `pipeline_router()`에서 무조건 다음 도구로 진행

### 3. 질문 패턴 매칭

```yaml
# configs/multi_request_patterns.yaml
- keywords: []
  any_of_keywords: ["은?", "는?", "의?", "이란?"]
  exclude_keywords: ["논문", "최신", "저장", "검색", "찾", "요약"]
  tools: [glossary, general]
  priority: 145
```

**매칭되는 질문:**
- "Self-Attention의 시간 복잡도는?"
- "Transformer의 성능은?"
- "BERT의 특징은?"
- "배치 정규화란?"

**매칭되지 않는 질문:**
- "Transformer 논문 찾아줘" (논문 키워드)
- "최신 AI 동향은?" (최신 키워드)
- "RAG 저장해줘" (저장 키워드)

### 4. 난이도별 답변 레벨

```python
# src/tools/general_answer.py
level_mapping = {
    "easy": ["elementary", "beginner"],
    "hard": ["intermediate", "advanced"]
}
```

**Easy 모드 (Solar-pro2):**
- `elementary`: 초등학생 수준, 일상 용어로 설명
- `beginner`: 입문자 수준, 기본 개념 설명

**Hard 모드 (GPT-5):**
- `intermediate`: 중급자 수준, 기술적 용어 사용
- `advanced`: 전문가 수준, 수식/벤치마크 포함

### 5. 하이브리드 검색 가중치

```yaml
# configs/model_config.yaml
rag:
  hybrid_search:
    tool_specific_weights:
      glossary:
        vector_weight: 0.5    # 50% (의미 유사도)
        keyword_weight: 0.5   # 50% (정확한 단어 매칭)
```

**용어집 검색 특성:**
- 정확한 용어명 매칭 중요 → 키워드 50%
- 동의어/유사 표현 탐색 → 벡터 50%

### 6. UI 렌더링

```python
# chat_interface.py
final_answers = state["final_answers"]
# {
#     "elementary": "...",
#     "beginner": "..."
# }

# UI에서 두 수준 답변 모두 표시
st.markdown("### Elementary 수준")
st.write(final_answers["elementary"])

st.markdown("### Beginner 수준")
st.write(final_answers["beginner"])
```

---

**작성일**: 2025-11-07
**버전**: 1.0
