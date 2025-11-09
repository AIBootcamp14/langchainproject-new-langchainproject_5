## 제목 : ExperimentManager 도구별 로그 기록 미구현 (3개 도구)

---

## 📋 작업 개요
- **작업 주제:** Text2SQL, 파일 저장, 일반 답변 도구의 get_tool_logger 통합
- **작성자:** 최현화[팀장]
- **담당자:** @최현화
- **우선순위:** Medium
- **예상 소요 시간:** 1시간

## 📅 기간
- 시작일: 2025-11-09
- 종료일: 2025-11-09

---

## 📌 이슈 목적

ExperimentManager의 `get_tool_logger()` 메서드는 7개 AI Agent 도구별로 독립적인 로그 파일을 생성하도록 설계되었으나, 현재 4개 도구에만 구현되어 있습니다. 나머지 3개 도구(Text2SQL, 파일 저장, 일반 답변)에도 동일한 로깅 시스템을 통합하여 실험 추적의 완전성을 확보합니다.

**핵심 목표:**
- Text2SQL 도구 로그 기록 구현
- 파일 저장 도구 로그 기록 구현
- 일반 답변 도구 로그 기록 구현
- 7개 도구 모두 일관된 로그 형식 유지

---

## 🔍 현재 상태 분석

### ✅ 로그 기록이 구현된 도구 (4개)

| 도구명 | 파일 경로 | 로그 파일 | 구현 코드 위치 |
|--------|-----------|-----------|----------------|
| **RAG 논문 검색** | `src/tools/search_paper.py` | `tools/rag_paper.log` | line 437: `tool_logger = exp_manager.get_tool_logger('rag_paper')` |
| **RAG 용어집** | `src/tools/glossary.py` | `tools/rag_glossary.log` | line 445: `tool_logger = exp_manager.get_tool_logger('rag_glossary')` |
| **웹 검색** | `src/tools/web_search.py` | `tools/web_search.log` | line 37: `tool_logger = exp_manager.get_tool_logger('web_search')` |
| **논문 요약** | `src/tools/summarize.py` | `tools/summarize.log` | line 47: `tool_logger = exp_manager.get_tool_logger('summarize')` |

**구현 패턴:**
```python
# 도구별 Logger 생성
tool_logger = exp_manager.get_tool_logger('도구명') if exp_manager else None

# 주요 이벤트 로깅
if tool_logger:
    tool_logger.write(f"도구 실행 시작 - 입력: {input_data}")
    tool_logger.write(f"검색 결과: {result_count}개 발견")
    tool_logger.write(f"도구 실행 완료 - 소요 시간: {elapsed_time}ms")
```

### ❌ 로그 기록이 미구현된 도구 (3개)

| 도구명 | 파일 경로 | 예상 로그 파일 | 현재 상태 |
|--------|-----------|----------------|-----------|
| **Text2SQL 통계** | `src/tools/text2sql.py` | `tools/text2sql.log` | ❌ `get_tool_logger()` 미호출 |
| **파일 저장** | `src/tools/save_file.py` | `tools/file_save.log` | ❌ `get_tool_logger()` 미호출 |
| **일반 답변** | `src/tools/general_answer.py` | `tools/general.log` | ❌ `get_tool_logger()` 미호출 |

---

## 🚨 문제점 및 영향

### 1. 실험 추적 불완전
- **문제**: 3개 도구 실행 시 도구별 독립 로그가 생성되지 않음
- **영향**:
  - `tools/` 폴더에 4개 로그만 존재 (7개 중 3개 누락)
  - Text2SQL 쿼리 생성 과정 추적 불가
  - 파일 저장 이력 추적 불가
  - 일반 답변 생성 과정 추적 불가
- **재현 방법**:
  1. 챗봇에서 "논문 통계 알려줘" 질문 (Text2SQL 도구 실행)
  2. `experiments/날짜/세션ID/tools/` 폴더 확인
  3. `text2sql.log` 파일 생성 안 됨 확인

### 2. 디버깅 효율성 저하
- **문제**: 3개 도구의 오류 발생 시 추적 어려움
- **영향**:
  - Text2SQL 실패 원인 파악 시 메인 `chatbot.log`만 확인 가능
  - 도구별 세부 로그 없어 오류 원인 분석 시간 증가
  - LLM 응답 전체 내용 기록 누락 (6개 도구 중 3개만 기록)

