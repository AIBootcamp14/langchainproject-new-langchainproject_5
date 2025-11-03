# src/agent/graph.py
"""
Agent 그래프 구성 모듈

LangGraph StateGraph 기반 AI Agent 그래프:
- 노드 추가 (router + 6개 도구)
- 조건부 엣지 설정
- 그래프 컴파일
"""

# ------------------------- 표준 라이브러리 ------------------------- #
from functools import partial

# ------------------------- LangGraph 라이브러리 ------------------------- #
from langgraph.graph import StateGraph, END
# StateGraph: LangGraph 상태 그래프
# END: 종료 노드

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.agent.state import AgentState
from src.agent.nodes import (
    router_node,
    general_answer_node,
    save_file_node,
    search_paper_node,
    web_search_node,
    glossary_node,
    summarize_node,
    text2sql_node
)
# AgentState: Agent 상태 정의
# 노드 함수들: router + 6개 도구


# ==================== 라우팅 함수 ==================== #
# ---------------------- 다음 노드 결정 ---------------------- #
def route_to_tool(state: AgentState):
    """
    라우팅 결정에 따라 다음 노드 선택

    Args:
        state (AgentState): Agent 상태

    Returns:
        str: 다음 노드 이름
    """
    # -------------- tool_choice 값을 반환 -------------- #
    return state["tool_choice"]                 # 선택된 도구 이름 반환


# ==================== Agent 그래프 생성 함수 ==================== #
# ---------------------- LangGraph StateGraph 구성 ---------------------- #
def create_agent_graph(exp_manager=None):
    """
    LangGraph Agent 그래프 생성

    Args:
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        CompiledGraph: 컴파일된 Agent 그래프
    """
    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write("Agent 그래프 생성 시작")

    # -------------- StateGraph 생성 -------------- #
    workflow = StateGraph(AgentState)           # AgentState 기반 그래프 생성

    # -------------- exp_manager를 바인딩한 노드 함수 생성 -------------- #
    # partial을 사용하여 각 노드에 exp_manager를 미리 바인딩
    router_with_exp = partial(router_node, exp_manager=exp_manager)
    general_with_exp = partial(general_answer_node, exp_manager=exp_manager)
    save_file_with_exp = partial(save_file_node, exp_manager=exp_manager)
    search_paper_with_exp = partial(search_paper_node, exp_manager=exp_manager)
    web_search_with_exp = partial(web_search_node, exp_manager=exp_manager)
    glossary_with_exp = partial(glossary_node, exp_manager=exp_manager)
    summarize_with_exp = partial(summarize_node, exp_manager=exp_manager)
    text2sql_with_exp = partial(text2sql_node, exp_manager=exp_manager)

    # -------------- 노드 추가 -------------- #
    workflow.add_node("router", router_with_exp)                    # 라우터 노드
    workflow.add_node("general", general_with_exp)                  # 일반 답변 노드
    workflow.add_node("save_file", save_file_with_exp)              # 파일 저장 노드
    workflow.add_node("search_paper", search_paper_with_exp)        # RAG 검색 노드
    workflow.add_node("web_search", web_search_with_exp)            # 웹 검색 노드
    workflow.add_node("glossary", glossary_with_exp)                # 용어집 노드
    workflow.add_node("summarize", summarize_with_exp)              # 논문 요약 노드
    workflow.add_node("text2sql", text2sql_with_exp)                # Text-to-SQL 노드

    # -------------- 시작점 설정 -------------- #
    workflow.set_entry_point("router")          # 라우터를 시작점으로 설정

    # -------------- 조건부 엣지 설정 -------------- #
    # 라우터에서 선택된 도구로 분기
    workflow.add_conditional_edges(
        "router",                               # 출발 노드
        route_to_tool,                          # 라우팅 함수
        {
            "general": "general",               # general → general_answer_node
            "save_file": "save_file",           # save_file → save_file_node
            "search_paper": "search_paper",     # search_paper → search_paper_node
            "web_search": "web_search",         # web_search → web_search_node
            "glossary": "glossary",             # glossary → glossary_node
            "summarize": "summarize",           # summarize → summarize_node
            "text2sql": "text2sql"              # text2sql → text2sql_node
        }
    )

    # -------------- 종료 엣지 설정 -------------- #
    # 모든 도구 노드에서 종료
    for node in ["general", "save_file", "search_paper", "web_search", "glossary", "summarize", "text2sql"]:
        workflow.add_edge(node, END)            # 각 노드 → END

    # -------------- 그래프 컴파일 -------------- #
    agent_executor = workflow.compile()         # 그래프 컴파일

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write("Agent 그래프 컴파일 완료")

    return agent_executor                       # 컴파일된 그래프 반환
