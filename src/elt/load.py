import duckdb
import pandas as pd
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, db_path: str = "data/hackerone.duckdb"):
        self.db_path = db_path
        
    def load_csv_to_raw(self, csv_path: str = "data/raw/hackerone_reports.csv"):
        conn = duckdb.connect(self.db_path)
        
        logger.info(f"Loading data from {csv_path} into raw_reports table...")
        
        df = pd.read_csv(csv_path)
        
        logger.info(f"Parsing JSON columns...")
        json_columns = ['reporter', 'team', 'weakness', 'structured_scope']
        
        for col in json_columns:
            if col in df.columns:
                df[f'{col}_parsed'] = df[col].apply(self._safe_json_parse)
        
        df['id'] = df['id'].astype(str)
        df['title'] = df['title'].astype(str)
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df['disclosed_at'] = pd.to_datetime(df['disclosed_at'], errors='coerce')
        
        df['reporter_username'] = df['reporter_parsed'].apply(
            lambda x: x.get('username', '') if isinstance(x, dict) else ''
        )
        df['reporter_name'] = df['reporter_parsed'].apply(
            lambda x: x.get('name', '') if isinstance(x, dict) else ''
        )
        
        df['team_handle'] = df['team_parsed'].apply(
            lambda x: x.get('handle', '') if isinstance(x, dict) else ''
        )
        df['team_name'] = df['team_parsed'].apply(
            lambda x: x.get('profile', {}).get('name', '') if isinstance(x, dict) else ''
        )
        
        df['weakness_id'] = df['weakness_parsed'].apply(
            lambda x: x.get('id', None) if isinstance(x, dict) else None
        )
        df['weakness_name'] = df['weakness_parsed'].apply(
            lambda x: x.get('name', '') if isinstance(x, dict) else ''
        )
        
        df['severity_rating'] = df['severity_rating'] if 'severity_rating' in df.columns else ''
        df['severity_score'] = pd.to_numeric(df['severity_score'], errors='coerce').fillna(0) if 'severity_score' in df.columns else 0
        df['bounty_amount'] = pd.to_numeric(df['bounty_amount'], errors='coerce').fillna(0) if 'bounty_amount' in df.columns else 0
        df['bonus_amount'] = pd.to_numeric(df['bonus_amount'], errors='coerce').fillna(0) if 'bonus_amount' in df.columns else 0
        df['has_bounty'] = df['has_bounty?'].astype(bool) if 'has_bounty?' in df.columns else False
        df['vote_count'] = pd.to_numeric(df['vote_count'], errors='coerce').fillna(0).astype(int)
        df['voter_count'] = pd.to_numeric(df['voter_count'], errors='coerce').fillna(0).astype(int) if 'voter_count' in df.columns else 0
        
        df['state'] = df['state'] if 'state' in df.columns else ''
        df['substate'] = df['substate']
        df['url'] = df['url'] if 'url' in df.columns else ''
        df['source'] = df['source'] if 'source' in df.columns else ''
        df['summary'] = df['summary'] if 'summary' in df.columns else ''
        df['description'] = df['vulnerability_information']
        df['vulnerability_information'] = df['vulnerability_information']
        df['impact'] = df['impact'] if 'impact' in df.columns else ''
        df['original_report_id'] = df['original_report_id'].astype(str)
        df['original_report_url'] = df['original_report_url'] if 'original_report_url' in df.columns else ''
        
        final_df = df[[
            'id', 'title', 'created_at', 'disclosed_at', 'state', 'substate',
            'severity_rating', 'severity_score', 'weakness_id', 'weakness_name',
            'reporter_username', 'reporter_name', 'team_handle', 'team_name',
            'bounty_amount', 'bonus_amount', 'has_bounty', 'vote_count', 'voter_count',
            'url', 'source', 'summary', 'description', 'vulnerability_information',
            'impact', 'original_report_id', 'original_report_url'
        ]]
        
        conn.execute("DELETE FROM raw_reports")
        
        conn.register('df_view', final_df)
        conn.execute("INSERT INTO raw_reports SELECT * FROM df_view")
        
        count = conn.execute("SELECT COUNT(*) FROM raw_reports").fetchone()[0]
        logger.info(f"Loaded {count:,} records into raw_reports table")
        
        conn.close()
        return count
    
    def _safe_json_parse(self, value):
        if pd.isna(value):
            return {}
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                import ast
                return ast.literal_eval(value)
            except:
                try:
                    return json.loads(value)
                except:
                    return {}
        return {}

def main():
    loader = DataLoader()
    count = loader.load_csv_to_raw()
    print(f"\nData loading complete! {count:,} records loaded into DuckDB.")

if __name__ == "__main__":
    main()