### 3. 일관성 부족
- **문제**: 4개 도구는 로그 있고, 3개 도구는 로그 없음
- **영향**:
  - README.md 문서와 실제 구현 불일치
  - 실험 관리 시스템의 신뢰도 저하
  - 팀원 간 혼란 발생 가능

---

## ✅ 작업 항목 체크리스트

### Phase 1: Text2SQL 도구 로그 기록 구현 (20분)
- [ ] `src/tools/text2sql.py` 파일 수정
  - [ ] `get_tool_logger('text2sql')` 호출 추가
  - [ ] 도구 실행 시작 로그 추가
    - [ ] 사용자 질문 기록
    - [ ] 난이도 모드 기록
  - [ ] SQL 쿼리 생성 과정 로그
    - [ ] LLM에 전달한 프롬프트 기록
    - [ ] 생성된 SQL 쿼리 기록
    - [ ] 쿼리 실행 결과 개수 기록
  - [ ] 도구 실행 완료 로그
    - [ ] 최종 결과 요약 기록
    - [ ] 소요 시간 기록
- [ ] 테스트
  - [ ] "2024년 논문 개수 알려줘" 질문 실행
  - [ ] `tools/text2sql.log` 파일 생성 확인
  - [ ] 로그 내용 완전성 검증

### Phase 2: 파일 저장 도구 로그 기록 구현 (15분)
- [ ] `src/tools/save_file.py` 파일 수정
  - [ ] `get_tool_logger('file_save')` 호출 추가
  - [ ] 도구 실행 시작 로그 추가
    - [ ] 저장 요청 파일명 기록
    - [ ] 저장 데이터 길이 기록
  - [ ] 파일 저장 과정 로그
    - [ ] 저장 경로 기록
    - [ ] 파일 크기 기록
    - [ ] 저장 성공/실패 여부 기록
  - [ ] 도구 실행 완료 로그
    - [ ] 최종 저장 경로 기록
    - [ ] 소요 시간 기록
- [ ] 테스트
  - [ ] "논문 요약 결과 파일로 저장해줘" 질문 실행
  - [ ] `tools/file_save.log` 파일 생성 확인
  - [ ] 로그 내용 완전성 검증

### Phase 3: 일반 답변 도구 로그 기록 구현 (15분)
- [ ] `src/tools/general_answer.py` 파일 수정
  - [ ] `get_tool_logger('general')` 호출 추가
  - [ ] 도구 실행 시작 로그 추가
    - [ ] 사용자 질문 기록
    - [ ] 난이도 모드 기록
    - [ ] Fallback 여부 기록 (다른 도구 실패 후 전환)
  - [ ] LLM 호출 과정 로그
    - [ ] 사용된 프롬프트 템플릿 기록
    - [ ] LLM 응답 전체 내용 기록
    - [ ] 토큰 사용량 기록
  - [ ] 도구 실행 완료 로그
    - [ ] 최종 답변 길이 기록
    - [ ] 소요 시간 기록
- [ ] 테스트
  - [ ] "안녕하세요" 질문 실행 (일반 답변 도구 사용)
  - [ ] `tools/general.log` 파일 생성 확인
  - [ ] 로그 내용 완전성 검증

### Phase 4: 통합 테스트 및 검증 (10분)
- [ ] 7개 도구 모두 실행하여 로그 생성 확인
  - [ ] RAG 용어집: "Transformer 뜻 알려줘"
  - [ ] RAG 논문: "Attention 논문 찾아줘"
  - [ ] 웹 검색: "2025년 최신 LLM 논문 검색"
  - [ ] 논문 요약: "Attention is All You Need 요약해줘"
  - [ ] Text2SQL: "2024년 논문 개수 알려줘"
  - [ ] 파일 저장: "요약 결과 저장해줘"
  - [ ] 일반 답변: "안녕하세요"
- [ ] `tools/` 폴더에 7개 로그 파일 모두 존재 확인
  ```
  tools/
  ├── rag_glossary.log
  ├── rag_paper.log
  ├── web_search.log
  ├── summarize.log
  ├── text2sql.log
  ├── file_save.log
  └── general.log
  ```
- [ ] 각 로그 파일 내용 검증
  - [ ] 타임스탬프 정상 기록 확인
  - [ ] 주요 이벤트 모두 기록 확인
  - [ ] 로그 형식 일관성 확인

---

## 📝 구현 가이드

### 1. 코드 위치 및 추가 방법

