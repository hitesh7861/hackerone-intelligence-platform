import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path
import base64
import os

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
    
    /* Fix scrollbar positioning at different zoom levels */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    .main {
        overflow-x: hidden !important;
    }
    
    body {
        overflow-x: hidden !important;
    }
    
    [data-testid="stSidebar"]::-webkit-scrollbar,
    [data-testid="stSidebar"] *::-webkit-scrollbar {
        display: none !important;
    }
    
    /* Chat Messages - Ensure full visibility */
    [data-testid="stChatMessageContainer"] {
        max-height: none !important;
        overflow: visible !important;
    }
    
    [data-testid="stChatMessage"] {
        max-height: none !important;
        overflow: visible !important;
        margin-bottom: 1rem !important;
    }
    
    /* Code blocks in chat */
    [data-testid="stChatMessage"] pre {
        max-height: none !important;
        overflow-x: auto !important;
        overflow-y: visible !important;
    }
    
    /* DataFrames in chat */
    [data-testid="stChatMessage"] [data-testid="stDataFrame"] {
        max-height: 400px !important;
        overflow: auto !important;
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
    
    /* Alert boxes - Remove background */
    .stAlert {
        background-color: transparent !important;
        border: none !important;
        padding: 0.5rem 0 !important;
    }
    
    [data-testid="stAlert"] {
        background-color: transparent !important;
        border: none !important;
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
    
    /* Fix chat container and input responsiveness */
    .main .block-container {
        max-height: calc(100vh - 100px) !important;
        overflow-y: auto !important;
        padding-bottom: 100px !important;
    }
    
    [data-testid="stChatInput"] {
        position: sticky !important;
        bottom: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        background: transparent !important;
        padding: 10px 0 !important;
        z-index: 100 !important;
    }
    
    [data-testid="stChatInput"] > div {
        width: 100% !important;
    }
    
    /* Force remove blue background from chat input - nuclear option */
    section[data-testid="stChatInput"],
    [data-testid="stChatInput"],
    [data-testid="stChatInput"]::before,
    [data-testid="stChatInput"]::after {
        background-color: #0a0a0a !important;
        background: #0a0a0a !important;
        background-image: none !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    
    [data-testid="stChatInput"] *,
    [data-testid="stChatInput"] div,
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div,
    [data-testid="stChatInput"] > div > div > div,
    [data-testid="stChatInput"] form,
    [data-testid="stChatInput"] form *,
    [data-testid="stChatInput"] [class*="st-"],
    [data-testid="stChatInput"] [class*="css-"] {
        background-color: #0a0a0a !important;
        background: #0a0a0a !important;
        background-image: none !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }
    
    [data-testid="stChatInput"] input,
    [data-testid="stChatInput"] textarea {
        background-color: #1a1a1a !important;
        background: #1a1a1a !important;
        border: 1px solid #404040 !important;
        color: #ffffff !important;
    }
    
    /* Chat message container */
    [data-testid="stChatMessageContainer"] {
        max-height: none !important;
        overflow: visible !important;
    }
    
    /* Floating AI Chatbot Button */
    .floating-chat-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        cursor: pointer;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        animation: pulse 2s infinite;
    }
    
    .floating-chat-button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 30px rgba(102, 126, 234, 0.6);
    }
    
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        }
        50% {
            box-shadow: 0 4px 30px rgba(102, 126, 234, 0.7);
        }
    }
    
    .chat-icon {
        font-size: 28px;
        color: white;
    }
    
    .chat-tooltip {
        position: fixed;
        bottom: 100px;
        right: 30px;
        background: #1a1a1a;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 999;
        white-space: nowrap;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Chat Widget Container */
    .chat-widget {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 400px;
        height: 600px;
        background: #0a0a0a;
        border: 1px solid #333;
        border-radius: 12px;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
        z-index: 1000;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .chat-widget-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 16px 20px;
        color: white;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-widget-body {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
    }
    
    .close-chat {
        cursor: pointer;
        font-size: 20px;
        opacity: 0.8;
        transition: opacity 0.2s;
    }
    
    .close-chat:hover {
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# Check if database exists and has data, if not run pipeline (only once per session)
if 'db_checked' not in st.session_state:
    st.session_state.db_checked = False

if not st.session_state.db_checked:
    db_path = Path(__file__).parent.parent.parent / "data" / "hackerone.duckdb"
    needs_setup = False

    # Check if database exists and has data
    if not db_path.exists():
        needs_setup = True
    else:
        # Check if database has data and views by querying fact_reports and views
        try:
            import duckdb
            conn = duckdb.connect(str(db_path), read_only=True)
            try:
                # Check if fact_reports table exists and has data
                result = conn.execute("SELECT COUNT(*) FROM fact_reports").fetchone()
                if result[0] == 0:
                    needs_setup = True
                else:
                    # Check if views exist (pipeline completed)
                    try:
                        conn.execute("SELECT COUNT(*) FROM vw_organization_metrics").fetchone()
                    except:
                        # Views don't exist, pipeline didn't complete
                        needs_setup = True
            except:
                # Table doesn't exist
                needs_setup = True
            finally:
                conn.close()
        except:
            needs_setup = True
    
    st.session_state.db_checked = True
else:
    needs_setup = False

if needs_setup:
    st.info("🔄 First time setup: Downloading and processing HackerOne dataset... This takes 2-5 minutes.")
    with st.spinner("Loading data..."):
        try:
            # Delete existing database if it exists but is empty/corrupted
            if db_path.exists():
                db_path.unlink()
            
            from src.elt.pipeline import ELTPipeline
            pipeline = ELTPipeline()
            pipeline.run_full_pipeline()
            st.success("✅ Data loaded successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.info("Try refreshing the page or contact support if the issue persists.")
            st.stop()

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
    
    # Refresh Data Button
    if st.button("🔄 Refresh Data", key="refresh-data", use_container_width=True, help="Reload data from HackerOne dataset"):
        with st.spinner("Refreshing data... This may take a few minutes."):
            try:
                from src.elt.pipeline import ELTPipeline
                pipeline = ELTPipeline()
                pipeline.run_full_pipeline()
                st.success("✅ Data refreshed successfully!")
                st.cache_resource.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error refreshing data: {str(e)}")
    
    st.markdown("---")
    
    # Simple navigation - AI Assistant at bottom with icon
    page = st.radio(
        "Navigation",
        ["Executive Dashboard", "Threat Intelligence", "Program Benchmarks", "Community Analytics", 
         "Market Evolution", "Strategic Insights", "Security Reference", "Data Workbench", "AI Assistant"],
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

# Main content - Executive Dashboard page
if page == "Executive Dashboard":
    st.title("Executive Dashboard")
    st.markdown("<p style='color: #a3a3a3; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Comprehensive intelligence platform providing real-time visibility into global vulnerability landscape, bounty economics, and security program performance</p>", unsafe_allow_html=True)
    
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
    
    # First row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reports", f"{int(metrics['total_reports']):,}")
    with col2:
        st.metric("Bounty Reports", f"{int(metrics['bounty_reports']):,}")
    with col3:
        bounty_rate = (metrics['bounty_reports'] / metrics['total_reports'] * 100)
        st.metric("Bounty Rate", f"{bounty_rate:.1f}%")
    with col4:
        st.metric("Organizations", f"{int(metrics['organizations']):,}")
    
    # Second row of metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("Researchers", f"{int(metrics['researchers']):,}")
    with col6:
        st.metric("Vulnerability Types", f"{int(metrics['vulnerability_types']):,}")
    with col7:
        avg_votes = db.execute_query("SELECT AVG(vote_count) as avg FROM fact_reports").iloc[0]['avg']
        st.metric("Avg Community Votes", f"{avg_votes:.1f}")
    with col8:
        top_vuln = db.execute_query("SELECT weakness_name FROM vw_vulnerability_metrics ORDER BY total_reports DESC LIMIT 1").iloc[0]['weakness_name']
        st.metric("Top Threat", top_vuln[:15] + "..." if len(top_vuln) > 15 else top_vuln)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Threat Landscape")
        top_vulns = db.execute_query("""
            SELECT weakness_name, total_reports, bounty_rate
            FROM vw_vulnerability_metrics
            ORDER BY total_reports DESC
            LIMIT 10
        """)
        
        # Gradient color based on bounty rate
        fig = px.bar(top_vulns, x='total_reports', y='weakness_name',
                     orientation='h',
                     color='bounty_rate',
                     color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'],
                     labels={'total_reports': 'Reports', 'weakness_name': '', 'bounty_rate': 'Bounty %'})
        fig.update_layout(
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a3a3a3', size=11),
            xaxis=dict(gridcolor='#1a1a1a', showgrid=True),
            yaxis=dict(categoryorder='total ascending', gridcolor='#1a1a1a'),
            margin=dict(l=0, r=20, t=0, b=0),
            coloraxis_colorbar=dict(title="Bounty %", thickness=10, len=0.7)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Insight box
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%); padding: 1rem; border-radius: 8px; border-left: 3px solid #8b5cf6; margin-top: 0.5rem;'>
            <p style='color: #a3a3a3; font-size: 0.85rem; margin: 0;'>
                <strong style='color: #8b5cf6;'>Key Insight:</strong> Color intensity shows bounty success rate. 
                Greener = higher payouts, indicating valuable vulnerabilities.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Program Performance Matrix")
        top_orgs = db.execute_query("""
            SELECT team_name, total_reports, bounty_rate, avg_votes
            FROM vw_organization_metrics
            ORDER BY total_reports DESC
            LIMIT 15
        """)
        
        # Scatter plot: Volume vs Quality
        fig = px.scatter(top_orgs, 
                        x='total_reports', 
                        y='bounty_rate',
                        size='avg_votes',
                        hover_data=['team_name'],
                        color='bounty_rate',
                        color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'],
                        labels={'total_reports': 'Report Volume', 'bounty_rate': 'Bounty Rate (%)', 'avg_votes': 'Community Engagement'})
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a3a3a3', size=11),
            xaxis=dict(gridcolor='#1a1a1a', showgrid=True, title='Report Volume'),
            yaxis=dict(gridcolor='#1a1a1a', showgrid=True, title='Bounty Rate (%)'),
            margin=dict(l=0, r=20, t=0, b=0),
            coloraxis_colorbar=dict(title="Bounty %", thickness=10, len=0.7)
        )
        fig.update_traces(marker=dict(line=dict(width=1, color='#ffffff')))
        st.plotly_chart(fig, use_container_width=True)
        
        # Insight box
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%); padding: 1rem; border-radius: 8px; border-left: 3px solid #10b981; margin-top: 0.5rem;'>
            <p style='color: #a3a3a3; font-size: 0.85rem; margin: 0;'>
                <strong style='color: #10b981;'>Performance Map:</strong> Top-right quadrant = high volume + high payouts (elite programs). 
                Bubble size = community engagement level.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
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

elif page == "Threat Intelligence":
    st.title("Threat Intelligence")
    st.markdown("<p style='color: #a3a3a3; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Deep-dive analysis of security weaknesses, attack patterns, and economic incentives driving the vulnerability disclosure ecosystem</p>", unsafe_allow_html=True)
    
    # Interactive filters
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        min_reports = st.slider("Minimum Reports", 0, 500, 50, 25, help="Filter vulnerabilities by minimum report count")
    with col_f2:
        top_n = st.selectbox("Show Top N", [10, 20, 50, 100, "All"], index=0, help="Limit number of results")
    with col_f3:
        sort_by = st.selectbox("Sort By", ["Reports", "Bounty Rate"], help="Sort vulnerabilities by metric")
    
    # Fetch data with filters
    vuln_df = db.execute_query("""
        SELECT * FROM vw_vulnerability_metrics
        ORDER BY total_reports DESC
    """)
    
    # Apply filters
    vuln_df = vuln_df[vuln_df['total_reports'] >= min_reports]
    if sort_by == "Bounty Rate":
        vuln_df = vuln_df.sort_values('bounty_rate', ascending=False)
    if top_n != "All":
        vuln_df = vuln_df.head(int(top_n))
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Types", len(vuln_df))
    with col2:
        st.metric("Avg Bounty Rate", f"{vuln_df['bounty_rate'].mean():.1f}%")
    with col3:
        st.metric("Total Reports", f"{vuln_df['total_reports'].sum():,}")
    with col4:
        st.metric("Avg Votes", f"{vuln_df['avg_votes'].mean():.1f}")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Volume vs Bounty Success")
        # Scatter plot
        fig = px.scatter(vuln_df.head(30), 
                        x='total_reports', 
                        y='bounty_rate',
                        size='avg_votes',
                        hover_data=['weakness_name'],
                        color='bounty_rate',
                        color_continuous_scale='Turbo',
                        labels={'total_reports': 'Total Reports', 'bounty_rate': 'Bounty Rate (%)', 'avg_votes': 'Avg Votes'})
        fig.update_layout(
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a3a3a3', size=10),
            xaxis=dict(gridcolor='#1a1a1a', showgrid=True),
            yaxis=dict(gridcolor='#1a1a1a', showgrid=True),
            margin=dict(l=0, r=20, t=0, b=0),
            coloraxis_colorbar=dict(title="Bounty %", thickness=8, len=0.6)
        )
        fig.update_traces(marker=dict(line=dict(width=0.5, color='#ffffff')))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top Threats by Bounty Rate")
        top_bounty = vuln_df.nlargest(10, 'bounty_rate')
        fig = px.bar(top_bounty, 
                     x='bounty_rate', 
                     y='weakness_name',
                     orientation='h',
                     color='total_reports',
                     color_continuous_scale='Plasma',
                     labels={'bounty_rate': 'Bounty Rate (%)', 'weakness_name': '', 'total_reports': 'Reports'})
        fig.update_layout(
            height=350,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#a3a3a3', size=10),
            xaxis=dict(gridcolor='#1a1a1a', showgrid=True),
            yaxis=dict(categoryorder='total ascending', gridcolor='#1a1a1a'),
            margin=dict(l=0, r=20, t=0, b=0),
            coloraxis_colorbar=dict(title="Reports", thickness=8, len=0.6)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Insight box
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 1.2rem; border-radius: 10px; border-left: 4px solid #6366f1; margin-bottom: 1rem;'>
        <p style='color: #e0e7ff; font-size: 0.9rem; margin: 0; line-height: 1.6;'>
            <strong style='color: #a5b4fc;'>Strategic Insight:</strong> High bounty rates indicate valuable vulnerabilities that organizations prioritize. 
            Focus security efforts on top-right quadrant vulnerabilities (high volume + high bounty rate) for maximum impact.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data table
    st.subheader("Detailed Breakdown")
    st.dataframe(
        vuln_df[['weakness_name', 'total_reports', 'bounty_reports', 'avg_votes', 'bounty_rate']],
        use_container_width=True,
        height=400
    )

elif page == "Program Benchmarks":
    st.title("Program Benchmarks")
    st.markdown("<p style='color: #a3a3a3; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Comparative analysis of security program maturity, researcher engagement, and bounty investment across industry leaders</p>", unsafe_allow_html=True)
    
    # Interactive filters
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        min_reports_org = st.slider("Minimum Reports", 0, 200, 20, 10, help="Filter organizations by minimum report count")
    with col_f2:
        min_bounty_rate = st.slider("Minimum Bounty Rate (%)", 0, 100, 0, 5, help="Filter by minimum bounty success rate")
    
    org_df = db.execute_query("""
        SELECT * FROM vw_organization_metrics
        ORDER BY total_reports DESC
    """)
    
    # Apply filters
    org_df = org_df[(org_df['total_reports'] >= min_reports_org) & (org_df['bounty_rate'] >= min_bounty_rate)]
    
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
    
    # Performance Matrix Scatter Plot
    st.subheader("Program Performance Quadrant Analysis")
    
    fig = px.scatter(org_df.head(50), 
                    x='total_reports', 
                    y='bounty_rate',
                    size='avg_votes',
                    hover_data=['team_name'],
                    color='bounty_rate',
                    color_continuous_scale=['#dc2626', '#f59e0b', '#10b981', '#06b6d4'],
                    labels={'total_reports': 'Report Volume', 'bounty_rate': 'Bounty Rate (%)', 'avg_votes': 'Community Votes'})
    fig.update_layout(
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a3a3a3', size=11),
        xaxis=dict(gridcolor='#1a1a1a', showgrid=True, title='Report Volume'),
        yaxis=dict(gridcolor='#1a1a1a', showgrid=True, title='Bounty Success Rate (%)'),
        margin=dict(l=0, r=20, t=0, b=0),
        coloraxis_colorbar=dict(title="Bounty %", thickness=10, len=0.7)
    )
    fig.update_traces(marker=dict(line=dict(width=1, color='#ffffff')))
    st.plotly_chart(fig, use_container_width=True)
    
    # Insight box
    st.markdown("""
    <div style='background: linear-gradient(135deg, #064e3b 0%, #065f46 100%); padding: 1.2rem; border-radius: 10px; border-left: 4px solid #10b981; margin-bottom: 1rem;'>
        <p style='color: #d1fae5; font-size: 0.9rem; margin: 0; line-height: 1.6;'>
            <strong style='color: #6ee7b7;'>Elite Programs:</strong> Top-right quadrant organizations demonstrate both high volume and high bounty rates - 
            these are mature security programs that attract quality researchers and reward valuable findings generously.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Detailed Organization Data")
    st.dataframe(
        org_df[['team_name', 'total_reports', 'bounty_reports', 'avg_votes', 'bounty_rate']],
        use_container_width=True,
        height=400
    )

elif page == "Community Analytics":
    st.title("Community Analytics")
    st.markdown("<p style='color: #a3a3a3; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Security researcher ecosystem analysis: contribution patterns, quality metrics, and community engagement dynamics</p>", unsafe_allow_html=True)
    
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
        researcher_df[['reporter_username', 'total_reports', 'bounty_reports', 'avg_votes', 'bounty_rate']].head(100),
        use_container_width=True,
        height=600
    )

elif page == "Market Evolution":
    st.title("Market Evolution")
    st.markdown("<p style='color: #a3a3a3; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Temporal analysis of vulnerability disclosure market dynamics, program growth trajectories, and emerging security trends</p>", unsafe_allow_html=True)
    
    trend_df = db.execute_query("""
        SELECT * FROM vw_time_trends
        ORDER BY month
    """)
    
    st.subheader("Report Volume Over Time")
    
    # Add padding columns to prevent toolbar overflow
    col_left, col_chart, col_right = st.columns([0.05, 0.9, 0.05])
    
    with col_chart:
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
            legend=dict(bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'displaylogo': False})

elif page == "Strategic Insights":
    st.title("Strategic Insights")
    st.markdown("<p style='color: #a3a3a3; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Executive intelligence briefings with data-driven recommendations for optimizing security investments and program effectiveness</p>", unsafe_allow_html=True)
    
    st.subheader("Top Security Threats")
    
    top_vulns = db.execute_query("""
        SELECT weakness_name, total_reports, bounty_rate, avg_votes
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
                st.metric("Avg Community Votes", f"{row['avg_votes']:.1f}")
            
            st.markdown(f"""
            **Risk Assessment:**
            - Frequency: {'High' if row['total_reports'] > 500 else 'Medium' if row['total_reports'] > 200 else 'Low'}
            - Bounty Success: {'High' if row['bounty_rate'] > 60 else 'Medium' if row['bounty_rate'] > 40 else 'Low'}
            - Community Interest: {'High' if row['avg_votes'] > 5 else 'Medium' if row['avg_votes'] > 2 else 'Low'}
            
            **Recommendation:** {'High priority - frequent and well-rewarded' if row['bounty_rate'] > 60 else 'Monitor and implement fixes' if row['bounty_rate'] > 40 else 'Regular security review'}
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
    
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    
    # Clear chat button with icon
    delete_icon_path = Path(__file__).parent / "assets" / "delete.png"
    if delete_icon_path.exists():
        import base64
        with open(str(delete_icon_path), 'rb') as f:
            delete_icon_data = base64.b64encode(f.read()).decode()
        
        col1, col2, col3 = st.columns([0.85, 0.15, 0])
        with col2:
            if st.button("Clear Chat", key="clear-chat", help="Clear conversation and start fresh"):
                st.session_state.messages = []
                st.rerun()
    else:
        col1, col2, col3 = st.columns([0.85, 0.15, 0])
        with col2:
            if st.button("Clear Chat", key="clear-chat", help="Clear conversation and start fresh"):
                st.session_state.messages = []
                st.rerun()
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
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
                        current_user = {"role": "admin", "organization": None}
                        # Pass conversation history for context
                        result = nlp_engine.process_query(prompt, current_user, st.session_state.messages[:-1])
                        
                        full_response = ""
                        
                        if result.get('sql_generated'):
                            st.markdown(f"**SQL Query:**")
                            st.code(result['sql_generated'], language='sql')
                            full_response += f"**SQL Query:**\n```sql\n{result['sql_generated']}\n```\n\n"
                            
                            if result.get('results') and len(result['results']) > 0:
                                st.markdown(f"**Results:** {len(result['results'])} rows found")
                                import pandas as pd
                                df_results = pd.DataFrame(result['results'])
                                
                                # Dynamic height based on number of rows
                                num_rows = len(df_results)
                                if num_rows == 1:
                                    table_height = 100
                                elif num_rows <= 5:
                                    table_height = 200
                                elif num_rows <= 10:
                                    table_height = 300
                                else:
                                    table_height = 400
                                
                                st.dataframe(df_results, use_container_width=True, height=table_height)
                                
                                summary = result.get('explanation', 'Query executed successfully.')
                                st.markdown(f"**Summary:** {summary}")
                                
                                full_response += f"**Results:** {len(result['results'])} rows found\n\n"
                                full_response += f"**Summary:** {summary}"
                            else:
                                st.info("No results found for your query.")
                                explanation = result.get('explanation', 'The query executed successfully but returned no data.')
                                st.markdown(f"**Explanation:** {explanation}")
                                
                                full_response += f"No results found.\n\n**Explanation:** {explanation}"
                        else:
                            # Conversational response (no SQL generated)
                            response_text = result.get('explanation', 'I can help you with that!')
                            st.markdown(response_text)
                            full_response = response_text
                        
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

elif page == "Security Reference":
    st.title("Security Reference")
    st.markdown("<p style='color: #a3a3a3; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Comprehensive knowledge repository covering vulnerability taxonomies, security metrics, and industry-standard terminology</p>", unsafe_allow_html=True)
    
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

elif page == "Data Workbench":
    st.title("Data Workbench")
    st.markdown("<p style='color: #a3a3a3; font-size: 1rem; margin-top: -1rem; margin-bottom: 2rem;'>Interactive data exploration workspace with advanced filtering, custom queries, and export capabilities for ad-hoc analysis</p>", unsafe_allow_html=True)
    
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

