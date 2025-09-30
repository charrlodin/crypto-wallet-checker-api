"""
Crypto Wallet Scam Checker API
Fast, transparent risk scoring for cryptocurrency addresses
"""
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import config
from data_loader import data_loader
from risk_scorer import RiskScorer
import seed_data

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title=config.API_NAME,
    version=config.API_VERSION,
    description="Check cryptocurrency wallet addresses for scam/sanctions risk. "
                "Combines open data sources with on-chain analysis for fast, transparent risk scoring.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize risk scorer
risk_scorer = None

# Request/Response models
class WalletCheckRequest(BaseModel):
    chain: str = Field(..., description="Blockchain: ethereum, bitcoin, polygon, bsc")
    address: str = Field(..., description="Wallet address to check")
    domain: Optional[str] = Field(None, description="Optional domain if transaction involves a website")
    tx_hash: Optional[str] = Field(None, description="Optional recent transaction hash for deeper analysis")
    
    @validator('chain')
    def validate_chain(cls, v):
        if v.lower() not in config.SUPPORTED_CHAINS:
            raise ValueError(f"Chain must be one of: {', '.join(config.SUPPORTED_CHAINS)}")
        return v.lower()
    
    @validator('address')
    def validate_address(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Address cannot be empty")
        # Basic validation
        if v.startswith("0x"):
            if len(v) != 42:
                raise ValueError("Invalid Ethereum address length")
        elif v.startswith(("1", "3", "bc1")):
            if len(v) < 26 or len(v) > 35:
                raise ValueError("Invalid Bitcoin address length")
        else:
            raise ValueError("Invalid address format")
        return v.lower()


class WalletCheckResponse(BaseModel):
    chain: str
    address: str
    scam_flag: bool
    risk_score: int
    label: str
    reasons: List[str]
    signals: dict
    sources: dict


class StatusResponse(BaseModel):
    status: str
    version: str
    data_sources: dict
    uptime_seconds: float


# Startup event
@app.on_event("startup")
async def startup_event():
    """Load data sources on startup"""
    global risk_scorer
    logger.info("Starting Crypto Wallet Scam Checker API...")
    
    # Load seed data first for immediate availability
    logger.info("Loading seed data...")
    seed_sanctions = seed_data.get_all_sanctioned_addresses()
    seed_scams = seed_data.get_all_scam_addresses()
    seed_domains = seed_data.get_all_phishing_domains()
    
    for chain in config.SUPPORTED_CHAINS:
        data_loader.data_cache["sanctions"][chain].update(seed_sanctions.get(chain, set()))
        data_loader.data_cache["scams"][chain].update(seed_scams.get(chain, set()))
    data_loader.data_cache["phishing_domains"].update(seed_domains)
    
    # Try to load cached external data and merge with seeds
    if data_loader.load_cache():
        logger.info("Loaded additional data from cache")
        # Re-add seed data on top of cache
        for chain in config.SUPPORTED_CHAINS:
            data_loader.data_cache["sanctions"][chain].update(seed_sanctions.get(chain, set()))
            data_loader.data_cache["scams"][chain].update(seed_scams.get(chain, set()))
        data_loader.data_cache["phishing_domains"].update(seed_domains)
    else:
        logger.info("No cache found, fetching fresh data...")
        data_loader.load_all_data()
        # Merge seed data
        for chain in config.SUPPORTED_CHAINS:
            data_loader.data_cache["sanctions"][chain].update(seed_sanctions.get(chain, set()))
            data_loader.data_cache["scams"][chain].update(seed_scams.get(chain, set()))
        data_loader.data_cache["phishing_domains"].update(seed_domains)
    
    # Initialize risk scorer
    risk_scorer = RiskScorer(data_loader)
    
    stats = data_loader.get_stats()
    logger.info("API ready!")
    logger.info(f"Loaded {stats['scams']['ethereum']} ETH scam addresses, {stats['sanctions']['ethereum']} ETH sanctioned addresses")
    logger.info(f"Loaded {stats['phishing_domains']} phishing domains, {stats['mixer_contracts']['ethereum']} mixer contracts")


# Health check
@app.get("/")
async def root():
    """API root - basic info"""
    return {
        "name": config.API_NAME,
        "version": config.API_VERSION,
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "check_wallet": "POST /wallet/check",
            "status": "GET /status"
        }
    }


# RapidAPI ping endpoint
@app.get("/ping")
async def ping():
    """Ping endpoint for RapidAPI health checks"""
    return {"status": "ok", "message": "pong"}


# Main endpoint: Check wallet
@app.post("/wallet/check", response_model=WalletCheckResponse)
async def check_wallet(request: WalletCheckRequest):
    """
    Check a cryptocurrency wallet address for scam/sanctions risk.
    
    Returns a risk score (0-100), label, detailed reasons, and data sources used.
    """
    logger.info(f"Checking {request.chain} address: {request.address[:10]}...")
    
    try:
        # Calculate risk
        result = risk_scorer.calculate_risk(
            chain=request.chain,
            address=request.address,
            domain=request.domain
        )
        
        # Add request details
        result["chain"] = request.chain
        result["address"] = request.address
        
        logger.info(f"Result: {result['label']} (score: {result['risk_score']})")
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking wallet: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


# Status endpoint
@app.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get API status and data source statistics.
    
    Returns dataset counts, last update times, and system health.
    """
    import time
    from datetime import datetime
    
    stats = data_loader.get_stats()
    
    return {
        "status": "operational",
        "version": config.API_VERSION,
        "data_sources": stats,
        "uptime_seconds": time.time() - startup_time
    }


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )


# Track startup time
startup_time = datetime.now().timestamp()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
