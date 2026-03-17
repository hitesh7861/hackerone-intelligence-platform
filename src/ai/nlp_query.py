from openai import OpenAI
from src import config
from src.database.connection import DatabaseConnection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPQueryEngine:
    def __init__(self):
        if not config.AI_ENABLED:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.db = DatabaseConnection()
        
        self.schema_context = """
        Database Schema:
        
        Tables:
        1. fact_reports: Main fact table with report details
           - id, created_at, disclosed_at, weakness_id, reporter_username, team_handle
           - severity_rating, severity_score, bounty_amount, has_bounty, vote_count
        
        2. dim_vulnerabilities: Vulnerability dimension
           - weakness_id, weakness_name
        
        3. dim_organizations: Organization dimension
           - team_handle, team_name, first_report_date, latest_report_date
        
        4. dim_reporters: Reporter dimension
           - reporter_username, reporter_name, first_report_date, latest_report_date
        
        Views:
        - vw_vulnerability_metrics: Aggregated vulnerability statistics
        - vw_organization_metrics: Organization performance metrics
        - vw_reporter_metrics: Reporter performance metrics
        - vw_time_trends: Monthly trend analysis
        - vw_severity_analysis: Severity-based analysis
        """
    
    def process_query(self, user_query: str, current_user: dict):
        logger.info(f"Processing NLP query: {user_query}")
        
        user_context = ""
        if current_user["role"] == "customer" and current_user["organization"]:
            user_context = f"\nUser is a customer with organization: {current_user['organization']}. Filter results to this organization only."
        
        prompt = f"""You are a SQL expert for a vulnerability intelligence database.
        
{self.schema_context}

{user_context}

User query: {user_query}

Generate a DuckDB SQL query to answer this question. Return ONLY the SQL query, no explanations.
The query should be safe, read-only, and properly formatted.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate only valid DuckDB SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            logger.info(f"Generated SQL: {sql_query}")
            
            results = self.db.execute_query_dict(sql_query)
            
            explanation = self._generate_explanation(user_query, sql_query, results)
            
            return {
                "query": user_query,
                "sql_generated": sql_query,
                "results": results[:100],
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"Error processing NLP query: {e}")
            return {
                "query": user_query,
                "sql_generated": "",
                "results": [],
                "explanation": f"Error processing query: {str(e)}"
            }
    
    def _generate_explanation(self, user_query: str, sql_query: str, results: list):
        if not results:
            return "No results found for your query."
        
        result_summary = f"Found {len(results)} result(s)."
        
        if len(results) > 0:
            first_result = results[0]
            result_summary += f" Sample data: {first_result}"
        
        return result_summary
