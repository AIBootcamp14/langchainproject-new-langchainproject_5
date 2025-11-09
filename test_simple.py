"""
간단한 멀티턴 키워드 검증 테스트
"""

import os
import sys

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_contextual_keywords():
    """멀티턴 키워드 검증"""

    # contextual_keywords 리스트 (nodes.py:50-58과 동일)
    contextual_keywords = [
        # 기존 키워드
        "관련", "그거", "이거", "저거", "해당", "방금", "위", "앞서", "이전", "그",
        # 추가 키워드 (멀티턴 대화 개선)
        "이", "그럼", "그러면", "그래서", "그런", "그런데",  # 지시대명사
        "후속", "개선", "보완", "발전", "확장",  # 연구 후속 표현
        "한계", "문제점", "단점", "장점", "기여",  # 논문 분석 표현
        "차이", "비교", "공통점", "다른점"  # 비교 표현
    ]

    test_cases = [
        # (질문, 메시지 개수, 예상 has_contextual_ref, 예상 skip_pattern)
        ("BERT의 한계점은 뭐야?", 0, True, False),  # 첫 질문, "한계" 키워드, 패턴 매칭 진행
        ("이 논문의 한계점은 뭐야?", 2, True, True),  # 멀티턴, "이"+"한계" 키워드, 패턴 스킵
        ("개선한 후속 연구 있어?", 2, True, True),  # 멀티턴, "개선"+"후속" 키워드, 패턴 스킵
        ("Transformer 논문 요약해줘", 0, False, False),  # 첫 질문, 키워드 없음, 패턴 매칭
        ("BERT와 GPT의 차이점은?", 0, True, False),  # 첫 질문, "차이" 키워드, 패턴 매칭
    ]

    print("\n" + "="*80)
    print("멀티턴 키워드 검증 테스트")
    print("="*80 + "\n")

    all_pass = True

    for question, num_messages, expected_ref, expected_skip in test_cases:
        has_contextual_ref = any(kw in question for kw in contextual_keywords)
        skip_pattern_matching = has_contextual_ref and num_messages > 1

        # 결과 출력
        status_ref = "✅" if has_contextual_ref == expected_ref else "❌"
        status_skip = "✅" if skip_pattern_matching == expected_skip else "❌"

        print(f"질문: {question}")
        print(f"  메시지 개수: {num_messages}")
        print(f"  {status_ref} has_contextual_ref: {has_contextual_ref} (예상: {expected_ref})")
        print(f"  {status_skip} skip_pattern_matching: {skip_pattern_matching} (예상: {expected_skip})")

        if has_contextual_ref != expected_ref or skip_pattern_matching != expected_skip:
            all_pass = False
            print(f"  ❌ FAIL")
        else:
            print(f"  ✅ PASS")
        print()

    print("="*80)
    if all_pass:
        print("✅ 모든 테스트 통과")
    else:
        print("❌ 일부 테스트 실패")
    print("="*80 + "\n")

    return all_pass


if __name__ == "__main__":
    test_contextual_keywords()
