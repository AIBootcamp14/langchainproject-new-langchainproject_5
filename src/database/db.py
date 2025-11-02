# ------------------------- 서드파티 라이브러리 ------------------------- #
import psycopg2
from psycopg2 import pool

# ------------------------- 프로젝트 모듈 ------------------------- #
from src.utils.config_loader import get_db_config


# ==================== PostgreSQL Connection Pool ==================== #
class PostgreSQLConnectionPool:
    """
    PostgreSQL 연결 풀 관리 클래스

    configs/db_config.yaml 설정 파일을 사용하여 연결합니다.
    """

    def __init__(self, min_connections=1, max_connections=10):
        """
        연결 풀 초기화

        Args:
            min_connections: 최소 연결 수
            max_connections: 최대 연결 수
        """
        # configs/db_config.yaml에서 설정 로드
        db_config = get_db_config()
        pg_config = db_config['postgresql']

        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=min_connections,                        # 최소 연결 수
            maxconn=max_connections,                        # 최대 연결 수
            host=pg_config['host'],
            port=pg_config['port'],
            database=pg_config['database'],
            user=pg_config['user'],
            password=pg_config['password']
        )

    # ---------------------- 연결 가져오기 ---------------------- #
    def get_connection(self):
        """
        연결 풀에서 연결 가져오기

        Returns:
            psycopg2 connection 객체
        """
        return self.connection_pool.getconn()

    # ---------------------- 연결 반환 ---------------------- #
    def put_connection(self, connection):
        """
        연결을 풀에 반환

        Args:
            connection: psycopg2 connection 객체
        """
        self.connection_pool.putconn(connection)

    # ---------------------- 연결 풀 종료 ---------------------- #
    def close_all_connections(self):
        """
        모든 연결 종료
        """
        self.connection_pool.closeall()


# ==================== 전역 연결 풀 인스턴스 ==================== #
connection_pool = PostgreSQLConnectionPool()


# ==================== 간단한 쿼리 실행 함수 ==================== #
def execute_query(query, params=None, fetch=False):
    """
    SQL 쿼리 실행 (INSERT, UPDATE, DELETE, SELECT)

    Args:
        query: SQL 쿼리문
        params: 쿼리 파라미터 (선택)
        fetch: True면 결과 반환, False면 None

    Returns:
        fetch=True: 조회 결과 리스트
        fetch=False: None
    """
    conn = connection_pool.get_connection()          # 연결 가져오기
    cursor = conn.cursor()

    try:
        # 쿼리 실행
        cursor.execute(query, params)
        conn.commit()                                # 트랜잭션 커밋

        # 결과 조회
        if fetch:
            result = cursor.fetchall()               # 모든 결과 가져오기
            return result
        else:
            return None

    except Exception as e:
        conn.rollback()                              # 오류 발생 시 롤백
        raise e

    finally:
        cursor.close()
        connection_pool.put_connection(conn)        # 연결 반환