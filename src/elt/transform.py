import duckdb
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataTransformer:
    def __init__(self, db_path: str = "data/hackerone.duckdb"):
        self.db_path = db_path
        
    def create_dimension_tables(self):
        conn = duckdb.connect(self.db_path)
        
        logger.info("Creating dimension tables...")
        
        conn.execute("DROP TABLE IF EXISTS dim_vulnerabilities")
        conn.execute("""
            CREATE TABLE dim_vulnerabilities AS
            SELECT DISTINCT
                weakness_id,
                weakness_name
            FROM raw_reports
            WHERE weakness_id IS NOT NULL AND weakness_name IS NOT NULL AND weakness_name != ''
        """)
        
        conn.execute("DROP TABLE IF EXISTS dim_organizations")
        conn.execute("""
            CREATE TABLE dim_organizations AS
            SELECT DISTINCT
                team_handle,
                team_name,
                MIN(created_at) as first_report_date,
                MAX(created_at) as latest_report_date
            FROM raw_reports
            WHERE team_handle IS NOT NULL AND team_handle != ''
            GROUP BY team_handle, team_name
        """)
        
        conn.execute("DROP TABLE IF EXISTS dim_reporters")
        conn.execute("""
            CREATE TABLE dim_reporters AS
            SELECT DISTINCT
                reporter_username,
                reporter_name,
                MIN(created_at) as first_report_date,
                MAX(created_at) as latest_report_date
            FROM raw_reports
            WHERE reporter_username IS NOT NULL AND reporter_username != ''
            GROUP BY reporter_username, reporter_name
        """)
        
        vuln_count = conn.execute("SELECT COUNT(*) FROM dim_vulnerabilities").fetchone()[0]
        org_count = conn.execute("SELECT COUNT(*) FROM dim_organizations").fetchone()[0]
        reporter_count = conn.execute("SELECT COUNT(*) FROM dim_reporters").fetchone()[0]
        
        logger.info(f"Created dimension tables:")
        logger.info(f"   - dim_vulnerabilities: {vuln_count:,} records")
        logger.info(f"   - dim_organizations: {org_count:,} records")
        logger.info(f"   - dim_reporters: {reporter_count:,} records")
        
        conn.close()
    
    def create_fact_table(self):
        conn = duckdb.connect(self.db_path)
        
        logger.info("Creating fact table...")
        
        conn.execute("DROP TABLE IF EXISTS fact_reports")
        conn.execute("""
            CREATE TABLE fact_reports AS
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
        
        count = conn.execute("SELECT COUNT(*) FROM fact_reports").fetchone()[0]
        logger.info(f"Created fact_reports table: {count:,} records")
        
        conn.close()
    
    def create_business_views(self):
        conn = duckdb.connect(self.db_path)
        
        logger.info("Creating business metric views...")
        
        conn.execute("""
            CREATE OR REPLACE VIEW vw_vulnerability_metrics AS
            SELECT
                v.weakness_name,
                COUNT(DISTINCT f.id) as total_reports,
                SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                ROUND(AVG(f.vote_count), 2) as avg_votes,
                ROUND(100.0 * SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) / COUNT(*), 2) as bounty_rate
            FROM fact_reports f
            JOIN dim_vulnerabilities v ON f.weakness_id = v.weakness_id
            GROUP BY v.weakness_name
            ORDER BY total_reports DESC
        """)
        
        conn.execute("""
            CREATE OR REPLACE VIEW vw_organization_metrics AS
            SELECT
                o.team_handle,
                o.team_name,
                COUNT(DISTINCT f.id) as total_reports,
                SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) as bounty_reports,
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
                ROUND(AVG(f.vote_count), 2) as avg_votes,
                ROUND(100.0 * SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) / COUNT(*), 2) as bounty_rate,
                r.first_report_date,
                r.latest_report_date
            FROM fact_reports f
            LEFT JOIN dim_reporters r ON f.reporter_username = r.reporter_username
            WHERE r.reporter_username IS NOT NULL
            GROUP BY r.reporter_username, r.reporter_name, r.first_report_date, r.latest_report_date
            ORDER BY total_reports DESC
        """)
        
        conn.execute("""
            CREATE OR REPLACE VIEW vw_time_trends AS
            SELECT
                DATE_TRUNC('month', created_at) as month,
                COUNT(DISTINCT id) as total_reports,
                SUM(CASE WHEN has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                COUNT(DISTINCT team_handle) as active_organizations,
                COUNT(DISTINCT reporter_username) as active_reporters
            FROM fact_reports
            GROUP BY DATE_TRUNC('month', created_at)
            ORDER BY month DESC
        """)
        
        conn.execute("""
            CREATE OR REPLACE VIEW vw_severity_analysis AS
            SELECT
                severity_rating,
                COUNT(DISTINCT id) as total_reports,
                SUM(CASE WHEN has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                ROUND(AVG(severity_score), 2) as avg_severity_score,
                ROUND(AVG(vote_count), 2) as avg_votes,
                ROUND(100.0 * SUM(CASE WHEN has_bounty THEN 1 ELSE 0 END) / COUNT(*), 2) as bounty_rate
            FROM fact_reports
            WHERE severity_rating IS NOT NULL AND severity_rating != ''
            GROUP BY severity_rating
            ORDER BY avg_severity_score DESC
        """)
        
        logger.info("Created business metric views:")
        logger.info("   - vw_vulnerability_metrics")
        logger.info("   - vw_organization_metrics")
        logger.info("   - vw_reporter_metrics")
        logger.info("   - vw_time_trends")
        logger.info("   - vw_severity_analysis")
        
        conn.close()
    
    def run_all_transformations(self):
        logger.info("Starting ELT transformation process...")
        self.create_dimension_tables()
        self.create_fact_table()
        self.create_business_views()
        logger.info("All transformations completed successfully!")

def main():
    transformer = DataTransformer()
    transformer.run_all_transformations()
    print("\nData transformation complete!")

if __name__ == "__main__":
    main()
