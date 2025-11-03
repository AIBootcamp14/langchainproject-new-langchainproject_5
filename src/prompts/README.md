# 프롬프트 파일 매핑 가이드

## 📁 프롬프트 파일 구조

```
src/prompts/
├── routing_prompts.json          # 라우팅 프롬프트 + Few-shot 예시
├── tool_prompts.json              # 6개 도구별 프롬프트
├── evaluation_prompts.json        # 평가 프롬프트
├── question_generation_prompts.json  # 질문 생성 프롬프트
├── golden_dataset.json            # Golden Dataset (테스트용 질문)
└── README.md                      # 이 파일
```

---

## 🗺️ 프롬프트 사용 파일 매핑

### 1. 라우팅 프롬프트 (`routing_prompts.json`)

**사용 위치**: `src/agent/nodes.py:router_node` (lines 44-81)

**현재 상태**: 하드코딩 (JSON 파일로 이동 필요)

**사용 방법**:
```python
import json

# JSON 프롬프트 로드
with open("src/prompts/routing_prompts.json", "r", encoding="utf-8") as f:
    routing_data = json.load(f)

routing_prompt = routing_data["routing_prompt"]
few_shot_examples = routing_data["few_shot_examples"]
```

**포함 내용**:
- 6개 도구 설명 및 사용 시나리오
- 도구별 키워드 리스트
- 중요 규칙 (비교 질문 → general 등)
- Few-shot 예시 10개

---

### 2. 도구별 프롬프트 (`tool_prompts.json`)

#### 2.1 일반 답변 프롬프트

**사용 위치**: `src/tools/general_answer.py` (lines 37-50)

**현재 상태**: 하드코딩 (JSON 파일로 이동 필요)

**사용 방법**:
```python
import json

with open("src/prompts/tool_prompts.json", "r", encoding="utf-8") as f:
    tool_prompts = json.load(f)

# 난이도별 프롬프트
difficulty = "easy"  # or "hard"
system_prompt = tool_prompts["general_answer_prompts"][difficulty]["system_prompt"]
```

**포함 내용**:
- Easy 모드 시스템 프롬프트
- Hard 모드 시스템 프롬프트
- 각 난이도별 예시

---

#### 2.2 웹 검색 프롬프트

**사용 위치**: `src/tools/web_search.py` (lines 119-147)

**현재 상태**: 하드코딩 (JSON 파일로 이동 필요)

**사용 방법**:
```python
import json

with open("src/prompts/tool_prompts.json", "r", encoding="utf-8") as f:
    tool_prompts = json.load(f)

# 난이도별 프롬프트
difficulty = "easy"  # or "hard"
system_prompt = tool_prompts["web_search_prompts"][difficulty]["system_prompt"]
user_prompt_template = tool_prompts["web_search_prompts"][difficulty]["user_prompt_template"]

# 사용 예시
user_prompt = user_prompt_template.format(
    formatted_results=formatted_results,
    question=question
)
```

**포함 내용**:
- Easy/Hard 시스템 프롬프트
- 사용자 프롬프트 템플릿 (검색 결과 포함)

---

#### 2.3 논문 요약 프롬프트

**사용 위치**: `src/tools/summarize.py`
- 제목 추출: lines 58-63
- 요약 프롬프트: lines 157-168

**현재 상태**: 하드코딩 (JSON 파일로 이동 필요)

**사용 방법**:
```python
import json

with open("src/prompts/tool_prompts.json", "r", encoding="utf-8") as f:
    tool_prompts = json.load(f)

# 제목 추출 프롬프트
title_extraction_template = tool_prompts["summarize_prompts"]["title_extraction"]["template"]
extract_prompt = title_extraction_template.format(question=question)

# 요약 프롬프트
difficulty = "easy"  # or "hard"
system_prompt = tool_prompts["summarize_prompts"][difficulty]["system_prompt"]
summary_template = tool_prompts["summarize_prompts"][difficulty]["summary_template"]

summary_prompt = summary_template.format(
    system_prompt=system_prompt,
    title=title,
    authors=authors,
    publish_date=publish_date,
    abstract=abstract,
    combined_text=combined_text
)
```

**포함 내용**:
- 논문 제목 추출 프롬프트
- Easy/Hard 요약 프롬프트
- 요약 템플릿

