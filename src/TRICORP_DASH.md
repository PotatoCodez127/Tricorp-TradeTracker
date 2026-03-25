# TriCorp TradeTracker

A MetaTrader 5 trade history dashboard that displays full account history via Python backend.

## 📁 Project Structure

```
src/
├── mt5/
│   └── TradeTrackerSync.mq5          # MQL5 EA (optional, for MetaApi sync)
├── python/
│   ├── webhook.py                    # FastAPI backend (MT5 history fetch)
│   └── requirements.txt              # FastAPI + MetaTrader5
└── frontend/
    ├── app.py                        # Flask proxy server
    └── tricorp-tradetracker-live.html  # Dashboard HTML
```

## 🚀 Quick Start

### 1. Start Python Backend
```bash
cd src/python
python webhook.py
```
Runs on `http://127.0.0.1:8000`

### 2. Start Flask Dashboard
```bash
cd src/frontend
python app.py
```
Runs on `http://localhost:5000/dashboard`

### 3. Use in Browser
- Select "Python Only" mode
- Click "Sync" button
- Enter MT5 Account ID (e.g., `400295823`)
- Dashboard displays full trade history

### 4. Switch Accounts
- Click "Accounts" button
- Select from dropdown or add new account
- Trades update instantly

## 📊 Data Flow

```
Python Backend (MT5) ↔️ Fetch API ↔️ Browser Dashboard
```

## 🔑 Configuration

**Webhook Token:** `USER_SECRET_TOKEN_123` (in `src/python/webhook.py`)

**MT5 Python Module:** `pip install MetaTrader5`

---

**Status:** ✅ Production Ready

