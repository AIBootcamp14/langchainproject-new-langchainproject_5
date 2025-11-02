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
                         - search_paper: 논문 데이터베이스에서 검색
                           * 예시: "Transformer 논문", "BERT 논문 찾아줘", "GPT 관련 논문"
                           * 특정 논문이나 연구를 찾을 때 사용

                         - web_search: 웹에서 최신 논문 검색
                           * 예시: "2024년 최신 논문", "최근 연구 동향"
                           * 최신 정보나 실시간 검색이 필요할 때 사용

                         - glossary: 단일 용어의 정의만 검색
                           * 예시: "Attention이 뭐야", "BLEU Score 정의"
                           * ❌ 비교/차이 질문은 해당 안됨: "A와 B의 차이", "A vs B"
                           * 오직 하나의 용어 정의만 물어볼 때 사용

                         - summarize: 논문 요약
                           * 예시: "논문 요약해줘", "이 논문 요약"
                           * 논문의 요약을 요청할 때 사용

                         - save_file: 파일 저장
                           * 예시: "파일로 저장해줘", "다운로드"
                           * 답변을 파일로 저장하고 싶을 때 사용

                         - general: 일반 답변 (기본 도구)
                           * 예시: "A와 B의 차이는?", "설명해줘", "어떻게 작동해?"
                           * 비교 질문, 설명 요청, 개념 질문 등
                           * 위의 특수 도구들에 해당하지 않는 모든 경우

                         중요한 규칙:
                         - "차이", "비교", "vs", "구별" 등의 단어가 있으면 → general
                         - 두 개 이상의 용어를 비교하는 질문 → general
                         - 개념 설명 요청 → general

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
