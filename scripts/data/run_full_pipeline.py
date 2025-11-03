"""전체 데이터 파이프라인을 순차적으로 실행하는 스크립트.

사용법:
    python scripts/run_full_pipeline.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.utils.experiment_manager import ExperimentManager


def run_command(script_name: str, description: str, exp_manager: ExperimentManager = None) -> bool:
    """스크립트를 실행하고 결과를 반환합니다."""
    separator = "=" * 60
    print(separator)
    print(f"{description}")
    print(separator)

    if exp_manager:
        exp_manager.logger.write(separator)
        exp_manager.logger.write(description)
        exp_manager.logger.write(separator)

    script_path = ROOT / "scripts" / "data" / script_name

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(ROOT),
            check=True,
            capture_output=True,
            text=True,
        )

        # stdout 로그 기록
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(line)
                    if exp_manager:
                        exp_manager.logger.write(line)

        # stderr 로그 기록
        if result.stderr:
            for line in result.stderr.strip().split('\n'):
                if line.strip():
                    print(line, file=sys.stderr)
                    if exp_manager:
                        exp_manager.logger.write(f"[STDERR] {line}")

        success_msg = f"✅ {description} 완료\n"
        print(success_msg)
        if exp_manager:
            exp_manager.logger.write(success_msg)
        return True

    except subprocess.CalledProcessError as e:
        error_msg = f"❌ {description} 실패: {e}\n"
        print(error_msg)
        if exp_manager:
            exp_manager.logger.write(error_msg)
            if e.stdout:
                exp_manager.logger.write("=== STDOUT ===")
                exp_manager.logger.write(e.stdout)
            if e.stderr:
                exp_manager.logger.write("=== STDERR ===")
                exp_manager.logger.write(e.stderr)
        return False

    except Exception as e:
        error_msg = f"❌ 오류: {e}\n"
        print(error_msg)
        if exp_manager:
            exp_manager.logger.write(error_msg)
        return False


def main() -> int:
    """전체 파이프라인을 실행합니다."""

    # ExperimentManager를 사용하여 전체 파이프라인 로그 기록
    with ExperimentManager() as exp:
        title = "전체 데이터 파이프라인 실행"
        separator = "=" * 60

        print(separator)
        print(title)
        print(separator)
        print()

        exp.logger.write(separator)
        exp.logger.write(title)
        exp.logger.write(separator)

        steps = [
            ("collect_arxiv_papers.py", "Phase 1: arXiv 논문 수집"),
            ("setup_database.py", "Phase 2: PostgreSQL 데이터베이스 초기화"),
            ("process_documents.py", "Phase 3: PDF 문서 로드 및 청크 분할"),
            ("load_embeddings.py", "Phase 4: 임베딩 생성 및 Vector DB 저장"),
        ]

        for script, description in steps:
            success = run_command(script, description, exp_manager=exp)
            if not success:
                warning_msg = f"⚠️ {description} 단계에서 실패했습니다.\n다음 단계는 건너뜁니다."
                print(warning_msg)
                exp.logger.write(warning_msg)
                return 1

        complete_msg = "✅ 전체 파이프라인 실행 완료!"
        print(separator)
        print(complete_msg)
        print(separator)

        exp.logger.write(separator)
        exp.logger.write(complete_msg)
        exp.logger.write(separator)

        return 0


if __name__ == "__main__":
    raise SystemExit(main())

