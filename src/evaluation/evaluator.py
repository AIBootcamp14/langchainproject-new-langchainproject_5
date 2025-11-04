# src/evaluation/evaluator.py
"""
답변 품질 평가 모듈

LLM-as-a-Judge 방식을 사용하여 챗봇 답변의 품질을 평가합니다.
"""

# ------------------------- 표준 라이브러리 ------------------------- #
import json
from typing import Dict, List, Optional

# ------------------------- 서드파티 라이브러리 ------------------------- #
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.utils.logger import Logger


# ==================== 평가 프롬프트 정의 ==================== #
EVALUATION_PROMPT_TEMPLATE = """
다음 AI 챗봇의 답변을 평가해주세요.

[사용자 질문]
{question}

[AI 답변]
{answer}

[참고 문서]
{reference_docs}

[난이도 모드]
{difficulty}

[평가 기준]

1. 정확도 (Accuracy) - 참고 문서와의 일치도 (0-10점)
   - 10점: 참고 문서의 핵심 내용을 모두 정확히 반영, 사실 관계 오류 없음
   - 7-9점: 핵심 내용 80% 이상 정확히 반영, 사소한 표현 차이만 있음
   - 4-6점: 핵심 내용 50% 이상 반영, 일부 내용 누락 또는 경미한 오류 1-2개
   - 1-3점: 일부만 정확, 중요 내용 누락, 사실 오류 여러 개
   - 0점: 참고 문서와 무관하거나 완전히 틀린 정보

2. 관련성 (Relevance) - 질문과 답변의 관련도 (0-10점)
   - 10점: 질문에 직접적이고 완전하게 답변, 불필요한 내용 없음
   - 7-9점: 질문에 직접 답변했으나 일부 정보 누락, 약간의 불필요한 내용 가능
   - 4-6점: 질문과 관련은 있으나 핵심 일부 벗어남, 답변이 간접적
   - 1-3점: 질문과 부분적으로만 관련, 핵심을 다루지 않음
   - 0점: 질문과 완전히 무관한 답변

3. 난이도 적합성 (Difficulty) - 모드별 설명 수준 (0-10점)

   [Easy 모드 기준]
   - 10점: 일상 용어, 비유/예시 사용, 단계별 쉬운 설명 (중학생 수준)
   - 7-9점: 대부분 쉬운 용어, 일부 전문 용어는 설명 추가 (고등학생 수준)
   - 4-6점: 쉬운 용어와 전문 용어 혼재 (대학생 수준)
   - 1-3점: 전문 용어 다수, 어렵고 추상적 설명 (대학원생 수준)
   - 0점: Hard 모드 수준의 전문적 설명

   [Hard 모드 기준]
   - 10점: 전문 용어 정확히 사용, 수식/알고리즘 포함, 논문 원문 수준
   - 7-9점: 대부분 전문적, 일부 간단한 설명 포함
   - 4-6점: 전문 용어와 쉬운 설명 혼재
   - 1-3점: 쉬운 용어 다수, 비유 위주, 피상적 설명
   - 0점: Easy 모드 수준의 쉬운 설명

4. 출처 명시 (Citation) - 참고 문헌 인용 (0-10점)
   - 10점: 논문 제목 + 저자 + 발행 연도 모두 명시
   - 7-9점: 논문 제목 + 저자 명시 (연도 누락) 또는 제목 + 연도 (저자 누락)
   - 4-6점: 논문 제목만 명시 또는 저자만 명시
   - 1-3점: 출처 언급했으나 구체적이지 않음 (예: "한 논문에 따르면")
   - 0점: 출처 명시 전혀 없음

[중요 지침]
- 각 기준별로 정확한 점수를 부여하세요
- 점수 부여 이유를 comment에 간단히 설명하세요
- total_score는 4개 항목의 합계입니다 (0-40점)

JSON 형식으로만 반환하세요:
{{
    "accuracy_score": <점수>,
    "relevance_score": <점수>,
    "difficulty_score": <점수>,
    "citation_score": <점수>,
    "total_score": <총점>,
    "comment": "<평가 코멘트>"
}}
"""

# 프롬프트 템플릿 생성
EVALUATION_PROMPT = PromptTemplate(
    template=EVALUATION_PROMPT_TEMPLATE,
    input_variables=["question", "answer", "reference_docs", "difficulty"]
)


