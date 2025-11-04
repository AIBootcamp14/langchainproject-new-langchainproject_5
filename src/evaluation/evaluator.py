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
1. 정확도 (0-10점): 참고 문서의 내용과 일치하는가?
2. 관련성 (0-10점): 질문과 답변이 관련있는가?
3. 난이도 적합성 (0-10점): 난이도 모드에 맞는 답변인가?
4. 출처 명시 (0-10점): 논문 제목, 저자를 명시했는가?

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
        # LLM 초기화 (OpenAI GPT-4)
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

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
