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

# ------------------------- 서드파티 라이브러리 ------------------------- #
import streamlit as st

# ------------------------- 프로젝트 모듈 ------------------------- #
# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.graph import create_agent_graph
from src.utils.experiment_manager import ExperimentManager
from ui.components.sidebar import render_sidebar
from ui.components.chat_interface import (
    initialize_chat_history,
    display_chat_history,
    render_chat_input
)


# ==================== 페이지 설정 ==================== #
st.set_page_config(
    page_title="논문 리뷰 챗봇",                # 브라우저 탭 제목
    page_icon="📚",                             # 파비콘
    layout="wide",                              # 와이드 레이아웃
    initial_sidebar_state="expanded"            # 사이드바 초기 상태
)


# ==================== 메인 헤더 ==================== #
st.title("📚 논문 리뷰 챗봇 (AI Agent + RAG)")
st.caption("🤖 LangGraph + RAG 기반 논문 검색 및 질문 답변")
st.divider()


# ==================== 환경 변수 확인 ==================== #
# ---------------------- API 키 검증 ---------------------- #
# OpenAI API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
    st.info("💡 .env 파일에 API 키를 추가하거나 환경 변수를 설정해주세요.")
    st.stop()                                   # 앱 실행 중지

# DATABASE_URL 확인
if not os.getenv("DATABASE_URL"):
    st.warning("⚠️ DATABASE_URL이 설정되지 않았습니다. RAG 기능이 제한될 수 있습니다.")


# ==================== Agent 및 ExperimentManager 초기화 ==================== #
# ---------------------- 세션 상태 초기화 ---------------------- #
@st.cache_resource
def initialize_agent():
    """
    Agent 및 ExperimentManager 초기화 (캐싱)

    Returns:
        tuple: (agent_executor, exp_manager)
    """
    try:
        # ExperimentManager 생성
        exp_manager = ExperimentManager()

        # Agent 그래프 생성
        agent_executor = create_agent_graph()

        exp_manager.logger.write("Streamlit UI 시작")
        exp_manager.logger.write(f"세션 폴더: {exp_manager.session_dir}")

        return agent_executor, exp_manager

    except Exception as e:
        st.error(f"❌ 초기화 실패: {str(e)}")
        st.stop()


# Agent 및 ExperimentManager 로드
agent_executor, exp_manager = initialize_agent()


# ==================== 사이드바 렌더링 ==================== #
# 난이도 선택 및 설정
difficulty = render_sidebar()


# ==================== 채팅 인터페이스 ==================== #
# ---------------------- 채팅 히스토리 초기화 ---------------------- #
initialize_chat_history()

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
st.caption("Powered by LangChain, LangGraph, OpenAI GPT-4, PostgreSQL + pgvector")
