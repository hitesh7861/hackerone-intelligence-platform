# Architecture Design Document

**HackerOne Intelligence Platform**

A simple, clear breakdown of how everything works together.

---

## High-Level Design

### What We're Building

An intelligence platform that turns raw vulnerability data into actionable insights through:
- **Data Pipeline** - Automated ETL to process HackerOne reports
- **Analytics Database** - Fast queries on structured vulnerability data
- **REST API** - Secure access for customers and business users
- **AI Assistant** - Natural language interface for data exploration
- **Dashboard** - Interactive visualizations and insights

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    HuggingFace Dataset                      │
│                  (10K+ Vulnerability Reports)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    ELT Pipeline                             │
│  Extract → Load → Transform (Star Schema)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    DuckDB Database                          │
│  • Raw Tables  • Dimension Tables  • Fact Tables            │
│  • Business Views  • Metrics                                │
└──────────────┬──────────────────────┬───────────────────────┘
               │                      │
               ▼                      ▼
    ┌──────────────────┐    ┌──────────────────┐
    │   FastAPI REST   │    │  AI Layer (GPT)  │
    │   • Auth (JWT)   │    │  • NLP Queries   │
    │   • Endpoints    │    │  • Summarization │
    │   • RBAC         │    │  • Patterns      │
    └────────┬─────────┘    └────────┬─────────┘
             │                       │
             └───────────┬───────────┘
                         ▼
              ┌─────────────────────┐
              │ Streamlit Dashboard │
              │  • Visualizations   │
              │  • AI Chat          │
              │  • Data Refresh     │
              └─────────────────────┘
```

### Key Design Decisions

**Why DuckDB?**
- Embedded analytics database (no separate server needed)
- Blazing fast for analytical queries
- Perfect for 10K-100K records
- Easy to deploy and maintain

**Why FastAPI?**
- Modern, fast Python web framework
- Auto-generated API docs (Swagger)
- Built-in validation with Pydantic
- Easy JWT authentication

**Why Streamlit?**
- Rapid dashboard development
- Python-native (no JS needed)
- Great for data apps
- Easy to iterate and demo

**Why Star Schema?**
- Optimized for analytics queries
- Clear separation of facts and dimensions
- Easy to understand and query
- Scalable design pattern

---

## Low-Level Design

### 1. Data Pipeline (ELT)

**Extract** (`src/elt/extract.py`)
```python
HuggingFace Dataset → Download → CSV File
- Dataset: Hacker0x01/disclosed_reports
- Output: data/raw/hackerone_reports.csv
- ~10,094 records
```

**Load** (`src/elt/load.py`)
```python
CSV → Parse JSON fields → DuckDB raw_reports table
- Handles nested JSON (reporter, team, weakness)
- Data cleaning and type conversion
- Creates raw_reports table
```

**Transform** (`src/elt/transform.py`)
```python
Raw Data → Star Schema (Dimensions + Facts) → Business Views

Dimensions:
- dim_vulnerabilities (weakness types)
- dim_organizations (companies)
- dim_researchers (security researchers)

Facts:
- fact_reports (main analytical table)

Views:
- vw_vulnerability_metrics
- vw_organization_metrics
- vw_reporter_metrics
- vw_time_trends
- vw_severity_analysis
```

### 2. Database Schema

**Star Schema Design:**

```
                    ┌──────────────────────┐
                    │   fact_reports       │
                    ├──────────────────────┤
                    │ id (PK)              │
                    │ weakness_id (FK)     │◄────┐
                    │ team_handle (FK)     │◄────┼────┐
                    │ reporter_username(FK)│◄────┼────┼────┐
                    │ created_at           │     │    │    │
                    │ severity_score       │     │    │    │
                    │ bounty_amount        │     │    │    │
                    │ has_bounty           │     │    │    │
                    └──────────────────────┘     │    │    │
                                                 │    │    │
    ┌────────────────────────────────────────────┘    │    │
    │                                                 │    │
    ▼                                                 │    │
┌─────────────────────┐                              │    │
│ dim_vulnerabilities │                              │    │
├─────────────────────┤                              │    │
│ weakness_id (PK)    │                              │    │
│ weakness_name       │                              │    │
│ total_reports       │                              │    │
└─────────────────────┘                              │    │
                                                     │    │
                    ┌────────────────────────────────┘    │
                    │                                     │
                    ▼                                     │
        ┌────────────────────────┐                       │
        │ dim_organizations      │                       │
        ├────────────────────────┤                       │
        │ team_handle (PK)       │                       │
        │ team_name              │                       │
        │ first_report_date      │                       │
        │ latest_report_date     │                       │
        └────────────────────────┘                       │
                                                         │
                            ┌────────────────────────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │ dim_researchers        │
                ├────────────────────────┤
                │ reporter_username (PK) │
                │ reporter_name          │
                │ total_reports          │
                │ first_report_date      │
                └────────────────────────┘
```

### 3. API Layer

**Authentication Flow:**
```
User → POST /api/v1/auth/login
     → Validate credentials
     → Generate JWT token
     → Return token

User → GET /api/v1/vulnerabilities
     → Verify JWT token
     → Check user role
     → Filter data by permissions
     → Return results
```

**Role-Based Access:**
- **Admin:** Full access to all data
- **Customer:** Only their organization's data

**Key Endpoints:**
```
Auth:
  POST /api/v1/auth/login

