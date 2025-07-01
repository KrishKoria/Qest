from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

from .models.database import DatabaseManager, create_indexes
from .models.schemas import QueryRequest, QueryResponse, ErrorResponse, CreateClientRequest, CreateOrderRequest
from .agents.crew_manager import CrewManager
from .api.routes import router
from .config.settings import get_settings

# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global crew manager instance
crew_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global crew_manager
    
    # Startup
    logger.info("Starting Fitness Studio Agent System...")
    
    # Connect to databases
    await DatabaseManager.connect_to_mongo()
    DatabaseManager.connect_to_mongo_sync()
    
    # Create database indexes
    await create_indexes()
    
    # Initialize crew manager
    crew_manager = CrewManager()
    
    logger.info("System startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await DatabaseManager.close_mongo_connection()
    DatabaseManager.close_mongo_connection_sync()
    logger.info("Shutdown complete!")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"  # Allow all origins for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "*",
    ],
    expose_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/", response_model=dict)
async def root():
    """Health check endpoint."""
    return {
        "message": "Fitness Studio Agent System",
        "status": "active",
        "version": "1.0.0"
    }


@app.post("/api/v1/support", response_model=QueryResponse)
async def support_query(request: QueryRequest):
    """Handle support agent queries."""
    try:
        if crew_manager is None:
            raise HTTPException(status_code=503, detail="System not ready")
        
        response = await crew_manager.handle_support_query(
            query=request.query,
            language=request.language,
            context=request.context
        )
        
        return QueryResponse(
            response=response["response"],
            data=response.get("data"),
            context=response.get("context"),
            language=request.language
        )
        
    except ValueError as e:
        # Handle configuration errors (like missing API key)
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Support query error: {str(e)}")
        # Check if it's an OpenAI API error
        if "openai" in str(e).lower() or "api" in str(e).lower():
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API error. Please check your API key and try again."
            )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/dashboard", response_model=QueryResponse)
async def dashboard_query(request: QueryRequest):
    """Handle dashboard agent queries."""
    try:
        if crew_manager is None:
            raise HTTPException(status_code=503, detail="System not ready")
        
        response = await crew_manager.handle_dashboard_query(
            query=request.query,
            language=request.language,
            context=request.context
        )
        
        return QueryResponse(
            response=response["response"],
            data=response.get("data"),
            context=response.get("context"),
            language=request.language
        )
        
    except ValueError as e:
        # Handle configuration errors (like missing API key)
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Dashboard query error: {str(e)}")
        # Check if it's an OpenAI API error
        if "openai" in str(e).lower() or "api" in str(e).lower():
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API error. Please check your API key and try again."
            )
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
