# src/agent/state.py
"""
Agent 상태 정의 모듈

LangGraph Agent의 상태(State)를 TypedDict로 정의:
- 사용자 질문 및 난이도
- 도구 선택 및 실행 결과
- 최종 답변
- 대화 히스토리
"""

# ------------------------- 표준 라이브러리 ------------------------- #
from typing import TypedDict
# TypedDict: 타입 힌트가 포함된 딕셔너리


# ==================== Agent 상태 정의 ==================== #
class AgentState(TypedDict):
    """
    LangGraph Agent의 상태 정의

    Attributes:
        question (str): 사용자 질문
        difficulty (str): 난이도 ('easy' 또는 'hard')
        tool_choice (str): 선택된 도구 이름
        tool_result (str): 도구 실행 결과
        final_answer (str): 최종 답변
        messages (list): 대화 히스토리 (메시지 리스트)
    """
    question: str                               # 사용자 질문
    difficulty: str                             # 난이도 (easy/hard)
    tool_choice: str                            # 선택된 도구
    tool_result: str                            # 도구 실행 결과
    final_answer: str                           # 최종 답변
    messages: list                              # 대화 히스토리
