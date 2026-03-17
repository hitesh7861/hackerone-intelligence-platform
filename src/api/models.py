from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    role: str
    organization: Optional[str] = None

class VulnerabilityMetric(BaseModel):
    weakness_name: str
    total_reports: int
    bounty_reports: int
    avg_bounty: Optional[float]
    max_bounty: Optional[float]
    avg_votes: Optional[float]
    bounty_rate: Optional[float]

class OrganizationMetric(BaseModel):
    team_handle: str
    team_name: str
    total_reports: int
    bounty_reports: int
    total_bounty_paid: Optional[float]
    avg_bounty: Optional[float]
    avg_votes: Optional[float]
    bounty_rate: Optional[float]
    first_report_date: Optional[datetime]
    latest_report_date: Optional[datetime]

class ReporterMetric(BaseModel):
    reporter_username: str
    reporter_name: str
    total_reports: int
    bounty_reports: int
    total_earnings: Optional[float]
    avg_bounty: Optional[float]
    avg_votes: Optional[float]
    bounty_rate: Optional[float]
    first_report_date: Optional[datetime]
    latest_report_date: Optional[datetime]

class TimeTrend(BaseModel):
    month: datetime
    total_reports: int
    bounty_reports: int
    total_bounty: Optional[float]
    avg_bounty: Optional[float]
    active_organizations: int
    active_reporters: int

class SeverityAnalysis(BaseModel):
    severity_rating: str
    total_reports: int
    bounty_reports: int
    avg_severity_score: Optional[float]
    avg_bounty: Optional[float]
    bounty_rate: Optional[float]

class NLPQueryRequest(BaseModel):
    query: str

class NLPQueryResponse(BaseModel):
    query: str
    sql_generated: str
    results: List[dict]
    explanation: str
