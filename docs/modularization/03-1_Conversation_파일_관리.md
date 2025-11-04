# 03-1. Conversation 파일 관리 상세

## 📋 문서 정보
- **최초 작성일**: 2025-11-04
- **최근 업데이트**: 2025-11-04
- **시스템명**: Conversation 파일 관리 시스템
- **구현 파일**: `src/utils/experiment_manager.py`, `ui/components/chat_interface.py`
- **우선순위**: ⭐⭐⭐ (최우선)
- **작성자**: 최현화[팀장]
- **상위 문서**: [03_실험_관리_시스템.md](./03_실험_관리_시스템.md)

---

## 📌 개요

Conversation 파일 관리 시스템은 **챗봇 세션의 모든 대화 내역을 체계적으로 저장하고 관리하는 시스템**입니다. 2025-11-04에 대대적인 개선이 이루어져 파일 중복 문제와 모드 구분 문제가 해결되었습니다.

---

## 🔴 개선 전 문제점

### 1. 파일 중복 생성 문제

**현상**:
- 매 답변마다 새로운 conversation 파일 생성
- 10번 질의응답 시 10개의 파일 생성

**예시**:
```
outputs/
├── conversation_20251104_213739.json  # 1번째 답변
├── conversation_20251104_213805.json  # 2번째 답변
├── conversation_20251104_213842.json  # 3번째 답변
├── conversation_20251104_213910.json  # 4번째 답변
├── conversation_20251104_214001.json  # 5번째 답변
├── conversation_20251104_214032.json  # 6번째 답변
├── conversation_20251104_214105.json  # 7번째 답변
├── conversation_20251104_214137.json  # 8번째 답변
├── conversation_20251104_214209.json  # 9번째 답변
└── conversation_20251104_214241.json  # 10번째 답변
```

**문제점**:
- 파일 개수 과다 (관리 어려움)
- 대화 흐름 추적 불가 (10개 파일 따로 열어야 함)
- 디스크 공간 낭비

### 2. 모드별 구분 없음

**현상**:
- Easy 모드, Hard 모드 대화가 같은 파일에 섞임
- 파일명에서 모드 구분 불가

**문제점**:
- 모드별 대화 분석 불가
- 난이도별 평가 어려움

---

## ✅ 개선 후 구조

### 1. 세션당 모드별 단일 파일

**개선 내용**:
- 세션당 모드별로 하나의 파일만 사용
- 새 메시지는 기존 파일에 이어쓰기

**예시**:
```
outputs/
├── conversation_easy_20251104_213739.json   # Easy 모드 전체 대화
└── conversation_hard_20251104_214500.json   # Hard 모드 전체 대화 (모드 변경 시)
```

### 2. 파일명 형식

**형식**: `conversation_{difficulty}_{timestamp}.json`

**필드 설명**:
- `difficulty`: 난이도 모드 (easy 또는 hard)
- `timestamp`: 세션 시작 시간 (YYYYMMDD_HHMMSS)

**예시**:
- `conversation_easy_20251104_213739.json` - Easy 모드 대화 (21:37:39 시작)
- `conversation_hard_20251104_220130.json` - Hard 모드 대화 (22:01:30 시작)

---

## 🔧 구현 상세

### save_conversation 메서드

**파일**: `src/utils/experiment_manager.py:559-596`

```python
def save_conversation(self, conversation_data: list, difficulty: str = "easy"):
    """
    전체 대화 기록 저장 (이어쓰기 방식)

    Args:
        conversation_data (list): 대화 메시지 리스트
        difficulty (str): 난이도 모드 (easy/hard)
    """
    # 1단계: 세션당 모드별로 하나의 파일 사용
    if not hasattr(self, f'conversation_file_{difficulty}'):
        # 첫 저장: 새 파일 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        conv_file = self.outputs_dir / f"conversation_{difficulty}_{timestamp}.json"
        setattr(self, f'conversation_file_{difficulty}', conv_file)
    else:
        # 이후 저장: 기존 파일 사용
        conv_file = getattr(self, f'conversation_file_{difficulty}')

    # 2단계: 기존 내용 읽기 (있다면)
    if conv_file.exists():
        with open(conv_file, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # 3단계: 새 메시지만 추가 (중복 방지)
    existing_contents = {msg.get('content', '') for msg in existing_data}
    for msg in conversation_data:
        if msg.get('content', '') not in existing_contents:
            existing_data.append(msg)
            existing_contents.add(msg.get('content', ''))

    # 4단계: 파일에 저장
    with open(conv_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    # 5단계: 로깅
    self.logger.write(f"대화 저장: {conv_file.name} ({len(existing_data)}개 메시지)")
```

