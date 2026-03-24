# 🏃 Quick Start Guide

## Prerequisites
- Python 3.13+ (verify: `python --version`)
- MetaTrader 5
- Browser (Chrome/Firefox/Edge)

## Step 1: Start Python Backend

```bash
cd "C:\Users\jeand\Desktop\New folder\src\python"
pip install -r requirements.txt
uvicorn webhook:app --reload
```

Expected output:
```
INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 2: Configure MQL5 Expert Advisor

1. Open MetaEditor (F4 in MT5)
2. Open `src/mt5/TradeTrackerSync.mq5`
3. Verify inputs:
   ```mql5
   input string InpUserToken = "USER_SECRET_TOKEN_123";
   input string InpWebhookURL = "http://localhost:8000/api/webhook";
   ```
4. Compile (F7)
5. Attach to chart
6. Enable WebRequests: Tools → Options → Expert Advisors → Add `http://localhost:8000`

## Step 3: Open Dashboard

Open `src/frontend/tricorp-tradetracker-live.html` in your browser.

Click **"Sync"** button to fetch trades from Python backend.

## 🧪 Test the Setup

### Test 1: Verify Python Backend
```bash
curl http://127.0.0.1:8000/api/trades/123456
# Should return []
```

### Test 2: Verify MT5 Webhook
After attaching EA to MT5 chart, wait 60 seconds for first sync.

Check Python console for:
```
✅ Received 5 trades for Account 12345678
```

### Test 3: Verify Dashboard
Dashboard should show trade table and charts populated with real data.

## 🐛 Common Issues

### "Connection to Python Backend Failed"
- Ensure backend is running: `uvicorn webhook:app --reload`
- Check firewall allows port 8000
- Verify `http://localhost:8000` is whitelisted in MT5

### "No trades found for this account"
- Ensure EA has generated trades (wait for 60s timer or manual trigger)
- Check MT5 account login matches dashboard selection
- Verify `HistorySelect` has data in last 30 days

### Empty table despite webhook receipt
- Check Python console for processing errors
- Verify `AccountInfoInteger(ACCOUNT_LOGIN)` returns valid account in MT5

## 🔁 Stop Services

Python: `Ctrl+C` in terminal  
MT5: Remove EA from chart  
Dashboard: Close browser tab

## 📊 Verify Data Flow

```
MT5 EA (60s timer)
    ↓ (POST /api/webhook)
Python Backend (stores in memory)
    ↓ (GET /api/trades/{account_id})
Dashboard (displays charts/tables)
```

## 🎯 Expected Timeline

1. **0-60s**: EA collects trades, sends webhook
2. **Python**: Receives, processes, stores
3. **Dashboard**: Fetches, displays on "Sync" click

## 📝 Notes

- Trades are stored **in-memory** (lost on restart)
- EA sends data every **60 seconds**
- Python runs on **localhost only** (not Production-ready)
- Use `.env` to customize configuration (see `.env.example`)
