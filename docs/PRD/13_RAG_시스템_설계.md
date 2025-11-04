# 13. RAG 시스템 설계

## 문서 정보
- **작성일**: 2025-10-30
- **프로젝트명**: 논문 리뷰 챗봇 (AI Agent + RAG)
- **팀명**: 연결의 민족
- **작성자**: 최현화[팀장]

---

## 1. RAG 파이프라인

### 1.1 전체 흐름

```mermaid
graph TB
    subgraph Prepare["🔸 데이터 준비"]
        direction LR
        A[논문 수집<br/>arXiv] --> B[텍스트 추출<br/>PDF → Text]
        B --> C[청크 분할<br/>1000자 단위]
        C --> D[임베딩<br/>OpenAI]
        D --> E[💾 VectorDB<br/>pgvector]
    end

    subgraph Search["🔹 검색"]
        direction LR
        F[사용자 질문] --> G[질문 임베딩]
        G --> H[유사도 검색<br/>Top-K]
        H --> I[관련 문서]
    end

    subgraph Generate["🔺 답변 생성"]
        direction LR
        J[컨텍스트 구성] --> K[LLM 생성<br/>OpenAI / Solar]
        K --> L[✅ 답변]
    end

    Prepare --> Search
    Search --> Generate
    E -.-> H
    I --> J

    %% Subgraph 스타일
    style Prepare fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    style Search fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style Generate fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000

    %% 노드 스타일 (데이터 준비 - 파랑 계열)
    style A fill:#90caf9,stroke:#1976d2,color:#000
    style B fill:#64b5f6,stroke:#1976d2,color:#000
    style C fill:#42a5f5,stroke:#1565c0,color:#000
    style D fill:#64b5f6,stroke:#1976d2,color:#000
    style E fill:#42a5f5,stroke:#1565c0,color:#000

    %% 노드 스타일 (검색 - 보라 계열)
    style F fill:#ce93d8,stroke:#7b1fa2,color:#000
    style G fill:#ba68c8,stroke:#7b1fa2,color:#fff
    style H fill:#ab47bc,stroke:#4a148c,color:#fff
    style I fill:#9c27b0,stroke:#4a148c,color:#fff

    %% 노드 스타일 (답변 생성 - 녹색 계열)
    style J fill:#a5d6a7,stroke:#388e3c,color:#000
    style K fill:#81c784,stroke:#2e7d32,color:#000
    style L fill:#66bb6a,stroke:#2e7d32,color:#fff
```

**RAG 파이프라인 설명:**
- RAG 시스템의 전체 흐름을 데이터 준비, 검색, 답변 생성 3단계로 구분하여 표현
- 데이터 준비 단계에서는 arXiv에서 논문을 수집하고 PDF에서 텍스트를 추출한 후 1000자 단위로 청크를 분할하며, OpenAI로 임베딩을 생성하여 pgvector에 저장
- 검색 단계에서는 사용자 질문을 임베딩으로 변환하고 유사도 검색을 통해 Top-K 관련 문서를 추출
- 답변 생성 단계에서는 검색된 문서로 컨텍스트를 구성하고 LLM(OpenAI/Solar)이 최종 답변을 생성하여 사용자에게 전달

---

## 2. 문서 처리

### 2.1 텍스트 분할

**필요 라이브러리:**
- `langchain.text_splitter` - RecursiveCharacterTextSplitter

**텍스트 분할 파라미터:**

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| chunk_size | 1000 | 청크 최대 크기 (문자 수) |
| chunk_overlap | 200 | 청크 간 겹치는 부분 (문자 수) |
| separators | ["\n\n", "\n", ". ", " ", ""] | 분할 우선순위 (단락 → 줄 → 문장 → 단어) |

**분할 방식:**
- RecursiveCharacterTextSplitter 사용
- 문서를 청크 단위로 분할
- split_documents() 메서드로 문서 리스트 처리

**구현 파일:** `src/rag/text_splitter.py`

### 2.2 임베딩 생성

**필요 라이브러리:**
- `langchain_openai` - OpenAIEmbeddings

**임베딩 모델 설정:**

| 항목 | 값 | 설명 |
|------|-----|------|
| 모델명 | text-embedding-3-small | OpenAI 임베딩 모델 |
| 차원 | 1536 | 벡터 차원 수 |

**임베딩 생성 방식:**
- OpenAIEmbeddings 인스턴스 생성
- embed_documents() 메서드로 청크 리스트 임베딩
- 각 청크의 page_content를 임베딩으로 변환

**구현 파일:** `src/rag/embeddings.py`

---

## 3. Vector Store

### 3.1 pgvector 연동

**필요 라이브러리:**
- `langchain_postgres.vectorstores` - PGVector

**PGVector 설정:**

| 파라미터 | 설명 |
|---------|------|
| collection_name | "paper_chunks" - 컬렉션 이름 |
| embedding_function | OpenAIEmbeddings 인스턴스 |
| connection_string | PostgreSQL 연결 문자열 |

**연결 문자열 형식:**
- `postgresql://user:password@localhost:5432/papers`
- 환경 변수로 관리 (DATABASE_URL)

