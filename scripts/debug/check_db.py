#!/usr/bin/env python
"""데이터베이스 상태 확인"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

# BERT 논문 확인
cursor.execute("SELECT paper_id, title FROM papers WHERE title ILIKE '%BERT%';")
papers = cursor.fetchall()

print("BERT 관련 논문:")
for paper_id, title in papers:
    print(f"  ID: {paper_id}, 제목: {title}")

# 논문 청크 확인
if papers:
    paper_id = papers[0][0]
    cursor.execute("""
        SELECT COUNT(*) FROM langchain_pg_embedding
        WHERE cmetadata->>'paper_id' = %s;
    """, (str(paper_id),))
    count = cursor.fetchone()[0]
    print(f"\nBERT 논문(ID: {paper_id})의 청크 수: {count}")

cursor.close()
conn.close()
