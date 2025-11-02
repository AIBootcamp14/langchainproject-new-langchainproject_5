# src/tools/summarize.py
"""
논문 요약 도구 모듈

PostgreSQL papers 테이블에서 논문 검색
pgvector에서 논문 청크 조회
load_summarize_chain (stuff 방식) 사용
난이도별 요약 프롬프트 적용
"""

# ==================== Import ==================== #
import os
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
import psycopg2
from src.agent.state import AgentState
from src.llm.client import LLMClient


# ==================== 도구 6: 논문 요약 노드 ==================== #
def summarize_node(state: AgentState, exp_manager=None):
    """
    논문 요약 노드
    PostgreSQL papers 테이블에서 논문을 검색하고,
    pgvector에서 해당 논문의 모든 청크를 조회하여 요약 생성
    난이도별(Easy/Hard) 요약 프롬프트 적용

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태 (final_answer에 요약 결과)
    """
    # ============================================================ #
    #                     초기화 및 상태 추출                      #
    # ============================================================ #
    question = state.get("question", "")        # 사용자 질문
    difficulty = state.get("difficulty", "easy") # 난이도

    # ExperimentManager 로거 설정
    tool_logger = None
    if exp_manager:
        tool_logger = exp_manager.get_tool_logger('summarize')
        tool_logger.write(f"논문 요약 노드 실행 - 질문: {question}, 난이도: {difficulty}")

    try:
        # ============================================================ #
        #              1단계: 논문 제목 추출 (LLM 사용)               #
        # ============================================================ #
        # 난이도별 LLM 초기화
        llm_client = LLMClient.from_difficulty(
            difficulty=difficulty,
            logger=exp_manager.logger if exp_manager else None
        )
        extract_prompt = f"""다음 질문에서 요약하려는 논문의 제목을 추출하세요.
                             논문 제목만 정확히 반환하세요. 다른 설명은 불필요합니다.

                             질문: {question}

                             논문 제목:"""

        if tool_logger:
            tool_logger.write(f"논문 제목 추출 프롬프트: {extract_prompt}")

        paper_title = llm_client.llm.invoke(extract_prompt).content.strip()

        if tool_logger:
            tool_logger.write(f"추출된 논문 제목: {paper_title}")

        # ============================================================ #
        #       2단계: PostgreSQL papers 테이블에서 논문 검색          #
        # ============================================================ #
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = conn.cursor()

        # 논문 제목으로 검색 (ILIKE로 부분 일치 허용)
        query = """
        SELECT paper_id, title, authors, abstract, publish_date
        FROM papers
        WHERE title ILIKE %s
        LIMIT 1
        """

        cursor.execute(query, (f"%{paper_title}%",))
        result = cursor.fetchone()

        # ExperimentManager SQL 쿼리 기록
        if exp_manager:
            exp_manager.log_sql_query(
                query=query,
                params=(f"%{paper_title}%",),
                result_count=1 if result else 0
            )

        # 논문을 찾지 못한 경우
        if not result:
            if tool_logger:
                tool_logger.write(f"논문을 찾지 못함: {paper_title}")

            cursor.close()
            conn.close()

            state["final_answer"] = f"'{paper_title}' 논문을 데이터베이스에서 찾지 못했습니다. 논문 제목을 정확히 확인해주세요."
            return state

        # 논문 정보 추출
        paper_id, title, authors, abstract, publish_date = result

        if tool_logger:
            tool_logger.write(f"논문 발견 - ID: {paper_id}, 제목: {title}")

        cursor.close()
        conn.close()

        # ============================================================ #
        #      3단계: pgvector에서 논문의 모든 청크 조회               #
        # ============================================================ #
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vectorstore = PGVector(
            collection_name="paper_chunks",
            embedding_function=embeddings,
            connection_string=os.getenv("DATABASE_URL")
        )

        # paper_id로 필터링하여 모든 청크 조회
        # PGVector의 similarity_search에서 filter 사용
        docs = vectorstore.similarity_search(
            query="",  # 빈 쿼리 (필터만 사용)
            k=100,     # 충분히 많은 수
            filter={"paper_id": paper_id}
        )

        if tool_logger:
            tool_logger.write(f"조회된 청크 수: {len(docs)}")

        # ExperimentManager pgvector 검색 기록
        if exp_manager:
            exp_manager.log_pgvector_search(
                query="",
                top_k=100,
                filter={"paper_id": paper_id},
                result_count=len(docs)
            )

        # 청크가 없는 경우
        if not docs:
            state["final_answer"] = f"'{title}' 논문의 내용을 찾지 못했습니다."
            return state

        # ============================================================ #
        #        4단계: 난이도별 프롬프트 설정 및 요약 생성            #
        # ============================================================ #
        if difficulty == "easy":
            system_content = """당신은 논문을 쉽게 설명하는 AI 어시스턴트입니다.
                                초심자도 이해할 수 있도록 다음 논문을 요약해주세요:
                                - 핵심 내용을 간단하고 명확하게 설명
                                - 전문 용어는 쉬운 말로 풀어서 설명
                                - 3-5개의 주요 포인트로 정리"""
        else:  # hard
            system_content = """당신은 전문적인 논문 분석 AI 어시스턴트입니다.
                                다음 논문을 전문적으로 요약해주세요:
                                - 연구 목적, 방법론, 주요 결과, 결론을 포함
                                - 기술적 세부사항과 핵심 기여도 강조
                                - 학술적 관점에서 종합적으로 분석"""

        # SystemMessage 저장
        if exp_manager:
            exp_manager.save_system_prompt(system_content, "summarize")
            exp_manager.save_user_prompt(question, "summarize")

        # 난이도별 LLM 초기화
        llm_client_summarize = LLMClient.from_difficulty(
            difficulty=difficulty,
            logger=exp_manager.logger if exp_manager else None
        )

        # 프롬프트 템플릿 정의
        prompt_template = f"""{system_content}

                              논문 정보:
                              - 제목: {title}
                              - 저자: {authors}
                              - 발행일: {publish_date}
                              - 초록: {abstract}

                              논문 내용:
                              {{text}}

                              요약:"""

        prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

        # Summarize chain 실행 (stuff 방식)
        chain = load_summarize_chain(
            llm=llm_client_summarize.llm,  # LLMClient의 llm 객체 사용
            chain_type="stuff",             # 모든 문서를 한번에 처리
            prompt=prompt
        )

        if tool_logger:
            tool_logger.write("Summarize chain 실행 중...")

        # 요약 실행
        summary_result = chain.invoke({"input_documents": docs})
        summary = summary_result.get("output_text", "요약 생성 실패")

        if tool_logger:
            tool_logger.write(f"요약 생성 완료 - 길이: {len(summary)} 문자")

        # ============================================================ #
        #                  5단계: 최종 답변 구성                       #
        # ============================================================ #
        final_answer = f"""📄 논문 요약

                           **제목**: {title}
                           **저자**: {authors}
                           **발행일**: {publish_date}

                           **요약**:
                           {summary}"""

        state["tool_result"] = summary          # 도구 실행 결과
        state["final_answer"] = final_answer    # 최종 답변

        if tool_logger:
            tool_logger.write("논문 요약 노드 실행 완료")

        return state

    except Exception as e:
        # 예외 처리
        error_msg = f"논문 요약 중 오류 발생: {str(e)}"

        if tool_logger:
            tool_logger.write(f"오류: {error_msg}")

        state["final_answer"] = error_msg
        return state
