#!/usr/bin/env python
"""데이터베이스 상태 상세 확인"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

# 모든 테이블 확인
print("데이터베이스의 모든 테이블:")
cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public';
""")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# langchain 관련 테이블의 레코드 수
print("\nlangchain 관련 테이블의 레코드 수:")
for table in tables:
    table_name = table[0]
    if 'langchain' in table_name or 'embedding' in table_name:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count}개")
        except Exception as e:
            print(f"  {table_name}: 오류 - {e}")

# langchain_pg_collection 확인
print("\nlangchain_pg_collection:")
try:
    cursor.execute("SELECT name, uuid FROM langchain_pg_collection;")
    collections = cursor.fetchall()
    for name, uuid in collections:
        print(f"  - {name}: {uuid}")

        # 각 컬렉션의 임베딩 수 확인
        cursor.execute("""
            SELECT COUNT(*)
            FROM langchain_pg_embedding
            WHERE collection_id = %s;
        """, (uuid,))
        count = cursor.fetchone()[0]
        print(f"    임베딩 수: {count}")
except Exception as e:
    print(f"오류: {e}")

cursor.close()
conn.close()
