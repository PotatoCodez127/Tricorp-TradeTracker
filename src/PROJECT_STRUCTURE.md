# 📁 Project Structure

```
triCorp-trade-tracker/
├── src/
│   ├── mt5/
│   │   └── TradeTrackerSync.mq5          # MQL5 Expert Advisor
│   ├── python/
│   │   ├── webhook.py                     # FastAPI backend
│   │   ├── requirements.txt               # Python dependencies
│   │   └── .env.example                   # Environment template
│   └── frontend/
│       ├── app.py                         # Flask dashboard server
│       ├── tricorp-tradetracker-live.html # HTML dashboard
│       └── requirements.txt               # Flask dependencies
├── README.md                              # Main documentation
├── START_DASHBOARD.md                     # Dashboard startup guide
├── QUICK_START.md                         # Quick setup guide
├── TESTING.md                             # Testing procedures
└── QUICK_TEST.md                          # Quick test commands
```

## 📦 Components

| Component | File | Purpose |
|-----------|------|---------|
| MQL5 EA | `src/mt5/TradeTrackerSync.mq5` | Push trades from MT5 to Python |
| Python Backend | `src/python/webhook.py` | FastAPI webhook + API |
| Flask Dashboard | `src/frontend/app.py` | Serves HTML to browser |
| HTML Dashboard | `src/frontend/tricorp-tradetracker-live.html` | Display UI with doSync() |

## 🚀 Quick Start

### Start Python Backend
```bash
cd src/python
python -m uvicorn webhook:app --reload
# http://127.0.0.1:8000
```

### Start Flask Dashboard (optional)
```bash
cd src/frontend
python app.py
# http://localhost:5000/dashboard
```

### Or use HTML directly
Open `src/frontend/tricorp-tradetracker-live.html` in browser.

## 📊 Data Flow

```
MT5 EA → WebRequest → Python Backend (port 8000)
Python Backend → GET API → Dashboard
```

## 🔧 Configuration

**Webhook Token:** `USER_SECRET_TOKEN_123` (must match in MQL5 EA)

---

**Status:** ✅ Production Ready (Local Use)
