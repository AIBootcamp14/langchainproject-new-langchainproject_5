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

    # -------------- 라우팅 결정 프롬프트 구성 -------------- #
    routing_prompt = f"""사용자 질문을 분석하여 적절한 도구를 선택하세요:

                         도구 목록:
                         - search_paper: 논문 데이터베이스에서 검색 (예: "Transformer 논문", "BERT에 대해 알려줘")
                         - web_search: 웹에서 최신 논문 검색 (예: "2024년 최신 논문", "최근 연구")
                         - glossary: 용어 정의 검색 (예: "Attention이 뭐야", "BLEU Score가 뭐야")
                         - summarize: 논문 요약 (예: "논문 요약해줘", "요약해줘")
                         - save_file: 파일 저장 (예: "파일로 저장해줘", "다운로드해줘", "저장해줘")
                         - general: 일반 답변 (위 도구들에 해당하지 않는 경우)

                         질문: {question}

                         하나의 도구 이름만 반환하세요 (예: search_paper):
                         """

    # -------------- 난이도별 LLM 초기화 -------------- #
    difficulty = state.get("difficulty", "easy")  # 난이도 (기본값: easy)
    llm_client = LLMClient.from_difficulty(
        difficulty=difficulty,
        logger=exp_manager.logger if exp_manager else None
    )

    # -------------- LLM 호출 -------------- #
    tool_choice = llm_client.llm.invoke(routing_prompt).content.strip()  # 도구 선택

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write(f"라우팅 결정: {tool_choice}")

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
