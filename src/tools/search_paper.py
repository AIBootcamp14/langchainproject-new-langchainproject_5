# ==========================================
# 📘 RAG 논문 검색 도구 모듈 + Agent 노드 통합
# ------------------------------------------
# - @tool: search_paper_database (팀원 구현)
# - Agent 노드: search_paper_node
# - pgvector 유사도 검색 (Top-K)
# - PostgreSQL papers 테이블 조회
# - 난이도별 RAG 프롬프트 적용
# ==========================================

# ------------------------- 프로젝트 모듈 ------------------------- #
from .rag_search import search_paper_database


# ==================== Agent 노드: RAG 검색 ==================== #

def search_paper_node(state, exp_manager=None):
    """
    Agent 노드: 논문 DB에서 관련 논문 검색 및 답변 생성

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- 상태에서 질문 및 난이도 추출 -------------- #
    question = state["question"]                          # 사용자 질문
    difficulty = state.get("difficulty", "easy")          # 난이도 (기본값: easy)

    # -------------- 도구별 Logger 생성 -------------- #
    tool_logger = exp_manager.get_tool_logger('rag_paper') if exp_manager else None

    if tool_logger:
        tool_logger.write(f"RAG 검색 노드 실행: {question}")
        tool_logger.write(f"난이도: {difficulty}")

    # -------------- search_paper_database 도구 호출 -------------- #
    try:
        # Langchain @tool 함수 호출
        result = search_paper_database.invoke({
            "query": question,                            # 검색 쿼리
            "year_gte": None,                             # 연도 필터 없음
            "author": None,                               # 저자 필터 없음
            "category": None,                             # 카테고리 필터 없음
            "top_k": 5,                                   # Top-5 검색
            "with_scores": True,                          # 유사도 점수 포함
            "use_multi_query": False,                     # MultiQuery 미사용
            "search_mode": "similarity",                  # 유사도 검색
        })

        if tool_logger:
            tool_logger.write(f"검색 결과: {len(result)} 글자")
            tool_logger.close()

        # -------------- 최종 답변 저장 -------------- #
        state["final_answer"] = result                    # 답변 저장

    except Exception as e:
        if tool_logger:
            tool_logger.write(f"논문 검색 실패: {e}")
            tool_logger.close()

        # 에러 메시지 저장
        state["final_answer"] = f"논문 검색 오류: {str(e)}"

    # -------------- 업데이트된 상태 반환 -------------- #
    return state
