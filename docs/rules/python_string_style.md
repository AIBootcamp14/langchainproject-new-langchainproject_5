# Python 문자열 스타일 가이드

## 개요

이 문서는 프로젝트에서 Python 코드 작성 시 문자열(특히 multi-line string) 사용에 대한 스타일 가이드를 정의합니다.

---

## Triple Quote (""") 문자열 들여쓰기 규칙

### 규칙 1: Multi-line 문자열의 들여쓰기

**❌ 잘못된 예시 (권장하지 않음):**
```python
system_content = """당신은 친절한 AI 어시스턴트입니다.
초심자도 이해할 수 있도록 쉽고 명확하게 답변해주세요.
- 전문 용어는 최소화하고 일상적인 언어를 사용하세요
- 복잡한 개념은 간단한 비유로 설명하세요
- 친근하고 이해하기 쉬운 톤을 유지하세요"""
```

**✅ 올바른 예시 (권장):**
```python
system_content = """당신은 친절한 AI 어시스턴트입니다.
                    초심자도 이해할 수 있도록 쉽고 명확하게 답변해주세요.
                    - 전문 용어는 최소화하고 일상적인 언어를 사용하세요
                    - 복잡한 개념은 간단한 비유로 설명하세요
                    - 친근하고 이해하기 쉬운 톤을 유지하세요"""
```

**이유:**
- 코드 가독성 향상: 들여쓰기를 맞추면 변수 할당문의 시작점과 문자열 내용이 시각적으로 구분됨
- 코드 구조 명확화: 문자열 내용이 코드 블록 내에서 정렬되어 보임
- 유지보수 용이성: 문자열 내용을 수정할 때 구조가 명확하게 보임

### 규칙 2: f-string에서의 Multi-line 문자열

**❌ 잘못된 예시:**
```python
user_prompt = f"""[참고 논문]
{context}

[질문]
{question}

위 논문을 참고하여 질문에 답변해주세요."""
```

**✅ 올바른 예시:**
```python
user_prompt = f"""[참고 논문]
                  {context}

                  [질문]
                  {question}

                  위 논문을 참고하여 질문에 답변해주세요."""
```

**주의사항:**
- f-string 변수(`{context}`, `{question}`)는 실제 값으로 대체되므로 들여쓰기가 최종 출력에 포함됨
- 프롬프트 엔지니어링 시 LLM에게 전달되는 텍스트의 포맷을 고려하여 적절히 조정

### 규칙 3: Docstring의 경우

**✅ Docstring은 기존 PEP 257 규칙 준수:**
```python
def example_function():
    """
    함수에 대한 간단한 설명

    Args:
        param1 (str): 매개변수 설명

    Returns:
        bool: 반환값 설명
    """
    pass
```

**이유:**
- Docstring은 Python 표준 규약(PEP 257)을 따름
- 자동 문서화 도구(Sphinx, pdoc 등)와의 호환성 유지

---

## 실제 프로젝트 적용 예시

### 1. 도구 노드의 난이도별 프롬프트

```python
# -------------- 난이도별 SystemMessage 설정 -------------- #
if difficulty == "easy":
    # Easy 모드: 초심자용 설명
    system_content = """당신은 친절한 AI 어시스턴트입니다.
                        초심자도 이해할 수 있도록 쉽고 명확하게 답변해주세요.
                        - 전문 용어는 최소화하고 일상적인 언어를 사용하세요
                        - 복잡한 개념은 간단한 비유로 설명하세요
                        - 친근하고 이해하기 쉬운 톤을 유지하세요"""
else:  # hard
    # Hard 모드: 전문가용 설명
    system_content = """당신은 전문적인 AI 어시스턴트입니다.
                        기술적인 세부사항을 포함하여 정확하고 전문적으로 답변해주세요.
                        - 기술 용어와 전문 개념을 자유롭게 사용하세요
                        - 깊이 있는 설명과 상세한 정보를 제공하세요
                        - 전문가 수준의 정확성을 유지하세요"""
```

### 2. RAG 시스템의 User Prompt

