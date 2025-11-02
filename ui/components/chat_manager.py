# ui/components/chat_manager.py

"""
채팅 세션 관리 컴포넌트

다중 채팅 세션 지원:
- 채팅 생성/삭제
- 채팅 목록 표시
- 채팅 전환
- 난이도별 채팅 관리
"""

# ------------------------- 표준 라이브러리 ------------------------- #
from datetime import datetime
from typing import Dict, List, Optional
import uuid

# ------------------------- 서드파티 라이브러리 ------------------------- #
import streamlit as st


# ==================== 채팅 세션 관리 ==================== #
# ---------------------- 세션 상태 초기화 ---------------------- #
def initialize_chat_sessions():
    """
    채팅 세션 관리를 위한 세션 상태 초기화

    세션 상태 구조:
    - chats: 모든 채팅 세션 딕셔너리
    - current_chat_id: 현재 활성 채팅 ID
    - last_difficulty: 마지막으로 선택한 난이도
    """
    # 채팅 세션 딕셔너리 초기화
    if "chats" not in st.session_state:
        st.session_state.chats = {}

    # 현재 활성 채팅 ID 초기화
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None

    # 마지막 난이도 추적
    if "last_difficulty" not in st.session_state:
        st.session_state.last_difficulty = None


# ---------------------- 새 채팅 생성 ---------------------- #
def create_new_chat(difficulty: str) -> str:
    """
    새 채팅 세션 생성

    Args:
        difficulty: 난이도 (easy 또는 hard)

    Returns:
        str: 생성된 채팅 ID
    """
    # 고유 채팅 ID 생성
    chat_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 채팅 세션 데이터 생성
    st.session_state.chats[chat_id] = {
        "messages": [],                     # 메시지 리스트
        "difficulty": difficulty,           # 난이도
        "created_at": timestamp,            # 생성 시간
        "title": "새 채팅"                  # 기본 제목
    }

    # 현재 채팅으로 설정
    st.session_state.current_chat_id = chat_id
    st.session_state.last_difficulty = difficulty

    return chat_id


# ---------------------- 채팅 제목 업데이트 ---------------------- #
def update_chat_title(chat_id: str, first_message: str):
    """
    첫 번째 메시지로 채팅 제목 업데이트

    Args:
        chat_id: 채팅 ID
        first_message: 첫 번째 사용자 메시지
    """
    if chat_id in st.session_state.chats:
        # 제목 생성 (최대 50자)
        title = first_message.strip()

        # 50자로 제한하되, 단어 중간에서 자르지 않도록
        if len(title) > 50:
            title = title[:50]
            # 마지막 공백에서 자르기
            last_space = title.rfind(' ')
            if last_space > 30:  # 최소 30자는 유지
                title = title[:last_space]
            title += "..."

        st.session_state.chats[chat_id]["title"] = title


# ---------------------- 채팅 전환 ---------------------- #
def switch_chat(chat_id: str):
    """
    다른 채팅 세션으로 전환

    Args:
        chat_id: 전환할 채팅 ID
    """
    if chat_id in st.session_state.chats:
        st.session_state.current_chat_id = chat_id
        # 해당 채팅의 난이도로 업데이트
        st.session_state.last_difficulty = st.session_state.chats[chat_id]["difficulty"]


# ---------------------- 채팅 삭제 ---------------------- #
def delete_chat(chat_id: str):
    """
    채팅 세션 삭제

    Args:
        chat_id: 삭제할 채팅 ID
    """
    if chat_id in st.session_state.chats:
        del st.session_state.chats[chat_id]

        # 현재 채팅이 삭제된 경우
        if st.session_state.current_chat_id == chat_id:
            # 다른 채팅이 있으면 전환
            if st.session_state.chats:
                st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
            else:
                st.session_state.current_chat_id = None


# ---------------------- 현재 채팅 메시지 가져오기 ---------------------- #
def get_current_messages() -> List[Dict]:
    """
    현재 활성 채팅의 메시지 리스트 반환

    Returns:
        List[Dict]: 메시지 리스트
    """
    chat_id = st.session_state.current_chat_id

    if chat_id and chat_id in st.session_state.chats:
        return st.session_state.chats[chat_id]["messages"]

    return []


