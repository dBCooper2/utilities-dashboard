from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from app.api.routes import router as api_router
from app.core.config import settings, log_settings
from app.db.init_db import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    logger.warning("Application may not function correctly without database")

# Log configuration
log_settings()

# Configure CORS
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS middleware configured with origins: {settings.CORS_ORIGINS}")
except Exception as e:
    logger.error(f"Failed to configure CORS middleware: {e}")
    logger.warning("API may not be accessible from frontend applications")

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get client IP
    client_host = request.client.host if request.client else "unknown"
    
    # Log request
    logger.info(f"Request started: {request.method} {request.url.path} from {client_host}")
    
    # Process request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"- Error: {str(e)} - Time: {process_time:.3f}s"
        )
        raise

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Energy Market Dashboard API"}
