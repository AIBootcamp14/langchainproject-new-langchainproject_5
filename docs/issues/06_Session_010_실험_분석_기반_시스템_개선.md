# 제목: Session 010 실험 분석 기반 시스템 개선

---

## 📋 작업 개요
- **작업 주제:** Session 010 실험 분석을 통해 발견된 8가지 문제점 개선
- **작성자:** 최현화[팀장]
- **담당자:** @최현화
- **마감일:** 2025-11-04 24:00

## 📅 기간
- 시작일: 2025-11-04
- 종료일: 2025-11-04

---

## 📌 이슈 목적

`experiments/20251104/20251104_213739_session_010` 폴더 분석을 통해 발견된 8가지 주요 문제점을 개선하여 시스템의 안정성과 사용성을 향상시킵니다.

**핵심 목표:**
- 파일 저장 로직 중복 제거 및 최적화
- conversation 파일 관리 체계 개선 (모드별 구분, 중복 방지)
- metadata.json 데이터 무결성 확보
- 다중 요청 처리 기능 구현
- 멀티턴 대화 기능 구현
- UI 동기화 및 사용성 개선

---

## 🔍 발견된 문제점 요약

### 분석 대상
- **세션 ID**: 010
- **실험 시작**: 2025-11-04 21:37:39
- **생성 파일**: 39개 (8개 디렉토리)
- **모드**: easy (초보자 모드 10개 질의응답)

### 주요 문제점 (우선순위별)

#### Critical (즉시 수정 필요)
1. **response.txt 중복 저장**: 매 답변마다 덮어쓰기 + 빈 타임스탬프 파일 생성
2. **conversation 파일 중복 생성**: 매 답변마다 새 파일 (10개), 모드 구분 없음
3. **metadata.json null 값**: difficulty, success, response_time_ms, end_time 미업데이트
4. **멀티턴 대화 불가**: messages=[] 전달로 이전 대화 참조 안됨

#### High Priority (중요 개선)
5. **다중 요청 처리 불가**: "논문 찾아서 요약해줘" → 단일 도구만 실행
6. **summary.md 위치**: outputs 루트에 저장 (summary 폴더로 이동 필요)

#### Medium Priority (개선 권장)
7. **UI 숫자 입력 동기화**: 슬라이더와 텍스트 입력 불일치
8. **복사 버튼 미작동**: JavaScript 실행 제한

---

## 📋 작업 항목 체크리스트

### Phase 1: 파일 저장 로직 개선 (Critical)

#### 1-1. response.txt 중복 저장 제거
- [x] `ui/components/chat_interface.py:322` response.txt 저장 로직 삭제
  - [x] 매 답변마다 response.txt 덮어쓰기 제거
  - [x] save_file 도구 실행 시에만 타임스탬프 파일 생성 유지

#### 1-2. conversation 파일 관리 개선
- [x] `src/utils/experiment_manager.py:559-572` save_conversation 메서드 수정
  - [x] 파일명에 difficulty 추가: `conversation_{difficulty}_{timestamp}.json`
  - [x] 세션당 하나의 conversation 파일 사용 (이어쓰기 방식)
  - [x] 기존 파일 존재 시 읽어서 새 메시지 추가

#### 1-3. summary.md 파일 위치 변경
- [x] `src/tools/summarize.py` 수정
  - [x] outputs/summary/ 폴더 생성 로직 추가
  - [x] 논문 제목을 파일명으로 사용 (특수문자 제거)
  - [x] summary/{논문제목}.md로 저장

### Phase 2: 메타데이터 무결성 확보 (Critical)

#### 2-1. metadata.json 업데이트 로직 보완
- [x] `ui/components/chat_interface.py:182-211` handle_agent_response 메서드 수정
  - [x] 시작 시간 기록 (start_time)
  - [x] difficulty 업데이트 추가
  - [x] 응답 완료 후 success=True, response_time_ms 계산 및 업데이트
  - [x] 에러 발생 시 success=False 업데이트

#### 2-2. 세션 종료 시 end_time 업데이트
- [x] `src/utils/experiment_manager.py:688` close 메서드 확인
  - [x] end_time 자동 업데이트 로직 유지

### Phase 3: 멀티턴 대화 기능 구현 (Critical)

#### 3-1. 이전 대화 전달 로직 구현
- [x] `ui/components/chat_interface.py:192-204` agent_executor.invoke 수정
  - [x] get_current_messages() 호출하여 이전 메시지 가져오기
  - [x] messages 필드에 이전 대화 전달 (빈 리스트 대신)

