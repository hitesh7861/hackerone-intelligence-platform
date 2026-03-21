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
        
        Always use the pre-aggregated VIEWS for queries, NOT the raw tables!
        
        Available Business Views (USE THESE):
        
        1. vw_vulnerability_metrics - Vulnerability statistics
           - weakness_name (VARCHAR): Vulnerability type name
           - total_reports (INTEGER): Total number of reports
           - bounty_reports (INTEGER): Number of reports with bounties
           - avg_votes (DOUBLE): Average votes per report
           - bounty_rate (DOUBLE): Percentage of reports with bounties (0-100)
        
        2. vw_organization_metrics - Organization statistics
           - team_handle (VARCHAR): Organization identifier
           - team_name (VARCHAR): Organization name
           - total_reports (INTEGER): Total reports for this org
           - bounty_reports (INTEGER): Reports with bounties
           - avg_votes (DOUBLE): Average votes
           - bounty_rate (DOUBLE): Percentage with bounties (0-100)
           - first_report_date (TIMESTAMP): First report date
           - latest_report_date (TIMESTAMP): Latest report date
        
        3. vw_reporter_metrics - Reporter/researcher statistics
           - reporter_username (VARCHAR): Reporter username
           - reporter_name (VARCHAR): Reporter display name
           - total_reports (INTEGER): Total reports
           - bounty_reports (INTEGER): Reports with bounties
           - avg_votes (DOUBLE): Average votes
           - bounty_rate (DOUBLE): Percentage with bounties (0-100)
           - first_report_date (TIMESTAMP): First report
           - latest_report_date (TIMESTAMP): Latest report
        
        4. vw_time_trends - Monthly trends
           - month (TIMESTAMP): Month
           - total_reports (INTEGER): Reports in month
           - bounty_reports (INTEGER): Bounty reports
           - active_organizations (INTEGER): Active orgs
           - active_reporters (INTEGER): Active reporters
        
        Example Queries (COPY THESE PATTERNS):
        - High bounty rate vulnerabilities: SELECT * FROM vw_vulnerability_metrics WHERE bounty_rate > 70 ORDER BY bounty_rate DESC LIMIT 10
        - Top vulnerabilities: SELECT * FROM vw_vulnerability_metrics ORDER BY total_reports DESC LIMIT 10
        - Best organizations: SELECT * FROM vw_organization_metrics ORDER BY bounty_rate DESC LIMIT 10
        - Top reporters: SELECT * FROM vw_reporter_metrics ORDER BY total_reports DESC LIMIT 10
        - All vulnerabilities: SELECT * FROM vw_vulnerability_metrics ORDER BY total_reports DESC
        - All organizations: SELECT * FROM vw_organization_metrics ORDER BY total_reports DESC
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
        
        # Keyword-based classification (skip AI for most questions)
        query_lower = user_query.lower()
        
        # Check for explicit data requests FIRST - highest priority
        if any(keyword in query_lower for keyword in [
            'show me', 'show all', 'list all', 'list the', 'give me', 'give all',
            'display the', 'display all',
            'which vulnerabilities', 'which organizations', 'which reporters', 'which',
            'top 5', 'top 10', 'top vulnerabilities', 'top organizations',
            'highest bounty', 'lowest bounty', 'best programs', 'worst programs', 'best security',
            'find vulnerabilities', 'find organizations', 'find reporters',
            'search for', 'get all', 'fetch all',
            'how many vulnerabilities', 'how many organizations', 'how many reporters',
            'vulnerabilities with', 'organizations with', 'reporters with'
        ]):
            logger.info("Explicit data request detected - using data_query mode")
            query_type = "data_query"
        # Check for greetings and general questions (only if NOT a data query)
        elif any(phrase in query_lower for phrase in [
            'hello', 'hi', 'hey', 'thanks', 'thank you', 'good morning', 'good afternoon',
            'what is this', 'what is the', 'tell me about', 'explain', 'how does',
            'what does', 'can you tell', 'describe', 'what\'s this', 'whats this'
        ]):
            logger.info("Greeting or general question detected - using conversation mode")
            query_type = "conversation"
        # Default to insight mode for everything else
        else:
            logger.info("No special keywords - defaulting to insight mode for conversational analysis")
            query_type = "insight"
        
        try:
            
            # Handle conversational queries
            if query_type == "conversation":
                logger.info("Handling conversational query...")
                
                try:
                    platform_context = """You are a friendly AI assistant for the HackerOne Intelligence Platform. Be helpful and concise.

The platform analyzes 10,000+ vulnerability reports with features like:
- Interactive dashboards with key metrics
- AI-powered insights
- Multiple pages: Dashboard, Security Threats, Companies, Researchers, Timeline, Reports, Knowledge Base, Search, and AI Assistant

You can help users understand the platform or query the vulnerability data."""
                    
                    conversation_response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": platform_context},
                            {"role": "user", "content": user_query}
                        ],
                        temperature=0.7,
                        max_tokens=200
                    )
                    
                    response_text = conversation_response.choices[0].message.content.strip()
                    logger.info(f"Conversational response generated successfully")
                    
                    return {
                        "query": user_query,
                        "sql_generated": None,
                        "results": [],
                        "explanation": response_text
                    }
                except Exception as conv_error:
                    logger.error(f"Error in conversational response: {conv_error}")
                    return {
                        "query": user_query,
                        "sql_generated": None,
                        "results": [],
                        "explanation": "Hello! I'm the AI assistant for the HackerOne Intelligence Platform. I can help you explore vulnerability data or answer questions about the platform. What would you like to know?"
                    }
            
            # Handle insight queries - fetch data and provide conversational analysis
            if query_type == "insight":
                logger.info("Handling insight query - fetching data and generating analysis...")
                
                try:
                    # First, generate SQL to get relevant data
                    sql_prompt = f"""Generate a SQL query to fetch relevant data for this question: "{user_query}"

{self.schema_context}

Return ONLY the SQL query. Keep it simple and limit to 20 rows max."""
                    
                    sql_response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a SQL expert. Generate only valid DuckDB SQL queries."},
                            {"role": "user", "content": sql_prompt}
                        ],
                        temperature=0.1,
                        max_tokens=300
                    )
                    
                    sql_query = sql_response.choices[0].message.content.strip()
                    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
                    logger.info(f"Generated SQL for insights: {sql_query}")
                    
                    # Execute query
                    results = self.db.execute_query_dict(sql_query)
                    logger.info(f"Query returned {len(results)} results")
                    
                    # Generate conversational analysis based on the data
                    analysis_prompt = f"""Answer this question in MAXIMUM 2 sentences: "{user_query}"

Data: {results[:5] if len(results) > 5 else results}
Total: {len(results)} records

Rules:
- MAXIMUM 2 sentences
- State the key number/finding first
- Add ONE brief insight
- NO extra details or explanations"""
                    
                    analysis_response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a data analyst. Answer in EXACTLY 1-2 sentences. Be extremely concise. State facts only."},
                            {"role": "user", "content": analysis_prompt}
                        ],
                        temperature=0.3,
                        max_tokens=150
                    )
                    
                    analysis_text = analysis_response.choices[0].message.content.strip()
                    logger.info("Insight analysis generated successfully")
                    
                    return {
                        "query": user_query,
                        "sql_generated": None,  # Don't show SQL for insights
                        "results": [],  # Don't show raw table
                        "explanation": analysis_text
                    }
                except Exception as insight_error:
                    logger.error(f"Error in insight generation: {insight_error}")
                    return {
                        "query": user_query,
                        "sql_generated": None,
                        "results": [],
                        "explanation": "I can help you understand the vulnerability data. Could you rephrase your question or ask for specific details?"
                    }
            
            # Handle data queries - generate SQL and show tables
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
