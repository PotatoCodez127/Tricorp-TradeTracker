from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List
from datetime import datetime
import uvicorn
import sys
import json
import os

app = FastAPI()

# Allow your HTML dashboard to talk to this Python server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary in-memory database (Use a JSON file or SQLite for production)
user_data = {}

# Configuration
WEBHOOK_TOKEN = "USER_SECRET_TOKEN_123"

# Define what the incoming trade data looks like
class Trade(BaseModel):
    ticket: int
    symbol: str
    type: str
    volume: float
    profit: float
    price: float
    time: int

class WebhookPayload(BaseModel):
    token: str
    account: int
    deals: List[Trade]

def log(msg: str):
    """Clean, precise log output"""
    # Check if running on Windows to handle emoji encoding
    is_windows = os.name == 'nt'
    prefix = "[ERROR] " if "❌" in msg or "❌" in msg else ""
    
    # Remove emojis on Windows for compatibility
    if is_windows:
        msg = msg.replace("❌", "[ERROR]").replace("✅", "[OK]").replace("⚠️", "[WARN]")
        msg = msg.replace("ℹ️", "[INFO]").replace("📤", "[OUT]").replace("🚀", "[START]")
        msg = msg.replace("📍", "[HOST]").replace("🔐", "[KEY]").replace("✔", "[OK]")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    sys.stdout.flush()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with clear logs"""
    error_details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_details.append(f"{field}: {msg}")
    
    log(f"❌ Validation error: {', '.join(error_details)}")
    log(f"   Request URL: {request.url}")
    log(f"   Method: {request.method}")
    
    return JSONResponse(
        status_code=400,
        content={"detail": error_details}
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    log(f"❌ Pydantic validation failed: {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    log(f"⚠️  HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# 1. THE WEBHOOK: MT5 sends data here
@app.post("/api/webhook")
async def receive_mt5_data(payload: WebhookPayload):
    # Validate token
    if payload.token != WEBHOOK_TOKEN:
        log(f"❌ Webhook rejected: Invalid token '{payload.token}' (Account: {payload.account})")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Validate account format
    if payload.account <= 0:
        log(f"❌ Webhook rejected: Invalid account number {payload.account}")
        raise HTTPException(status_code=400, detail="Invalid account number")
    
    # Process deals
    if not payload.deals:
        log(f"⚠️  Webhook accepted but empty: Account {payload.account} sent 0 deals")
    
    # Format date from Unix timestamp to ISO format (YYYY-MM-DD)
    formatted_trades = []
    for d in payload.deals:
        # Validate trade data
        if not d.symbol or len(d.symbol) < 2:
            log(f"❌ Skipped invalid trade (ticket {d.ticket}): empty symbol")
            continue
            
        date_str = datetime.utcfromtimestamp(d.time).strftime('%Y-%m-%d')
        formatted_trades.append({
            "id": str(d.ticket),
            "symbol": d.symbol,
            "type": d.type.upper() if isinstance(d.type, str) else d.type,
            "volume": round(d.volume, 2),
            "openPrice": round(d.price, 5),
            "closePrice": round(d.price, 5),
            "profit": round(d.profit, 2),
            "date": date_str
        })
    
    # Save to our "database"
    account_str = str(payload.account)
    user_data[account_str] = formatted_trades
    
    # Clear log
    log("=" * 50)
    log(f"✅ Webhook processed successfully")
    log(f"  Account {payload.account}")
    log(f"   Traded symbols: {', '.join(set(t['symbol'] for t in formatted_trades)) if formatted_trades else 'None'}")
    log(f"   Total deals: {len(formatted_trades)}")
    log(f"   Total profit: ${sum(t['profit'] for t in formatted_trades):,.2f}")
    log(f"   Date range: {formatted_trades[0]['date'] if formatted_trades else 'N/A'} - {formatted_trades[-1]['date'] if formatted_trades else 'N/A'}")
    log("=" * 50)
    
    return {"status": "success", "deals_processed": len(formatted_trades)}

# 2. THE API: Your Dashboard gets data from here
@app.get("/api/trades/{account_id}")
async def get_trades(account_id: str):
    if account_id not in user_data:
        log(f"ℹ️  Dashboard request: No data for Account {account_id}")
        return []
    
    trades = user_data[account_id]
    log(f"📤 Dashboard request: Sent {len(trades)} trades to Account {account_id}")
    return trades

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    log("=" * 50)
    log(f"[START] Starting TriCorp TradeTracker Backend")
    log(f"[HOST] Listening on http://0.0.0.0:8000")
    log(f"[KEY] Webhook token: {WEBHOOK_TOKEN}")
    log(f"[OK] Python version: {sys.version.split()[0]}")
    log("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