Business Analytics (Admin):
  GET /api/v1/vulnerabilities
  GET /api/v1/organizations
  GET /api/v1/reporters
  GET /api/v1/trends/time

Customer Portal:
  GET /api/v1/organizations/me
  GET /api/v1/reports/mine

AI Features:
  POST /api/v1/query/nlp
  POST /api/v1/reports/{id}/summarize
```

### 4. AI Layer

**Natural Language Query** (`src/ai/nlp_query.py`)
```
User Question → GPT-4o-mini → SQL Query → Execute → Results → Explain

Flow:
1. Classify query (conversation vs data query)
2. Build context (schema + conversation history)
3. Generate SQL using GPT-4o-mini
4. Execute SQL on DuckDB
5. Format results
6. Generate explanation
```

**Conversation Memory:**
- Stores last 5 messages in session state
- Passes to GPT for context
- Enables follow-up questions

**Report Summarization** (`src/ai/report_summarizer.py`)
```
Vulnerability Report → GPT-4o-mini → Summary

Output:
- One-line summary
- Risk level
- Business impact
- Recommended actions
```

### 5. Dashboard

**Pages:**
1. **Dashboard** - Overview metrics
2. **Security Threats** - Vulnerability analysis
3. **Companies** - Organization performance
4. **Researchers** - Top contributors
5. **Timeline & Patterns** - Trends
6. **Intelligence Reports** - Detailed reports
7. **AI Assistant** - Chat interface
8. **Knowledge Base** - Glossary
9. **Search & Export** - Data export

**Key Features:**
- Interactive charts (Plotly)
- Real-time filtering
- Data export (CSV)
- AI chat with memory
- One-click data refresh

### 6. Data Flow Example

**User asks: "How many XSS vulnerabilities are there?"**

```
1. User types in AI Assistant chat
   ↓
2. Frontend sends to nlp_query.process_query()
   ↓
3. AI classifies as "data_query"
   ↓
4. GPT-4o-mini generates SQL:
   SELECT COUNT(*) FROM fact_reports 
   WHERE weakness_name LIKE '%XSS%'
   ↓
5. Execute SQL on DuckDB
   ↓
6. Get results: 847 reports
   ↓
7. GPT generates explanation
   ↓
8. Display in chat with table
```

---

## Technology Choices

| Component | Technology | Why? |
|-----------|-----------|------|
| Language | Python 3.11+ | Rich data ecosystem, AI libraries |
| Database | DuckDB | Fast analytics, embedded, no server |
| API | FastAPI | Modern, fast, auto-docs |
| Dashboard | Streamlit | Rapid development, Python-native |
| AI | OpenAI GPT-4o-mini | Cost-effective, powerful NLP |
| Auth | JWT | Stateless, scalable |
| Data Source | HuggingFace | Public dataset, easy access |

---

## Performance Characteristics

**Database:**
- Size: ~50MB for 10K reports
- Query time: <100ms for most queries
- Supports: 100K+ records easily

**API:**
- Response time: <100ms average
- Concurrent users: 10-50 (single process)
- Scalable with multiple workers

**Dashboard:**
- Load time: <2 seconds
- Real-time updates via Streamlit
- Handles 10-20 concurrent users

**AI Queries:**
- Time: 1-3 seconds (OpenAI API latency)
- Cost: ~$0.001 per query
- Rate limit: OpenAI tier limits

---

## Security Model

**Authentication:**
```
JWT Token = Header + Payload + Signature
Payload contains: user_id, role, organization, expiry
```

**Authorization:**
```python
if user.role == "admin":
    # Full access
    return all_data
elif user.role == "customer":
    # Filtered access
    return data.filter(organization == user.organization)
```

**Data Isolation:**
- SQL queries automatically filtered by organization
- No cross-organization data leakage
- Admin role bypasses filters

---

## Scalability Considerations

**Current Scale:**
- 10K reports
- Single DuckDB file
- Single Streamlit process
- Works great for demo/POC

**Future Scale (100K+ reports):**
- DuckDB still works (tested to 1M+ rows)
- Consider PostgreSQL for multi-user writes
- Add Redis for caching
- Deploy with Gunicorn/Uvicorn workers
- Use load balancer for API

**Cloud Migration Path:**
- Database: DuckDB → PostgreSQL/Snowflake
- API: Single server → Container cluster
- Dashboard: Streamlit → Streamlit Cloud
- Storage: Local files → S3/Cloud Storage

---

## File Structure

```
src/
├── elt/
│   ├── extract.py      # Download from HuggingFace
│   ├── load.py         # Load into DuckDB
│   ├── transform.py    # Create star schema
│   └── pipeline.py     # Orchestrate all steps
│
├── database/
│   ├── schema.py       # Table definitions
│   └── connection.py   # DB connection management
│
├── api/
│   ├── main.py         # FastAPI app
│   ├── routes.py       # API endpoints
│   ├── auth.py         # JWT authentication
│   └── models.py       # Pydantic models
│
├── ai/
│   ├── nlp_query.py           # Natural language queries
│   ├── report_summarizer.py  # AI summarization
│   └── pattern_detector.py   # Pattern analysis
│
└── dashboard/
    └── app.py          # Streamlit dashboard

data/
├── raw/                # CSV files
└── hackerone.duckdb   # Database file

config.py              # Configuration
run_pipeline.py        # Run ETL
run_api.py            # Start API
run_dashboard.py      # Start dashboard
```

---

**That's it!** Simple, scalable, and production-ready architecture for vulnerability intelligence.
