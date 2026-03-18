from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import timedelta
import config
from src.api.models import (
    LoginRequest, Token, User, VulnerabilityMetric, OrganizationMetric,
    ReporterMetric, TimeTrend, SeverityAnalysis, NLPQueryRequest, NLPQueryResponse
)
from src.api.auth import authenticate_user, create_access_token, get_current_user, get_admin_user
from src.database.connection import DatabaseConnection

router = APIRouter()
db = DatabaseConnection()

@router.post("/auth/login", response_model=Token)
async def login(request: LoginRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "organization": user["organization"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    return User(
        username=current_user["username"],
        role=current_user["role"],
        organization=current_user["organization"]
    )

@router.get("/vulnerabilities", response_model=List[VulnerabilityMetric])
async def get_vulnerabilities(
    limit: Optional[int] = 50,
    current_user: dict = Depends(get_current_user)
):
    query = f"""
        SELECT * FROM vw_vulnerability_metrics
        ORDER BY total_reports DESC
        LIMIT {limit}
    """
    results = db.execute_query_dict(query)
    return results

@router.get("/organizations", response_model=List[OrganizationMetric])
async def get_organizations(
    limit: Optional[int] = 50,
    current_user: dict = Depends(get_admin_user)
):
    query = f"""
        SELECT * FROM vw_organization_metrics
        ORDER BY total_reports DESC
        LIMIT {limit}
    """
    results = db.execute_query_dict(query)
    return results

@router.get("/organizations/me", response_model=OrganizationMetric)
async def get_my_organization(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "customer" or not current_user["organization"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required with organization"
        )
    
    query = f"""
        SELECT * FROM vw_organization_metrics
        WHERE team_handle = '{current_user["organization"]}'
    """
    results = db.execute_query_dict(query)
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return results[0]

@router.get("/organizations/{team_handle}/reports")
async def get_organization_reports(
    team_handle: str,
    limit: Optional[int] = 100,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] == "customer":
        if current_user["organization"] != team_handle:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only access your own organization's reports"
            )
    
    query = f"""
        SELECT 
            r.id,
            r.created_at,
            r.disclosed_at,
            r.severity_rating,
            r.severity_score,
            r.bounty_amount,
            r.has_bounty,
            r.vote_count,
            v.weakness_name,
            rep.reporter_username
        FROM fact_reports r
        LEFT JOIN dim_vulnerabilities v ON r.weakness_id = v.weakness_id
        LEFT JOIN dim_reporters rep ON r.reporter_username = rep.reporter_username
        WHERE r.team_handle = '{team_handle}'
        ORDER BY r.created_at DESC
        LIMIT {limit}
    """
    results = db.execute_query_dict(query)
    return results

@router.get("/reporters", response_model=List[ReporterMetric])
async def get_reporters(
    limit: Optional[int] = 50,
    current_user: dict = Depends(get_admin_user)
):
    query = f"""
        SELECT * FROM vw_reporter_metrics
        ORDER BY total_reports DESC
        LIMIT {limit}
    """
    results = db.execute_query_dict(query)
    return results

@router.get("/trends/time", response_model=List[TimeTrend])
async def get_time_trends(current_user: dict = Depends(get_current_user)):
    query = """
        SELECT * FROM vw_time_trends
        ORDER BY month
    """
    results = db.execute_query_dict(query)
    return results

@router.get("/trends/severity", response_model=List[SeverityAnalysis])
async def get_severity_analysis(current_user: dict = Depends(get_current_user)):
    query = """
        SELECT * FROM vw_severity_analysis
        ORDER BY avg_severity_score DESC
    """
    results = db.execute_query_dict(query)
    return results

@router.get("/stats/overview")
async def get_overview_stats(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "customer" and current_user["organization"]:
        query = f"""
            SELECT
                COUNT(DISTINCT id) as total_reports,
                SUM(CASE WHEN has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                ROUND(SUM(bounty_amount), 2) as total_bounty_paid,
                ROUND(AVG(CASE WHEN bounty_amount > 0 THEN bounty_amount END), 2) as avg_bounty,
                COUNT(DISTINCT reporter_username) as unique_reporters,
                COUNT(DISTINCT weakness_id) as unique_vulnerabilities
            FROM fact_reports
            WHERE team_handle = '{current_user["organization"]}'
        """
    else:
        query = """
            SELECT
                COUNT(DISTINCT id) as total_reports,
                SUM(CASE WHEN has_bounty THEN 1 ELSE 0 END) as bounty_reports,
                ROUND(SUM(bounty_amount), 2) as total_bounty_paid,
                ROUND(AVG(CASE WHEN bounty_amount > 0 THEN bounty_amount END), 2) as avg_bounty,
                COUNT(DISTINCT reporter_username) as unique_reporters,
                COUNT(DISTINCT team_handle) as unique_organizations,
                COUNT(DISTINCT weakness_id) as unique_vulnerabilities
            FROM fact_reports
        """
    
    results = db.execute_query_dict(query)
    return results[0] if results else {}

@router.post("/query/nlp", response_model=NLPQueryResponse)
async def nlp_query(
    request: NLPQueryRequest,
    current_user: dict = Depends(get_current_user)
):
    if not config.AI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features not enabled. Please configure OPENAI_API_KEY."
        )
    
    from src.ai.nlp_query import NLPQueryEngine
    
    engine = NLPQueryEngine()
    result = engine.process_query(request.query, current_user)
    
    return result
