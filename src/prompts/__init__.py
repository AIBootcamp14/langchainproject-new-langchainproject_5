# src/prompts/__init__.py
"""
프롬프트 모듈

프로젝트 최상위 prompts/ 폴더의 JSON 프롬프트 파일을 로드하여 제공
"""

from .loader import (
    # 라우팅 프롬프트
    load_routing_prompts,
    get_routing_prompt,
    get_few_shot_examples,

    # 도구별 프롬프트
    load_tool_prompts,
    get_tool_prompt,
    get_summarize_title_extraction_prompt,
    get_summarize_template,
    get_web_search_user_prompt_template,

    # 평가 프롬프트
    load_evaluation_prompts,
    get_evaluation_prompt_template,
    get_evaluation_input_variables,

    # 질문 생성 프롬프트
    load_question_generation_prompts,
    get_question_generation_template,
    get_question_templates,

    # Golden Dataset
    load_golden_dataset,
    get_golden_questions,
    get_golden_questions_by_tool,
    get_golden_questions_by_difficulty,
)

__all__ = [
    # 라우팅
    'load_routing_prompts',
    'get_routing_prompt',
    'get_few_shot_examples',

    # 도구별
    'load_tool_prompts',
    'get_tool_prompt',
    'get_summarize_title_extraction_prompt',
    'get_summarize_template',
    'get_web_search_user_prompt_template',

    # 평가
    'load_evaluation_prompts',
    'get_evaluation_prompt_template',
    'get_evaluation_input_variables',

    # 질문 생성
    'load_question_generation_prompts',
    'get_question_generation_template',
    'get_question_templates',

    # Golden Dataset
    'load_golden_dataset',
    'get_golden_questions',
    'get_golden_questions_by_tool',
    'get_golden_questions_by_difficulty',
]
