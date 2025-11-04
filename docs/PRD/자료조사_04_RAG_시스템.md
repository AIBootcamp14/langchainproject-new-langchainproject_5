# 자료조사: RAG 시스템 설계

## 문서 정보
- **작성일**: 2025-10-29
- **프로젝트**: 논문 리뷰 챗봇 (AI Agent + RAG)
- **팀명**: 연결의 민족

---

## 1. RAG (Retrieval-Augmented Generation) 개요

### 1.1 RAG란?

**RAG**는 외부 지식 베이스(Knowledge Base)에서 관련 정보를 검색(Retrieval)하여 LLM의 답변 생성(Generation)을 보강하는 기술입니다.

### 1.2 RAG의 필요성

1. **LLM의 한계 극복**
   - LLM은 학습 데이터 기준 시점 이후의 정보를 모름
   - 특정 도메인(논문)에 대한 깊이 있는 지식 부족
   - Hallucination(환각) 문제 해결

2. **논문 리뷰 챗봇에서의 중요성**
   - 수천 개의 논문 정보를 LLM이 직접 학습 불가능
   - 정확한 출처와 인용 제공 필요
   - 최신 논문까지 커버 가능

---

## 2. RAG 시스템 구조

### 2.1 전체 파이프라인

```
[데이터 수집] → [전처리] → [청크 분할] → [임베딩] → [Vector DB 저장]
                                                            ↓
[사용자 질문] → [질문 임베딩] → [유사도 검색] → [관련 문서 조회] → [LLM에 전달] → [답변 생성]
```

### 2.2 Mermaid 다이어그램

