#!/usr/bin/env python
# test_summarize.py
"""
논문 요약 기능 테스트 스크립트
"""

import os
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.graph import create_agent_graph
from src.utils.experiment_manager import ExperimentManager

def test_bert_summarize():
    """BERT 논문 요약 테스트"""
    print("=" * 80)
    print("테스트: BERT 논문 요약 기능")
    print("=" * 80)

    # ExperimentManager 생성
    exp_manager = ExperimentManager()
    print(f"\n실험 폴더: {exp_manager.experiment_dir}")

    # Agent 생성
    print("\nAgent 생성 중...")
    agent_executor = create_agent_graph(exp_manager=exp_manager)

    # 테스트 질문
    question = "BERT 논문의 방법론 부분만 요약해줘"
    print(f"\n질문: {question}")
    print("\nAgent 실행 중...\n")

    try:
        # Agent 실행
        response = agent_executor.invoke({
            "question": question,
            "difficulty": "easy",
            "messages": []
        })

        print("\n" + "=" * 80)
        print("결과")
        print("=" * 80)

        # 도구 선택
        tool_choice = response.get("tool_choice", "unknown")
        print(f"\n선택된 도구: {tool_choice}")

        # 최종 답변
        final_answer = response.get("final_answer", "답변 없음")
        print(f"\n최종 답변:\n{final_answer}")

        # 성공 여부 확인
        if "오류" in final_answer or "실패" in final_answer:
            print("\n❌ 테스트 실패!")
            return False
        else:
            print("\n✅ 테스트 성공!")
            return True

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bert_summarize()
    sys.exit(0 if success else 1)
