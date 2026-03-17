#!/usr/bin/env python3
"""
Start the Streamlit dashboard
"""
import subprocess
import sys

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   HackerOne Intelligence Platform - Dashboard             ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Starting Streamlit dashboard...
    Dashboard will open in your browser
    """)
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "src/dashboard/app.py",
        "--server.port=8501",
        "--server.address=localhost"
    ])