```mermaid
graph TB
    subgraph Prepare["🔸 단계 1: 데이터 준비 & 저장"]
        direction LR
        A[논문 데이터 수집<br/>📊 arXiv, Scholar] --> B[데이터 전처리<br/>PDF → 텍스트]
        B --> C[텍스트 청크 분할<br/>1000자 단위]
        C --> D[임베딩 벡터 생성<br/>OpenAI Embeddings]
        D --> E[💾 Vector DB 저장<br/>pgvector]
    end

    subgraph Search["🔹 단계 2: 검색 & 조회"]
        direction LR
        F[사용자 질문 입력] --> G[질문 임베딩<br/>벡터 변환]
        G --> H[유사도 검색<br/>Cosine Similarity]
        H --> I[관련 문서 Top-K<br/>상위 5개 조회]
    end

    subgraph Generate["🔺 단계 3: 답변 생성"]
        direction LR
        J[컨텍스트 구성<br/>문서 + 질문] --> K[LLM 답변 생성<br/>GPT-5]
        K --> L[✅ 사용자 응답<br/>난이도 적용]
    end

    %% 단계 간 연결
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
    style B fill:#81d4fa,stroke:#0288d1,color:#000
    style C fill:#64b5f6,stroke:#1976d2,color:#000
    style D fill:#42a5f5,stroke:#1565c0,color:#000
    style E fill:#1e88e5,stroke:#0d47a1,color:#fff

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

---

## 3. 데이터 수집 및 전처리

### 3.1 논문 데이터 수집

**데이터 소스:**
1. arXiv API (최신 논문)
2. Google Scholar (인용 정보)
3. Semantic Scholar API (논문 메타데이터)
4. 수동 업로드 (PDF 파일)

### 3.2 데이터 텍스트화

**지원 형식:**
- PDF → `PyPDF2`, `pdfplumber`
- HTML → `BeautifulSoup4`
- LaTeX → `pandoc`

**필요 라이브러리:** `langchain.document_loaders.PyPDFLoader`, `langchain.document_loaders.ArxivLoader`

**문서 로더 설정:**

| 로더 | 파라미터 | 설명 |
|------|----------|------|
| PyPDFLoader | file_path | PDF 파일 경로 지정 |
| ArxivLoader | query, max_docs | 검색 쿼리 및 최대 문서 수 |

**사용 방법:**
1. PDF 파일 로드: PyPDFLoader로 로컬 PDF 파일 읽기
2. arXiv 직접 로드: ArxivLoader로 arXiv API에서 논문 검색 및 로드

### 3.3 메타데이터 추출

**추출 정보:**
- 제목 (Title)
- 저자 (Authors)
- 출판일 (Publication Date)
- 출처 (Source: arXiv, IEEE, ACL 등)
- 키워드/카테고리 (Keywords/Category)
- DOI/URL
- 초록 (Abstract)

**PostgreSQL 저장:**

**필요 라이브러리:** `psycopg2`

**함수: save_paper_metadata**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| paper_data | dict | 논문 메타데이터 딕셔너리 |

**paper_data 필드:**
- title: 논문 제목
- authors: 저자 목록
- publish_date: 출판일
- source: 출처 (arXiv, IEEE 등)
- url: 논문 URL
- abstract: 초록
- category: 카테고리

**반환값:** paper_id (int)

**처리 흐름:**
1. PostgreSQL 연결
2. papers 테이블에 INSERT 실행
3. RETURNING으로 생성된 paper_id 반환
4. 커밋 및 연결 종료

---

## 4. 텍스트 청크 분할 (Text Splitting)

### 4.1 청크 분할의 필요성

- LLM의 컨텍스트 윈도우 제한
- 임베딩 모델의 토큰 제한
- 검색 정확도 향상 (작은 청크가 더 관련성 높은 정보 포함)

### 4.2 청크 분할 전략

**RecursiveCharacterTextSplitter (추천)**

**필요 라이브러리:** `langchain.text_splitter.RecursiveCharacterTextSplitter`

**설정 파라미터:**

| 파라미터 | 권장값 | 설명 |
|---------|--------|------|
| chunk_size | 1000 | 청크 크기 (문자 수) |
| chunk_overlap | 200 | 청크 간 중복 (맥락 유지) |
| separators | ["\n\n", "\n", ". ", " ", ""] | 분할 우선순위 (단락 → 문장 → 단어) |
| length_function | len | 길이 측정 함수 |

**사용 방법:** split_documents(documents)로 문서 리스트를 청크로 분할

**논문 구조 기반 분할 (고급)**

논문의 섹션 구조를 활용한 분할:
- Abstract (초록)
- Introduction (서론)
- Related Work (관련 연구)
- Method (방법론)
- Experiments (실험)
- Conclusion (결론)

**함수: split_by_sections**

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| paper_text | str | 논문 전체 텍스트 |

**반환값:** dict - 섹션별로 분리된 텍스트 딕셔너리

**추출 섹션:**
- abstract: 초록
- introduction: 서론
- method: 방법론
- experiments: 실험
- conclusion: 결론

**청크 크기 권장사항:**
- **Small (500-800자)**: 정확한 검색, 작은 질문에 적합
- **Medium (1000-1500자)**: 균형잡힌 선택 (추천)
- **Large (2000-3000자)**: 넓은 맥락, 요약 작업에 적합

---

## 5. 임베딩 (Embedding)

### 5.1 임베딩 모델 선택

**OpenAI Embedding Models:**

| 모델 | 차원 | 비용 (1M tokens) | 사용 권장 |
|------|------|------------------|-----------|
| text-embedding-3-small | 1536 | $0.02 | ✅ 권장 (비용 효율) |
| text-embedding-3-large | 3072 | $0.13 | 높은 정확도 필요 시 |
| text-embedding-ada-002 | 1536 | $0.10 | 구버전 |

**필요 라이브러리:** `langchain.embeddings.OpenAIEmbeddings`

**OpenAIEmbeddings 설정:**

| 파라미터 | 권장값 | 설명 |
|---------|--------|------|
| model | "text-embedding-3-small" | 임베딩 모델명 |
| openai_api_key | 환경변수에서 로드 | OpenAI API 키 |

**사용 방법:**
- embed_query(text): 단일 텍스트 임베딩
- 반환 벡터 차원: 1536 (text-embedding-3-small)

### 5.2 임베딩 저장

**Vector DB에 저장:**

**필요 라이브러리:** `langchain_postgres.vectorstores.PGVector`

**PGVector 초기화 파라미터:**

| 파라미터 | 설명 |
|---------|------|
| collection_name | 컬렉션명 (예: "paper_embeddings") |
| embedding_function | OpenAIEmbeddings 인스턴스 |
| connection_string | PostgreSQL 연결 문자열 |

**사용 방법:**
- add_documents(chunks): 문서 청크 리스트를 벡터 DB에 저장

---

## 6. Vector Database 설계

### 6.1 컬렉션 구조

**3개의 컬렉션 운영:**

#### 1. `paper_chunks` (논문 본문)
- **용도**: 논문 전체 내용 검색
- **메타데이터**: paper_id, section, page_num

#### 2. `paper_abstracts` (논문 초록)
- **용도**: 빠른 논문 개요 검색
- **메타데이터**: paper_id, title, authors

#### 3. `glossary_embeddings` (용어집)
- **용도**: 전문 용어 정의 검색
- **메타데이터**: term, category, difficulty_level

### 6.2 컬렉션별 구현

**연결 문자열:** `postgresql://user:password@localhost:5432/papers`

