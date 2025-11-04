# src/agent/config_loader.py
"""
Fallback Chain 설정 로더 모듈

configs/model_config.yaml에서 Fallback Chain 설정을 로드하고,
기본값을 제공합니다.
"""

# ------------------------- 표준 라이브러리 ------------------------- #
import os
from pathlib import Path
from typing import Dict, Any, List
import yaml


# ==================== 기본 설정 ==================== #
DEFAULT_CONFIG = {
    "fallback_chain": {
        "enabled": True,
        "max_retries": 3,
        "validation_enabled": True,
        "validation_retries": 2,
        "priorities": {
            "term_definition": ["glossary", "general"],
            "paper_search": ["search_paper", "web_search", "general"],
            "latest_research": ["web_search", "search_paper", "general"],
            "paper_summary": ["summarize", "search_paper", "general"],
            "statistics": ["text2sql", "general"],
            "general_question": ["general"],
            "file_save": ["save_file"],
        }
    }
}


# ==================== 설정 캐시 ==================== #
_config_cache = None


# ==================== 설정 로더 함수 ==================== #
def load_fallback_config(force_reload: bool = False) -> Dict[str, Any]:
    """
    Fallback Chain 설정 로드

    Args:
        force_reload: 캐시 무시하고 강제로 재로드

    Returns:
        Dict[str, Any]: Fallback Chain 설정 딕셔너리
    """
    global _config_cache

    # 캐시된 설정 반환
    if _config_cache is not None and not force_reload:
        return _config_cache

    # 설정 파일 경로
    config_path = Path(__file__).parent.parent.parent / "configs" / "model_config.yaml"

    # 설정 파일이 없으면 기본값 반환
    if not config_path.exists():
        print(f"경고: 설정 파일을 찾을 수 없습니다: {config_path}")
        print("기본 설정을 사용합니다.")
        _config_cache = DEFAULT_CONFIG["fallback_chain"]
        return _config_cache

    try:
        # YAML 파일 읽기
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # fallback_chain 섹션 추출
        if config and "fallback_chain" in config:
            fallback_config = config["fallback_chain"]

            # 기본값과 병합 (누락된 키 보완)
            merged_config = _merge_with_defaults(fallback_config)

            # 설정 검증
            _validate_config(merged_config)

            # 캐시 저장
            _config_cache = merged_config
            return _config_cache
        else:
            print("경고: fallback_chain 섹션을 찾을 수 없습니다.")
            print("기본 설정을 사용합니다.")
            _config_cache = DEFAULT_CONFIG["fallback_chain"]
            return _config_cache

    except yaml.YAMLError as e:
        print(f"오류: YAML 파싱 실패: {e}")
        print("기본 설정을 사용합니다.")
        _config_cache = DEFAULT_CONFIG["fallback_chain"]
        return _config_cache

    except Exception as e:
        print(f"오류: 설정 로드 실패: {e}")
        print("기본 설정을 사용합니다.")
        _config_cache = DEFAULT_CONFIG["fallback_chain"]
        return _config_cache


def _merge_with_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    기본값과 사용자 설정 병합

    Args:
        config: 사용자 설정

    Returns:
        Dict[str, Any]: 병합된 설정
    """
    default = DEFAULT_CONFIG["fallback_chain"].copy()

    # 최상위 키 병합
    for key in ["enabled", "max_retries", "validation_enabled", "validation_retries"]:
        if key in config:
            default[key] = config[key]

    # priorities 병합
    if "priorities" in config:
        for question_type, tools in config["priorities"].items():
            default["priorities"][question_type] = tools

    return default


def _validate_config(config: Dict[str, Any]):
    """
    설정 유효성 검증

    Args:
        config: 검증할 설정

    Raises:
        ValueError: 유효하지 않은 설정
    """
    # enabled 검증
    if not isinstance(config.get("enabled"), bool):
        raise ValueError("enabled는 boolean이어야 합니다.")

    # max_retries 검증
    max_retries = config.get("max_retries")
    if not isinstance(max_retries, int) or max_retries < 1 or max_retries > 10:
        raise ValueError("max_retries는 1-10 사이의 정수여야 합니다.")

    # validation_enabled 검증
    if not isinstance(config.get("validation_enabled"), bool):
        raise ValueError("validation_enabled는 boolean이어야 합니다.")

    # validation_retries 검증
    validation_retries = config.get("validation_retries")
    if not isinstance(validation_retries, int) or validation_retries < 1 or validation_retries > 5:
        raise ValueError("validation_retries는 1-5 사이의 정수여야 합니다.")

    # priorities 검증
    priorities = config.get("priorities", {})
    if not isinstance(priorities, dict):
        raise ValueError("priorities는 딕셔너리여야 합니다.")

    # 각 우선순위 리스트 검증
    valid_tools = ["general", "glossary", "search_paper", "web_search", "summarize", "text2sql", "save_file"]

    for question_type, tools in priorities.items():
        if not isinstance(tools, list):
            raise ValueError(f"{question_type}의 우선순위는 리스트여야 합니다.")

        if len(tools) == 0:
            raise ValueError(f"{question_type}의 우선순위 리스트가 비어있습니다.")

        for tool in tools:
            if tool not in valid_tools:
                raise ValueError(f"유효하지 않은 도구: {tool} (질문 유형: {question_type})")

        # 마지막 도구는 general이어야 함 (최종 Fallback)
        # file_save와 일부 예외 제외
        if question_type not in ["file_save", "general_question"]:
            if tools[-1] != "general":
                print(f"경고: {question_type}의 마지막 도구가 'general'이 아닙니다. 최종 Fallback이 없을 수 있습니다.")


def get_priority_chain(question_type: str) -> List[str]:
    """
    질문 유형에 대한 도구 우선순위 리스트 반환

    Args:
        question_type: 질문 유형

    Returns:
        List[str]: 도구 우선순위 리스트
    """
    config = load_fallback_config()
    priorities = config.get("priorities", {})

    # 질문 유형에 해당하는 우선순위 반환
    if question_type in priorities:
        return priorities[question_type].copy()

    # 기본값: general_question 우선순위
    return priorities.get("general_question", ["general"]).copy()


def is_fallback_enabled() -> bool:
    """
    Fallback Chain 활성화 여부 반환

    Returns:
        bool: 활성화 여부
    """
    config = load_fallback_config()
    return config.get("enabled", True)


def is_validation_enabled() -> bool:
    """
    Router 검증 활성화 여부 반환

    Returns:
        bool: 활성화 여부
    """
    config = load_fallback_config()
    return config.get("validation_enabled", True)


def get_max_retries() -> int:
    """
    최대 재시도 횟수 반환

    Returns:
        int: 최대 재시도 횟수
    """
    config = load_fallback_config()
    return config.get("max_retries", 3)


def get_max_validation_retries() -> int:
    """
    최대 검증 재시도 횟수 반환

    Returns:
        int: 최대 검증 재시도 횟수
    """
    config = load_fallback_config()
    return config.get("validation_retries", 2)


def reload_config():
    """
    설정 강제 재로드
    """
    load_fallback_config(force_reload=True)
