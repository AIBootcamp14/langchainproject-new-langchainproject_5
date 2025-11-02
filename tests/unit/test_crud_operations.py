# tests/unit/test_crud_operations.py

"""
RDBMS CRUD 작업 테스트

데이터베이스에 샘플 논문 데이터를 삽입하고 조회/수정/삭제 작업을 테스트합니다.
"""

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.database.db import execute_query


# ==================== CREATE (삽입) ==================== #
def insert_paper(title, authors, publish_date, source, url, category, abstract):
    """
    papers 테이블에 논문 데이터 삽입

    Args:
        title: 논문 제목
        authors: 저자 목록
        publish_date: 발표 날짜 (YYYY-MM-DD)
        source: 출처 (arXiv, IEEE 등)
        url: 논문 URL
        category: 카테고리
        abstract: 초록

    Returns:
        삽입된 paper_id
    """
    query = """
        INSERT INTO papers (title, authors, publish_date, source, url, category, abstract)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
        RETURNING paper_id;
    """

    params = (title, authors, publish_date, source, url, category, abstract)
    result = execute_query(query, params, fetch=True)

    if result:
        paper_id = result[0][0]
        print(f"✅ 논문 삽입 완료: paper_id = {paper_id}")
        return paper_id
    else:
        print("ℹ️  이미 존재하는 논문입니다 (URL 중복)")
        return None


# ==================== READ (조회) ==================== #
def get_all_papers(limit=10):
    """
    모든 논문 조회

    Args:
        limit: 조회할 최대 개수

    Returns:
        논문 데이터 리스트
    """
    query = """
        SELECT paper_id, title, authors, publish_date, source, category
        FROM papers
        ORDER BY created_at DESC
        LIMIT %s;
    """

    result = execute_query(query, (limit,), fetch=True)

    # 출력
    print(f"\n📚 전체 논문 목록 (최대 {limit}개):")
    print("=" * 80)
    for row in result:
        print(f"[{row[0]}] {row[1]} ({row[3]})")
        print(f"    저자: {row[2][:50]}...")
        print(f"    카테고리: {row[5]}")
        print()

    return result


def search_papers_by_title(keyword):
    """
    제목에 키워드가 포함된 논문 검색

    Args:
        keyword: 검색 키워드

    Returns:
        검색 결과 리스트
    """
    query = """
        SELECT paper_id, title, authors, publish_date
        FROM papers
        WHERE title ILIKE %s
        ORDER BY publish_date DESC;
    """

    # ILIKE: 대소문자 구분 없는 검색
    result = execute_query(query, (f"%{keyword}%",), fetch=True)

    # 출력
    print(f"\n🔍 '{keyword}' 검색 결과:")
    print("=" * 80)
    for row in result:
        print(f"[{row[0]}] {row[1]} ({row[3]})")

    return result


# ==================== UPDATE (수정) ==================== #
def update_citation_count(paper_id, citation_count):
    """
    논문 인용 수 업데이트

    Args:
        paper_id: 논문 ID
        citation_count: 새로운 인용 수
    """
    query = """
        UPDATE papers
        SET citation_count = %s, updated_at = CURRENT_TIMESTAMP
        WHERE paper_id = %s;
    """

    execute_query(query, (citation_count, paper_id))
    print(f"✅ paper_id {paper_id}의 인용 수를 {citation_count}로 업데이트 완료")


# ==================== 메인 테스트 ==================== #
if __name__ == "__main__":
    print("=" * 80)
    print("PostgreSQL CRUD 작업 테스트 시작")
    print("=" * 80)

    # ---------------------- 1. CREATE: 샘플 논문 삽입 ---------------------- #
    print("\n[1] CREATE: 샘플 논문 삽입")
    print("-" * 80)

    papers_data = [
        {
            "title": "Attention Is All You Need",
            "authors": "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin",
            "publish_date": "2017-06-12",
            "source": "arXiv",
            "url": "https://arxiv.org/abs/1706.03762",
            "category": "cs.CL",
            "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
            "authors": "Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova",
            "publish_date": "2018-10-11",
            "source": "arXiv",
            "url": "https://arxiv.org/abs/1810.04805",
            "category": "cs.CL",
            "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers."
        },
        {
            "title": "Language Models are Few-Shot Learners",
            "authors": "Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al.",
            "publish_date": "2020-05-28",
            "source": "arXiv",
            "url": "https://arxiv.org/abs/2005.14165",
            "category": "cs.CL",
            "abstract": "Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. While typically task-agnostic in architecture, this method still requires task-specific fine-tuning datasets of thousands or tens of thousands of examples."
        }
    ]

    paper_ids = []
    for paper in papers_data:
        paper_id = insert_paper(
            title=paper['title'],
            authors=paper['authors'],
            publish_date=paper['publish_date'],
            source=paper['source'],
            url=paper['url'],
            category=paper['category'],
            abstract=paper['abstract']
        )
        if paper_id:
            paper_ids.append(paper_id)

    print(f"\n총 {len(paper_ids)}개 논문 삽입 완료")

    # ---------------------- 2. READ: 논문 조회 ---------------------- #
    print("\n[2] READ: 논문 조회")
    print("-" * 80)
    get_all_papers(limit=5)

    # ---------------------- 3. READ: 키워드 검색 ---------------------- #
    print("\n[3] READ: 키워드 검색")
    print("-" * 80)
    search_papers_by_title("Transformer")

    # ---------------------- 4. UPDATE: 인용 수 업데이트 ---------------------- #
    if paper_ids:
        print("\n[4] UPDATE: 인용 수 업데이트")
        print("-" * 80)
        update_citation_count(paper_ids[0], 50000)

    print("\n" + "=" * 80)
    print("✅ CRUD 작업 테스트 완료")
    print("=" * 80)