### Phase 4: 다중 요청 처리 기능 구현 (High Priority)

#### 4-1. 질문 분석 및 다중 도구 감지
- [x] `src/agent/nodes.py:48-96` router_node 메서드 수정
  - [x] 다중 요청 감지 로직 추가 (키워드 기반)
  - [x] 예: "논문 찾아서 요약해줘" → ["search_paper", "summarize"]
  - [x] tool_pipeline 필드 추가 (순차 실행 도구 목록)

#### 4-2. 순차 실행 메커니즘 구현
- [ ] `src/agent/graph.py` 그래프 수정
  - [ ] tool_pipeline 순회하며 순차 실행
  - [ ] 각 도구 결과를 다음 도구에 전달
  - [x] 기본 다중 요청 감지는 완료 (graph 수정은 향후 개선)

### Phase 5: UI 개선 (Medium Priority)

#### 5-1. 숫자 입력 동기화 완전 개선
- [x] `ui/components/sidebar.py:182-237` 용어 추출 설정 수정
  - [x] 슬라이더 변경 시 session_state 즉시 업데이트 (on_change 콜백)
  - [x] number_input도 session_state 직접 참조하도록 수정
  - [x] 양방향 완전 동기화 구현

#### 5-2. 복사 버튼 대안 제공
- [x] `ui/components/chat_interface.py:267-318` 복사 버튼 수정
  - [x] HTTPS 환경 확인 로직 추가 (환경 변수 체크)
  - [x] HTTP 환경 시 fallback: expander + st.code() 블록 제공
  - [x] 수동 복사 안내 메시지 추가

---

## 🔧 수정 대상 파일 목록

### 필수 수정 파일 (Critical)
1. `ui/components/chat_interface.py`
   - response.txt 저장 로직 삭제 (line 322)
   - metadata 업데이트 로직 추가 (line 155-164)
   - 멀티턴 대화 지원 (line 187-195)

2. `src/utils/experiment_manager.py`
   - save_conversation 메서드 수정 (line 559-572)
   - 파일명에 difficulty 추가
   - 이어쓰기 방식 구현

3. `src/tools/summarize.py`
   - summary.md 저장 위치 변경
   - outputs/summary/ 폴더로 이동

### 중요 수정 파일 (High Priority)
4. `src/agent/nodes.py`
   - router_node 메서드 수정 (line 30-74)
   - 다중 요청 감지 및 처리

5. `src/agent/graph.py`
   - 순차 실행 메커니즘 추가
   - tool_pipeline 지원

### 개선 권장 파일 (Medium Priority)
6. `ui/components/sidebar.py`
   - 용어 추출 숫자 입력 동기화 (line 182-237)

---

## 📝 상세 구현 가이드

### 1. conversation 파일 이어쓰기 구현

**기존 코드 (src/utils/experiment_manager.py:559-572):**
```python
def save_conversation(self, conversation_data: list):
    """전체 대화 기록 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 매번 새 타임스탬프
    conv_file = self.outputs_dir / f"conversation_{timestamp}.json"  # 모드 없음

    with open(conv_file, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, ensure_ascii=False, indent=2)

    self.logger.write(f"전체 대화 저장: {conv_file.name}")
```

**개선 코드:**
```python
def save_conversation(self, conversation_data: list, difficulty: str = "easy"):
    """전체 대화 기록 저장 (이어쓰기)"""
    # 세션당 하나의 파일 사용
    if not hasattr(self, 'conversation_file'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_file = self.outputs_dir / f"conversation_{difficulty}_{timestamp}.json"

    # 기존 내용 읽기 (있다면)
    if self.conversation_file.exists():
        with open(self.conversation_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # 새 메시지만 추가 (중복 방지)
    for msg in conversation_data:
        if msg not in existing_data:
            existing_data.append(msg)

    # 저장
    with open(self.conversation_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    self.logger.write(f"대화 저장: {self.conversation_file.name} ({len(existing_data)}개 메시지)")
```

### 2. metadata.json 업데이트 로직

**개선 코드 (ui/components/chat_interface.py):**
```python
def handle_agent_response(agent_executor, prompt: str, difficulty: str, exp_manager=None):
    # 시작 시간 기록
    start_time = datetime.now()

    # difficulty 업데이트
    if exp_manager:
        exp_manager.update_metadata(difficulty=difficulty)

    with st.chat_message("assistant"):
        try:
            # Agent 실행
            response = agent_executor.invoke(...)

            # 종료 시간 계산
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)

            # 성공 시 메타데이터 업데이트
            if exp_manager:
                exp_manager.update_metadata(
                    success=True,
                    response_time_ms=response_time_ms
                )

            # 답변 표시
            answer = response.get("final_answer", "...")
            # ...

        except Exception as e:
            # 실패 시 메타데이터 업데이트
            if exp_manager:
                exp_manager.update_metadata(
                    success=False,
                    error=str(e)
                )
            # ...
```

