from openai import OpenAI
import config
from src.database.connection import DatabaseConnection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportSummarizer:
    def __init__(self):
        if not config.AI_ENABLED:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.db = DatabaseConnection()
    
    def summarize_report(self, report_id: str):
        query = f"""
            SELECT 
                r.id,
                r.title,
                r.summary,
                r.description,
                r.vulnerability_information,
                r.impact,
                r.severity_rating,
                r.bounty_amount,
                v.weakness_name,
                o.team_name
            FROM raw_reports r
            LEFT JOIN dim_vulnerabilities v ON r.weakness_id = v.weakness_id
            LEFT JOIN dim_organizations o ON r.team_handle = o.team_handle
            WHERE r.id = '{report_id}'
        """
        
        results = self.db.execute_query_dict(query)
        
        if not results:
            return {"error": "Report not found"}
        
        report = results[0]
        
        prompt = f"""Summarize this vulnerability report in a concise, executive-friendly format:

Title: {report.get('title', 'N/A')}
Vulnerability Type: {report.get('weakness_name', 'N/A')}
Organization: {report.get('team_name', 'N/A')}
Severity: {report.get('severity_rating', 'N/A')}
Bounty: ${report.get('bounty_amount', 0)}

Description: {report.get('vulnerability_information', report.get('description', 'N/A'))}

Impact: {report.get('impact', 'N/A')}

Provide:
1. One-sentence summary
2. Key risk
3. Business impact
4. Recommended action

Keep it under 150 words.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity analyst providing executive summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                "report_id": report_id,
                "original_title": report.get('title'),
                "vulnerability_type": report.get('weakness_name'),
                "severity": report.get('severity_rating'),
                "bounty": report.get('bounty_amount'),
                "ai_summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error summarizing report: {e}")
            return {"error": str(e)}
    
    def batch_summarize_top_vulnerabilities(self, limit: int = 5):
        query = f"""
            SELECT 
                v.weakness_name,
                COUNT(*) as total_reports,
                ROUND(AVG(f.bounty_amount), 2) as avg_bounty,
                ROUND(AVG(f.severity_score), 2) as avg_severity
            FROM fact_reports f
            JOIN dim_vulnerabilities v ON f.weakness_id = v.weakness_id
            GROUP BY v.weakness_name
            ORDER BY total_reports DESC
            LIMIT {limit}
        """
        
        results = self.db.execute_query_dict(query)
        
        summaries = []
        for vuln in results:
            prompt = f"""Provide a brief security insight about {vuln['weakness_name']} vulnerability:
            
Statistics:
- Total reports: {vuln['total_reports']}
- Average bounty: ${vuln['avg_bounty']}
- Average severity: {vuln['avg_severity']}

In 2-3 sentences, explain:
1. What this vulnerability is
2. Why it's common
3. Key mitigation strategy
"""
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a cybersecurity expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=150
                )
                
                insight = response.choices[0].message.content.strip()
                
                summaries.append({
                    "vulnerability": vuln['weakness_name'],
                    "total_reports": vuln['total_reports'],
                    "avg_bounty": vuln['avg_bounty'],
                    "insight": insight
                })
                
            except Exception as e:
                logger.error(f"Error generating insight: {e}")
                continue
        
        return summaries
