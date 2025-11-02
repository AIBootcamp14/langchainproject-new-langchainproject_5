# ui/components/chat_interface.py

"""
채팅 인터페이스 UI 컴포넌트

Streamlit 채팅 UI 구성:
- 채팅 히스토리 표시
- 사용자 입력 처리
- Agent 실행 및 답변 표시
"""

# ------------------------- 서드파티 라이브러리 ------------------------- #
import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler

# ------------------------- 프로젝트 모듈 ------------------------- #
from ui.components.file_download import show_download_success, create_download_button


# ==================== 채팅 히스토리 관리 ==================== #
# ---------------------- 세션 상태 초기화 ---------------------- #
def initialize_chat_history():
    """
    채팅 히스토리 세션 상태 초기화

    session_state.messages 리스트가 없으면 생성
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []              # 빈 메시지 리스트 생성


# ---------------------- 기존 메시지 표시 ---------------------- #
def display_chat_history():
    """
    저장된 채팅 히스토리 표시

    session_state에 저장된 모든 메시지를 렌더링
    """
    # 모든 메시지 순회
    for message in st.session_state.messages:
        role = message["role"]                      # user 또는 assistant
        content = message["content"]                # 메시지 내용

        # 역할별 채팅 버블 표시
        with st.chat_message(role):
            st.markdown(content)

            # -------------- 출처 정보 표시 -------------- #
            # assistant 메시지에 출처가 있으면 expander로 표시
            if role == "assistant" and "sources" in message:
                with st.expander("📚 참고 논문"):
                    for doc in message["sources"]:
                        st.markdown(f"""
                        **제목**: {doc.get('title', 'N/A')}
                        **저자**: {doc.get('authors', 'N/A')}
                        **연도**: {doc.get('year', 'N/A')}
                        """)
                        st.divider()


# ==================== 사용자 입력 처리 ==================== #
# ---------------------- 사용자 메시지 추가 ---------------------- #
def add_user_message(prompt: str):
    """
    사용자 메시지를 히스토리에 추가하고 표시

    Args:
        prompt: 사용자 입력 텍스트
    """
    # 세션 상태에 메시지 추가
    st.session_state.messages.append({
        "role": "user",                             # 사용자 메시지
        "content": prompt                           # 질문 내용
    })

    # 채팅 버블로 표시
    with st.chat_message("user"):
        st.markdown(prompt)


# ---------------------- Agent 응답 처리 ---------------------- #
def handle_agent_response(agent_executor, prompt: str, difficulty: str, exp_manager=None):
    """
    Agent를 실행하고 응답을 처리

    Args:
        agent_executor: Agent 실행기
        prompt: 사용자 질문
        difficulty: 난이도 (easy/hard)
        exp_manager: ExperimentManager 인스턴스 (선택)

    Returns:
        dict: Agent 응답 결과
    """
    # Assistant 채팅 버블 표시
    with st.chat_message("assistant"):
        # 메시지 플레이스홀더 생성
        message_placeholder = st.empty()

        # -------------- StreamlitCallbackHandler 생성 -------------- #
        # Agent 실행 과정을 실시간으로 표시
        st_callback = StreamlitCallbackHandler(
            parent_container=st.container(),
            expand_new_thoughts=True,               # 새 단계 자동 펼치기
            collapse_completed_thoughts=True        # 완료 단계 자동 접기
        )

        try:
            # -------------- Agent 실행 -------------- #
            with st.spinner("🤖 답변 생성 중..."):
                response = agent_executor.invoke(
                    {
                        "question": prompt,
                        "difficulty": difficulty,
                        "messages": []          # 대화 메모리 (필요시)
                    },
                    config={"callbacks": [st_callback]}
                )

            # -------------- 답변 표시 -------------- #
            answer = response.get("final_answer", "답변을 생성할 수 없습니다.")
            message_placeholder.markdown(answer)

            # -------------- 출처 정보 표시 -------------- #
            sources = []
            if "source_documents" in response:
                with st.expander("📚 참고 논문"):
                    for doc in response["source_documents"]:
                        metadata = doc.metadata
                        st.markdown(f"""
                        **제목**: {metadata.get('title', 'N/A')}
                        **저자**: {metadata.get('authors', 'N/A')}
                        **연도**: {metadata.get('year', 'N/A')}
                        """)
                        st.divider()

                        # 출처 정보 저장
                        sources.append(metadata)

            # -------------- 파일 저장 도구 실행 시 다운로드 버튼 -------------- #
            if response.get("tool_choice") == "save_file":
                st.divider()
                show_download_success()
                create_download_button(
                    content=answer,
                    filename=f"paper_response_{response.get('timestamp', 'unknown')}.txt"
                )

            # -------------- 메시지 히스토리에 추가 -------------- #
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources if sources else None
            })

            return response

        except Exception as e:
            # -------------- 에러 처리 -------------- #
            error_msg = f"❌ 오류 발생: {str(e)}"
            st.error(error_msg)

            # 로그 기록 (ExperimentManager 사용 시)
            if exp_manager:
                exp_manager.logger.write(f"UI 에러: {e}", print_error=True)

            return None


# ==================== 채팅 입력 처리 ==================== #
# ---------------------- 채팅 입력 UI ---------------------- #
def render_chat_input(agent_executor, difficulty: str, exp_manager=None):
    """
    채팅 입력 UI 렌더링 및 처리

    Args:
        agent_executor: Agent 실행기
        difficulty: 난이도
        exp_manager: ExperimentManager 인스턴스 (선택)
    """
    # 채팅 입력창 표시
    if prompt := st.chat_input("논문에 대해 질문해보세요..."):
        # 사용자 메시지 추가
        add_user_message(prompt)

        # Agent 응답 처리
        handle_agent_response(
            agent_executor=agent_executor,
            prompt=prompt,
            difficulty=difficulty,
            exp_manager=exp_manager
        )
