from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

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

# 1. THE WEBHOOK: MT5 sends data here
@app.post("/api/webhook")
async def receive_mt5_data(payload: WebhookPayload):
    # Process the MT5 deals into the format your HTML expects
    formatted_trades = []
    for d in payload.deals:
        formatted_trades.append({
            "id": str(d.ticket),
            "symbol": d.symbol,
            "type": d.type,
            "volume": d.volume,
            "openPrice": d.price,
            "closePrice": d.price,
            "profit": d.profit,
            "date": d.time # You can format this string in Python or JS
        })
    
    # Save to our "database"
    user_data[str(payload.account)] = formatted_trades
    print(f"✅ Received {len(formatted_trades)} trades for Account {payload.account}")
    return {"status": "success"}

# 2. THE API: Your Dashboard gets data from here
@app.get("/api/trades/{account_id}")
async def get_trades(account_id: str):
    if account_id not in user_data:
        return []
    return user_data[account_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)