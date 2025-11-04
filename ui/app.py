# ui/app.py

"""
Streamlit 메인 UI

논문 리뷰 챗봇 웹 인터페이스:
- 사이드바 (난이도 선택)
- 채팅 인터페이스
- AI Agent 통합
"""

# ------------------------- 표준 라이브러리 ------------------------- #
import os
import sys
import atexit
from pathlib import Path

# ------------------------- 서드파티 라이브러리 ------------------------- #
import streamlit as st

# ------------------------- 프로젝트 모듈 ------------------------- #
# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.graph import create_agent_graph
from src.utils.experiment_manager import ExperimentManager
from ui.components.sidebar import render_sidebar
from ui.components.chat_interface import (
    display_chat_history,
    render_chat_input,
    render_chat_export_buttons
)
from ui.components.chat_manager import (
    initialize_chat_sessions,
    create_new_chat,
    get_current_difficulty
)
from ui.components.storage import initialize_storage


# ==================== 페이지 설정 ==================== #
st.set_page_config(
    page_title="논문 리뷰 챗봇",                # 브라우저 탭 제목
    page_icon="📚",                             # 파비콘
    layout="wide",                              # 와이드 레이아웃
    initial_sidebar_state="expanded"            # 사이드바 초기 상태
)


# ==================== 환경 변수 확인 (앱 시작 전) ==================== #
# ---------------------- API 키 검증 ---------------------- #
# OpenAI API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
    st.info("💡 .env 파일에 API 키를 추가하거나 환경 변수를 설정해주세요.")
    st.stop()                                   # 앱 실행 중지

# PostgreSQL 설정 확인
postgres_config_ok = all([
    os.getenv("POSTGRES_USER"),
    os.getenv("POSTGRES_PASSWORD"),
    os.getenv("POSTGRES_HOST"),
    os.getenv("POSTGRES_DB")
])

if not postgres_config_ok:
    st.warning("⚠️ PostgreSQL 설정이 완전하지 않습니다. RAG 기능이 제한될 수 있습니다.")
    st.info("💡 .env 파일에서 POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB를 확인해주세요.")


# ==================== Agent 및 ExperimentManager 초기화 ==================== #
# ---------------------- 세션 상태 초기화 ---------------------- #
@st.cache_resource
def initialize_agent(_today: str):
    """
    Agent 및 ExperimentManager 초기화 (캐싱)

    Args:
        _today: 날짜 (YYYYMMDD) - 캐시 키로 사용 (날짜 변경 시 새로 초기화)

    Returns:
        tuple: (agent_executor, exp_manager)
    """
    try:
        # ExperimentManager 생성
        exp_manager = ExperimentManager()

        # Agent 그래프 생성
        agent_executor = create_agent_graph(exp_manager=exp_manager)

        exp_manager.logger.write("Streamlit UI 시작")
        exp_manager.logger.write(f"실험 폴더: {exp_manager.experiment_dir}")

        return agent_executor, exp_manager

    except Exception as e:
        st.error(f"❌ 초기화 실패: {str(e)}")
        st.stop()


# Agent 및 ExperimentManager 로드 (날짜를 캐시 키에 포함)
from datetime import datetime
today = datetime.now().strftime("%Y%m%d")
agent_executor, exp_manager = initialize_agent(today)

# Storage 초기화
initialize_storage()


# ==================== 앱 종료 시 빈 폴더 정리 ==================== #
def cleanup_on_exit():
    """
    Streamlit 앱 종료 시 빈 폴더 정리

    오늘 날짜의 experiments 폴더에서 빈 폴더를 모두 정리합니다.
    """
    try:
        from datetime import datetime
        from pathlib import Path

        today = datetime.now().strftime("%Y%m%d")
        date_dir = Path(f"experiments/{today}")

        if not date_dir.exists():
            return

        deleted_count = 0

        # 날짜 폴더 전체의 빈 폴더 찾기 (하위 폴더부터 상위 폴더 순으로)
        for folder in sorted(date_dir.rglob("*"), key=lambda p: -len(p.parts)):
            if folder.is_dir() and not any(folder.iterdir()):
                try:
                    folder.rmdir()
                    deleted_count += 1
                except Exception:
                    pass

        if deleted_count > 0:
            print(f"🧹 앱 종료: {deleted_count}개의 빈 폴더 정리 완료")

    except Exception as e:
        print(f"⚠️ 빈 폴더 정리 중 오류: {e}")


# atexit에 cleanup 함수 등록
atexit.register(cleanup_on_exit)


# ==================== 메인 헤더 ==================== #
st.title("📚 논문 리뷰 챗봇 (AI Agent + RAG)")
st.caption("🤖 LangGraph + RAG 기반 논문 검색 및 질문 답변")
st.divider()


# ==================== 채팅 세션 관리 초기화 ==================== #
initialize_chat_sessions()

# 첫 실행 시 또는 채팅이 없으면 자동으로 새 채팅 생성
if not st.session_state.current_chat_id:
    create_new_chat(difficulty="easy")
    exp_manager.log_ui_interaction("첫 실행: 새 채팅 자동 생성 (난이도: easy)")


# ==================== 사이드바 렌더링 ==================== #
# 난이도 선택 및 설정
difficulty = render_sidebar(exp_manager=exp_manager)

# 현재 채팅의 난이도 가져오기 (사이드바에서 난이도가 변경되지 않았다면)
current_difficulty = get_current_difficulty()
if current_difficulty:
    difficulty = current_difficulty


# ==================== 채팅 인터페이스 ==================== #
# ---------------------- 기존 메시지 표시 ---------------------- #
display_chat_history()

# ---------------------- 사용자 입력 처리 ---------------------- #
render_chat_input(
    agent_executor=agent_executor,
    difficulty=difficulty,
    exp_manager=exp_manager
)


# ==================== 푸터 ==================== #
st.divider()
st.caption("Made with ❤️ by 연결의 민족 팀")
st.caption("Powered by LangChain, LangGraph, OpenAI GPT-5, PostgreSQL + pgvector")

# 전체 대화 복사/저장 버튼
render_chat_export_buttons()
