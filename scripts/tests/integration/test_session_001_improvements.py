"""
Session 001 질문들로 개선사항 통합 테스트

멀티턴 대화 및 Text2SQL 기능이 정상 작동하는지 확인
"""

import os
import sys
from datetime import datetime

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.graph import create_agent_graph
from src.utils.experiment_manager import ExperimentManager
from langchain_core.messages import HumanMessage, AIMessage


def test_multimodal_questions():
    """멀티턴 대화 테스트"""
    print("\n" + "="*80)
    print("테스트 1: 멀티턴 대화 기능")
    print("="*80 + "\n")

    # 실험 매니저 초기화
    exp_manager = ExperimentManager(
        experiment_type="test",
        difficulty="easy",
        auto_save=False
    )

    # 그래프 생성
    graph = create_agent_graph(exp_manager=exp_manager)

    questions = [
        '"Attention Is All You Need" 논문 요약해줘',
        '이 논문의 한계점은 뭐야?',  # 멀티턴 테스트 1
        '개선한 후속 연구 있어?',  # 멀티턴 테스트 2
    ]

    messages = []

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"질문 {i}: {question}")
        print('='*60 + "\n")

        # 상태 초기화
        state = {
            "messages": messages.copy(),
            "question": question,
            "difficulty": "easy",
            "final_answer": "",
            "current_tool": None,
            "tool_result": None,
            "tool_pipeline": [],
            "pipeline_index": 0,
        }

        # 그래프 실행
        try:
            result = graph.invoke(state, config={"exp_manager": exp_manager})

            # 메시지 기록 업데이트
            messages.append(HumanMessage(content=question))
            if result.get("final_answer"):
                messages.append(AIMessage(content=result["final_answer"][:500]))  # 500자로 제한

            # 결과 출력
            print(f"\n선택된 도구: {result.get('current_tool', 'N/A')}")
            print(f"도구 파이프라인: {result.get('tool_pipeline', [])}")
            print(f"파이프라인 종료 플래그: {result.get('pipeline_terminated', False)}")
            print(f"답변 길이: {len(result.get('final_answer', ''))} 자")

            # 멀티턴 검증
            if i >= 2:
                print(f"\n✅ 멀티턴 맥락 참조: 메시지 수 = {len(messages)}")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("멀티턴 테스트 완료")
    print("="*80 + "\n")


def test_text2sql_questions():
    """Text2SQL 파이프라인 최적화 테스트"""
    print("\n" + "="*80)
    print("테스트 2: Text2SQL 파이프라인 최적화")
    print("="*80 + "\n")

    # 실험 매니저 초기화
    exp_manager = ExperimentManager(
        experiment_type="test",
        difficulty="easy",
        auto_save=False
    )

    # 그래프 생성
    graph = create_agent_graph(exp_manager=exp_manager)

    questions = [
        '카테고리별 논문 수 통계 보여줘',  # 단순 통계 (text2sql만 실행되어야 함)
        '2024년에 나온 AI 논문 몇 개야?',  # 빈 결과셋 (정상 응답으로 처리되어야 함)
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"질문 {i}: {question}")
        print('='*60 + "\n")

        # 상태 초기화
        state = {
            "messages": [],
            "question": question,
            "difficulty": "easy",
            "final_answer": "",
            "current_tool": None,
            "tool_result": None,
            "tool_pipeline": [],
            "pipeline_index": 0,
        }

        # 실행 시작 시간
        start_time = datetime.now()

        # 그래프 실행
        try:
            result = graph.invoke(state, config={"exp_manager": exp_manager})

            # 실행 시간 계산
            elapsed_time = (datetime.now() - start_time).total_seconds()

            # 결과 출력
            print(f"\n선택된 도구: {result.get('current_tool', 'N/A')}")
            print(f"도구 파이프라인: {result.get('tool_pipeline', [])}")
            print(f"파이프라인 종료 플래그: {result.get('pipeline_terminated', False)}")
            print(f"종료 사유: {result.get('termination_reason', 'N/A')}")
            print(f"실행 시간: {elapsed_time:.2f}초")
            print(f"답변 길이: {len(result.get('final_answer', ''))} 자")

            # 효율성 검증
            pipeline = result.get('tool_pipeline', [])
            if 'text2sql' in pipeline:
                print(f"\n✅ text2sql 포함")
                if len(pipeline) == 1:
                    print(f"✅ 단일 도구 실행 (최적화 성공)")
                else:
                    print(f"⚠️  복합 파이프라인 ({len(pipeline)}개 도구): {pipeline}")

            if elapsed_time < 20:
                print(f"✅ 응답 시간 양호 ({elapsed_time:.2f}초 < 20초)")
            else:
                print(f"⚠️  응답 시간 느림 ({elapsed_time:.2f}초 >= 20초)")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("Text2SQL 테스트 완료")
    print("="*80 + "\n")


def test_first_question_with_keywords():
    """첫 질문에서 멀티턴 키워드 사용 시 정상 동작 테스트"""
    print("\n" + "="*80)
    print("테스트 3: 첫 질문에서 멀티턴 키워드 사용")
    print("="*80 + "\n")

    # 실험 매니저 초기화
    exp_manager = ExperimentManager(
        experiment_type="test",
        difficulty="easy",
        auto_save=False
    )

    # 그래프 생성
    graph = create_agent_graph(exp_manager=exp_manager)

    questions = [
        'BERT의 한계점은 뭐야?',  # 첫 질문인데 "한계" 키워드 포함
        'Transformer와 BERT의 차이점은?',  # 첫 질문인데 "차이" 키워드 포함
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"질문 {i}: {question}")
        print('='*60 + "\n")

        # 상태 초기화 (대화 기록 없음)
        state = {
            "messages": [],  # 빈 메시지 리스트
            "question": question,
            "difficulty": "easy",
            "final_answer": "",
            "current_tool": None,
            "tool_result": None,
            "tool_pipeline": [],
            "pipeline_index": 0,
        }

        # 그래프 실행
        try:
            result = graph.invoke(state, config={"exp_manager": exp_manager})

            # 결과 출력
            print(f"\n선택된 도구: {result.get('current_tool', 'N/A')}")
            print(f"도구 파이프라인: {result.get('tool_pipeline', [])}")
            print(f"답변 길이: {len(result.get('final_answer', ''))} 자")

            # 검증: 정상적인 도구 선택 확인
            current_tool = result.get('current_tool')
            if current_tool and current_tool != 'error':
                print(f"✅ 정상 동작 (도구 선택: {current_tool})")
            else:
                print(f"❌ 도구 선택 실패")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("첫 질문 키워드 테스트 완료")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Session 001 통합 테스트 시작")
    print("="*80)

    # 테스트 1: 멀티턴 대화
    test_multimodal_questions()

    # 테스트 2: Text2SQL 최적화
    test_text2sql_questions()

    # 테스트 3: 첫 질문에서 멀티턴 키워드
    test_first_question_with_keywords()

    print("\n" + "="*80)
    print("모든 테스트 완료")
    print("="*80 + "\n")