**3개의 PGVector 컬렉션:**

| 컬렉션명 | collection_name | 용도 |
|---------|----------------|------|
| paper_chunks_store | "paper_chunks" | 논문 본문 청크 저장 |
| abstract_store | "paper_abstracts" | 논문 초록 저장 |
| glossary_store | "glossary_embeddings" | 용어집 임베딩 저장 |

**공통 설정:**
- embedding_function: embeddings 인스턴스
- connection_string: CONNECTION_STRING

---

## 7. 용어집(Glossary) 관리 시스템 ★ 중요

### 7.1 용어집의 필요성

논문에는 전문 용어가 많이 등장하며, 초심자는 이해하기 어려움:
- "Attention Mechanism"
- "Fine-tuning"
- "BLEU Score"
- "Backpropagation"

### 7.2 용어집 데이터 구조

**PostgreSQL 테이블:**

```sql
CREATE TABLE glossary (
    term_id SERIAL PRIMARY KEY,
    term VARCHAR(200) NOT NULL UNIQUE,
    definition TEXT NOT NULL,
    easy_explanation TEXT,  -- 초심자용 설명
    hard_explanation TEXT,  -- 전문가용 설명
    category VARCHAR(100),  -- ML, NLP, CV, RL 등
    difficulty_level VARCHAR(20),  -- beginner, intermediate, advanced
    related_terms TEXT[],  -- 관련 용어
    examples TEXT,  -- 사용 예시
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 예시 데이터
INSERT INTO glossary (term, definition, easy_explanation, hard_explanation, category, difficulty_level)
VALUES (
    'Attention Mechanism',
    'A technique that allows models to focus on specific parts of the input when generating output.',
    '책을 읽을 때 중요한 부분에 집중하는 것처럼, AI가 입력 데이터에서 중요한 부분에 집중하는 기술입니다.',
    'A weighted sum mechanism that computes attention scores between query and key vectors, allowing the model to dynamically focus on relevant input positions during sequence processing.',
    'Deep Learning',
    'intermediate'
);
```

### 7.3 용어집 RAG 활용 방안

#### 방안 1: 용어집을 Vector DB에 임베딩 저장

**장점:**
- 사용자 질문에 용어가 포함되면 자동으로 검색됨
- 유사한 용어도 함께 찾아줌 (예: "어텐션" → "Attention")

**구현 방법:**

**함수: add_glossary_to_vectordb**

**처리 흐름:**

| 단계 | 동작 |
|------|------|
| 1 | PostgreSQL 용어집 테이블 조회 (term, definition, easy_explanation, category) |
| 2 | 각 용어를 Document 객체로 변환 |
| 3 | page_content: "용어: {term}\n정의: {definition}\n쉬운 설명: {easy_exp}" |
| 4 | metadata: term, category, type="glossary" 설정 |
| 5 | glossary_store.add_documents()로 벡터 DB에 저장 |

#### 방안 2: 질문 분석 시 용어 자동 추출 및 컨텍스트 추가

**함수: extract_and_add_glossary_context**

