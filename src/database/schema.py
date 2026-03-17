import duckdb
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSchema:
    def __init__(self, db_path: str = "data/hackerone.duckdb"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
    def create_raw_tables(self):
        conn = duckdb.connect(self.db_path)
        
        logger.info("Creating raw data tables...")
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_reports (
                id VARCHAR PRIMARY KEY,
                title VARCHAR,
                created_at TIMESTAMP,
                disclosed_at TIMESTAMP,
                state VARCHAR,
                substate VARCHAR,
                severity_rating VARCHAR,
                severity_score DOUBLE,
                weakness_id INTEGER,
                weakness_name VARCHAR,
                reporter_username VARCHAR,
                reporter_name VARCHAR,
                team_handle VARCHAR,
                team_name VARCHAR,
                bounty_amount DOUBLE,
                bonus_amount DOUBLE,
                has_bounty BOOLEAN,
                vote_count INTEGER,
                voter_count INTEGER,
                url VARCHAR,
                source VARCHAR,
                summary TEXT,
                description TEXT,
                vulnerability_information TEXT,
                impact TEXT,
                original_report_id VARCHAR,
                original_report_url VARCHAR
            )
        """)
        
        logger.info("Raw tables created successfully")
        conn.close()
    
    def create_transformed_tables(self):
        conn = duckdb.connect(self.db_path)
        
        logger.info("Creating transformed tables and views...")
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dim_vulnerabilities AS
            SELECT DISTINCT
                weakness_id,
                weakness_name,
                COUNT(*) OVER (PARTITION BY weakness_id) as total_occurrences
            FROM raw_reports
            WHERE weakness_id IS NOT NULL
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dim_organizations AS
            SELECT DISTINCT
                team_handle,
                team_name,
                MIN(created_at) OVER (PARTITION BY team_handle) as first_report_date,
                MAX(created_at) OVER (PARTITION BY team_handle) as latest_report_date,
                COUNT(*) OVER (PARTITION BY team_handle) as total_reports
            FROM raw_reports
            WHERE team_handle IS NOT NULL
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dim_reporters AS
            SELECT DISTINCT
                reporter_username,
                reporter_name,
                MIN(created_at) OVER (PARTITION BY reporter_username) as first_report_date,
                MAX(created_at) OVER (PARTITION BY reporter_username) as latest_report_date,
                COUNT(*) OVER (PARTITION BY reporter_username) as total_reports
            FROM raw_reports
            WHERE reporter_username IS NOT NULL
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fact_reports AS
            SELECT
                id,
                created_at,
                disclosed_at,
                weakness_id,
                reporter_username,
                team_handle,
                severity_rating,
                severity_score,
                bounty_amount,
                bonus_amount,
                has_bounty,
                vote_count,
                voter_count,
                state,
                substate
            FROM raw_reports
        """)
        
        logger.info("Creating business metric views...")
        
        conn.execute("""
            CREATE OR REPLACE VIEW vw_vulnerability_metrics AS
            SELECT
                w.weakness_name,
                COUNT(DISTINCT f.id) as total_reports,
                SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                ROUND(AVG(f.bounty_amount), 2) as avg_bounty,
                ROUND(MAX(f.bounty_amount), 2) as max_bounty,
                ROUND(AVG(f.vote_count), 2) as avg_votes,
                ROUND(100.0 * SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) / COUNT(*), 2) as bounty_rate
            FROM fact_reports f
            JOIN dim_vulnerabilities w ON f.weakness_id = w.weakness_id
            GROUP BY w.weakness_name
            ORDER BY total_reports DESC
        """)
        
        conn.execute("""
            CREATE OR REPLACE VIEW vw_organization_metrics AS
            SELECT
                o.team_handle,
                o.team_name,
                COUNT(DISTINCT f.id) as total_reports,
                SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                ROUND(SUM(f.bounty_amount), 2) as total_bounty_paid,
                ROUND(AVG(f.bounty_amount), 2) as avg_bounty,
                ROUND(AVG(f.vote_count), 2) as avg_votes,
                ROUND(100.0 * SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) / COUNT(*), 2) as bounty_rate,
                o.first_report_date,
                o.latest_report_date
            FROM fact_reports f
            JOIN dim_organizations o ON f.team_handle = o.team_handle
            GROUP BY o.team_handle, o.team_name, o.first_report_date, o.latest_report_date
            ORDER BY total_reports DESC
        """)
        
        conn.execute("""
            CREATE OR REPLACE VIEW vw_reporter_metrics AS
            SELECT
                r.reporter_username,
                r.reporter_name,
                COUNT(DISTINCT f.id) as total_reports,
                SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                ROUND(SUM(f.bounty_amount), 2) as total_earnings,
                ROUND(AVG(f.bounty_amount), 2) as avg_bounty,
                ROUND(AVG(f.vote_count), 2) as avg_votes,
                ROUND(100.0 * SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) / COUNT(*), 2) as bounty_rate,
                r.first_report_date,
                r.latest_report_date
            FROM fact_reports f
            JOIN dim_reporters r ON f.reporter_username = r.reporter_username
            GROUP BY r.reporter_username, r.reporter_name, r.first_report_date, r.latest_report_date
            ORDER BY total_reports DESC
        """)
        
        conn.execute("""
            CREATE OR REPLACE VIEW vw_time_trends AS
            SELECT
                DATE_TRUNC('month', created_at) as month,
                COUNT(DISTINCT id) as total_reports,
                SUM(CASE WHEN has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                ROUND(SUM(bounty_amount), 2) as total_bounty,
                ROUND(AVG(bounty_amount), 2) as avg_bounty,
                COUNT(DISTINCT team_handle) as active_organizations,
                COUNT(DISTINCT reporter_username) as active_reporters
            FROM fact_reports
            WHERE created_at IS NOT NULL
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month
        """)
        
        logger.info("Transformed tables and views created successfully")
        conn.close()
    
    def load_raw_data(self, csv_path: str = "data/raw/hackerone_reports.csv"):
        conn = duckdb.connect(self.db_path)
        
        logger.info(f"Loading data from {csv_path}...")
        
        conn.execute(f"""
            INSERT INTO raw_reports 
            SELECT * FROM read_csv_auto('{csv_path}')
        """)
        
        count = conn.execute("SELECT COUNT(*) FROM raw_reports").fetchone()[0]
        logger.info(f"Loaded {count:,} records into raw_reports table")
        
        conn.close()
        return count

def main():
    schema = DatabaseSchema()
    
    print("Creating database schema...")
    schema.create_raw_tables()
    
    print("Loading raw data...")
    count = schema.load_raw_data()
    
    print("Creating transformed tables and views...")
    schema.create_transformed_tables()
    
    print(f"\nDatabase setup complete! {count:,} records loaded.")

if __name__ == "__main__":
    main()
