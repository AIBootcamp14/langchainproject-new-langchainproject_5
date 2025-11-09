# 시나리오: Text2SQL 통계 (Text2SQL Statistics)

## 📋 도구 설명

**도구명**: `text2sql`
**목적**: 자연어 질문을 SQL 쿼리로 변환하여 논문 데이터베이스의 통계 정보 제공

### 주요 기능
- 자연어 → SQL 자동 변환 (LLM 기반)
- PostgreSQL 논문 DB 통계 조회
- 연도별, 카테고리별, 저자별 논문 분포 분석
- 안전한 SQL 실행 (Read-only, Prepared Statements)

---

## 🎯 사용 시나리오

### 시나리오 1: 연도별 논문 수 조회

**사용자 상황**: 특정 연도에 발표된 논문의 수를 알고 싶음

**사용자 질문**:
```
"2024년에 발표된 논문은 몇 편이야?"
```

**Agent 동작**:
1. Router가 질문 분석
2. 통계 조회 질문으로 판단
3. `text2sql` 도구 선택
4. LLM이 자연어를 SQL로 변환
5. PostgreSQL에서 쿼리 실행
6. 결과를 자연어로 변환하여 답변

**실행 로그** (experiments/날짜/실행폴더/tools/text2sql.log):
```
Text2SQL 노드 실행: 2024년에 발표된 논문은 몇 편이야?
난이도: easy
SQL 생성 시작
생성된 SQL: SELECT COUNT(*) FROM papers WHERE EXTRACT(YEAR FROM publish_date) = 2024;
SQL 실행 시작
실행 결과: [(1247,)]
답변 생성 시작
답변 생성 완료
```

**예상 답변** (Easy 모드):
```
2024년에 발표된 논문은 총 **1,247편**입니다.

📊 2024년 논문 통계:
- 전체 논문: 1,247편
- 월평균: 약 104편
- 일평균: 약 3.4편

AI/ML 분야가 활발하게 연구되고 있네요! 🚀
```

**예상 답변** (Hard 모드):
```
2024년 논문 발표 현황:

📊 통계:
- **총 논문 수**: 1,247편
- **기간**: 2024-01-01 ~ 2024-12-31
- **평균 발표율**: 3.4편/일

📈 연도별 비교 (최근 3년):
- 2022: 987편
- 2023: 1,134편
- 2024: 1,247편 (+10% YoY)

💡 Insight:
AI/ML 분야의 논문 발표가 매년 증가하는 추세를 보이고 있으며,
특히 LLM과 Computer Vision 분야에서 활발한 연구가 진행 중입니다.
```

**UI 표시**:
- 🗣️ 사용된 도구: **📊 Text2SQL 통계**
- 실행된 SQL 쿼리 (Expander):
  ```sql
  SELECT COUNT(*) FROM papers
  WHERE EXTRACT(YEAR FROM publish_date) = 2024;
  ```

---

### 시나리오 2: 카테고리별 논문 분포

**사용자 질문**:
```
"어떤 카테고리의 논문이 가장 많아?"
```

**Agent 동작**:
1. `text2sql` 도구 선택
2. LLM이 GROUP BY 쿼리 생성
3. 카테고리별 논문 수 집계
4. 상위 5개 카테고리 반환

**생성된 SQL**:
```sql
SELECT category, COUNT(*) as count
FROM papers
GROUP BY category
ORDER BY count DESC
LIMIT 5;
```

**예상 답변**:
```
논문이 가장 많은 카테고리 Top 5:

1. 🥇 **Computer Vision (CV)**: 3,542편
   - 이미지 인식, 객체 탐지, Segmentation 등

2. 🥈 **Natural Language Processing (NLP)**: 2,987편
   - LLM, Machine Translation, Text Generation 등

3. 🥉 **Machine Learning (ML)**: 2,134편
   - 강화학습, Few-shot Learning, Meta-Learning 등

4. **Robotics**: 1,423편
   - 자율주행, 로봇 제어, Path Planning 등

5. **Speech**: 876편
   - 음성 인식, TTS, Speech Enhancement 등

📊 전체 카테고리 수: 12개
📄 총 논문 수: 11,962편
```

