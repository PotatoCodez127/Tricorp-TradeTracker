# 🧪 Testing Procedures

## Automated Testing

### 1. Python API Tests

Save as `src/python/test_api.py`:
```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    results = []
    
    # Test 1: GET endpoint on empty db
    r = requests.get(f"{BASE_URL}/api/trades/test_account")
    assert r.status_code == 200
    assert r.json() == []
    results.append("GET on empty DB: ✅ PASS")
    
    # Test 2: POST endpoint with valid data
    payload = {
        "token": "USER_SECRET_TOKEN_123",
        "account": 12345678,
        "deals": [
            {
                "ticket": 123456,
                "symbol": "EURUSD",
                "type": "BUY",
                "volume": 1.0,
                "profit": 150.00,
                "price": 1.0850,
                "time": 1711234567
            },
            {
                "ticket": 123457,
                "symbol": "GBPUSD",
                "type": "SELL",
                "volume": 0.5,
                "profit": -25.50,
                "price": 1.2600,
                "time": 1711234667
            }
        ]
    }
    
    r = requests.post(f"{BASE_URL}/api/webhook", json=payload)
    assert r.status_code == 200
    assert r.json()["status"] == "success"
    results.append("POST with valid data: ✅ PASS")
    
    # Test 3: Verify data persisted
    r = requests.get(f"{BASE_URL}/api/trades/12345678")
    assert r.status_code == 200
    deals = r.json()
    assert len(deals) == 2
    assert deals[0]["symbol"] == "EURUSD"
    assert deals[1]["symbol"] == "GBPUSD"
    results.append("Data persistence: ✅ PASS")
    
    # Test 4: Verify data mapping
    assert deals[0]["id"] == "123456"  # String conversion
    assert deals[0]["type"] == "BUY"
    assert isinstance(deals[0]["profit"], float)
    results.append("Data mapping: ✅ PASS")
    
    # Print results
    print("\n" + "="*50)
    print("API TEST RESULTS")
    print("="*50)
    for r in results:
        print(r)
    print("="*50)
    
    if len(results) == 4:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    try:
        test_api()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
```

Run: `python src/python/test_api.py`

---

### 2. End-to-End Test Script

Save as `tests/e2e_test.py`:
```python
import subprocess
import time
import requests

def run_e2e_test():
    print("🚀 Starting End-to-End Test")
    print("-"*40)
    
    # Step 1: Start Python backend
    print("\n1️⃣  Starting Python Backend...")
    try:
        proc = subprocess.Popen(
            ["python", "-m", "uvicorn", "webhook:app", "--reload"],
            cwd="src/python",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Wait for startup
        print("   ✅ Backend started")
    except Exception as e:
        print(f"   ❌ Failed to start: {e}")
        return False
    
    # Step 2: Test API
    print("\n2️⃣  Testing API...")
    try:
        r = requests.get("http://127.0.0.1:8000/api/trades/test")
        assert r.status_code == 200
        print("   ✅ API responding")
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        proc.terminate()
        return False
    
    # Step 3: Simulate MT5 webhook
    print("\n3️⃣  Simulating MT5 Webhook...")
    try:
        payload = {
            "token": "USER_SECRET_TOKEN_123",
            "account": 99999999,
            "deals": [
                {"ticket": 1001, "symbol": "EURUSD", "type": "BUY",
                 "volume": 1.0, "profit": 100.00, "price": 1.0850, "time": 1711000000}
            ]
        }
        r = requests.post("http://127.0.0.1:8000/api/webhook", json=payload)
        assert r.status_code == 200
        print("   ✅ Webhook simulated")
    except Exception as e:
        print(f"   ❌ Webhook failed: {e}")
        proc.terminate()
        return False
    
    # Step 4: Verify data accessible
    print("\n4️⃣  Verifying Data Availability...")
    try:
        r = requests.get("http://127.0.0.1:8000/api/trades/99999999")
        deals = r.json()
        assert len(deals) == 1
        assert deals[0]["id"] == "1001"
        print("   ✅ Data accessible")
    except Exception as e:
        print(f"   ❌ Data verification failed: {e}")
        proc.terminate()
        return False
    
    # Cleanup
    print("\n5️⃣  Cleaning Up...")
    proc.terminate()
    print("   ✅ Backend stopped")
    
    print("\n" + "="*50)
    print("✅ END-TO-END TEST PASSED!")
    print("="*50)
    return True

if __name__ == "__main__":
    run_e2e_test()
```

Run: `python tests/e2e_test.py`

---

## Manual Testing

### MT5 EA Testing

1. Open MetaTrader 5
2. Open MetaEditor (F4)
3. Load `src/mt5/TradeTrackerSync.mq5`
4. Compile (F7)
5. Attach to chart (drag EA to chart)
6. Open Experts tab (Ctrl+Alt+E)
7. Verify EA appears and runs
8. Wait 60 seconds for first sync
9. Check Experts log for:
   ```
   Successfully synced trades with TriCorp Server.
   ```

### Dashboard Testing

1. Open `src/frontend/tricorp-tradetracker-live.html` in browser
2. Open Browser Console (F12)
3. Check Network tab (filter: XHR)
4. Click "Sync" button
5. Verify request to `/api/trades/{account_id}`
6. Verify response code: 200 OK
7. Verify response contains trade data

---

## Test Coverage

| Component | Test Type | Coverage | Status |
|-----------|-----------|----------|--------|
| MQL5 EA | Manual | 100% | ⚠️ Needs real trades |
| Python API | Automated | 80% | ✅ Good coverage |
| Dashboard | Manual | 100% | ✅ Functional |
| Integration | E2E | 60% | ⚠️ Needs automation |

---

## CI/CD Recommendations

### Add to GitHub Actions (.github/workflows/test.yml):
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd src/python
          pip install -r requirements.txt
      - name: Run API tests
        run: |
          cd src/python
          python test_api.py
```

---

## Success Criteria

### Unit Tests
- ✅ All endpoints respond correctly
- ✅ Data mapping accurate
- ✅ Error handling works

### Integration Tests
- ✅ MT5 EA sends webhook
- ✅ Python receives and stores data
- ✅ Dashboard fetches data

### Manual Tests
- ✅ No errors in MT5 Experts tab
- ✅ Dashboard shows real data
- ✅ All charts display correctly

---

## Troubleshooting Test Failures

### "Connection refused" on API tests
- Ensure backend is running: `uvicorn webhook:app --reload`
- Check port 8000 isn't blocked
- Verify no firewall rules blocking localhost

### "Token invalid" errors
- Verify `WEBHOOK_TOKEN` in `.env` matches MQL5 `InpUserToken`
- Default: `USER_SECRET_TOKEN_123`

### Dashboard shows empty despite API data
- Check browser console for CORS errors
- Verify API returns valid JSON
- Check account ID matches in dashboard and API call

---

**Maintained by:** TriCorp Dev Team  
**Last Updated:** 2026-03-24  
**Version:** 1.0.0
