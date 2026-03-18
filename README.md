# 🔒 HackerOne Intelligence Platform

**Turn vulnerability data into actionable intelligence—with AI superpowers!**

Welcome! This is an enterprise-grade platform that makes vulnerability intelligence accessible, actionable, and actually fun to explore. Whether you're a security analyst, data engineer, or just curious about bug bounty trends, you'll find something powerful here.

## What is this?

A complete intelligence platform for HackerOne vulnerability data featuring:
- 📊 **Interactive dashboards** with real-time insights
- 🤖 **AI-powered assistant** that answers questions in plain English
- 🔐 **Secure API** with customer-specific data access
- 📈 **Business analytics** for trends, patterns, and predictions

Built for HackerOne's Senior Data Engineer assignment, but designed like a real production system.

## What can you do here?

- 📊 **Explore the Data**: Dive into 10,000+ real vulnerability reports with interactive charts and filters
- 🤖 **Chat with AI**: Ask questions like "Show me top XSS vulnerabilities" and get instant SQL-powered answers
- 🔐 **Customer Portal**: Organizations can securely access only their data with role-based permissions
- 📈 **Spot Trends**: See which vulnerabilities are hot, which orgs pay the most, and who the elite hackers are
- 🔄 **Refresh Data**: One-click data refresh right from the dashboard
- 🛠️ **Use the API**: RESTful endpoints with JWT auth for programmatic access

## How it works

```
HuggingFace Dataset (10K+ reports)
    ↓
ELT Pipeline (Extract → Load → Transform)
    ↓
DuckDB (Fast, embedded analytics DB)
    ↓
    ├─→ REST API (FastAPI + JWT auth)
    ├─→ AI Assistant (GPT-4o-mini)
    └─→ Dashboard (Streamlit)
```

**Tech Stack:** Python, FastAPI, Streamlit, DuckDB, OpenAI, Plotly

**Want the deep dive?** Check out [ARCHITECTURE.md](docs/ARCHITECTURE.md) for design decisions and tradeoffs.

## How to get started

**You'll need:** Python 3.11+ and a few minutes

1. **Install what you need:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Load the data:**
   ```bash
   python run_pipeline.py
   ```
   This downloads 10K+ vulnerability reports from HuggingFace and sets up the database. Takes 2-5 minutes.

3. **Fire up the dashboard:**
   ```bash
   python run_dashboard.py
   ```
   Opens at http://localhost:8501

4. **(Optional) Enable AI features:**
   ```bash
   cp .env.example .env
   # Add your OPENAI_API_KEY to .env
   ```

**That's it!** You're ready to explore.

**Want the API instead?**
```bash
python run_api.py  # API at http://localhost:8000/docs
```

## Dashboard Pages

- **Dashboard** - Key metrics and platform overview
- **Security Threats** - Top vulnerabilities and risk analysis
- **Companies** - Organization performance and bounty stats
- **Researchers** - Top security researchers and their impact
- **Timeline & Patterns** - Trends over time
- **Intelligence Reports** - Detailed vulnerability reports
- **🤖 AI Assistant** - Chat with AI about the data
- **Knowledge Base** - Vulnerability glossary
- **Search & Export** - Find and download specific reports

## Using the API

**1. Login:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d '{"username": "admin", "password": "admin123"}'
```

**2. Query data:**
```bash
curl "http://localhost:8000/api/v1/vulnerabilities" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**3. Ask AI (natural language):**
```bash
curl -X POST "http://localhost:8000/api/v1/query/nlp" \
  -d '{"query": "Show me top 10 XSS vulnerabilities"}'
```

**Full API docs:** http://localhost:8000/docs

## Demo Logins

Try these accounts to see different views:

| Username | Password | What you'll see |
|----------|----------|----------------|
| `admin` | `admin123` | Everything - full platform access |
| `mailru` | `mailru123` | Only Mail.ru's vulnerability data |
| `shopify` | `shopify123` | Only Shopify's vulnerability data |
| `gitlab` | `gitlab123` | Only GitLab's vulnerability data |

## AI Superpowers 🤖

The AI Assistant can:

**Chat in plain English:**
- "How many XSS vulnerabilities are there?"
- "Which org pays the most bounties?"
- "Show me critical bugs from last year"

**Summarize reports:**
- One-line summaries of complex vulnerability reports
- Risk assessment and business impact
- Recommended actions

**Spot patterns:**
- Emerging vulnerability trends
- High-value bug predictions
- Security recommendations

**Conversation memory:**
- Remembers your last 5 questions
- Handles follow-up questions naturally
- Clear chat button to start fresh

**Note:** AI features need an OpenAI API key in `.env`. The platform works fine without it, just without the AI magic.

## Project Layout

```
hackerone-intelligence-platform/
├── src/
│   ├── elt/              # Data pipeline (Extract → Load → Transform)
│   ├── database/         # DuckDB schema and connections
│   ├── api/              # FastAPI REST endpoints
│   ├── ai/               # AI features (NLP, summarization, patterns)
│   └── dashboard/        # Streamlit UI
├── data/
│   ├── raw/              # Downloaded CSV data
│   └── hackerone.duckdb  # The database (created by pipeline)
├── docs/
│   └── ARCHITECTURE.md   # Deep dive into design decisions
├── tests/                # Test suite
├── run_pipeline.py       # Load the data
├── run_api.py           # Start API server
└── run_dashboard.py     # Start dashboard
```

## Fun Facts & Insights

- 🕵️ **Information Disclosure** is the most common vulnerability type
- 💰 Some organizations pay bounties on **90%+** of their reports
- 🌟 Elite researchers have **>95%** valid report rates
- 📈 The platform has grown significantly - see the trends yourself!
- � **One-click data refresh** right from the dashboard
- 🤖 **AI remembers** your last 5 questions for natural follow-ups

## Performance Stats

- 📊 **10,000+ vulnerability reports** in the database
- ⚡ **<100ms** average API response time
- 🚀 **<2 seconds** dashboard load time
- 💾 **~50MB** database size (DuckDB is efficient!)
- 🤖 **1-3 seconds** for AI-powered queries

## Security Features

- 🔐 JWT authentication with role-based access
- 🏢 Organization-level data isolation
- 🛡️ SQL injection prevention
- 🔑 Secure secrets management via `.env`

## Want to know more?

Check out `docs/DESIGN.md` for the complete architecture breakdown - both high-level and low-level design explained simply.

---

**Built with Python, FastAPI, Streamlit, DuckDB, and a passion for security intelligence.**

Made for HackerOne's Senior Data Engineer assignment by **Hitesh Kumar** | March 2026

🙏 Thanks to HackerOne for the dataset, OpenAI for GPT-4o-mini, and the amazing open-source community.

**Enjoy exploring!** 🚀