### UI 통합

**파일**: `ui/components/chat_interface.py:462`

```python
# 답변 완료 후 대화 저장
if exp_manager:
    from ui.components.chat_manager import get_current_messages
    messages = get_current_messages()
    if messages:
        # difficulty 파라미터 전달 (필수!)
        exp_manager.save_conversation(messages, difficulty=difficulty)
```

---

## 📁 파일 구조 예시

### Easy 모드만 사용한 경우

```json
// conversation_easy_20251104_213739.json
[
  {
    "role": "user",
    "content": "RAG가 뭐야?"
  },
  {
    "role": "assistant",
    "content": "RAG는 Retrieval-Augmented Generation의 약자로..."
  },
  {
    "role": "user",
    "content": "어디에 사용돼?"
  },
  {
    "role": "assistant",
    "content": "RAG는 다음과 같은 상황에서 사용됩니다..."
  }
]
```

### Easy → Hard 모드 변경한 경우

```
outputs/
├── conversation_easy_20251104_213739.json   # Easy 모드 3개 질문
└── conversation_hard_20251104_214130.json   # Hard 모드 2개 질문
```

**conversation_easy_20251104_213739.json**:
```json
[
  {"role": "user", "content": "RAG가 뭐야?"},
  {"role": "assistant", "content": "RAG는..."},
  {"role": "user", "content": "어디에 사용돼?"},
  {"role": "assistant", "content": "..."}
]
```

**conversation_hard_20251104_214130.json**:
```json
[
  {"role": "user", "content": "RAG의 성능 평가 지표는?"},
  {"role": "assistant", "content": "RAG 시스템의 성능 평가에는..."},
  {"role": "user", "content": "Recall@K 계산 방법은?"},
  {"role": "assistant", "content": "Recall@K는..."}
]
```

---

## 🔄 동작 흐름

### 첫 번째 질문 (Easy 모드)

```
1. 사용자 질문 입력
   ↓
2. Agent 답변 생성
   ↓
3. save_conversation(messages, difficulty="easy") 호출
   ↓
4. conversation_file_easy 속성 없음 → 새 파일 생성
   파일명: conversation_easy_20251104_213739.json
   ↓
5. 메시지 저장 (1개 사용자 + 1개 어시스턴트)
```

### 두 번째 질문 (Easy 모드 계속)

```
1. 사용자 질문 입력
   ↓
2. Agent 답변 생성
   ↓
3. save_conversation(messages, difficulty="easy") 호출
   ↓
4. conversation_file_easy 속성 있음 → 기존 파일 사용
   파일명: conversation_easy_20251104_213739.json (동일)
   ↓
5. 기존 파일 읽기 (2개 메시지)
   ↓
6. 새 메시지 추가 (2개 추가: 질문 + 답변)
   ↓
7. 메시지 저장 (총 4개 메시지)
```

### 모드 변경 (Easy → Hard)

```
1. 사용자 난이도 변경: Hard 모드 선택
   ↓
2. 새 질문 입력
   ↓
3. Agent 답변 생성
   ↓
4. save_conversation(messages, difficulty="hard") 호출
   ↓
5. conversation_file_hard 속성 없음 → 새 파일 생성
   파일명: conversation_hard_20251104_214130.json
   ↓
6. 메시지 저장 (1개 사용자 + 1개 어시스턴트)
```

**결과**: Easy 파일과 Hard 파일 분리 저장

---

## 🎯 주요 기능

### 1. 중복 방지 메커니즘

