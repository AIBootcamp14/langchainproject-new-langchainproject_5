# ui/components/auth.py

"""
사용자 인증 시스템

streamlit-authenticator를 사용한 간단한 로그인 시스템:
- 사용자 로그인/로그아웃
- 세션 관리
- 권한 확인
"""

# ------------------------- 표준 라이브러리 ------------------------- #
from typing import Optional, Tuple

# ------------------------- 서드파티 라이브러리 ------------------------- #
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


# ==================== 인증 설정 ==================== #
# 기본 사용자 데이터 (실제 환경에서는 DB나 별도 파일로 관리)
DEFAULT_USERS = {
    'usernames': {
        'demo': {
            'name': 'Demo User',
            'password': '$2b$12$KpSHR5qPKjJQvBWE7BfEeOXWpW5rGxmUqP4nHD3IWqXDPWwCQUH8W',  # 'demo123'
            'email': 'demo@example.com',
            'role': 'user'
        },
        'admin': {
            'name': 'Admin User',
            'password': '$2b$12$vHFJ5FKk4S9UUTMfCy4uLeJ9u1fN9lGJZUe8KKW1FW2qGRtEwKCzu',  # 'admin123'
            'email': 'admin@example.com',
            'role': 'admin'
        }
    }
}

# 인증 설정
AUTH_CONFIG = {
    'cookie': {
        'expiry_days': 7,
        'key': 'langchain_project_auth',
        'name': 'langchain_auth_cookie'
    },
    'preauthorized': {
        'emails': []
    }
}


# ==================== 인증 초기화 ==================== #
def initialize_authenticator():
    """
    Authenticator 객체 초기화

    Returns:
        Authenticator: streamlit-authenticator 인스턴스
    """
    if "authenticator" not in st.session_state:
        # 사용자 설정 로드
        config = {
            'credentials': DEFAULT_USERS,
            'cookie': AUTH_CONFIG['cookie'],
            'preauthorized': AUTH_CONFIG['preauthorized']
        }

        # Authenticator 생성
        # streamlit-authenticator 최신 버전: pre_authorized 파라미터 제거됨
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )

        st.session_state.authenticator = authenticator

    return st.session_state.authenticator


# ==================== 로그인 UI ==================== #
def render_login_page(exp_manager=None) -> Tuple[Optional[str], Optional[str], Optional[bool]]:
    """
    로그인 페이지 렌더링

    Args:
        exp_manager: ExperimentManager 인스턴스 (선택)

    Returns:
        Tuple[name, username, authentication_status]:
            - name: 사용자 이름
            - username: 사용자 ID
            - authentication_status: 인증 상태 (True/False/None)
    """
    st.markdown("## 📚 논문 리뷰 챗봇")
    st.caption("🔐 로그인이 필요합니다")
    st.divider()

    # Authenticator 초기화
    authenticator = initialize_authenticator()

    # 로그인 UI
    name, authentication_status, username = authenticator.login()

    # 로그인 상태 처리
    if authentication_status is False:
        st.error("⚠️ 사용자 이름 또는 비밀번호가 올바르지 않습니다.")

        if exp_manager:
            exp_manager.log_ui_interaction("로그인 실패")

    elif authentication_status is None:
        st.info("👤 사용자 이름과 비밀번호를 입력해주세요.")

        # 데모 계정 안내
        with st.expander("ℹ️ 데모 계정 정보", expanded=False):
            st.markdown("""
            **일반 사용자:**
            - 사용자명: `demo`
            - 비밀번호: `demo123`

            **관리자:**
            - 사용자명: `admin`
            - 비밀번호: `admin123`
            """)

    elif authentication_status:
        # 로그인 성공
        if exp_manager:
            exp_manager.log_ui_interaction(f"로그인 성공: {username}")

    return name, username, authentication_status


# ==================== 로그아웃 버튼 ==================== #
def render_logout_button(exp_manager=None):
    """
    로그아웃 버튼 렌더링 (사이드바용)

    Args:
        exp_manager: ExperimentManager 인스턴스 (선택)
    """
    authenticator = st.session_state.get("authenticator")

    if authenticator and st.session_state.get("authentication_status"):
        username = st.session_state.get("username", "사용자")
        name = st.session_state.get("name", "사용자")

        st.markdown(f"### 👤 {name}")
        st.caption(f"@{username}")
        st.divider()

        if st.button("🚪 로그아웃", use_container_width=True):
            authenticator.logout()

            if exp_manager:
                exp_manager.log_ui_interaction(f"로그아웃: {username}")

            st.rerun()


# ==================== 인증 상태 확인 ==================== #
def check_authentication() -> bool:
    """
    현재 사용자의 인증 상태 확인

    Returns:
        bool: 인증되었으면 True, 아니면 False
    """
    return st.session_state.get("authentication_status", False)


# ==================== 사용자 정보 가져오기 ==================== #
def get_current_user() -> Optional[dict]:
    """
    현재 로그인한 사용자 정보 반환

    Returns:
        Optional[dict]: 사용자 정보 딕셔너리 또는 None
    """
    if not check_authentication():
        return None

    username = st.session_state.get("username")
    name = st.session_state.get("name")

    if username and name:
        # 사용자 역할 가져오기
        user_data = DEFAULT_USERS['usernames'].get(username, {})
        role = user_data.get('role', 'user')
        email = user_data.get('email', '')

        return {
            'username': username,
            'name': name,
            'email': email,
            'role': role
        }

    return None


# ==================== 관리자 권한 확인 ==================== #
def is_admin() -> bool:
    """
    현재 사용자가 관리자인지 확인

    Returns:
        bool: 관리자면 True, 아니면 False
    """
    user = get_current_user()

    if user:
        return user.get('role') == 'admin'

    return False
