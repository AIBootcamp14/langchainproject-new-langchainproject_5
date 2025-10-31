# src/memory/chat_history.py
"""
대화 메모리 관리 모듈

ConversationBufferMemory 기반 대화 히스토리 관리:
- ChatMemoryManager: 인메모리 대화 히스토리 관리
- get_session_history: 세션 기반 PostgreSQL 저장 (선택)
"""

# ==================== Import ==================== #
from langchain.memory import ConversationBufferMemory
from langchain_postgres import PostgresChatMessageHistory
import os


# ==================== ChatMemoryManager 클래스 ==================== #
class ChatMemoryManager:
    """
    대화 메모리 관리 클래스

    ConversationBufferMemory를 사용하여 대화 히스토리를 관리합니다.
    최근 대화 내용을 메모리에 저장하여 컨텍스트를 유지합니다.
    """

    def __init__(self, return_messages: bool = True, memory_key: str = "chat_history"):
        """
        ConversationBufferMemory 초기화

        Args:
            return_messages (bool): 메시지 객체 형태로 반환 여부 (기본값: True)
            memory_key (str): 메모리 키 설정 (기본값: "chat_history")
        """
        # -------------- ConversationBufferMemory 생성 -------------- #
        self.memory = ConversationBufferMemory(
            return_messages=return_messages,  # 메시지 객체 형태로 반환
            memory_key=memory_key             # 메모리 키
        )

    def add_user_message(self, message: str):
        """
        사용자 메시지 추가

        Args:
            message (str): 사용자 메시지 내용
        """
        # -------------- 사용자 메시지를 메모리에 추가 -------------- #
        self.memory.chat_memory.add_user_message(message)

    def add_ai_message(self, message: str):
        """
        AI 메시지 추가

        Args:
            message (str): AI 응답 메시지 내용
        """
        # -------------- AI 메시지를 메모리에 추가 -------------- #
        self.memory.chat_memory.add_ai_message(message)

    def get_history(self) -> dict:
        """
        전체 대화 히스토리 반환

        Returns:
            dict: 대화 히스토리 (chat_history 키에 메시지 리스트)
        """
        # -------------- 메모리에서 대화 히스토리 로드 -------------- #
        return self.memory.load_memory_variables({})

    def clear(self):
        """
        대화 히스토리 초기화

        메모리에 저장된 모든 대화 내용을 삭제합니다.
        """
        # -------------- 메모리 클리어 -------------- #
        self.memory.clear()


# ==================== 세션 기반 메모리 함수 (선택) ==================== #
def get_session_history(session_id: str) -> PostgresChatMessageHistory:
    """
    세션 기반 메모리 (PostgreSQL 저장)

    PostgreSQL에 대화 내용을 영구 저장하여 세션별로 관리합니다.
    여러 사용자의 대화를 독립적으로 추적할 수 있습니다.

    Args:
        session_id (str): 세션 ID (예: "user_123", "session_abc")

    Returns:
        PostgresChatMessageHistory: PostgreSQL 기반 대화 히스토리 인스턴스
    """
    # -------------- DATABASE_URL 환경변수 로드 -------------- #
    connection_string = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/papers"  # 기본값
    )

    # -------------- PostgresChatMessageHistory 생성 -------------- #
    return PostgresChatMessageHistory(
        session_id=session_id,              # 세션 ID
        connection_string=connection_string, # DB 연결 문자열
        table_name="chat_history"           # 테이블 이름
    )


# ==================== 사용 예시 ==================== #
if __name__ == "__main__":
    # -------------- 기본 메모리 사용 예시 -------------- #
    print("=== ChatMemoryManager 사용 예시 ===")

    # ChatMemoryManager 인스턴스 생성
    memory_manager = ChatMemoryManager()

    # 대화 추가
    memory_manager.add_user_message("Transformer 논문 설명해줘")
    memory_manager.add_ai_message("Transformer는 2017년 Google에서 발표한 'Attention is All You Need' 논문에서 제안된 모델입니다...")

    memory_manager.add_user_message("BERT는 뭐야?")
    memory_manager.add_ai_message("BERT는 2018년에 발표된 사전 훈련 언어 모델로, Bidirectional Encoder Representations from Transformers의 약자입니다...")

    # 히스토리 조회
    history = memory_manager.get_history()
    print(f"대화 히스토리: {history}")

    # 히스토리 초기화
    memory_manager.clear()
    print("히스토리 초기화 완료")

    print("\n=== 세션 기반 메모리 사용 예시 ===")

    # 세션 기반 메모리 (PostgreSQL 필요)
    try:
        session_history = get_session_history("user_123")
        session_history.add_user_message("GPT-3는 어떤 모델이야?")
        session_history.add_ai_message("GPT-3는 2020년 OpenAI에서 발표한 대규모 언어 모델입니다...")

        print(f"세션 메시지 수: {len(session_history.messages)}")
        print("세션 기반 메모리 사용 성공")
    except Exception as e:
        print(f"세션 기반 메모리 오류 (PostgreSQL 연결 필요): {e}")
