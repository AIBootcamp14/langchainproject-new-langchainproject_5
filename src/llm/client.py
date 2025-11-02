# src/llm/client.py
"""
LLM 클라이언트 모듈

LangChain 기반 다중 LLM 클라이언트 구현:
- OpenAI API (GPT-3.5, GPT-4)
- Solar API (Upstage)
- 에러 핸들링 및 재시도 로직
- 토큰 사용량 추적
- 스트리밍 응답 처리
"""

# ------------------------- 표준 라이브러리 ------------------------- #
import os
# os: 환경변수 로드

# ------------------------- LangChain 라이브러리 ------------------------- #
from langchain_openai import ChatOpenAI
from langchain_upstage import ChatUpstage
from langchain.callbacks import get_openai_callback
# ChatOpenAI: OpenAI GPT 모델 클라이언트
# ChatUpstage: Solar (Upstage) 모델 클라이언트
# get_openai_callback: OpenAI 토큰 사용량 추적

# ------------------------- 유틸리티 라이브러리 ------------------------- #
from tenacity import retry, stop_after_attempt, wait_exponential
# tenacity: 재시도 로직 (Exponential Backoff)

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.utils.config_loader import get_llm_for_difficulty
# get_llm_for_difficulty: 난이도별 LLM 모델 선택


# ==================== LLM 클라이언트 클래스 ==================== #
class LLMClient:
    """다중 LLM 클라이언트 클래스"""

    # ---------------------- 초기화 함수 ---------------------- #
    def __init__(self, provider="openai", model="gpt-3.5-turbo", temperature=0.7, logger=None):
        """
        LLM 클라이언트 초기화

        Args:
            provider (str): LLM 제공자 ("openai" 또는 "solar")
            model (str): 모델 이름
            temperature (float): 창의성 수준 (0.0 ~ 1.0)
            logger: Logger 인스턴스 (선택 사항)
        """
        self.provider = provider                    # LLM 제공자 저장
        self.logger = logger                        # Logger 인스턴스 저장

        # -------------- 로깅 시작 -------------- #
        if self.logger:
            self.logger.write(f"LLM 초기화: provider={provider}, model={model}")

        # -------------- OpenAI 클라이언트 생성 -------------- #
        if provider == "openai":
            self.llm = ChatOpenAI(
                model=model,                        # 모델명 (gpt-3.5-turbo, gpt-4)
                temperature=temperature,            # 창의성 수준
                openai_api_key=os.getenv("OPENAI_API_KEY"),  # API 키
                streaming=True                      # 스트리밍 응답 활성화
            )

        # -------------- Solar 클라이언트 생성 -------------- #
        elif provider == "solar":
            self.llm = ChatUpstage(
                model=model,                        # Solar 모델명
                temperature=temperature,            # 창의성 수준
                api_key=os.getenv("SOLAR_API_KEY"),  # Upstage API 키
                streaming=True                      # 스트리밍 응답 활성화
            )

    # ---------------------- 난이도별 LLM 클라이언트 생성 (클래스 메서드) ---------------------- #
    @classmethod
    def from_difficulty(cls, difficulty: str, language: str = "ko", logger=None):
        """
        난이도에 따라 적절한 LLM 클라이언트 생성

        Args:
            difficulty: 난이도 (easy 또는 hard)
            language: 언어 코드 (ko, en 등)
            logger: Logger 인스턴스 (선택 사항)

        Returns:
            LLMClient 인스턴스
        """
        # -------------- config에서 모델 정보 가져오기 -------------- #
        model_info = get_llm_for_difficulty(difficulty, language)

        provider = model_info["provider"]           # openai 또는 solar
        model = model_info["model"]                 # 모델명

        # -------------- Temperature 설정 -------------- #
        # easy 모드: 0.7 (자연스러운 답변)
        # hard 모드: 0.7 (전문적이지만 자연스러운 답변)
        temperature = 0.7

        # -------------- 로깅 -------------- #
        if logger:
            logger.write(f"난이도별 LLM 선택: difficulty={difficulty}, provider={provider}, model={model}")

        # -------------- LLMClient 인스턴스 생성 -------------- #
        return cls(provider=provider, model=model, temperature=temperature, logger=logger)

    # ---------------------- 재시도 로직이 포함된 LLM 호출 ---------------------- #
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=8))
    def invoke_with_retry(self, messages):
        """
        에러 핸들링 및 재시도 로직

        최대 3회 재시도, Exponential Backoff (2초 → 4초 → 8초)

        Args:
            messages: LLM에 전달할 메시지 리스트

        Returns:
            LLM 응답
        """
        # -------------- 로깅 -------------- #
        if self.logger:
            self.logger.write("LLM 호출 시작 (재시도 가능)")

        # -------------- LLM 호출 -------------- #
        return self.llm.invoke(messages)            # 메시지 전달 및 응답 반환

    # ---------------------- 토큰 사용량 추적이 포함된 LLM 호출 ---------------------- #
    def invoke_with_tracking(self, messages):
        """
        토큰 사용량 추적

        OpenAI API의 경우 토큰 수와 비용을 추적

        Args:
            messages: LLM에 전달할 메시지 리스트

        Returns:
            LLM 응답
        """
        # -------------- OpenAI 토큰 추적 -------------- #
        if self.provider == "openai":
            with get_openai_callback() as cb:       # OpenAI 콜백 시작
                response = self.llm.invoke(messages)  # LLM 호출

                # 토큰 정보 로깅
                if self.logger:
                    self.logger.write(f"Tokens Used: {cb.total_tokens}")
                    self.logger.write(f"Total Cost: ${cb.total_cost:.4f}")

                return response                     # 응답 반환

        # -------------- Solar 기본 호출 -------------- #
        else:
            return self.llm.invoke(messages)        # Solar는 토큰 추적 미지원

    # ---------------------- 스트리밍 응답 처리 ---------------------- #
    async def astream(self, messages):
        """
        스트리밍 응답 처리

        비동기 스트리밍으로 LLM 응답을 청크 단위로 yield

        Args:
            messages: LLM에 전달할 메시지 리스트

        Yields:
            응답 청크
        """
        # -------------- 로깅 -------------- #
        if self.logger:
            self.logger.write("스트리밍 응답 시작")

        # -------------- 비동기 스트리밍 -------------- #
        async for chunk in self.llm.astream(messages):  # 청크 단위로 응답 수신
            yield chunk                             # 청크 반환


