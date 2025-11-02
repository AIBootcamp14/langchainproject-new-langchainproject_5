# ui/components/sidebar.py

"""
사이드바 UI 컴포넌트

Streamlit 사이드바 구성 요소:
- 난이도 설명 및 선택 (Easy/Hard)
- 새 채팅 버튼 - 선택된 난이도로 채팅 생성
- 채팅 목록 (ChatGPT 스타일)
- 설정 정보 표시
"""

# ------------------------- 표준 라이브러리 ------------------------- #
from datetime import datetime, timedelta

# ------------------------- 서드파티 라이브러리 ------------------------- #
import streamlit as st

# ------------------------- 프로젝트 모듈 ------------------------- #
from ui.components.chat_manager import (
    create_new_chat,
    switch_chat,
    delete_chat,
    get_chat_list,
    get_current_difficulty,
    export_chat
)


# ==================== 사이드바 렌더링 함수 ==================== #
# ---------------------- 날짜별 그룹화 ---------------------- #
def group_chats_by_date(chat_list):
    """
    채팅 목록을 날짜별로 그룹화 (ChatGPT 스타일)

    Returns:
        dict: {"오늘": [...], "어제": [...], "지난 7일": [...], "그 이전": [...]}
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    week_ago = today_start - timedelta(days=7)

    groups = {
        "오늘": [],
        "어제": [],
        "지난 7일": [],
        "그 이전": []
    }

    for chat in chat_list:
        # 문자열을 datetime으로 변환
        created_at = datetime.strptime(chat["created_at"], "%Y-%m-%d %H:%M:%S")

        if created_at >= today_start:
            groups["오늘"].append(chat)
        elif created_at >= yesterday_start:
            groups["어제"].append(chat)
        elif created_at >= week_ago:
            groups["지난 7일"].append(chat)
        else:
            groups["그 이전"].append(chat)

    # 빈 그룹 제거
    return {k: v for k, v in groups.items() if v}


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
        # -------------- 난이도 설정 섹션 -------------- #
        st.markdown("### ⚙️ 설정")

        # 난이도 설명 (위쪽에 배치)
        with st.expander("ℹ️ 난이도 설명", expanded=False):
            st.markdown("""
            **🟢 초급 모드**:
            - 쉬운 용어 사용
            - 비유와 예시 활용
            - 수식 최소화

            **🔴 전문가 모드**:
            - 전문 용어 사용
            - 수식 및 알고리즘 상세 설명
            - 기술적 세부사항 포함
            """)

        # 현재 채팅이 있으면 그 난이도를 기본값으로
        current_difficulty = get_current_difficulty()
        default_index = 0 if current_difficulty == "easy" else 1 if current_difficulty else 0

        # 난이도 선택 라디오 버튼 (콜백 제거)
        difficulty = st.radio(
            "난이도 선택",
            options=["easy", "hard"],
            format_func=lambda x: "🟢 초급" if x == "easy" else "🔴 전문가",
            index=default_index,
            help="답변의 난이도를 선택하세요",
            key="difficulty_selector",
            horizontal=True
        )

        # 새 채팅 버튼
        if st.button("➕ 새 채팅", use_container_width=True, type="primary"):
            selected_difficulty = st.session_state.difficulty_selector
            create_new_chat(selected_difficulty)

            if exp_manager:
                exp_manager.log_ui_interaction(f"새 채팅 생성: 난이도={selected_difficulty}")

            st.rerun()

        # 구분선 추가
        st.divider()

        # -------------- 채팅 목록 -------------- #
        st.markdown("### 💬 채팅 기록")

        chat_list = get_chat_list()

        if not chat_list:
            st.caption("📝 채팅 기록이 없습니다.")
            st.caption("아래에서 질문을 시작하세요!")
        else:
            # 날짜별 그룹화
            grouped_chats = group_chats_by_date(chat_list)

            # 각 그룹별로 표시
            for group_name, chats in grouped_chats.items():
                # 그룹 헤더
                st.markdown(f"**{group_name}**")

                for chat_info in chats:
                    chat_id = chat_info["id"]
                    title = chat_info["title"]
                    difficulty_icon = "🟢" if chat_info["difficulty"] == "easy" else "🔴"

                    # 현재 활성 채팅 표시
                    is_current = (chat_id == st.session_state.current_chat_id)

                    # 채팅 컨테이너 (현재 채팅은 배경색 표시)
                    if is_current:
                        # 현재 채팅 - 다른 스타일
                        st.markdown(
                            f"""
                            <div style="
                                background-color: rgba(255, 75, 75, 0.1);
                                padding: 8px;
                                border-radius: 6px;
                                margin-bottom: 4px;
                                border-left: 3px solid #FF4B4B;
                            ">
                                {difficulty_icon} {title}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        # 일반 채팅 - 버튼으로 표시
                        col1, col2, col3 = st.columns([5, 1, 1])

                        with col1:
                            if st.button(
                                f"{difficulty_icon} {title}",
                                key=f"chat_{chat_id}",
                                use_container_width=True
                            ):
                                # 채팅 전환
                                switch_chat(chat_id)

                                if exp_manager:
                                    exp_manager.log_ui_interaction(f"채팅 전환: {chat_id}")

                                st.rerun()

                        with col2:
                            # 저장 버튼
                            chat_content = export_chat(chat_id)
                            if chat_content:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"chat_{title[:20]}_{timestamp}.md"

                                st.download_button(
                                    label="💾",
                                    data=chat_content,
                                    file_name=filename,
                                    mime="text/markdown",
                                    key=f"save_{chat_id}",
                                    help="저장"
                                )

                        with col3:
                            # 삭제 버튼
                            if st.button("🗑️", key=f"delete_{chat_id}", help="삭제"):
                                delete_chat(chat_id)

                                if exp_manager:
                                    exp_manager.log_ui_interaction(f"채팅 삭제: {chat_id}")

                                st.rerun()

                # 그룹 구분선
                st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)

        # 구분선 추가
        st.divider()

        # -------------- 시스템 정보 표시 -------------- #
        st.caption("📚 논문 리뷰 챗봇")
        st.caption("🤖 LangGraph + RAG 기반")
        st.caption("💬 OpenAI GPT-5 / Solar-pro2")

    # 선택된 난이도 반환
    return difficulty
