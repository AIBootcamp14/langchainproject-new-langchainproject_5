"""임베딩을 생성하고 Vector DB에 저장하는 스크립트.

사용법:
    python scripts/load_embeddings.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.data.document_loader import PaperDocumentLoader
from src.database.vector_store import get_pgvector_store


def main() -> int:
    """임베딩을 생성하고 Vector DB에 저장합니다."""
    
    # 설정
    pdf_dir = ROOT / "data/raw/pdfs"
    metadata_path = ROOT / "data/raw/arxiv_papers_metadata.json"
    mapping_path = ROOT / "data/processed/paper_id_mapping.json"
    
    # 파일 존재 확인
    if not pdf_dir.exists():
        print(f"❌ PDF 디렉토리가 없습니다: {pdf_dir}")
        return 1
    
    if not metadata_path.exists():
        print(f"❌ 메타데이터 파일이 없습니다: {metadata_path}")
        print("먼저 scripts/collect_arxiv_papers.py를 실행하세요.")
        return 1
    
    if not mapping_path.exists():
        print(f"❌ 매핑 파일이 없습니다: {mapping_path}")
        print("먼저 scripts/setup_database.py를 실행하세요.")
        return 1
    
    print("=" * 60)
    print("임베딩 생성 및 Vector DB 저장")
    print("=" * 60)
    print(f"PDF 디렉토리: {pdf_dir}")
    print(f"메타데이터: {metadata_path}")
    print(f"매핑 파일: {mapping_path}")
    print()
    
    # Document 로드
    print("1단계: PDF 문서 로드 및 청크 분할 중...")
    loader = PaperDocumentLoader(chunk_size=1000, chunk_overlap=200)
    
    try:
        chunks = loader.load_all_pdfs(pdf_dir, metadata_path)
        print(f"   ✅ {len(chunks)}개 청크 생성 완료")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 매핑 파일 로드
    print("\n2단계: paper_id 매핑 파일 로드 중...")
    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        print(f"   ✅ {len(mapping)}개 매핑 로드 완료")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return 1
    
    # paper_id 메타데이터 추가
    print("\n3단계: paper_id 메타데이터 추가 중...")
    enriched_docs = []
    for doc in chunks:
        # arxiv_id 추출
        arxiv_id = doc.metadata.get("arxiv_id")
        if not arxiv_id:
            # entry_id에서 추출
            entry_id = doc.metadata.get("entry_id", "")
            arxiv_id = entry_id.split("/")[-1] if entry_id else None

        # paper_id 매핑
        if arxiv_id and arxiv_id in mapping:
            doc.metadata["paper_id"] = mapping[arxiv_id]
            enriched_docs.append(doc)
        else:
            print(f"   ⚠️  paper_id를 찾을 수 없음: {arxiv_id}")

    print(f"   ✅ {len(enriched_docs)}/{len(chunks)}개 문서에 paper_id 추가 완료")

    # 임베딩 및 저장
    print("\n4단계: 임베딩 생성 및 Vector DB 저장 중...")
    print("   (시간이 소요될 수 있습니다. 배치 처리 중...)")

    try:
        # VectorStore 초기화
        vectorstore = get_pgvector_store(collection_name="paper_chunks")

        # 배치 처리
        batch_size = 50
        total = 0
        num_batches = (len(enriched_docs) + batch_size - 1) // batch_size

        for i in range(0, len(enriched_docs), batch_size):
            batch = enriched_docs[i : i + batch_size]
            batch_num = i // batch_size + 1

            try:
                vectorstore.add_documents(batch)
                total += len(batch)
                print(f"   배치 {batch_num}/{num_batches}: {len(batch)}개 문서 저장 완료 (총: {total})")

                # Rate Limit 대응
                if i + batch_size < len(enriched_docs):
                    time.sleep(0.1)

            except Exception as e:
                print(f"   ⚠️  배치 {batch_num} 실패: {e}")
                if "rate limit" in str(e).lower() or "429" in str(e):
                    print("   Rate limit 감지, 5초 대기...")
                    time.sleep(5)
                continue

        print(f"\n✅ {total}개 문서가 Vector DB에 저장되었습니다.")
        return 0

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

