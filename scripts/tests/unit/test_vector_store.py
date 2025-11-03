# tests/unit/test_vector_store.py

"""
PGVector 벡터 검색 테스트

Langchain PGVector를 사용하여 문서 추가 및 유사도 검색을 테스트합니다.
"""

# ------------------------- 서드파티 라이브러리 ------------------------- #
from langchain.schema import Document

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.database.vector_store import get_pgvector_store


# ==================== 메인 테스트 ==================== #
if __name__ == "__main__":
    print("=" * 80)
    print("PGVector 벡터 검색 테스트 시작")
    print("=" * 80)

    # ---------------------- 1. VectorStore 인스턴스 생성 ---------------------- #
    print("\n[1] VectorStore 초기화")
    print("-" * 80)
    vector_store = get_pgvector_store(collection_name="paper_chunks")
    print("✅ VectorStore 초기화 완료")

    # ---------------------- 2. 샘플 문서 추가 ---------------------- #
    print("\n[2] 샘플 문서 추가")
    print("-" * 80)

    sample_documents = [
        Document(
            page_content="The Transformer is a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output.",
            metadata={"source": "Attention Is All You Need", "page": 1, "chunk_id": 1}
        ),
        Document(
            page_content="BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
            metadata={"source": "BERT", "page": 1, "chunk_id": 1}
        ),
        Document(
            page_content="GPT-3 demonstrates that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches.",
            metadata={"source": "GPT-3", "page": 1, "chunk_id": 1}
        ),
        Document(
            page_content="Self-attention, sometimes called intra-attention is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence.",
            metadata={"source": "Attention Is All You Need", "page": 2, "chunk_id": 2}
        ),
        Document(
            page_content="The dominant approach to neural machine translation is based on sequence-to-sequence models with an encoder-decoder architecture.",
            metadata={"source": "Neural Machine Translation", "page": 1, "chunk_id": 1}
        )
    ]

    try:
        ids = vector_store.add_documents(sample_documents)
        print(f"✅ {len(ids)}개 문서 추가 완료")
        print(f"문서 ID: {ids}")
    except Exception as e:
        print(f"⚠️  문서 추가 중 오류 발생: {e}")
        print("(이미 추가된 문서일 수 있습니다)")

    # ---------------------- 3. 유사도 검색 (Similarity Search) ---------------------- #
    print("\n[3] 유사도 검색 (Similarity Search)")
    print("-" * 80)

    query = "What is the transformer architecture?"
    print(f"검색 쿼리: '{query}'")
    print()

    docs = vector_store.similarity_search(query, k=3)
    print(f"✅ {len(docs)}개 유사 문서 검색 완료")

    print("\n검색 결과:")
    for i, doc in enumerate(docs, 1):
        print(f"\n[{i}] {doc.page_content[:150]}...")
        print(f"    메타데이터: {doc.metadata}")

    # ---------------------- 4. MMR 검색 (다양성) ---------------------- #
    print("\n[4] MMR 검색 (Maximal Marginal Relevance)")
    print("-" * 80)

    query = "pre-training language models"
    print(f"검색 쿼리: '{query}'")
    print()

    docs = vector_store.max_marginal_relevance_search(query, k=3, lambda_mult=0.5)
    print(f"✅ {len(docs)}개 다양한 문서 검색 완료")

    print("\n검색 결과 (다양성 고려):")
    for i, doc in enumerate(docs, 1):
        print(f"\n[{i}] {doc.page_content[:150]}...")
        print(f"    메타데이터: {doc.metadata}")

    # ---------------------- 5. 유사도 점수 포함 검색 ---------------------- #
    print("\n[5] 유사도 점수 포함 검색")
    print("-" * 80)

    query = "attention mechanism"
    print(f"검색 쿼리: '{query}'")
    print()

    docs_with_scores = vector_store.similarity_search_with_score(query, k=3)

    print("\n검색 결과 (유사도 점수 포함):")
    for i, (doc, score) in enumerate(docs_with_scores, 1):
        print(f"\n[{i}] 유사도 점수: {score:.4f}")
        print(f"    내용: {doc.page_content[:150]}...")
        print(f"    메타데이터: {doc.metadata}")

    print("\n" + "=" * 80)
    print("✅ PGVector 벡터 검색 테스트 완료")
    print("=" * 80)
