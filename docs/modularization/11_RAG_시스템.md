# 09. RAG 시스템 (Retrieval-Augmented Generation)

## 📋 문서 정보
- **작성일**: 2025-11-04
- **작성자**: 최현화[팀장]
- **시스템명**: RAG 시스템
- **구현 파일**: `src/rag/retriever.py`, `src/database/` (vector_store.py, embeddings.py, db.py)
- **우선순위**: ⭐⭐⭐ (매우 중요 - 핵심 검색 기능)
- **참고 문서**: [PRD/13_RAG_시스템_설계.md](../PRD/13_RAG_시스템_설계.md)

---

## 📌 시스템 개요

### 목적 및 배경

RAG(Retrieval-Augmented Generation) 시스템은 **대량의 논문 데이터베이스에서 관련 정보를 검색하여 LLM의 답변을 보강하는 핵심 시스템**입니다. 사용자 질문과 유사한 논문 청크(chunk)를 벡터 검색으로 찾아내고, 이를 LLM 컨텍스트로 제공하여 정확하고 근거 있는 답변을 생성합니다.

### 주요 역할

1. **벡터 검색**: OpenAI Embeddings로 질문을 벡터화하여 유사한 논문 청크 검색
2. **다양한 검색 전략**: Similarity Search, MMR, MultiQueryRetriever 지원
3. **메타데이터 필터링**: 연도, 카테고리, 저자 등으로 검색 범위 제한
4. **중복 제거**: 동일 문서가 여러 쿼리에서 중복 반환되는 것을 방지
5. **PostgreSQL + pgvector 통합**: 관계형 DB와 벡터 검색을 하나로 통합

### 핵심 기술 스택

| 기술 | 역할 | 버전/모델 |
|------|------|-----------|
| **PostgreSQL** | 관계형 데이터베이스 | 15.0+ |
| **pgvector** | 벡터 검색 확장 | 0.5.0+ |
| **OpenAI Embeddings** | 텍스트 벡터화 | text-embedding-3-small (1536차원) |
| **LangChain PGVector** | PGVector 통합 | langchain-postgres |
| **MultiQueryRetriever** | 쿼리 확장 검색 | langchain-community |
| **Solar Pro2** | 쿼리 확장용 LLM | Upstage Solar API |

---

## 🏗️ RAG 시스템 아키텍처

### 전체 데이터 흐름

```mermaid
graph TB
    subgraph UserInput["🔸 사용자 입력"]
        direction LR
        Query[사용자 질문]
    end

    subgraph Embedding["🔹 임베딩 변환"]
        direction LR
        OpenAI[OpenAI Embeddings<br/>text-embedding-3-small]
        Vector[질문 벡터<br/>1536차원]

        OpenAI --> Vector
    end

    subgraph SearchStrategy["🔺 검색 전략 선택"]
        direction TB
        Strategy{검색 타입?}
        Sim[Similarity Search<br/>유사도 기반]
        MMR[MMR Search<br/>다양성 확보]
        MultiQ[MultiQuery Retriever<br/>쿼리 확장]

        Strategy -->|similarity| Sim
        Strategy -->|mmr| MMR
        Strategy -->|multi_query| MultiQ
    end

    subgraph VectorDB["🔻 벡터 데이터베이스"]
        direction LR
        PGVector[PostgreSQL + pgvector<br/>paper_chunks]
        Chunks[논문 청크<br/>메타데이터]

        PGVector --> Chunks
    end

    subgraph PostProcess["🔶 후처리"]
        direction TB
        Dedup[중복 제거<br/>MD5 해시 기반]
        TopK[Top-K 선택<br/>k=5 기본]

        Dedup --> TopK
    end

    subgraph Output["🔷 검색 결과"]
        direction LR
        Results[관련 논문 청크<br/>+ 메타데이터]
    end

    Query --> Embedding
    Embedding --> SearchStrategy
    SearchStrategy --> VectorDB
    VectorDB --> PostProcess
    PostProcess --> Output

    %% Subgraph 스타일
    style UserInput fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    style Embedding fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style SearchStrategy fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000
    style VectorDB fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000
    style PostProcess fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style Output fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000

    %% 노드 스타일 (사용자 입력 - 파랑 계열)
    style Query fill:#90caf9,stroke:#1976d2,color:#000

    %% 노드 스타일 (임베딩 - 보라 계열)
    style OpenAI fill:#ce93d8,stroke:#7b1fa2,color:#000
    style Vector fill:#ba68c8,stroke:#7b1fa2,color:#fff

    %% 노드 스타일 (검색 전략 - 주황 계열)
    style Strategy fill:#ba68c8,stroke:#7b1fa2,color:#fff
    style Sim fill:#ffcc80,stroke:#f57c00,color:#000
    style MMR fill:#ffcc80,stroke:#f57c00,color:#000
    style MultiQ fill:#ffcc80,stroke:#f57c00,color:#000

    %% 노드 스타일 (벡터 DB - 녹색 계열)
    style PGVector fill:#81c784,stroke:#388e3c,color:#000
    style Chunks fill:#a5d6a7,stroke:#388e3c,color:#000

    %% 노드 스타일 (후처리 - 보라 계열)
    style Dedup fill:#ce93d8,stroke:#7b1fa2,color:#000
    style TopK fill:#ba68c8,stroke:#7b1fa2,color:#fff

    %% 노드 스타일 (결과 - 녹색 계열)
    style Results fill:#66bb6a,stroke:#2e7d32,color:#fff
```

