# 🚀 Start Dashboard

## Method 1: Start Backend AND Flask
```bash
# Terminal 1: Start Python Backend
cd src/python
python -m uvicorn webhook:app --reload

# Terminal 2: Start Flask Dashboard
cd src/frontend
python app.py
```
Access at: http://localhost:5000/dashboard

## Method 2: Direct HTML (no Flask)
```bash
# Just open the HTML file in your browser
src/frontend/tricorp-tradetracker-live.html
```

## Summary
- **Flask** serves the dashboard UI at `http://localhost:5000/dashboard`
- **Python Backend** (FastAPI) serves trade data at `http://127.0.0.1:8000/api/trades/{account_id}`
- Dashboard fetches trades directly from Python backend

## Notes
- Flask is optional - you can use the HTML file directly
- If using Flask, both services must be running
- Python backend is required (stores and serves trade data)
