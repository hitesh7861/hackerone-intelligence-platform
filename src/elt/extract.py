import os
from pathlib import Path
from datasets import load_dataset
import pandas as pd
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HackerOneDataExtractor:
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_from_huggingface(self, dataset_name: str = "Hacker0x01/disclosed_reports"):
        logger.info(f"Loading dataset from HuggingFace: {dataset_name}")
        
        try:
            dataset = load_dataset(dataset_name)
            
            logger.info(f"Dataset loaded successfully. Keys: {dataset.keys()}")
            
            train_data = dataset['train']
            df = pd.DataFrame(train_data)
            
            logger.info(f"Extracted {len(df)} records")
            logger.info(f"Columns: {df.columns.tolist()}")
            
            output_file = self.output_dir / "hackerone_reports.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"Raw data saved to {output_file}")
            
            self._print_data_summary(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            raise
    
    def _print_data_summary(self, df: pd.DataFrame):
        logger.info("\n" + "="*50)
        logger.info("DATA SUMMARY")
        logger.info("="*50)
        logger.info(f"Total Records: {len(df):,}")
        logger.info(f"Total Columns: {len(df.columns)}")
        logger.info(f"\nColumn Names:\n{df.columns.tolist()}")
        logger.info(f"\nData Types:\n{df.dtypes}")
        logger.info(f"\nNull Values:\n{df.isnull().sum()}")
        logger.info(f"\nMemory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        logger.info("="*50 + "\n")

def main():
    extractor = HackerOneDataExtractor()
    df = extractor.extract_from_huggingface()
    print(f"\nExtraction complete! {len(df):,} records extracted.")
    print(f"Data saved to: data/raw/hackerone_reports.csv")

if __name__ == "__main__":
    main()
