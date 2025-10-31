# test_experiment_manager.py 사용법

## 개요

ExperimentManager 클래스의 단위 테스트 스크립트입니다.

**목적**: 실험 관리 시스템의 핵심 기능인 Session ID 자동 부여, 폴더 구조 생성, 메타데이터 관리, 평가 지표 저장 등을 검증합니다.

**위치**: `tests/unit/test_experiment_manager.py`

---

## 실행 방법

### 1. pytest를 통한 전체 테스트 실행

```bash
pytest tests/unit/test_experiment_manager.py -v
```

### 2. 특정 테스트만 실행

```bash
# Session ID 테스트만 실행
pytest tests/unit/test_experiment_manager.py::test_session_id_auto_increment -v

# 폴더 구조 테스트만 실행
pytest tests/unit/test_experiment_manager.py::test_folder_structure_creation -v

# 메타데이터 테스트만 실행
pytest tests/unit/test_experiment_manager.py::test_metadata_update -v
```

### 3. 상세 출력과 함께 실행

```bash
pytest tests/unit/test_experiment_manager.py -vv -s
```

---

## 테스트 항목

### 1. Session ID 관리 테스트

#### test_session_id_auto_increment
- **목적**: Session ID 자동 증가 검증
- **검증 내용**:
  - 첫 실행: `session_001`
  - 두 번째 실행: `session_002`
  - 세 번째 실행: `session_003`

#### test_session_id_reset_on_new_date
- **목적**: 날짜 변경 시 Session ID 초기화 검증
- **검증 내용**:
  - 다른 날짜의 Session ID는 001부터 다시 시작

### 2. 폴더 구조 테스트

#### test_folder_structure_creation
- **목적**: 필수 폴더 생성 검증
- **검증 내용**:
  - 메인 폴더 생성
  - 6개 필수 서브 폴더 생성 (`tools/`, `database/`, `prompts/`, `ui/`, `outputs/`, `evaluation/`)
  - `chatbot.log` 파일 생성

#### test_folder_naming_convention
- **목적**: 폴더명 형식 검증
- **검증 내용**:
  - 형식: `YYYYMMDD_HHMMSS_session_XXX`
  - Session ID는 3자리 숫자

### 3. metadata.json 테스트

#### test_metadata_initialization
- **목적**: metadata.json 초기화 검증
- **검증 내용**:
  - 필수 키 존재 확인
  - 초기값 설정 확인

#### test_metadata_update
- **목적**: metadata.json 업데이트 검증
- **검증 내용**:
  - 메타데이터 동적 업데이트
  - 파일에 정상 저장

### 4. 평가 지표 저장 테스트

#### test_save_rag_metrics
- **목적**: RAG 평가 지표 저장 검증
- **검증 내용**:
  - `rag_metrics.json` 파일 생성
  - 데이터 정상 저장 (recall, precision, faithfulness, answer_relevancy)

#### test_save_agent_accuracy
- **목적**: Agent 정확도 저장 검증
- **검증 내용**:
  - `agent_accuracy.json` 파일 생성
  - 데이터 정상 저장 (routing_accuracy, correct_decisions, incorrect_decisions)

#### test_save_latency_report
- **목적**: 응답 시간 분석 저장 검증
- **검증 내용**:
  - `latency_report.json` 파일 생성
  - 데이터 정상 저장 (total_time_ms, routing_time_ms, retrieval_time_ms, generation_time_ms)

#### test_save_cost_analysis
- **목적**: 비용 분석 저장 검증
- **검증 내용**:
  - `cost_analysis.json` 파일 생성
  - 데이터 정상 저장 (total_tokens, cost_usd, cost_krw)

### 5. 프롬프트 저장 테스트

#### test_save_prompts
- **목적**: 프롬프트 저장 검증
- **검증 내용**:
  - `system_prompt.txt` 저장
  - `user_prompt.txt` 저장
  - `final_prompt.txt` 저장

### 6. 데이터베이스 로깅 테스트

#### test_log_sql_query
- **목적**: SQL 쿼리 저장 검증
- **검증 내용**:
  - `queries.sql` 파일 생성
  - 쿼리 정상 기록

### 7. 컨텍스트 매니저 테스트

#### test_context_manager_with_statement
- **목적**: with 문 자동 종료 검증
- **검증 내용**:
  - with 문 진입 시 정상 초기화
  - with 문 종료 시 자동 close 호출
  - end_time 자동 기록

#### test_context_manager_with_exception
- **목적**: with 문 예외 처리 검증
- **검증 내용**:
  - 예외 발생 시에도 close 호출
  - end_time 기록

### 8. 도구 Logger 테스트

#### test_get_tool_logger
- **목적**: 도구별 Logger 생성 검증
- **검증 내용**:
  - 도구별 로그 파일 생성
  - Logger 인스턴스 반환

### 9. 통합 워크플로우 테스트

#### test_full_workflow
- **목적**: 전체 워크플로우 시뮬레이션
- **검증 내용**:
  1. 실험 시작 (with 문)
  2. 메타데이터 업데이트
  3. 프롬프트 저장
  4. DB 쿼리 기록
  5. 평가 지표 저장
  6. 실험 종료 (자동)

---

## 예상 결과

### 성공 시

```bash
$ pytest tests/unit/test_experiment_manager.py -v

tests/unit/test_experiment_manager.py::test_session_id_auto_increment PASSED
tests/unit/test_experiment_manager.py::test_session_id_reset_on_new_date PASSED
tests/unit/test_experiment_manager.py::test_folder_structure_creation PASSED
tests/unit/test_experiment_manager.py::test_folder_naming_convention PASSED
tests/unit/test_experiment_manager.py::test_metadata_initialization PASSED
tests/unit/test_experiment_manager.py::test_metadata_update PASSED
tests/unit/test_experiment_manager.py::test_save_rag_metrics PASSED
tests/unit/test_experiment_manager.py::test_save_agent_accuracy PASSED
tests/unit/test_experiment_manager.py::test_save_latency_report PASSED
tests/unit/test_experiment_manager.py::test_save_cost_analysis PASSED
tests/unit/test_experiment_manager.py::test_save_prompts PASSED
tests/unit/test_experiment_manager.py::test_log_sql_query PASSED
tests/unit/test_experiment_manager.py::test_context_manager_with_statement PASSED
tests/unit/test_experiment_manager.py::test_context_manager_with_exception PASSED
tests/unit/test_experiment_manager.py::test_get_tool_logger PASSED
tests/unit/test_experiment_manager.py::test_full_workflow PASSED

======================== 16 passed in 0.50s ========================
```

---

## 주의 사항

1. **테스트 격리**:
   - 각 테스트 후 `experiments/` 폴더가 자동으로 삭제됨
   - pytest 픽스처(`cleanup_experiments`)가 자동으로 처리

2. **실행 환경**:
   - 프로젝트 루트 디렉토리에서 실행 권장
   - Python 경로가 올바르게 설정되어 있어야 함

3. **의존성**:
   - pytest 패키지 필요: `pip install pytest`

---

## 관련 파일

- `src/utils/experiment_manager.py`: ExperimentManager 클래스 구현
- `tests/integration/test_integration.py`: 통합 테스트 스크립트
