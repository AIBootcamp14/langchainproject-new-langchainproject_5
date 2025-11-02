# ui/components/file_download.py

"""
파일 다운로드 UI 컴포넌트

답변 내용을 텍스트 파일로 다운로드할 수 있는 버튼 제공
"""

# ------------------------- 표준 라이브러리 ------------------------- #
from datetime import datetime

# ------------------------- 서드파티 라이브러리 ------------------------- #
import streamlit as st


# ==================== 파일 다운로드 함수 ==================== #
# ---------------------- 다운로드 버튼 생성 ---------------------- #
def create_download_button(content: str, filename: str = None):
    """
    파일 다운로드 버튼 생성

    Args:
        content: 다운로드할 파일 내용
        filename: 파일명 (None이면 자동 생성)
    """
    # -------------- 파일명 자동 생성 -------------- #
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")   # 현재 시각
        filename = f"paper_response_{timestamp}.txt"           # 기본 파일명

    # -------------- 다운로드 버튼 표시 -------------- #
    st.download_button(
        label="⬇️ 파일 다운로드",
        data=content,                               # 파일 내용
        file_name=filename,                         # 파일명
        mime="text/plain",                          # MIME 타입
        use_container_width=True                    # 버튼 너비 전체 사용
    )


# ---------------------- 파일 저장 성공 메시지 ---------------------- #
def show_download_success():
    """
    파일 다운로드 준비 완료 메시지 표시
    """
    st.success("✅ 파일이 준비되었습니다!")
    st.info("💡 아래 버튼을 클릭하여 파일을 다운로드하세요.")


# ---------------------- 다운로드 옵션 선택 ---------------------- #
def render_download_options(content: str, metadata: dict = None):
    """
    다운로드 옵션 UI 렌더링

    Args:
        content: 다운로드할 내용
        metadata: 메타데이터 (제목, 날짜 등)
    """
    with st.expander("📁 다운로드 옵션", expanded=True):
        # -------------- 파일명 입력 -------------- #
        custom_filename = st.text_input(
            "파일명",
            value="paper_response",
            help="확장자 없이 파일명만 입력하세요"
        )

        # -------------- 파일 형식 선택 -------------- #
        file_format = st.selectbox(
            "파일 형식",
            options=["txt", "md"],
            format_func=lambda x: "텍스트 (.txt)" if x == "txt" else "마크다운 (.md)"
        )

        # -------------- 메타데이터 포함 여부 -------------- #
        include_metadata = st.checkbox(
            "메타데이터 포함",
            value=True,
            help="날짜, 난이도 등의 정보를 파일에 포함"
        )

        st.divider()

        # -------------- 파일 내용 구성 -------------- #
        # 메타데이터 헤더 추가
        if include_metadata and metadata:
            header = f"""# 논문 리뷰 챗봇 답변
생성 일시: {metadata.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
난이도: {metadata.get('difficulty', 'N/A')}
질문: {metadata.get('question', 'N/A')}

---

"""
            final_content = header + content
        else:
            final_content = content

        # 최종 파일명 생성
        final_filename = f"{custom_filename}.{file_format}"

        # 다운로드 버튼 표시
        create_download_button(final_content, final_filename)
