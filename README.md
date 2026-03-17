# 🔒 HackerOne Intelligence Platform

> Scalable enterprise vulnerability intelligence platform with AI-driven analytics, customer data access, and agentic capabilities.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red.svg)](https://streamlit.io/)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.9-yellow.svg)](https://duckdb.org/)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [AI Capabilities](#ai-capabilities)
- [Project Structure](#project-structure)
- [Demo Credentials](#demo-credentials)

## 🎯 Overview

This platform addresses **HackerOne's Senior Data Engineer Assignment** by building a scalable, intelligence-enabled enterprise system that:

1. **Challenge 1:** Enables business reporting and customer data access for vulnerability intelligence
2. **Challenge 2:** Presents compelling data stories through interactive dashboards and AI insights

### Key Highlights

- ✅ **Modern ELT Architecture** - Extract-Load-Transform using DuckDB
- ✅ **REST API** - FastAPI with JWT authentication and role-based access
- ✅ **AI/Agentic Features** - NLP queries, report summarization, pattern detection
- ✅ **Interactive Dashboard** - Streamlit with business metrics and customer portal
- ✅ **Scalable Design** - Production-ready architecture with clear migration path

## 🚀 Features

### Core Capabilities

- **📊 Business Intelligence**
  - Vulnerability trend analysis
  - Organization performance metrics
  - Reporter analytics
  - Time-series analysis
  - Severity-based insights

- **🔐 Customer Portal**
  - Organization-specific data access
  - Secure authentication
  - Role-based permissions
  - Custom reporting

- **🤖 AI-Powered Insights**
  - Natural language query interface
  - Automated report summarization
  - Vulnerability pattern detection
  - Predictive analytics
  - Security recommendations

- **🔌 REST API**
  - OpenAPI/Swagger documentation
  - JWT authentication
  - Rate limiting ready
  - Customer data isolation

## 🏗️ Architecture

### High-Level Design

```
Data Source (HuggingFace) 
    ↓
ELT Pipeline (Extract → Load → Transform)
    ↓
DuckDB (Star Schema: Facts + Dimensions)
    ↓
    ├─→ FastAPI (Business & Customer Endpoints)
    └─→ AI Layer (OpenAI GPT-4o-mini)
         ↓
    Streamlit Dashboard
```

### Technology Stack

- **Backend:** Python 3.11+, FastAPI, DuckDB
- **Frontend:** Streamlit, Plotly
- **AI/ML:** OpenAI GPT-4o-mini, LangChain
- **Auth:** JWT (python-jose)
- **Data:** Pandas, HuggingFace Datasets

**See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design decisions and tradeoffs.**

## ⚡ Quick Start

### Prerequisites

- Python 3.11 or higher
- pip or conda
- (Optional) OpenAI API key for AI features

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/hackerone-intelligence-platform.git
cd hackerone-intelligence-platform
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment (optional for AI features)**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

5. **Run the ELT pipeline**
```bash
python run_pipeline.py
```

This will:
- Download HackerOne dataset from HuggingFace (~10K reports)
- Load raw data into DuckDB
- Transform data into star schema
- Create business metric views

**Expected time:** 2-5 minutes depending on internet speed

### Start the Services

**Option 1: Dashboard (Recommended for demo)**
```bash
python run_dashboard.py
# Opens at http://localhost:8501
```

**Option 2: API Server**
```bash
python run_api.py
# API at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## 📖 Usage

### Dashboard Navigation

1. **📊 Overview** - Platform statistics and key metrics
2. **🐛 Vulnerabilities** - Vulnerability type analysis
3. **🏢 Organizations** - Organization performance metrics
4. **👥 Reporters** - Security researcher analytics
5. **📈 Trends** - Time-series and trend analysis
6. **🤖 AI Insights** - Natural language queries and AI-powered insights

### API Usage

**1. Authenticate**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**2. Get vulnerability metrics**
```bash
curl -X GET "http://localhost:8000/api/v1/vulnerabilities" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**3. Natural language query (AI feature)**
```bash
curl -X POST "http://localhost:8000/api/v1/query/nlp" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me top 10 XSS vulnerabilities"}'
```

## 🔑 Demo Credentials

| Username | Password | Role | Access |
|----------|----------|------|--------|
| `admin` | `admin123` | Admin | Full platform access |
| `mailru` | `mailru123` | Customer | Mail.ru organization data |
| `shopify` | `shopify123` | Customer | Shopify organization data |
| `gitlab` | `gitlab123` | Customer | GitLab organization data |

## 🤖 AI Capabilities

### 1. Natural Language Query

Ask questions in plain English:
- "What's the average bounty for SQL injection?"
- "Show me all critical vulnerabilities from 2023"
- "Which organization pays the highest bounties?"

### 2. Report Summarization

Automatically generate executive summaries of vulnerability reports with:
- One-sentence summary
- Key risk identification
- Business impact analysis
- Recommended actions

### 3. Pattern Detection

Identify emerging trends:
- Vulnerability frequency patterns
- High-value vulnerability prediction
- Security recommendations
- Anomaly detection

**Note:** AI features require `OPENAI_API_KEY` in `.env` file. Platform works without AI but with reduced insights.

## 📁 Project Structure

```
hackerone-intelligence-platform/
├── src/
│   ├── elt/              # ELT pipeline (Extract-Load-Transform)
│   │   ├── extract.py    # Data extraction from HuggingFace
│   │   ├── load.py       # Load raw data into DuckDB
│   │   ├── transform.py  # SQL transformations
│   │   └── pipeline.py   # Orchestration
│   ├── database/         # Database layer
│   │   ├── schema.py     # Schema definitions
│   │   └── connection.py # Connection management
│   ├── api/              # FastAPI REST API
│   │   ├── main.py       # API entry point
│   │   ├── routes.py     # Endpoint definitions
│   │   ├── auth.py       # Authentication
│   │   └── models.py     # Pydantic models
│   ├── ai/               # AI/Agentic capabilities
│   │   ├── nlp_query.py  # Natural language queries
│   │   ├── report_summarizer.py
│   │   └── pattern_detector.py
│   └── dashboard/        # Streamlit dashboard
│       └── app.py
├── data/
│   ├── raw/              # Raw CSV data
│   ├── processed/        # Processed data
│   └── hackerone.duckdb  # DuckDB database
├── docs/
│   ├── ARCHITECTURE.md   # Architecture documentation
│   └── presentation/     # Executive presentation
├── tests/                # Test suite
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── run_pipeline.py       # Run ELT pipeline
├── run_api.py           # Start API server
└── run_dashboard.py     # Start dashboard
```

## 📊 API Documentation

Interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/auth/login` - Authenticate user
- `GET /api/v1/vulnerabilities` - Get vulnerability metrics
- `GET /api/v1/organizations` - Get organization metrics (admin only)
- `GET /api/v1/organizations/me` - Get current organization data (customer)
- `GET /api/v1/reporters` - Get reporter analytics (admin only)
- `GET /api/v1/trends/time` - Get time-series trends
- `POST /api/v1/query/nlp` - Natural language query (AI)

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## 🚀 Deployment

### Local Development
```bash
python run_pipeline.py  # One-time setup
python run_dashboard.py # Start dashboard
```

### Production Deployment

**Docker (Recommended)**
```bash
docker build -t hackerone-platform .
docker run -p 8000:8000 -p 8501:8501 hackerone-platform
```

**Cloud Deployment**
- AWS: ECS/Fargate + RDS
- GCP: Cloud Run + Cloud SQL
- Azure: App Service + Azure SQL

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for scaling considerations.

## 📈 Performance

- **Dataset Size:** ~10,000 reports
- **API Response Time:** <100ms (avg)
- **Dashboard Load Time:** <2s
- **Database Size:** ~50MB
- **AI Query Time:** 1-3s (OpenAI API)

## 🔐 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Organization-level data isolation
- SQL injection prevention
- Secrets management via environment variables

## 📝 License

This project is created for the HackerOne Senior Data Engineer assignment.

## 👤 Author

**Hitesh Kumar**
- Assignment: HackerOne Senior Data Engineer
- Date: March 2026

## 🙏 Acknowledgments

- HackerOne for the disclosed reports dataset
- OpenAI for GPT-4o-mini API
- FastAPI, Streamlit, and DuckDB communities

---

**Built with ❤️ for HackerOne**