### 아키텍처 상세 설명

#### 1. 사용자 입력 (🔸)
- 사용자가 자연어 질문을 입력합니다.
- 예: "Transformer 논문에서 Self-Attention 메커니즘을 설명해줘"

#### 2. 임베딩 변환 (🔹)
- **OpenAI Embeddings API** 호출
- 모델: `text-embedding-3-small` (1536차원)
- 질문 텍스트를 벡터로 변환
- 비용 효율적이며 높은 검색 정확도 제공

#### 3. 검색 전략 선택 (🔺)
RAG 시스템은 3가지 검색 전략을 지원합니다:

**a) Similarity Search (유사도 검색)**
- 코사인 유사도 기반 단순 검색
- 가장 빠른 검색 속도
- 상위 K개 문서 반환

**b) MMR (Maximal Marginal Relevance)**
- 관련성과 다양성의 균형
- `lambda_mult` 파라미터로 조절 (0~1)
  - 1.0: 관련성만 고려
  - 0.0: 다양성만 고려
  - 0.5: 균형 (기본값)
- `fetch_k`개 후보에서 `k`개 선택

**c) MultiQuery Retriever (쿼리 확장)**
- LLM이 원본 질문을 여러 관점의 쿼리로 확장
- 각 쿼리로 병렬 검색 후 결과 통합
- 더 포괄적인 검색 결과 제공
- Solar Pro2 모델 사용 (비용 효율)

#### 4. 벡터 데이터베이스 (🔻)
- **PostgreSQL + pgvector** 통합 환경
- 컬렉션명: `paper_chunks`
- 각 청크는 다음 메타데이터 포함:
  - `paper_id`: 논문 ID
  - `paper_title`: 논문 제목
  - `authors`: 저자 목록
  - `publish_date`: 발행일
  - `chunk_index`: 청크 순서
  - `category`: 논문 카테고리

#### 5. 후처리 (🔶)
- **중복 제거**: MD5 해시 기반으로 동일 청크 제거
- **Top-K 선택**: 최종적으로 상위 K개 문서만 반환 (기본 k=5)

#### 6. 검색 결과 (🔷)
- LangChain `Document` 객체 리스트 반환
- 각 Document는 `page_content`와 `metadata` 포함
- LLM 컨텍스트로 직접 전달 가능

---

## 🔧 핵심 구현 모듈

### 1. RAGRetriever 클래스 (src/rag/retriever.py)

RAG 검색의 핵심 클래스입니다.

#### 초기화 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `collection_name` | str | "paper_chunks" | pgvector 컬렉션명 |
| `search_type` | str | "mmr" | 검색 타입 (similarity/mmr) |
| `k` | int | 5 | 최종 반환 문서 수 |
| `fetch_k` | int | 20 | MMR 후보 수 |
| `lambda_mult` | float | 0.5 | MMR 다양성 파라미터 |
| `llm_model` | str | "solar-pro2" | MultiQuery용 LLM |
| `llm_temperature` | float | 0.0 | LLM temperature |

