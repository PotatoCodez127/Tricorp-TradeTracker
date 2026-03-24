# 📑 TriCorp TradeTracker Native Bridge

## 🎯 Overview

Live MT5 trade synchronization system:
- **MQL5 EA** → Pushes trades every 60s
- **Python Backend** (FastAPI) → Collects, validates & serves data
- **HTML Dashboard** → Displays trade history

## 📁 Structure

```
src/
├── mt5/TradeTrackerSync.mq5          # MT5 Expert Advisor
├── python/
│   ├── webhook.py                    # FastAPI backend
│   ├── requirements.txt              # Dependencies
│   └── .env.example                  # Config template
└── frontend/
    └── tricorp-tradetracker-live.html  # Dashboard
```

## 🚀 Setup & Run

### 1. Start Backend
```bash
cd src/python
pip install -r requirements.txt
uvicorn webhook:app --reload
```
Backend runs on `http://127.0.0.1:8000`

### 2. Configure MQL5
1. Compile `src/mt5/TradeTrackerSync.mq5` in MetaEditor
2. Attach to MT5 chart
3. **Inputs auto-show**:
   - `InpWebhookURL` = `http://127.0.0.1:8000/api/webhook`
   - `InpUserToken` = `USER_SECRET_TOKEN_123` (must match Python)
4. Add `http://127.0.0.1:8000` to MT5 WebRequest whitelist

### 3. Use Dashboard
Open `src/frontend/tricorp-tradetracker-live.html` in browser.

Click **"Sync"** to fetch trades from Python backend.

## 🔗 Data Flow

```
MT5 EA (60s timer)
  ↓ HistorySelect → DEAL_ENTRY_OUT filters
  ↓ Extract: ticket, symbol, type, volume, profit, price, time
  ↓ WebRequest(POST) with token, account, deals[]
  ↓
Python Backend (/api/webhook)
  ↓ Validates token
  ↓ Converts Unix timestamp → ISO date (YYYY-MM-DD)
  ↓ Stores in memory: user_data[account_id]
  ↓ Returns: {"status": "success"}
  ↓
Dashboard (doSync() function)
  ↓ Fetches from /api/trades/{account_id}
  ↓ Displays: charts, tables, stats
```

## ✅ Verified

| Component | Status |
|-----------|--------|
| MQL5 EA (JSON, timer, webhook) | ✅ |
| Python (FastAPI, CORS, token validation) | ✅ |
| Date conversion (Unix → ISO) | ✅ |
| HTML (doSync, fetch, rAll) | ✅ |

**Status:** Production-ready (local use)

## 📖 Docs

| File | Purpose |
|------|---------|
| `README.md` (this) | Overview & setup |
| `QUICK_START.md` | Detailed setup guide |
| `TESTING.md` | Testing procedures |
