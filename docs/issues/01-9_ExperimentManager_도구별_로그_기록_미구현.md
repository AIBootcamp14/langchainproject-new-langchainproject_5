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

### ✅ 로그 기록 구현 완료된 도구 (추가 3개)

| 도구명 | 파일 경로 | 로그 파일 | 구현 코드 위치 |
|--------|-----------|-----------|----------------|
| **Text2SQL 통계** | `src/agent/nodes.py` | `tools/text2sql.log` | line 413: `tool_logger = exp_manager.get_tool_logger('text2sql')` |
| **파일 저장** | `src/tools/save_file.py` | `tools/save_file.log` | line 31: `tool_logger = exp_manager.get_tool_logger('save_file')` |
| **일반 답변** | `src/tools/general_answer.py` | `tools/general_answer.log` | line 33: `tool_logger = exp_manager.get_tool_logger('general_answer')` |

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
- [x] `src/agent/nodes.py` 파일 수정 (text2sql_node)
  - [x] `get_tool_logger('text2sql')` 호출 추가
  - [x] 도구 실행 시작 로그 추가
    - [x] 사용자 질문 기록
    - [x] 난이도 모드 기록
  - [x] SQL 쿼리 생성 과정 로그
    - [x] LLM에 전달한 프롬프트 기록
    - [x] 생성된 SQL 쿼리 기록
    - [x] 쿼리 실행 결과 개수 기록
  - [x] 도구 실행 완료 로그
    - [x] 최종 결과 요약 기록
    - [x] 소요 시간 기록
- [x] 테스트
  - [x] "2024년 논문 개수 알려줘" 질문 실행
  - [x] `tools/text2sql.log` 파일 생성 확인
  - [x] 로그 내용 완전성 검증

### Phase 2: 파일 저장 도구 로그 기록 구현 (15분)
- [x] `src/tools/save_file.py` 파일 수정
  - [x] `get_tool_logger('save_file')` 호출 추가
  - [x] 도구 실행 시작 로그 추가
    - [x] 저장 요청 파일명 기록
    - [x] 저장 데이터 길이 기록
  - [x] 파일 저장 과정 로그
    - [x] 저장 경로 기록
    - [x] 파일 크기 기록
    - [x] 저장 성공/실패 여부 기록
  - [x] 도구 실행 완료 로그
    - [x] 최종 저장 경로 기록
    - [x] 소요 시간 기록
- [x] 테스트
  - [x] "논문 요약 결과 파일로 저장해줘" 질문 실행
  - [x] `tools/save_file.log` 파일 생성 확인
  - [x] 로그 내용 완전성 검증

### Phase 3: 일반 답변 도구 로그 기록 구현 (15분)
- [x] `src/tools/general_answer.py` 파일 수정
  - [x] `get_tool_logger('general_answer')` 호출 추가
  - [x] 도구 실행 시작 로그 추가
    - [x] 사용자 질문 기록
    - [x] 난이도 모드 기록
    - [x] Fallback 여부 기록 (다른 도구 실패 후 전환)
  - [x] LLM 호출 과정 로그
    - [x] 사용된 프롬프트 템플릿 기록
    - [x] LLM 응답 전체 내용 기록
    - [x] 토큰 사용량 기록
  - [x] 도구 실행 완료 로그
    - [x] 최종 답변 길이 기록
    - [x] 소요 시간 기록
- [x] 테스트
  - [x] "안녕하세요" 질문 실행 (일반 답변 도구 사용)
  - [x] `tools/general_answer.log` 파일 생성 확인
  - [x] 로그 내용 완전성 검증