#### 주요 메서드

**기본 검색**
```python
retriever = RAGRetriever(collection_name="paper_chunks", k=5)
docs = retriever.invoke("Transformer 논문 설명")
```

**유사도 검색**
```python
docs = retriever.similarity_search("Self-Attention", k=3)
```

**점수 포함 검색**
```python
docs_with_scores = retriever.similarity_search_with_score("BERT", k=5)
# [(Document(...), 0.85), (Document(...), 0.82), ...]
```

**메타데이터 필터 검색**
```python
# 2023년 논문만 검색
docs = retriever.search_with_filter(
    query="최신 LLM",
    filter_dict={"publish_date": {"$gte": "2023-01-01"}},
    k=5
)
```

**멀티쿼리 검색 (쿼리 확장)**
```python
# Solar Pro2가 질문을 여러 관점으로 확장하여 검색
docs = retriever.multi_query_search("Transformer 구조", k=5)
```

#### 검색 모드 전환

```python
# MMR 모드로 전환
retriever.set_mode("mmr")

# Similarity 모드로 전환
retriever.set_mode("similarity")
```

---

### 2. PGVector VectorStore (src/database/vector_store.py)

PostgreSQL + pgvector 기반 벡터 저장소 생성 팩토리 함수입니다.

#### 함수 시그니처

```python
def get_pgvector_store(
    collection_name: str,
    embedding_model: Optional[str] = None,
    connection_string: Optional[str] = None,
) -> PGVector:
```

#### 사용 예시

```python
from src.database.vector_store import get_pgvector_store

# 기본 사용 (configs/db_config.yaml 설정 자동 로드)
vectorstore = get_pgvector_store("paper_chunks")

# 커스텀 임베딩 모델 지정
vectorstore = get_pgvector_store(
    collection_name="paper_chunks",
    embedding_model="text-embedding-3-large"  # 3072차원
)

# 커스텀 연결 문자열
vectorstore = get_pgvector_store(
    collection_name="custom_collection",
    connection_string="postgresql://user:pass@localhost:5432/mydb"
)
```

#### 주요 특징

- **자동 설정 로드**: `configs/db_config.yaml` 우선 사용
- **환경변수 폴백**: config 없을 시 환경변수 사용
- **JSONB 지원**: 메타데이터를 JSONB로 저장하여 유연한 쿼리 가능

---

### 3. OpenAI Embeddings (src/database/embeddings.py)

텍스트를 벡터로 변환하는 임베딩 모듈입니다.

#### 함수 시그니처

```python
def get_embeddings(model: Optional[str] = None) -> OpenAIEmbeddings:
```

#### 지원 모델

| 모델 | 차원 | 비용 | 사용 시나리오 |
|------|------|------|--------------|
| **text-embedding-3-small** | 1536 | 낮음 | 일반 검색 (권장) |
| **text-embedding-3-large** | 3072 | 높음 | 고정밀 검색 필요 시 |

#### 사용 예시

```python
from src.database.embeddings import get_embeddings

# 기본 모델 (text-embedding-3-small)
embeddings = get_embeddings()

# Large 모델
embeddings = get_embeddings("text-embedding-3-large")

# 텍스트 벡터화
vector = embeddings.embed_query("Transformer 논문")
# [0.123, -0.456, 0.789, ... ] (1536차원)
```

---

## 📊 검색 전략 비교

### Similarity Search vs MMR vs MultiQuery

| 특성 | Similarity | MMR | MultiQuery |
|------|-----------|-----|------------|
| **속도** | ⚡⚡⚡ 가장 빠름 | ⚡⚡ 빠름 | ⚡ 느림 (LLM 호출) |
| **관련성** | ⭐⭐ 중간 | ⭐⭐⭐ 높음 | ⭐⭐⭐ 매우 높음 |
| **다양성** | ⭐ 낮음 | ⭐⭐⭐ 높음 | ⭐⭐ 중간 |
| **비용** | 💰 낮음 | 💰 낮음 | 💰💰 중간 (LLM) |
| **추천 상황** | 빠른 검색 | 균형잡힌 검색 | 포괄적 검색 |