```python
user_prompt = f"""[참고 논문]
                  {context}

                  [질문]
                  {question}

                  위 논문을 참고하여 질문에 답변해주세요."""
```

### 3. 라우터 노드의 프롬프트

```python
routing_prompt = f"""사용자 질문을 분석하여 적절한 도구를 선택하세요:

                     도구 목록:
                     - search_paper: 논문 데이터베이스에서 검색
                     - web_search: 웹에서 최신 논문 검색
                     - glossary: 용어 정의 검색
                     - summarize: 논문 요약
                     - save_file: 파일 저장
                     - general: 일반 답변

                     질문: {question}

                     하나의 도구 이름만 반환하세요:
                     """
```

### 4. 용어 추출 프롬프트

```python
extract_prompt = f"""다음 질문에서 핵심 용어를 추출하세요. 용어만 반환하세요:

                     질문: {question}

                     용어:"""
```

### 5. 최종 답변 구성

```python
final_answer = f"""📄 논문 요약

                   **제목**: {title}
                   **저자**: {authors}
                   **발행일**: {publish_date}

                   **요약**:
                   {summary}"""
```

---

## 들여쓰기 정렬 가이드

### 기본 원칙

1. **첫 줄 제외**: Triple quote 시작 직후의 첫 줄은 들여쓰기 없이 작성
2. **나머지 줄**: 첫 줄 이후의 모든 줄은 변수명과 `=` 위치에 맞춰 들여쓰기
3. **공백 문자 사용**: 들여쓰기는 공백(space) 문자로만 구성 (탭 사용 금지)

### 들여쓰기 계산 방법

```python
# 예시:
system_content = """첫 줄은 여기
                    두 번째 줄부터 들여쓰기"""

# 들여쓰기 크기 계산:
# - 변수명 길이: len("system_content") = 14
# - 공백 + = + 공백 + """: 4
# - 총 들여쓰기: 14 + 4 = 18 spaces (또는 변수명과 시각적으로 정렬)
```

### 실용적 팁

- **에디터 설정**: VSCode, PyCharm 등 IDE에서 "Show Whitespace" 옵션을 활성화하여 공백 확인
- **자동 정렬**: 코드 포맷터(Black, autopep8)를 사용할 경우, 이 규칙과 충돌할 수 있으므로 수동 조정 필요
- **일관성 유지**: 프로젝트 전체에서 동일한 스타일 적용

---

## 예외 상황

### 1. 짧은 문자열

한 줄로 작성 가능한 짧은 문자열은 single/double quote 사용:

```python
short_message = "간단한 메시지"
```

### 2. SQL 쿼리

SQL 쿼리는 가독성을 위해 별도 규칙 적용 가능:

```python
query = """
SELECT paper_id, title, authors
FROM papers
WHERE title ILIKE %s
LIMIT 1
"""
```

또는:

```python
query = """SELECT paper_id, title, authors
           FROM papers
           WHERE title ILIKE %s
           LIMIT 1"""
```

### 3. 매우 긴 문자열

100자 이상의 매우 긴 라인은 적절히 줄바꿈하여 가독성 유지:

```python
long_text = """매우 긴 텍스트의 첫 번째 줄입니다. 이 줄은 100자를 넘어가므로
               적절히 줄바꿈하여 가독성을 높입니다. 두 번째 줄부터는 들여쓰기를
               맞춰서 작성합니다."""
```

---

## 체크리스트

코드 리뷰 시 다음 항목을 확인하세요:

- [ ] Triple quote 문자열의 첫 줄 제외, 나머지 줄 들여쓰기 확인
- [ ] f-string에서 변수 위치와 들여쓰기 조화 확인
- [ ] Docstring은 PEP 257 규칙 준수 확인
- [ ] 모든 들여쓰기가 공백(space)으로만 구성되었는지 확인
- [ ] 프로젝트 전체에서 일관된 스타일 적용 확인

---

## 참고 문서

- [docs/rules/annotate_style.md](./annotate_style.md) - 한글 주석 스타일 가이드
- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)

---

## 버전 이력

- **v1.0** (2025-11-01): 초안 작성 - Triple quote 문자열 들여쓰기 규칙 정의
