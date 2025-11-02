# main.py
"""
Streamlit UI 실행 파일

python main.py 실행 시 Streamlit UI가 자동으로 실행됩니다:
- Streamlit 웹 서버 시작
- ui/app.py 실행
- 논문 리뷰 챗봇 UI 제공
"""

# ==================== Import ==================== #
import os
import sys
import subprocess
from dotenv import load_dotenv

# ==================== 환경변수 로드 ==================== #
load_dotenv()  # .env 파일 로드


# ==================== Streamlit 실행 함수 ==================== #
def main():
    """
    Streamlit UI 실행 함수

    Streamlit 웹 서버를 시작하여 ui/app.py 실행
    """
    print("="*80)
    print("📚 논문 리뷰 챗봇 시작")
    print("="*80)
    print()
    print("🚀 Streamlit UI 서버를 시작합니다...")
    print()
    print("💡 브라우저에서 자동으로 열립니다.")
    print("💡 종료하려면 Ctrl+C를 누르세요.")
    print()
    print("="*80)

    # -------------- Streamlit 실행 -------------- #
    # ui/app.py 경로 확인
    ui_path = os.path.join(os.path.dirname(__file__), "ui", "app.py")

    if not os.path.exists(ui_path):
        print(f"❌ UI 파일을 찾을 수 없습니다: {ui_path}")
        sys.exit(1)

    # Streamlit 서버 시작
    try:
        subprocess.run([
            "streamlit", "run", ui_path,
            "--server.port", "8501",                # 포트 번호
            "--server.headless", "false",           # 브라우저 자동 열기
            "--theme.base", "light"                 # 라이트 테마
        ])
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("👋 Streamlit UI 서버를 종료합니다.")
        print("="*80)
    except FileNotFoundError:
        print("❌ Streamlit이 설치되지 않았습니다.")
        print("💡 다음 명령어로 설치하세요: pip install streamlit")
        sys.exit(1)


# ==================== 실행 ==================== #
if __name__ == "__main__":
    main()
