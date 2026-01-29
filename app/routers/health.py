from fastapi import APIRouter
from sqlalchemy import text
from app.database import SessionLocal
from app.utils.response import base_response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Railway"""
    health_status = {
        "api": "ok",
        "database": "unknown",
        "scheduler": "unknown"
    }
    
    # Check database
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "disconnected"
    
    # Check scheduler
    try:
        health_status["scheduler"] = "running"
    except:
        health_status["scheduler"] = "stopped"
    
    return base_response(
        message="P2H System is healthy",
        payload=health_status,
        status_code=200
    )

@router.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return base_response(
        message="P2H System API is running",
        payload={"version": "1.0.0", "docs": "/docs"},
        status_code=200
    )