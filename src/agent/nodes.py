# src/agent/nodes.py
"""
Agent 노드 함수 모듈

LangGraph Agent의 노드 함수들:
- router_node: 질문 분석 및 도구 선택
- 6개 도구 노드
"""

# ------------------------- 표준 라이브러리 ------------------------- #
from datetime import datetime
import os
# datetime: 파일명 생성용 타임스탬프
# os: 파일 경로 처리

# ------------------------- LangChain 라이브러리 ------------------------- #
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import SystemMessage, HumanMessage
from langchain_postgres.vectorstores import PGVector
from langchain_community.tools.tavily_search import TavilySearchResults
# ChatOpenAI: OpenAI GPT 모델 클라이언트
# OpenAIEmbeddings: OpenAI 임베딩 모델
# SystemMessage, HumanMessage: 메시지 타입
# PGVector: PostgreSQL pgvector 벡터 스토어
# TavilySearchResults: Tavily 웹 검색 도구

# ------------------------- 데이터베이스 라이브러리 ------------------------- #
import psycopg2
# psycopg2: PostgreSQL 연결

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
    파일 저장 노드: 답변 내용을 파일로 저장

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- 상태에서 질문 추출 -------------- #
    question = state["question"]                # 사용자 질문

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write(f"파일 저장 노드 실행: {question}")

    # -------------- 저장할 내용 확인 -------------- #
    # 이전 답변이 있으면 그것을 저장, 없으면 대화 히스토리 저장
    content_to_save = state.get("tool_result") or state.get("final_answer") or "저장할 내용이 없습니다."

    if exp_manager:
        exp_manager.logger.write(f"저장할 내용 길이: {len(content_to_save)} 글자")

    # -------------- 파일명 생성 -------------- #
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 타임스탬프 생성
    filename = f"response_{timestamp}.txt"      # 파일명 구성

    if exp_manager:
        exp_manager.logger.write(f"파일명: {filename}")

    # -------------- 파일 저장 -------------- #
    if exp_manager:
        # ExperimentManager의 save_output 메서드 사용
        file_path = exp_manager.save_output(filename, content_to_save)  # 파일 저장

        exp_manager.logger.write(f"파일 저장 완료: {file_path}")

        # 성공 메시지 구성
        answer = f"파일이 성공적으로 저장되었습니다.\n파일 경로: {file_path}"
    else:
        # ExperimentManager 없을 때 (테스트 환경)
        output_dir = "outputs"                  # 기본 출력 디렉토리
        os.makedirs(output_dir, exist_ok=True)  # 디렉토리 생성
        file_path = os.path.join(output_dir, filename)  # 파일 경로 생성

        # 파일 쓰기
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_to_save)            # 내용 저장

        # 성공 메시지 구성
        answer = f"파일이 성공적으로 저장되었습니다.\n파일 경로: {file_path}"

    # -------------- 최종 답변 저장 -------------- #
    state["final_answer"] = answer              # 성공 메시지 저장

    return state                                # 업데이트된 상태 반환


# ---------------------- 도구 3: RAG 검색 노드 ---------------------- #
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


# ---------------------- 도구 4: 웹 검색 노드 ---------------------- #
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


# ---------------------- 도구 5: 용어집 노드 ---------------------- #
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
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)  # 용어 추출용 LLM
        extract_prompt = f"""다음 질문에서 핵심 용어를 추출하세요. 용어만 반환하세요:

질문: {question}

용어:"""

        term = llm.invoke(extract_prompt).content.strip()  # 용어 추출

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


# ---------------------- 도구 6: 논문 요약 노드 ---------------------- #
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
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        extract_prompt = f"""다음 질문에서 요약하려는 논문의 제목을 추출하세요.
논문 제목만 정확히 반환하세요. 다른 설명은 불필요합니다.

질문: {question}

논문 제목:"""

        if tool_logger:
            tool_logger.write(f"논문 제목 추출 프롬프트: {extract_prompt}")

        paper_title = llm.invoke(extract_prompt).content.strip()

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

        # LLM 초기화 (GPT-4 사용 - 요약 품질 향상)
        llm_summarize = ChatOpenAI(model="gpt-4", temperature=0.3)

        # load_summarize_chain 사용 (stuff 방식)
        from langchain.chains.summarize import load_summarize_chain
        from langchain.prompts import PromptTemplate

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
            llm=llm_summarize,
            chain_type="stuff",  # 모든 문서를 한번에 처리
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
