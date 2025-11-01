# src/utils/config_loader.py

"""
설정 파일 로더 모듈

YAML 설정 파일을 로드하고 환경 변수를 치환하여 반환합니다.
"""

# ==================================================================================== #
#                                   IMPORT MODULES                                     #
# ==================================================================================== #

# ------------------------- 표준 라이브러리 ------------------------- #
import os
import re
from typing import Dict, Any

# ------------------------- 서드파티 라이브러리 ------------------------- #
import yaml
from dotenv import load_dotenv


# ==================================================================================== #
#                                ENVIRONMENT LOADING                                   #
# ==================================================================================== #

# .env 파일 로드 (프로젝트 루트 기준)
load_dotenv()


# ==================================================================================== #
#                               CONFIG LOADER CLASS                                    #
# ==================================================================================== #

class ConfigLoader:
    """
    YAML 설정 파일 로더 클래스

    환경 변수(${VAR_NAME}) 형태를 실제 값으로 치환하여 설정을 로드합니다.
    """

    def __init__(self, config_dir: str = "configs"):
        """
        ConfigLoader 초기화

        Args:
            config_dir: 설정 파일 디렉토리 경로 (기본값: "configs")
        """
        self.config_dir = config_dir

    # ---------------------- 환경 변수 치환 ---------------------- #
    def _replace_env_vars(self, value: Any) -> Any:
        """
        값에 포함된 환경 변수 ${VAR_NAME}를 실제 값으로 치환

        Args:
            value: 원본 값 (str, dict, list 등)

        Returns:
            환경 변수가 치환된 값
        """
        if isinstance(value, str):
            # ${VAR_NAME} 패턴 찾기
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, value)

            # 각 환경 변수를 실제 값으로 치환
            for var_name in matches:
                env_value = os.getenv(var_name, '')
                value = value.replace(f'${{{var_name}}}', env_value)

            return value

        elif isinstance(value, dict):
            # 딕셔너리의 모든 값에 재귀 적용
            return {k: self._replace_env_vars(v) for k, v in value.items()}

        elif isinstance(value, list):
            # 리스트의 모든 항목에 재귀 적용
            return [self._replace_env_vars(item) for item in value]

        else:
            # 그 외 타입은 그대로 반환
            return value

    # ---------------------- YAML 파일 로드 ---------------------- #
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        YAML 파일 로드 및 환경 변수 치환

        Args:
            filename: YAML 파일명 (예: "db_config.yaml")

        Returns:
            환경 변수가 치환된 설정 딕셔너리

        Raises:
            FileNotFoundError: YAML 파일이 없는 경우
            yaml.YAMLError: YAML 파싱 오류
        """
        file_path = os.path.join(self.config_dir, filename)

        # YAML 파일 로드
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 환경 변수 치환
        config = self._replace_env_vars(config)

        return config

    # ---------------------- 데이터베이스 설정 로드 ---------------------- #
    def load_db_config(self) -> Dict[str, Any]:
        """
        데이터베이스 설정 로드 (db_config.yaml)

        Returns:
            데이터베이스 설정 딕셔너리
        """
        return self.load_yaml("db_config.yaml")

    # ---------------------- LLM 모델 설정 로드 ---------------------- #
    def load_model_config(self) -> Dict[str, Any]:
        """
        LLM 모델 설정 로드 (model_config.yaml)

        Returns:
            모델 설정 딕셔너리
        """
        return self.load_yaml("model_config.yaml")

    # ---------------------- 프롬프트 설정 로드 ---------------------- #
    def load_prompt_config(self) -> Dict[str, Any]:
        """
        프롬프트 설정 로드 (prompt_config.yaml)

        Returns:
            프롬프트 설정 딕셔너리
        """
        return self.load_yaml("prompt_config.yaml")

    # ---------------------- PostgreSQL 연결 문자열 생성 ---------------------- #
    def get_postgres_connection_string(self) -> str:
        """
        PostgreSQL 연결 문자열 생성

        Returns:
            PostgreSQL 연결 문자열
            예: "postgresql://langchain:password@localhost:5432/papers"
        """
        db_config = self.load_db_config()
        pg_config = db_config['postgresql']

        connection_string = (
            f"postgresql://"
            f"{pg_config['user']}:{pg_config['password']}"
            f"@{pg_config['host']}:{pg_config['port']}"
            f"/{pg_config['database']}"
        )

        return connection_string


# ==================================================================================== #
#                                GLOBAL INSTANCE                                       #
# ==================================================================================== #

# 전역 ConfigLoader 인스턴스
config_loader = ConfigLoader()


# ==================================================================================== #
#                                HELPER FUNCTIONS                                      #
# ==================================================================================== #

def get_db_config() -> Dict[str, Any]:
    """
    데이터베이스 설정 가져오기 (간편 함수)

    Returns:
        데이터베이스 설정 딕셔너리
    """
    return config_loader.load_db_config()


def get_model_config() -> Dict[str, Any]:
    """
    LLM 모델 설정 가져오기 (간편 함수)

    Returns:
        모델 설정 딕셔너리
    """
    return config_loader.load_model_config()


def get_prompt_config() -> Dict[str, Any]:
    """
    프롬프트 설정 가져오기 (간편 함수)

    Returns:
        프롬프트 설정 딕셔너리
    """
    return config_loader.load_prompt_config()


def get_postgres_connection_string() -> str:
    """
    PostgreSQL 연결 문자열 가져오기 (간편 함수)

    Returns:
        PostgreSQL 연결 문자열
    """
    return config_loader.get_postgres_connection_string()


# ==================================================================================== #
#                                    MAIN TEST                                         #
# ==================================================================================== #

if __name__ == "__main__":
    # ConfigLoader 테스트

    print("=" * 70)
    print("ConfigLoader 테스트")
    print("=" * 70)

    # 데이터베이스 설정 로드
    db_config = get_db_config()
    print("\n[데이터베이스 설정]")
    print(f"Host: {db_config['postgresql']['host']}")
    print(f"Port: {db_config['postgresql']['port']}")
    print(f"Database: {db_config['postgresql']['database']}")
    print(f"User: {db_config['postgresql']['user']}")

    # PostgreSQL 연결 문자열
    connection_string = get_postgres_connection_string()
    print(f"\n[PostgreSQL 연결 문자열]")
    print(connection_string)

    # 모델 설정 로드
    model_config = get_model_config()
    print(f"\n[LLM 모델 설정]")
    print(f"개발 모델: {model_config['llm']['development']['model']}")
    print(f"프로덕션 모델: {model_config['llm']['production']['model']}")
    print(f"임베딩 모델: {model_config['embeddings']['model']}")

    print("\n" + "=" * 70)
    print("✅ ConfigLoader 테스트 완료")
    print("=" * 70)
