# ------------------------- 프로젝트 모듈 ------------------------- #
from src.database.db import execute_query

# ---------------------- PostgreSQL 버전 확인 ---------------------- #
result = execute_query("SELECT version()", fetch=True)
print(f"PostgreSQL 버전: {result[0][0]}")

# ---------------------- papers 테이블 개수 확인 ---------------------- #
result = execute_query("SELECT COUNT(*) FROM papers", fetch=True)
print(f"papers 테이블 레코드 수: {result[0][0]}")