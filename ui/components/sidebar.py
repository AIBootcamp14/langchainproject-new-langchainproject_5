# ui/components/sidebar.py

"""
사이드바 UI 컴포넌트

Streamlit 사이드바 구성 요소:
- 난이도 선택 (Easy/Hard)
- 대화 초기화 버튼
- 설정 정보 표시
"""

# ------------------------- 서드파티 라이브러리 ------------------------- #
import streamlit as st


# ==================== 사이드바 렌더링 함수 ==================== #
# ---------------------- 난이도 선택 사이드바 ---------------------- #
def render_sidebar(exp_manager=None):
    """
    사이드바 UI 렌더링

    Args:
        exp_manager: ExperimentManager 인스턴스 (선택)

    Returns:
        str: 선택된 난이도 (easy 또는 hard)
    """
    with st.sidebar:
        # 헤더 표시
        st.header("⚙️ 설정")

        # -------------- 난이도 선택 라디오 버튼 -------------- #
        difficulty = st.radio(
            "🎚️ 난이도 선택",
            options=["easy", "hard"],
            format_func=lambda x: "초급 (쉬운 설명)" if x == "easy" else "전문가 (상세 설명)",
            index=0,                                    # 기본값: easy
            help="답변의 난이도를 선택하세요"
        )

        # -------------- 난이도 변경 로그 기록 -------------- #
        # 세션 상태에 이전 난이도 저장 및 변경 감지
        if "previous_difficulty" not in st.session_state:
            st.session_state.previous_difficulty = difficulty
            # 첫 실행 시 로깅
            if exp_manager:
                exp_manager.log_ui_interaction(f"초기 난이도 설정: {difficulty}")
                exp_manager.update_metadata(difficulty=difficulty)
        elif st.session_state.previous_difficulty != difficulty:
            # 난이도 변경 감지
            if exp_manager:
                exp_manager.log_ui_interaction(
                    f"난이도 변경: {st.session_state.previous_difficulty} → {difficulty}"
                )
                exp_manager.update_metadata(difficulty=difficulty)
            st.session_state.previous_difficulty = difficulty

        # 구분선 추가
        st.divider()

        # -------------- 난이도별 설명 정보 박스 -------------- #
        st.info("""
        **초급 모드**:
        - 쉬운 용어 사용
        - 비유와 예시 활용
        - 수식 최소화

        **전문가 모드**:
        - 전문 용어 사용
        - 수식 및 알고리즘 상세 설명
        - 기술적 세부사항 포함
        """)

        # 구분선 추가
        st.divider()

        # -------------- 대화 초기화 버튼 -------------- #
        if st.button("🔄 대화 초기화", use_container_width=True):
            # 세션 상태의 메시지 히스토리 초기화
            st.session_state.messages = []              # 메시지 리스트 비우기
            st.rerun()                                  # UI 새로고침

        # 구분선 추가
        st.divider()

        # -------------- 시스템 정보 표시 -------------- #
        st.caption("📚 논문 리뷰 챗봇")
        st.caption("🤖 LangGraph + RAG 기반")
        st.caption("💬 OpenAI GPT-4 / Solar-pro")

    # 선택된 난이도 반환
    return difficulty
