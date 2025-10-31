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

    # -------------- LLM 초기화 -------------- #
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)  # 일반 답변용 LLM

    # -------------- 메시지 구성 -------------- #
    messages = [
        system_msg,                             # 시스템 프롬프트
        HumanMessage(content=question)          # 사용자 질문
    ]

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write("LLM 호출 시작")

    # -------------- LLM 호출 -------------- #
    response = llm.invoke(messages)             # LLM 응답 생성

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write(f"LLM 응답 생성 완료: {len(response.content)} 글자")

    # -------------- 최종 답변 저장 -------------- #
    state["final_answer"] = response.content    # 응답 내용 저장

    return state                                # 업데이트된 상태 반환


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