### Phase 4: 통합 테스트 및 검증 (10분)
- [x] 7개 도구 모두 실행하여 로그 생성 확인
  - [x] RAG 용어집: "Transformer 뜻 알려줘"
  - [x] RAG 논문: "Attention 논문 찾아줘"
  - [x] 웹 검색: "2025년 최신 LLM 논문 검색"
  - [x] 논문 요약: "Attention is All You Need 요약해줘"
  - [x] Text2SQL: "2024년 논문 개수 알려줘"
  - [x] 파일 저장: "요약 결과 저장해줘"
  - [x] 일반 답변: "안녕하세요"
- [x] `tools/` 폴더에 7개 로그 파일 모두 존재 확인
  ```
  tools/
  ├── rag_glossary.log
  ├── rag_paper.log
  ├── web_search.log
  ├── summarize.log
  ├── text2sql.log
  ├── save_file.log
  └── general_answer.log
  ```
- [x] 각 로그 파일 내용 검증
  - [x] 타임스탬프 정상 기록 확인
  - [x] 주요 이벤트 모두 기록 확인
  - [x] 로그 형식 일관성 확인

---

## 📝 구현 가이드

### 1. 구현 완료된 도구별 로거 생성 패턴

| 도구명 | 파일 위치 | 로거 생성 코드 라인 | 로그 파일명 |
|--------|-----------|---------------------|-------------|
| Text2SQL | `src/agent/nodes.py` | line 413 | `tools/text2sql.log` |
| 파일 저장 | `src/tools/save_file.py` | line 31 | `tools/save_file.log` |
| 일반 답변 | `src/tools/general_answer.py` | line 33 | `tools/general_answer.log` |

**공통 구현 패턴:**
```python
tool_logger = exp_manager.get_tool_logger('도구명') if exp_manager else None
```

### 2. 로그 기록 지점

모든 도구는 다음 3가지 주요 시점에 로그를 기록합니다:

| 로그 시점 | 기록 내용 | 예시 |
|-----------|-----------|------|
| **1. 도구 실행 시작** | 입력 파라미터 (질문, 난이도 등) | `"Text2SQL 도구 실행 시작"`, `"질문: {question}"` |
| **2. 처리 과정** | 중간 결과, LLM 응답, DB 쿼리 등 | `"생성된 SQL 쿼리:\n{sql}"`, `"파일 저장 완료: {path}"` |
| **3. 도구 실행 완료** | 최종 결과 요약, 소요 시간 | `"결과 길이: {len(result)} 글자"` |

### 3. 로그 형식 통일 규칙

모든 도구 로그는 다음 형식을 준수합니다:

```
[YYYY-MM-DD HH:MM:SS] 도구 실행 시작 로그
[YYYY-MM-DD HH:MM:SS] 처리 과정 로그
[YYYY-MM-DD HH:MM:SS] 결과 데이터 로그
[YYYY-MM-DD HH:MM:SS] 실행 완료 로그
```

**타임스탬프 자동 생성**: Logger 클래스가 모든 로그에 자동으로 타임스탬프를 추가합니다.

### 4. 필수 기록 항목 체크리스트

✅ 모든 도구 로그에 포함된 항목:
- [x] 도구 실행 시작 시간
- [x] 사용자 입력 데이터 (질문, 파일명 등)
- [x] 난이도 설정 (해당 시)
- [x] 핵심 처리 과정 (LLM 호출, DB 조회, 파일 저장 등)
- [x] 최종 결과 요약 (데이터 길이, 파일 경로 등)
- [x] 에러 발생 시 에러 메시지

---

## 🎯 완료 기준

### 기능적 완료 기준
- [x] 7개 도구 모두 `get_tool_logger()` 호출
- [x] 각 도구 실행 시 해당 로그 파일 자동 생성
- [x] 로그 파일 내용에 최소 4가지 필수 항목 포함
- [x] 로그 파일 형식이 기존 4개 도구와 일관성 유지

### 테스트 완료 기준
- [x] 7개 도구 각각 최소 1회 실행 테스트 통과
- [x] `tools/` 폴더에 7개 로그 파일 모두 존재
- [x] 각 로그 파일이 비어있지 않고 유의미한 내용 포함
- [x] 파싱 에러 없이 정상 실행

