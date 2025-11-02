# src/utils/glossary_extractor.py

"""
용어 추출 및 저장 유틸리티 모듈

LLM 답변에서 AI/ML 용어를 추출하고 glossary 테이블에 자동 저장
"""

# ==================================================================================== #
#                                   IMPORT MODULES                                     #
# ==================================================================================== #

# ------------------------- 표준 라이브러리 ------------------------- #
import os
import json
from typing import List, Dict, Optional

# ------------------------- 서드파티 라이브러리 ------------------------- #
import psycopg2

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.llm.client import LLMClient


# ==================================================================================== #
#                              GLOSSARY EXTRACTOR FUNCTIONS                            #
# ==================================================================================== #

# ---------------------- 용어 추출 함수 ---------------------- #
def extract_terms_from_answer(answer: str, difficulty: str = "easy", logger=None) -> List[Dict[str, str]]:
    """
    LLM 답변에서 AI/ML 용어를 추출하고 정의 생성

    Args:
        answer: LLM 답변 텍스트
        difficulty: 난이도 (easy 또는 hard)
        logger: Logger 인스턴스 (선택 사항)

    Returns:
        용어 리스트 [{"term": "...", "definition": "...", "category": "..."}]
    """
    # -------------- 로깅 -------------- #
    if logger:
        logger.write("용어 추출 시작")

    # -------------- LLM 프롬프트 구성 -------------- #
    extraction_prompt = f"""다음 답변에서 사용된 AI/ML 관련 전문 용어를 추출하고, 각 용어에 대한 간단한 정의를 생성하세요.

답변:
{answer}

다음 JSON 형식으로 반환하세요:
{{
  "terms": [
    {{
      "term": "용어명",
      "definition": "간단한 정의 (1-2문장)",
      "category": "카테고리 (예: Deep Learning, NLP, Computer Vision 등)"
    }}
  ]
}}

주의사항:
- AI/ML 관련 전문 용어만 추출하세요
- 일반적인 단어는 제외하세요
- 최대 5개 용어만 추출하세요
- 용어가 없으면 빈 리스트를 반환하세요
"""

    # -------------- LLM 호출 -------------- #
    try:
        llm_client = LLMClient.from_difficulty(difficulty=difficulty, logger=logger)
        response = llm_client.llm.invoke(extraction_prompt)
        response_text = response.content.strip()

        if logger:
            logger.write(f"LLM 응답: {response_text[:200]}...")

        # -------------- JSON 파싱 -------------- #
        # LLM이 ```json ... ``` 형식으로 반환할 수 있으므로 처리
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        data = json.loads(response_text)
        terms = data.get("terms", [])

        if logger:
            logger.write(f"추출된 용어 수: {len(terms)}")

        return terms

    except Exception as e:
        if logger:
            logger.write(f"용어 추출 실패: {e}", print_error=True)
        return []


# ---------------------- 용어 저장 함수 ---------------------- #
def save_terms_to_glossary(terms: List[Dict[str, str]], logger=None) -> int:
    """
    추출된 용어를 glossary 테이블에 저장

    Args:
        terms: 용어 리스트
        logger: Logger 인스턴스 (선택 사항)

    Returns:
        저장된 용어 수
    """
    if not terms:
        return 0

    # -------------- PostgreSQL 연결 -------------- #
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = conn.cursor()

        if logger:
            logger.write(f"glossary 테이블에 {len(terms)}개 용어 저장 시작")

        # -------------- INSERT 쿼리 -------------- #
        insert_query = """
        INSERT INTO glossary (term, definition, category, created_at)
        VALUES (%s, %s, %s, NOW())
        ON CONFLICT (term) DO NOTHING
        RETURNING term_id;
        """

        saved_count = 0

        for term_data in terms:
            term = term_data.get("term", "").strip()
            definition = term_data.get("definition", "").strip()
            category = term_data.get("category", "AI/ML").strip()

            # 필수 필드 확인
            if not term or not definition:
                if logger:
                    logger.write(f"용어 건너뛰기 (필수 필드 없음): {term_data}")
                continue

            try:
                cursor.execute(insert_query, (term, definition, category))
                result = cursor.fetchone()

                # RETURNING이 None이면 중복으로 인해 저장되지 않음
                if result:
                    saved_count += 1
                    if logger:
                        logger.write(f"용어 저장 성공: {term}")
                else:
                    if logger:
                        logger.write(f"용어 이미 존재 (건너뜀): {term}")

            except Exception as e:
                if logger:
                    logger.write(f"용어 저장 실패 ({term}): {e}", print_error=True)

        # -------------- 커밋 및 종료 -------------- #
        conn.commit()
        cursor.close()
        conn.close()

        if logger:
            logger.write(f"용어 저장 완료: {saved_count}/{len(terms)}개")

        return saved_count

    except Exception as e:
        if logger:
            logger.write(f"PostgreSQL 연결 실패: {e}", print_error=True)
        return 0


# ---------------------- 통합 함수 ---------------------- #
def extract_and_save_terms(answer: str, difficulty: str = "easy", logger=None) -> int:
    """
    LLM 답변에서 용어를 추출하고 저장하는 통합 함수

    Args:
        answer: LLM 답변 텍스트
        difficulty: 난이도
        logger: Logger 인스턴스 (선택 사항)

    Returns:
        저장된 용어 수
    """
    # 용어 추출
    terms = extract_terms_from_answer(answer, difficulty, logger)

    # 용어 저장
    saved_count = save_terms_to_glossary(terms, logger)

    return saved_count
