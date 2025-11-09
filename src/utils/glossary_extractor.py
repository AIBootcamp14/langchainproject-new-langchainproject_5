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
def extract_terms_from_answer(
    answer: str,
    difficulty: str = "easy",
    min_terms: int = 1,
    max_terms: int = 5,
    logger=None
) -> List[Dict[str, str]]:
    """
    LLM 답변에서 AI/ML 용어를 추출하고 정의 생성

    Args:
        answer: LLM 답변 텍스트
        difficulty: 난이도 (easy 또는 hard)
        min_terms: 최소 추출 용어 개수 (기본값: 1)
        max_terms: 최대 추출 용어 개수 (기본값: 5)
        logger: Logger 인스턴스 (선택 사항)

    Returns:
        용어 리스트 [{"term": "...", "definition": "...", "category": "..."}]
    """
    # -------------- 로깅 -------------- #
    if logger:
        logger.write(f"용어 추출 시작 (범위: {min_terms}-{max_terms}개)")

    # -------------- LLM 프롬프트 구성 -------------- #
    extraction_prompt = f"""다음 답변에서 사용된 AI/ML 관련 전문 용어를 추출하고, 각 용어에 대한 정의와 난이도별 설명을 생성하세요.

답변:
{answer}

다음 JSON 형식으로 반환하세요:
{{
  "terms": [
    {{
      "term": "용어명",
      "definition": "간단한 정의 (1-2문장)",
      "easy_explanation": "초보자도 이해할 수 있는 쉬운 설명 (비유, 예시 포함)",
      "hard_explanation": "전문가용 상세 설명 (기술적 세부사항, 수식 포함)",
      "category": "카테고리 (예: Deep Learning, NLP, Computer Vision 등)"
    }}
  ]
}}

주의사항:
- AI/ML 관련 전문 용어만 추출하세요
- IT/컴퓨터 과학 관련 용어만 대상으로 합니다
- easy_explanation은 비유와 예시를 사용하여 쉽게 설명
- hard_explanation은 기술적 세부사항과 수식을 포함
- 일반적인 단어는 제외하세요
- 용어를 정확성/유사도 순으로 우선순위를 정하세요
- **최소 {min_terms}개 ~ 최대 {max_terms}개 용어를 추출하세요**
- IT 용어가 {min_terms}개 미만이면 실제 추출된 개수만 반환하세요
- 개수를 맞추기 위해 무작위 단어를 포함하지 마세요
- 용어가 없으면 빈 리스트를 반환하세요

용어 우선순위 기준:
1. 핵심 개념인 용어 우선 (예: Transformer, BERT)
2. 자주 사용된 용어 우선
3. 정의가 명확한 용어 우선
4. 일반 단어보다 전문 용어 우선

결과는 우선순위 높은 순서로 정렬하세요.
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

        # JSON 파싱 전 escape 문자 처리
        # LLM이 생성한 JSON에서 잘못된 escape 문자를 정리
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            if logger:
                logger.write(f"JSON 파싱 1차 시도 실패: {e}", print_error=True)

            # 2차 시도: strict=False로 파싱 (이스케이프 처리 완화)
            try:
                data = json.loads(response_text, strict=False)
            except json.JSONDecodeError as e2:
                if logger:
                    logger.write(f"JSON 파싱 2차 시도 실패: {e2}", print_error=True)
                    logger.write(f"응답 텍스트 샘플: {response_text[:500]}")
                return []

        terms = data.get("terms", [])

        if logger:
            logger.write(f"추출된 용어 수: {len(terms)}")

        return terms

    except Exception as e:
        if logger:
            logger.write(f"용어 추출 실패: {e}", print_error=True)
        return []


# ---------------------- IT 용어 검증 및 필터링 함수 ---------------------- #
def validate_extracted_terms(terms: List[Dict], min_terms: int, max_terms: int, logger=None) -> List[Dict]:
    """
    추출된 용어의 품질 검증 및 필터링

    조건:
    - IT/ML 관련 용어만 포함
    - 정확성/유사도 높은 순으로 정렬 (LLM이 이미 정렬함)
    - min_terms 미만이어도 무작위 단어 추가 금지
    - max_terms 초과 시 상위 max_terms개만 반환

    Args:
        terms: 추출된 용어 리스트
        min_terms: 최소 용어 개수
        max_terms: 최대 용어 개수
        logger: Logger 인스턴스 (선택 사항)

    Returns:
        검증된 용어 리스트 (최대 max_terms개)
    """
    if not terms:
        return []

    # IT 관련 키워드 리스트
    it_keywords = [
        # AI/ML 기본
        "learning", "network", "neural", "algorithm", "data", "model",
        "training", "deep", "machine", "artificial", "intelligence",

        # Transformer/NLP
        "transformer", "attention", "embedding", "vector", "tensor",
        "bert", "gpt", "nlp", "language", "token", "encoder", "decoder",

        # 딥러닝 기본
        "gradient", "optimization", "loss", "activation", "layer",
        "convolution", "pooling", "dropout", "batch", "normalization",

        # Computer Vision
        "cnn", "resnet", "yolo", "detection", "segmentation", "classification",
        "image", "vision", "feature", "filter", "kernel",

        # Reinforcement Learning
        "reinforcement", "policy", "reward", "agent", "q-learning",
        "markov", "monte carlo", "temporal difference",

        # 일반 IT/CS
        "database", "sql", "query", "index", "schema", "table",
        "api", "http", "rest", "json", "xml", "protocol",
        "python", "java", "javascript", "code", "function", "class",
        "graph", "tree", "array", "matrix", "optimization",
        "probability", "statistics", "distribution", "variance",

        # 기타
        "gan", "vae", "autoencoder", "lstm", "rnn", "gru",
        "backpropagation", "forward", "inference", "prediction"
    ]

    # IT 용어 필터링
    filtered_terms = []
    for term in terms:
        term_name = term.get("term", "").lower()
        category = term.get("category", "").lower()

        # 카테고리나 용어명에 IT 키워드가 포함되어 있는지 확인
        is_it_term = any(keyword in term_name or keyword in category for keyword in it_keywords)

        if is_it_term:
            filtered_terms.append(term)
        else:
            if logger:
                logger.write(f"IT 용어 아님 (필터링): {term.get('term', 'Unknown')}")

    # 최대 개수 제한 (LLM이 이미 우선순위 순으로 정렬했으므로 상위 N개만)
    result = filtered_terms[:max_terms]

    if logger:
        logger.write(f"용어 검증 완료: {len(terms)}개 → {len(filtered_terms)}개 (IT 필터링) → {len(result)}개 (최대 개수 제한)")

    return result


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
        INSERT INTO glossary (term, definition, easy_explanation, hard_explanation, category, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON CONFLICT (term) DO NOTHING
        RETURNING term_id;
        """

        saved_count = 0

        for term_data in terms:
            term = term_data.get("term", "").strip()
            definition = term_data.get("definition", "").strip()
            easy_explanation = term_data.get("easy_explanation", "").strip()
            hard_explanation = term_data.get("hard_explanation", "").strip()
            category = term_data.get("category", "AI/ML").strip()

            # 필수 필드 확인
            if not term or not definition:
                if logger:
                    logger.write(f"용어 건너뛰기 (필수 필드 없음): {term_data}")
                continue

            try:
                cursor.execute(insert_query, (term, definition, easy_explanation, hard_explanation, category))
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
def extract_and_save_terms(
    answer: str,
    difficulty: str = "easy",
    min_terms: int = 1,
    max_terms: int = 5,
    logger=None
) -> int:
    """
    LLM 답변에서 용어를 추출하고 저장하는 통합 함수

    Args:
        answer: LLM 답변 텍스트
        difficulty: 난이도
        min_terms: 최소 추출 용어 개수 (기본값: 1)
        max_terms: 최대 추출 용어 개수 (기본값: 5)
        logger: Logger 인스턴스 (선택 사항)

    Returns:
        저장된 용어 수
    """
    # 용어 추출
    terms = extract_terms_from_answer(answer, difficulty, min_terms, max_terms, logger)

    # 품질 검증 및 IT 용어 필터링
    validated_terms = validate_extracted_terms(terms, min_terms, max_terms, logger)

    # 용어 저장
    saved_count = save_terms_to_glossary(validated_terms, logger)

    return saved_count
