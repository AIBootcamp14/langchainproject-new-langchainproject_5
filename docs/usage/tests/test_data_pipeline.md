# test_data_pipeline.py 사용법

## 개요

데이터 파이프라인 구조를 검증하는 통합 테스트 스크립트입니다.

**목적**: ArXiv 논문 수집부터 데이터베이스 설정까지 전체 파이프라인의 구조와 기본 동작을 확인합니다.

**위치**: `tests/integration/test_data_pipeline.py`

---

## 실행 방법

### 1. 기본 실행

```bash
python tests/integration/test_data_pipeline.py
```

### 2. pytest를 통한 실행

```bash
pytest tests/integration/test_data_pipeline.py -v
```

---

## 테스트 항목

### 1. ArxivPaperCollector 테스트
- **목적**: 논문 수집 클래스의 구조 검증
- **검증 내용**:
  - 클래스 초기화 성공 여부
  - 저장 디렉토리 생성 확인
  - 필수 메서드 존재 확인 (`collect_papers`, `collect_by_keywords`, `remove_duplicates`)

### 2. PaperDocumentLoader 테스트
- **목적**: 문서 로더 클래스의 구조 검증
- **검증 내용**:
  - 클래스 초기화 성공 여부
  - chunk_size 및 chunk_overlap 설정 확인
  - 필수 메서드 존재 확인 (`load_pdf`, `load_and_split`, `load_all_pdfs`)

### 3. PaperEmbeddingManager 테스트
- **목적**: 임베딩 관리자 클래스의 구조 검증
- **검증 내용**:
  - 모듈 임포트 성공 여부
  - 필수 메서드 존재 확인 (`add_documents`, `add_documents_with_paper_id`)

### 4. setup_database 스크립트 테스트
- **목적**: 데이터베이스 설정 스크립트 검증
- **검증 내용**:
  - 모든 함수 임포트 성공
  - DDL 쿼리 구조 확인 (CREATE TABLE, CREATE INDEX)

### 5. 데이터 파일 확인
- **목적**: 필요한 데이터 파일 존재 여부 확인
- **검증 내용**:
  - 메타데이터 파일: `data/raw/arxiv_papers_metadata.json`
  - PDF 디렉토리: `data/raw/pdfs/`
  - 매핑 파일: `data/processed/paper_id_mapping.json`

---

## 예상 결과

### 성공 시

```
============================================================
데이터 파이프라인 구조 테스트
============================================================

============================================================
1. ArxivPaperCollector 테스트
============================================================
[OK] ArxivPaperCollector 초기화 성공
   저장 디렉토리: data/raw/pdfs
   디렉토리 존재: True
[OK] 모든 메서드 존재 확인

============================================================
2. PaperDocumentLoader 테스트
============================================================
[OK] PaperDocumentLoader 초기화 성공
   chunk_size: 1000
   chunk_overlap: 200
[OK] 모든 메서드 존재 확인

...

============================================================
테스트 결과 요약
============================================================
ArxivPaperCollector: [OK] 통과
PaperDocumentLoader: [OK] 통과
PaperEmbeddingManager: [OK] 통과
setup_database: [OK] 통과
데이터 파일: [OK] 통과

[OK] 모든 테스트 통과!
```

### 일부 실패 시

```
...
[WARN] 일부 테스트 실패 (환경 변수 또는 의존성 문제일 수 있음)
```

---

## 주의 사항

1. **환경 변수 미설정 시**:
   - 일부 테스트는 API 키가 없어도 구조 검증만 수행
   - 경고 메시지는 정상적인 동작

2. **데이터 파일 미존재 시**:
   - 메타데이터 파일이 없으면 `[WARN]` 표시
   - `scripts/collect_arxiv_papers.py` 먼저 실행 필요

3. **의존성 패키지**:
   - 모든 필수 패키지가 설치되어 있어야 함
   - `requirements.txt` 확인

---

## 관련 파일

- `scripts/collect_arxiv_papers.py`: ArXiv 논문 수집 스크립트
- `src/data/document_loader.py`: 문서 로더 모듈
- `src/data/embeddings.py`: 임베딩 관리 모듈
- `scripts/setup_database.py`: 데이터베이스 설정 스크립트
