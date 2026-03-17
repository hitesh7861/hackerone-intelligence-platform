import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path
import base64

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.database.connection import DatabaseConnection
from src import config

st.set_page_config(
    page_title="HackerOne Intelligence Platform",
    page_icon="H1",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Essential CSS - Cleaned up
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background-color: #0a0a0a;
    }
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1800px;
        background-color: #0a0a0a;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        min-width: 21rem !important;
        max-width: 21rem !important;
        border-right: 1px solid #444444 !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #000000 !important;
        min-height: 100vh !important;
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    button[data-testid="collapsedControl"] {
        display: block !important;
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] label {
        font-size: 1rem !important;
        line-height: 1.3 !important;
        padding: 0.15rem 0 !important;
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 0.05rem !important;
    }
    
    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
        border: 0 !important;
        border-top: 2px solid #666666 !important;
        opacity: 1 !important;
        height: 0 !important;
        background: transparent !important;
        display: block !important;
        visibility: visible !important;
        width: 100% !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        padding: 0.1rem 0 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
    
    [data-testid="stSidebar"] p {
        font-size: 0.75rem !important;
    }
    
    /* Disable Sidebar Scrolling */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div:first-child {
        overflow: hidden !important;
    }
    
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] > div {
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }
    
    [data-testid="stSidebar"]::-webkit-scrollbar,
    [data-testid="stSidebar"] *::-webkit-scrollbar {
        display: none !important;
    }
    
    /* Headers */
    h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    
    h2 {
        color: #e5e5e5;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.25rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 600;
        color: #737373;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* DataFrames */
    .dataframe {
        background-color: #0f0f0f !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 8px;
    }
    
    .dataframe th {
        background-color: #141414 !important;
        color: #e5e5e5 !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase;
        padding: 1rem !important;
        border-bottom: 2px solid #1a1a1a !important;
    }
    
    .dataframe td {
        background-color: #0f0f0f !important;
        color: #d4d4d4 !important;
        font-size: 0.9375rem !important;
        padding: 0.875rem 1rem !important;
        border-bottom: 1px solid #1a1a1a !important;
    }
    
    .dataframe td,
    .dataframe td *,
    [data-testid="stDataFrame"] td,
    [data-testid="stDataFrame"] td * {
        color: #d4d4d4 !important;
    }
    
    .dataframe tr:hover td {
        background-color: #141414 !important;
    }
    
    .dataframe tr:hover td,
    .dataframe tr:hover td * {
        color: #e5e5e5 !important;
    }
    
    /* Plotly Charts */
    .js-plotly-plot {
        background-color: transparent !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #262626;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #404040;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_db_connection():
    return DatabaseConnection()

db = get_db_connection()

# Sidebar
with st.sidebar:
    # HackerOne Logo
    logo_path = Path(__file__).parent / "assets" / "h1.jpg"
    if logo_path.exists():
        import base64
        with open(str(logo_path), 'rb') as f:
            logo_data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style='background: #000000; padding: 0 0.5rem; border-radius: 8px; margin: -1rem 0.5rem 0.3rem 0.5rem;'>
                <div style='text-align: center;'>
                    <img src='data:image/jpeg;base64,{logo_data}' style='width: 70px; border-radius: 6px;'/>
                    <p style='color: #888888; font-size: 0.75rem; margin: 0.3rem 0 0 0; font-weight: 500;'>Security Research Platform</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='background: #000000; padding: 0 0.5rem; border-radius: 8px; margin: -1rem 0.5rem 0.3rem 0.5rem;'>
                <div style='text-align: center;'>
                    <h1 style='color: #ffffff; font-size: 1rem; margin: 0; font-weight: 700;'>HackerOne</h1>
                    <p style='color: #a0a0a0; font-size: 0.7rem; margin: 0.1rem 0 0 0;'>Intelligence Platform</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["Dashboard", "Security Threats", "Companies", "Researchers", 
         "Timeline & Patterns", "Intelligence Reports", "AI Assistant", "Knowledge Base", "Search & Export"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick Stats
    try:
        stats = db.execute_query("""
            SELECT 
                COUNT(DISTINCT id) as reports,
                COUNT(DISTINCT team_handle) as orgs,
                COUNT(DISTINCT reporter_username) as researchers
            FROM raw_reports
        """).iloc[0]
        
        st.markdown("<p style='color: #737373; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; font-weight: 600;'>Platform Stats</p>", unsafe_allow_html=True)
        st.metric("Total Reports", f"{int(stats['reports']):,}")
        st.metric("Organizations", f"{int(stats['orgs']):,}")
        st.metric("Researchers", f"{int(stats['researchers']):,}")
    except:
        pass

# Main content - Dashboard page
if page == "Dashboard":
    st.title("Dashboard")
    
    # Key metrics
    metrics = db.execute_query("""
        SELECT
            COUNT(DISTINCT id) as total_reports,
            SUM(CASE WHEN has_bounty THEN 1 ELSE 0 END) as bounty_reports,
            COUNT(DISTINCT weakness_id) as vulnerability_types,
            COUNT(DISTINCT team_handle) as organizations,
            COUNT(DISTINCT reporter_username) as researchers
        FROM fact_reports
    """).iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reports", f"{int(metrics['total_reports']):,}")
    with col2:
        st.metric("Bounty Reports", f"{int(metrics['bounty_reports']):,}")
    with col3:
        st.metric("Vulnerability Types", f"{int(metrics['vulnerability_types']):,}")
    with col4:
        bounty_rate = (metrics['bounty_reports'] / metrics['total_reports'] * 100)
        st.metric("Bounty Rate", f"{bounty_rate:.1f}%")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Vulnerabilities")
        top_vulns = db.execute_query("""
            SELECT weakness_name, total_reports
            FROM vw_vulnerability_metrics
            ORDER BY total_reports DESC
            LIMIT 10
        """)
        
        fig = px.bar(top_vulns, x='total_reports', y='weakness_name',
                     orientation='h',
                     labels={'total_reports': 'Reports', 'weakness_name': ''})
        fig.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a3a3a3', size=12),
            xaxis=dict(gridcolor='#1a1a1a'),
            yaxis=dict(categoryorder='total ascending', gridcolor='#1a1a1a'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        fig.update_traces(marker_color='#8b5cf6')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top 10 Organizations")
        top_orgs = db.execute_query("""
            SELECT team_name, total_reports
            FROM vw_organization_metrics
            ORDER BY total_reports DESC
            LIMIT 10
        """)
        
        fig = px.bar(top_orgs, x='total_reports', y='team_name',
                     orientation='h',
                     labels={'total_reports': 'Reports', 'team_name': ''})
        fig.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a3a3a3', size=12),
            xaxis=dict(gridcolor='#1a1a1a'),
            yaxis=dict(categoryorder='total ascending', gridcolor='#1a1a1a'),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        fig.update_traces(marker_color='#10b981')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Recent Activity")
    recent = db.execute_query("""
        SELECT id, title, team_name, weakness_name, created_at, 
               CASE WHEN has_bounty THEN 'Yes' ELSE 'No' END as bounty
        FROM raw_reports
        WHERE created_at IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 15
    """)
    st.dataframe(recent, use_container_width=True, height=400)

# Import remaining pages from backup
elif page == "Security Threats":
    st.title("Security Threats Analysis")
    
    vuln_df = db.execute_query("""
        SELECT * FROM vw_vulnerability_metrics
        ORDER BY total_reports DESC
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Types", len(vuln_df))
    with col2:
        st.metric("Avg Severity", f"{vuln_df['avg_severity'].mean():.2f}")
    with col3:
        st.metric("Avg Bounty Rate", f"{vuln_df['bounty_rate'].mean():.1f}%")
    with col4:
        st.metric("Total Reports", f"{vuln_df['total_reports'].sum():,}")
    
    st.markdown("---")
    
    st.dataframe(
        vuln_df[['weakness_name', 'total_reports', 'bounty_reports', 'avg_severity', 'bounty_rate']],
        use_container_width=True,
        height=600
    )

elif page == "Companies":
    st.title("Company Performance")
    
    org_df = db.execute_query("""
        SELECT * FROM vw_organization_metrics
        ORDER BY total_reports DESC
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Organizations", len(org_df))
    with col2:
        st.metric("Avg Reports/Org", f"{org_df['total_reports'].mean():.0f}")
    with col3:
        st.metric("Avg Bounty Rate", f"{org_df['bounty_rate'].mean():.1f}%")
    with col4:
        st.metric("Total Reports", f"{org_df['total_reports'].sum():,}")
    
    st.markdown("---")
    
    st.dataframe(
        org_df[['team_name', 'total_reports', 'bounty_reports', 'avg_severity', 'bounty_rate']],
        use_container_width=True,
        height=600
    )

elif page == "Researchers":
    st.title("Researcher Performance")
    
    researcher_df = db.execute_query("""
        SELECT * FROM vw_reporter_metrics
        ORDER BY total_reports DESC
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Researchers", len(researcher_df))
    with col2:
        st.metric("Avg Reports", f"{researcher_df['total_reports'].mean():.0f}")
    with col3:
        st.metric("Avg Bounty Rate", f"{researcher_df['bounty_rate'].mean():.1f}%")
    with col4:
        st.metric("Total Reports", f"{researcher_df['total_reports'].sum():,}")
    
    st.markdown("---")
    
    st.dataframe(
        researcher_df[['reporter_username', 'total_reports', 'bounty_reports', 'avg_severity', 'bounty_rate']].head(100),
        use_container_width=True,
        height=600
    )

elif page == "Timeline & Patterns":
    st.title("Timeline & Pattern Analysis")
    
    trend_df = db.execute_query("""
        SELECT * FROM vw_time_trends
        ORDER BY month
    """)
    
    st.subheader("Report Volume Over Time")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend_df['month'], y=trend_df['total_reports'],
                             mode='lines+markers', name='Total Reports', line=dict(width=3, color='#8b5cf6')))
    fig.add_trace(go.Scatter(x=trend_df['month'], y=trend_df['bounty_reports'],
                             mode='lines+markers', name='Bounty Reports', line=dict(width=3, color='#10b981')))
    fig.update_layout(
        height=400,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a3a3a3'),
        xaxis=dict(gridcolor='#1a1a1a'),
        yaxis=dict(gridcolor='#1a1a1a'),
        legend=dict(bgcolor='rgba(0,0,0,0)')
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "Intelligence Reports":
    st.title("Intelligence Reports")
    
    st.subheader("Top Security Threats")
    
    top_vulns = db.execute_query("""
        SELECT weakness_name, total_reports, bounty_rate, avg_severity
        FROM vw_vulnerability_metrics
        ORDER BY total_reports DESC
        LIMIT 5
    """)
    
    for idx, row in top_vulns.iterrows():
        with st.expander(f"{idx+1}. {row['weakness_name']} ({row['total_reports']} reports)"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Reports", f"{row['total_reports']:,}")
                st.metric("Bounty Rate", f"{row['bounty_rate']:.1f}%")
            with col2:
                st.metric("Avg Severity", f"{row['avg_severity']:.2f}")
            
            st.markdown(f"""
            **Risk Assessment:**
            - Frequency: {'High' if row['total_reports'] > 500 else 'Medium' if row['total_reports'] > 200 else 'Low'}
            - Bounty Success: {'High' if row['bounty_rate'] > 60 else 'Medium' if row['bounty_rate'] > 40 else 'Low'}
            - Severity Level: {'Critical' if row['avg_severity'] > 7 else 'High' if row['avg_severity'] > 5 else 'Medium'}
            
            **Recommendation:** {'Immediate action required' if row['avg_severity'] > 7 else 'Monitor and implement fixes' if row['avg_severity'] > 5 else 'Regular security review'}
            """)
    
    st.markdown("---")
    
    st.subheader("Organization Performance Insights")
    
    org_stats = db.execute_query("""
        SELECT 
            AVG(bounty_rate) as avg_bounty_rate,
            AVG(total_reports) as avg_reports
        FROM vw_organization_metrics
    """).iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Industry Benchmarks**
        
        - Average reports per organization: {org_stats['avg_reports']:.0f}
        - Average bounty rate: {org_stats['avg_bounty_rate']:.1f}%
        
        Organizations performing above these metrics demonstrate strong security programs.
        """)
    
    with col2:
        st.markdown("""
        **Best Practices**
        
        1. Maintain clear vulnerability disclosure policies
        2. Respond to reports within 24-48 hours
        3. Provide detailed feedback to researchers
        4. Offer competitive bounty amounts
        5. Engage actively with the security community
        """)

elif page == "AI Assistant":
    st.title("AI-Powered Assistant")
    
    if not config.AI_ENABLED:
        st.warning("AI features require OpenAI API key. Configure it in your .env file.")
    else:
        st.success("AI Assistant is ready")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask about vulnerability data..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        from src.ai.nlp_query import NLPQueryEngine
                        nlp_engine = NLPQueryEngine()
                        result = nlp_engine.process_query(prompt, user_role="admin")
                        
                        if result['success']:
                            st.markdown(f"**Query:** `{result['sql']}`")
                            st.dataframe(result['data'], use_container_width=True)
                            response = f"Found {len(result['data'])} results."
                        else:
                            response = f"Error: {result.get('error', 'Unknown error')}"
                        
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

elif page == "Knowledge Base":
    st.title("Security Knowledge Base")
    
    st.markdown("Comprehensive glossary of common vulnerability types and security concepts.")
    
    search = st.text_input("Search for a vulnerability type", placeholder="e.g., XSS, SQL Injection...")
    
    vuln_types = db.execute_query("""
        SELECT DISTINCT weakness_name, COUNT(*) as count 
        FROM raw_reports 
        WHERE weakness_name IS NOT NULL AND weakness_name != ''
        GROUP BY weakness_name 
        ORDER BY count DESC
    """)
    
    if search:
        filtered = vuln_types[vuln_types['weakness_name'].str.contains(search, case=False, na=False)]
    else:
        filtered = vuln_types
    
    glossary = {
        "Cross-site Scripting (XSS)": {
            "description": "Malicious scripts injected into trusted websites that execute in users' browsers.",
            "impact": "Steal session cookies, redirect users, deface websites, steal sensitive data",
            "prevention": "Input validation, output encoding, Content Security Policy (CSP)",
            "severity": "Medium to High"
        },
        "SQL Injection": {
            "description": "Attackers insert malicious SQL code into application queries.",
            "impact": "Database breach, data theft, data manipulation, authentication bypass",
            "prevention": "Parameterized queries, input validation, least privilege database access",
            "severity": "Critical"
        },
        "Improper Authorization": {
            "description": "Users can access resources or perform actions they shouldn't be allowed to.",
            "impact": "Unauthorized data access, privilege escalation, account takeover",
            "prevention": "Role-based access control, proper permission checks, session management",
            "severity": "High"
        },
        "Information Disclosure": {
            "description": "Sensitive information exposed to unauthorized users.",
            "impact": "Data leakage, privacy violations, credential exposure",
            "prevention": "Proper error handling, secure configuration, data classification",
            "severity": "Low to High"
        },
        "Cross-Site Request Forgery (CSRF)": {
            "description": "Attackers trick users into performing unwanted actions on authenticated sites.",
            "impact": "Unauthorized transactions, account modifications, data changes",
            "prevention": "CSRF tokens, SameSite cookies, user confirmation for sensitive actions",
            "severity": "Medium"
        },
        "Server-Side Request Forgery (SSRF)": {
            "description": "Attacker forces server to make requests to unintended locations.",
            "impact": "Access internal systems, port scanning, data exfiltration",
            "prevention": "Input validation, whitelist allowed destinations, network segmentation",
            "severity": "High"
        },
        "Remote Code Execution": {
            "description": "Attacker can execute arbitrary code on the target system.",
            "impact": "Complete system compromise, data theft, malware installation",
            "prevention": "Input validation, secure coding practices, sandboxing",
            "severity": "Critical"
        }
    }
    
    st.markdown(f"**Showing {len(filtered)} vulnerability types**")
    
    for vuln_name in filtered['weakness_name'].head(20):
        with st.expander(f"{vuln_name} ({filtered[filtered['weakness_name']==vuln_name]['count'].values[0]} reports)"):
            if vuln_name in glossary:
                info = glossary[vuln_name]
                st.markdown(f"**Description:** {info['description']}")
                st.markdown(f"**Impact:** {info['impact']}")
                st.markdown(f"**Prevention:** {info['prevention']}")
                st.markdown(f"**Severity:** {info['severity']}")
            else:
                st.markdown(f"Common vulnerability type found in {filtered[filtered['weakness_name']==vuln_name]['count'].values[0]} reports.")
                st.markdown("*Check OWASP or CWE for detailed information.*")
    
    st.markdown("---")
    st.subheader("External Resources")
    st.markdown("""
    - [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Most critical web application security risks
    - [CWE Database](https://cwe.mitre.org/) - Common Weakness Enumeration
    - [CVSS Calculator](https://www.first.org/cvss/) - Common Vulnerability Scoring System
    - [HackerOne Hacktivity](https://hackerone.com/hacktivity) - Public disclosed reports
    """)

elif page == "Search & Export":
    st.title("Search & Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_filter = st.selectbox("Time Period", ["All Time", "Last 30 Days", "Last 90 Days", "Last Year"])
    
    with col2:
        severity_options = db.execute_query("SELECT DISTINCT severity_rating FROM raw_reports WHERE severity_rating IS NOT NULL AND severity_rating != ''").values.flatten().tolist()
        severity = st.multiselect("Severity", ["All"] + severity_options, default=["All"])
    
    with col3:
        org_options = db.execute_query("SELECT DISTINCT team_name FROM raw_reports WHERE team_name IS NOT NULL AND team_name != '' LIMIT 50").values.flatten().tolist()
        org = st.multiselect("Organization", ["All"] + org_options, default=["All"])
    
    search = st.text_input("Search", placeholder="Search in titles...")
    
    query = "SELECT id, title, created_at, team_name, weakness_name, severity_rating, has_bounty FROM raw_reports WHERE 1=1"
    
    if date_filter == "Last 30 Days":
        query += " AND created_at >= CURRENT_DATE - INTERVAL '30 days'"
    elif date_filter == "Last 90 Days":
        query += " AND created_at >= CURRENT_DATE - INTERVAL '90 days'"
    elif date_filter == "Last Year":
        query += " AND created_at >= CURRENT_DATE - INTERVAL '1 year'"
    
    if "All" not in severity and severity:
        severity_list = "','".join(severity)
        query += f" AND severity_rating IN ('{severity_list}')"
    
    if "All" not in org and org:
        org_list = "','".join([o.replace("'", "''") for o in org])
        query += f" AND team_name IN ('{org_list}')"
    
    if search:
        query += f" AND title ILIKE '%{search}%'"
    
    query += " ORDER BY created_at DESC LIMIT 1000"
    
    df = db.execute_query(query)
    
    st.markdown(f"**Found {len(df):,} reports**")
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"hackerone_reports_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    st.dataframe(df, use_container_width=True, height=600)
