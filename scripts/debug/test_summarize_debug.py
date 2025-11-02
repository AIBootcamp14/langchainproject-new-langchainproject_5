#!/usr/bin/env python
"""논문 요약 기능 디버그 테스트"""

import os
import sys
import traceback
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent.graph import create_agent_graph
from src.utils.experiment_manager import ExperimentManager

def test_bert_summarize():
    exp_manager = ExperimentManager()
    agent_executor = create_agent_graph(exp_manager=exp_manager)

    question = "BERT 논문의 방법론 부분만 요약해줘"

    try:
        response = agent_executor.invoke({
            "question": question,
            "difficulty": "easy",
            "messages": []
        })

        print("성공!")
        print(response.get("final_answer", ""))

    except Exception as e:
        print(f"오류 발생: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_bert_summarize()