# ==================== 작업 유형별 LLM 선택 함수 ==================== #
# ---------------------- 작업 유형별 최적 LLM 선택 ---------------------- #
def get_llm_for_task(task_type, logger=None):
    """
    작업 유형별 최적 LLM 선택

    Args:
        task_type (str): 작업 유형 (routing, generation, summarization, 기타)
        logger: Logger 인스턴스 (선택 사항)

    Returns:
        LLMClient 인스턴스
    """
    # -------------- 로깅 -------------- #
    if logger:
        logger.write(f"작업 유형별 LLM 선택: {task_type}")

    # -------------- 라우팅용 (빠른 응답) -------------- #
    if task_type == "routing":
        return LLMClient(provider="solar", model="solar-1-mini-chat", temperature=0, logger=logger)

    # -------------- 답변 생성용 (높은 정확도) -------------- #
    elif task_type == "generation":
        return LLMClient(provider="openai", model="gpt-4", temperature=0.7, logger=logger)

    # -------------- 요약용 (품질 중요) -------------- #
    elif task_type == "summarization":
        return LLMClient(provider="openai", model="gpt-4", temperature=0, logger=logger)

    # -------------- 기본값 (비용 효율) -------------- #
    else:
        return LLMClient(provider="openai", model="gpt-3.5-turbo", temperature=0.7, logger=logger)
