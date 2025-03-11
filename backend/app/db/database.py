import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection settings from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "energy_dashboard")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
TIMESCALE_ENABLED = os.getenv("TIMESCALE_ENABLED", "True").lower() == "true"
CHUNK_TIME_INTERVAL = os.getenv("CHUNK_TIME_INTERVAL", "1 day")

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to initialize TimescaleDB extension and create hypertables
def init_timescale_db():
    if not TIMESCALE_ENABLED:
        return
    
    # Connect to the database
    with engine.connect() as conn:
        # Create TimescaleDB extension if it doesn't exist
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
        conn.commit()

# Function to create hypertable for a time-series table
def create_hypertable(table_name, time_column="timestamp"):
    if not TIMESCALE_ENABLED:
        return
    
    # Connect to the database
    with engine.connect() as conn:
        # Check if the table already exists as a hypertable
        result = conn.execute(text(f"""
            SELECT * FROM timescaledb_information.hypertables 
            WHERE hypertable_name = '{table_name}';
        """))
        
        # If the table is not already a hypertable, convert it
        if not result.fetchone():
            conn.execute(text(f"""
                SELECT create_hypertable(
                    '{table_name}', '{time_column}',
                    if_not_exists => TRUE,
                    create_default_indexes => TRUE
                );
            """))
            
            # Set chunk time interval
            conn.execute(text(f"""
                SELECT set_chunk_time_interval(
                    '{table_name}', interval '{CHUNK_TIME_INTERVAL}'
                );
            """))
        
        conn.commit() 