# test_integration.py 사용법

## 개요

실험 관리 시스템의 통합 테스트 스크립트입니다.

**목적**: 여러 실험 생성 및 검색, find_experiments.py 및 aggregate_metrics.py 스크립트 기능, 실제 사용 시나리오를 검증합니다.

**위치**: `tests/integration/test_integration.py`

---

## 실행 방법

### 1. pytest를 통한 전체 테스트 실행

```bash
pytest tests/integration/test_integration.py -v
```

### 2. 특정 테스트만 실행

```bash
# 다중 실험 생성 테스트
pytest tests/integration/test_integration.py::test_multiple_experiments_creation -v

# 검색 기능 테스트
pytest tests/integration/test_integration.py::test_find_experiments_integration -v

# 집계 기능 테스트
pytest tests/integration/test_integration.py::test_aggregate_metrics_integration -v

# 실제 시나리오 테스트
pytest tests/integration/test_integration.py::test_real_world_scenario -v
```

### 3. 상세 출력과 함께 실행

```bash
pytest tests/integration/test_integration.py -vv -s
```

---

## 테스트 항목

### 1. 다중 실험 시나리오 테스트

#### test_multiple_experiments_creation
- **목적**: 여러 실험 생성 및 검색 검증
- **검증 내용**:
  - 3개 실험 생성
  - Session ID 자동 증가 (001, 002, 003)
  - 각 실험 독립적 폴더 생성
  - metadata.json 개별 관리

### 2. 검색 기능 통합 테스트

#### test_find_experiments_integration
- **목적**: `find_experiments.py` 스크립트 기능 검증
- **검증 내용**:
  - 난이도별 검색 (`difficulty="easy"`, `difficulty="hard"`)
  - 도구별 검색 (`tool="rag_paper"`, `tool="web_search"`)
  - 성공 여부 검색 (`min_success=True`)
  - 복합 조건 검색 (예: `difficulty="easy"` + `min_success=True`)

**예시**:
```python
# 난이도별 검색
easy_results = find_experiments(difficulty="easy")

# 도구별 검색
rag_results = find_experiments(tool="rag_paper")

# 복합 조건 검색
easy_success_results = find_experiments(difficulty="easy", min_success=True)
```

### 3. 집계 기능 통합 테스트

#### test_aggregate_metrics_integration
- **목적**: `aggregate_metrics.py` 스크립트 기능 검증
- **검증 내용**:
  - RAG 지표 집계 (recall, precision, faithfulness, answer_relevancy)
  - Agent 정확도 집계 (routing_accuracy, correct/incorrect decisions)
  - 응답 시간 집계 (total_time_ms, retrieval_time_ms, generation_time_ms)
  - 비용 분석 집계 (total_tokens, cost_usd, cost_krw)

**집계 결과 형식**:
```json
{
  "recall_at_5": {
    "mean": 0.85,
    "min": 0.80,
    "max": 0.90,
    "std": 0.05
  }
}
```

### 4. 실제 사용 시나리오 테스트

#### test_real_world_scenario
- **목적**: 전체 워크플로우 시뮬레이션
- **시나리오**:
  1. 챗봇 시작 (실험 초기화)
  2. 사용자 질문 입력
  3. Agent 도구 선택
  4. RAG 검색 실행
  5. DB 쿼리 기록
  6. 프롬프트 저장
  7. 답변 생성
  8. 평가 지표 계산
  9. 실험 종료
  10. 검색 및 집계

**생성되는 파일**:
- `chatbot.log`: 챗봇 로그
- `tools/rag_paper.log`: 도구별 로그
- `database/queries.sql`: SQL 쿼리 기록
- `database/pgvector_searches.json`: pgvector 검색 기록
- `database/search_results.json`: 검색 결과
- `prompts/system_prompt.txt`: 시스템 프롬프트
- `prompts/user_prompt.txt`: 사용자 프롬프트
- `prompts/final_prompt.txt`: 최종 프롬프트
- `ui/user_interactions.log`: UI 인터랙션 로그
- `ui/ui_events.json`: UI 이벤트 로그
- `outputs/response.txt`: 응답 텍스트
- `evaluation/rag_metrics.json`: RAG 평가 지표
- `evaluation/agent_accuracy.json`: Agent 정확도
- `evaluation/latency_report.json`: 응답 시간 분석
- `evaluation/cost_analysis.json`: 비용 분석

### 5. 스크립트 실행 테스트

#### test_find_experiments_script_execution
- **목적**: `find_experiments.py` 명령줄 실행 검증
- **실행 예시**:
```bash
python scripts/system/find_experiments.py --difficulty easy
```

#### test_aggregate_metrics_script_execution
- **목적**: `aggregate_metrics.py` 명령줄 실행 검증
- **실행 예시**:
```bash
python scripts/system/aggregate_metrics.py --date 20251031 --output result.json
```

---

## 예상 결과

### 성공 시

```bash
$ pytest tests/integration/test_integration.py -v

tests/integration/test_integration.py::test_multiple_experiments_creation PASSED
tests/integration/test_integration.py::test_find_experiments_integration PASSED
tests/integration/test_integration.py::test_aggregate_metrics_integration PASSED
tests/integration/test_integration.py::test_real_world_scenario PASSED
tests/integration/test_integration.py::test_find_experiments_script_execution PASSED
tests/integration/test_integration.py::test_aggregate_metrics_script_execution PASSED

======================== 6 passed in 1.20s ========================
```

---

## 주의 사항

1. **테스트 격리**:
   - 각 테스트 후 `experiments/` 폴더가 자동으로 삭제됨
   - pytest 픽스처(`cleanup_experiments`)가 자동으로 처리

2. **환경 변수 설정**:
   - `PYTHONPATH` 환경 변수가 프로젝트 루트를 가리켜야 함
   - 스크립트 실행 테스트 시 필요

3. **의존성**:
   - pytest 패키지 필요: `pip install pytest`

4. **실행 위치**:
   - 프로젝트 루트 디렉토리에서 실행 권장

---

## 관련 파일

- `src/utils/experiment_manager.py`: ExperimentManager 클래스 구현
- `scripts/system/find_experiments.py`: 실험 검색 스크립트
- `scripts/system/aggregate_metrics.py`: 평가 지표 집계 스크립트
- `tests/unit/test_experiment_manager.py`: ExperimentManager 단위 테스트
