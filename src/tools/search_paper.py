# src/tools/search_paper.py
"""
RAG 논문 검색 도구 모듈

pgvector 유사도 검색 (Top-5)
PostgreSQL papers 테이블 조회
난이도별 RAG 프롬프트 적용
"""

# ==================== Import ==================== #
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import SystemMessage, HumanMessage
from langchain_postgres.vectorstores import PGVector
import psycopg2
from src.agent.state import AgentState


# ==================== 도구 3: RAG 검색 노드 ==================== #
def search_paper_node(state: AgentState, exp_manager=None):
    """
    RAG 검색 노드: 논문 DB에서 관련 논문 검색 및 답변 생성

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
    tool_logger = exp_manager.get_tool_logger('rag_paper') if exp_manager else None

    if tool_logger:
        tool_logger.write(f"RAG 검색 노드 실행: {question}")
        tool_logger.write(f"난이도: {difficulty}")

    # -------------- Vector DB 초기화 -------------- #
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # 임베딩 모델
        vectorstore = PGVector(
            collection_name="paper_chunks",     # 컬렉션 이름
            embedding_function=embeddings,      # 임베딩 함수
            connection_string=os.getenv("DATABASE_URL")  # DB 연결 문자열
        )

        if tool_logger:
            tool_logger.write("Vector DB 초기화 완료")
    except Exception as e:
        if tool_logger:
            tool_logger.write(f"Vector DB 초기화 실패: {e}")
            tool_logger.close()
        state["final_answer"] = f"데이터베이스 연결 오류: {str(e)}"
        return state

    # -------------- 유사도 검색 (Top-5) -------------- #
    try:
        if tool_logger:
            tool_logger.write("Vector DB 유사도 검색 시작 (Top-5)")

        docs = vectorstore.similarity_search(question, k=5)  # 유사도 검색

        if tool_logger:
            tool_logger.write(f"검색된 문서 수: {len(docs)}")

            # pgvector 검색 기록
            if exp_manager:
                exp_manager.log_pgvector_search({
                    "tool": "rag_paper",          # 도구 이름
                    "query_text": question,       # 검색 질문
                    "top_k": 5,                   # Top-K 값
                    "results_count": len(docs)    # 검색 결과 수
                })
    except Exception as e:
        if tool_logger:
            tool_logger.write(f"Vector 검색 실패: {e}")
            tool_logger.close()
        state["final_answer"] = f"검색 오류: {str(e)}"
        return state

    # -------------- 검색 결과 확인 -------------- #
    if not docs:
        if tool_logger:
            tool_logger.write("검색된 논문이 없음")
            tool_logger.close()
        state["final_answer"] = "관련 논문을 찾을 수 없습니다."
        return state

    # -------------- paper_id 추출 및 메타데이터 조회 -------------- #
    paper_ids = list(set([doc.metadata.get("paper_id") for doc in docs if doc.metadata.get("paper_id")]))

    if not paper_ids:
        if tool_logger:
            tool_logger.write("paper_id를 찾을 수 없음")
            tool_logger.close()
        state["final_answer"] = "논문 메타데이터를 찾을 수 없습니다."
        return state

    # -------------- PostgreSQL 연결 및 메타데이터 조회 -------------- #
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))  # PostgreSQL 연결
        cursor = conn.cursor()

        # papers 테이블에서 메타데이터 조회
        placeholders = ','.join(['%s'] * len(paper_ids))  # SQL placeholder 생성
        query = f"SELECT paper_id, title, authors, publish_date FROM papers WHERE paper_id IN ({placeholders})"

        if tool_logger:
            tool_logger.write(f"SQL 쿼리 실행: paper_id IN {paper_ids}")

            # SQL 쿼리 기록
            if exp_manager:
                exp_manager.log_sql_query(
                    query=query,                  # SQL 쿼리
                    description="논문 메타데이터 조회",  # 쿼리 설명
                    tool="rag_paper"              # 도구 이름
                )

        cursor.execute(query, paper_ids)        # 쿼리 실행
        papers_meta = cursor.fetchall()         # 결과 조회
        cursor.close()                          # 커서 닫기
        conn.close()                            # 연결 닫기

        if tool_logger:
            tool_logger.write(f"조회된 논문 메타데이터 수: {len(papers_meta)}")
    except Exception as e:
        if tool_logger:
            tool_logger.write(f"PostgreSQL 조회 실패: {e}")
            tool_logger.close()
        state["final_answer"] = f"데이터베이스 조회 오류: {str(e)}"
        return state

    # -------------- 컨텍스트 구성 -------------- #
    context = "\n\n".join([
        f"[논문 {i+1}] {doc.page_content}\n출처: {doc.metadata.get('title', 'Unknown')}"
        for i, doc in enumerate(docs)
    ])

    # -------------- 난이도별 프롬프트 설정 -------------- #
    if difficulty == "easy":
        # Easy 모드: 초심자용 설명
        system_prompt = """당신은 논문을 쉽게 설명하는 전문가입니다.
초심자도 이해할 수 있도록 쉽고 명확하게 답변해주세요.
- 전문 용어는 풀어서 설명하세요
- 비유와 예시를 사용하세요
- 수식은 최소화하세요
- 친근하고 이해하기 쉬운 톤을 유지하세요"""
    else:  # hard
        # Hard 모드: 전문가용 설명
        system_prompt = """당신은 논문 분석 전문가입니다.
기술적 세부사항을 포함하여 정확하고 전문적으로 답변해주세요.
- 논문의 핵심 기여를 명확히 설명하세요
- 수식 및 알고리즘을 포함하세요
- 관련 연구와 비교하세요
- 전문가 수준의 정확성을 유지하세요"""

    user_prompt = f"""[참고 논문]
{context}

[질문]
{question}

위 논문을 참고하여 질문에 답변해주세요."""

    # -------------- 프롬프트 저장 -------------- #
    if exp_manager:
        exp_manager.save_system_prompt(system_prompt, metadata={"difficulty": difficulty})
        exp_manager.save_user_prompt(user_prompt, metadata={"papers_count": len(papers_meta)})

    # -------------- LLM 답변 생성 -------------- #
    try:
        if tool_logger:
            tool_logger.write("LLM 답변 생성 시작")

        llm = ChatOpenAI(model="gpt-4", temperature=0.7)  # RAG용 LLM
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
