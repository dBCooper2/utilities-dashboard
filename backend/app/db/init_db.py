from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.models import SkiResort, WeatherData, EnergyData, InterfaceFlow
from datetime import datetime

def init_db():
    """Initialize database with tables"""
    Base.metadata.create_all(bind=engine)
    
    # Use this function to populate initial data if needed
    db = SessionLocal()
    try:
        populate_initial_data(db)
    finally:
        db.close()

def populate_initial_data(db: Session):
    """Populate database with initial data if needed"""
    # Check if we already have resorts
    resort_count = db.query(SkiResort).count()
    if resort_count > 0:
        return  # Database already has data
    
    # Sample ski resorts
    sample_resorts = [
        {
            "name": "Vail",
            "latitude": 39.6403,
            "longitude": -106.3742,
            "region": "US_WEST",
            "country": "US"
        },
        {
            "name": "Aspen",
            "latitude": 39.1911,
            "longitude": -106.8175,
            "region": "US_WEST",
            "country": "US"
        },
        {
            "name": "Zermatt",
            "latitude": 46.0207,
            "longitude": 7.7491,
            "region": "EU_ALPINE",
            "country": "CH"
        },
        # Add more as needed
    ]
    
    # Add resorts to database
    for resort_data in sample_resorts:
        resort = SkiResort(**resort_data)
        db.add(resort)
    
    db.commit()

if __name__ == "__main__":
    init_db() 