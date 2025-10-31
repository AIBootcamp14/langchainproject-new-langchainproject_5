# src/tools/save_file.py
"""
파일 저장 도구 모듈

답변 내용을 파일로 저장
타임스탬프 기반 파일명 생성
"""

# ==================== Import ==================== #
from datetime import datetime
import os
from src.agent.state import AgentState


# ==================== 도구 2: 파일 저장 노드 ==================== #
def save_file_node(state: AgentState, exp_manager=None):
    """
    파일 저장 노드: 답변 내용을 파일로 저장

    Args:
        state (AgentState): Agent 상태
        exp_manager: ExperimentManager 인스턴스 (선택 사항)

    Returns:
        AgentState: 업데이트된 상태
    """
    # -------------- 상태에서 질문 추출 -------------- #
    question = state["question"]                # 사용자 질문

    # -------------- 로깅 -------------- #
    if exp_manager:
        exp_manager.logger.write(f"파일 저장 노드 실행: {question}")

    # -------------- 저장할 내용 확인 -------------- #
    # 이전 답변이 있으면 그것을 저장, 없으면 대화 히스토리 저장
    content_to_save = state.get("tool_result") or state.get("final_answer") or "저장할 내용이 없습니다."

    if exp_manager:
        exp_manager.logger.write(f"저장할 내용 길이: {len(content_to_save)} 글자")

    # -------------- 파일명 생성 -------------- #
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 타임스탬프 생성
    filename = f"response_{timestamp}.txt"      # 파일명 구성

    if exp_manager:
        exp_manager.logger.write(f"파일명: {filename}")

    # -------------- 파일 저장 -------------- #
    if exp_manager:
        # ExperimentManager의 save_output 메서드 사용
        file_path = exp_manager.save_output(filename, content_to_save)  # 파일 저장

        exp_manager.logger.write(f"파일 저장 완료: {file_path}")

        # 성공 메시지 구성
        answer = f"파일이 성공적으로 저장되었습니다.\n파일 경로: {file_path}"
    else:
        # ExperimentManager 없을 때 (테스트 환경)
        output_dir = "outputs"                  # 기본 출력 디렉토리
        os.makedirs(output_dir, exist_ok=True)  # 디렉토리 생성
        file_path = os.path.join(output_dir, filename)  # 파일 경로 생성

        # 파일 쓰기
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_to_save)            # 내용 저장

        # 성공 메시지 구성
        answer = f"파일이 성공적으로 저장되었습니다.\n파일 경로: {file_path}"

    # -------------- 최종 답변 저장 -------------- #
    state["final_answer"] = answer              # 성공 메시지 저장

    return state                                # 업데이트된 상태 반환
