#!/usr/bin/env python3
"""
Main script to run the complete ELT pipeline
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.elt.pipeline import ELTPipeline
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   HackerOne Intelligence Platform - ELT Pipeline          ║
    ║   Extract → Load → Transform                              ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    pipeline = ELTPipeline()
    
    try:
        count = pipeline.run_full_pipeline()
        
        print("\n" + "="*60)
        print("SUCCESS! Pipeline completed successfully")
        print("="*60)
        print(f"Total records processed: {count:,}")
        print("\nNext Steps:")
        print("   1. Start API server: python -m uvicorn src.api.main:app --reload")
        print("   2. Start dashboard: streamlit run src/dashboard/app.py")
        print("   3. View API docs: http://localhost:8000/docs")
        print("="*60)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
