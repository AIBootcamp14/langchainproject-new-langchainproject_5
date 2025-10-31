# src/tools/web_search.py
"""
웹 검색 도구 모듈

Tavily API로 최신 논문 정보 검색
검색 결과 LLM 정리
난이도별 프롬프트 적용
"""

# ==================== Import ==================== #
import os
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from src.agent.state import AgentState


# ==================== 도구 4: 웹 검색 노드 ==================== #
def web_search_node(state: AgentState, exp_manager=None):
    """
    웹 검색 노드: Tavily API로 최신 논문 정보 검색

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- 상태에서 질문 및 난이도 추출 -------------- #
    question = state["question"]                # 사용자 질문
    difficulty = state.get("difficulty", "easy")  # 난이도 (기본값: easy)

    # -------------- 도구별 Logger 생성 -------------- #
    tool_logger = exp_manager.get_tool_logger('web_search') if exp_manager else None

    if tool_logger:
        tool_logger.write(f"웹 검색 노드 실행: {question}")
        tool_logger.write(f"난이도: {difficulty}")

    # -------------- Tavily Search API 초기화 -------------- #
    try:
        search_tool = TavilySearchResults(
            max_results=5,                      # 최대 검색 결과 수
            api_key=os.getenv("TAVILY_API_KEY")  # Tavily API 키
        )

        if tool_logger:
            tool_logger.write("Tavily Search API 초기화 완료")
    except Exception as e:
        if tool_logger:
            tool_logger.write(f"Tavily API 초기화 실패: {e}")
            tool_logger.close()
        state["final_answer"] = f"웹 검색 API 초기화 오류: {str(e)}"
        return state

    # -------------- 웹 검색 실행 -------------- #
    try:
        if tool_logger:
            tool_logger.write("Tavily Search API 호출 시작")

        search_results = search_tool.invoke({"query": question})  # 검색 실행

        if tool_logger:
            tool_logger.write(f"검색 결과 수: {len(search_results)}")
    except Exception as e:
        if tool_logger:
            tool_logger.write(f"웹 검색 실패: {e}")
            tool_logger.close()
        state["final_answer"] = f"웹 검색 오류: {str(e)}"
        return state

    # -------------- 검색 결과 확인 -------------- #
    if not search_results:
        if tool_logger:
            tool_logger.write("검색 결과가 없음")
            tool_logger.close()
        state["final_answer"] = "웹에서 관련 정보를 찾을 수 없습니다."
        return state

    # -------------- 검색 결과 포맷팅 -------------- #
    formatted_results = "\n\n".join([
        f"[결과 {i+1}]\n제목: {result.get('title', 'N/A')}\n내용: {result.get('content', 'N/A')}\nURL: {result.get('url', 'N/A')}"
        for i, result in enumerate(search_results)
    ])

    # -------------- 난이도별 프롬프트 설정 -------------- #
    if difficulty == "easy":
        # Easy 모드: 초심자용 설명
        system_prompt = """당신은 최신 논문 정보를 쉽게 설명하는 전문가입니다.
초심자도 이해할 수 있도록 검색 결과를 정리해주세요.
- 핵심 내용을 간단히 요약하세요
- 쉬운 언어를 사용하세요
- 중요한 정보만 선별하세요
- 친근하고 이해하기 쉬운 톤을 유지하세요"""
    else:  # hard
        # Hard 모드: 전문가용 설명
        system_prompt = """당신은 논문 분석 전문가입니다.
검색 결과를 전문적으로 정리해주세요.
- 기술적 세부사항을 포함하세요
- 최신 연구 동향을 분석하세요
- 관련 논문들을 비교하세요
- 전문가 수준의 정확성을 유지하세요"""

    user_prompt = f"""[웹 검색 결과]
{formatted_results}

[질문]
{question}

위 검색 결과를 바탕으로 질문에 답변해주세요."""

    # -------------- 프롬프트 저장 -------------- #
    if exp_manager:
        exp_manager.save_system_prompt(system_prompt, metadata={"difficulty": difficulty})
        exp_manager.save_user_prompt(user_prompt, metadata={"results_count": len(search_results)})

    # -------------- LLM 답변 생성 -------------- #
    try:
        if tool_logger:
            tool_logger.write("LLM 답변 생성 시작")

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)  # 웹 검색용 LLM
        messages = [
            SystemMessage(content=system_prompt),  # 시스템 프롬프트
            HumanMessage(content=user_prompt)      # 사용자 프롬프트
        ]

        response = llm.invoke(messages)         # LLM 호출

        if tool_logger:
            tool_logger.write(f"답변 생성 완료: {len(response.content)} 글자")
            tool_logger.close()

        # -------------- 최종 답변 저장 -------------- #
        state["final_answer"] = response.content  # 응답 내용 저장

    except Exception as e:
        if tool_logger:
            tool_logger.write(f"LLM 호출 실패: {e}")
            tool_logger.close()
        state["final_answer"] = f"답변 생성 오류: {str(e)}"

    return state                                # 업데이트된 상태 반환