**목적:** 사용자 질문에서 전문 용어를 추출하여 용어집 정의를 프롬프트에 추가

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| user_query | str | 사용자 질문 |

**반환값:** str - 용어 정의 컨텍스트 (또는 빈 문자열)

**처리 흐름:**

| 단계 | 동작 |
|------|------|
| 1 | PostgreSQL 연결 |
| 2 | SQL ILIKE로 질문에 포함된 용어 검색 |
| 3 | 발견된 용어들의 easy_explanation 수집 |
| 4 | "[용어 정의]" 섹션 형식으로 컨텍스트 구성 |
| 5 | 최종 프롬프트에 glossary_context 추가 |

**SQL 쿼리:**
```sql
SELECT term, definition, easy_explanation
FROM glossary
WHERE %s ILIKE '%' || term || '%'
```

#### 방안 3: 하이브리드 검색 (Hybrid Search)

**용어집 + 논문 본문 동시 검색:**

**함수: hybrid_search**

| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| query | str | (필수) | 검색 쿼리 |
| difficulty | str | "easy" | 난이도 (easy/hard) |

**처리 흐름:**

| 단계 | 동작 | 설명 |
|------|------|------|
| 1 | 용어집 검색 | glossary_store.similarity_search(query, k=2) |
| 2 | 논문 검색 | paper_chunks_store.similarity_search(query, k=3) |
| 3 | 결과 결합 | "### 용어 정의" + "### 논문 내용" 섹션 구성 |
| 4 | 프롬프트 생성 | 난이도에 따라 "쉽게" 또는 "자세히" 요청 추가 |
| 5 | LLM 호출 | llm.invoke(prompt)로 답변 생성 |

### 7.4 용어집 자동 생성

**논문에서 자동으로 용어 추출:**

**함수: auto_generate_glossary_from_papers**

**목적:** 논문에서 중요 용어를 자동 추출하여 용어집에 추가

**처리 흐름:**

| 단계 | 동작 | 설명 |
|------|------|------|
| 1 | 용어 추출 프롬프트 구성 | "다음 논문에서 중요한 기술 용어 5개 추출" 요청 |
| 2 | LLM 호출 | llm.invoke()로 용어와 정의 추출 |
| 3 | PostgreSQL 저장 | 중복 체크 후 glossary 테이블에 INSERT |

**출력 형식:**
```
1. 용어: 정의
2. 용어: 정의
...
```

---

## 8. 검색 (Retrieval) 전략

### 8.1 기본 유사도 검색

**메서드:** vectorstore.similarity_search()

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| query | str | 검색 쿼리 텍스트 |
| k | int | 반환할 상위 문서 수 (예: 5) |

**반환값:** List[Document] - 유사도가 높은 상위 k개 문서

### 8.2 MMR (Maximal Marginal Relevance) 검색

**목적:** 관련성 높으면서도 다양한 문서 검색

**메서드:** vectorstore.max_marginal_relevance_search()

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| query | str | 검색 쿼리 |
| k | 5 | 최종 반환 문서 수 |
| fetch_k | 20 | 먼저 검색할 후보 문서 수 |
| lambda_mult | 0.5 | 관련성 vs 다양성 균형 (0~1) |

### 8.3 메타데이터 필터링

**메서드:** vectorstore.similarity_search() with filter

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| query | str | 검색 쿼리 |
| k | int | 반환 문서 수 |
| filter | dict | 메타데이터 필터 조건 |

**필터 예시:**
- `{"year": {"$gte": 2020}}`: 2020년 이후 논문만
- `{"category": "cs.AI"}`: 특정 카테고리만

### 8.4 Reranking (재순위화)

**Cohere Rerank API 사용:**

**필요 라이브러리:**
- `langchain.retrievers.ContextualCompressionRetriever`
- `langchain.retrievers.document_compressors.CohereRerank`

**설정 컴포넌트:**

| 컴포넌트 | 설정 | 설명 |
|---------|------|------|
| compressor | CohereRerank(model="rerank-english-v2.0") | Cohere Rerank 모델 |
| retriever | ContextualCompressionRetriever | 압축 및 재순위화 리트리버 |