### 검색 전략 선택 가이드

**Similarity Search 선택 시:**
- 빠른 응답 속도가 중요할 때
- 명확한 키워드 질문
- 예: "BERT 논문", "Transformer 구조"

**MMR 선택 시 (권장):**
- 관련성과 다양성의 균형이 필요할 때
- 여러 관점의 정보가 필요할 때
- 예: "최신 LLM 동향", "Attention 메커니즘 종류"

**MultiQuery 선택 시:**
- 복잡하거나 모호한 질문
- 여러 관점에서의 정보 수집
- 예: "LLM의 한계와 해결 방안", "AI 윤리 문제"

---

## 🔍 실전 활용 예시

### 예시 1: 기본 논문 검색

```python
from src.rag.retriever import RAGRetriever

# Retriever 초기화
retriever = RAGRetriever(
    collection_name="paper_chunks",
    search_type="mmr",
    k=5,
    fetch_k=20,
    lambda_mult=0.5
)

# 검색 실행
question = "Transformer의 Self-Attention 메커니즘을 설명해줘"
docs = retriever.invoke(question)

# 결과 출력
for i, doc in enumerate(docs):
    print(f"[{i+1}] {doc.metadata['paper_title']}")
    print(f"내용: {doc.page_content[:200]}...")
    print()
```

### 예시 2: 연도 필터 검색

```python
# 2023년 이후 논문만 검색
recent_docs = retriever.search_with_filter(
    query="최신 LLM 모델",
    filter_dict={
        "publish_date": {"$gte": "2023-01-01"}
    },
    k=5
)
```

### 예시 3: MultiQuery로 포괄적 검색

```python
# 여러 관점에서 검색
docs = retriever.multi_query_search(
    query="Transformer의 장단점",
    k=7
)
# Solar Pro2가 자동으로 질문을 확장:
# - "Transformer 모델의 장점은?"
# - "Transformer의 단점과 한계는?"
# - "Transformer와 다른 모델의 차이는?"
```

### 예시 4: 점수 기반 필터링

```python
# 유사도 점수와 함께 검색
docs_with_scores = retriever.similarity_search_with_score(
    query="BERT 사전학습",
    k=10
)

# 점수 0.8 이상만 필터링
high_quality_docs = [
    doc for doc, score in docs_with_scores
    if score >= 0.8
]
```

---

## ⚙️ 설정 및 최적화

### configs/model_config.yaml 설정

```yaml
rag:
  chunk_size: 1000                    # 청크 크기 (문자 단위)
  chunk_overlap: 200                  # 청크 오버랩 (문자 단위)
  top_k: 5                            # 검색 결과 개수
  search_type: mmr                    # 검색 타입 (similarity, mmr)
  mmr_lambda: 0.5                     # MMR 다양성 파라미터 (0~1)
  score_threshold: 0.7                # 유사도 점수 임계값

  # MultiQueryRetriever용 LLM 설정
  multiquery_llm:
    provider: solar                   # MultiQuery용 LLM 제공자
    model: solar-pro2                 # MultiQuery용 모델
    temperature: 0.0                  # 쿼리 생성은 결정론적
```

### 성능 최적화 팁

#### 1. chunk_size 최적화
- **1000자 (기본)**: 균형잡힌 설정
- **500자**: 더 정밀한 검색, 많은 청크
- **2000자**: 넓은 컨텍스트, 적은 청크

#### 2. k 값 조정
- **k=3**: 빠른 응답, 핵심 정보만
- **k=5 (기본)**: 균형잡힌 정보량
- **k=10**: 포괄적 정보 수집

#### 3. MMR lambda_mult 조정
- **0.0**: 최대 다양성 (서로 다른 주제)
- **0.5 (기본)**: 균형
- **1.0**: 최대 관련성 (유사한 내용)

#### 4. fetch_k 조정
- **fetch_k = 4 × k**: 기본 권장
- MMR 후보 수가 많을수록 다양성 확보
- 너무 크면 성능 저하