### 3. 멀티턴 대화 지원

**기존 코드:**
```python
response = agent_executor.invoke(
    {
        "question": prompt,
        "difficulty": difficulty,
        "messages": []          # 빈 리스트 (문제!)
    },
    config={"callbacks": [st_callback]}
)
```

**개선 코드:**
```python
from ui.components.chat_manager import get_current_messages

# 이전 대화 가져오기
previous_messages = get_current_messages()

response = agent_executor.invoke(
    {
        "question": prompt,
        "difficulty": difficulty,
        "messages": previous_messages  # 이전 대화 전달
    },
    config={"callbacks": [st_callback]}
)
```

### 4. 다중 요청 처리 (간단한 버전)

**개선 코드 (src/agent/nodes.py):**
```python
def router_node(state: AgentState, exp_manager=None):
    """라우터 노드: 다중 요청 감지"""
    question = state["question"]

    # 다중 요청 키워드 감지
    multi_keywords = {
        ("찾", "요약"): ["search_paper", "summarize"],
        ("검색", "정리"): ["search_paper", "summarize", "general"],
        ("논문", "설명"): ["search_paper", "general"]
    }

    # 단일 도구 선택 (기본)
    routing_prompt = get_routing_prompt().format(question=question)
    llm_client = LLMClient.from_difficulty(state.get("difficulty", "easy"))
    raw_response = llm_client.llm.invoke(routing_prompt).content.strip()
    tool_choice = raw_response.split()[0] if raw_response else "general"

    # 다중 요청 감지 시 tool_pipeline 설정
    for keywords, tools in multi_keywords.items():
        if all(kw in question for kw in keywords):
            state["tool_pipeline"] = tools
            state["tool_choice"] = tools[0]  # 첫 번째 도구부터 시작
            if exp_manager:
                exp_manager.logger.write(f"다중 요청 감지: {tools}")
            return state

    # 단일 요청
    state["tool_choice"] = tool_choice
    state["tool_pipeline"] = [tool_choice]

    return state
```

---

## ✅ 테스트 계획

### 1. response.txt 삭제 테스트
```
1. 챗봇 실행
2. 질문 입력 후 답변 받기
3. outputs 폴더 확인 → response.txt 없어야 함
4. "파일 저장해줘" 실행 → response_타임스탬프.txt 생성되어야 함
```

### 2. conversation 파일 테스트
```
1. easy 모드로 3개 질문
2. outputs/conversation_easy_타임스탬프.json 하나만 생성 확인
3. hard 모드로 2개 질문
4. outputs/conversation_hard_타임스탬프.json 생성 확인
5. 각 파일에 올바른 개수 메시지 확인
```

### 3. metadata.json 테스트
```
1. 챗봇 실행 후 질문
2. metadata.json 열기
3. difficulty, success, response_time_ms 값 확인
4. 세션 종료 후 end_time 값 확인
```

### 4. 멀티턴 대화 테스트
```
1. "Transformer 논문 찾아줘" 질문
2. "첫 번째 논문 요약해줘" 후속 질문
3. LLM이 이전 대화 참조하여 올바르게 답변하는지 확인
```

### 5. 다중 요청 테스트
```
1. "Transformer 논문 찾아서 요약해줘" 질문
2. 로그에서 tool_pipeline 확인
3. search_paper → summarize 순차 실행 확인
4. 최종 답변에 요약 포함 확인
```

---

## 📚 참고 문서
- [분석 보고서](../20251104/20251104_213739_session_010_실험_분석_보고서.md)
- [실험 관리 시스템 이슈](01-1_실험_관리_시스템_구현.md)
- [로깅 시스템 이슈](01-2_로깅_시스템_구현.md)

---

## 📌 완료 조건
- [x] 모든 Critical 문제점 수정 완료 (Phase 1-3)
- [x] 다중 요청 처리 기본 구현 완료 (Phase 4)
- [ ] 모든 테스트 통과
- [ ] 코드 리뷰 완료
- [x] Git 커밋 완료 (파일별 커밋, AI 출처 제외)
- [x] modularization 문서 업데이트

---

**작성일:** 2025-11-04
**최종 수정일:** 2025-11-04
