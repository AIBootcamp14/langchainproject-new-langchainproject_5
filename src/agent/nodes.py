# src/agent/nodes.py
"""
Agent 노드 함수 모듈

LangGraph Agent의 노드 함수들:
- router_node: 질문 분석 및 도구 선택
- 6개 도구 노드 (placeholder)
"""

# ------------------------- LangChain 라이브러리 ------------------------- #
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
# ChatOpenAI: OpenAI GPT 모델 클라이언트
# SystemMessage, HumanMessage: 메시지 타입

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.agent.state import AgentState
# AgentState: Agent 상태 정의


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
    routing_prompt = f"""
사용자 질문을 분석하여 적절한 도구를 선택하세요:

도구 목록:
- search_paper: 논문 데이터베이스에서 검색
- web_search: 웹에서 최신 논문 검색
- glossary: 용어 정의 검색
- summarize: 논문 요약
- save_file: 파일 저장
- general: 일반 답변

질문: {question}

하나의 도구 이름만 반환하세요:
    """

    # -------------- LLM 초기화 -------------- #
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)  # 라우팅용 LLM

    # -------------- LLM 호출 -------------- #
    tool_choice = llm.invoke(routing_prompt).content.strip()  # 도구 선택

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write(f"라우팅 결정: {tool_choice}")

    # -------------- 상태 업데이트 -------------- #
    state["tool_choice"] = tool_choice          # 선택된 도구 저장

    return state                                # 업데이트된 상태 반환


# ==================== 6개 도구 노드 (Placeholder) ==================== #
# ---------------------- 도구 1: 일반 답변 노드 ---------------------- #
def general_answer_node(state: AgentState, exp_manager=None):
    """
    일반 답변 노드 (Placeholder)

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- Placeholder 구현 -------------- #
    if exp_manager:
        exp_manager.logger.write("일반 답변 노드 실행 (Placeholder)")

    state["final_answer"] = "일반 답변 노드 (구현 예정)"  # Placeholder 응답

    return state                                # 상태 반환


# ---------------------- 도구 2: 파일 저장 노드 ---------------------- #
def save_file_node(state: AgentState, exp_manager=None):
    """
    파일 저장 노드 (Placeholder)

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- Placeholder 구현 -------------- #
    if exp_manager:
        exp_manager.logger.write("파일 저장 노드 실행 (Placeholder)")

    state["final_answer"] = "파일 저장 노드 (구현 예정)"  # Placeholder 응답

    return state                                # 상태 반환


# ---------------------- 도구 3: RAG 검색 노드 ---------------------- #
def search_paper_node(state: AgentState, exp_manager=None):
    """
    RAG 검색 노드 (Placeholder)

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- Placeholder 구현 -------------- #
    if exp_manager:
        exp_manager.logger.write("RAG 검색 노드 실행 (Placeholder)")

    state["final_answer"] = "RAG 검색 노드 (구현 예정)"  # Placeholder 응답

    return state                                # 상태 반환


# ---------------------- 도구 4: 웹 검색 노드 ---------------------- #
def web_search_node(state: AgentState, exp_manager=None):
    """
    웹 검색 노드 (Placeholder)

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- Placeholder 구현 -------------- #
    if exp_manager:
        exp_manager.logger.write("웹 검색 노드 실행 (Placeholder)")

    state["final_answer"] = "웹 검색 노드 (구현 예정)"  # Placeholder 응답

    return state                                # 상태 반환


# ---------------------- 도구 5: 용어집 노드 ---------------------- #
def glossary_node(state: AgentState, exp_manager=None):
    """
    용어집 노드 (Placeholder)

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- Placeholder 구현 -------------- #
    if exp_manager:
        exp_manager.logger.write("용어집 노드 실행 (Placeholder)")

    state["final_answer"] = "용어집 노드 (구현 예정)"  # Placeholder 응답

    return state                                # 상태 반환


# ---------------------- 도구 6: 논문 요약 노드 ---------------------- #
def summarize_node(state: AgentState, exp_manager=None):
    """
    논문 요약 노드 (Placeholder)

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- Placeholder 구현 -------------- #
    if exp_manager:
        exp_manager.logger.write("논문 요약 노드 실행 (Placeholder)")

    state["final_answer"] = "논문 요약 노드 (구현 예정)"  # Placeholder 응답

    return state                                # 상태 반환