**문제**:
- Streamlit의 `st.chat_message` 특성상 같은 메시지가 여러 번 추가될 수 있음

**해결**:
```python
# 메시지 내용을 set으로 관리
existing_contents = {msg.get('content', '') for msg in existing_data}

# 중복 체크
for msg in conversation_data:
    if msg.get('content', '') not in existing_contents:
        existing_data.append(msg)
        existing_contents.add(msg.get('content', ''))
```

**장점**:
- 같은 내용의 메시지는 한 번만 저장
- 파일 크기 절감

### 2. 모드별 파일 분리

**구현**:
```python
# Easy 모드 파일
if not hasattr(self, f'conversation_file_easy'):
    ...

# Hard 모드 파일
if not hasattr(self, f'conversation_file_hard'):
    ...
```

**장점**:
- 모드별 대화 분석 가능
- 난이도별 평가 용이
- 파일명만 봐도 모드 구분 가능

### 3. 타임스탬프 일관성

**구현**:
- 세션 시작 시 한 번만 타임스탬프 생성
- 이후 저장 시 동일 파일명 사용

**장점**:
- 파일명 일관성 유지
- 대화 흐름 추적 용이

---

## 📊 개선 효과

### 파일 개수 감소

**개선 전**:
- 10번 질의응답 → 10개 파일 생성

**개선 후**:
- 10번 질의응답 (Easy 모드) → 1개 파일
- 5번 Easy + 5번 Hard → 2개 파일

**효과**: 파일 개수 80-90% 감소

### 대화 추적 용이성

**개선 전**:
- 전체 대화 보려면 10개 파일 순차적으로 열어야 함

**개선 후**:
- 1개 파일만 열면 전체 대화 확인 가능

**효과**: 분석 시간 대폭 단축

### 모드별 분석 가능

**개선 전**:
- 모드 구분 불가 (파일명에 모드 정보 없음)

**개선 후**:
- 파일명만 봐도 모드 구분 가능
- Easy/Hard 대화 따로 분석 가능

**효과**: 난이도별 성능 평가 가능

---

## 🔗 관련 문서

- **[03_실험_관리_시스템.md](./03_실험_관리_시스템.md)** - 상위 문서
- **[06_AI_Agent_시스템.md](./06_AI_Agent_시스템.md)** - 멀티턴 대화 통합
- **[docs/issues/06_Session_010_실험_분석_기반_시스템_개선.md](../issues/06_Session_010_실험_분석_기반_시스템_개선.md)** - 개선 이슈

---

## 📝 요약

### 핵심 개선사항

1. ✅ **파일 중복 제거**: 매 답변마다 새 파일 생성 → 세션당 모드별 1개 파일
2. ✅ **모드별 파일명 구분**: conversation_{difficulty}_{timestamp}.json 형식
3. ✅ **이어쓰기 방식**: 기존 파일에 새 메시지 추가
4. ✅ **중복 방지**: 메시지 내용 기준 중복 체크
5. ✅ **타임스탬프 일관성**: 세션당 한 번만 생성

### 사용 패턴

```python
# ExperimentManager 사용
with ExperimentManager() as exp:
    # 첫 번째 답변 (Easy 모드)
    exp.save_conversation(messages, difficulty="easy")
    # → conversation_easy_20251104_213739.json 생성

    # 두 번째 답변 (Easy 모드)
    exp.save_conversation(messages, difficulty="easy")
    # → conversation_easy_20251104_213739.json 업데이트

    # 세 번째 답변 (Hard 모드로 변경)
    exp.save_conversation(messages, difficulty="hard")
    # → conversation_hard_20251104_214130.json 생성
```

### 주의사항

1. **difficulty 파라미터 필수**: `save_conversation(messages, difficulty=difficulty)` 형식으로 호출
2. **모드 변경 시**: 새 파일 자동 생성 (Easy ↔ Hard)
3. **세션 유지**: ExperimentManager 인스턴스가 유지되는 동안 파일명 일관성 보장
4. **JSON 형식**: 메시지는 LangChain BaseMessage 형식 또는 딕셔너리 형식
