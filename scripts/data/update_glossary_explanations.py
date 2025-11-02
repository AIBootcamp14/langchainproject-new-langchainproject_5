#!/usr/bin/env python3
"""
용어집 설명 업데이트 스크립트

설명이 없는 용어들에 대해 easy_explanation과 hard_explanation을 추가합니다.
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
load_dotenv()

import psycopg2


# 용어별 설명 데이터
TERM_EXPLANATIONS = {
    "Attention Mechanism": {
        "easy": "중요한 정보에 더 집중하는 기술입니다. 예를 들어, 긴 문장을 번역할 때 지금 번역하는 단어와 관련된 부분에만 집중하는 것처럼 동작합니다. 마치 사람이 책을 읽을 때 중요한 부분에 형광펜을 긋는 것과 비슷합니다.",
        "hard": "입력 시퀀스의 각 위치에 대해 중요도 가중치를 학습하여, 출력 생성 시 관련성이 높은 정보에 선택적으로 집중하는 메커니즘입니다. Query, Key, Value 벡터 간의 내적을 통해 유사도를 계산하고, Softmax를 적용하여 가중치를 정규화합니다. Transformer 아키텍처의 핵심 구성 요소로, Self-Attention과 Cross-Attention 방식이 있습니다."
    },

    "BLEU Score": {
        "easy": "기계번역이나 AI가 만든 문장이 실제 사람이 만든 문장과 얼마나 비슷한지 점수로 나타낸 것입니다. 0점부터 100점까지 있으며, 점수가 높을수록 더 좋은 번역이라는 뜻입니다. 주로 기계번역 품질을 평가할 때 사용합니다.",
        "hard": "Bilingual Evaluation Understudy의 약자로, n-gram precision을 기반으로 기계 생성 텍스트와 참조 텍스트 간의 유사도를 정량적으로 평가하는 지표입니다. 1-gram부터 4-gram까지의 precision을 기하평균하고, Brevity Penalty를 적용하여 짧은 문장에 대한 편향을 보정합니다. 값의 범위는 0~1이며, 일반적으로 0.3 이상이면 양호한 번역으로 간주됩니다."
    },

    "Controllable Text Generation": {
        "easy": "AI가 텍스트를 생성할 때, 특정 스타일이나 톤으로 글을 쓰도록 조절하는 기술입니다. 예를 들어, '공손하게', '유머러스하게', 또는 '전문적으로' 같은 스타일을 지정하면 그에 맞게 텍스트를 생성합니다. 마치 작가에게 '이런 느낌으로 써주세요'라고 요청하는 것과 비슷합니다.",
        "hard": "사용자가 지정한 속성(감정, 톤, 스타일, 주제 등)에 따라 텍스트 생성을 제어하는 NLP 기술입니다. CTRL(Conditional Transformer Language), PPLM(Plug and Play Language Models) 등의 방법론이 있으며, 조건부 확률 분포 P(text|condition)을 최적화하여 구현합니다. Prompt Engineering, Fine-tuning, Latent Code Manipulation 등 다양한 제어 메커니즘이 활용됩니다."
    },

    "Distillation": {
        "easy": "큰 AI 모델의 지식을 작은 모델로 옮겨 담는 기술입니다. 큰 모델(선생님)이 학습한 내용을 작은 모델(학생)에게 가르쳐서, 작은 모델도 비슷한 성능을 내도록 만듭니다. 이렇게 하면 속도는 빠르면서도 성능은 유지할 수 있습니다.",
        "hard": "Knowledge Distillation은 Teacher 모델의 출력 분포(Soft Targets)를 Student 모델이 모방하도록 학습하는 모델 압축 기법입니다. Temperature Scaling을 통해 Softmax 출력을 부드럽게 만들고, KL Divergence Loss를 최소화합니다. DistilBERT, TinyBERT 등이 대표적 사례이며, 파라미터 수를 40~60% 감소시키면서도 성능 저하를 2~5% 이내로 제한할 수 있습니다."
    },

    "Fine-tuning": {
        "easy": "이미 학습된 AI 모델을 특정 작업에 맞게 추가로 학습시키는 과정입니다. 예를 들어, 일반적인 언어 모델을 의료 분야 문서 분석에 특화되도록 다시 학습시키는 것입니다. 처음부터 학습하는 것보다 훨씬 빠르고 효율적입니다.",
        "hard": "사전학습된 모델의 파라미터를 특정 다운스트림 태스크에 맞게 재조정하는 전이학습 기법입니다. Learning Rate는 사전학습 시보다 낮게(1e-5 ~ 5e-5) 설정하며, 전체 파라미터를 업데이트하는 Full Fine-tuning과 일부만 업데이트하는 Adapter-based, LoRA(Low-Rank Adaptation) 등의 Parameter-Efficient Fine-Tuning(PEFT) 방식이 있습니다. Catastrophic Forgetting을 방지하기 위해 Regularization 기법을 적용합니다."
    },

    "LLM (Large Language Model)": {
        "easy": "방대한 양의 텍스트 데이터로 학습한 거대한 AI 언어 모델입니다. GPT, BERT 같은 모델이 대표적이며, 문장 생성, 번역, 요약, 질문 답변 등 다양한 언어 작업을 수행할 수 있습니다. 마치 수백만 권의 책을 읽은 AI 비서와 같습니다.",
        "hard": "수십억~수조 개의 파라미터를 가진 대규모 신경망 언어 모델로, Transformer 아키텍처를 기반으로 방대한 말뭉치(Corpus)에서 자기지도 학습(Self-Supervised Learning)을 수행합니다. GPT-3(175B), PaLM(540B), GPT-4(추정 1.7T) 등이 있으며, In-Context Learning, Few-Shot Learning, Chain-of-Thought Reasoning 등의 Emergent Abilities를 보입니다. Pre-training 단계에서 언어의 통계적 패턴을 학습하고, Fine-tuning 또는 RLHF(Reinforcement Learning from Human Feedback)를 통해 특정 태스크에 최적화됩니다."
    },

    "LLM(Large Language Model)": {  # 중복 용어
        "easy": "방대한 양의 텍스트 데이터로 학습한 거대한 AI 언어 모델입니다. GPT, BERT 같은 모델이 대표적이며, 문장 생성, 번역, 요약, 질문 답변 등 다양한 언어 작업을 수행할 수 있습니다. 마치 수백만 권의 책을 읽은 AI 비서와 같습니다.",
        "hard": "수십억~수조 개의 파라미터를 가진 대규모 신경망 언어 모델로, Transformer 아키텍처를 기반으로 방대한 말뭉치(Corpus)에서 자기지도 학습(Self-Supervised Learning)을 수행합니다. GPT-3(175B), PaLM(540B), GPT-4(추정 1.7T) 등이 있으며, In-Context Learning, Few-Shot Learning, Chain-of-Thought Reasoning 등의 Emergent Abilities를 보입니다. Pre-training 단계에서 언어의 통계적 패턴을 학습하고, Fine-tuning 또는 RLHF(Reinforcement Learning from Human Feedback)를 통해 특정 태스크에 최적화됩니다."
    },

    "Mixture of Experts (MoE)": {
        "easy": "여러 개의 전문가(작은 모델들)를 두고, 입력에 따라 필요한 전문가만 활성화하는 효율적인 AI 구조입니다. 예를 들어, 수학 문제는 수학 전문가가, 역사 질문은 역사 전문가가 답하는 방식입니다. 모든 전문가를 항상 사용하지 않아 계산이 빠릅니다.",
        "hard": "다수의 Expert 네트워크와 Gating Network로 구성된 조건부 계산(Conditional Computation) 아키텍처입니다. Gating Network는 입력에 따라 상위 K개의 Expert를 선택하고, 각 Expert의 출력을 가중 평균하여 최종 결과를 생성합니다. Switch Transformer, GLaM 등이 대표적이며, 밀집 모델 대비 파라미터 수는 증가하지만 FLOPs는 일정하게 유지하여 효율성을 극대화합니다. Load Balancing Loss를 통해 Expert 활용도를 균등하게 조절합니다."
    },

    "Open-Domain Knowledge Extraction": {
        "easy": "특정 분야에 국한되지 않고, 다양한 주제의 텍스트에서 자동으로 지식을 추출하는 기술입니다. 예를 들어, 뉴스, 블로그, 논문 등에서 인물, 장소, 사건 관계 등을 자동으로 찾아내는 것입니다.",
        "hard": "도메인 제약 없이 웹 텍스트, 문서 등 비구조화 데이터에서 개체(Entity), 관계(Relation), 사실(Fact)을 자동 추출하는 정보 추출(Information Extraction) 기술입니다. Named Entity Recognition(NER), Relation Extraction(RE), Open Information Extraction(Open IE) 등의 기법을 활용하며, Knowledge Graph 구축의 핵심 요소입니다. BERT, GPT 등 LLM을 활용한 Zero-shot/Few-shot 추출 방식이 최근 주목받고 있습니다."
    },

    "Pruning": {
        "easy": "AI 모델에서 불필요한 부분을 제거하여 크기를 줄이는 기술입니다. 나무를 가지치기하듯 중요하지 않은 연결이나 뉴런을 제거해서 모델을 가볍게 만듭니다. 이렇게 하면 속도는 빠르면서 성능은 거의 유지됩니다.",
        "hard": "신경망의 중요도가 낮은 가중치, 뉴런, 또는 레이어를 제거하여 모델 크기와 계산 복잡도를 감소시키는 모델 압축 기법입니다. Magnitude-based Pruning(가중치 절댓값 기준), Structured Pruning(전체 필터/채널 제거), Unstructured Pruning(개별 가중치 제거) 등의 방식이 있습니다. Lottery Ticket Hypothesis에 따르면, 큰 네트워크 내에는 처음부터 좋은 성능을 내는 부분 네트워크(Winning Ticket)가 존재합니다. Iterative Magnitude Pruning(IMP)을 통해 50~90% 파라미터를 제거해도 성능 유지가 가능합니다."
    },

    "밀집(Dense) 모델": {
        "easy": "모든 부분을 항상 사용하는 전통적인 AI 모델입니다. 입력이 무엇이든 모델의 모든 뉴런과 연결이 계산에 참여합니다. 성능은 좋지만, 큰 모델일수록 계산 비용이 많이 듭니다.",
        "hard": "모든 파라미터가 매 추론마다 활성화되는 전통적인 신경망 아키텍처로, Feed-Forward 계층의 모든 뉴런이 입력과 무관하게 계산에 참여합니다. BERT, GPT-3 등 대부분의 Transformer 모델이 Dense 구조를 따르며, 모델 크기에 비례하여 FLOPs가 증가합니다. Sparse 모델(MoE 등)과 대비되는 개념으로, 계산 효율성은 낮지만 구현이 단순하고 안정적입니다."
    },

    "파라미터(Parameter)": {
        "easy": "AI 모델이 학습을 통해 조정하는 숫자 값들입니다. 모델이 데이터를 학습하면서 이 값들을 계속 조정해서 정확도를 높입니다. 파라미터가 많을수록 모델이 복잡한 패턴을 학습할 수 있지만, 그만큼 계산도 많이 필요합니다.",
        "hard": "신경망을 구성하는 학습 가능한 가중치(Weight)와 편향(Bias)의 집합으로, 역전파(Backpropagation)와 경사하강법(Gradient Descent)을 통해 최적화됩니다. Fully Connected Layer의 경우 파라미터 수는 (입력 차원 × 출력 차원 + 편향), Transformer의 경우 d_model, n_heads, n_layers 등에 의해 결정됩니다. GPT-3는 175B(1,750억) 파라미터를 가지며, 파라미터 수가 증가할수록 모델 용량(Capacity)과 표현력이 향상되지만 과적합(Overfitting) 위험과 계산 비용도 증가합니다."
    },

    "희소(Sparse) 학습": {
        "easy": "AI 모델의 일부만 선택적으로 사용하여 학습하는 방법입니다. 모든 부분을 사용하지 않고 필요한 부분만 활성화해서 계산 시간과 메모리를 절약합니다. 전체를 사용하는 것보다 효율적이면서도 비슷한 성능을 낼 수 있습니다.",
        "hard": "전체 파라미터 중 일부(통상 10~30%)만을 활성화하여 Forward/Backward Pass를 수행하는 효율적 학습 기법입니다. Mixture of Experts(MoE), Dynamic Sparse Training(DST), Lottery Ticket Hypothesis 등이 대표적입니다. Top-K Gating, Threshold-based Activation 등을 통해 활성 파라미터를 선택하며, 동일 파라미터 수 대비 FLOPs를 크게 감소시킵니다. 그러나 불규칙한 메모리 접근 패턴으로 인한 하드웨어 최적화 어려움과 Load Imbalance 문제가 존재합니다."
    }
}


def update_glossary_explanations():
    """용어집 설명 업데이트"""

    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
        return False

    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        print("=" * 80)
        print("용어집 설명 업데이트 시작")
        print("=" * 80)

        updated_count = 0

        for term, explanations in TERM_EXPLANATIONS.items():
            try:
                # 용어 존재 확인
                cursor.execute("SELECT term FROM glossary WHERE term = %s", (term,))
                result = cursor.fetchone()

                if not result:
                    print(f"⚠️  용어 '{term}'를 찾을 수 없습니다. 건너뜁니다.")
                    continue

                # 설명 업데이트
                update_query = """
                UPDATE glossary
                SET easy_explanation = %s,
                    hard_explanation = %s
                WHERE term = %s
                """

                cursor.execute(update_query, (
                    explanations['easy'],
                    explanations['hard'],
                    term
                ))

                updated_count += 1
                print(f"✅ '{term}' 설명 업데이트 완료")

            except Exception as e:
                print(f"❌ '{term}' 업데이트 실패: {e}")
                continue

        # 변경사항 커밋
        conn.commit()

        print("=" * 80)
        print(f"✅ 총 {updated_count}개 용어 설명 업데이트 완료!")
        print("=" * 80)

        # 결과 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM glossary
            WHERE easy_explanation IS NOT NULL
              AND hard_explanation IS NOT NULL
              AND easy_explanation NOT LIKE '%추가되지 않았습니다%'
              AND hard_explanation NOT LIKE '%추가되지 않았습니다%'
        """)
        total_with_explanations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM glossary")
        total_terms = cursor.fetchone()[0]

        print(f"\n📊 통계:")
        print(f"   전체 용어: {total_terms}개")
        print(f"   설명 완료: {total_with_explanations}개")
        print(f"   설명 없음: {total_terms - total_with_explanations}개")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    update_glossary_explanations()
