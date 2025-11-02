# ui/components/sidebar.py

"""
사이드바 UI 컴포넌트

Streamlit 사이드바 구성 요소:
- 난이도 선택 (Easy/Hard) - 변경 시 새 채팅 생성
- 새 채팅 버튼
- 채팅 목록 (이전 채팅 기록)
- 설정 정보 표시
"""

# ------------------------- 서드파티 라이브러리 ------------------------- #
import streamlit as st

# ------------------------- 프로젝트 모듈 ------------------------- #
from ui.components.chat_manager import (
    create_new_chat,
    switch_chat,
    delete_chat,
    get_chat_list,
    get_current_difficulty
)


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
        # 현재 채팅이 있으면 그 난이도를 기본값으로
        current_difficulty = get_current_difficulty()
        default_index = 0 if current_difficulty == "easy" else 1 if current_difficulty else 0

        # 난이도 변경 콜백 함수
        def on_difficulty_change():
            """난이도 변경 시 새 채팅 생성"""
            new_difficulty = st.session_state.difficulty_selector

            # 첫 실행이 아니고, 현재 채팅이 있고, 실제로 난이도가 변경된 경우만
            if "difficulty_initialized" in st.session_state and st.session_state.current_chat_id:
                current_chat_difficulty = get_current_difficulty()

                # 현재 채팅의 난이도와 다른 경우만 새 채팅 생성
                if current_chat_difficulty and current_chat_difficulty != new_difficulty:
                    if exp_manager:
                        exp_manager.log_ui_interaction(
                            f"난이도 변경: {current_chat_difficulty} → {new_difficulty} (새 채팅 생성)"
                        )
                    create_new_chat(new_difficulty)

            # 초기화 플래그 설정
            st.session_state.difficulty_initialized = True

        difficulty = st.radio(
            "🎚️ 난이도 선택",
            options=["easy", "hard"],
            format_func=lambda x: "초급 (쉬운 설명)" if x == "easy" else "전문가 (상세 설명)",
            index=default_index,
            help="답변의 난이도를 선택하세요",
            key="difficulty_selector",
            on_change=on_difficulty_change
        )

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

        # -------------- 채팅 목록 -------------- #
        st.subheader("💬 채팅 기록")

        chat_list = get_chat_list()

        if not chat_list:
            st.caption("아직 채팅 기록이 없습니다.")
        else:
            for chat_info in chat_list:
                chat_id = chat_info["id"]
                title = chat_info["title"]
                difficulty_label = "초급" if chat_info["difficulty"] == "easy" else "전문가"
                msg_count = chat_info["message_count"]

                # 현재 활성 채팅 표시
                is_current = (chat_id == st.session_state.current_chat_id)
                prefix = "🔹" if is_current else "⚪"

                # 채팅 컨테이너
                with st.container():
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        # 채팅 선택 버튼
                        if st.button(
                            f"{prefix} {title}",
                            key=f"chat_{chat_id}",
                            use_container_width=True,
                            disabled=is_current
                        ):
                            # 채팅 전환
                            switch_chat(chat_id)

                            if exp_manager:
                                exp_manager.log_ui_interaction(f"채팅 전환: {chat_id}")

                            st.rerun()

                    with col2:
                        # 삭제 버튼 (현재 채팅이 아닌 경우만)
                        if not is_current:
                            if st.button("🗑️", key=f"delete_{chat_id}", help="채팅 삭제"):
                                delete_chat(chat_id)

                                if exp_manager:
                                    exp_manager.log_ui_interaction(f"채팅 삭제: {chat_id}")

                                st.rerun()

                    # 채팅 정보
                    st.caption(f"{difficulty_label} | {msg_count}개 메시지")

        # 구분선 추가
        st.divider()

        # -------------- 시스템 정보 표시 -------------- #
        st.caption("📚 논문 리뷰 챗봇")
        st.caption("🤖 LangGraph + RAG 기반")
        st.caption("💬 OpenAI GPT-4 / Solar-pro")

    # 선택된 난이도 반환
    return difficulty