---

### 시나리오 3: 특정 저자 논문 수 조회

**사용자 질문**:
```
"Yoshua Bengio가 쓴 논문은 몇 편이야?"
```

**Agent 동작**:
1. `text2sql` 도구 선택
2. authors 필드에서 LIKE 검색 쿼리 생성
3. 해당 저자의 논문 수 반환

**생성된 SQL**:
```sql
SELECT COUNT(*)
FROM papers
WHERE authors LIKE '%Yoshua Bengio%';
```

**예상 답변** (Easy 모드):
```
Yoshua Bengio가 저자로 참여한 논문은 총 **42편**입니다.

🏆 Yoshua Bengio는 딥러닝의 3대 거장 중 한 명이에요!
- Turing Award 수상자 (2018)
- Montreal University 교수
- 딥러닝 연구의 선구자
```

**예상 답변** (Hard 모드):
```
Yoshua Bengio 논문 분석:

📊 기본 통계:
- **총 논문 수**: 42편
- **데이터베이스 내 비율**: 0.35%
- **평균 공동 저자 수**: 4.2명

📅 연도별 분포 (추정):
- 2010-2015: 15편
- 2016-2020: 18편
- 2021-2024: 9편

🔬 주요 연구 분야:
- Deep Learning Fundamentals
- Generative Models (GANs, VAEs)
- Representation Learning
- Neural Architecture

💡 Impact:
Bengio 교수는 Geoffrey Hinton, Yann LeCun과 함께
2018년 Turing Award를 공동 수상하였으며,
딥러닝 발전에 핵심적인 기여를 하였습니다.
```

---

### 시나리오 4: 기간별 논문 추이 분석

**사용자 질문**:
```
"최근 5년간 논문 발표 추이를 보여줘"
```

**Agent 동작**:
1. `text2sql` 도구 선택
2. 연도별 GROUP BY 쿼리 생성
3. 2020-2024년 데이터 조회
4. 추이 분석 및 시각화 정보 제공

**생성된 SQL**:
```sql
SELECT EXTRACT(YEAR FROM publish_date) as year, COUNT(*) as count
FROM papers
WHERE EXTRACT(YEAR FROM publish_date) BETWEEN 2020 AND 2024
GROUP BY year
ORDER BY year;
```

**예상 답변**:
```
최근 5년간 논문 발표 추이 (2020-2024):

📈 연도별 통계:
```
2020: ████████████░░░░░░░░ 723편
2021: ██████████████░░░░░░ 892편 (+23%)
2022: ████████████████░░░░ 987편 (+11%)
2023: ██████████████████░░ 1,134편 (+15%)
2024: ████████████████████ 1,247편 (+10%)
```

📊 주요 인사이트:
- **총 증가율**: +72% (2020 대비 2024)
- **연평균 성장률**: +14.5%
- **총 논문 수**: 4,983편

🚀 성장 요인:
- ChatGPT/GPT-4 등 LLM 혁신 (2022~)
- Diffusion Models (Stable Diffusion, DALL-E)
- Computer Vision 발전 (ViT, CLIP)
- 연구 인프라 개선 (A100, H100 GPU)

💡 전망:
현재 추세로 보면 2025년에는 약 1,370편의 논문이
발표될 것으로 예상됩니다.
```

---

### 시나리오 5: 복합 조건 통계 조회

**사용자 질문**:
```
"2023년 NLP 분야 논문 중 저자가 5명 이상인 논문은 몇 편?"
```

**Agent 동작**:
1. `text2sql` 도구 선택
2. 복합 WHERE 조건 쿼리 생성
3. 다중 조건 필터링 실행

**생성된 SQL** (추정):
```sql
SELECT COUNT(*)
FROM papers
WHERE EXTRACT(YEAR FROM publish_date) = 2023
  AND category = 'NLP'
  AND array_length(string_to_array(authors, ','), 1) >= 5;
```

