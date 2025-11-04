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
from src.prompts import get_tool_prompt


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

    # -------------- JSON 프롬프트 로드 -------------- #
    system_content = get_tool_prompt("general_answer", difficulty)  # JSON 파일에서 프롬프트 로드
    system_msg = SystemMessage(content=system_content)              # SystemMessage 객체 생성

    # 프롬프트 저장 (prompts 폴더)
    if exp_manager:
        exp_manager.save_system_prompt(system_content, {
            "tool": "general_answer",
            "difficulty": difficulty
        })
        exp_manager.save_user_prompt(question, {
            "tool": "general_answer",
            "difficulty": difficulty
        })

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
        exp_manager.logger.write("=" * 80)
        exp_manager.logger.write("[LLM 답변 전체 내용]")
        exp_manager.logger.write(response.content)
        exp_manager.logger.write("=" * 80)

    # -------------- 최종 답변 저장 -------------- #
    state["final_answer"] = response.content    # 응답 내용 저장

    return state                                # 업데이트된 상태 반환