# ---------------------- 현재 채팅 난이도 가져오기 ---------------------- #
def get_current_difficulty() -> Optional[str]:
    """
    현재 활성 채팅의 난이도 반환

    Returns:
        Optional[str]: 난이도 (easy 또는 hard)
    """
    chat_id = st.session_state.current_chat_id

    if chat_id and chat_id in st.session_state.chats:
        return st.session_state.chats[chat_id]["difficulty"]

    return None


# ---------------------- 메시지 추가 ---------------------- #
def add_message_to_current_chat(role: str, content: str, **kwargs):
    """
    현재 채팅에 메시지 추가

    Args:
        role: 메시지 역할 (user 또는 assistant)
        content: 메시지 내용
        **kwargs: 추가 메타데이터 (tool_choice, sources 등)
    """
    chat_id = st.session_state.current_chat_id

    if chat_id and chat_id in st.session_state.chats:
        message = {
            "role": role,
            "content": content,
            **kwargs
        }

        st.session_state.chats[chat_id]["messages"].append(message)

        # 첫 번째 사용자 메시지면 제목 업데이트
        if role == "user" and len(st.session_state.chats[chat_id]["messages"]) == 1:
            update_chat_title(chat_id, content)


# ---------------------- 채팅 목록 가져오기 ---------------------- #
def get_chat_list() -> List[Dict]:
    """
    모든 채팅 세션 목록 반환 (최신순)

    Returns:
        List[Dict]: 채팅 정보 리스트
    """
    chat_list = []

    for chat_id, chat_data in st.session_state.chats.items():
        chat_list.append({
            "id": chat_id,
            "title": chat_data["title"],
            "difficulty": chat_data["difficulty"],
            "created_at": chat_data["created_at"],
            "message_count": len(chat_data["messages"])
        })

    # 생성 시간 역순으로 정렬
    chat_list.sort(key=lambda x: x["created_at"], reverse=True)

    return chat_list


# ---------------------- 특정 채팅 내역 내보내기 ---------------------- #
def export_chat(chat_id: str) -> str:
    """
    특정 채팅의 전체 대화 내역을 마크다운 형식으로 변환

    Args:
        chat_id: 채팅 ID

    Returns:
        str: 대화 내역 마크다운 텍스트
    """
    if not chat_id or chat_id not in st.session_state.chats:
        return ""

    chat_data = st.session_state.chats[chat_id]
    messages = chat_data["messages"]

    # 마크다운 헤더 정보
    export_text = f"""# 채팅 기록

**제목**: {chat_data['title']}
**난이도**: {chat_data['difficulty']}
**생성 시간**: {chat_data['created_at']}
**메시지 수**: {len(messages)}

---

"""

    # 모든 메시지 추가
    for i, msg in enumerate(messages, 1):
        role = "🙋 사용자" if msg["role"] == "user" else "🤖 AI"
        export_text += f"## [{i}] {role}\n\n{msg['content']}\n\n"

        # 도구 정보 추가
        if msg["role"] == "assistant" and "tool_choice" in msg:
            tool_labels = {
                "general": "🗣️ 일반 답변",
                "search_paper": "📚 RAG 논문 검색",
                "web_search": "🌐 웹 검색",
                "glossary": "📖 RAG 용어집",
                "summarize": "📄 논문 요약",
                "save_file": "💾 파일 저장"
            }
            tool_label = tool_labels.get(msg["tool_choice"], msg["tool_choice"])
            export_text += f"*사용된 도구: {tool_label}*\n\n"

        export_text += "---\n\n"

    return export_text


# ---------------------- 현재 채팅 내역 내보내기 ---------------------- #
def export_current_chat() -> str:
    """
    현재 채팅의 전체 대화 내역을 마크다운 형식으로 변환

    Returns:
        str: 대화 내역 마크다운 텍스트
    """
    chat_id = st.session_state.current_chat_id
    return export_chat(chat_id)
