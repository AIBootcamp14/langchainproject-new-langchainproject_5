# ui/components/storage.py

"""
LocalStorage 기반 데이터 영속성 관리

브라우저 LocalStorage를 사용하여 채팅 기록을 영구 저장:
- 페이지 새로고침 시에도 채팅 기록 유지
- JSON 형식으로 직렬화
- 자동 저장/로드
"""

# ------------------------- 표준 라이브러리 ------------------------- #
import json
from typing import Dict, Optional

# ------------------------- 서드파티 라이브러리 ------------------------- #
import streamlit as st
import streamlit.components.v1 as components


# ==================== LocalStorage 관리 ==================== #
# ---------------------- 채팅 데이터 저장 ---------------------- #
def save_chats_to_local_storage():
    """
    현재 채팅 데이터를 LocalStorage에 저장

    st.session_state.chats를 JSON으로 직렬화하여 브라우저에 저장
    """
    if "chats" not in st.session_state:
        return

    # 채팅 데이터 직렬화
    chats_json = json.dumps(st.session_state.chats)
    current_chat_id = st.session_state.get("current_chat_id", "")
    last_difficulty = st.session_state.get("last_difficulty", "easy")

    # JavaScript로 LocalStorage에 저장
    save_script = f"""
    <script>
    (function() {{
        try {{
            localStorage.setItem('langchain_chats', {json.dumps(chats_json)});
            localStorage.setItem('langchain_current_chat_id', '{current_chat_id}');
            localStorage.setItem('langchain_last_difficulty', '{last_difficulty}');
            console.log('채팅 데이터 LocalStorage 저장 완료');
        }} catch(e) {{
            console.error('LocalStorage 저장 실패:', e);
        }}
    }})();
    </script>
    """

    components.html(save_script, height=0)


# ---------------------- 채팅 데이터 로드 ---------------------- #
def load_chats_from_local_storage() -> Optional[Dict]:
    """
    LocalStorage에서 채팅 데이터 로드

    Returns:
        Optional[Dict]: 로드된 채팅 데이터 또는 None
    """
    # JavaScript로 LocalStorage 읽기
    load_script = """
    <script>
    (function() {
        try {
            const chats = localStorage.getItem('langchain_chats');
            const currentChatId = localStorage.getItem('langchain_current_chat_id');
            const lastDifficulty = localStorage.getItem('langchain_last_difficulty');

            if (chats) {
                // Streamlit으로 데이터 전송
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: {
                        chats: chats,
                        current_chat_id: currentChatId,
                        last_difficulty: lastDifficulty
                    }
                }, '*');
                console.log('채팅 데이터 LocalStorage 로드 완료');
            } else {
                console.log('LocalStorage에 저장된 채팅 없음');
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: null
                }, '*');
            }
        } catch(e) {
            console.error('LocalStorage 로드 실패:', e);
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: null
            }, '*');
        }
    })();
    </script>
    """

    # Streamlit component로 JavaScript 실행
    result = components.html(load_script, height=0)

    if result:
        try:
            chats_data = json.loads(result['chats'])
            return {
                'chats': chats_data,
                'current_chat_id': result.get('current_chat_id'),
                'last_difficulty': result.get('last_difficulty', 'easy')
            }
        except Exception as e:
            st.warning(f"채팅 데이터 로드 중 오류 발생: {e}")
            return None

    return None


# ---------------------- LocalStorage 초기화 ---------------------- #
def initialize_storage():
    """
    Storage 시스템 초기화

    페이지 로드 시 LocalStorage에서 데이터 복원
    """
    if "storage_initialized" not in st.session_state:
        # 자동 저장 플래그 초기화
        st.session_state.storage_initialized = True
        st.session_state.auto_save_enabled = True


# ---------------------- 자동 저장 활성화/비활성화 ---------------------- #
def toggle_auto_save(enabled: bool):
    """
    자동 저장 기능 활성화/비활성화

    Args:
        enabled: True면 활성화, False면 비활성화
    """
    st.session_state.auto_save_enabled = enabled


# ---------------------- LocalStorage 클리어 ---------------------- #
def clear_local_storage():
    """
    LocalStorage의 모든 채팅 데이터 삭제
    """
    clear_script = """
    <script>
    (function() {
        try {
            localStorage.removeItem('langchain_chats');
            localStorage.removeItem('langchain_current_chat_id');
            localStorage.removeItem('langchain_last_difficulty');
            console.log('LocalStorage 초기화 완료');
        } catch(e) {
            console.error('LocalStorage 초기화 실패:', e);
        }
    })();
    </script>
    """

    components.html(clear_script, height=0)
    st.success("브라우저 저장소가 초기화되었습니다.")


# ---------------------- Storage 상태 확인 ---------------------- #
def get_storage_info() -> Dict:
    """
    LocalStorage 사용 정보 반환

    Returns:
        Dict: 저장된 채팅 수, 자동 저장 상태 등
    """
    info = {
        "auto_save_enabled": st.session_state.get("auto_save_enabled", True),
        "storage_initialized": st.session_state.get("storage_initialized", False),
        "total_chats": len(st.session_state.get("chats", {}))
    }

    return info
