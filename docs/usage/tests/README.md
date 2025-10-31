# 테스트 사용법 문서

## 개요

이 디렉토리는 프로젝트의 모든 테스트 파일에 대한 사용법 문서를 포함합니다.

---

## 테스트 파일 목록

### 통합 테스트 (Integration Tests)

| 파일명 | 위치 | 목적 | 문서 |
|--------|------|------|------|
| `test_data_pipeline.py` | `tests/integration/` | 데이터 파이프라인 구조 검증 | [📄 문서](./test_data_pipeline.md) |
| `test_integration.py` | `tests/integration/` | 실험 관리 시스템 통합 테스트 | [📄 문서](./test_integration.md) |
| `test_agent_system.py` | `tests/integration/` (브랜치: `feature/agent-system`) | Phase 1: 기반 시스템 테스트 | [📄 문서](./test_agent_system.md) |

### 단위 테스트 (Unit Tests)

| 파일명 | 위치 | 목적 | 문서 |
|--------|------|------|------|
| `test_experiment_manager.py` | `tests/unit/` | ExperimentManager 클래스 단위 테스트 | [📄 문서](./test_experiment_manager.md) |

---

## 빠른 실행 가이드

### 전체 테스트 실행

```bash
# 프로젝트 루트에서 실행
pytest tests/ -v
```

### 통합 테스트만 실행

```bash
pytest tests/integration/ -v
```

### 단위 테스트만 실행

```bash
pytest tests/unit/ -v
```

### 특정 파일 실행

```bash
# 데이터 파이프라인 테스트
python tests/integration/test_data_pipeline.py

# ExperimentManager 단위 테스트
pytest tests/unit/test_experiment_manager.py -v

# 실험 관리 시스템 통합 테스트
pytest tests/integration/test_integration.py -v

# Agent 시스템 테스트 (feature/agent-system 브랜치)
python tests/integration/test_agent_system.py
```

---

## 테스트별 요약

### 1. test_data_pipeline.py
**목적**: 데이터 수집부터 데이터베이스 설정까지 전체 파이프라인 검증

**주요 테스트**:
- ArxivPaperCollector 클래스 구조
- PaperDocumentLoader 클래스 구조
- PaperEmbeddingManager 클래스 구조
- setup_database 스크립트
- 데이터 파일 존재 확인

**실행 방법**:
```bash
python tests/integration/test_data_pipeline.py
```

---

### 2. test_experiment_manager.py
**목적**: ExperimentManager 클래스의 핵심 기능 검증

**주요 테스트**:
- Session ID 자동 부여 및 증가
- 폴더 구조 생성
- metadata.json 관리
- 평가 지표 저장 (RAG, Agent, Latency, Cost)
- with 문 컨텍스트 매니저

**실행 방법**:
```bash
pytest tests/unit/test_experiment_manager.py -v
```

---

### 3. test_integration.py
**목적**: 실험 관리 시스템의 통합 기능 검증

**주요 테스트**:
- 다중 실험 생성 및 검색
- find_experiments.py 스크립트 기능
- aggregate_metrics.py 스크립트 기능
- 실제 사용 시나리오 (챗봇 전체 워크플로우)

**실행 방법**:
```bash
pytest tests/integration/test_integration.py -v
```

---

### 4. test_agent_system.py
**목적**: Phase 1 기반 시스템 검증 (LLM 클라이언트, AgentState, Agent 그래프)

**주요 테스트**:
- LLM 클라이언트 초기화 (OpenAI, Solar)
- Agent 그래프 컴파일
- 라우터 노드 도구 선택 로직

**실행 방법**:
```bash
# feature/agent-system 브랜치에서 실행
python tests/integration/test_agent_system.py
```

**참고**: API 키가 없어도 그래프 구조 검증은 가능

---

## 환경 설정

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. pytest 설치

```bash
pip install pytest
```

### 3. 환경 변수 설정 (.env 파일)

```bash
# OpenAI API (test_agent_system.py에 필요)
OPENAI_API_KEY=your_openai_api_key

# Upstage API (test_agent_system.py에 필요)
SOLAR_API_KEY=your_SOLAR_API_KEY

# PostgreSQL (데이터베이스 관련 테스트에 필요)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_chatbot
DB_USER=your_username
DB_PASSWORD=your_password
```

---

## 테스트 격리 및 정리

### 자동 정리
- 통합 테스트는 pytest 픽스처를 사용하여 각 테스트 후 `experiments/` 폴더를 자동으로 삭제
- 테스트 간 간섭이 없도록 격리

### 수동 정리
만약 테스트 실패로 인해 폴더가 남아있다면:

```bash
# experiments 폴더 삭제
rm -rf experiments/
```

---

## 자주 묻는 질문 (FAQ)

### Q1. API 키 없이 테스트할 수 있나요?
**A**: 일부 테스트는 가능합니다.
- `test_data_pipeline.py`: 가능 (구조 검증만 수행)
- `test_experiment_manager.py`: 가능 (API 키 불필요)
- `test_integration.py`: 가능 (API 키 불필요)
- `test_agent_system.py`: 부분적으로 가능 (그래프 구조 검증은 가능, LLM 호출은 불가)

### Q2. 테스트 실패 시 어떻게 해야 하나요?
**A**:
1. 환경 변수 확인 (`.env` 파일)
2. 필수 패키지 설치 확인 (`pip install -r requirements.txt`)
3. 실행 위치 확인 (프로젝트 루트에서 실행)
4. 오류 메시지 확인 및 관련 문서 참조

### Q3. pytest vs 직접 실행의 차이는?
**A**:
- **pytest**: 모든 테스트 함수를 개별적으로 실행, 상세한 결과 제공
- **직접 실행**: `main()` 함수를 통해 순차적으로 실행, 간단한 결과 출력

둘 다 동일한 테스트를 수행하지만, pytest가 더 상세한 정보를 제공합니다.

### Q4. 브랜치별 테스트 파일이 다른가요?
**A**: 네, 일부 테스트는 특정 브랜치에서만 존재합니다.
- `test_agent_system.py`: `feature/agent-system` 브랜치
- 나머지 테스트: 모든 브랜치에서 사용 가능

---

## 문의 및 지원

테스트 관련 문의사항은 프로젝트 문서를 참조하세요:
- PRD 문서: `docs/prd/`
- 역할 문서: `docs/roles/`
- 이슈 문서: `docs/issues/`
