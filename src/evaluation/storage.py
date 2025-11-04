# src/evaluation/storage.py
"""
평가 결과 저장 모듈

evaluation_results 테이블에 평가 결과를 저장하고 조회하는 기능을 제공합니다.
"""

# ------------------------- 표준 라이브러리 ------------------------- #
import os
from typing import List, Dict
from datetime import datetime

# ------------------------- 서드파티 라이브러리 ------------------------- #
import psycopg2
from dotenv import load_dotenv

# ------------------------- 환경 변수 로드 ------------------------- #
load_dotenv()


# ==================== DB 연결 함수 ==================== #
def _get_conn():
    """
    PostgreSQL 연결

    Returns:
        psycopg2.connection: PostgreSQL 연결 객체
    """
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        database=os.getenv("POSTGRES_DB", "papers")
    )


# ==================== 테이블 생성 함수 ==================== #
def create_evaluation_table():
    """
    evaluation_results 테이블 생성

    테이블 스키마:
    - eval_id: 평가 ID (Primary Key, Serial)
    - question: 사용자 질문
    - answer: AI 답변
    - accuracy_score: 정확도 점수 (0-10)
    - relevance_score: 관련성 점수 (0-10)
    - difficulty_score: 난이도 적합성 점수 (0-10)
    - citation_score: 출처 명시 점수 (0-10)
    - total_score: 총점 (0-40)
    - comment: 평가 코멘트
    - created_at: 생성 시간
    """
    # DB 연결
    conn = _get_conn()
    cursor = conn.cursor()

    # 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_results (
            eval_id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            accuracy_score INT CHECK (accuracy_score >= 0 AND accuracy_score <= 10),
            relevance_score INT CHECK (relevance_score >= 0 AND relevance_score <= 10),
            difficulty_score INT CHECK (difficulty_score >= 0 AND difficulty_score <= 10),
            citation_score INT CHECK (citation_score >= 0 AND citation_score <= 10),
            total_score INT CHECK (total_score >= 0 AND total_score <= 40),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 커밋 및 종료
    conn.commit()
    cursor.close()
    conn.close()


# ==================== 평가 결과 저장 함수 ==================== #
def save_evaluation_results(evaluation_results: List[Dict]):
    """
    평가 결과를 PostgreSQL에 저장

    Args:
        evaluation_results (List[Dict]): 평가 결과 리스트
            [{"question": ..., "answer": ..., "accuracy_score": ..., ...}, ...]
    """
    # DB 연결
    conn = _get_conn()
    cursor = conn.cursor()

    # 테이블 생성 (없을 경우)
    create_evaluation_table()

    # 평가 결과 삽입
    for result in evaluation_results:
        cursor.execute("""
            INSERT INTO evaluation_results
            (question, answer, accuracy_score, relevance_score, difficulty_score, citation_score, total_score, comment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            result['question'],
            result['answer'],
            result['accuracy_score'],
            result['relevance_score'],
            result['difficulty_score'],
            result['citation_score'],
            result['total_score'],
            result['comment']
        ))

    # 커밋 및 종료
    conn.commit()
    cursor.close()
    conn.close()


# ==================== 평가 결과 조회 함수 ==================== #
def get_evaluation_results(limit: int = 10) -> List[Dict]:
    """
    최근 평가 결과 조회

    Args:
        limit (int): 조회 개수 (기본: 10)

    Returns:
        List[Dict]: 평가 결과 리스트
    """
    # DB 연결
    conn = _get_conn()
    cursor = conn.cursor()

    # 최근 평가 결과 조회
    cursor.execute("""
        SELECT eval_id, question, answer, accuracy_score, relevance_score,
               difficulty_score, citation_score, total_score, comment, created_at
        FROM evaluation_results
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()

    # 딕셔너리 변환
    results = []
    for row in rows:
        results.append({
            "eval_id": row[0],
            "question": row[1],
            "answer": row[2],
            "accuracy_score": row[3],
            "relevance_score": row[4],
            "difficulty_score": row[5],
            "citation_score": row[6],
            "total_score": row[7],
            "comment": row[8],
            "created_at": row[9]
        })

    # 종료
    cursor.close()
    conn.close()

    return results


# ==================== 평가 통계 조회 함수 ==================== #
def get_evaluation_statistics() -> Dict:
    """
    평가 통계 조회

    Returns:
        Dict: 평가 통계 딕셔너리
            - total_count: 총 평가 개수
            - avg_accuracy: 평균 정확도
            - avg_relevance: 평균 관련성
            - avg_difficulty: 평균 난이도 적합성
            - avg_citation: 평균 출처 명시
            - avg_total: 평균 총점
    """
    # DB 연결
    conn = _get_conn()
    cursor = conn.cursor()

    # 통계 조회
    cursor.execute("""
        SELECT COUNT(*),
               AVG(accuracy_score),
               AVG(relevance_score),
               AVG(difficulty_score),
               AVG(citation_score),
               AVG(total_score)
        FROM evaluation_results
    """)

    row = cursor.fetchone()

    # 통계 딕셔너리 생성
    stats = {
        "total_count": row[0] or 0,
        "avg_accuracy": round(row[1] or 0, 2),
        "avg_relevance": round(row[2] or 0, 2),
        "avg_difficulty": round(row[3] or 0, 2),
        "avg_citation": round(row[4] or 0, 2),
        "avg_total": round(row[5] or 0, 2)
    }

    # 종료
    cursor.close()
    conn.close()

    return stats
