import logging
from src.elt.extract import HackerOneDataExtractor
from src.database.schema import DatabaseSchema
from src.elt.load import DataLoader
from src.elt.transform import DataTransformer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ELTPipeline:
    def __init__(self, db_path: str = "data/hackerone.duckdb"):
        self.db_path = db_path
        self.extractor = HackerOneDataExtractor()
        self.schema = DatabaseSchema(db_path)
        self.loader = DataLoader(db_path)
        self.transformer = DataTransformer(db_path)
    
    def run_full_pipeline(self):
        logger.info("="*60)
        logger.info("STARTING ELT PIPELINE")
        logger.info("="*60)
        
        logger.info("\n[STEP 1/5] EXTRACT: Downloading data from HuggingFace...")
        df = self.extractor.extract_from_huggingface()
        
        logger.info("\n[STEP 2/5] LOAD PREP: Creating database schema...")
        self.schema.create_raw_tables()
        
        logger.info("\n[STEP 3/5] LOAD: Loading raw data into DuckDB...")
        count = self.loader.load_csv_to_raw()
        
        logger.info("\n[STEP 4/5] TRANSFORM: Creating dimension and fact tables...")
        self.transformer.create_dimension_tables()
        self.transformer.create_fact_table()
        
        logger.info("\n[STEP 5/5] TRANSFORM: Creating business metric views...")
        self.transformer.create_business_views()
        
        logger.info("\n" + "="*60)
        logger.info("ELT PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"Total records processed: {count:,}")
        logger.info("="*60)
        
        return count

def main():
    pipeline = ELTPipeline()
    pipeline.run_full_pipeline()
    print("\nFull ELT pipeline execution complete!")
    print("Database ready for querying and analysis")
    print("Next steps: Run API server or dashboard")

if __name__ == "__main__":
    main()
