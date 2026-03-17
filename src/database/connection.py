import duckdb
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self, db_path: str = "data/hackerone.duckdb"):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        conn = duckdb.connect(self.db_path, read_only=False)
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str):
        with self.get_connection() as conn:
            result = conn.execute(query).fetchdf()
            return result
    
    def execute_query_dict(self, query: str):
        with self.get_connection() as conn:
            result = conn.execute(query).fetchall()
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]
    
    def get_table_info(self, table_name: str):
        query = f"DESCRIBE {table_name}"
        return self.execute_query(query)
    
    def get_row_count(self, table_name: str):
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.execute_query(query)
        return result['count'].iloc[0]

def get_db():
    return DatabaseConnection()