# ==================== AnswerEvaluator 클래스 ==================== #
class AnswerEvaluator:
    """
    답변 품질 평가 클래스 (LLM-as-a-Judge)

    사용자 질문, AI 답변, 참고 문서, 난이도 모드를 입력받아
    4가지 평가 기준으로 답변 품질을 평가합니다.
    """

    # ---------------------- 초기화 메서드 ---------------------- #
    def __init__(self, exp_manager=None):
        """
        AnswerEvaluator 초기화

        Args:
            exp_manager: ExperimentManager 인스턴스 (선택 사항)
        """
        # LLM 초기화 (OpenAI GPT-5)
        self.llm = ChatOpenAI(model="gpt-5", temperature=0)

        # ExperimentManager 설정
        self.exp_manager = exp_manager

        # Logger 초기화
        if exp_manager:
            self.logger = exp_manager.get_tool_logger("evaluator")
        else:
            self.logger = Logger("logs/evaluator.log")

        self.logger.write("AnswerEvaluator 초기화 완료")

    # ---------------------- 답변 평가 메서드 ---------------------- #
    def evaluate(
        self,
        question: str,
        answer: str,
        reference_docs: str,
        difficulty: str
    ) -> Dict:
        """
        답변 평가

        Args:
            question (str): 사용자 질문
            answer (str): AI 답변
            reference_docs (str): 참고 문서
            difficulty (str): 난이도 모드 (easy/hard)

        Returns:
            Dict: 평가 결과 딕셔너리
                - accuracy_score (int): 정확도 점수 (0-10)
                - relevance_score (int): 관련성 점수 (0-10)
                - difficulty_score (int): 난이도 적합성 점수 (0-10)
                - citation_score (int): 출처 명시 점수 (0-10)
                - total_score (int): 총점 (0-40)
                - comment (str): 평가 코멘트
        """
        # -------------- 프롬프트 포맷팅 -------------- #
        # 프롬프트 포맷팅
        prompt = EVALUATION_PROMPT.format(
            question=question,
            answer=answer,
            reference_docs=reference_docs,
            difficulty=difficulty
        )

        self.logger.write(f"평가 시작: {question[:50]}...")

        # -------------- LLM 호출 -------------- #
        try:
            # LLM 호출
            response = self.llm.invoke(prompt)
            result_text = response.content

            self.logger.write(f"LLM 응답 수신: {len(result_text)} 글자")

            # -------------- JSON 파싱 -------------- #
            # JSON 파싱
            result = json.loads(result_text)

            self.logger.write(f"평가 완료: 총점 {result.get('total_score', 0)}/40")

            return result

        # -------------- 예외 처리 -------------- #
        except json.JSONDecodeError as e:
            self.logger.write(f"JSON 파싱 오류: {e}")
            return {
                "accuracy_score": 0,
                "relevance_score": 0,
                "difficulty_score": 0,
                "citation_score": 0,
                "total_score": 0,
                "comment": f"평가 실패: JSON 파싱 오류 ({str(e)})"
            }

        except Exception as e:
            self.logger.write(f"평가 오류: {e}")
            return {
                "accuracy_score": 0,
                "relevance_score": 0,
                "difficulty_score": 0,
                "citation_score": 0,
                "total_score": 0,
                "comment": f"평가 실패: {str(e)}"
            }

    # ---------------------- 배치 평가 메서드 ---------------------- #
    def evaluate_batch(self, test_cases: List[Dict]) -> List[Dict]:
        """
        배치 평가

        Args:
            test_cases (List[Dict]): 테스트 케이스 리스트
                [{"question": ..., "answer": ..., "reference_docs": ..., "difficulty": ...}, ...]

        Returns:
            List[Dict]: 평가 결과 리스트
        """
        results = []

        self.logger.write(f"배치 평가 시작: {len(test_cases)}개 케이스")

        # 각 테스트 케이스 평가
        for i, case in enumerate(test_cases, 1):
            self.logger.write(f"[{i}/{len(test_cases)}] 평가 중...")

            # 평가 수행
            result = self.evaluate(
                question=case["question"],
                answer=case["answer"],
                reference_docs=case.get("reference_docs", ""),
                difficulty=case.get("difficulty", "easy")
            )

            # 질문과 답변 추가
            result["question"] = case["question"]
            result["answer"] = case["answer"]

            results.append(result)

        self.logger.write(f"배치 평가 완료: {len(results)}개 결과")

        return results

    # ---------------------- 종료 메서드 ---------------------- #
    def close(self):
        """Logger 종료"""
        if self.logger and not self.exp_manager:
            self.logger.close()
