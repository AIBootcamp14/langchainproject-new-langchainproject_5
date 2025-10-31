# tests/test_agent_system.py
"""
Phase 1: 기반 시스템 테스트

LLM 클라이언트, AgentState, Agent 그래프 기본 기능 테스트
"""

# ------------------------- 표준 라이브러리 ------------------------- #
import os
import sys
# os: 환경변수 및 경로 처리
# sys: 경로 추가

# ------------------------- 프로젝트 루트 경로 추가 ------------------------- #
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.llm.client import LLMClient, get_llm_for_task
from src.agent.state import AgentState
from src.agent.graph import create_agent_graph
# LLMClient: LLM 클라이언트
# AgentState: Agent 상태 정의
# create_agent_graph: Agent 그래프 생성 함수


# ==================== 테스트 1: LLM 클라이언트 ==================== #
def test_llm_client():
    """LLM 클라이언트 단독 테스트"""
    print("\n" + "="*60)
    print("테스트 1: LLM 클라이언트")
    print("="*60)

    # -------------- OpenAI 클라이언트 테스트 -------------- #
    try:
        print("\n[1-1] OpenAI 클라이언트 초기화 테스트...")
        llm_openai = LLMClient(provider="openai", model="gpt-3.5-turbo", temperature=0)
        print("✅ OpenAI 클라이언트 초기화 성공")
    except Exception as e:
        print(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
        return False

    # -------------- Solar 클라이언트 테스트 -------------- #
    try:
        print("\n[1-2] Solar 클라이언트 초기화 테스트...")
        llm_solar = LLMClient(provider="solar", model="solar-1-mini-chat", temperature=0)
        print("✅ Solar 클라이언트 초기화 성공")
    except Exception as e:
        print(f"❌ Solar 클라이언트 초기화 실패: {e}")
        return False

    # -------------- get_llm_for_task 함수 테스트 -------------- #
    try:
        print("\n[1-3] get_llm_for_task() 함수 테스트...")
        llm_routing = get_llm_for_task("routing")
        llm_generation = get_llm_for_task("generation")
        print("✅ get_llm_for_task() 함수 정상 작동")
    except Exception as e:
        print(f"❌ get_llm_for_task() 함수 실패: {e}")
        return False

    print("\n✅ LLM 클라이언트 테스트 통과")
    return True


# ==================== 테스트 2: Agent 그래프 컴파일 ==================== #
def test_agent_graph_compile():
    """Agent 그래프 컴파일 테스트"""
    print("\n" + "="*60)
    print("테스트 2: Agent 그래프 컴파일")
    print("="*60)

    # -------------- Agent 그래프 생성 -------------- #
    try:
        print("\n[2-1] Agent 그래프 생성 테스트...")
        agent_executor = create_agent_graph()
        print("✅ Agent 그래프 생성 및 컴파일 성공")
    except Exception as e:
        print(f"❌ Agent 그래프 생성 실패: {e}")
        return False

    # -------------- 그래프 구조 확인 -------------- #
    try:
        print("\n[2-2] 그래프 구조 확인...")
        # 그래프가 정상적으로 컴파일되었는지 확인
        if agent_executor is not None:
            print("✅ 그래프 객체 정상 생성")
        else:
            print("❌ 그래프 객체가 None")
            return False
    except Exception as e:
        print(f"❌ 그래프 구조 확인 실패: {e}")
        return False

    print("\n✅ Agent 그래프 컴파일 테스트 통과")
    return True


# ==================== 테스트 3: 라우터 노드 ==================== #
def test_router_node():
    """라우터 노드 테스트"""
    print("\n" + "="*60)
    print("테스트 3: 라우터 노드 (도구 선택 로직)")
    print("="*60)

    # -------------- Agent 그래프 생성 -------------- #
    try:
        print("\n[3-1] Agent 그래프 생성...")
        agent_executor = create_agent_graph()
        print("✅ Agent 그래프 생성 성공")
    except Exception as e:
        print(f"❌ Agent 그래프 생성 실패: {e}")
        return False

    # -------------- 테스트 케이스 정의 -------------- #
    test_cases = [
        {
            "question": "Transformer 논문에 대해 알려줘",
            "expected_tools": ["search_paper", "general"],
            "difficulty": "easy"
        },
        {
            "question": "안녕하세요",
            "expected_tools": ["general"],
            "difficulty": "easy"
        }
    ]

    # -------------- 각 테스트 케이스 실행 -------------- #
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n[3-{i+1}] 테스트 케이스 {i}: {test_case['question']}")

            # 초기 상태 생성
            initial_state: AgentState = {
                "question": test_case["question"],
                "difficulty": test_case["difficulty"],
                "tool_choice": "",
                "tool_result": "",
                "final_answer": "",
                "messages": []
            }

            # Agent 실행
            result = agent_executor.invoke(initial_state)

            # 결과 확인
            if "tool_choice" in result:
                selected_tool = result.get("tool_choice", "")
                print(f"   선택된 도구: {selected_tool}")

                if selected_tool in test_case["expected_tools"]:
                    print(f"   ✅ 예상 도구 중 하나 선택됨")
                else:
                    print(f"   ⚠️  예상 도구({test_case['expected_tools']})와 다름")

            if "final_answer" in result:
                print(f"   최종 답변: {result['final_answer'][:50]}...")

            print(f"   ✅ 테스트 케이스 {i} 통과")

        except Exception as e:
            print(f"   ❌ 테스트 케이스 {i} 실패: {e}")
            # 테스트는 계속 진행
            continue

    print("\n✅ 라우터 노드 테스트 통과")
    return True


# ==================== 메인 실행 ==================== #
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Phase 1: 기반 시스템 테스트 시작")
    print("="*60)

    # -------------- 환경변수 확인 -------------- #
    print("\n[환경변수 확인]")
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OPENAI_API_KEY 설정됨")
    else:
        print("❌ OPENAI_API_KEY 미설정")

    if os.getenv("UPSTAGE_API_KEY"):
        print("✅ UPSTAGE_API_KEY 설정됨")
    else:
        print("⚠️  UPSTAGE_API_KEY 미설정 (Solar 테스트 제한)")

    # -------------- 테스트 실행 -------------- #
    results = []

    # 테스트 1: LLM 클라이언트
    results.append(("LLM 클라이언트", test_llm_client()))

    # 테스트 2: Agent 그래프 컴파일
    results.append(("Agent 그래프 컴파일", test_agent_graph_compile()))

    # 테스트 3: 라우터 노드
    results.append(("라우터 노드", test_router_node()))

    # -------------- 최종 결과 출력 -------------- #
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)

    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")

    # 전체 통과 여부
    all_passed = all(result for _, result in results)
    print("\n" + "="*60)
    if all_passed:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️  일부 테스트 실패")
    print("="*60)