#### Text2SQL 도구 (`src/tools/text2sql.py`)
```python
def text2sql_node(state: AgentState) -> AgentState:
    """Text2SQL 통계 조회 노드"""
    # ============ 도구별 Logger 생성 ============
    exp_manager = state.get("exp_manager")
    tool_logger = exp_manager.get_tool_logger('text2sql') if exp_manager else None

    # ============ 도구 실행 시작 로그 ============
    question = state.get("question", "")
    difficulty = state.get("difficulty", "easy")

    if tool_logger:
        tool_logger.write(f"Text2SQL 노드 실행 - 질문: {question}, 난이도: {difficulty}")

    # ... (기존 로직) ...

    # ============ SQL 쿼리 생성 로그 ============
    if tool_logger:
        tool_logger.write(f"생성된 SQL 쿼리:\n{generated_sql}")
        tool_logger.write(f"쿼리 실행 결과: {result_count}개 행 반환")

    # ============ 도구 실행 완료 로그 ============
    if tool_logger:
        tool_logger.write(f"Text2SQL 실행 완료 - 소요 시간: {elapsed_time}ms")

    return state
```

#### 파일 저장 도구 (`src/tools/save_file.py`)
```python
def file_save_node(state: AgentState) -> AgentState:
    """파일 저장 노드"""
    # ============ 도구별 Logger 생성 ============
    exp_manager = state.get("exp_manager")
    tool_logger = exp_manager.get_tool_logger('file_save') if exp_manager else None

    # ============ 도구 실행 시작 로그 ============
    filename = state.get("filename", "unknown")
    data_length = len(state.get("data_to_save", ""))

    if tool_logger:
        tool_logger.write(f"파일 저장 노드 실행 - 파일명: {filename}, 데이터 크기: {data_length}자")

    # ... (기존 로직) ...

    # ============ 파일 저장 완료 로그 ============
    if tool_logger:
        tool_logger.write(f"파일 저장 완료 - 경로: {save_path}, 크기: {file_size}bytes")

    return state
```

#### 일반 답변 도구 (`src/tools/general_answer.py`)
```python
def general_answer_node(state: AgentState) -> AgentState:
    """일반 답변 노드"""
    # ============ 도구별 Logger 생성 ============
    exp_manager = state.get("exp_manager")
    tool_logger = exp_manager.get_tool_logger('general') if exp_manager else None

    # ============ 도구 실행 시작 로그 ============
    question = state.get("question", "")
    difficulty = state.get("difficulty", "easy")
    is_fallback = state.get("tool_status") == "failed"  # Fallback 여부

    if tool_logger:
        fallback_msg = " (Fallback)" if is_fallback else ""
        tool_logger.write(f"일반 답변 노드 실행{fallback_msg} - 질문: {question}, 난이도: {difficulty}")

    # ... (LLM 호출 로직) ...

    # ============ LLM 응답 로그 ============
    if tool_logger and llm_response:
        tool_logger.write(f"LLM 응답 전체 내용:\n{llm_response}")
        tool_logger.write(f"토큰 사용량: {token_count}개")

    # ============ 도구 실행 완료 로그 ============
    if tool_logger:
        tool_logger.write(f"일반 답변 생성 완료 - 답변 길이: {len(final_answer)}자")

    return state
```

### 2. 로그 형식 통일 가이드

모든 도구는 다음 형식을 따라야 합니다:

```
[YYYY-MM-DD HH:MM:SS] 도구 실행 시작 - 입력 정보
[YYYY-MM-DD HH:MM:SS] 주요 처리 과정 로그
[YYYY-MM-DD HH:MM:SS] 결과 데이터 로그
[YYYY-MM-DD HH:MM:SS] 도구 실행 완료 - 요약 정보
```

### 3. 필수 기록 항목

모든 도구 로그에 반드시 포함되어야 할 항목:
1. **실행 시작**: 입력 데이터 (질문, 난이도 등)
2. **처리 과정**: 핵심 로직 실행 내용 (LLM 호출, DB 조회 등)
3. **결과 데이터**: 생성된 데이터 전체 내용 또는 요약
4. **실행 완료**: 소요 시간, 성공/실패 여부

---

## 🎯 완료 기준

### 기능적 완료 기준
- [ ] 7개 도구 모두 `get_tool_logger()` 호출
- [ ] 각 도구 실행 시 해당 로그 파일 자동 생성
- [ ] 로그 파일 내용에 최소 4가지 필수 항목 포함
- [ ] 로그 파일 형식이 기존 4개 도구와 일관성 유지