---

#### 2.4 용어집 프롬프트

**사용 위치**: `src/tools/glossary.py`

**현재 상태**: 구현 필요

**사용 방법**:
```python
import json

with open("src/prompts/tool_prompts.json", "r", encoding="utf-8") as f:
    tool_prompts = json.load(f)

# 난이도별 프롬프트
difficulty = "easy"  # or "hard"
system_prompt = tool_prompts["glossary_prompts"][difficulty]["system_prompt"]
```

**포함 내용**:
- Easy/Hard 시스템 프롬프트

---

#### 2.5 논문 검색 프롬프트

**사용 위치**: `src/tools/search_paper.py`

**현재 상태**: 구현 필요

**사용 방법**:
```python
import json

with open("src/prompts/tool_prompts.json", "r", encoding="utf-8") as f:
    tool_prompts = json.load(f)

# 난이도별 프롬프트
difficulty = "easy"  # or "hard"
system_prompt = tool_prompts["search_paper_prompts"][difficulty]["system_prompt"]
```

**포함 내용**:
- Easy/Hard 시스템 프롬프트

---

#### 2.6 파일 저장 프롬프트

**사용 위치**: `src/tools/file_save.py` 또는 `src/tools/save_file.py`

**현재 상태**: 구현 필요

**사용 방법**:
```python
import json

with open("src/prompts/tool_prompts.json", "r", encoding="utf-8") as f:
    tool_prompts = json.load(f)

# 메시지
confirmation_msg = tool_prompts["save_file_prompts"]["confirmation_message"]
success_msg = tool_prompts["save_file_prompts"]["success_message"].format(filepath=filepath)
error_msg = tool_prompts["save_file_prompts"]["error_message"].format(error=str(e))
```

**포함 내용**:
- 확인 메시지
- 성공 메시지
- 오류 메시지

---

### 3. 평가 프롬프트 (`evaluation_prompts.json`)

**사용 위치**: `src/evaluation/evaluator.py`

**현재 상태**: 구현 필요

**사용 방법**:
```python
import json
from langchain.prompts import PromptTemplate

with open("src/prompts/evaluation_prompts.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

# 평가 프롬프트 템플릿
prompt_template = PromptTemplate(
    template=eval_data["evaluation_prompt"]["template"],
    input_variables=eval_data["evaluation_prompt"]["input_variables"]
)

# 프롬프트 포맷팅
prompt = prompt_template.format(
    question=question,
    answer=answer,
    reference_docs=reference_docs,
    difficulty=difficulty
)
```

**포함 내용**:
- 평가 프롬프트 템플릿
- 평가 기준 (정확도, 관련성, 난이도 적합성, 출처 명시)
- 평가 예시

---

### 4. 질문 생성 프롬프트 (`question_generation_prompts.json`)

**사용 위치**: 테스트 스크립트 또는 질문 자동 생성 도구

**현재 상태**: 구현 필요

**사용 방법**:
```python
import json
from langchain.prompts import PromptTemplate

with open("src/prompts/question_generation_prompts.json", "r", encoding="utf-8") as f:
    qgen_data = json.load(f)

# 질문 생성 프롬프트
prompt_template = PromptTemplate(
    template=qgen_data["question_generation_prompt"]["template"],
    input_variables=qgen_data["question_generation_prompt"]["input_variables"]
)

# 질문 생성
prompt = prompt_template.format(
    title=title,
    authors=authors,
    abstract=abstract
)

response = llm.invoke(prompt)
questions = json.loads(response.content)
```

**포함 내용**:
- 질문 생성 프롬프트 템플릿
- 질문 템플릿 (Easy/Hard)
- 도구별 질문 템플릿
- 생성 예시

---

### 5. Golden Dataset (`golden_dataset.json`)

**사용 위치**: 테스트 스크립트, 평가 스크립트

**현재 상태**: 15개 질문 포함

**사용 방법**:
```python
import json

with open("src/prompts/golden_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

# 전체 질문 목록
questions = dataset["golden_dataset"]

# 테스트 실행
for item in questions:
    question = item["question"]
    expected_tool = item["expected_tool"]
    expected_keywords = item["expected_answer_keywords"]

    # Agent 실행
    result = agent.invoke({"question": question, "difficulty": item["difficulty"]})

    # 라우팅 정확도 검증
    actual_tool = result["tool_choice"]
    assert actual_tool == expected_tool, f"Expected {expected_tool}, got {actual_tool}"
```

