from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List
from datetime import datetime, timedelta
import uvicorn
import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

user_data = {}
WEBHOOK_TOKEN = "USER_SECRET_TOKEN_123"

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def fetch_mt5_history(account_id: str):
    """Fetch historical trades from MetaTrader 5"""
    try:
        import MetaTrader5 as mt5
        if not mt5.initialize():
            log(f"[WARN] MT5 not initialized (terminal not running?)")
            return []
        
        # Get account info to verify we're connected to the right account
        account_info = mt5.account_info()
        log(f"[DEBUG] Account login: {account_info.login}, requested: {account_id}")
        if account_info.login != int(account_id):
            log(f"[WARN] Connected to account {account_info.login}, requested {account_id}")
            mt5.shutdown()
            return []
        
        today = datetime.now()
        # Fetch entire history (start from 10 years ago)
        start_date = today - timedelta(days=3650)
        
        history = mt5.history_deals_get(start_date, today)
        
        if history is None:
            log(f"[ERROR] history_deals_get() failed: {mt5.last_error()}")
            mt5.shutdown()
            return []
        
        trades = []
        for deal in history:
            if deal.entry == mt5.DEAL_ENTRY_OUT:
                profit = deal.profit + deal.commission + deal.swap
                trades.append({
                    "id": str(deal.ticket),
                    "symbol": deal.symbol,
                    "type": "BUY" if deal.type == mt5.DEAL_TYPE_BUY else "SELL",
                    "volume": round(deal.volume, 2),
                    "openPrice": round(deal.price, 5),
                    "closePrice": round(deal.price, 5),
                    "profit": round(profit, 2),
                    "date": datetime.fromtimestamp(deal.time).strftime('%Y-%m-%d')
                })
        
        mt5.shutdown()
        log(f"[OK] Fetched {len(trades)} closed deals from MT5 for Account {account_id}")
        return trades
        
    except ImportError:
        log("[WARN] MetaTrader5 module not loaded")
        return []
    except Exception as e:
        log(f"[WARN] MT5 error (is terminal running?): {e}")
        return []


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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        error_details.append(f"{field}: {error['msg']}")
    log(f"[ERROR] Validation error: {', '.join(error_details)}")
    return JSONResponse(status_code=400, content={"detail": error_details})


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    log(f"[ERROR] Pydantic validation failed: {exc.errors()}")
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    log(f"[WARN] HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.post("/api/webhook")
async def receive_mt5_data(payload: WebhookPayload):
    if payload.token != WEBHOOK_TOKEN:
        log(f"[ERROR] Webhook rejected: Invalid token '{payload.token}' (Account: {payload.account})")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if payload.account <= 0:
        log(f"[ERROR] Webhook rejected: Invalid account number {payload.account}")
        raise HTTPException(status_code=400, detail="Invalid account number")
    
    formatted_trades = []
    for d in payload.deals:
        if not d.symbol or len(d.symbol) < 2:
            log(f"[ERROR] Skipped invalid trade (ticket {d.ticket}): empty symbol")
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
    
    account_str = str(payload.account)
    user_data[account_str] = formatted_trades
    log(f"[OK] Webhook processed: Account {payload.account}, {len(formatted_trades)} trades")
    
    return {"status": "success", "deals_processed": len(formatted_trades)}


@app.get("/api/trades/{account_id}")
async def get_trades(account_id: str):
    log(f"[INFO] GET /api/trades/{account_id}")
    
    # First check if we have cached data from webhook
    if account_id in user_data:
        trades = user_data[account_id]
        log(f"[OUT] Cached: {len(trades)} trades for Account {account_id}")
        log(f"  [SHOWING] First trade: {trades[0]}")
        return trades
    
    # No cached data, fetch from MT5 history
    log(f"[INFO] Fetching {account_id} from MT5 history")
    trades = fetch_mt5_history(account_id)
    
    if trades:
        user_data[account_id] = trades
        log(f"[OUT] MT5 History: {len(trades)} trades for Account {account_id}")
        log(f"  [SHOWING TRADES]")
        for i, t in enumerate(trades[:3]):  # Show first 3
            log(f"    Trade {i+1}: {t['symbol']} {t['type']} profit=${t['profit']}")
        if len(trades) > 3:
            log(f"    ... and {len(trades) - 3} more trades")
    else:
        log(f"[INFO] No data for Account {account_id}")
    return trades


@app.get("/api/history/{account_id}")
async def get_history(account_id: str):
    """Directly fetch MT5 history (bypass cache)"""
    log(f"[INFO] GET /api/history/{account_id}")
    trades = fetch_mt5_history(account_id)
    log(f"[INFO] History endpoint returned {len(trades)} trades")
    
    # Show trades in terminal for visibility
    if trades:
        log(f"  [TRADE LIST]")
        for t in trades[:5]:
            log(f"    - {t['symbol']} {t['type']} ${t['profit']}")
    
    return trades


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import os
    log("=" * 50)
    log(f"[START] Starting TriCorp TradeTracker Backend")
    log(f"[HOST] Listening on http://0.0.0.0:8000")
    log(f"[KEY] Webhook token: {WEBHOOK_TOKEN}")
    log(f"[OK] Python version: {sys.version.split()[0]}")
    log(f"[OK] Webhook.py path: {os.path.abspath(__file__)}")
    log("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