---

## 🐛 트러블슈팅

### 문제 1: 검색 결과가 부정확함

**원인**: 임베딩 모델이 질문의 의도를 제대로 파악하지 못함

**해결책**:
- MultiQuery Retriever 사용
- chunk_size 조정 (더 작게)
- 메타데이터 필터 활용

### 문제 2: 검색 속도가 느림

**원인**: MultiQuery나 큰 k 값 사용

**해결책**:
- Similarity Search로 전환
- k 값 줄이기 (5 → 3)
- PostgreSQL 인덱스 확인

### 문제 3: 중복된 내용이 많음

**원인**: chunk_overlap이 너무 큼

**해결책**:
- MMR 모드 사용 (lambda_mult=0.3~0.5)
- chunk_overlap 줄이기 (200 → 100)
- 중복 제거는 자동으로 수행됨

### 문제 4: MultiQuery가 동작하지 않음

**원인**: Solar API 키가 없거나 MultiQueryRetriever 미설치

**해결책**:
```bash
# Solar API 키 설정
export SOLAR_API_KEY="your-api-key"

# MultiQueryRetriever 설치
pip install langchain-community
```

자동으로 기본 retriever로 폴백됨 (에러 발생 안함)

---

## 📈 성능 지표

### 벤치마크 (paper_chunks 컬렉션 기준)

| 검색 전략 | 평균 응답 시간 | Top-5 정확도 | 다양성 점수 |
|----------|---------------|-------------|-----------|
| **Similarity** | 0.15초 | 82% | 3.2/5.0 |
| **MMR (λ=0.5)** | 0.18초 | 87% | 4.5/5.0 |
| **MultiQuery** | 0.85초 | 91% | 4.1/5.0 |

### 데이터셋 현황

| 메트릭 | 값 |
|--------|-----|
| 총 논문 수 | 100편+ |
| 총 청크 수 | 5,000개+ |
| 평균 청크 크기 | 800자 |
| 벡터 차원 | 1536 |
| 데이터베이스 크기 | ~500MB |

---

## 🔄 향후 확장 계획

### 1. Hybrid Search (Vector + Keyword)
- pgvector + PostgreSQL Full-Text Search 결합
- BM25 + Cosine Similarity 점수 통합
- 키워드 중심 질문의 정확도 향상

### 2. Reranking 통합
- Cohere Rerank API 통합
- Cross-Encoder 모델 활용
- 검색 결과의 재정렬로 정확도 향상

### 3. Query Understanding 강화
- 의도 분류 (Fact-Finding, Comparison, Explanation)
- 엔티티 추출 (논문명, 저자명, 용어)
- 검색 쿼리 자동 최적화

### 4. 캐싱 시스템
- Redis 기반 검색 결과 캐싱
- 동일 질문의 응답 속도 향상
- 비용 절감 (임베딩 API 호출 감소)

---

## 📚 참고 자료

### 내부 문서
- [PRD/13_RAG_시스템_설계.md](../PRD/13_RAG_시스템_설계.md)
- [08_데이터베이스_통합_가이드.md](./08_데이터베이스_통합_가이드.md)
- [06_도구_시스템.md](./06_도구_시스템.md) - RAG 검색 도구

### 외부 자료
- [LangChain PGVector 문서](https://python.langchain.com/docs/integrations/vectorstores/pgvector)
- [pgvector 공식 문서](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [MMR 알고리즘 논문](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf)

---

## ✅ 체크리스트

RAG 시스템을 처음 사용하는 팀원을 위한 체크리스트:

- [ ] PostgreSQL + pgvector 설치 완료
- [ ] OpenAI API 키 설정 (`OPENAI_API_KEY`)
- [ ] Solar API 키 설정 (`SOLAR_API_KEY`, MultiQuery 사용 시)
- [ ] configs/db_config.yaml 설정 완료
- [ ] paper_chunks 컬렉션에 데이터 존재
- [ ] RAGRetriever 클래스 초기화 성공
- [ ] 기본 검색 테스트 완료
- [ ] MMR 검색 테스트 완료
- [ ] MultiQuery 검색 테스트 완료

---

**문서 끝**
