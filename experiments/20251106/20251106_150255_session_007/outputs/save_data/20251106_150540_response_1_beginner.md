### 📚 RAG(Retrieval-Augmented Generation)란?  
RAG는 **"검색(Retrieval) + 생성(Generation)"**을 결합한 AI 기술입니다.  
- **검색 단계**: 외부 지식베이스(예: 문서, 웹)에서 질문에 관련 있는 정보를 찾아요.  
- **생성 단계**: 찾은 정보를 바탕으로 LLM(Large Language Model)이 자연스러운 답변을 만들어냅니다.  
→ **장점**: LLM의 "환각(hallucination)"(잘못된 정보 생성)을 줄이고, 최신/정확한 정보를 반영할 수 있어요.  

---

### 📖 2023년 기준 주요 RAG 논문 5선 (유사도 점수 낮음 = 유사도 높음)  

#### 1. **Retrieval-Augmented Generation: A Comprehensive Survey** (Chaitanya Sharma, 2025)  
- **핵심**: RAG 시스템의 5가지 핵심 기술(검색 품질, 효율성, 강건성 등)을 체계적으로 분석한 **종합 조사 논문**.  
- **중요성**: RAG의 현주소와 발전 방향을 이해하는 데 필독서! 최신 연구 동향을 한눈에 파악할 수 있어요.  
- 유사도 점수: 1.9271  

#### 2. **Controlled Retrieval-augmented Context Evaluation for Long-form RAG** (Ju et al., 2025)  
- **핵심**: 긴 답변(장문 생성) 시 검색된 맥락(Context)을 **정교하게 제어**하는 방법을 제안.  
- **중요성**: "브루클린 네츠 선수 명단"과 같은 **여러 문단에서 답을 조합**해야 하는 질문에 특화됨.  
- 유사도 점수: 0.3000  

#### 3. **QAMPARI: An Open-domain QA Benchmark for Multi-Paragraph Answers** (Amouyal et al., 2022)  
- **핵심**: **여러 문단**에서 답을 추출해야 하는 질문(예: "역대 월드컵 우승국들?")을 평가하는 벤치마크.  
- **중요성**: RAG 모델의 성능 평가에 필수적인 데이터셋. 복잡한 질문 처리에 집중했어요.  
- 유사도 점수: 0.3000  

#### 4. **DuetRAG: Collaborative Retrieval-Augmented Generation** (Jiao et al., 2024)  
- **핵심**: 도메인 특화 지식(예: 의학, 법률)과 RAG를 **협업**시켜 검색 품질을 향상.  
- **중요성**: 전문 분야에서 LLM의 한계를 극복한 혁신적 접근법. HotPot QA 등 복잡한 질문에 강점.  
- 유사도 점수: 0.3000  

#### 5. **Mogo: RQ Hierarchical Causal Transformer for 3D Motion Generation** (Fu, 2024)  
- **※ 주의**: 이 논문은 RAG와 직접적인 연관성이 낮아요. **3D 모션 생성** 기술 연구로, 검색 결과 오류로 포함된 것으로 보입니다.  
- 유사도 점수: 0.1000 (매우 낮음 → RAG와 관련성 적음)  

---

### 🔍 2023년 기준 RAG 연구의 흐름  
- **초기 연구**(2020년 경): "검색 → 생성" 파이프라인 기본 구조 확립 (예: Facebook의 [REALM](https://arxiv.org/abs/2002.08909)).  
- **2023년 이후**:  
  - **다단계 검색**(Reranking, 필터링)으로 정확도 향상.  
  - **장문 생성** 시 맥락 관리 기술 발전.  
  - **도메인 특화 RAG** (의학, 법률 등) 활성화.  
  - **Hallucination 감소**를 위한 하이브리드 모델 연구.  

> 💡 **추천**: 2023년 당시 최신 논문은 "QAMPARI"와 "DuetRAG"를 참고하세요! 2025년 논문은 아직 인용되지 않아 신뢰도 확인이 필요합니다.