#!/usr/bin/env python3
"""
arXiv Handler 테스트 스크립트

ArxivPaperHandler의 주요 기능 테스트:
1. arXiv URL 파싱
2. 메타데이터 추출
3. PDF 다운로드
4. 텍스트 추출
5. DB 저장
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# .env 파일 로딩
from dotenv import load_dotenv
load_dotenv()

from src.tools.arxiv_handler import ArxivPaperHandler


def test_arxiv_handler():
    """ArxivPaperHandler 기능 테스트"""

    print("\n" + "="*70)
    print("arXiv Handler 테스트 시작")
    print("="*70 + "\n")

    # 테스트용 arXiv URL (가벼운 논문)
    test_url = "https://arxiv.org/abs/1706.03762"  # Attention Is All You Need

    # Handler 초기화
    handler = ArxivPaperHandler(data_dir="data/raw")

    # ========== 1. URL 파싱 테스트 ========== #
    print("📌 1. URL 파싱 테스트")
    arxiv_id = handler.parse_arxiv_url(test_url)

    if arxiv_id:
        print(f"   ✅ arXiv ID 추출 성공: {arxiv_id}\n")
    else:
        print(f"   ❌ arXiv ID 추출 실패\n")
        return False

    # ========== 2. 메타데이터 추출 테스트 ========== #
    print("📌 2. 메타데이터 추출 테스트")
    metadata = handler.fetch_arxiv_metadata(arxiv_id)

    if metadata:
        print(f"   ✅ 메타데이터 추출 성공")
        print(f"   - 제목: {metadata['title'][:50]}...")
        print(f"   - 저자: {metadata['authors'][:50]}...")
        print(f"   - 발행일: {metadata['publish_date']}\n")
    else:
        print(f"   ❌ 메타데이터 추출 실패\n")
        return False

    # ========== 3. PDF 다운로드 테스트 ========== #
    print("📌 3. PDF 다운로드 테스트")
    pdf_path = handler.download_pdf(arxiv_id)

    if pdf_path and pdf_path.exists():
        file_size = pdf_path.stat().st_size / 1024  # KB
        print(f"   ✅ PDF 다운로드 성공: {pdf_path}")
        print(f"   - 파일 크기: {file_size:.2f} KB\n")
    else:
        print(f"   ❌ PDF 다운로드 실패\n")
        return False

    # ========== 4. 텍스트 추출 테스트 ========== #
    print("📌 4. 텍스트 추출 테스트")
    text = handler.extract_text_from_pdf(pdf_path)

    if text:
        print(f"   ✅ 텍스트 추출 성공")
        print(f"   - 추출된 텍스트 길이: {len(text)} 글자")
        print(f"   - 첫 100자: {text[:100].replace(chr(10), ' ')}...\n")
    else:
        print(f"   ❌ 텍스트 추출 실패\n")
        return False

    # ========== 5. papers 테이블 저장 테스트 ========== #
    print("📌 5. papers 테이블 저장 테스트")
    paper_id = handler.save_to_papers_table(metadata)

    if paper_id:
        print(f"   ✅ papers 테이블 저장 성공: paper_id={paper_id}\n")
    else:
        print(f"   ❌ papers 테이블 저장 실패\n")
        return False

    # ========== 6. pgvector 저장 테스트 ========== #
    print("📌 6. pgvector 저장 테스트")

    # 테스트를 위해 짧은 텍스트만 사용
    short_text = text[:5000] if len(text) > 5000 else text

    success = handler.save_to_pgvector(
        paper_id=paper_id,
        arxiv_id=arxiv_id,
        text=short_text,
        chunk_size=1000
    )

    if success:
        print(f"   ✅ pgvector 저장 성공\n")
    else:
        print(f"   ❌ pgvector 저장 실패\n")
        return False

    # ========== 전체 프로세스 테스트 ========== #
    print("📌 7. 전체 프로세스 테스트 (다른 논문)")
    test_url_2 = "https://arxiv.org/abs/1810.04805"  # BERT

    success = handler.process_arxiv_paper(test_url_2)

    if success:
        print(f"   ✅ 전체 프로세스 성공\n")
    else:
        print(f"   ❌ 전체 프로세스 실패\n")
        return False

    print("="*70)
    print("✅ 모든 테스트 통과!")
    print("="*70 + "\n")

    return True


if __name__ == "__main__":
    try:
        test_arxiv_handler()
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
