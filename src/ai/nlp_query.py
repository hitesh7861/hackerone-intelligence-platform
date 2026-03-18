from openai import OpenAI
from src import config
from src.database.connection import DatabaseConnection
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPQueryEngine:
    def __init__(self):
        logger.info("Initializing NLP Query Engine...")
        
        if not config.AI_ENABLED:
            logger.error("OpenAI API key not configured")
            raise ValueError("OpenAI API key not configured")
        
        logger.info(f"OpenAI API key configured: {config.OPENAI_API_KEY[:10]}...")
        
        # Use OpenAI 1.0+ API with minimal parameters
        try:
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            logger.info("OpenAI client created successfully")
        except Exception as e:
            logger.error(f"Failed to create OpenAI client: {e}")
            raise
        
        self.db = DatabaseConnection()
        logger.info("NLP Query Engine initialized successfully")
        
        self.schema_context = """
        Database: DuckDB
        
        Tables:
        1. fact_reports: Main fact table with report details
           - id (VARCHAR): Unique report identifier
           - created_at (TIMESTAMP): Report creation date
           - disclosed_at (TIMESTAMP): Report disclosure date
           - weakness_id (VARCHAR): Foreign key to dim_vulnerabilities
           - reporter_username (VARCHAR): Reporter username
           - team_handle (VARCHAR): Foreign key to dim_organizations
           - severity_rating (VARCHAR): Severity level (e.g., 'critical', 'high', 'medium', 'low')
           - severity_score (DOUBLE): Numeric severity score
           - bounty_amount (DOUBLE): Bounty amount in USD
           - has_bounty (BOOLEAN): Whether bounty was awarded
           - vote_count (INTEGER): Number of votes
        
        2. dim_vulnerabilities: Vulnerability dimension
           - weakness_id (VARCHAR): Primary key
           - weakness_name (VARCHAR): Vulnerability type name
        
        3. dim_organizations: Organization dimension
           - team_handle (VARCHAR): Primary key
           - team_name (VARCHAR): Organization name
           - first_report_date (TIMESTAMP): First report date
           - latest_report_date (TIMESTAMP): Latest report date
        
        4. dim_researchers: Researcher dimension
           - reporter_username (VARCHAR): Primary key
           - total_reports (INTEGER): Total number of reports
        
        IMPORTANT NOTES:
        - To count researchers: Use COUNT(DISTINCT reporter_username) FROM fact_reports
        - To count organizations: Use COUNT(DISTINCT team_handle) FROM fact_reports
        - To count vulnerabilities: Use COUNT(DISTINCT weakness_id) FROM fact_reports
        - The dim_* tables are for detailed info, but counts should come from fact_reports
        
        DuckDB Syntax Rules (IMPORTANT):
        - Use TIMESTAMP type for dates (not DATETIME)
        - Date difference: date_diff('day', date1, date2) or EXTRACT(day FROM date2 - date1)
        - JOIN syntax: JOIN table_name ON condition (use proper ON keyword)
        - String comparison is case-sensitive
        - Use CAST() for type conversions
        - Aggregate functions: COUNT(), SUM(), AVG(), MAX(), MIN()
        - Always use proper table aliases in JOINs
        
        Example Queries:
        - Total reports: SELECT COUNT(*) FROM fact_reports
        - Total researchers: SELECT COUNT(DISTINCT reporter_username) FROM fact_reports
        - Total organizations: SELECT COUNT(DISTINCT team_handle) FROM fact_reports
        - With JOIN: SELECT o.team_name, COUNT(*) FROM fact_reports r JOIN dim_organizations o ON r.team_handle = o.team_handle GROUP BY o.team_name
        - Date diff: SELECT AVG(date_diff('day', created_at, disclosed_at)) FROM fact_reports WHERE disclosed_at IS NOT NULL
        """
    
    def process_query(self, user_query: str, current_user: dict, conversation_history: list = None):
        logger.info(f"Processing NLP query: {user_query}")
        
        if conversation_history is None:
            conversation_history = []
        
        user_context = ""
        if current_user["role"] == "customer" and current_user["organization"]:
            user_context = f"\nUser is a customer with organization: {current_user['organization']}. Filter results to this organization only."
        
        # Build conversation context from history (last 5 messages)
        conversation_context = ""
        if conversation_history:
            recent_history = conversation_history[-5:]  # Last 5 messages
            conversation_context = "\n\nConversation History:\n"
            for msg in recent_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')[:200]  # Truncate long messages
                conversation_context += f"{role}: {content}\n"
        
        # First, check if this is a conversational query or a data query
        classification_prompt = f"""Classify this user message as either 'conversation' or 'data_query':

{conversation_context}

Current user message: "{user_query}"

Rules:
- 'conversation': greetings (hi, hello, hey), thanks, casual chat, questions about the assistant itself, questions about the dashboard/platform features, what tabs do, how to use the platform
- 'data_query': specific questions about vulnerability data, counts, statistics, trends that require querying the database

Respond with ONLY one word: conversation or data_query"""

        try:
            logger.info("Classifying query type...")
            classification = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a query classifier. Respond with only 'conversation' or 'data_query'."},
                    {"role": "user", "content": classification_prompt}
                ],
                temperature=0,
                max_tokens=10
            )
            
            query_type = classification.choices[0].message.content.strip().lower()
            logger.info(f"Query classified as: {query_type}")
            
            # Handle conversational queries
            if query_type == "conversation":
                logger.info("Handling conversational query...")
                
                platform_context = """
You are an AI assistant for the HackerOne Intelligence Platform. Here's what you should know:

**Platform Overview:**
This is an enterprise vulnerability intelligence platform that analyzes 10,000+ real HackerOne vulnerability reports.

**Dashboard Pages:**
1. **Dashboard** - Overview with key metrics (total reports, bounty rate, top vulnerabilities and organizations)
2. **Security Threats** - Deep dive into vulnerability types, severity analysis, and risk assessment
3. **Companies** - Organization performance metrics, bounty statistics, and top performers
4. **Researchers** - Security researcher analytics, top contributors, and their impact
5. **Timeline & Patterns** - Time-series trends, monthly activity, and pattern analysis
6. **Intelligence Reports** - Detailed vulnerability reports with AI-powered summaries
7. **Knowledge Base** - Glossary of vulnerability types and security terms
8. **Search & Export** - Advanced search and data export functionality
9. **AI Assistant** (this page) - Natural language interface to query and explore the data

**Key Features:**
- Interactive visualizations with Plotly charts
- AI-powered insights and report summarization
- Conversation memory (remembers last 5 messages)
- One-click data refresh
- Role-based access (admin vs customer views)
- Export data to CSV

**What I Can Help With:**
- Answer questions about the platform and its features
- Explain what different tabs/pages do
- Query the vulnerability database using natural language
- Provide statistics and trends about vulnerabilities, organizations, and researchers
- Summarize vulnerability reports
"""
                
                conversation_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": platform_context},
                        {"role": "user", "content": user_query}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                
                response_text = conversation_response.choices[0].message.content.strip()
                
                return {
                    "query": user_query,
                    "sql_generated": None,
                    "results": [],
                    "explanation": response_text
                }
            
            # Handle data queries - generate SQL
            logger.info("Handling data query - generating SQL...")
            prompt = f"""You are a SQL expert for a vulnerability intelligence database.
        
{self.schema_context}

{user_context}

{conversation_context}

Current user query: {user_query}

Generate a DuckDB SQL query to answer this question. Consider the conversation history for context (e.g., follow-up questions).
Return ONLY the SQL query, no explanations.
The query should be safe, read-only, and properly formatted.
"""
        
            logger.info("Calling OpenAI API for SQL generation...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate only valid DuckDB SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            logger.info("OpenAI API call successful")
            sql_query = response.choices[0].message.content.strip()
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            logger.info(f"Generated SQL: {sql_query}")
            
            logger.info("Executing SQL query...")
            results = self.db.execute_query_dict(sql_query)
            logger.info(f"Query returned {len(results)} results")
            
            logger.info("Generating explanation...")
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