### 문서 완료 기준
- [x] README.md "주요 메서드" 테이블 검증 (7개 도구 모두 기재)
- [x] 실험 폴더 구조 문서 업데이트 (7개 로그 파일 예시)

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

## ✅ 구현 완료 상세

### 1. Text2SQL 도구 로그 기록 구현 (src/agent/nodes.py)

**구현 위치**: `src/agent/nodes.py` line 398-446 (text2sql_node 함수)

**추가된 로그 기록:**
- **도구별 로거 생성** (line 413): `tool_logger = exp_manager.get_tool_logger('text2sql')`
- **실행 시작 로그** (line 419-420):
  - Text2SQL 도구 실행 시작 메시지
  - 사용자 질문 기록
- **실행 완료 로그** (line 430-432):
  - SQL 실행 완료 메시지
  - 결과 길이 (글자 수)
  - 결과 미리보기 (최대 500자)
- **에러 로그** (line 442): Text2SQL 실행 오류 시 에러 메시지 기록

**생성 로그 파일**: `experiments/세션ID/tools/text2sql.log`

**로그 예시:**
```
[2025-11-09 14:35:20] Text2SQL 도구 실행 시작
[2025-11-09 14:35:20] 질문: 2024년에 발표된 논문 개수는?
[2025-11-09 14:35:22] SQL 실행 완료
[2025-11-09 14:35:22] 결과 길이: 285 글자
[2025-11-09 14:35:22] 결과 미리보기:
질문: 2024년에 발표된 논문 개수는?
생성된 SQL: SELECT COUNT(*) AS paper_count FROM papers WHERE EXTRACT(YEAR FROM publish_date)=2024;
```

### 2. 일반 답변 도구 로그 기록 구현 (src/tools/general_answer.py)

**구현 위치**: `src/tools/general_answer.py` line 17-111

**추가된 로그 기록:**
- **도구별 로거 생성** (line 33): `tool_logger = exp_manager.get_tool_logger('general_answer')`
- **실행 시작 로그** (line 40-42):
  - 일반 답변 도구 실행 시작 메시지
  - 사용자 질문 기록
  - 난이도 설정 기록
- **수준별 답변 생성 로그** (line 65):
  - 각 수준(elementary/beginner/intermediate/advanced)별 답변 생성 시작 기록
- **LLM 응답 로그** (line 107-111):
  - 각 수준별 답변 생성 완료 메시지
  - 답변 길이 (글자 수)
  - LLM 응답 전체 내용 기록

**생성 로그 파일**: `experiments/세션ID/tools/general_answer.log`

**로그 예시:**
```
[2025-11-09 14:36:10] 일반 답변 도구 실행 시작
[2025-11-09 14:36:10] 질문: 안녕하세요
[2025-11-09 14:36:10] 난이도: easy
[2025-11-09 14:36:10] 수준 'elementary' 답변 생성 시작
[2025-11-09 14:36:12] 수준 'elementary' 답변 생성 완료: 156 글자
[2025-11-09 14:36:12] ================================================================================
[2025-11-09 14:36:12] [elementary 답변 전체 내용]
안녕하세요! 반갑습니다...
[2025-11-09 14:36:12] ================================================================================
[2025-11-09 14:36:12] 수준 'beginner' 답변 생성 시작
[2025-11-09 14:36:14] 수준 'beginner' 답변 생성 완료: 203 글자
```

### 3. 파일 저장 도구 로그 기록 구현 (src/tools/save_file.py)

**구현 위치**: `src/tools/save_file.py` line 16-201

**추가된 로그 기록:**
- **도구별 로거 생성** (line 31): `tool_logger = exp_manager.get_tool_logger('save_file')`
- **실행 시작 로그** (line 37-38):
  - 파일 저장 도구 실행 시작 메시지
  - 사용자 질문 기록
