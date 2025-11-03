# src/agent/nodes.py
"""
Agent 노드 함수 모듈

LangGraph Agent의 노드 함수들:
- router_node: 질문 분석 및 도구 선택
- 6개 도구 노드 (src/tools/에서 import)
"""

# ==================== 라이브러리 Import ==================== #
from src.agent.state import AgentState
from src.llm.client import LLMClient
from src.prompts import get_routing_prompt

# ==================== 도구 Import ==================== #
from src.tools.general_answer import general_answer_node
from src.tools.save_file import save_file_node
from src.tools.search_paper import search_paper_node
from src.tools.web_search import web_search_node
from src.tools.glossary import glossary_node
from src.tools.summarize import summarize_node


# ==================== 라우터 노드 ==================== #
# ---------------------- 질문 분석 및 도구 선택 ---------------------- #
def router_node(state: AgentState, exp_manager=None):
    """
    라우터 노드: 질문을 분석하여 적절한 도구 선택

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태 (tool_choice 포함)
    """
    # -------------- 상태에서 질문 추출 -------------- #
    question = state["question"]                # 사용자 질문

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write(f"라우터 노드 실행: {question}")

    # -------------- JSON 프롬프트 로드 -------------- #
    routing_prompt_template = get_routing_prompt()    # JSON 파일에서 프롬프트 로드
    routing_prompt = routing_prompt_template.format(question=question)  # 질문 삽입

    # -------------- 난이도별 LLM 초기화 -------------- #
    difficulty = state.get("difficulty", "easy")  # 난이도 (기본값: easy)
    llm_client = LLMClient.from_difficulty(
        difficulty=difficulty,
        logger=exp_manager.logger if exp_manager else None
    )

    # -------------- LLM 호출 -------------- #
    raw_response = llm_client.llm.invoke(routing_prompt).content.strip()  # 도구 선택

    # -------------- 응답 파싱: 첫 번째 단어만 추출 -------------- #
    # LLM이 설명을 포함할 수 있으므로, 첫 번째 단어만 가져옴
    tool_choice = raw_response.split()[0] if raw_response else "general"

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write(f"라우팅 결정 (원본): {raw_response[:100]}...")
        exp_manager.logger.write(f"라우팅 결정 (파싱): {tool_choice}")

    # -------------- 상태 업데이트 -------------- #
    state["tool_choice"] = tool_choice          # 선택된 도구 저장

    return state                                # 업데이트된 상태 반환


# ==================== Export 목록 ==================== #
__all__ = [
    'router_node',
    'general_answer_node',
    'save_file_node',
    'search_paper_node',
    'web_search_node',
    'glossary_node',
    'summarize_node',
]
