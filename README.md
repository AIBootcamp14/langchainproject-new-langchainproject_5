# 논문 리뷰 챗봇 (AI Agent + RAG)

> 🤖 **LangGraph 기반 멀티 에이전트 시스템**을 활용한 논문 검색 및 분석 챗봇
>
> AI Agent와 RAG(Retrieval Augmented Generation) 기술을 결합하여 사용자의 다양한 질문에 지능적으로 응답

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.59-green.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41.1-red.svg)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-0.8.0-orange.svg)](https://github.com/pgvector/pgvector)

</div>

---

## 📋 목차



---

## 🎯 프로젝트 개요

### 배경

AI 연구가 빠르게 발전하면서 arXiv 등의 플랫폼에 매일 수백 편의 논문이 게재되고 있습니다. 연구자와 학생들은 방대한 논문 속에서 필요한 정보를 찾고, 이해하는 데 많은 시간을 소비합니다.

### 목적

본 프로젝트는 **LangGraph 기반 AI Agent**와 **RAG 기술**을 결합하여 사용자 질문의 의도를 자동으로 파악하고, 적절한 도구를 선택하여 정확한 답변을 제공하는 지능형 챗봇을 구현합니다.

### 핵심 가치

- 🎯 **자동 의도 파악**: 사용자 질문을 분석하여 7가지 도구 중 최적의 도구를 자동 선택
- 🔄 **멀티 턴 대화**: 대화 맥락을 유지하며 자연스러운 연속 질문 처리
- 📊 **난이도 선택**: Easy/Hard 모드로 사용자 수준에 맞는 답변 제공
- 🚀 **고성능 검색**: PostgreSQL + pgvector를 활용한 빠른 벡터 유사도 검색
- 💾 **실험 관리**: 모든 대화와 실험 결과를 체계적으로 로깅 및 저장

---

## 👥 팀 소개

### 연결의 민족

#### 👨‍💻 팀 연락처

- **팀명**: 연결의 민족
- **팀장**: 최현화
- **프로젝트 기간**: 2025.10.28 ~ 2025.11.06
- **GitHub**: [Team Repository](https://github.com/AIBootcamp14/langchainproject-new-langchainproject_5)

| 이름 | 역할 | 담당 업무 |
|------|------|-----------|
| **최현화** | Project Lead | 프로젝트 총괄, 로깅 시스템, AI Agent 시스템, 평가 시스템, Web Search Tool, Summarize Tool, Save File Tool, Streamlit UI 개발 |
| **박재홍** | Database & Data Pipeline | 데이터베이스 설계 및 구축, 데이터 수집/저장, Embedding 처리, Vector DB 구축, Streamlit UI 개발 |
| **신준엽** | RAG & Query Systems | RAG 시스템 구현, 논문 검색 Tool, 용어 검색 Tool, Text-to-SQL Tool 개발 |
| **임예슬** | Prompt Engineering & QA | 프롬프트 엔지니어링, 시스템 최적화, QA 테스트 수행 |

---

## 🏗️ 시스템 아키텍처

### 전체 워크플로우

```mermaid
graph TB
    subgraph MainFlow["📋 논문 리뷰 챗봇 워크플로우"]
        direction TB

        subgraph Input["🔸 입력 처리"]
            direction LR
            Start([▶️ 사용자 질문]) --> A[질문 분석]
            A --> B[난이도 선택<br/>Easy/Hard]
            B --> C[대화 이력 로드]
            C --> D[입력 처리 완료]
        end

        subgraph Routing["🔹 라우팅 & 도구 선택"]
            direction LR
            E[Router Node] --> F{의도 파악}
            F -->|일반 질문| G[General Tool]
            F -->|논문 검색| H[Search Paper]
            F -->|용어 검색| I[Glossary]
            F -->|웹 검색| J[Web Search]
            F -->|요약| K[Summarize]
            F -->|DB 조회| L[Text2SQL]
            F -->|저장| M[Save File]
        end

        subgraph Execution["🔺 도구 실행"]
            direction LR
            N[선택된 도구] --> O[RAG/LLM 처리]
            O --> P[결과 생성]
            P --> Q[💾 로그 저장]
        end

        subgraph Output["🔶 출력 & 평가"]
            direction LR
            R[최종 답변 생성] --> S[Streamlit UI 표시]
            S --> T[평가 수행<br/>LLM-as-a-Judge]
            T --> U[💾 결과 저장<br/>✅ 완료]
        end

        %% 단계 간 연결
        Input --> Routing
        Routing --> Execution
        Execution --> Output
    end

    %% 메인 워크플로우 배경
    style MainFlow fill:#fffde7,stroke:#f9a825,stroke-width:4px,color:#000

    %% Subgraph 스타일
    style Input fill:#e0f7fa,stroke:#006064,stroke-width:3px,color:#000
    style Routing fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style Execution fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000
    style Output fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000

    %% 노드 스타일 (입력 - 청록 계열)
    style Start fill:#4db6ac,stroke:#00695c,stroke-width:3px,color:#000
    style A fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style B fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style C fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000
    style D fill:#4dd0e1,stroke:#006064,stroke-width:2px,color:#000

    %% 노드 스타일 (라우팅 - 보라 계열)
    style E fill:#ce93d8,stroke:#6a1b9a,stroke-width:2px,color:#000
    style F fill:#ce93d8,stroke:#7b1fa2,stroke-width:2px,color:#000
    style G fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style H fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style I fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style J fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style K fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style L fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000
    style M fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#000

    %% 노드 스타일 (실행 - 녹색 계열)
    style N fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style O fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style P fill:#81c784,stroke:#2e7d32,stroke-width:2px,color:#000
    style Q fill:#66bb6a,stroke:#1b5e20,stroke-width:2px,color:#000

    %% 노드 스타일 (출력 - 주황 계열)
    style R fill:#ffb74d,stroke:#e65100,stroke-width:2px,color:#000
    style S fill:#ffb74d,stroke:#e65100,stroke-width:2px,color:#000
    style T fill:#ffb74d,stroke:#e65100,stroke-width:2px,color:#000
    style U fill:#ffa726,stroke:#ef6c00,stroke-width:2px,color:#000

    %% 연결선 스타일 (입력 0~3)
    linkStyle 0 stroke:#006064,stroke-width:2px
    linkStyle 1 stroke:#006064,stroke-width:2px
    linkStyle 2 stroke:#006064,stroke-width:2px
    linkStyle 3 stroke:#006064,stroke-width:2px

    %% 연결선 스타일 (라우팅 4~11)
    linkStyle 4 stroke:#7b1fa2,stroke-width:2px
    linkStyle 5 stroke:#7b1fa2,stroke-width:2px
    linkStyle 6 stroke:#7b1fa2,stroke-width:2px
    linkStyle 7 stroke:#7b1fa2,stroke-width:2px
    linkStyle 8 stroke:#7b1fa2,stroke-width:2px
    linkStyle 9 stroke:#7b1fa2,stroke-width:2px
    linkStyle 10 stroke:#7b1fa2,stroke-width:2px
    linkStyle 11 stroke:#7b1fa2,stroke-width:2px

    %% 연결선 스타일 (실행 12~14)
    linkStyle 12 stroke:#2e7d32,stroke-width:2px
    linkStyle 13 stroke:#2e7d32,stroke-width:2px
    linkStyle 14 stroke:#2e7d32,stroke-width:2px

    %% 연결선 스타일 (출력 15~17)
    linkStyle 15 stroke:#e65100,stroke-width:2px
    linkStyle 16 stroke:#e65100,stroke-width:2px
    linkStyle 17 stroke:#e65100,stroke-width:2px

    %% 단계 간 연결 (회색 18~20)
    linkStyle 18 stroke:#616161,stroke-width:3px
    linkStyle 19 stroke:#616161,stroke-width:3px
    linkStyle 20 stroke:#616161,stroke-width:3px
```



---

## 🚀 주요 기능

### 1. 핵심 기능

| 기능 | 설명 | 구현 여부 |
|------|------|-----------|
| **🤖 AI Agent 시스템** | LangGraph StateGraph 기반 멀티 에이전트 | ✅ |
| **📚 논문 검색** | arXiv 논문 검색 및 자동 저장 | ✅ |
| **📖 용어 검색** | 논문 내 용어 설명 검색 (RAG) | ✅ |
| **🌐 웹 검색** | Tavily API를 활용한 실시간 웹 검색 | ✅ |
| **📝 요약 생성** | 논문/텍스트 요약 및 핵심 내용 추출 | ✅ |
| **🗄️ Text-to-SQL** | 자연어를 SQL 쿼리로 변환 (보안 검증 포함) | ✅ |
| **💾 파일 저장** | 대화 내용 마크다운 파일로 저장 | ✅ |

### 2. 선택 기능

| 기능 | 설명 | 구현 여부 |
|------|------|-----------|
| **🔄 멀티 턴 대화** | 대화 맥락 유지 및 연속 질문 처리 | ✅ |
| **📊 난이도 조절** | Easy/Hard 모드로 답변 수준 조절 | ✅ |
| **🎨 Streamlit UI** | ChatGPT 스타일 웹 인터페이스 | ✅ |
| **📈 성능 평가** | LLM-as-a-Judge 평가 시스템 | ✅ |
| **🔐 사용자 인증** | 로그인/로그아웃 기능 | ✅ |

### 3. 고급 기능

- **🔄 Fallback Chain**: 도구 실행 실패 시 자동으로 다른 도구로 전환
- **🧩 멀티 요청 감지**: 하나의 질문에 여러 요청이 포함된 경우 자동 분리 처리 (2025-11-04 구현)
- **📊 Connection Pooling**: PostgreSQL 연결 풀링으로 성능 최적화 (min=1, max=10)
- **🚀 IVFFlat Index**: pgvector 인덱스를 활용한 고속 유사도 검색
- **🔍 MMR Search**: Maximal Marginal Relevance를 통한 다양성 있는 검색 결과
- **🔄 MultiQueryRetriever**: LLM을 활용한 쿼리 확장 및 검색 최적화
- **💾 LocalStorage 연동**: 채팅 세션 데이터 로컬 저장 및 복원
- **🌙 다크 모드**: 사용자 선호도에 따른 테마 전환

---

## 🛠️ 기술 스택

### AI & LLM

| 기술 | 버전 | 용도 |
|------|------|------|
| **OpenAI GPT-5** | gpt-4o | Hard 모드 답변 생성 (고난이도 질문) |
| **Solar Pro2** | solar-pro-preview-240910 | Easy 모드 답변 생성 (일반 질문) |
| **LangChain** | 0.3.13 | LLM 체이닝 및 프롬프트 관리 |
| **LangGraph** | 0.2.59 | AI Agent StateGraph 구현 |
| **OpenAI Embeddings** | text-embedding-3-small | 텍스트 임베딩 (1536 차원) |

### Database & Vector Store

| 기술 | 버전 | 용도 |
|------|------|------|
| **PostgreSQL** | 16+ | RDBMS (논문, 용어, 로그 데이터) |
| **pgvector** | 0.8.0 | 벡터 유사도 검색 (IVFFlat 인덱스) |
| **psycopg2** | 2.9.10 | PostgreSQL 드라이버 |

### Web Framework & UI

| 기술 | 버전 | 용도 |
|------|------|------|
| **Streamlit** | 1.41.1 | 웹 UI 프레임워크 |
| **streamlit-javascript** | 0.1.5 | JavaScript 연동 (LocalStorage) |

### Data Processing

| 기술 | 버전 | 용도 |
|------|------|------|
| **pandas** | 2.2.3 | 데이터 처리 |
| **PyPDF** | 5.1.0 | PDF 텍스트 추출 |
| **arxiv** | 2.1.3 | arXiv API 클라이언트 |

### External APIs

| API | 용도 |
|-----|------|
| **Tavily Search API** | 웹 검색 기능 |
| **arXiv API** | 논문 메타데이터 및 PDF 다운로드 |

### Development Tools

| 도구 | 용도 |
|------|------|
| **Python** | 3.11 |
| **YAML** | 설정 파일 관리 |
| **tqdm** | 진행 상황 표시 |

---

## ✅ 구현 완료 기능

### 1. 로깅 시스템 (Logger)

**파일 위치**: `src/utils/logger.py:1`

**주요 기능**:
- 📝 타임스탬프 자동 추가 로깅
- 💾 파일 + 콘솔 이중 출력
- 🔄 stdout/stderr 리다이렉션
- 📊 tqdm 프로그레스 바 통합

**디렉토리 구조**:
```
experiments/
└── {날짜}/
    └── {날짜}_{시간}_session_XXX/
        ├── chatbot.log        # 메인 로그
        ├── config.yaml        # 실험 설정
        └── results/           # 실험 결과
```

**구현 코드 예시**:
```python
class Logger:
    def __init__(self, log_path: Path, print_also: bool = True)
    def write(self, message: str, print_also: bool = True, print_error: bool = False)
    def flush(self)
    def close(self)
    def start_redirect(self)  # stdout/stderr 리다이렉션 시작
    def stop_redirect(self)   # 리다이렉션 종료
    def tqdm(self, *args, **kwargs)  # tqdm 래퍼
```

---

### 2. 데이터베이스 시스템 (PostgreSQL + pgvector)



---

### 3. AI Agent 시스템 (LangGraph)



---

### 4. 도구 시스템 (7가지 Tools)



---

### 5. RAG 시스템



---

### 6. Streamlit UI 시스템



---

### 7. 평가 시스템 (LLM-as-a-Judge)

---

### 8. 프롬프트 엔지니어링


### 2. 설치

```bash
# 리포지토리 클론
git clone https://github.com/AIBootcamp14/langchainproject-new-langchainproject_5.git
cd langchainproject-new-langchainproject_5

# 가상환경 생성 및 활성화
pyenv activate langchain_py3_11_9

# 의존성 설치
pip install -r requirements.txt

# PostgreSQL pgvector extension 설치 및 데이터 수집 파이프라인 실행
# docs/usage/데이터베이스_설치_및_설정_가이드.md 순차적으로 1~8단계까지 실행

# 논문 리뷰 챗봇 실행
python main.py

```

### 3. 환경 설정

`.env` 파일 생성:
```bash
# OpenAI API
OPENAI_API_KEY=sk-...

# Upstage API (Solar Pro2)
UPSTAGE_API_KEY=up_...

# Tavily API (웹 검색)
TAVILY_API_KEY=tvly-...

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=paper_chatbot
DB_USER=postgres
DB_PASSWORD=your_password

# Streamlit
STREAMLIT_SERVER_PORT=8501
```

`configs/db_config.yaml` 설정:
```yaml
postgresql:
  host: localhost
  port: 5432
  database: paper_chatbot
  user: postgres
  password: your_password

connection_pool:
  min_connections: 1
  max_connections: 10

vector_store:
  embedding_model: text-embedding-3-small
  embedding_dimensions: 1536
  collection_prefix: chatbot
```

### 4. 실행

**Streamlit UI 실행**:
```bash
streamlit run ui/app.py
```

브라우저에서 `http://localhost:8501` 접속

**CLI 실행** (테스트용):
```bash
python main.py --question "Transformer 모델 설명해줘" --difficulty easy
```

---

## 📁 프로젝트 구조

```
```

---

## 🗄️ 데이터베이스 설계

### ERD (Entity Relationship Diagram)


---

## ⚡ 성능 최적화


---

## 📊 주요 성과

- ✅ **7가지 AI Agent 도구** 구현 완료
- ✅ **LangGraph StateGraph** 기반 멀티 에이전트 시스템
- ✅ **PostgreSQL + pgvector** 단일 DB 통합
- ✅ **Streamlit UI** ChatGPT 스타일 웹 인터페이스
- ✅ **LLM-as-a-Judge** 자동 평가 시스템
- ✅ **Fallback Chain** 오류 복구 메커니즘
- ✅ **멀티 턴 대화** 맥락 유지 기능
- ✅ **난이도 조절** Easy/Hard 모드
- ✅ **Connection Pooling** 성능 최적화
- ✅ **IVFFlat 인덱스** 고속 벡터 검색

---

## 📚 참고 자료

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

---

<div align="center">

**작성자**: 최현화
**작성일**: 2025-11-07
**버전**: 1.0
**Made with ❤️ by 연결의 민족**

</div>