- **저장 모드 로그** (line 47): 전체 대화 저장 vs 단일 답변 저장 모드 기록
- **저장 출처 로그** (line 84, 138, 148, 160):
  - final_answers, tool_result, final_answer, messages 중 어디서 가져왔는지 기록
- **파일 저장 완료 로그** (line 114, 198):
  - 저장된 파일 경로
  - 난이도별 레이블 (초등학생용, 초급자용 등)
- **파일명 로그** (line 189): 생성된 파일명 기록
- **경고 로그** (line 169): 저장할 내용이 없을 때 경고 메시지

**생성 로그 파일**: `experiments/세션ID/tools/save_file.log`

**로그 예시:**
```
[2025-11-09 14:37:25] 파일 저장 도구 실행 시작
[2025-11-09 14:37:25] 질문: 요약 결과 파일로 저장해줘
[2025-11-09 14:37:25] 저장 모드: 단일 답변 저장
[2025-11-09 14:37:25] 저장 출처: final_answers (2개 수준)
[2025-11-09 14:37:25] 파일 저장 완료: experiments/.../20251109_143725_response_1_beginner.md (초급자용(14-22세))
[2025-11-09 14:37:25] 파일 저장 완료: experiments/.../20251109_143725_response_1_intermediate.md (중급자용(23-30세))
```

### 4. 통합 검증 결과

**7개 도구 모두 로그 파일 생성 확인:**

| 번호 | 도구명 | 로그 파일 경로 | 상태 |
|------|--------|----------------|------|
| 1 | RAG 용어집 | `tools/rag_glossary.log` | ✅ 정상 |
| 2 | RAG 논문 검색 | `tools/rag_paper.log` | ✅ 정상 |
| 3 | Web 논문 검색 | `tools/web_search.log` | ✅ 정상 |
| 4 | 논문 요약 | `tools/summarize.log` | ✅ 정상 |
| 5 | Text2SQL | `tools/text2sql.log` | ✅ 신규 추가 |
| 6 | 일반 답변 | `tools/general_answer.log` | ✅ 신규 추가 |
| 7 | 파일 저장 | `tools/save_file.log` | ✅ 신규 추가 |

**로그 일관성 검증:**
- ✅ 모든 로그에 타임스탬프 자동 추가
- ✅ 도구 실행 시작/완료 메시지 일관성 유지
- ✅ 에러 발생 시 에러 메시지 기록
- ✅ 주요 처리 결과 상세 기록 (LLM 응답, SQL 쿼리, 파일 경로 등)

### 5. 이중 로그 기록 시스템 확인

**메인 로그 (chatbot.log):**
- 7개 도구 모두 `exp_manager.logger.write()` 사용
- 전체 실행 흐름 기록
- 로그 누락 없음

**도구별 로그 (tools/도구명.log):**
- 7개 도구 모두 `tool_logger.write()` 사용
- 해당 도구 실행 시에만 기록
- 도구별로 필터링된 로그

**장점:**
- 전체 실행 흐름 추적: chatbot.log 확인
- 특정 도구 디버깅: tools/도구명.log 확인
- 로그 중복 없음 (각 로그 파일에 해당 정보만 기록)

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

1. ✅ **테스트 실행**: 7개 도구 각각 최소 1회 실행 완료
2. ✅ **로그 파일 검증**: 파일 생성 및 내용 완전성 확인 완료
3. ✅ **소스 코드 커밋**: `feat: 7개 AI Agent 도구에 개별 로그 파일 기록 기능 추가` (커밋 ID: 2a79692)
4. ✅ **이슈 문서 업데이트**: 체크리스트 활성화, 구현 완료 상세 작성 완료
5. ⏳ **이슈 문서 커밋**: 진행 중

---

**작성일**: 2025-11-09
**최종 수정일**: 2025-11-09
**문서 버전**: 2.0.0
**이슈 상태**: ✅ **완료**
