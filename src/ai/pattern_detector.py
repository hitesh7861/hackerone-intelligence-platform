from openai import OpenAI
from src import config
from src.database.connection import DatabaseConnection
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VulnerabilityPatternDetector:
    def __init__(self):
        if not config.AI_ENABLED:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.db = DatabaseConnection()
    
    def detect_emerging_patterns(self):
        query = """
            SELECT 
                DATE_TRUNC('month', created_at) as month,
                v.weakness_name,
                COUNT(*) as report_count,
                ROUND(AVG(f.bounty_amount), 2) as avg_bounty
            FROM fact_reports f
            JOIN dim_vulnerabilities v ON f.weakness_id = v.weakness_id
            WHERE created_at >= CURRENT_DATE - INTERVAL '12 months'
            GROUP BY DATE_TRUNC('month', created_at), v.weakness_name
            ORDER BY month DESC, report_count DESC
        """
        
        df = self.db.execute_query(query)
        
        recent_trends = df.groupby('weakness_name').agg({
            'report_count': 'sum',
            'avg_bounty': 'mean'
        }).sort_values('report_count', ascending=False).head(10)
        
        trend_data = recent_trends.to_dict('index')
        
        prompt = f"""Analyze these vulnerability trends from the last 12 months:

{trend_data}

Identify:
1. Top 3 emerging vulnerability patterns
2. Vulnerabilities showing increasing frequency
3. Security recommendations for organizations

Provide insights in a structured format.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a security analyst identifying vulnerability trends."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content.strip()
            
            return {
                "analysis": analysis,
                "data": trend_data
            }
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {"error": str(e)}
    
    def predict_high_value_vulnerabilities(self, organization: str = None):
        if organization:
            query = f"""
                SELECT 
                    v.weakness_name,
                    COUNT(*) as historical_count,
                    ROUND(AVG(f.bounty_amount), 2) as avg_bounty,
                    ROUND(MAX(f.bounty_amount), 2) as max_bounty,
                    ROUND(AVG(f.severity_score), 2) as avg_severity
                FROM fact_reports f
                JOIN dim_vulnerabilities v ON f.weakness_id = v.weakness_id
                WHERE f.team_handle = '{organization}' AND f.bounty_amount > 0
                GROUP BY v.weakness_name
                ORDER BY avg_bounty DESC
                LIMIT 10
            """
        else:
            query = """
                SELECT 
                    v.weakness_name,
                    COUNT(*) as historical_count,
                    ROUND(AVG(f.bounty_amount), 2) as avg_bounty,
                    ROUND(MAX(f.bounty_amount), 2) as max_bounty,
                    ROUND(AVG(f.severity_score), 2) as avg_severity
                FROM fact_reports f
                JOIN dim_vulnerabilities v ON f.weakness_id = v.weakness_id
                WHERE f.bounty_amount > 0
                GROUP BY v.weakness_name
                ORDER BY avg_bounty DESC
                LIMIT 10
            """
        
        results = self.db.execute_query_dict(query)
        
        prompt = f"""Based on this historical data, predict which vulnerability types are most likely to yield high bounties:

{results}

Provide:
1. Top 3 vulnerability types to focus on
2. Expected bounty range for each
3. Why these are valuable
4. Skills needed to find them

Keep it actionable and data-driven.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a bug bounty strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            prediction = response.choices[0].message.content.strip()
            
            return {
                "prediction": prediction,
                "data": results
            }
            
        except Exception as e:
            logger.error(f"Error predicting vulnerabilities: {e}")
            return {"error": str(e)}
    
    def generate_security_recommendations(self, organization: str):
        query = f"""
            SELECT 
                v.weakness_name,
                COUNT(*) as total_reports,
                SUM(CASE WHEN f.has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                ROUND(AVG(f.severity_score), 2) as avg_severity,
                ROUND(SUM(f.bounty_amount), 2) as total_paid
            FROM fact_reports f
            JOIN dim_vulnerabilities v ON f.weakness_id = v.weakness_id
            WHERE f.team_handle = '{organization}'
            GROUP BY v.weakness_name
            ORDER BY total_reports DESC
            LIMIT 5
        """
        
        results = self.db.execute_query_dict(query)
        
        if not results:
            return {"error": "No data found for organization"}
        
        prompt = f"""As a security consultant, provide recommendations for this organization based on their vulnerability history:

{results}

Provide:
1. Top 3 security priorities
2. Specific remediation steps
3. Training recommendations
4. Expected impact of improvements

Be specific and actionable.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a CISO providing security recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            recommendations = response.choices[0].message.content.strip()
            
            return {
                "organization": organization,
                "recommendations": recommendations,
                "vulnerability_data": results
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {"error": str(e)}