**파라미터:**
- base_compressor: compressor 인스턴스
- base_retriever: vectorstore.as_retriever(search_kwargs={"k": 10})

**사용:** retriever.get_relevant_documents(query)로 재순위화된 문서 조회

---

## 9. LLM 프롬프트 구성

### 9.1 RAG 프롬프트 템플릿

**템플릿: RAG_PROMPT_TEMPLATE**

| 구성 요소 | 내용 |
|----------|------|
| 역할 | 논문 리뷰 전문가 |
| 참고 자료 | {context} - RAG 검색 결과 |
| 질문 | {question} - 사용자 질문 |
| 난이도 | {difficulty} - easy/hard 모드 |

**답변 규칙:**
1. 참고 논문의 내용을 기반으로 답변
2. 출처 명시 (논문 제목, 저자)
3. 논문에 없는 내용은 추측 금지
4. 난이도에 맞춰 설명 조절

### 9.2 용어집 포함 프롬프트

**템플릿: RAG_WITH_GLOSSARY_PROMPT**

| 구성 요소 | 내용 |
|----------|------|
| 역할 | 논문 리뷰 전문가 |
| 용어 정의 | {glossary_context} - 용어집 검색 결과 |
| 참고 논문 | {paper_context} - 논문 검색 결과 |
| 질문 | {question} - 사용자 질문 |

**특징:** 용어 정의와 논문 내용을 모두 포함하여 초심자도 이해 가능

---

## 10. RAG 체인 구현

### 10.1 Langchain RAG Chain

**필요 라이브러리:**
- `langchain.chains.RetrievalQA`
- `langchain.prompts.PromptTemplate`

**구성 요소:**

| 컴포넌트 | 설정 | 설명 |
|---------|------|------|
| PromptTemplate | template, input_variables | RAG_PROMPT_TEMPLATE 사용 |
| RetrievalQA | from_chain_type() | RAG 체인 생성 |

**RetrievalQA 파라미터:**

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| llm | llm 인스턴스 | LLM 모델 |
| chain_type | "stuff" | 모든 문서를 하나의 프롬프트로 결합 |
| retriever | vectorstore.as_retriever(search_kwargs={"k": 5}) | 검색기 설정 |
| chain_type_kwargs | {"prompt": prompt} | 프롬프트 템플릿 전달 |

**실행:** rag_chain.run(query, difficulty)

### 10.2 LangGraph를 활용한 복잡한 RAG

**필요 라이브러리:** `langgraph.graph.StateGraph`

**RAGState 정의:**

| 필드 | 타입 | 설명 |
|------|------|------|
| question | str | 사용자 질문 |
| difficulty | str | 난이도 (easy/hard) |
| glossary_context | str | 용어집 검색 결과 |
| paper_context | str | 논문 검색 결과 |
| final_answer | str | 최종 답변 |

**노드 함수:**

| 노드 | 동작 | 설명 |
|------|------|------|
| glossary_search_node | glossary_store.similarity_search(k=2) | 용어집 검색 및 컨텍스트 저장 |
| paper_search_node | paper_chunks_store.similarity_search(k=3) | 논문 검색 및 컨텍스트 저장 |
| generate_answer_node | llm.invoke(prompt) | RAG_WITH_GLOSSARY_PROMPT로 답변 생성 |

**그래프 구성:**

| 단계 | 동작 |
|------|------|
| 1 | StateGraph(RAGState) 생성 |
| 2 | 3개 노드 추가 (glossary_search, paper_search, generate_answer) |
| 3 | 진입점: glossary_search |
| 4 | 엣지: glossary_search → paper_search → generate_answer → END |
| 5 | workflow.compile()로 실행 가능 그래프 생성 |

---

## 11. 참고 자료

- Langchain RAG 튜토리얼: https://python.langchain.com/docs/tutorials/rag/
- Langchain Vector Stores: https://python.langchain.com/docs/integrations/vectorstores/
- pgvector 문서: https://github.com/pgvector/pgvector
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings
- Text Splitters: https://docs.langchain.com/oss/python/integrations/splitters
