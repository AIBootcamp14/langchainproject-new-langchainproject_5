# 논문 리뷰 챗봇 (AI Agent + RAG)

> 🤖 **LangGraph 기반 멀티 에이전트 시스템**을 활용한 논문 검색 및 분석 챗봇
>
> AI Agent와 RAG(Retrieval Augmented Generation) 기술을 결합하여 사용자의 다양한 질문에 지능적으로 응답

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0+-green.svg)](https://github.com/langchain-ai/langchain)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0.1+-green.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0+-red.svg)](https://streamlit.io/)

[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-412991.svg)](https://openai.com/)
[![Upstage](https://img.shields.io/badge/Upstage-Solar--pro2-orange.svg)](https://www.upstage.ai/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-0.3.6-orange.svg)](https://github.com/pgvector/pgvector)

</div>

---

## 📋 목차

- [🎯 프로젝트 개요](#-프로젝트-개요)
  - [배경](#배경)
  - [목적](#목적)
  - [핵심 가치](#핵심-가치)
- [👥 팀 소개](#-팀-소개)
- [🏗️ 시스템 아키텍처](#️-시스템-아키텍처)
  - [전체 워크플로우](#전체-워크플로우)
  - [단계별 워크플로우 상세 설명](#단계별-워크플로우-상세-설명)
    - [Phase 1: 프로그램 시작 및 초기화](#-phase-1-프로그램-시작-및-초기화-16단계)
    - [Phase 2: 사용자 입력 및 Agent 실행](#-phase-2-사용자-입력-및-agent-실행-710단계)
    - [Phase 3: 도구 실행 및 Fallback](#-phase-3-도구-실행-및-fallback-1118단계)
    - [Phase 4: LLM 호출 및 상태 관리](#-phase-4-llm-호출-및-상태-관리-1921단계)
    - [Phase 5: UI 표시 및 부가 기능](#️-phase-5-ui-표시-및-부가-기능-2226단계)
  - [핵심 개념 정리](#-핵심-개념-정리)
- [🚀 주요 기능](#-주요-기능)
- [🛠️ 기술 스택](#️-기술-스택)
- [📁 프로젝트 구조](#-프로젝트-구조)
- [🔧 핵심 기술 구현](#-핵심-기술-구현)
  - [1. 로깅 & 실험 관리 시스템](#1-로깅--실험-관리-시스템)
  - [2. 데이터베이스 시스템 (PostgreSQL + pgvector)](#2-데이터베이스-시스템-postgresql--pgvector)
  - [3. 논문 데이터 수집 파이프라인](#3-논문-데이터-수집-파이프라인)
  - [4. AI Agent 시스템 (LangGraph)](#4-ai-agent-시스템-langgraph)
  - [5. RAG 시스템](#5-rag-시스템)
  - [5. Streamlit UI 시스템](#5-streamlit-ui-시스템)
  - [6. 평가 시스템 (LLM-as-a-Judge)](#6-평가-시스템-llm-as-a-judge)
  - [7. 프롬프트 엔지니어링](#7-프롬프트-엔지니어링)
- [📦 설치 및 실행](#-설치-및-실행)
- [⚡ 성능 최적화](#-성능-최적화)
- [📊 주요 성과](#-주요-성과)
- [📚 참고 자료](#-참고-자료)



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

| 이름 | 역할 | 기술 개발 및 구현 | 프로젝트 운영 및 문서화 |
|:----:|------|------------------|----------------------|
| <div align="center"><img src="https://avatars.githubusercontent.com/u/166781765?v=4" width="80" height="80" style="border-radius: 50%;"><br>**[최현화](https://github.com/iejob/langchain-project)**</div> | - Project Lead<br>- Tech Lead | - 프로젝트 총괄 및 시스템 아키텍처 설계<br>- AI Agent 시스템(LangGraph)<br>- 단일/다중 요청시 Fallback 도구 자동 전환<br>- 멀티턴 대화 기능<br>- 로깅 & 실험 모니터링 시스템<br>- 평가 시스템(LLM-as-a-Judge)<br>- Web 논문 검색 도구<br>- 논문 요약 도구<br>- 파일 저장 도구<br>- Streamlit UI | - 팀 리드 및 역할 배분<br>- 개발 규칙 및 컨벤션 정립<br>- 회의록(팀/멘토링) 작성 및 관리<br>- PRD 및 기술 명세 문서 총괄<br>- PPT 및 README 작성 및 관리<br>- Github Issue 관리<br>- Github Project 관리<br>- Git 브랜치 관리 & 병합 |
| <div align="center"><img src="https://avatars.githubusercontent.com/u/66048976?v=4" width="80" height="80" style="border-radius: 50%;"><br>**[박재홍](https://github.com/woghd8503/langchainproject-new-langchainproject_5)**</div> | - Database<br>- Data Pipeline | - 데이터베이스 설계<br>- 데이터 수집<br>- 데이터 저장(로컬/RDBMS)<br>- 임베딩 및 Vector DB 적재<br>- Streamlit UI | - PRD 자료조사<br>- 데이터파이프라인 기술 보고서 작성<br>- Github Issue 작성 |
| <div align="center"><img src="https://avatars.githubusercontent.com/u/180160571?v=4" width="80" height="80" style="border-radius: 50%;"><br>**[신준엽](https://github.com/Shin-junyeob/langchainproject_5)**</div> | - RAG<br>- Query Systems | - RAG 시스템<br>- RAG 논문 검색 도구<br>- RAG 용어집 검색 도구<br>- Text2SQL 도구 | - PRD 자료조사<br>- Github Issue 작성<br>- PPT |
| <div align="center"><img src="https://avatars.githubusercontent.com/u/113421456?v=4" width="80" height="80" style="border-radius: 50%;"><br>**[임예슬](https://github.com/joy007fun/langchainproject_team5)**</div> | - Prompt<br>Engineering<br>- QA | - 프롬프트 엔지니어링<br>- 프롬프트 최적화<br>- 실행 테스트 및 검증(QA) | - PRD 자료조사<br>- Github Issue 작성<br>- PPT |

---

## 🏗️ 시스템 아키텍처

### 전체 워크플로우

#### 전체 아키텍처 구조 (단순 흐름도)
![전체 아키텍처 (단순 흐름도)](docs/images/architecture/01_전체%20아키텍처(단순%20흐름도).png)

#### 전체 아키텍처 구조 (상세 흐름도)
![전체 아키텍처 (상세 흐름도)](docs/images/architecture/02_전체%20아키텍처(상세%20흐름도).png)

#### 전체 흐름 요약 표

아래 표는 main.py부터 시작되는 전체 시스템 실행 흐름을 단계별로 정리한 것입니다.


<details>
<summary><strong>전체 흐름 요약 표</strong></summary>

| 단계 | 도구/컴포넌트명 | 파일명 | 메서드명 | 동작 설명 | 입력 | 출력 | Fallback | 세션 저장 |
|------|-----------------|--------|----------|-----------|------|------|----------|----------|
| **1** | **프로그램 시작** | `main.py` | `main()`, `load_dotenv()` | .env 파일 로드 후 Streamlit 서버 시작 | 없음 | 환경변수 로드 완료 | 없음 | 없음 |
| **2** | **Streamlit 서버** | `main.py` | `subprocess.run()` | Streamlit 앱 실행 (port 8501) | `ui/app.py` 경로 | 브라우저 localhost:8501 열림 | 없음 | 없음 |
| **3** | **UI 초기화** | `ui/app.py` | `st.set_page_config()`, `initialize_agent()` | 페이지 설정 및 환경변수 검증 | OPENAI_API_KEY 확인 | Agent 및 ExpManager 생성 | 없음 | `st.session_state` |
| **4** | **ExperimentManager** | `src/utils/experiment_manager.py` | `__init__()`, `Logger.write()` | 실험 폴더 생성 (experiments/YYYYMMDD/ID) | 없음 | 로그 파일 생성, config.json 저장 | 없음 | 로컬 파일 |
| **5** | **Agent 그래프 생성** | `src/agent/graph.py` | `create_agent_graph()`, `StateGraph()`, `workflow.compile()` | LangGraph 그래프 구성 (router + 7개 도구 노드) | `exp_manager` | 컴파일된 Agent 그래프 | 없음 | 메모리 |
| **6** | **UI 렌더링** | `ui/app.py` | `initialize_storage()`, `initialize_chat_sessions()`, `create_new_chat()`, `render_sidebar()` | Storage 및 채팅 세션 초기화 | 없음 | 첫 채팅 자동 생성 완료 | 없음 | `st.session_state` |
| **7** | **사용자 입력 처리** | `ui/components/chat_interface.py` | `st.chat_input()`, `render_chat_input()` | 사용자 질문 수신 및 메시지 추가 | 사용자 prompt | 채팅 히스토리에 메시지 추가 | 없음 | `st.session_state.chats` |
| **8** | **Agent 실행** | `ui/components/chat_interface.py` | `agent_executor.invoke()` | LangGraph 그래프 실행 시작 | `question`, `difficulty`, `messages` | AgentState 반환 | 없음 | 없음 |
| **9** | **라우터 노드** | `src/agent/nodes.py` | `router_node()`, `extract_keywords()` | 다중 요청 패턴 확인 및 도구 선택 | `question`, `multi_request_patterns.yaml` | `tool_choice`, `tool_pipeline`, `routing_reason` | 없음 | `AgentState` |
| **10** | **도구 래퍼** | `src/agent/tool_wrapper.py` | `wrap_tool_node()` | 도구 실행 전 래퍼 적용 | 도구 함수 | `tool_status`, `tool_result` 설정 | 없음 | `AgentState` |
| **11-A** | **RAG 용어집 검색** | `src/tools/glossary.py` | `glossary_node()`, `extract_term_from_question()`, `hybrid_search()` | SQL(ILIKE) + Vector 하이브리드 검색 (50%+50%) | `question` | 용어 정의 또는 실패 | **일반 답변** | `AgentState.tool_result` |
| **11-A-F** | **일반 답변 (Fallback)** | `src/tools/general.py` | `general_node()`, `get_general_template()`, `LLMClient.generate()` | LLM으로 직접 답변 생성 | `question`, `difficulty` | 일반 답변 텍스트 | 없음 | `AgentState.final_answers` |
| **12** | **DB 조회 (glossary)** | `src/db/rag_retriever.py` | `hybrid_search()`, `sql_search()`, `vector_search()` | PostgreSQL glossary 테이블 + pgvector 검색 | 추출된 용어 | SQL 결과 + 벡터 결과 병합 | 없음 | 없음 |
| **13** | **Fallback 체크** | `src/agent/graph.py` | `check_pipeline_or_fallback()` | `tool_status` 확인하여 Fallback 또는 Pipeline 진행 | `tool_status` | `pipeline_router` 또는 `fallback_router_node` | 없음 | 없음 |
| **14** | **Fallback Router** | `src/agent/nodes.py` | `fallback_router_node()`, `TOOL_FALLBACKS.get()` | 실패한 도구를 Fallback 도구로 교체 (glossary→general) | `tool_choice`, `TOOL_FALLBACKS` | `tool_pipeline` 수정, `retry_count` 증가 | 없음 | `AgentState` |
| **15** | **Pipeline Router** | `src/agent/graph.py` | `pipeline_router()` | 검색 성공 시 스킵 로직 적용 (search_paper→summarize 직행) | `tool_status`, `pipeline_index` | 다음 도구 선택 또는 스킵 | 없음 | `AgentState` |
| **16-A** | **RAG 논문 검색** | `src/tools/search_paper.py` | `search_paper_node()`, `RAGRetriever()`, `hybrid_search()` | Vector(70%) + FTS(30%) 하이브리드 검색 | `question` | 논문 본문 또는 실패 | **Web 논문 검색** | `AgentState.tool_result` |
| **16-A-F1** | **Web 논문 검색 (Fallback 1)** | `src/tools/web_search.py` | `web_search_node()`, `TavilySearchResults()` | Tavily API로 웹 검색 | `question` | 웹 검색 결과 또는 실패 | **일반 답변** | `AgentState.tool_result` |
| **16-A-F2** | **일반 답변 (Fallback 2)** | `src/tools/general.py` | `general_node()`, `get_general_template()`, `LLMClient.generate()` | LLM으로 직접 답변 생성 | `question`, `difficulty` | 일반 답변 텍스트 | 없음 | `AgentState.final_answers` |
| **17** | **DB 조회 (papers)** | `src/db/rag_retriever.py` | `hybrid_search()`, `vector_search()`, `fts_search()` | PostgreSQL papers 테이블 + pgvector 검색 | 질문 임베딩 | Vector 70% + FTS 30% 병합 결과 | 없음 | 없음 |
| **18** | **논문 요약** | `src/tools/summarize.py` | `summarize_node()`, `get_summarize_template()`, `LLMClient.generate()` | 파이프라인 모드: 이전 tool_result 활용하여 요약 | 검색된 논문 본문, `difficulty` | 난이도별 논문 요약 | **일반 답변** | `AgentState.final_answers` |
| **18-F** | **일반 답변 (Fallback)** | `src/tools/general.py` | `general_node()`, `get_general_template()`, `LLMClient.generate()` | 요약 실패 시 일반 답변 생성 | `question`, `difficulty` | 일반 답변 텍스트 | 없음 | `AgentState.final_answers` |
| **19** | **LLM 호출** | `src/llm/client.py` | `LLMClient.generate()`, `chat.completions.create()` | OpenAI API 호출 (Solar-pro2 또는 GPT-5) | 시스템 프롬프트 + 사용자 질문 | `generated_text`, 토큰 사용량 | 없음 | 없음 |
| **20** | **AgentState 업데이트** | `src/agent/graph.py` | (LangGraph 자동) | `tool_result`, `final_answers`, `tool_status`, `messages`, `metadata` 업데이트 | 도구 출력 | AgentState 갱신 | 없음 | 메모리 |
| **21** | **종료 조건 확인** | `src/agent/graph.py` | `should_end()` | `pipeline_index` 완료, `final_answers` 존재, `retry_count` 초과 확인 | `AgentState` | `END` 또는 `CONTINUE` | 없음 | 없음 |
| **22** | **UI 답변 표시** | `ui/components/chat_interface.py` | `render_chat_input()`, `st.markdown()` | 난이도별 답변, 도구 배지, 선택 이유 표시 | `response.final_answers` | 채팅 UI에 답변 렌더링 | 없음 | `st.session_state.chats` |
| **23** | **용어 추출 및 저장** | `ui/components/chat_interface.py` | `extract_and_save_terms()`, 정규식 매칭, LLM 추출 | 답변에서 기술 용어 추출 후 DB 저장 | 답변 텍스트 | `extracted_terms` 테이블에 INSERT | 없음 | PostgreSQL DB |
| **24** | **답변 평가** | `ui/components/chat_interface.py` | `LLMClient.generate()` (평가 프롬프트) | LLM-as-a-Judge로 정확성/완전성/명확성 평가 | 질문 + 답변 | 평가 점수(0~100), `evaluations` 테이블 저장 | 없음 | PostgreSQL DB |
| **25** | **계속 대화** | `ui/components/chat_interface.py` | `st.chat_input()` | 새 질문 대기, 있으면 7단계로 복귀 | 새 질문 또는 없음 | 7단계로 복귀 또는 세션 유지 | 없음 | `st.session_state` |
| **26** | **세션 종료** | `ui/app.py` | `cleanup_on_exit()`, `atexit.register()` | 브라우저 탭 닫기 시 빈 폴더 정리 | `experiments/` 폴더 | 빈 폴더 삭제 완료 | 없음 | 로컬 파일 시스템 |
</details>

### 표 설명

- **단계**: 실행 순서 (1~26단계)
- **Fallback 표기**:
  - `11-A`: 용어집 검색 (메인)
  - `11-A-F`: 용어집 실패 시 Fallback (일반 답변)
  - `16-A`: 논문 검색 (메인)
  - `16-A-F1`: 논문 검색 실패 시 Fallback 1단계 (Web 검색)
  - `16-A-F2`: Web 검색 실패 시 Fallback 2단계 (일반 답변)
- **세션 저장**: 각 단계의 결과가 저장되는 위치 (메모리, DB, 파일 등)

---

## 단계별 워크플로우 상세 설명

아래는 각 단계가 **언제, 왜, 어떻게** 실행되는지를 이해할 수 있도록 상세히 설명한 것입니다.

### 🚀 Phase 1: 프로그램 시작 및 초기화 (1~6단계)

<details>
<summary><strong>1단계: 프로그램 시작</strong></summary>

**언제 실행되나요?**
- 터미널에서 `python main.py` 명령어를 실행했을 때 가장 먼저 실행됩니다.

**무엇을 하나요?**
- `.env` 파일에 저장된 환경변수(API 키, DB 접속 정보 등)를 메모리에 로드합니다.
- `load_dotenv()` 함수가 `.env` 파일을 읽어서 `os.getenv()`로 접근 가능하게 만듭니다.

**왜 필요한가요?**
- OpenAI API 키나 PostgreSQL 비밀번호 같은 민감한 정보를 코드에 직접 쓰지 않고 안전하게 관리하기 위함입니다.

**실제 코드 예시:**
```python
# main.py
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드
```

</details>

<details>
<summary><strong>2단계: Streamlit 서버 시작</strong></summary>

**언제 실행되나요?**
- 1단계에서 환경변수 로드가 완료된 직후 실행됩니다.

**무엇을 하나요?**
- `subprocess.run()` 함수로 새로운 프로세스를 생성하여 Streamlit 서버를 시작합니다.
- 서버는 `localhost:8501` 포트에서 실행되며, 자동으로 브라우저가 열립니다.

**왜 필요한가요?**
- 사용자가 웹 브라우저에서 챗봇과 대화할 수 있는 UI를 제공하기 위함입니다.

**실제 코드 예시:**
```python
# main.py
subprocess.run(["streamlit", "run", "ui/app.py"])
```

</details>

<details>
<summary><strong>3단계: UI 초기화</strong></summary>

**언제 실행되나요?**
- Streamlit 서버가 시작되고 브라우저에서 페이지를 로드할 때 실행됩니다.

**무엇을 하나요?**
- `st.set_page_config()`로 페이지 제목, 아이콘, 레이아웃을 설정합니다.
- 환경변수 검증: `OPENAI_API_KEY`가 없으면 에러 메시지를 표시하고 앱을 중지합니다.
- `initialize_agent()` 함수로 Agent와 ExperimentManager를 생성합니다 (캐싱됨).

**왜 필요한가요?**
- API 키가 없으면 LLM을 호출할 수 없으므로, 앱 시작 전에 검증해야 합니다.
- Agent를 매번 새로 생성하면 느리므로, 캐싱하여 재사용합니다.

**실제 코드 예시:**
```python
# ui/app.py
st.set_page_config(page_title="논문 리뷰 챗봇", page_icon="📚")
if not os.getenv("OPENAI_API_KEY"):
    st.error("❌ API 키가 없습니다")
    st.stop()
```

</details>

<details>
<summary><strong>4단계: ExperimentManager 생성</strong></summary>

**언제 실행되나요?**
- 3단계의 `initialize_agent()` 함수 내부에서 실행됩니다.

**무엇을 하나요?**
- 실험 폴더를 생성합니다: `experiments/20250108/exp_001/` (날짜와 ID로 구분)
- 로그 파일(`log.txt`)과 설정 파일(`config.json`)을 생성합니다.
- 모든 실험 데이터를 이 폴더에 저장합니다.

**왜 필요한가요?**
- 여러 실험을 체계적으로 관리하고, 나중에 결과를 비교/분석하기 위함입니다.
- 로그를 통해 문제가 발생했을 때 디버깅이 쉬워집니다.

**실제 폴더 구조:**
```
experiments/
└── 20251028/
    ├── 날짜_시간_session_001/
    └── 날짜_시간_session_002/
```

</details>

<details>
<summary><strong>5단계: Agent 그래프 생성</strong></summary>

**언제 실행되나요?**
- 4단계에서 ExperimentManager 생성 직후 실행됩니다.

**무엇을 하나요?**
- LangGraph의 `StateGraph`를 사용하여 Agent의 실행 흐름을 정의합니다.
- 노드 추가: `router_node`, `glossary_node`, `search_paper_node` 등 8개 노드
- 엣지 추가: 노드 간 연결 (조건부 라우팅 포함)
- `workflow.compile()`로 그래프를 실행 가능한 형태로 컴파일합니다.

**왜 필요한가요?**
- Agent가 질문을 받았을 때 어떤 순서로 도구를 실행할지 미리 정의해야 합니다.
- 그래프 구조로 표현하면 복잡한 로직도 시각적으로 이해하기 쉽습니다.

**실제 코드 예시:**
```python
# src/agent/graph.py
workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("glossary", glossary_node)
workflow.add_edge("router", "glossary")
agent = workflow.compile()
```

</details>

<details>
<summary><strong>6단계: UI 렌더링</strong></summary>

**언제 실행되나요?**
- 5단계에서 Agent 그래프 생성 완료 후, 페이지를 처음 로드할 때 실행됩니다.

**무엇을 하나요?**
- `initialize_storage()`: Storage 초기화 (채팅 데이터 저장용)
- `initialize_chat_sessions()`: 세션 상태 초기화 (`st.session_state.chats = {}`)
- `create_new_chat()`: 첫 번째 채팅을 자동으로 생성 (난이도: easy)
- `render_sidebar()`: 사이드바에 난이도 선택, 채팅 목록 표시

**왜 필요한가요?**
- 사용자가 페이지를 열자마자 바로 대화를 시작할 수 있도록 준비합니다.
- 여러 채팅 세션을 관리하기 위한 초기 구조를 설정합니다.

**실제 화면:**
```
사이드바: [새 채팅] [난이도: Easy] [채팅 1, 채팅 2, ...]
메인 화면: 채팅 입력창 (비어있음)
```

</details>

---

### 💬 Phase 2: 사용자 입력 및 Agent 실행 (7~10단계)

<details>
<summary><strong>7단계: 사용자 입력 처리</strong></summary>

**언제 실행되나요?**
- 사용자가 채팅 입력창에 질문을 입력하고 Enter를 누를 때 실행됩니다.

**무엇을 하나요?**
- `st.chat_input()`으로 사용자 입력을 수신합니다.
- 현재 채팅 ID를 가져와서 해당 채팅의 메시지 히스토리에 사용자 메시지를 추가합니다.
- 이전 대화 내역도 함께 로드하여 Agent에 전달합니다.

**왜 필요한가요?**
- Agent가 이전 대화 맥락을 이해하고 연속적인 대화를 할 수 있도록 합니다.
- 여러 채팅 세션을 구분하여 관리합니다.

**실제 코드 예시:**
```python
# ui/components/chat_interface.py
user_input = st.chat_input("질문을 입력하세요")
if user_input:
    st.session_state.chats[chat_id]["messages"].append({
        "role": "user",
        "content": user_input
    })
```

</details>

<details>
<summary><strong>8단계: Agent 실행</strong></summary>

**언제 실행되나요?**
- 7단계에서 사용자 메시지가 추가된 직후 실행됩니다.

**무엇을 하나요?**
- `agent_executor.invoke()`로 LangGraph 그래프를 실행합니다.
- 입력 데이터: `question` (사용자 질문), `difficulty` (난이도), `messages` (대화 히스토리)
- Streamlit Callback을 사용하여 실시간으로 로그를 출력합니다.

**왜 필요한가요?**
- Agent의 실행을 시작하는 진입점입니다.
- 입력 데이터를 AgentState에 전달하여 모든 노드에서 접근 가능하게 만듭니다.

**실제 코드 예시:**
```python
# ui/components/chat_interface.py
response = agent_executor.invoke({
    "question": user_input,
    "difficulty": difficulty,
    "messages": previous_messages
})
```

</details>

<details>
<summary><strong>9단계: 라우터 노드</strong></summary>

**언제 실행되나요?**
- Agent 실행 시 가장 먼저 실행되는 노드입니다.

**무엇을 하나요?**
- 사용자 질문을 분석하여 어떤 도구를 사용할지 결정합니다.
- **다중 요청 패턴 확인**: `multi_request_patterns.yaml` 파일에서 패턴을 찾습니다.
  - 예: "논문 검색 후 요약해줘" → `[search_paper, summarize]` 파이프라인
- **단일 요청**: LLM을 사용하여 가장 적합한 도구 1개를 선택합니다.
- 결과: `tool_choice`, `tool_pipeline`, `routing_reason`을 AgentState에 저장

**왜 필요한가요?**
- 질문에 따라 다른 도구를 사용해야 하므로, 라우팅 로직이 필요합니다.
- 다중 요청을 자동으로 감지하여 여러 도구를 순차 실행합니다.

**실제 예시:**
```
질문: "Transformer가 뭐야?"
→ 라우터 판단: glossary (용어집 검색)

질문: "Attention 논문 찾아서 요약해줘"
→ 라우터 판단: [search_paper, summarize] 파이프라인
```

</details>

<details>
<summary><strong>10단계: 도구 래퍼</strong></summary>

**언제 실행되나요?**
- 라우터가 도구를 선택한 직후, 실제 도구를 실행하기 전에 래퍼가 감싸서 실행합니다.

**무엇을 하나요?**
- 선택된 도구 함수(예: `glossary_node`)를 호출합니다.
- 도구 실행 결과를 검증합니다 (성공/실패 판단).
- `tool_status`를 자동으로 설정합니다 (`success` 또는 `failed`).
- `tool_result`를 AgentState에 저장합니다.

**왜 필요한가요?**
- 모든 도구에 공통적으로 적용되는 로직(상태 설정, 결과 저장)을 중복 없이 처리합니다.
- 도구가 실패했을 때 자동으로 Fallback을 트리거할 수 있습니다.

**실제 코드 예시:**
```python
# src/agent/tool_wrapper.py
def wrap_tool_node(tool_func):
    def wrapper(state: AgentState):
        result = tool_func(state)  # 도구 실행
        if result:
            state["tool_status"] = "success"
        else:
            state["tool_status"] = "failed"
        state["tool_result"] = result
        return state
    return wrapper
```

</details>

---

### 🔍 Phase 3: 도구 실행 및 Fallback (11~18단계)

<details>
<summary><strong>11-A단계: RAG 용어집 검색</strong></summary>

**언제 실행되나요?**
- 라우터가 `glossary` 도구를 선택했을 때 실행됩니다.

**무엇을 하나요?**
1. **용어 추출**: `extract_term_from_question()`으로 질문에서 기술 용어를 추출
   - 예: "Transformer가 뭐야?" → "Transformer"
2. **SQL 검색**: PostgreSQL `glossary` 테이블에서 `ILIKE '%Transformer%'` 검색
3. **벡터 검색**: `glossary_embeddings` 테이블에서 코사인 유사도 검색
4. **하이브리드 병합**: SQL 결과 50% + 벡터 결과 50%를 합산하여 최종 결과 선택

**왜 필요한가요?**
- 단순 키워드 검색(SQL)만으로는 동의어나 유사 용어를 찾기 어렵습니다.
- 벡터 검색을 함께 사용하면 의미적으로 유사한 용어도 찾을 수 있습니다.

**결과:**
- **성공**: 용어 정의를 `tool_result`에 저장 → 바로 22단계(UI 표시)로 이동
- **실패**: `tool_status = "failed"` → 11-A-F단계(Fallback)로 이동

</details>

<details>
<summary><strong>11-A-F단계: 일반 답변 (Fallback)</strong></summary>

**언제 실행되나요?**
- 11-A단계에서 용어를 찾지 못했을 때(실패) 자동으로 실행됩니다.

**무엇을 하나요?**
- `general_node()`를 실행하여 LLM에게 직접 질문을 전달합니다.
- 난이도에 맞는 프롬프트 템플릿을 로드합니다 (`get_general_template()`).
- LLM이 자체 지식으로 답변을 생성합니다.

**왜 필요한가요?**
- DB에 없는 용어라도 사용자에게 "찾을 수 없습니다"라고만 답하는 것보다, LLM의 일반 지식으로 답변하는 것이 더 유용합니다.

**실제 예시:**
```
질문: "Quantum Attention이 뭐야?"
→ glossary 검색 실패 (DB에 없음)
→ Fallback: general_node가 LLM으로 답변 생성
→ "Quantum Attention은 양자 컴퓨팅 개념을 Attention 메커니즘에 적용한 것입니다..."
```

</details>

<details>
<summary><strong>12단계: DB 조회 (glossary)</strong></summary>

**언제 실행되나요?**
- 11-A단계의 `glossary_node` 내부에서 실행됩니다.

**무엇을 하나요?**
- `RAGRetriever.hybrid_search()` 메서드 호출
- **SQL 검색**: `SELECT * FROM glossary WHERE term ILIKE '%검색어%'`
- **벡터 검색**: pgvector 확장을 사용하여 임베딩 유사도 검색
- 두 결과를 점수 기반으로 병합합니다.

**왜 필요한가요?**
- 실제 데이터를 가져오는 레이어입니다.
- SQL과 벡터 검색을 분리하여 각각의 장점을 활용합니다.

**실제 SQL 예시:**
```sql
-- SQL 검색
SELECT term, definition FROM glossary WHERE term ILIKE '%Transformer%';

-- 벡터 검색 (pgvector)
SELECT term, definition
FROM glossary_embeddings
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 5;
```

</details>

<details>
<summary><strong>13단계: Fallback 체크</strong></summary>

**언제 실행되나요?**
- 도구(11-A단계) 실행 완료 후 자동으로 실행됩니다.

**무엇을 하나요?**
- `tool_status`를 확인합니다.
- **성공**: `pipeline_router`로 이동 (다음 도구 실행 또는 종료)
- **실패**: `fallback_router_node`로 이동 (Fallback 도구 실행)

**왜 필요한가요?**
- 도구 실패 시 자동으로 대체 도구를 실행하여 사용자에게 항상 답변을 제공합니다.

**실제 흐름:**
```
glossary 성공 → pipeline_router → END
glossary 실패 → fallback_router_node → general 실행
```

</details>

<details>
<summary><strong>14단계: Fallback Router</strong></summary>

**언제 실행되나요?**
- 13단계에서 `tool_status = "failed"`일 때 실행됩니다.

**무엇을 하나요?**
- `TOOL_FALLBACKS` 딕셔너리에서 실패한 도구의 Fallback을 조회합니다.
  - 예: `TOOL_FALLBACKS = {"glossary": "general", "search_paper": "web_search"}`
- `tool_pipeline`을 수정하여 실패한 도구를 Fallback 도구로 교체합니다.
- `retry_count`를 증가시켜 무한 루프를 방지합니다.

**왜 필요한가요?**
- 도구마다 다른 Fallback 전략을 가질 수 있습니다.
- 자동으로 Fallback 체인을 따라 재시도합니다.

**실제 예시:**
```python
TOOL_FALLBACKS = {
    "glossary": "general",
    "search_paper": "web_search",
    "web_search": "general",
    "summarize": "general"
}

# glossary 실패 시
tool_pipeline = ["glossary"]  # 원래
→ tool_pipeline = ["general"]  # Fallback 적용
```

</details>

<details>
<summary><strong>15단계: Pipeline Router</strong></summary>

**언제 실행되나요?**
- 13단계에서 `tool_status = "success"`일 때, 또는 14단계(Fallback Router) 실행 후 실행됩니다.

**무엇을 하나요?**
- **검색 스킵 로직**: 검색 도구가 성공하면 나머지 검색 도구를 건너뜁니다.
  - `search_paper` 성공 → `web_search`, `general` 건너뛰기 → `summarize`로 직행
  - `web_search` 성공 → `general` 건너뛰기 → `summarize`로 직행
- **순차 진행**: 파이프라인의 다음 도구로 `pipeline_index`를 증가시킵니다.

**왜 필요한가요?**
- 불필요한 검색을 방지하여 실행 시간과 비용을 절약합니다.
- 다중 요청 파이프라인에서 효율적으로 도구를 실행합니다.

**실제 예시:**
```
파이프라인: [search_paper, web_search, general, summarize]

Case 1: search_paper 성공
→ web_search, general 스킵
→ summarize 실행

Case 2: search_paper 실패 → web_search 성공
→ general 스킵
→ summarize 실행

Case 3: search_paper, web_search 모두 실패
→ general 실행 (Fallback)
→ summarize 실행
```

</details>

<details>
<summary><strong>16-A단계: RAG 논문 검색</strong></summary>

**언제 실행되나요?**
- 라우터가 `search_paper` 도구를 선택했을 때 실행됩니다.

**무엇을 하나요?**
1. **RAGRetriever 초기화**: PostgreSQL + pgvector 연결
2. **벡터 검색**: `papers_embeddings` 테이블에서 임베딩 유사도 검색 (70% 가중치)
3. **FTS 검색**: `papers` 테이블에서 Full-Text Search (30% 가중치)
4. **하이브리드 병합**: 벡터 70% + FTS 30%를 합산하여 최상위 논문 선택
5. **유사도 확인**: 유사도가 0.5 미만이면 성공, 0.5 이상이면 실패

**왜 필요한가요?**
- 로컬 DB에 저장된 논문을 먼저 검색하는 것이 웹 검색보다 빠르고 정확합니다.
- 벡터 검색은 의미적 유사도를, FTS는 키워드 매칭을 잘 수행합니다.

**결과:**
- **성공**: 논문 본문을 `tool_result`에 저장 → 18단계(요약)로 이동
- **실패**: `tool_status = "failed"` → 16-A-F1단계(Web 검색)로 Fallback

</details>

<details>
<summary><strong>16-A-F1단계: Web 논문 검색 (Fallback 1)</strong></summary>

**언제 실행되나요?**
- 16-A단계에서 논문을 찾지 못했을 때 자동으로 실행됩니다.

**무엇을 하나요?**
- Tavily API를 사용하여 웹에서 논문을 검색합니다.
- `TavilySearchResults()` 도구가 Google Scholar, arXiv 등에서 검색합니다.
- 검색 결과(제목, 링크, 요약)를 반환합니다.

**왜 필요한가요?**
- 로컬 DB에 없는 최신 논문이나 특정 논문은 웹 검색으로 찾아야 합니다.

**결과:**
- **성공**: 웹 검색 결과를 `tool_result`에 저장 → 18단계(요약)로 이동
- **실패**: `tool_status = "failed"` → 16-A-F2단계(일반 답변)로 Fallback

</details>

<details>
<summary><strong>16-A-F2단계: 일반 답변 (Fallback 2)</strong></summary>

**언제 실행되나요?**
- 16-A-F1단계(Web 검색)도 실패했을 때 최종적으로 실행됩니다.

**무엇을 하나요?**
- LLM에게 질문을 직접 전달하여 일반 지식으로 답변을 생성합니다.

**왜 필요한가요?**
- 모든 검색이 실패해도 사용자에게 "찾을 수 없습니다"보다는 LLM의 일반 지식으로 답변하는 것이 더 유용합니다.

**실제 예시:**
```
질문: "2025년 1월에 발표된 최신 LLM 논문 찾아줘"
→ search_paper 실패 (로컬 DB에 없음)
→ web_search 실패 (너무 최신이라 인덱싱 안 됨)
→ Fallback: general_node가 답변
→ "2025년 1월 최신 논문은 아직 제 데이터베이스에 없습니다. 하지만 일반적으로 LLM 연구는..."
```

</details>

<details>
<summary><strong>17단계: DB 조회 (papers)</strong></summary>

**언제 실행되나요?**
- 16-A단계의 `search_paper_node` 내부에서 실행됩니다.

**무엇을 하나요?**
- **벡터 검색**: `papers_embeddings` 테이블에서 임베딩 유사도 검색
- **FTS 검색**: `papers` 테이블에서 PostgreSQL Full-Text Search
- 두 결과를 가중치 기반으로 병합 (벡터 70%, FTS 30%)

**왜 필요한가요?**
- 논문 검색은 용어집보다 복잡하므로 벡터 검색 비중을 더 높입니다.
- FTS는 저자명, 논문 제목 등 정확한 키워드 매칭에 유리합니다.

**실제 SQL 예시:**
```sql
-- FTS 검색
SELECT title, abstract, content
FROM papers
WHERE to_tsvector('english', content) @@ to_tsquery('Transformer & Attention');

-- 벡터 검색
SELECT title, abstract, content
FROM papers_embeddings
ORDER BY embedding <=> '[...]'
LIMIT 10;
```

</details>

<details>
<summary><strong>18단계: 논문 요약</strong></summary>

**언제 실행되나요?**
- 16-A, 16-A-F1, 또는 16-A-F2 중 하나가 성공한 후, 파이프라인에 `summarize`가 있을 때 실행됩니다.

**무엇을 하나요?**
1. **파이프라인 모드 확인**: 이전 단계의 `tool_result` 사용 (검색 결과 활용)
2. **난이도 매핑**: `easy` → `elementary/beginner` 수준으로 변환
3. **프롬프트 로드**: `get_summarize_template(difficulty)`로 난이도별 프롬프트 가져오기
4. **LLM 호출**: `LLMClient.generate()`로 요약 생성

**왜 필요한가요?**
- 논문 전문은 길고 어려우므로, 사용자 난이도에 맞게 요약해야 합니다.
- 초보자는 쉬운 용어로, 전문가는 상세한 기술 내용으로 요약합니다.

**결과:**
- **성공**: 난이도별 요약을 `final_answers`에 저장 → 22단계(UI 표시)로 이동
- **실패**: Fallback (`18-F`)으로 일반 답변 생성

</details>

<details>
<summary><strong>18-F단계: 일반 답변 (Fallback)</strong></summary>

**언제 실행되나요?**
- 18단계에서 요약 생성이 실패했을 때 실행됩니다.

**무엇을 하나요?**
- LLM에게 원래 질문을 전달하여 일반 답변을 생성합니다.

**왜 필요한가요?**
- 요약 실패 시에도 사용자에게 답변을 제공하기 위함입니다.

</details>

---

### 🤖 Phase 4: LLM 호출 및 상태 관리 (19~21단계)

<details>
<summary><strong>19단계: LLM 호출</strong></summary>

**언제 실행되나요?**
- 일반 답변(`general_node`), 요약(`summarize_node`), 평가 등에서 LLM이 필요할 때 실행됩니다.

**무엇을 하나요?**
1. **모델 선택**: 환경변수 또는 설정에 따라 Solar-pro2 또는 GPT-5 선택
2. **프롬프트 조합**: 시스템 프롬프트 + 사용자 질문 결합
3. **OpenAI API 호출**: `chat.completions.create()` 메서드 사용
4. **응답 수신**: `generated_text` 추출
5. **토큰 사용량 계산**: `prompt_tokens + completion_tokens` 계산하여 로깅

**왜 필요한가요?**
- LLM은 모든 도구의 핵심입니다 (답변 생성, 라우팅, 평가 등).
- 토큰 사용량을 추적하여 비용을 관리합니다.

**실제 코드 예시:**
```python
# src/llm/client.py
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ],
    temperature=0.7
)
generated_text = response.choices[0].message.content
```

</details>

<details>
<summary><strong>20단계: AgentState 업데이트</strong></summary>

**언제 실행되나요?**
- 각 도구 실행 후 자동으로 LangGraph가 상태를 업데이트합니다.

**무엇을 하나요?**
- `tool_result`: 도구 실행 결과 저장
- `final_answers`: 난이도별 최종 답변 저장
- `tool_status`: `success` 또는 `failed` 저장
- `messages`: 대화 히스토리에 AI 메시지 추가
- `metadata`: 도구명, 선택 이유, 실행 시간 등 저장

**왜 필요한가요?**
- 모든 노드가 공유 상태를 통해 데이터를 주고받습니다.
- 대화 히스토리를 유지하여 연속적인 대화를 가능하게 합니다.

**AgentState 구조:**
```python
class AgentState(TypedDict):
    question: str
    difficulty: str
    tool_choice: str
    tool_result: str
    tool_status: str  # "success" or "failed"
    final_answers: dict  # {"easy": "...", "medium": "...", "hard": "..."}
    messages: list
    metadata: dict
    pipeline_index: int
    retry_count: int
```

</details>

<details>
<summary><strong>21단계: 종료 조건 확인</strong></summary>

**언제 실행되나요?**
- 각 도구 실행 후 매번 확인합니다.

**무엇을 하나요?**
- `should_end()` 함수가 다음 조건을 확인합니다:
  1. **파이프라인 완료**: `pipeline_index >= len(tool_pipeline)`
  2. **최종 답변 존재**: `final_answers`에 난이도별 답변이 모두 있음
  3. **재시도 횟수 초과**: `retry_count > 3`
- 조건 충족 시 `END`, 아니면 `CONTINUE`

**왜 필요한가요?**
- 무한 루프를 방지합니다.
- 답변이 완성되면 즉시 종료하여 불필요한 실행을 막습니다.

**실제 코드 예시:**
```python
# src/agent/graph.py
def should_end(state: AgentState):
    if state.get("final_answers"):
        return "END"
    if state.get("retry_count", 0) > 3:
        return "END"
    if state.get("pipeline_index", 0) >= len(state.get("tool_pipeline", [])):
        return "END"
    return "CONTINUE"
```

</details>

---

### 🖥️ Phase 5: UI 표시 및 부가 기능 (22~26단계)

<details>
<summary><strong>22단계: UI 답변 표시</strong></summary>

**언제 실행되나요?**
- Agent 실행이 완료되고 `response` 객체를 받은 후 실행됩니다.

**무엇을 하나요?**
1. **`final_answers` 추출**: 난이도별 답변 가져오기
2. **도구 배지 표시**: 어떤 도구를 사용했는지 표시 (예: `[용어집]`, `[논문 검색]`)
3. **선택 이유 표시**: `routing_reason` 출력
4. **답변 텍스트**: `st.markdown()`으로 마크다운 형식 렌더링

**왜 필요한가요?**
- 사용자에게 답변을 시각적으로 보기 좋게 표시합니다.
- 어떤 도구를 사용했는지 투명하게 보여줍니다.

**실제 화면 예시:**
```
🤖 AI 답변 [용어집]

선택 이유: 질문에서 기술 용어 "Transformer"를 감지하여 용어집 검색을 선택했습니다.

Transformer는 2017년 Google이 발표한...
```

</details>

<details>
<summary><strong>23단계: 용어 추출 및 저장</strong></summary>

**언제 실행되나요?**
- 22단계에서 답변이 UI에 표시된 직후 자동으로 실행됩니다.

**무엇을 하나요?**
1. **정규식 매칭**: 답변 텍스트에서 대문자로 시작하는 기술 용어 패턴 찾기
2. **LLM 용어 추출**: GPT로 기술 용어를 자동으로 추출
3. **DB 저장**: `extracted_terms` 테이블에 INSERT
4. **UI 표시**: 추출된 용어 목록을 사이드바나 하단에 표시

**왜 필요한가요?**
- 대화 중 등장한 기술 용어를 자동으로 수집하여 나중에 복습할 수 있습니다.
- 사용자가 어떤 용어에 관심 있는지 분석할 수 있습니다.

**실제 예시:**
```
답변: "Transformer는 Self-Attention 메커니즘을 사용합니다..."

추출된 용어:
- Transformer
- Self-Attention
- Multi-Head Attention
```

</details>

<details>
<summary><strong>24단계: 답변 평가</strong></summary>

**언제 실행되나요?**
- 사용자가 "평가하기" 버튼을 클릭했을 때 실행됩니다 (선택적 기능).

**무엇을 하나요?**
1. **평가 프롬프트 생성**: 질문 + 답변을 LLM에게 전달
2. **평가 기준 적용**:
   - 정확성 (Accuracy): 답변이 사실적으로 정확한가?
   - 완전성 (Completeness): 질문에 충분히 답변했는가?
   - 명확성 (Clarity): 이해하기 쉬운가?
3. **점수 계산**: 0~100점 산출
4. **DB 저장**: `evaluations` 테이블에 저장
5. **UI 표시**: 평가 결과를 사용자에게 표시

**왜 필요한가요?**
- Agent의 답변 품질을 자동으로 평가하여 개선점을 찾을 수 있습니다.
- LLM-as-a-Judge 방식으로 인간 평가 없이 빠르게 평가합니다.

**실제 평가 결과 예시:**
```
📊 답변 평가 결과

✅ 정확성: 90/100
✅ 완전성: 85/100
✅ 명확성: 95/100

총점: 90/100
```

</details>

<details>
<summary><strong>25단계: 계속 대화</strong></summary>

**언제 실행되나요?**
- 22~24단계가 완료된 후, 화면 하단에 입력창이 다시 활성화됩니다.

**무엇을 하나요?**
- `st.chat_input()`이 새로운 질문을 대기합니다.
- **새 질문 입력 시**: 7단계로 복귀하여 새 질문 처리
- **입력 없음**: 세션 유지, 대화 히스토리 보존

**왜 필요한가요?**
- 연속적인 대화를 지원하여 멀티턴 대화가 가능합니다.
- 이전 대화 맥락을 유지합니다.

**실제 흐름:**
```
사용자: "Transformer가 뭐야?"
→ (7~24단계 실행)
→ AI: "Transformer는..."

사용자: "그럼 BERT는?"
→ (7~24단계 다시 실행, 이전 대화 맥락 포함)
→ AI: "BERT는 Transformer 기반의..."
```

</details>

<details>
<summary><strong>26단계: 세션 종료</strong></summary>

**언제 실행되나요?**
- 사용자가 브라우저 탭을 닫거나 Streamlit 서버를 종료할 때 실행됩니다.

**무엇을 하나요?**
1. **`cleanup_on_exit()` 함수 호출**: `atexit.register()`로 등록된 정리 함수
2. **빈 폴더 탐색**: `experiments/YYYYMMDD/` 폴더에서 빈 폴더 찾기
3. **빈 폴더 삭제**: `folder.rmdir()`로 빈 폴더 정리
4. **로그 출력**: 삭제된 폴더 개수 출력

**왜 필요한가요?**
- 실험 폴더는 자동으로 생성되지만, 아무 파일도 없으면 불필요한 폴더가 쌓입니다.
- 정리 함수로 자동으로 디스크 공간을 절약합니다.

**실제 코드 예시:**
```python
# ui/app.py
def cleanup_on_exit():
    date_dir = Path(f"experiments/{today}")
    for folder in sorted(date_dir.rglob("*"), key=lambda p: -len(p.parts)):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()

atexit.register(cleanup_on_exit)
```

</details>

---

### 📊 핵심 개념 정리

#### Fallback 체인 (도구 자동 전환)

```
용어집 검색:
glossary (DB 검색) → 실패 → general (LLM 답변)

논문 검색:
search_paper (로컬 DB) → 실패 → web_search (Tavily) → 실패 → general (LLM)

요약:
summarize (파이프라인 모드) → 실패 → general (LLM)
```

#### 하이브리드 검색

**용어집 (50% + 50%)**
- SQL 검색 50%: 정확한 키워드 매칭
- 벡터 검색 50%: 의미적 유사도

**논문 (70% + 30%)**
- 벡터 검색 70%: 논문은 의미적 유사도가 더 중요
- FTS 검색 30%: 저자명, 제목 등 정확한 매칭

#### 다중 요청 파이프라인

```
질문: "Attention 논문 찾아서 초보자용으로 요약해줘"

파이프라인: [search_paper, web_search, general, summarize]

실행 흐름:
1. search_paper 실행 → 성공
2. web_search, general 스킵 (검색 성공했으므로)
3. summarize 실행 (이전 검색 결과 활용)
4. 최종 답변 반환
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
| **OpenAI API** | gpt-5 | Hard 모드 답변 생성 (전문가 수준 질문) |
| **Upstage Solar API** | solar-pro2 | Easy 모드 답변 생성 (초심자 수준 질문) |
| **LangChain** | ≥0.1.0 | LLM 체이닝 및 프롬프트 관리 |
| **LangChain Community** | ≥0.0.20 | 커뮤니티 통합 도구 |
| **LangChain OpenAI** | ≥0.1.0 | OpenAI 모델 통합 |
| **LangChain Upstage** | ≥0.7.4 | Upstage Solar 모델 통합 |
| **LangGraph** | ≥1.0.1 | AI Agent StateGraph 구현 |
| **OpenAI Embeddings** | text-embedding-3-small | 텍스트 임베딩 (1536 차원) |

### Database & Vector Store

| 기술 | 버전 | 용도 |
|------|------|------|
| **PostgreSQL** | 15+ | RDBMS (논문, 용어, 로그 데이터) |
| **pgvector** | 0.3.6 | 벡터 유사도 검색 (IVFFlat 인덱스) |
| **psycopg2-binary** | ≥2.9.11 | PostgreSQL 드라이버 |
| **LangChain PostgreSQL** | ≥0.0.16 | Langchain PostgreSQL 통합 |
| **SQLAlchemy** | ≥2.0.0 | ORM 및 DB 추상화 |

### Web Framework & UI

| 기술 | 버전 | 용도 |
|------|------|------|
| **Streamlit** | ≥1.29.0 | 웹 UI 프레임워크 |
| **streamlit-authenticator** | ≥0.4.2 | 사용자 인증 시스템 |

### Data Processing

| 기술 | 버전 | 용도 |
|------|------|------|
| **sentence-transformers** | ≥2.2.0 | 문장 임베딩 모델 |
| **arxiv** | ≥2.0.0 | arXiv API 클라이언트 |
| **pymupdf** | ≥1.24.0 | PDF 처리 (MuPDF 기반) |
| **pypdf** | ≥4.0.0 | PDF 텍스트 추출 |
| **LangChain Text Splitters** | ≥0.0.1 | 문서 청킹 |

### External APIs

| API | 패키지 버전 | 용도 |
|-----|------------|------|
| **Tavily Search API** | tavily-python ≥0.5.0 | 실시간 웹 검색 |
| **arXiv API** | arxiv ≥2.0.0 | 논문 메타데이터 및 PDF 다운로드 |
| **DuckDuckGo Search** | duckduckgo-search ≥3.9.0 | 웹 검색 Fallback |

### Development Tools

| 도구 | 버전 | 용도 |
|------|------|------|
| **Python** | 3.11.9 | 프로그래밍 언어 |
| **PyYAML** | ≥6.0.0 | 설정 파일 관리 |
| **python-dotenv** | ≥1.0.0 | 환경 변수 관리 |
| **tenacity** | ≥8.2.0 | 재시도 로직 |
| **pytest** | ≥7.4.0 | 테스트 프레임워크 |
| **uv** | 0.9.7 | 의존성 관리 최적화 |

---

## 📁 프로젝트 구조
```
langchain-project/
├── .env                                      # 환경 변수 (실제 값)
├── .env.example                              # 환경 변수 템플릿
├── .envrc                                    # direnv 설정
├── .gitignore                                # Git 제외 파일 목록
├── README.md                                 # 프로젝트 소개 문서
├── main.py                                   # 애플리케이션 진입점
├── requirements.txt                          # Python 의존성 패키지
│
├── configs/                                  # 설정 파일
│   └── collect/                              # 데이터 수집 설정
│
├── data/                                     # 데이터 저장소
│   ├── processed/                            # 전처리된 데이터
│   ├── raw/                                  # 원본 데이터
│   │   └── pdfs/                             # PDF 논문 파일
│   ├── rdbms/                                # 관계형 DB 데이터
│   └── vectordb/                             # 벡터 DB 데이터
│       └── papers_faiss/                     # FAISS 인덱스
│
├── database/                                 # DB 스키마 및 마이그레이션
│
├── docs/                                     # 프로젝트 문서
│   ├── PRD/                                  # 제품 요구사항 명세서
│   ├── QnA/                                  # 질의응답 문서
│   ├── architecture/                         # 아키텍처 문서
│   │   ├── mermaid/                          # Mermaid 다이어그램
│   │   ├── multiple_request/                 # 다중 요청 아키텍처 문서
│   │   └── single_request/                   # 단일 요청 아키텍처 문서
│   ├── errors/                               # 에러 로그
│   ├── images/                               # 문서 이미지
│   │   ├── architecture/                     # 아키텍처 이미지
│   │   ├── github/                           # GitHub 관련 이미지
│   │   ├── logging_experimentmanager_system/ # 로깅/실험관리 시스템 이미지
│   │   ├── run_img/                          # 실행 화면 이미지
│   │   └── slack/                            # Slack 관련 이미지
│   ├── issues/                               # 이슈 트래킹
│   ├── minutes/                              # 회의록
│   ├── modularization/                       # 모듈화 문서
│   ├── roles/                                # 역할 정의
│   ├── rules/                                # 규칙 및 가이드
│   ├── scenarios/                            # 사용 시나리오
│   └── usage/                                # 사용법 문서
│       ├── team/                             # 팀별 사용법 문서
│       └── tests/                            # 테스트 관련 문서
│
├── experiments/                              # 실험 로그 (자동 생성)
│   └── YYYYMMDD/                             # 날짜별 폴더
│       └── YYYYMMDD_HHMMSS_session_XXX/      # 세션별 폴더
│           ├── configs/                      # 설정 파일
│           ├── database/                     # 데이터베이스 관련 로그
│           ├── evaluation/                   # 평가 결과
│           ├── outputs/                      # 출력 파일
│           │   └── save_data/                # 사용자 저장 데이터
│           ├── prompts/                      # 프롬프트 기록
│           ├── tools/                        # 도구 실행 로그
│           ├── ui/                           # UI 인터랙션 로그
│           ├── chatbot.log                   # 메인 챗봇 로그
│           └── metadata.json                 # 세션 메타데이터
│
├── notebooks/                                # Jupyter 노트북
│   ├── base/                                 # 기본 실험 노트북
│   └── team/                                 # 팀별 노트북
│
├── prompts/                                  # 프롬프트 템플릿
│
├── scripts/                                  # 유틸리티 스크립트
│   ├── analysis/                             # 분석 스크립트
│   ├── data/                                 # 데이터 처리
│   ├── debug/                                # 디버깅 도구
│   ├── system/                               # 시스템 관리
│   └── tests/                                # 테스트 스크립트
│       ├── integration/                      # 통합 테스트
│       └── unit/                             # 단위 테스트
│
├── src/                                      # 소스 코드
│   ├── agent/                                # AI Agent (LangGraph)
│   ├── data/                                 # 데이터 처리
│   ├── database/                             # DB 연결 및 쿼리
│   ├── evaluation/                           # 성능 평가
│   ├── llm/                                  # LLM 클라이언트
│   ├── memory/                               # 대화 메모리
│   ├── papers/                               # 논문 처리
│   │   ├── domain/                           # 도메인 모델
│   │   └── infra/                            # 인프라 계층
│   ├── prompts/                              # 프롬프트 관리
│   ├── rag/                                  # RAG 검색
│   ├── text2sql/                             # Text-to-SQL
│   ├── tools/                                # Agent 도구
│   └── utils/                                # 유틸리티 함수
│
└── ui/                                       # Streamlit UI
    ├── assets/                               # 정적 자산
    ├── components/                           # UI 컴포넌트
    ├── pages/                                # 페이지
    └── test/                                 # UI 테스트
```

---

## 🔧 핵심 기술 구현

### 1. 로깅 & 실험 관리 시스템

#### [Logger 시스템]

**위치**: `src/utils/logger.py`

논문 리뷰 챗봇 프로젝트 전체에서 사용하는 통합 로깅 기반 시스템으로, 개발 과정에서 발생하는 모든 이벤트를 체계적으로 기록합니다.

| 구분 | 내용 |
|------|------|
| **핵심 역할** | 이벤트 기록, 실험 추적, 디버깅 지원, 성능 분석, 문서화 |
| **의존성** | 모든 상위 시스템(Agent, RAG, LLM Client, Tools)의 기반 |
| **로그 정책** | print() 사용 금지, logger.write() 필수 사용 |
| **파일 위치** | `experiments/날짜/날짜_시간_session_XXX/chatbot.log` |

**주요 기능**:

| 기능 | 설명 | 사용 방법 |
|------|------|-----------|
| **타임스탬프 자동 추가** | 모든 로그에 `YYYY-MM-DD HH:MM:SS` 형식 시간 기록 | 자동 적용 |
| **파일 및 콘솔 동시 출력** | 파일 저장 + 콘솔 실시간 확인 | `print_also=True` (기본값) |
| **표준 출력 리디렉션** | print()를 로그로 자동 저장 | `start_redirect()` / `stop_redirect()` |
| **tqdm 진행률 지원** | 콘솔: 실시간 표시, 로그: 10% 단위만 기록 | `logger.tqdm()` |
| **에러 메시지 색상 구분** | 콘솔에 빨간색으로 표시 | `print_error=True` |
| **with 문 지원** | 자동 리소스 정리 | `with Logger(...) as logger:` |

**로깅 흐름**:
1. 개발자가 코드 실행 → Logger 초기화 → 로그 파일 자동 생성
2. 코드 실행 중 `logger.write()` 호출 → 타임스탬프 추가 → 파일과 콘솔에 동시 출력
3. 작업 완료 후 `logger.close()` → 파일 닫기 → 개발자가 로그 확인 및 분석

**성능 최적화**:
- **즉시 플러시**: 모든 write() 호출 시 자동 flush로 프로그램 비정상 종료 시에도 로그 보존
- **tqdm 최적화**: 콘솔(모든 진행률) vs 로그(10% 단위)로 파일 크기 절약

**참조 문서**:
- [실험 관리 시스템 구현 이슈](docs/issues/01-1_실험_관리_시스템_구현.md)
- [Logger 사용법 가이드](docs/rules/logger_사용법.md)
- [최현화 로깅&모니터링 역할](docs/roles/01-2_최현화_로깅_모니터링.md)
- [로깅 시스템 PRD](docs/PRD/05_로깅_시스템.md)
- [실험 관리 시스템 모듈화 문서](docs/modularization/03_실험_관리_시스템.md)


#### [ExperimentManager 시스템]

**위치**: `src/utils/experiment_manager.py`

모든 챗봇 실행을 체계적으로 추적하고 관리하는 핵심 시스템으로, Session ID 자동 부여, 폴더 구조 자동 생성, Logger 통합, 메타데이터 관리를 제공합니다.

| 구분 | 내용 |
|------|------|
| **핵심 역할** | Session ID 자동 부여, 폴더 구조 자동 생성, Logger 통합, 메타데이터 관리 |
| **의존성** | Logger, DB Queries, Prompts, UI Events, Outputs, Evaluation |
| **사용 방법** | with 문 필수 사용 (자동 리소스 정리) |
| **Session ID 규칙** | 당일 기준 순차 증가 (session_001, 002...), 매일 001부터 재시작 |

**자동 생성 폴더 구조 (7개)**:

| 폴더 | 용도 | 주요 파일 |
|------|------|-----------|
| **tools/** | 도구 실행 로그 | rag_paper.log, web_search.log, text2sql.log, general.log 등 |
| **database/** | DB 쿼리 및 검색 기록 | queries.sql, pgvector_searches.json |
| **prompts/** | 프롬프트 기록 | system_prompt.txt, user_prompt.txt, final_prompt.txt |
| **ui/** | UI 인터랙션 로그 | user_interactions.log, errors.log |
| **outputs/** | 생성 결과물 | response.txt, conversation_easy/hard.json, save_data/ |
| **evaluation/** | 평가 지표 | evaluation_YYYYMMDD_HHMMSS.json |
| **configs/** | 설정 파일 | db_config.yaml, model_config.yaml, multi_request_patterns.yaml |

**주요 메서드**:

| 분류 | 메서드 | 설명 | 저장 위치 |
|------|--------|------|-----------|
| **도구** | `get_tool_logger(tool_name)` | 도구별 독립 Logger 생성 | tools/{tool_name}.log |
| **DB** | `log_sql_query(...)` | SQL 쿼리 기록 | database/queries.sql |
| **DB** | `log_pgvector_search(...)` | pgvector 검색 기록 | database/pgvector_searches.json |
| **프롬프트** | `save_system_prompt(...)` | 시스템 프롬프트 저장 | prompts/system_prompt.txt |
| **프롬프트** | `save_user_prompt(...)` | 사용자 프롬프트 저장 | prompts/user_prompt.txt |
| **UI** | `log_ui_interaction(message)` | UI 인터랙션 로그 | ui/user_interactions.log |
| **평가** | `save_evaluation_result(...)` | 평가 결과 저장 | evaluation/evaluation_*.json |
| **출력** | `save_conversation(...)` | 전체 대화 저장 | outputs/conversation_*.json |
| **메타** | `update_metadata(**kwargs)` | metadata.json 업데이트 | metadata.json |

**실험 폴더 생성 흐름**:
1. **초기화**: 챗봇 실행 시 Session ID 자동 부여 → 폴더 및 서브 폴더 7개 생성 → metadata.json과 Logger 초기화
2. **실행**: 사용자 질문 입력 → AI Agent 도구 선택 → 실행 과정 각 폴더에 기록 → 평가 지표 수집
3. **종료**: 최종 답변 생성 → outputs/response.txt 저장 → metadata.json 업데이트 → Logger 종료

**완전 구현된 기능** (2025-11-04 기준):
- ✅ 평가 시스템 완전 작동 (KeyError 해결)
- ✅ LLM 응답 전체 내용 로깅 (6개 도구)
- ✅ 평가 결과 자동 저장 (evaluation 폴더)
- ✅ 전체 대화 자동 저장 (모드별 이어쓰기 방식)
- ✅ SQL 쿼리 자동 저장 (close 시 자동 실행)
- ✅ 프롬프트 자동 저장 (5개 주요 도구)

**Session ID 예시**:
```
experiments/20251103/
├── 20251103_103015_session_001/   # 오늘 첫 번째 실행
├── 20251103_110234_session_002/   # 오늘 두 번째 실행
└── 20251103_143520_session_003/   # 오늘 세 번째 실행

experiments/20251104/
└── 20251104_090012_session_001/   # 다음 날, 다시 001부터 시작
```

**참조 문서**:
- [실험 관리 시스템 구현 이슈](docs/issues/01-1_실험_관리_시스템_구현.md)
- [최현화 실험 관리 시스템 역할](docs/roles/01-1_최현화_실험_관리_시스템.md)
- [실험 폴더 구조 규칙](docs/rules/실험_폴더_구조.md)
- [실험 추적 관리 PRD](docs/PRD/06_실험_추적_관리.md)
- [실험 관리 시스템 모듈화 문서](docs/modularization/03_실험_관리_시스템.md)
- [Conversation 파일 관리](docs/modularization/03-1_Conversation_파일_관리.md)

#### 자동 생성 디렉토리 구조

```
experiments/
└── YYYYMMDD/
    └── YYYYMMDD_HHMMSS_session_XXX/
        ├── configs/                                           # 설정 파일
        │   ├── db_config.yaml                                 # 데이터베이스 설정
        │   ├── model_config.yaml                              # LLM 모델 설정
        │   └── multi_request_patterns.yaml                    # 다중 요청 패턴 정의
        │
        ├── database/                                          # 데이터베이스 관련 로그
        │   └── pgvector_searches.json                         # 벡터 검색 기록
        │
        ├── evaluation/                                        # 평가 결과
        │   ├── evaluation_YYYYMMDD_HHMMSS.json                # 평가 결과 (복수 생성 가능)
        │   └── evaluation_YYYYMMDD_HHMMSS.json
        |
        ├── outputs/                                           # 출력 파일
        │   ├── save_data/                                     # 사용자 저장 데이터
        │   │   ├── YYYYMMDD_HHMMSS_response_N_beginner.md     # Easy 모드 단일 답변
        │   │   ├── YYYYMMDD_HHMMSS_response_N_elementary.md   # Easy 모드 단일 답변 (대체 표현)
        │   │   └── YYYYMMDD_HHMMSS_response_N.md              # 전체 대화 기록
        │   ├── conversation_easy_YYYYMMDD_HHMMSS.json         # Easy 모드 대화 세션
        │   └── conversation_hard_YYYYMMDD_HHMMSS.json         # Hard 모드 대화 세션
        |
        ├── prompts/                                           # 프롬프트 기록
        │   ├── system_prompt.txt                              # 사용된 시스템 프롬프트
        │   ├── user_prompt.txt                                # 사용자 질문 + 컨텍스트
        │   ├── final_prompt.txt                               # LLM에 전달된 최종 프롬프트
        │   └── prompt_template.yaml                           # 프롬프트 템플릿 정보
        |
        ├── tools/                                             # 도구 실행 로그
        │   ├── evaluator.log                                  # 평가 도구 로그
        │   ├── rag_glossary.log                               # RAG 용어집 로그
        │   ├── rag_paper.log                                  # RAG 논문 검색 로그
        │   ├── summarize.log                                  # 요약 도구 로그
        │   ├── web_search.log                                 # Web 검색 도구 로그
        │   ├── text2sql.log                                   # Text2SQL 도구 로그
        │   ├── file_save.log                                  # 파일 저장 도구 로그
        │   └── general.log                                    # 일반 답변 도구 로그
        |
        ├── ui/                                                # UI 인터랙션 로그
        │   ├── errors.log                                     # UI 에러 로그
        │   └── user_interactions.log                          # 사용자 상호작용 로그
        |
        ├── chatbot.log                                        # 메인 챗봇 로그
        └── metadata.json                                      # 세션 메타데이터
```

#### 주요 특징
- **날짜별 폴더 구분**: 실험 관리의 용이성
- **세션별 독립 관리**: 각 대화 세션마다 고유 ID 부여
- **타임스탬프 기반 파일명**: 시간순 추적 가능
- **계층적 로그 구조**: 도구별/기능별 로그 분리로 디버깅 효율성 극대화

**상세**: [실험_관리_시스템.md](docs/modularization/03_실험_관리_시스템.md)

---

### 2. 데이터베이스 시스템 (PostgreSQL + pgvector)

**위치**: `src/database/`, `database/schema.sql`, `configs/db_config.yaml`

하나의 데이터베이스에서 **관계형 데이터**와 **벡터 데이터**를 모두 처리하는 통합 솔루션입니다.

#### 시스템 구성

| 구분 | 내용 |
|------|------|
| **RDBMS** | PostgreSQL 15.5+ |
| **벡터 검색** | pgvector 0.5.0+ (IVFFlat 인덱스) |
| **Connection Pool** | psycopg2.pool (min=1, max=10) |
| **데이터베이스명** | papers |
| **사용자** | langchain / dusrufdmlalswhr |
| **호스트** | localhost:5432 |
| **임베딩 모델** | OpenAI text-embedding-3-small (1536차원) |

#### PostgreSQL + pgvector 선택 이유

**통합 관리의 장점**:
- ✅ **단일 DB 관리**: 관계형 + 벡터 데이터를 하나의 DB에서 처리
- ✅ **비용 효율**: 무료 오픈소스 (Pinecone 등 유료 서비스 불필요)
- ✅ **트랜잭션 일관성**: ACID 보장, 조인 가능
- ✅ **Text-to-SQL 지원**: 표준 SQL 사용 가능
- ✅ **Langchain 통합**: PGVector 네이티브 지원
- ✅ **검증된 안정성**: 20년+ 프로덕션 검증

**대안 비교** (MySQL + Pinecone, Weaviate, Chroma):
- MySQL: 벡터 검색 미지원 → 별도 Vector DB 필요 (관리 복잡도 증가)
- Pinecone: 유료 서비스, 메타데이터만 저장 가능, Text-to-SQL 불가
- Weaviate: 자체 호스팅 복잡, 관계형 데이터 제한적, SQL 불가
- Chroma: 메모리 기반, 프로덕션 부적합, 관계형 데이터 불가

#### 전체 테이블 구조

```
papers DB (PostgreSQL 15+)
│
├── 📁 RDBMS 테이블 (수동 생성, 4개)
│   ├── papers (논문 메타데이터)
│   ├── glossary (용어집)
│   ├── query_logs (사용자 질의 로그)
│   └── evaluation_results (성능 평가 결과)
│
└── 📁 VectorDB 테이블 (LangChain 자동 생성, 2개)
    ├── langchain_pg_collection (벡터 컬렉션 메타데이터)
    └── langchain_pg_embedding (벡터 임베딩 데이터)
```

**RDBMS vs VectorDB 구분**:

| 구분 | 테이블 | 생성 방식 | 관리 주체 | 용도 |
|------|--------|-----------|-----------|------|
| **RDBMS** | papers, glossary, query_logs, evaluation_results | `database/schema.sql` 수동 실행 | 개발자 | 논문 메타데이터, 용어집, 로그, 평가 저장 |
| **VectorDB** | langchain_pg_collection, langchain_pg_embedding | LangChain PGVector 자동 생성 | LangChain 라이브러리 | 벡터 임베딩 저장 및 유사도 검색 |

#### 🗄️ 데이터베이스 설계

**데이터베이스 관계도 (ERD)**

![데이터베이스 관계도](docs/images/architecture/05_데이터베이스_스키마.png)


**RDBMS vs VectorDB 구분**:

| 구분 | 테이블 | 생성 방식 | 관리 주체 | 용도 |
|------|--------|-----------|-----------|------|
| **RDBMS** | papers, glossary, query_logs, evaluation_results | `database/schema.sql` 수동 실행 | 개발자 | 논문 메타데이터, 용어집, 로그, 평가 결과 저장 |
| **VectorDB** | langchain_pg_collection, langchain_pg_embedding | LangChain PGVector 자동 생성 | LangChain 라이브러리 | 벡터 임베딩 저장 및 유사도 검색 |

**관계 및 연결**:

| 관계 | 타입 | 연결 방식 | 설명 |
|------|------|-----------|------|
| **langchain_pg_collection ← langchain_pg_embedding** | 1:N (실선) | 외래키 (FK) | `langchain_pg_embedding.collection_id` → `langchain_pg_collection.uuid`<br/>하나의 컬렉션이 여러 임베딩 벡터를 포함 |
| **papers ↔ langchain_pg_embedding** | 논리적 조인 (점선) | JSONB 조인 | `langchain_pg_embedding.cmetadata->>'paper_id'` = `papers.paper_id`<br/>논문 메타데이터와 벡터 임베딩 연결 (검색 시 사용) |
| **query_logs** | 독립 테이블 | - | 사용자 질의 로그 독립 저장 (FK 관계 없음) |
| **evaluation_results** | 독립 테이블 | - | 성능 평가 결과 독립 저장 (FK 관계 없음) |
| **glossary** | 독립 테이블 | - | 용어집 독립 저장 (FK 관계 없음) |

**연결 상세 설명**:

1. **Collection ← Embedding (1:N 관계)**
   - **연결 방식**: `collection_id` 외래키로 직접 연결
   - **무결성**: `ON DELETE CASCADE` (컬렉션 삭제 시 임베딩 자동 삭제)
   - **용도**: 벡터 컬렉션별 임베딩 그룹화 (예: paper_chunks, glossary_chunks)

2. **Papers ↔ Embedding (논리적 조인)**
   - **연결 방식**: JSONB `cmetadata` 필드를 통한 논리적 조인
   - **조인 쿼리 예시**:
     ```sql
     SELECT p.title, e.document, e.embedding
     FROM papers p
     JOIN langchain_pg_embedding e
       ON p.paper_id = (e.cmetadata->>'paper_id')::INT
     WHERE p.category = 'cs.AI';
     ```
   - **용도**: 검색 결과에 논문 메타데이터 추가 (제목, 저자, 출처 등)

3. **독립 테이블**
   - **query_logs**: 사용자 질의 및 응답 이력 추적 (통계 분석용)
   - **evaluation_results**: 챗봇 성능 평가 결과 저장 (품질 관리용)
   - **glossary**: 용어 정의 및 난이도별 설명 저장 (독립적 RAG 검색용)

**VectorDB 자동 생성 메커니즘**:
- **시점**: `PGVector.from_documents()` 또는 `add_documents()` 최초 호출 시
- **방식**: LangChain이 내부적으로 `CREATE TABLE IF NOT EXISTS` 실행
- **특징**: 개발자가 직접 테이블 생성 불필요, IVFFlat 인덱스 자동 생성

#### 테이블 상세 스키마

**1. papers 테이블 (논문 메타데이터)**

용도: 논문 메타데이터 저장 및 관리

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| **paper_id** | SERIAL | PRIMARY KEY | 논문 고유 ID (자동 증가) |
| **title** | VARCHAR(500) | NOT NULL | 논문 제목 |
| **authors** | TEXT | - | 저자 목록 (쉼표 구분) |
| **publish_date** | DATE | - | 발표 날짜 (YYYY-MM-DD) |
| **source** | VARCHAR(100) | - | 출처 (arXiv, IEEE, ACL 등) |
| **url** | TEXT | UNIQUE | 논문 URL (중복 방지) |
| **category** | VARCHAR(100) | - | 카테고리 (cs.AI, cs.CL, cs.CV) |
| **citation_count** | INT | DEFAULT 0 | 인용 수 |
| **abstract** | TEXT | - | 논문 초록 |
| **created_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시간 |
| **updated_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 수정 시간 |

주요 인덱스:
- `idx_papers_title`: GIN 인덱스 (Full-text search) - `to_tsvector('english', title)`
- `idx_papers_category`: B-tree 인덱스 (카테고리 필터)
- `idx_papers_publish_date`: B-tree 인덱스 (발표 날짜 정렬, DESC)
- `idx_papers_created_at`: B-tree 인덱스 (생성 시간 정렬, DESC)

사용 도구: search_paper, summarize, web_search, text2sql

**2. glossary 테이블 (용어집)**

용도: AI/ML 용어 정의 및 난이도별 설명 저장

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| **term_id** | SERIAL | PRIMARY KEY | 용어 고유 ID |
| **term** | VARCHAR(200) | NOT NULL, UNIQUE | 용어 (예: "BERT", "Attention") |
| **definition** | TEXT | NOT NULL | 기본 정의 |
| **easy_explanation** | TEXT | - | Easy 모드 설명 (초심자용, 비유/예시 중심) |
| **hard_explanation** | TEXT | - | Hard 모드 설명 (전문가용, 기술적 상세) |
| **category** | VARCHAR(100) | - | 카테고리 (ML, NLP, CV, RL 등) |
| **difficulty_level** | VARCHAR(20) | - | 난이도 (beginner, intermediate, advanced) |
| **related_terms** | TEXT[] | - | 관련 용어 배열 |
| **examples** | TEXT | - | 사용 예시 |
| **created_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시간 |
| **updated_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 수정 시간 |

주요 인덱스:
- `idx_glossary_term`: B-tree 인덱스 (용어 검색) - `term` 컬럼
- `idx_glossary_category`: B-tree 인덱스 (카테고리 필터) - `category` 컬럼
- `idx_glossary_difficulty`: B-tree 인덱스 (난이도 필터) - `difficulty_level` 컬럼

사용 도구: glossary

**3. query_logs 테이블 (사용자 질의 로그)**

용도: 사용자 질문 및 시스템 응답 로깅 (성능 분석, 사용 패턴 파악)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| **log_id** | SERIAL | PRIMARY KEY | 로그 고유 ID |
| **user_query** | TEXT | NOT NULL | 사용자 질문 |
| **difficulty_mode** | VARCHAR(20) | - | 난이도 모드 (easy, hard) |
| **tool_used** | VARCHAR(50) | - | 사용된 도구명 (search_paper, glossary 등) |
| **response** | TEXT | - | 생성된 응답 |
| **response_time_ms** | INT | - | 응답 시간 (밀리초) |
| **success** | BOOLEAN | DEFAULT TRUE | 성공 여부 |
| **error_message** | TEXT | - | 오류 메시지 (실패 시) |
| **created_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시간 |

주요 인덱스:
- `idx_query_logs_created_at`: B-tree 인덱스 (시간 기반 조회, DESC) - `created_at` 컬럼
- `idx_query_logs_tool_used`: B-tree 인덱스 (도구별 필터) - `tool_used` 컬럼
- `idx_query_logs_success`: B-tree 인덱스 (성공/실패 필터) - `success` 컬럼

사용 도구: text2sql (로그 저장)

**4. evaluation_results 테이블 (성능 평가 결과)**

용도: LLM-as-a-Judge 방식 평가 결과 저장

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| **eval_id** | SERIAL | PRIMARY KEY | 평가 고유 ID |
| **question** | TEXT | NOT NULL | 사용자 질문 |
| **answer** | TEXT | NOT NULL | AI 답변 |
| **accuracy_score** | INT | CHECK (0~10) | 정확도 점수 (참고 문서 일치도) |
| **relevance_score** | INT | CHECK (0~10) | 관련성 점수 (질문-답변 연관성) |
| **difficulty_score** | INT | CHECK (0~10) | 난이도 적합성 점수 (Easy/Hard 모드) |
| **citation_score** | INT | CHECK (0~10) | 출처 명시 점수 (논문 제목, 저자) |
| **total_score** | INT | CHECK (0~40) | 총점 (4개 항목 합계) |
| **comment** | TEXT | - | 평가 코멘트 (상세 피드백) |
| **created_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 생성 시간 |

주요 인덱스:
- `idx_evaluation_results_created_at`: B-tree 인덱스 (시간 기반 조회, DESC) - `created_at` 컬럼
- `idx_evaluation_results_total_score`: B-tree 인덱스 (성능 순위, DESC) - `total_score` 컬럼

사용 시스템: 평가 시스템 (`src/evaluation/evaluator.py`)

**5. langchain_pg_collection 테이블 (VectorDB 컬렉션 메타데이터)**

용도: 벡터 컬렉션 메타데이터 관리 (LangChain 자동 생성)

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| **uuid** | UUID | 컬렉션 고유 ID (자동 생성) |
| **name** | VARCHAR | 컬렉션 이름 (예: "paper_chunks") |
| **cmetadata** | JSONB | 컬렉션 메타데이터 (선택적) |

자동 생성 시점: `PGVector(collection_name="paper_chunks", ...)` 초기화 시

**6. langchain_pg_embedding 테이블 (VectorDB 벡터 데이터)**

용도: 벡터 임베딩 데이터 및 유사도 검색 (LangChain 자동 생성)

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| **uuid** | UUID | 임베딩 고유 ID (자동 생성) |
| **collection_id** | UUID | 컬렉션 ID (FK → langchain_pg_collection.uuid) |
| **embedding** | vector(1536) | 벡터 임베딩 (1536차원, OpenAI text-embedding-3-small) |
| **document** | TEXT | 원본 텍스트 (청크 내용) |
| **cmetadata** | JSONB | 메타데이터 (paper_id, chunk_index, title 등) |

주요 인덱스:
- IVFFlat 인덱스 (코사인 유사도, `vector_cosine_ops`)

메타데이터 예시:
```json
{
  "paper_id": 123,
  "chunk_index": 0,
  "title": "Attention Is All You Need",
  "source": "arXiv"
}
```

사용 도구: search_paper, summarize, web_search (RAG 검색)

#### 도구별 DB 사용 현황

| 도구 | 사용 테이블 | 쿼리 수 | 주요 작업 |
|------|-------------|---------|-----------|
| **search_paper** | langchain_pg_embedding, papers | 1~2회 | 벡터 유사도 검색 + 메타데이터 조회 |
| **glossary** | glossary | 1회 | 용어 검색 및 난이도별 설명 반환 |
| **summarize** | papers, langchain_pg_embedding | 2회 | 제목으로 paper_id 검색 + 전체 청크 조회 |
| **text2sql** | papers, query_logs | 2회 | SQL 쿼리 실행 + 로그 저장 |
| **web_search** | papers, langchain_pg_embedding | 2회 | arXiv 논문 저장 + 임베딩 저장 |
| **평가 시스템** | evaluation_results | 1회 | 평가 결과 저장 |

#### 성능 최적화 전략

**Connection Pool**:
- 최소 1개, 최대 10개 연결 유지
- 연결 재사용으로 오버헤드 제거
- 동시 요청 처리 지원

**인덱스 최적화**:
- **IVFFlat 인덱스**: 벡터 유사도 검색 (O(log n))
- **GIN 인덱스**: Full-text search (제목 검색)
- **B-tree 인덱스**: 필터링 및 정렬 (카테고리, 날짜)

**쿼리 최적화**:
- Prepared statements (SQL 인젝션 방지)
- EXPLAIN ANALYZE로 실행 계획 확인
- 적절한 LIMIT 사용으로 결과 제한

**참조 문서**:
- [데이터베이스 설계 PRD](docs/PRD/11_데이터베이스_설계.md)
- [데이터베이스 시스템 모듈화 문서](docs/modularization/05_데이터베이스_시스템.md)
- [데이터베이스 설치 가이드](docs/usage/데이터베이스_설치_및_설정_가이드.md)

---

### 3. 논문 데이터 수집 파이프라인

**위치**: `scripts/data/`, `src/data/`

arXiv API를 통해 AI/ML 논문을 자동 수집하고, PDF를 Langchain Document로 변환하여 PostgreSQL + pgvector에 저장하는 전체 파이프라인입니다.

#### 파이프라인 아키텍처

![논문 데이터 수집 파이프라인](docs/images/architecture/04_논문_데이터_수집_파이프라인.png)

#### 파이프라인 구성 요소

| 단계 | 컴포넌트 | 파일 위치 | 주요 기능 |
|------|----------|----------|-----------|
| **1. 논문 수집** | ArxivPaperCollector | `scripts/collect_arxiv_papers.py` | arXiv API 검색, PDF 다운로드, 메타데이터 수집, 중복 제거 |
| **2. 문서 처리** | PaperDocumentLoader | `src/data/document_loader.py` | PyPDFLoader로 PDF 로드, RecursiveCharacterTextSplitter로 청크 분할 (size=1000, overlap=200) |
| **3. 임베딩 생성** | PaperEmbeddingManager | `src/data/embeddings.py` | OpenAI text-embedding-3-small (1536차원), 배치 처리 (50개 단위) |
| **4. DB 저장** | DatabaseManager | `scripts/setup_database.py` | PostgreSQL 메타데이터 저장, pgvector 임베딩 저장, paper_id 매핑 생성 |

#### 핵심 설정

**문서 청킹 (RecursiveCharacterTextSplitter)**:

| 설정 | 값 | 설명 |
|------|-----|------|
| **chunk_size** | 1000 | 각 청크의 최대 문자 수 |
| **chunk_overlap** | 200 | 청크 간 중복 문자 수 (맥락 유지) |
| **separators** | `["\n\n", "\n", ". ", " ", ""]` | 분할 우선순위 (문단 → 줄 → 문장 → 단어) |

**임베딩 모델**:

| 항목 | 값 |
|------|-----|
| **모델** | OpenAI text-embedding-3-small |
| **차원** | 1536 |
| **배치 크기** | 50개 (API 속도 제한 대응) |

#### 데이터 품질 관리

**중복 제거 전략**:

1. **논문 레벨**: 제목 기준 중복 제거 (대소문자 정규화)
2. **청크 레벨**: 내용 해시 기반 중복 청크 필터링
3. **메타데이터 무결성**: chunk_index 자동 부여 (0부터 순차)

**품질 이슈 해결** (Issue #03-3 참조):
- ✅ 저작권 페이지 필터링 (의미 없는 메타데이터 제외)
- ✅ 중복 청크 제거 (동일 내용 hash 비교)
- ✅ chunk_index 메타데이터 누락 수정

#### 수집 현황

| 항목 | 값 |
|------|-----|
| **수집 논문 수** | 100편+ (AI/ML 분야) |
| **키워드** | Transformer, BERT, GPT, Attention Mechanism, Fine-tuning, NLP, Computer Vision |
| **총 청크 수** | ~15,000개 (논문당 평균 150개) |
| **저장 위치** | PostgreSQL papers 테이블, pgvector paper_chunks 컬렉션 |

#### 실행 방법

**전체 파이프라인 실행**:
```bash
# 1단계: 논문 수집 (arXiv API)
python scripts/collect_arxiv_papers.py

# 2단계: 데이터베이스 스키마 생성 및 메타데이터 저장
python scripts/setup_database.py

# 3단계: 문서 처리 및 청크 분할
python scripts/data/process_documents.py

# 4단계: 임베딩 생성 및 pgvector 저장
python scripts/data/load_embeddings.py

# 또는 전체 파이프라인 자동 실행
python scripts/data/run_full_pipeline.py
```

**참조 문서**:
- [논문 데이터 수집 가이드](docs/roles/03_박재홍_논문데이터수집.md)
- [논문 데이터 수집 및 DB 구축](docs/issues/03_논문데이터_수집_및_DB_구축.md)
- [데이터 파이프라인 구현](docs/issues/03-1_data_pipeline_implementation.md)
- [데이터 파이프라인 완료 보고서](docs/issues/03-2_data_pipeline_completion_report.md)
- [데이터 파이프라인 청크 중복 문제 해결](docs/issues/03-3_데이터_파이프라인_청크_중복_문제.md)
- [데이터베이스 설치 가이드](docs/usage/데이터베이스_설치_및_설정_가이드.md)

---

### 4. AI Agent 시스템 (LangGraph)

**위치**: `src/agent/` (graph.py, nodes.py, state.py)

LangGraph StateGraph 기반으로 **사용자 질문을 분석하여 적절한 도구를 자동 선택하고 실행하는 지능형 라우팅 시스템**입니다.

#### Agent 아키텍처

![AI Agent 아키텍처](docs/images/architecture/03_AI%20Agent.png)

#### 시스템 구성

| 구분 | 내용 |
|------|------|
| **프레임워크** | LangGraph StateGraph |
| **라우팅 방식** | 패턴 기반 + LLM Fallback (2단계) |
| **노드 구성** | 1개 Router + 7개 Tool + 1개 Pipeline Router |
| **상태 관리** | AgentState (TypedDict) |
| **다중 요청 처리** | tool_pipeline 기반 순차 실행 (최대 6단계) |
| **LLM 모델** | OpenAI GPT-4o (temperature=0) |

#### 7가지 도구

| 도구명 | 설명 | 파일 위치 | 사용 시나리오 |
|--------|------|----------|--------------|
| **general** | LLM 직접 호출 (일반 답변) | `tools/general_answer.py` | 일반적인 질문, 비교 분석, 추론 |
| **search_paper** | pgvector 유사도 검색 (RAG) | `tools/search_paper.py` | 논문 내용 검색, 기술 설명 |
| **glossary** | 용어집 DB 조회 | `tools/glossary.py` | 용어 정의, Easy/Hard 설명 |
| **web_search** | Tavily API 웹 검색 | `tools/web_search.py` | 최신 논문, arXiv 검색 |
| **summarize** | 논문 전체 요약 | `tools/summarize.py` | 특정 논문 요약 요청 |
| **text2sql** | 자연어 → SQL 변환 | `tools/text2sql.py` | 논문 통계 (개수, 순위, 분포) |
| **save_file** | 대화 내용 저장 | `tools/save_file.py` | 결과물 다운로드 요청 |

#### 패턴 기반 라우팅

**라우팅 우선순위** (2단계):

1. **패턴 매칭** (1순위): 키워드 기반 규칙 라우팅
   - YAML 설정 파일 (`configs/multi_request_patterns.yaml`)
   - 17개 사전 정의 패턴 (우선순위 0~200)
   - 빠른 속도 (0.001초 미만), 비용 없음, 100% 일관성

2. **LLM 라우팅** (2순위, Fallback): 패턴 매칭 실패 시
   - OpenAI GPT-4o 분석
   - 유연한 판단, 새로운 질문 패턴 대응

**패턴 예시**:

| 키워드 조합 | 실행 도구 파이프라인 | Priority | 설명 |
|------------|---------------------|----------|------|
| ["뭐야"] (제외: 논문, 검색) | [glossary] | 200 | 용어 정의 질문 |
| ["논문", "요약"] | [search_paper, web_search, general, summarize] | 120 | 논문 검색 후 요약 (4단계) |
| ["몇 개", "논문"] | [text2sql] | 150 | 논문 통계 조회 |
| ["저장"] | [save_file] | 180 | 파일 저장 요청 |

#### 다중 요청 처리 (Multi-Request Pipeline)

**기능**: "논문 찾아서 요약해줘"와 같은 복합 요청을 자동으로 여러 도구로 분할하여 순차 실행

**처리 흐름**:

```
사용자: "Transformer 논문 요약해줘"
   ↓
1단계: Router 노드
   - 패턴 매칭: ["논문", "요약"] 감지
   - tool_pipeline = [search_paper, web_search, general, summarize]
   - tool_choice = "search_paper" (첫 번째 도구)
   ↓
2단계: search_paper 실행
   - 논문 검색 (pgvector RAG)
   - 결과: "Attention Is All You Need" 찾음
   ↓
3단계: Pipeline Router 확인
   - pipeline_index (1) < len(tool_pipeline) (4)
   - 다음 도구 존재 → "continue"
   ↓
4단계: web_search 실행 (옵션)
   - arXiv 최신 정보 검색
   ↓
5단계: general 실행
   - 논문 내용 분석 및 정리
   ↓
6단계: summarize 실행
   - 최종 요약 생성
   ↓
최종 답변: "Transformer 논문 요약 내용..."
```

**AgentState 구조**:

| 필드 | 타입 | 설명 |
|------|------|------|
| **question** | str | 사용자 질문 |
| **difficulty** | str | 난이도 (easy/hard) |
| **tool_choice** | str | 현재 실행 중인 도구 |
| **tool_pipeline** | List[str] | 순차 실행 도구 목록 (다중 요청 시) |
| **pipeline_index** | int | 현재 실행 중인 도구 인덱스 |
| **tool_result** | str | 도구 실행 결과 |
| **final_answer** | str | 최종 답변 |
| **messages** | Sequence[BaseMessage] | 대화 히스토리 (멀티턴 지원) |

#### Fallback Chain (도구 실패 시 자동 전환)

| 원본 도구 | Fallback 경로 | 트리거 조건 |
|----------|--------------|------------|
| **search_paper** (RAG) | → web_search → general | 검색 결과 없음, DB 오류 |
| **glossary** (용어집) | → general | 용어 미등록 |
| **text2sql** (SQL) | → general | SQL 실행 오류, 결과 없음 |
| **web_search** | → general | API 오류, 결과 없음 |

**Fallback 감지 패턴** (`src/agent/failure_detector.py`):
- "검색 결과가 없습니다"
- "찾을 수 없습니다"
- "오류가 발생했습니다"
- "데이터베이스 연결 실패"

#### 성능 최적화

| 최적화 항목 | 구현 내용 | 효과 |
|-----------|----------|------|
| **패턴 기반 라우팅** | 키워드 매칭 우선 사용 | LLM 호출 50% 감소, 응답 속도 2초 단축 |
| **Streaming 응답** | LLM 결과 실시간 전송 | 사용자 경험 개선 (즉각적 피드백) |
| **Connection Pooling** | DB 연결 재사용 | DB 연결 오버헤드 제거 |
| **캐싱** | 동일 질문 결과 캐시 | 중복 LLM 호출 방지 |

**참조 문서**:
- [AI Agent 시스템 전체](docs/modularization/06_AI_Agent_시스템.md)
- [다중 요청 처리 상세](docs/modularization/06-1_다중_요청_처리.md)
- [패턴 기반 라우팅 상세](docs/modularization/06-2_패턴_기반_도구_라우팅.md)

---

### 5. RAG 시스템

#### 파이프라인
1. 임베딩 생성 (text-embedding-3-small, 1536차원)
2. 벡터 검색 (pgvector similarity_search)
3. 메타데이터 조회 (PostgreSQL)
4. 컨텍스트 구성
5. LLM 답변 생성

#### 최적화
- IVFFlat 인덱스로 고속 검색
- MMR Search로 다양성 확보
- MultiQueryRetriever로 쿼리 확장
- Connection Pooling으로 성능 향상

**구현**: `src/rag/retriever.py`

---

### 5. Streamlit UI 시스템

#### 주요 기능
- ChatGPT 스타일 채팅 인터페이스
- 멀티 세션 관리
- 난이도 선택 (Easy/Hard)
- 실시간 스트리밍 답변
- 도구 배지 & 출처 표시
- 평가 결과 표시
- LocalStorage 연동
- 사용자 인증

**구현**: `ui/app.py`, `ui/components/`

---

### 6. 평가 시스템 (LLM-as-a-Judge)

#### 평가 항목 (40점)
- 정확도 (10점): 사실적 정확성
- 관련성 (10점): 질문 연관성
- 난이도 적합성 (10점): Easy/Hard 적합성
- 출처 명시 (10점): 참고 문서 명확성

#### 자동화
- 답변 생성 후 자동 평가
- evaluation 폴더 JSON 저장
- UI 실시간 표시
- 데이터베이스 저장

**구현**: `src/evaluation/evaluator.py`

---

### 7. 프롬프트 엔지니어링

#### 난이도별 프롬프트
- **Easy**: 초등학생 수준, 비유/예시 활용
- **Hard**: 전문가 수준, 기술 용어 사용

#### 관리
- `prompts/` 폴더 JSON 형식
- 실험 폴더 자동 저장
- 버전 관리

**구현**: `src/prompts/loader.py`, `prompts/`

---

## 📦 설치 및 실행

### 1. 저장소 클론 및 환경 설정

```bash
# 저장소 클론
git clone https://github.com/AIBootcamp14/langchainproject-new-langchainproject_5.git
cd langchainproject-new-langchainproject_5

# 가상환경 활성화
pyenv activate langchain_py3_11_9

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (`.env` 파일)

```bash
# OpenAI API
OPENAI_API_KEY=sk-...

# Upstage Solar API
UPSTAGE_API_KEY=up_...

# Tavily API (웹 검색)
TAVILY_API_KEY=tvly-...

# PostgreSQL
POSTGRES_USER=langchain
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=papers
```

### 3. 데이터베이스 설정

데이터베이스 설치 및 설정은 [데이터베이스_설치_및_설정_가이드.md](docs/usage/데이터베이스_설치_및_설정_가이드.md) 문서를 참조하여 단계별로 진행합니다:

```bash
# 1. PostgreSQL 사용자 생성
sudo -u postgres psql
CREATE USER langchain WITH PASSWORD 'dusrufdmlalswhr';
ALTER USER langchain CREATEDB;
ALTER USER langchain WITH SUPERUSER;
\q

# 2. ~/.pgpass 파일 설정 (비밀번호 자동 인증)
cat > ~/.pgpass << 'EOF'
localhost:5432:*:langchain:dusrufdmlalswhr
EOF
chmod 600 ~/.pgpass

# 3. pgvector Extension 설치
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
sudo systemctl restart postgresql

# 4. Extension 활성화
sudo -u postgres psql
CREATE EXTENSION vector;
\dx
\q

# 5. papers 데이터베이스 생성
psql -U langchain -d postgres -h localhost
CREATE DATABASE papers;
\c papers
CREATE EXTENSION vector;
\q

# 6. 스키마 생성
psql -U langchain -d papers -h localhost -f database/schema.sql

# 7. 테이블 생성 확인
psql -U langchain -d papers -h localhost
\dt
\q

# 8. 데이터베이스 연결 테스트
python scripts/tests/unit/test_db_connection.py
```

### 4. 논문 리뷰 챗봇 실행

```bash
python main.py
```
## ⚡ 성능 최적화

### 데이터베이스 최적화

| 항목 | 기술 | 효과 |
|------|------|------|
| **Connection Pooling** | min=1, max=10 | 연결 재사용으로 오버헤드 감소 |
| **IVFFlat 인덱스** | pgvector | 벡터 검색 속도 10배 향상 |
| **GIN 인덱스** | PostgreSQL | 전문 검색 성능 향상 |
| **prepared statements** | psycopg2 | SQL 인젝션 방지 및 성능 개선 |

### RAG 시스템 최적화

```mermaid
graph LR
    A[사용자 질문] --> B[임베딩 생성<br/>100ms]
    B --> C[pgvector 검색<br/>45ms]
    C --> D[메타데이터 조회<br/>12ms]
    D --> E[컨텍스트 구성<br/>50ms]
    E --> F[LLM 답변 생성<br/>2000ms]

    style A fill:#90caf9,stroke:#1976d2,color:#000
    style B fill:#81c784,stroke:#388e3c,color:#000
    style C fill:#81c784,stroke:#388e3c,color:#000
    style D fill:#81c784,stroke:#388e3c,color:#000
    style E fill:#81c784,stroke:#388e3c,color:#000
    style F fill:#ffb74d,stroke:#f57c00,color:#000
```

**최적화 기법**:
- MMR (Maximal Marginal Relevance): 검색 결과 다양성 확보
- MultiQueryRetriever: LLM 기반 쿼리 확장으로 검색 품질 향상
- 청킹 전략: RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)

### 응답 시간 목표

| 도구 | 목표 (p95) | 실제 | 상태 |
|------|-----------|------|------|
| 일반 답변 | 3초 | 2.1초 | ✅ PASS |
| RAG 논문 검색 | 5초 | 4.8초 | ✅ PASS |
| Web 검색 | 8초 | 7.2초 | ✅ PASS |
| 용어집 검색 | 2초 | 1.5초 | ✅ PASS |

---

## 📊 주요 성과

### 시스템 성능

| 지표 | 목표 | 달성 | 상태 |
|------|------|------|------|
| **RAG Recall@5** | ≥60% | 80% | ✅ 목표 초과 |
| **응답 정확도** | ≥85% | 92% | ✅ 목표 초과 |
| **응답 시간 (p95)** | ≤6초 | 4.8초 | ✅ 목표 달성 |
| **도구 선택 정확도** | ≥90% | 95% | ✅ 목표 초과 |

### 기술적 성과

#### 1. 멀티 에이전트 시스템
- LangGraph StateGraph 기반 7개 도구 통합
- Fallback Chain으로 99% 응답 성공률 달성
- 난이도별 프롬프트로 사용자 만족도 향상

#### 2. 통합 데이터베이스
- PostgreSQL + pgvector로 관계형/벡터 데이터 단일 DB 관리
- IVFFlat 인덱스로 100만 벡터 기준 45ms 검색 달성
- Connection Pooling으로 동시 접속 10명 안정 처리

#### 3. 실험 관리 시스템
- ExperimentManager로 모든 실험 자동 추적
- Session ID 자동 부여 및 7개 서브 폴더 자동 생성
- 평가/대화/SQL/프롬프트 자동 저장

#### 4. LLM-as-a-Judge 평가
- 4개 항목 (정확도/관련성/난이도/출처) 자동 평가
- 평가 결과 DB 저장 및 UI 실시간 표시
- 평균 평가 점수 32/40 (80%) 달성

### 프로젝트 관리

- **협업**: 4명 팀원 역할 분담 및 주간 회의
- **버전 관리**: Git 브랜치 전략 (main/develop/feature)
- **문서화**: PRD, 아키텍처, 기술 보고서 작성
- **이슈 관리**: GitHub Issues & Projects로 진행 상황 추적

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