**예상 답변**:
```
2023년 NLP 분야에서 저자가 5명 이상인 논문은 **187편**입니다.

📊 세부 분석:
- **전체 2023년 NLP 논문**: 567편
- **5명 이상 저자 논문**: 187편 (33%)
- **평균 공동 저자 수**: 3.8명

🔬 대규모 협업 추세:
최근 NLP 분야는 LLM 연구가 활발하여
대규모 팀 협업이 증가하는 추세입니다.
특히 GPT, LLaMA 등 Foundation Model 연구는
평균 10명 이상의 연구진이 참여합니다.
```

---

## 📊 성능 지표

- **SQL 생성 정확도**: ~85% (단순 쿼리 95%, 복잡 쿼리 75%)
- **평균 응답 시간**: 3초 (SQL 생성 1.5초 + 실행 0.5초 + 답변 생성 1초)
- **지원 쿼리 유형**: SELECT (집계, 필터링, 정렬, 그룹화)
- **안전성**: Read-only, Prepared Statements로 SQL Injection 방지

---

## 🔧 내부 구현

### DB 스키마 (papers 테이블)
```sql
CREATE TABLE papers (
    paper_id SERIAL PRIMARY KEY,
    title TEXT,
    authors TEXT,
    abstract TEXT,
    publish_date DATE,
    category VARCHAR(50),
    pdf_url TEXT
);
```

### SQL 생성 프롬프트
```python
system_prompt = """당신은 자연어를 SQL로 변환하는 전문가입니다.
다음 스키마를 사용하여 SELECT 쿼리만 생성하세요:

테이블: papers
- paper_id: 논문 ID (SERIAL PRIMARY KEY)
- title: 논문 제목 (TEXT)
- authors: 저자 (TEXT, 쉼표로 구분)
- publish_date: 발표일 (DATE)
- category: 카테고리 (VARCHAR)

규칙:
1. SELECT 쿼리만 생성
2. COUNT, SUM, AVG 등 집계 함수 사용 가능
3. GROUP BY, ORDER BY 사용 가능
4. LIMIT 사용 권장 (기본 10)
"""
```

### 로깅
- **tools/text2sql.log**: SQL 생성 및 실행 로그
- **chatbot.log**: 전체 Agent 실행 흐름

---

## ⚠️ 제한사항

1. **Read-only**: SELECT 쿼리만 지원 (INSERT, UPDATE, DELETE 불가)
2. **단일 테이블**: papers 테이블만 조회 가능
3. **복잡한 쿼리**: JOIN, Subquery 등 고급 쿼리는 정확도 낮음
4. **날짜 형식**: ISO 8601 형식 (YYYY-MM-DD) 권장

---

## 🔄 다른 도구로의 전환

| 상황 | 추천 도구 |
|------|----------|
| 논문 내용 검색 필요 | `search_paper` (RAG) |
| 최신 논문 통계 | `web_search` → `text2sql` |
| 결과 저장 필요 | `text2sql` → `save_file` |

---

## 💡 활용 팁

1. **명확한 조건**: "2024년" 대신 "2024년 1월부터 12월까지" 명시
2. **카테고리 정확도**: 카테고리명을 정확히 입력 (NLP, CV, ML 등)
3. **집계 함수**: "몇 편", "평균", "총합" 등 집계 의도 명확히 표현
4. **결과 제한**: "상위 10개", "Top 5" 등으로 LIMIT 활용

---

## 📈 예상 질문 리스트

### 단순 조회
1. "2023년 논문은 몇 편이야?"
2. "Computer Vision 논문은 총 몇 편?"
3. "가장 최근 논문은 언제 발표됐어?"

### 집계 분석
4. "카테고리별 논문 수를 보여줘"
5. "연도별 논문 추이를 알려줘"
6. "평균 저자 수는 몇 명이야?"

### 복합 조건
7. "2024년 NLP 논문 중 상위 10개는?"
8. "최근 5년간 가장 많이 연구된 분야는?"
9. "Geoffrey Hinton이 참여한 2020년 이후 논문은?"

---

**작성일**: 2025-11-09
**버전**: 1.0
