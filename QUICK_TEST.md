# 📋 Quick Test Guide

## Run Backend
```bash
cd src/python
python -m uvicorn webhook:app --reload
```

## Test Webhook
```bash
curl -X POST http://127.0.0.1:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{"token":"USER_SECRET_TOKEN_123","account":400295823,"deals":[{"ticket":123,"symbol":"EURUSD","type":"BUY","volume":1.0,"profit":150.00,"price":1.0850,"time":1711234567}]}'
```

## Test API
```bash
curl http://127.0.0.1:8000/api/trades/400295823
```

## Use Dashboard
1. Open `src/frontend/tricorp-tradetracker-live.html`
2. Click "🐍 Python Only" tab
3. Click "Sync" button
4. Data should appear in table

## Expected Logs
```
[2026-03-24 XX:XX:XX] [OK] Webhook processed successfully
[2026-03-24 XX:XX:XX]   Account 400295823
[2026-03-24 XX:XX:XX]   Traded symbols: EURUSD
[2026-03-24 XX:XX:XX]   Total deals: 1
[2026-03-24 XX:XX:XX]   Total profit: $150.00
[2026-03-24 XX:XX:XX] ==================================================
```
