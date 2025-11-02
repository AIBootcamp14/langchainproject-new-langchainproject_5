# src/tools/glossary.py
"""
용어집 검색 도구 모듈

PostgreSQL glossary 테이블 연동
LLM 기반 핵심 용어 추출
난이도별 설명 제공 (easy_explanation, hard_explanation)
"""

# ==================== Import ==================== #
import os
import psycopg2
from src.agent.state import AgentState
from src.llm.client import LLMClient


# ==================== 도구 5: 용어집 노드 ==================== #
def glossary_node(state: AgentState, exp_manager=None):
    """
    용어집 노드: glossary 테이블에서 용어 정의 검색

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
    tool_logger = exp_manager.get_tool_logger('rag_glossary') if exp_manager else None

    if tool_logger:
        tool_logger.write(f"용어집 노드 실행: {question}")
        tool_logger.write(f"난이도: {difficulty}")

    # -------------- 질문에서 용어 추출 -------------- #
    try:
        # 난이도별 LLM 초기화
        llm_client = LLMClient.from_difficulty(
            difficulty=difficulty,
            logger=exp_manager.logger if exp_manager else None
        )
        extract_prompt = f"""다음 질문에서 핵심 용어를 추출하세요. 용어만 반환하세요:

                             질문: {question}

                             용어:"""

        term = llm_client.llm.invoke(extract_prompt).content.strip()  # 용어 추출

        if tool_logger:
            tool_logger.write(f"추출된 용어: {term}")
    except Exception as e:
        if tool_logger:
            tool_logger.write(f"용어 추출 실패: {e}")
            tool_logger.close()
        state["final_answer"] = f"용어 추출 오류: {str(e)}"
        return state

    # -------------- PostgreSQL glossary 테이블에서 검색 -------------- #
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))  # PostgreSQL 연결
        cursor = conn.cursor()

        query = "SELECT term, definition, easy_explanation, hard_explanation, category FROM glossary WHERE term ILIKE %s"

        if tool_logger:
            tool_logger.write(f"SQL 쿼리 실행: term ILIKE '%{term}%'")

            # SQL 쿼리 기록
            if exp_manager:
                exp_manager.log_sql_query(
                    query=query,                  # SQL 쿼리
                    description="용어집 검색",     # 쿼리 설명
                    tool="rag_glossary"           # 도구 이름
                )

        cursor.execute(query, (f"%{term}%",))   # 쿼리 실행
        result = cursor.fetchone()              # 결과 조회
        cursor.close()                          # 커서 닫기
        conn.close()                            # 연결 닫기
    except Exception as e:
        if tool_logger:
            tool_logger.write(f"PostgreSQL 조회 실패: {e}")
            tool_logger.close()
        state["final_answer"] = f"데이터베이스 조회 오류: {str(e)}"
        return state

    # -------------- 결과 처리 -------------- #
    if not result:
        if tool_logger:
            tool_logger.write("용어를 찾을 수 없음")
            tool_logger.close()
        state["final_answer"] = f"'{term}' 용어를 용어집에서 찾을 수 없습니다."
        return state

    # 검색 결과 파싱
    term_name, definition, easy_exp, hard_exp, category = result

    if tool_logger:
        tool_logger.write(f"용어 발견: {term_name} (카테고리: {category})")

    # -------------- 난이도별 설명 선택 -------------- #
    if difficulty == "easy":
        # Easy 모드: 쉬운 설명 사용
        explanation = easy_exp if easy_exp else definition
        if tool_logger:
            tool_logger.write("Easy 모드 설명 사용")
    else:  # hard
        # Hard 모드: 어려운 설명 사용
        explanation = hard_exp if hard_exp else definition
        if tool_logger:
            tool_logger.write("Hard 모드 설명 사용")

    # -------------- 최종 답변 구성 -------------- #
    answer = f"""**용어**: {term_name}

                 **카테고리**: {category}

                 **설명**:
                 {explanation}"""

    if tool_logger:
        tool_logger.write(f"답변 생성 완료: {len(answer)} 글자")
        tool_logger.close()

    # -------------- 최종 답변 저장 -------------- #
    state["final_answer"] = answer              # 답변 저장

    return state                                # 업데이트된 상태 반환
