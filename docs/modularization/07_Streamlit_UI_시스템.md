# 07. Streamlit UI 시스템

## 📋 문서 정보
- **작성일**: 2025-11-03
- **시스템명**: Streamlit UI 시스템
- **구현 파일**: `ui/` (4개 파일)
- **우선순위**: ⭐⭐ (중요 - 사용자 인터페이스)
- **참고 문서**: Phase 1~3 구현 문서

---

## 📌 시스템 개요

### 목적 및 배경

Streamlit UI 시스템은 **논문 리뷰 챗봇의 웹 인터페이스**를 제공하는 시스템입니다. ChatGPT 스타일의 직관적인 UI를 통해 사용자가 AI Agent와 대화하고, 채팅 기록을 관리하며, 답변을 저장할 수 있습니다.

### 주요 특징

- **다중 채팅 세션 관리**: 여러 채팅을 동시에 유지하고 전환 가능
- **난이도 선택**: 초급(Easy) / 전문가(Hard) 모드 지원
- **ChatGPT 스타일 UI**: 날짜별 그룹화된 채팅 목록
- **메시지 복사 기능**: 각 AI 답변마다 복사 버튼 제공
- **채팅 저장/내보내기**: Markdown 형식으로 대화 기록 저장
- **실시간 Agent 통합**: LangGraph AI Agent와 실시간 연동

### 폴더 구조

```
ui/
├── app.py                        # 메인 애플리케이션
└── components/
    ├── sidebar.py                # 사이드바 컴포넌트
    ├── chat_interface.py         # 채팅 인터페이스
    └── chat_manager.py           # 채팅 세션 관리
```

---

## 🏗️ 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────────┐
│              Streamlit 애플리케이션              │
│                   (app.py)                      │
└─────────────────────────────────────────────────┘
           │                        │
           ▼                        ▼
┌──────────────────┐      ┌───────────────────┐
│   Sidebar        │      │  Chat Interface   │
│  (sidebar.py)    │      │(chat_interface.py)│
│                  │      │                   │
│ - 난이도 선택     │      │ - 메시지 표시      │
│ - 새 채팅 버튼   │      │ - 입력 처리        │
│ - 채팅 목록      │      │ - 복사/저장 버튼   │
│ - 저장/삭제      │      │ - Agent 호출       │
└──────────────────┘      └───────────────────┘
           │                        │
           └────────┬───────────────┘
                    ▼
          ┌──────────────────┐
          │  Chat Manager    │
          │(chat_manager.py) │
          │                  │
          │ - 세션 관리      │
          │ - CRUD 작업      │
          │ - 메시지 추가    │
          │ - 내보내기       │
          └──────────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ st.session_state │
          │  (세션 저장소)    │
          │                  │
          │ - chats: {}      │
          │ - current_chat_id│
          │ - last_difficulty│
          └──────────────────┘
```

### AI Agent 통합

```
사용자 입력 → chat_interface.py → agent_executor.invoke()
                                           ↓
                                    LangGraph Agent
                                           ↓
                                    6가지 도구 실행
                                           ↓
                                    답변 생성
                                           ↓
                                    UI에 표시
