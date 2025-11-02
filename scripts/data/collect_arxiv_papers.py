# scripts/data/collect_arxiv_papers.py

"""
arXiv 논문 수집 스크립트

ArxivClient를 래핑하여 PDF 다운로드 및 메타데이터 저장 기능을 제공합니다.
"""

# ==================================================================================== #
#                                   IMPORT MODULES                                     #
# ==================================================================================== #

# ------------------------- 표준 라이브러리 ------------------------- #
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set

# ------------------------- 서드파티 라이브러리 ------------------------- #
import arxiv
from dotenv import load_dotenv

# ------------------------- 프로젝트 모듈 ------------------------- #
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.papers.infra.arxiv_client import ArxivClient
from src.utils.experiment_manager import ExperimentManager


# ==================================================================================== #
#                                ENVIRONMENT LOADING                                   #
# ==================================================================================== #

load_dotenv(ROOT / ".env")


# ==================================================================================== #
#                            ARXIV PAPER COLLECTOR CLASS                               #
# ==================================================================================== #

class ArxivPaperCollector:
    """
    arXiv 논문 수집 클래스

    ArxivClient를 래핑하여 PDF 다운로드 및 메타데이터 저장을 수행합니다.
    """

    def __init__(self, save_dir: str = "data/raw/pdfs", exp_manager: ExperimentManager = None):
        """
        Args:
            save_dir: PDF 파일 저장 디렉토리
            exp_manager: ExperimentManager 인스턴스 (선택적)
        """
        self.save_dir = Path(ROOT) / save_dir
        self.exp_manager = exp_manager
        self.client = ArxivClient(max_results_default=20)

        # -------------- 디렉토리 생성 -------------- #
        self.save_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------- 논문 수집 ---------------------- #
    def collect_papers(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        arXiv에서 논문 수집

        Args:
            query: 검색 쿼리
            max_results: 최대 수집 논문 수

        Returns:
            논문 메타데이터 리스트
        """
        # 로그 기록
        if self.exp_manager:
            self.exp_manager.logger.write(f"검색 시작: query={query}, max_results={max_results}")

        # -------------- ArxivClient로 메타데이터 수집 -------------- #
        papers_dto = self.client.search(query, max_results=max_results)

        papers_data = []

        # -------------- 각 논문에 대해 PDF 다운로드 및 메타데이터 변환 -------------- #
        for dto in papers_dto:
            try:
                # -------------- 메타데이터 구성 -------------- #
                paper_info = {
                    "title": dto.title,
                    "authors": ", ".join(dto.authors),           # 저자 목록 문자열로 변환
                    "published_date": dto.published_at.strftime("%Y-%m-%d") if dto.published_at else None,
                    "summary": dto.abstract,
                    "pdf_url": dto.pdf_url,
                    "entry_id": f"http://arxiv.org/abs/{dto.arxiv_id}",
                    "categories": [],                            # ArxivClient는 카테고리 미제공
                    "primary_category": None,
                }

                papers_data.append(paper_info)

                # -------------- PDF 다운로드 -------------- #
                if dto.pdf_url:
                    pdf_filename = self.save_dir / f"{dto.arxiv_id}.pdf"

                    # PDF 파일이 이미 존재하면 건너뛰기
                    if pdf_filename.exists():
                        if self.exp_manager:
                            self.exp_manager.logger.write(f"이미 존재: {dto.arxiv_id}.pdf")
                        continue

                    # arxiv 패키지로 PDF 다운로드
                    self._download_pdf(dto.arxiv_id, pdf_filename)

                    if self.exp_manager:
                        self.exp_manager.logger.write(f"다운로드 완료: {dto.title} ({dto.arxiv_id})")

            except Exception as e:
                if self.exp_manager:
                    self.exp_manager.logger.write(f"오류 발생: {dto.title} - {e}")
                continue

        return papers_data

    # ---------------------- PDF 다운로드 ---------------------- #
    def _download_pdf(self, arxiv_id: str, save_path: Path):
        """
        arxiv 패키지를 사용하여 PDF 다운로드

        Args:
            arxiv_id: arXiv ID
            save_path: 저장할 파일 경로
        """
        try:
            # -------------- arxiv.Search로 논문 검색 -------------- #
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(search.results())

            # -------------- PDF 다운로드 -------------- #
            paper.download_pdf(filename=str(save_path))

        except Exception as e:
            if self.exp_manager:
                self.exp_manager.logger.write(f"PDF 다운로드 실패: {arxiv_id} - {e}")
            raise

    # ---------------------- 여러 키워드로 수집 ---------------------- #
    def collect_by_keywords(self, keywords: List[str], per_keyword: int = 15) -> List[Dict]:
        """
        여러 키워드로 논문 수집

        Args:
            keywords: 키워드 리스트
            per_keyword: 키워드당 수집할 논문 수

        Returns:
            전체 논문 메타데이터 리스트
        """
        all_papers = []

        # -------------- 각 키워드로 반복 수집 -------------- #
        for keyword in keywords:
            if self.exp_manager:
                self.exp_manager.logger.write(f"\n키워드 수집 시작: {keyword}")

            papers = self.collect_papers(keyword, max_results=per_keyword)
            all_papers.extend(papers)

        # -------------- 중복 제거 -------------- #
        unique_papers = self.remove_duplicates(all_papers)

        if self.exp_manager:
            self.exp_manager.logger.write(f"\n총 수집: {len(all_papers)}편 → 중복 제거: {len(unique_papers)}편")

        return unique_papers

    # ---------------------- 중복 제거 ---------------------- #
    def remove_duplicates(self, papers: List[Dict]) -> List[Dict]:
        """
        제목 기준으로 중복 논문 제거

        Args:
            papers: 논문 리스트

        Returns:
            중복 제거된 논문 리스트
        """
        seen_titles: Set[str] = set()
        unique_papers = []

        # -------------- 각 논문의 제목 확인 -------------- #
        for paper in papers:
            title_normalized = paper["title"].lower().strip()

            # -------------- 중복되지 않은 논문만 추가 -------------- #
            if title_normalized not in seen_titles:
                unique_papers.append(paper)
                seen_titles.add(title_normalized)

        return unique_papers


# ==================================================================================== #
#                                    MAIN SCRIPT                                       #
# ==================================================================================== #

def main():
    """메인 실행 함수"""

    print("=" * 70)
    print("arXiv 논문 수집 시작")
    print("=" * 70)

    # ---------------------- ExperimentManager 초기화 ---------------------- #
    with ExperimentManager() as exp:
        # -------------- ArxivPaperCollector 생성 -------------- #
        collector = ArxivPaperCollector(exp_manager=exp)

        # -------------- AI/ML 관련 키워드 -------------- #
        keywords = [
            "transformer attention",
            "BERT GPT",
            "large language model",
            "retrieval augmented generation",
            "neural machine translation",
            "question answering",
            "AI agent",
        ]

        # -------------- 키워드당 15편씩 수집 -------------- #
        papers = collector.collect_by_keywords(keywords, per_keyword=15)

        exp.logger.write(f"\n총 {len(papers)}편의 논문 수집 완료")

        # -------------- 메타데이터 JSON 파일 저장 -------------- #
        metadata_path = ROOT / "data" / "raw" / "arxiv_papers_metadata.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)

        exp.logger.write(f"메타데이터 저장 완료: {metadata_path}")

    print("\n" + "=" * 70)
    print("✅ arXiv 논문 수집 완료")
    print("=" * 70)


# ==================================================================================== #
#                                SCRIPT ENTRY POINT                                    #
# ==================================================================================== #

if __name__ == "__main__":
    main()
