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
    """Print with full context to terminal"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def fetch_mt5_history(account_id: str):
    """Fetch historical trades from MetaTrader 5"""
    print(f"[MT5.HISTORY] === START ===")
    print(f"[MT5.HISTORY] Account ID: '{account_id}' (type={type(account_id).__name__})")
    
    if not account_id or account_id == 'null':
        print(f"[MT5.HISTORY] ERROR: Empty/null account ID")
        return []
    
    try:
        print(f"[MT5.HISTORY] Importing MetaTrader5...")
        import MetaTrader5 as mt5
        print(f"[MT5.HISTORY] MT5 imported")
        
        if not mt5.initialize():
            print(f"[MT5.HISTORY] ERROR: mt5.initialize() failed")
            return []
        print(f"[MT5.HISTORY] MT5 initialized")
        
        account_info = mt5.account_info()
        print(f"[MT5.HISTORY] Account login: {account_info.login}, name: {account_info.name}")
        
        if account_info.login != int(account_id):
            print(f"[MT5.HISTORY] ERROR: Account mismatch (got {account_info.login}, expected {account_id})")
            mt5.shutdown()
            return []
        print(f"[MT5.HISTORY] Account match verified")
        
        today = datetime.now()
        start_date = today - timedelta(days=3650)
        print(f"[MT5.HISTORY] Date range: {start_date} to {today}")
        
        history = mt5.history_deals_get(start_date, today)
        print(f"[MT5.HISTORY] history_deals_get returned: {len(history) if history else 0} deals")
        
        if history is None:
            print(f"[MT5.HISTORY] ERROR: history_deals_get() returned None")
            print(f"[MT5.HISTORY] MT5 Error: {mt5.last_error()}")
            mt5.shutdown()
            return []
        
        trades = []
        balance = 10000  # Starting balance
        for deal in history:
            if deal.entry == mt5.DEAL_ENTRY_OUT:
                profit = deal.profit + deal.commission + deal.swap
                balance += profit
                trades.append({
                    "id": str(deal.ticket),
                    "symbol": deal.symbol,
                    "type": "BUY" if deal.type == mt5.DEAL_TYPE_BUY else "SELL",
                    "volume": round(deal.volume, 2),
                    "openPrice": round(deal.price, 5),
                    "closePrice": round(deal.price, 5),
                    "profit": round(profit, 2),
                    "balance": round(balance, 2),
                    "date": datetime.fromtimestamp(deal.time).strftime('%Y-%m-%d')
                })
        
        print(f"[MT5.HISTORY] Filtered {len(trades)} ENTRY_OUT trades")
        if trades:
            print(f"[MT5.HISTORY] First 3 trades:")
            for t in trades[:3]:
                print(f"[MT5.HISTORY]   - {t['symbol']} {t['type']} ${t['profit']}")
        
        mt5.shutdown()
        print(f"[MT5.HISTORY] === END: {len(trades)} trades ===")
        return trades
        
    except ImportError:
        print(f"[MT5.HISTORY] ERROR: MetaTrader5 module not available")
        return []
    except Exception as e:
        print(f"[MT5.HISTORY] ERROR: {type(e).__name__}: {e}")
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
    log(f"[ERROR] Validation: {', '.join(error_details)}")
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
    print(f"[WEBHOOK] Request from Account {payload.account}")
    
    if payload.token != WEBHOOK_TOKEN:
        log(f"[ERROR] Webhook rejected: Invalid token for Account {payload.account}")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if payload.account <= 0:
        log(f"[ERROR] Webhook rejected: Invalid account number {payload.account}")
        raise HTTPException(status_code=400, detail="Invalid account number")
    
    formatted_trades = []
    for d in payload.deals:
        if not d.symbol or len(d.symbol) < 2:
            log(f"[ERROR] Skipped invalid trade: {d.ticket} - empty symbol")
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
    log(f"[WEBHOOK] Stored {len(formatted_trades)} trades for Account {payload.account}")
    
    return {"status": "success", "deals_processed": len(formatted_trades)}


@app.get("/api/trades/{account_id}")
async def get_trades(account_id: str):
    print(f"[API.GET] Request for Account '{account_id}'")
    print(f"[API.GET] user_data keys: {list(user_data.keys())}")
    
    if account_id in user_data:
        trades = user_data[account_id]
        print(f"[API.GET] Found {len(trades)} trades in cache")
        return trades
    
    print(f"[API.GET] Not in cache, fetching from MT5...")
    trades = fetch_mt5_history(account_id)
    print(f"[API.GET] MT5 returned {len(trades)} trades")
    
    if trades:
        user_data[account_id] = trades
        print(f"[API.GET] Stored in cache")
    
    print(f"[API.GET] Returning {len(trades)} trades")
    return trades


@app.get("/api/history/{account_id}")
async def get_history(account_id: str):
    print(f"[API.HISTORY] Request for Account '{account_id}'")
    trades = fetch_mt5_history(account_id)
    print(f"[API.HISTORY] Returning {len(trades)} trades")
    return trades


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
