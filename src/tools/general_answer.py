# src/tools/general_answer.py
"""
일반 답변 도구 모듈

LLM의 자체 지식으로 직접 답변 생성
난이도별(Easy/Hard) 프롬프트 적용
"""

# ==================== Import ==================== #
from langchain.schema import SystemMessage, HumanMessage
from src.agent.state import AgentState
from src.llm.client import LLMClient


# ==================== 도구 1: 일반 답변 노드 ==================== #
def general_answer_node(state: AgentState, exp_manager=None):
    """
    일반 답변 노드: LLM의 자체 지식으로 직접 답변

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- 상태에서 질문 및 난이도 추출 -------------- #
    question = state["question"]                # 사용자 질문
    difficulty = state.get("difficulty", "easy")  # 난이도 (기본값: easy)

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write(f"일반 답변 노드 실행: {question}")
        exp_manager.logger.write(f"난이도: {difficulty}")

    # -------------- 난이도별 SystemMessage 설정 -------------- #
    if difficulty == "easy":
        # Easy 모드: 초심자용 설명
        system_content = """당신은 친절한 AI 어시스턴트입니다.
                            초심자도 이해할 수 있도록 쉽고 명확하게 답변해주세요.
                            - 전문 용어는 최소화하고 일상적인 언어를 사용하세요
                            - 복잡한 개념은 간단한 비유로 설명하세요
                            - 친근하고 이해하기 쉬운 톤을 유지하세요"""
    else:  # hard
        # Hard 모드: 전문가용 설명
        system_content = """당신은 전문적인 AI 어시스턴트입니다.
                            기술적인 세부사항을 포함하여 정확하고 전문적으로 답변해주세요.
                            - 기술 용어와 전문 개념을 자유롭게 사용하세요
                            - 깊이 있는 설명과 상세한 정보를 제공하세요
                            - 전문가 수준의 정확성을 유지하세요"""

    system_msg = SystemMessage(content=system_content)  # SystemMessage 객체 생성

    # -------------- 난이도별 LLM 초기화 -------------- #
    llm_client = LLMClient.from_difficulty(
        difficulty=difficulty,
        logger=exp_manager.logger if exp_manager else None
    )

    # -------------- 메시지 구성 -------------- #
    messages = [
        system_msg,                             # 시스템 프롬프트
        HumanMessage(content=question)          # 사용자 질문
    ]

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write("LLM 호출 시작")

    # -------------- LLM 호출 -------------- #
    response = llm_client.llm.invoke(messages)  # LLM 응답 생성

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write(f"LLM 응답 생성 완료: {len(response.content)} 글자")

    # -------------- 최종 답변 저장 -------------- #
    state["final_answer"] = response.content    # 응답 내용 저장

    return state                                # 업데이트된 상태 반환
