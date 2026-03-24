# 📑 TriCorp TradeTracker Native Bridge

## 🎯 Overview

Live MT5 trade synchronization system:
- **MQL5 EA** → Pushes trades every 60s
- **Python Backend** (FastAPI) → Collects & serves data
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
# Runs on http://127.0.0.1:8000
```

### 2. Configure MQL5
1. Compile `src/mt5/TradeTrackerSync.mq5` in MetaEditor
2. Attach to MT5 chart
3. Edit inputs:
   ```mql5
   input string InpWebhookURL = "http://localhost:8000/api/webhook";
   input string InpUserToken = "USER_SECRET_TOKEN_123";  // Must match
   ```
4. Add `http://localhost:8000` to MT5 whitelist (Tools → Options → Expert Advisors)

### 3. Use Dashboard
Open `src/frontend/tricorp-tradetracker-live.html` in browser.

Click **"Sync"** to fetch latest trades.

## 📖 Docs

| File | Purpose |
|------|---------|
| `README.md` (this file) | Overview & setup |
| `QUICK_START.md` | Detailed setup guide |
| `TESTING.md` | Testing procedures |
| `DEPLOYMENT.md` | Production deployment |

## ✅ Verified

| Component | Status |
|-----------|--------|
| MQL5 EA (json, timer, webhook) | ✅ |
| Python (FastAPI, CORS, endpoints) | ✅ |
| HTML (doSync, fetch, rAll) | ✅ |
| Data mapping (ticket→string, date→ISO) | ✅ |

**Status:** Production-ready (local use)