**포함 내용**:
- 15개 테스트 질문
- 각 질문의 난이도, 예상 도구, 예상 키워드
- 질문 분포 메타데이터

---

## 📊 프롬프트 파일 통계

| 파일명 | 프롬프트 수 | 사용 파일 수 |
|-------|-----------|-----------|
| routing_prompts.json | 1 + 10 예시 | 1 (nodes.py) |
| tool_prompts.json | 12 (6개 도구 × 2 난이도) | 6 (각 도구 파일) |
| evaluation_prompts.json | 1 | 1 (evaluator.py) |
| question_generation_prompts.json | 1 | 1 (테스트 스크립트) |
| golden_dataset.json | 15 질문 | 1 (테스트 스크립트) |

---

## 🔧 구현 우선순위

### Phase 1: 라우팅 프롬프트 (최우선)
1. `src/agent/nodes.py:router_node` 수정
   - JSON 파일 로드
   - Few-shot 프롬프트 적용
2. 라우팅 정확도 테스트 (Golden Dataset 사용)

### Phase 2: 도구별 프롬프트
1. `src/tools/general_answer.py` 수정
2. `src/tools/web_search.py` 수정
3. `src/tools/summarize.py` 수정
4. `src/tools/glossary.py` 수정 (구현 필요)
5. `src/tools/search_paper.py` 수정 (구현 필요)
6. `src/tools/save_file.py` 수정 (구현 필요)

### Phase 3: 평가 시스템
1. `src/evaluation/evaluator.py` 구현
2. 평가 결과 DB 저장 로직
3. 평가 결과 시각화 (Streamlit)

### Phase 4: 테스트 자동화
1. 질문 생성 스크립트
2. Golden Dataset 테스트 스크립트
3. 라우팅 정확도 측정 스크립트

---

## 🧪 테스트 가이드

### 라우팅 정확도 테스트

```python
# scripts/test_routing_accuracy.py

import json
from src.agent.graph import create_agent_graph

# Golden Dataset 로드
with open("src/prompts/golden_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

questions = dataset["golden_dataset"]
agent = create_agent_graph()

# 테스트 실행
correct = 0
total = len(questions)

for item in questions:
    result = agent.invoke({
        "question": item["question"],
        "difficulty": item["difficulty"]
    })

    if result["tool_choice"] == item["expected_tool"]:
        correct += 1
        print(f"✅ {item['question']}: {item['expected_tool']}")
    else:
        print(f"❌ {item['question']}: Expected {item['expected_tool']}, Got {result['tool_choice']}")

# 정확도 계산
accuracy = correct / total * 100
print(f"\n라우팅 정확도: {accuracy:.2f}% ({correct}/{total})")
```

---

## 📝 프롬프트 수정 가이드

### 프롬프트 수정 시 주의사항

1. **JSON 형식 유지**
   - 올바른 JSON 문법 사용
   - 문자열 내 줄바꿈은 `\n` 사용

2. **템플릿 변수 확인**
   - `{question}`, `{difficulty}` 등 변수명 일치 확인
   - 모든 변수가 포맷팅 시 전달되는지 확인

3. **난이도별 프롬프트**
   - Easy: 쉬운 언어, 비유, 간단 요약
   - Hard: 기술 용어, 수식, 복잡도, 논문 비교

4. **Few-shot 예시**
   - 각 도구별 최소 2개 이상
   - 다양한 질문 패턴 포함

5. **버전 관리**
   - 프롬프트 수정 시 git commit
   - 성능 개선 여부 측정 (Golden Dataset 테스트)

---

## 🔗 참고 문서

- [담당역할_04_임예슬_프롬프트_엔지니어링.md](../../docs/roles/담당역할_04_임예슬_프롬프트_엔지니어링.md)
- [15_프롬프트_엔지니어링.md](../../docs/PRD/15_프롬프트_엔지니어링.md)
- [멘토링 문서](../../docs/minutes/20251030/20251030_멘토링.md) - 프롬프트 인사이트 (lines 417-553)

---

## 📞 문의

프롬프트 관련 문의: 임예슬 (@임예슬)

---
