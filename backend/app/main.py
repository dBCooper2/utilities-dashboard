from app.utils.init_db import init_db, create_sample_zone_interfaces, create_sample_zone_interface_flow, create_sample_data

@app.on_event("startup")
async def startup_event():
    """Initialize app on startup"""
    # Initialize database if needed
    init_db()
    
    # Create sample zone interfaces and flow data
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        create_sample_zone_interfaces(db)
        create_sample_zone_interface_flow(db)
    finally:
        db.close()
    
    # Start scheduler
    scheduler.start()
    logger.info("Application started") 