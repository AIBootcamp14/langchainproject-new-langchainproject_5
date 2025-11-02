#!/usr/bin/env python
"""BERT 논문 청크 확인"""

import os
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

# BERT 논문 확인
cursor.execute("SELECT paper_id FROM papers WHERE title ILIKE '%BERT%' LIMIT 1;")
paper_id = cursor.fetchone()[0]
print(f"BERT 논문 ID: {paper_id}")

# 컬렉션 UUID 가져오기
cursor.execute("SELECT uuid FROM langchain_pg_collection WHERE name = 'paper_chunks';")
collection_id = cursor.fetchone()[0]
print(f"paper_chunks 컬렉션 ID: {collection_id}")

# BERT 논문의 청크 수 확인 (여러 방법으로)
print("\n방법 1: cmetadata->>'paper_id' = '2'")
cursor.execute("""
    SELECT COUNT(*)
    FROM langchain_pg_embedding
    WHERE collection_id = %s AND cmetadata->>'paper_id' = '2';
""", (collection_id,))
count1 = cursor.fetchone()[0]
print(f"  청크 수: {count1}")

print("\n방법 2: cmetadata->>'paper_id' = %s (paper_id 변수)")
cursor.execute("""
    SELECT COUNT(*)
    FROM langchain_pg_embedding
    WHERE collection_id = %s AND cmetadata->>'paper_id' = %s;
""", (collection_id, str(paper_id)))
count2 = cursor.fetchone()[0]
print(f"  청크 수: {count2}")

print("\n방법 3: (cmetadata->>'paper_id')::int = 2")
cursor.execute("""
    SELECT COUNT(*)
    FROM langchain_pg_embedding
    WHERE collection_id = %s AND (cmetadata->>'paper_id')::int = 2;
""", (collection_id,))
count3 = cursor.fetchone()[0]
print(f"  청크 수: {count3}")

# 실제 cmetadata 샘플 확인
print("\ncmetadata 샘플 (처음 5개):")
cursor.execute("""
    SELECT cmetadata
    FROM langchain_pg_embedding
    WHERE collection_id = %s
    LIMIT 5;
""", (collection_id,))
samples = cursor.fetchall()
for i, (metadata,) in enumerate(samples, 1):
    print(f"  {i}. {json.dumps(metadata, indent=2)}")

cursor.close()
conn.close()