**문서 추가 방식:**
- add_documents() 메서드로 청크 리스트 추가
- 자동으로 임베딩 생성 및 저장

**구현 파일:** `src/rag/vectorstore.py`

### 3.2 검색 방식

**검색 타입:**

| 타입 | 메서드 | 설명 |
|------|--------|------|
| Similarity Search | similarity_search(query, k) | 유사도 검색으로 Top-K 문서 반환 |
| MMR | max_marginal_relevance_search(query, k, fetch_k) | 다양성을 고려한 검색 (중복 제거) |

**MMR 파라미터:**

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| k | 5 | 최종 반환할 문서 수 |
| fetch_k | 20 | 초기 검색할 문서 수 (다양성 선택 전) |

**구현 파일:** `src/rag/vectorstore.py`

---

## 4. Retriever

### 4.1 기본 Retriever

**Retriever 생성 방식:**
- vectorstore.as_retriever() 메서드 사용
- 검색 타입 및 파라미터 설정

**Retriever 설정:**

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| search_type | "mmr" | MMR 검색 사용 |
| search_kwargs | {"k": 5, "fetch_k": 20} | 검색 파라미터 딕셔너리 |

**사용 방식:**
- retriever.invoke(query) 메서드로 검색
- 질문 문자열 입력 → 관련 문서 리스트 반환

**구현 파일:** `src/rag/retriever.py`

### 4.2 MultiQueryRetriever

**필요 라이브러리:**
- `langchain.retrievers` - MultiQueryRetriever

**MultiQueryRetriever 설명:**
- 질문을 여러 개의 변형된 질문으로 확장
- 각 질문으로 검색 후 결과 병합
- 더 포괄적인 검색 결과 제공

**생성 방식:**

| 파라미터 | 설명 |
|---------|------|
| retriever | 기본 retriever 인스턴스 |
| llm | 질문 변형 생성에 사용할 LLM |

**동작 흐름:**
1. LLM이 원본 질문을 여러 변형 질문으로 생성
2. 각 변형 질문으로 retriever 검색
3. 모든 결과를 병합하여 반환

**구현 파일:** `src/rag/retriever.py`

---

## 5. 용어집 통합

### 5.1 용어집 검색

**용어집 전용 Vector Store 설정:**

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| collection_name | "glossary_embeddings" | 용어집 컬렉션 이름 |
| embedding_function | OpenAIEmbeddings 인스턴스 |
| connection_string | PostgreSQL 연결 문자열 |

**용어 검색 방식:**
- glossary_store.similarity_search(term, k=3)
- 용어와 관련된 상위 3개 정의 반환

**구현 파일:** `src/rag/glossary_search.py`

### 5.2 하이브리드 검색

**하이브리드 검색 함수:**

| 요소 | 설명 |
|------|------|
| 함수명 | hybrid_search(query, difficulty) |
| 입력 | query (질문), difficulty (난이도) |
| 반환 | combined_context (결합된 컨텍스트 문자열) |

**검색 프로세스:**

| 단계 | 동작 | 파라미터 |
|------|------|---------|
| 1. 용어집 검색 | glossary_store.similarity_search() | k=2 (상위 2개 용어) |
| 2. 논문 검색 | vectorstore.similarity_search() | k=3 (상위 3개 논문 청크) |
| 3. 결합 | 용어와 논문을 하나의 컨텍스트로 결합 | "### 용어:\n" + "### 논문:\n" |

**결합 형식:**
```
### 용어:
[용어집 검색 결과]

### 논문:
[논문 검색 결과]
```

**구현 파일:** `src/rag/hybrid_search.py`

---

## 6. 프롬프트 구성

### 6.1 RAG 프롬프트 구조

**프롬프트 섹션:**

| 섹션 | 내용 |
|------|------|
| 역할 정의 | "당신은 논문 리뷰 전문가입니다" |
| 참고 논문 | {context} - 검색된 논문 내용 |
| 질문 | {question} - 사용자 질문 |
| 난이도 | {difficulty} - easy 또는 hard |

**답변 규칙:**

| 규칙 | 설명 |
|------|------|
| 근거 기반 | 참고 논문의 내용을 기반으로 답변 |
| 출처 명시 | 논문 제목, 저자 명시 |
| 정확성 | 논문에 없는 내용은 추측하지 말 것 |
| 난이도 준수 | 선택된 난이도에 맞는 설명 |

**프롬프트 템플릿 변수:**

| 변수 | 설명 | 예시 |
|------|------|------|
| {context} | 검색된 문서 내용 | "논문 제목: ..., 저자: ..., 내용: ..." |
| {question} | 사용자 질문 | "Transformer의 핵심 개념은?" |
| {difficulty} | 난이도 | "easy" 또는 "hard" |

**구현 파일:** `prompts/rag_prompts.py`

---

## 7. 참고 자료

- Langchain RAG: https://python.langchain.com/docs/tutorials/rag/
- Langchain VectorStores: https://python.langchain.com/docs/integrations/vectorstores/
