# main.py
"""
AI Agent 메인 실행 파일

LangGraph 기반 논문 리뷰 챗봇 AI Agent 실행:
- Agent 그래프 생성 및 컴파일
- ExperimentManager 통합
- ChatMemoryManager 대화 메모리 관리
- 테스트 질문 실행 및 결과 출력
"""

# ==================== Import ==================== #
import os
from dotenv import load_dotenv
from src.agent.graph import create_agent_graph
from src.memory.chat_history import ChatMemoryManager
from src.utils.experiment_manager import ExperimentManager

# ==================== 환경변수 로드 ==================== #
load_dotenv()  # .env 파일 로드


# ==================== 테스트 질문 리스트 ==================== #
TEST_QUESTIONS = [
    # (질문, 난이도)
    ("Transformer 모델의 핵심 개념을 설명해줘", "easy"),
    ("Attention is All You Need 논문을 요약해줘", "hard"),
    ("Self-Attention이 뭐야?", "easy"),
    ("BERT와 GPT의 차이점을 논문 검색해서 알려줘", "hard"),
    ("NLP 논문 최신 동향을 웹에서 검색해줘", "easy"),
]


# ==================== Main 함수 ==================== #
def main():
    """
    AI Agent 메인 실행 함수

    1. ExperimentManager 초기화
    2. Agent 그래프 생성
    3. ChatMemoryManager 초기화
    4. 테스트 질문 실행
    5. 결과 출력 및 로깅
    """
    print("="*80)
    print("🤖 AI Agent 시스템 시작")
    print("="*80)

    # ============================================================ #
    #                  1. ExperimentManager 초기화                 #
    # ============================================================ #
    with ExperimentManager() as exp_manager:
        exp_manager.logger.write("="*60)
        exp_manager.logger.write("AI Agent 실행 시작")
        exp_manager.logger.write("="*60)

        # ============================================================ #
        #                   2. Agent 그래프 생성                      #
        # ============================================================ #
        print("\n📊 Agent 그래프 생성 중...")
        exp_manager.logger.write("Agent 그래프 생성 시작")

        agent_executor = create_agent_graph(exp_manager=exp_manager)

        print("✅ Agent 그래프 생성 완료")
        exp_manager.logger.write("Agent 그래프 생성 완료")

        # ============================================================ #
        #                 3. ChatMemoryManager 초기화                 #
        # ============================================================ #
        print("\n💬 대화 메모리 초기화 중...")
        memory_manager = ChatMemoryManager()

        print("✅ 대화 메모리 초기화 완료")
        exp_manager.logger.write("ChatMemoryManager 초기화 완료")

        # ============================================================ #
        #                   4. 테스트 질문 실행                       #
        # ============================================================ #
        print(f"\n🧪 테스트 질문 실행 ({len(TEST_QUESTIONS)}개)")
        print("="*80)

        for idx, (question, difficulty) in enumerate(TEST_QUESTIONS, 1):
            print(f"\n[질문 {idx}/{len(TEST_QUESTIONS)}]")
            print(f"📝 질문: {question}")
            print(f"⚙️  난이도: {difficulty.upper()}")

            # ExperimentManager 로그
            exp_manager.logger.write("")
            exp_manager.logger.write("-" * 60)
            exp_manager.logger.write(f"질문 {idx}: {question}")
            exp_manager.logger.write(f"난이도: {difficulty}")

            try:
                # -------------- 대화 히스토리 가져오기 -------------- #
                chat_history = memory_manager.get_history().get("chat_history", [])

                # -------------- Agent 상태 구성 -------------- #
                initial_state = {
                    "question": question,
                    "difficulty": difficulty,
                    "messages": chat_history,
                    "tool_choice": "",
                    "tool_result": "",
                    "final_answer": ""
                }

                # -------------- Agent 실행 -------------- #
                print("⏳ Agent 실행 중...")
                exp_manager.logger.write("Agent invoke 시작")

                result = agent_executor.invoke(initial_state)

                exp_manager.logger.write("Agent invoke 완료")

                # -------------- 결과 추출 -------------- #
                final_answer = result.get("final_answer", "답변 생성 실패")
                tool_choice = result.get("tool_choice", "Unknown")

                # -------------- 결과 출력 -------------- #
                print(f"🔧 선택된 도구: {tool_choice}")
                print(f"💡 답변:\n{final_answer}")

                # ExperimentManager 로그
                exp_manager.logger.write(f"선택된 도구: {tool_choice}")
                exp_manager.logger.write(f"답변 길이: {len(final_answer)} 글자")

                # -------------- 대화 메모리에 추가 -------------- #
                memory_manager.add_user_message(question)
                memory_manager.add_ai_message(final_answer)

                exp_manager.logger.write("대화 메모리에 추가 완료")

                print("✅ 질문 처리 완료")

            except Exception as e:
                # 에러 처리
                error_msg = f"오류 발생: {str(e)}"
                print(f"❌ {error_msg}")

                exp_manager.logger.write(f"오류: {error_msg}")

        # ============================================================ #
        #                    5. 실행 결과 요약                         #
        # ============================================================ #
        print("\n" + "="*80)
        print("📊 실행 결과 요약")
        print("="*80)

        # 대화 히스토리 확인
        final_history = memory_manager.get_history()
        message_count = len(final_history.get("chat_history", []))

        print(f"✅ 총 질문 수: {len(TEST_QUESTIONS)}개")
        print(f"✅ 대화 메모리 메시지 수: {message_count}개")
        print(f"✅ 실험 로그 저장 경로: {exp_manager.experiment_dir}")

        exp_manager.logger.write("")
        exp_manager.logger.write("="*60)
        exp_manager.logger.write("AI Agent 실행 완료")
        exp_manager.logger.write(f"총 질문 수: {len(TEST_QUESTIONS)}개")
        exp_manager.logger.write(f"대화 메모리 메시지 수: {message_count}개")
        exp_manager.logger.write("="*60)

        print("\n🎉 AI Agent 시스템 종료")
        print("="*80)


# ==================== 실행 ==================== #
if __name__ == "__main__":
    main()