```

---

## 🔧 주요 컴포넌트

## 1. 메인 애플리케이션 (app.py)

### 역할

- Streamlit 애플리케이션 진입점
- 페이지 설정 및 레이아웃 구성
- Agent 및 ExperimentManager 초기화
- 환경 변수 검증

### 주요 기능

**페이지 설정:**
```python
st.set_page_config(
    page_title="논문 리뷰 챗봇",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

**Agent 초기화 (캐싱):**
```python
@st.cache_resource
def initialize_agent():
    exp_manager = ExperimentManager()
    agent_executor = create_agent_graph(exp_manager=exp_manager)
    return agent_executor, exp_manager
```

**환경 변수 검증:**
- `OPENAI_API_KEY`: 필수 (없으면 앱 중지)
- PostgreSQL 설정: 선택 (경고만 표시)

**레이아웃 구성:**
```python
# 헤더
st.title("📚 논문 리뷰 챗봇 (AI Agent + RAG)")

# 사이드바
difficulty = render_sidebar(exp_manager=exp_manager)

# 채팅 인터페이스
display_chat_history()
render_chat_input(agent_executor, difficulty, exp_manager)

# 푸터
render_chat_export_buttons()
```

---

## 2. 사이드바 (sidebar.py)

### 역할

- 난이도 선택 UI 제공
- 새 채팅 생성 버튼
- 채팅 목록 표시 (ChatGPT 스타일)
- 개별 채팅 저장/삭제 기능

### 주요 함수

#### `render_sidebar(exp_manager=None)`

**기능:**
- 사이드바 전체 UI 렌더링
- 선택된 난이도 반환

**구성 요소:**

1. **난이도 선택 섹션:**
```python
st.markdown("### ⚙️ 설정")

# 난이도 설명 (접기 가능)
with st.expander("ℹ️ 난이도 설명", expanded=False):
    st.markdown("""
    **🟢 초급 모드**: 쉬운 용어, 비유와 예시, 수식 최소화
    **🔴 전문가 모드**: 전문 용어, 수식 및 알고리즘, 기술적 세부사항
    """)

# 라디오 버튼
difficulty = st.radio(
    "난이도 선택",
    options=["easy", "hard"],
    format_func=lambda x: "🟢 초급" if x == "easy" else "🔴 전문가",
    horizontal=True
)
```

2. **새 채팅 버튼:**
```python
if st.button("➕ 새 채팅", use_container_width=True, type="primary"):
    selected_difficulty = st.session_state.difficulty_selector
    create_new_chat(selected_difficulty)
    st.rerun()
```

3. **채팅 목록:**
```python
chat_list = get_chat_list()
grouped_chats = group_chats_by_date(chat_list)

for group_name, chats in grouped_chats.items():
    st.markdown(f"**{group_name}**")  # 오늘, 어제, 지난 7일, 그 이전

    for chat_info in chats:
        # 현재 채팅은 강조 표시
        if is_current:
            st.markdown(f"<div style='background-color: rgba(255, 75, 75, 0.1);'>
                         {difficulty_icon} {title}</div>")
        else:
            # 버튼 3개: 전환, 저장, 삭제
            col1, col2, col3 = st.columns([5, 1, 1])
```

#### `group_chats_by_date(chat_list)`

**기능:**
- 채팅 목록을 날짜별로 그룹화 (ChatGPT 스타일)

**반환값:**
```python
{
    "오늘": [...],
    "어제": [...],
    "지난 7일": [...],
    "그 이전": [...]
}
```

**로직:**
- `datetime.now()` 기준으로 시간 계산
- 각 채팅의 `created_at` 비교
- 빈 그룹은 제거

---

## 3. 채팅 인터페이스 (chat_interface.py)

### 역할

- 채팅 기록 표시
- 사용자 입력 처리
- AI Agent 호출 및 응답 표시
- 복사/저장 버튼 제공

### 주요 함수

#### `display_chat_history()`

**기능:**
- 현재 채팅의 모든 메시지 표시
- 각 메시지마다 역할(user/assistant) 구분

**메시지 렌더링:**
```python
messages = get_current_messages()

for idx, message in enumerate(messages):
    role = message["role"]
    content = message["content"]

    if role == "user":
        with st.chat_message("user", avatar="🙋"):
            st.markdown(content)

    else:  # assistant
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(content)

            # 복사 버튼 추가 (JavaScript)
            unique_id = abs(hash(content + str(idx)))
            copy_button_html = f"""
            <button onclick="copyToClipboard_{unique_id}()">📋 복사</button>
            <script>
            function copyToClipboard_{unique_id}() {{
                navigator.clipboard.writeText({json.dumps(content)});
            }}
            </script>
            """
            st.markdown(copy_button_html, unsafe_allow_html=True)
```

**도구 사용 표시:**
```python
if "tool_choice" in message:
    tool_labels = {
        "general": "🗣️ 일반 답변",
        "search_paper": "📚 RAG 논문 검색",
        "web_search": "🌐 웹 검색",
        ...
    }
    st.caption(f"사용된 도구: {tool_labels[tool_choice]}")
```

#### `render_chat_input(agent_executor, difficulty, exp_manager)`

**기능:**
- 사용자 입력 처리
- Agent 호출 및 응답 표시
- 메시지 저장

**처리 흐름:**
```python
user_input = st.chat_input("질문을 입력하세요...")

if user_input:
    # 1. 사용자 메시지 추가
    add_message_to_current_chat("user", user_input)

    # 2. UI에 즉시 표시
    with st.chat_message("user", avatar="🙋"):
        st.markdown(user_input)

    # 3. Agent 호출
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("답변 생성 중..."):
            result = agent_executor.invoke({
                "question": user_input,
                "difficulty": difficulty
            })

            answer = result["final_answer"]
            tool_used = result.get("tool_choice")

    # 4. 답변 저장 및 표시
    add_message_to_current_chat("assistant", answer, tool_choice=tool_used)
    st.markdown(answer)

    st.rerun()  # 화면 갱신
```

#### `render_chat_export_buttons()`

**기능:**
- 전체 대화 복사/저장 버튼 제공
- 푸터 영역에 배치

**구현:**
```python
# 전체 대화 복사 버튼
export_text = export_current_chat()

copy_button_html = f"""
<button onclick="copyAllChat()">📋 전체 대화 복사</button>
<script>
function copyAllChat() {{
    navigator.clipboard.writeText({json.dumps(export_text)});
}}
</script>
"""
st.markdown(copy_button_html, unsafe_allow_html=True)

# 전체 대화 저장 버튼
st.download_button(
    label="💾 전체 대화 저장",
    data=export_text,
    file_name=f"chat_{timestamp}.md",
    mime="text/markdown"
)
```

---

## 4. 채팅 관리자 (chat_manager.py)

### 역할

- 채팅 세션 CRUD 작업
- 세션 상태 초기화 및 관리
- 메시지 추가/조회
- 채팅 내보내기

### 세션 상태 구조

**st.session_state:**
```python
{
    "chats": {
        "abc123": {
            "messages": [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "...", "tool_choice": "search_paper"}
            ],
            "difficulty": "easy",
            "created_at": "2025-11-03 10:30:15",
            "title": "Transformer 논문 설명해줘"
        },
        "def456": { ... }
    },
    "current_chat_id": "abc123",
    "last_difficulty": "easy"
}
```

### 주요 함수

#### `initialize_chat_sessions()`

**기능:**
- 세션 상태 초기화
- 앱 시작 시 1회 호출

```python
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "last_difficulty" not in st.session_state:
    st.session_state.last_difficulty = None
```

#### `create_new_chat(difficulty: str) -> str`

**기능:**
- 새 채팅 세션 생성
- 고유 ID 생성 (UUID 8자리)

```python
chat_id = str(uuid.uuid4())[:8]
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.session_state.chats[chat_id] = {
    "messages": [],
    "difficulty": difficulty,
    "created_at": timestamp,
    "title": "새 채팅"
}

st.session_state.current_chat_id = chat_id
return chat_id
```

#### `update_chat_title(chat_id: str, first_message: str)`

**기능:**
- 첫 번째 메시지로 채팅 제목 자동 생성
- 50자로 제한

```python
title = first_message.strip()

if len(title) > 50:
    title = title[:50]
    last_space = title.rfind(' ')
    if last_space > 30:
        title = title[:last_space]
    title += "..."

st.session_state.chats[chat_id]["title"] = title
```

#### `switch_chat(chat_id: str)`

**기능:**
- 다른 채팅으로 전환

```python
if chat_id in st.session_state.chats:
    st.session_state.current_chat_id = chat_id
    st.session_state.last_difficulty = st.session_state.chats[chat_id]["difficulty"]
```

#### `delete_chat(chat_id: str)`

**기능:**
- 채팅 세션 삭제
- 현재 채팅 삭제 시 다른 채팅으로 자동 전환

```python
del st.session_state.chats[chat_id]

if st.session_state.current_chat_id == chat_id:
    if st.session_state.chats:
        st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
    else:
        st.session_state.current_chat_id = None
```

#### `export_chat(chat_id: str) -> str`

**기능:**
- 특정 채팅을 Markdown 형식으로 변환

**출력 형식:**
```markdown
# 채팅 기록

**제목**: Transformer 논문 설명해줘
**난이도**: easy
**생성 시간**: 2025-11-03 10:30:15
**메시지 수**: 10

---

## [1] 🙋 사용자

Transformer 논문 설명해줘

---

## [2] 🤖 AI

Transformer는 2017년 Google이 발표한...

*사용된 도구: 📚 RAG 논문 검색*

---

...
```

---

## 🎨 핵심 기능

### 1. 다중 채팅 세션 관리

**특징:**
- 무제한 채팅 세션 생성 가능
- 각 채팅마다 독립적인 난이도 설정
- 세션 간 전환 시 대화 기록 유지
- 채팅별 고유 ID (UUID 8자리)

**구현 방식:**
```python
# 채팅 생성
create_new_chat("easy")

# 채팅 전환
switch_chat("abc123")

# 채팅 삭제
delete_chat("abc123")
```

### 2. 난이도 선택 시스템

**두 가지 모드:**

| 난이도 | 아이콘 | LLM 모델 | 프롬프트 스타일 | 사용 사례 |
|--------|--------|----------|----------------|----------|
| **Easy** | 🟢 | GPT-3.5-turbo / Solar-mini | 쉬운 용어, 비유, 예시 | 초심자, 학부생 |
| **Hard** | 🔴 | GPT-4 / Solar-pro | 전문 용어, 수식, 알고리즘 | 전문가, 대학원생 |

**적용 범위:**
- 모든 도구에서 난이도별 프롬프트 사용
- LLM 모델 자동 선택 (LLMClient.from_difficulty)
- 채팅마다 난이도 독립 설정

### 3. 메시지 복사 기능

**개별 메시지 복사:**
- 각 AI 답변마다 "📋 복사" 버튼
- JavaScript Clipboard API 사용
- 복사 성공 시 "✅ 복사됨!" 표시 (2초)

**전체 대화 복사:**
- 푸터의 "📋 전체 대화 복사" 버튼
- Markdown 형식으로 복사
- 모든 메시지 + 메타데이터 포함

**구현 방식:**
```javascript
navigator.clipboard.writeText(content).then(
    function() {
        button.textContent = '✅ 복사됨!';
        setTimeout(() => { button.textContent = '📋 복사'; }, 2000);
    },
    function(err) {
        alert('❌ 복사 실패: ' + err);
    }
);
```

### 4. 채팅 저장/내보내기

**개별 채팅 저장:**
- 사이드바 각 채팅의 "💾" 버튼
- 파일명: `chat_{제목}_{타임스탬프}.md`
- Markdown 형식

**전체 대화 저장:**
- 푸터의 "💾 전체 대화 저장" 버튼
- 파일명: `chat_{타임스탬프}.md`
- 브라우저 다운로드 기능 사용

**Markdown 형식 예시:**
```markdown
# 채팅 기록

**제목**: Transformer 논문
**난이도**: easy
**생성 시간**: 2025-11-03 10:30:15
**메시지 수**: 4

---

## [1] 🙋 사용자
...

## [2] 🤖 AI
...
*사용된 도구: 📚 RAG 논문 검색*
```

### 5. ChatGPT 스타일 UI

**날짜별 그룹화:**
```
💬 채팅 기록
───────────────
오늘
  🟢 Transformer 논문 설명
  🔴 BERT 모델 분석

어제
  🟢 Attention 메커니즘

지난 7일
  🔴 최신 LLM 논문

그 이전
  🟢 논문 요약 요청
```

**현재 채팅 강조:**
- 배경색 강조 (rgba(255, 75, 75, 0.1))
- 왼쪽 테두리 (3px solid #FF4B4B)
- 버튼 비활성화 (전환 불가)

**버튼 구성:**
- **전환**: 해당 채팅으로 이동
- **저장**: Markdown 파일 다운로드
- **삭제**: 채팅 세션 삭제

---

## 🔄 세션 상태 관리

### Streamlit Session State

**개념:**
- 페이지 새로고침 간 데이터 유지
- 딕셔너리 형태로 접근
- 컴포넌트 간 데이터 공유

**사용 이유:**
- Streamlit은 매 인터랙션마다 스크립트 재실행
- Session State로 채팅 기록 영구 저장
- 세션 동안만 유지 (브라우저 닫으면 삭제)

### 주요 변수

```python
st.session_state.chats              # 모든 채팅 데이터
st.session_state.current_chat_id    # 현재 활성 채팅 ID
st.session_state.last_difficulty    # 마지막 선택 난이도
st.session_state.difficulty_selector # 라디오 버튼 상태
```

### 데이터 흐름

```
사용자 입력
    ↓
chat_interface.py (입력 처리)
    ↓
chat_manager.py (메시지 추가)
    ↓
st.session_state.chats 업데이트
    ↓
st.rerun() (화면 갱신)
    ↓
display_chat_history() (메시지 표시)
```

---

## 🔗 AI Agent 통합

### Agent 호출 워크플로우

```python
# 1. 사용자 입력
user_input = st.chat_input("질문을 입력하세요...")

# 2. Agent 호출
result = agent_executor.invoke({
    "question": user_input,
    "difficulty": difficulty
})

# 3. 결과 추출
answer = result["final_answer"]
tool_used = result.get("tool_choice")

# 4. 메시지 저장
add_message_to_current_chat("assistant", answer, tool_choice=tool_used)
```

### ExperimentManager 통합

**로깅 위치:**
```
experiments/20251103/20251103_103015_session_001/
├── metadata.json           # 세션 메타데이터
├── logger_main.log         # 메인 로그
├── system_prompts/         # 시스템 프롬프트
├── user_prompts/           # 사용자 프롬프트
└── tools/                  # 도구별 로그
    ├── web_search_001.log
    ├── search_paper_001.log
    └── ...
```

**UI 인터랙션 로깅:**
```python
exp_manager.log_ui_interaction("새 채팅 생성: 난이도=easy")
exp_manager.log_ui_interaction("채팅 전환: abc123")
exp_manager.log_ui_interaction("채팅 삭제: def456")
```

---

## 📊 기술 스택

### 프론트엔드

| 기술 | 버전 | 용도 |
|------|------|------|
| **Streamlit** | 1.41.1 | 웹 UI 프레임워크 |
| **HTML/CSS** | - | 커스텀 스타일링 |
| **JavaScript** | - | 복사 기능 (Clipboard API) |

### 상태 관리

| 컴포넌트 | 저장소 | 범위 |
|----------|--------|------|
| **채팅 데이터** | st.session_state | 세션 |
| **현재 채팅 ID** | st.session_state | 세션 |
| **Agent 인스턴스** | st.cache_resource | 애플리케이션 |

### 백엔드 통합

- **LangGraph Agent**: AI 답변 생성
- **ExperimentManager**: 로깅 및 실험 추적
- **PostgreSQL**: 논문 및 용어 데이터
- **OpenAI API**: LLM 모델 호출

---

## 🚀 실행 방법

### 로컬 실행

```bash
# 1. 환경 변수 설정 (.env 파일)
OPENAI_API_KEY=your_key_here
POSTGRES_USER=langchain
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_DB=langchain_project

# 2. Streamlit 앱 실행
streamlit run ui/app.py

# 3. 브라우저에서 접속
# http://localhost:8501
```

### 포트 변경

```bash
streamlit run ui/app.py --server.port 8502
```

### 헤드리스 모드 (서버 배포)

```bash
streamlit run ui/app.py --server.headless true
```

---

## ⚠️ 주의사항

### Session State 관리

- **브라우저 새로고침 시 세션 초기화**: 채팅 기록 손실
- **해결책**: 중요한 대화는 저장 기능 사용

### JavaScript 복사 기능

- **HTTPS 필요**: 일부 브라우저에서 Clipboard API 제한
- **Fallback**: `document.execCommand('copy')` 사용 고려

### Agent 호출 시간

- **Web Search**: 5~10초 소요
- **RAG 검색**: 2~5초 소요
- **UI Spinner**: `st.spinner()` 사용으로 사용자 경험 개선

### 동시 사용자

- **Session State 격리**: 사용자별 독립적인 세션
- **Agent 캐싱**: `@st.cache_resource`로 공유

---

## 🎯 향후 개선 사항

### 데이터 영속성

- **LocalStorage 통합**: 브라우저 새로고침 시에도 채팅 유지
- **PostgreSQL 저장**: 사용자 계정별 채팅 기록 DB 저장

### 사용자 인증

- **로그인 시스템**: Streamlit-Authenticator 통합
- **채팅 공유 기능**: URL로 특정 채팅 공유

### UI/UX 개선

- **다크 모드**: 테마 전환 기능
- **검색 기능**: 채팅 목록 검색
- **메시지 편집**: 사용자 메시지 수정 기능
- **Streaming 답변**: 실시간 답변 생성 표시

### 성능 최적화

- **Lazy Loading**: 긴 채팅 기록 페이지네이션
- **Agent 병렬 처리**: 여러 도구 동시 호출
- **캐싱 확대**: 검색 결과 캐싱

---

## 📚 참고 자료

- [Streamlit Documentation](https://docs.streamlit.io/)
- [ChatGPT UI Design Pattern](https://openai.com/chatgpt)
- [Clipboard API MDN](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API)
- `docs/modularization/03_AI_Agent_시스템.md` - Agent 통합
- `docs/modularization/02_실험_관리_시스템.md` - ExperimentManager

---

## ✅ 체크리스트

- [x] 다중 채팅 세션 관리
- [x] 난이도 선택 (Easy/Hard)
- [x] ChatGPT 스타일 UI (날짜별 그룹화)
- [x] 개별 메시지 복사 버튼
- [x] 전체 대화 복사/저장
- [x] 개별 채팅 저장 (.md)
- [x] Agent 실시간 통합
- [x] ExperimentManager 로깅
- [ ] 데이터 영속성 (LocalStorage/DB)
- [ ] 사용자 인증
- [ ] 다크 모드