### 테스트 완료 기준
- [ ] 7개 도구 각각 최소 1회 실행 테스트 통과
- [ ] `tools/` 폴더에 7개 로그 파일 모두 존재
- [ ] 각 로그 파일이 비어있지 않고 유의미한 내용 포함
- [ ] 파싱 에러 없이 정상 실행

### 문서 완료 기준
- [ ] README.md "주요 메서드" 테이블 검증 (7개 도구 모두 기재)
- [ ] 실험 폴더 구조 문서 업데이트 (7개 로그 파일 예시)

---

## 🔗 관련 파일

### 수정 대상 파일
- `src/tools/text2sql.py` - Text2SQL 도구
- `src/tools/save_file.py` - 파일 저장 도구
- `src/tools/general_answer.py` - 일반 답변 도구

### 참조 파일 (구현 예시)
- `src/tools/search_paper.py` - RAG 논문 검색 (line 437)
- `src/tools/glossary.py` - RAG 용어집 (line 445)
- `src/tools/web_search.py` - 웹 검색 (line 37)
- `src/tools/summarize.py` - 논문 요약 (line 47)

### 시스템 파일
- `src/utils/experiment_manager.py` - ExperimentManager 클래스 (line 176: `get_tool_logger()` 정의)
- `src/utils/logger.py` - Logger 클래스

### 문서 파일
- `README.md` - line 1420~1432 (주요 메서드 테이블)
- `docs/architecture/mermaid/02_로깅_실험_폴더_관리_시스템.md` - 로깅 시스템 아키텍처

---

## 💡 참고 사항

### 1. ExperimentManager가 None인 경우 처리
```python
tool_logger = exp_manager.get_tool_logger('도구명') if exp_manager else None

if tool_logger:
    tool_logger.write("로그 내용")  # None 체크 후 기록
```

### 2. LLM 응답 전체 내용 기록 권장
기존 4개 도구는 LLM 응답 전체를 로그에 기록하므로, 3개 도구도 동일하게 구현:
```python
if tool_logger and llm_response:
    tool_logger.write(f"LLM 응답 전체:\n{llm_response}")
```

### 3. 소요 시간 측정 권장
```python
import time
start_time = time.time()
# ... 도구 로직 ...
elapsed_time = int((time.time() - start_time) * 1000)  # 밀리초 단위

if tool_logger:
    tool_logger.write(f"소요 시간: {elapsed_time}ms")
```

---

## 📊 예상 결과

### 작업 전 (현재)
```
experiments/20251109/20251109_143520_session_001/
├── tools/
│   ├── rag_glossary.log       ✅ 존재
│   ├── rag_paper.log           ✅ 존재
│   ├── web_search.log          ✅ 존재
│   └── summarize.log           ✅ 존재
└── chatbot.log
```

### 작업 후 (목표)
```
experiments/20251109/20251109_143520_session_001/
├── tools/
│   ├── rag_glossary.log       ✅ 존재
│   ├── rag_paper.log           ✅ 존재
│   ├── web_search.log          ✅ 존재
│   ├── summarize.log           ✅ 존재
│   ├── text2sql.log            ✅ 추가
│   ├── file_save.log           ✅ 추가
│   └── general.log             ✅ 추가
└── chatbot.log
```

---

## ⚠️ 주의사항

1. **기존 코드 로직 변경 금지**
   - 로그 기록만 추가하고, 도구의 핵심 로직은 수정하지 않음

2. **성능 영향 최소화**
   - 로그 기록은 비동기가 아니므로 과도한 로깅 지양
   - 필수 정보만 간결하게 기록

3. **개인정보 보호**
   - 사용자 질문은 기록하되, 개인정보는 마스킹 필요
   - API 키, 비밀번호 등 민감 정보 로그 기록 금지

4. **파일 핸들 관리**
   - Logger 클래스가 자동으로 파일 핸들을 관리하므로 별도 close 불필요

---

## 🏁 완료 후 조치

1. **테스트 실행**: 7개 도구 각각 최소 1회 실행
2. **로그 파일 검증**: 파일 생성 및 내용 완전성 확인
3. **커밋 메시지**: `feat: Text2SQL, 파일 저장, 일반 답변 도구 로그 기록 구현`
4. **이슈 종료**: 체크리스트 완료 후 이슈 Close

---

**작성일**: 2025-11-09
**문서 버전**: 1.0.0
