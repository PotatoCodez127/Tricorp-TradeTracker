from flask import Flask, send_from_directory, request, Response
from flask_cors import CORS
from pathlib import Path
import requests

app = Flask(__name__, static_folder=None)
CORS(app)

SCRIPT_DIR = Path(__file__).parent.resolve()

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return send_from_directory(SCRIPT_DIR, 'tricorp-tradetracker-live.html')

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_api(path):
    backend_url = f'http://127.0.0.1:8000/api/{path}'
    
    print(f"[FLASK PROXY] {request.method} /api/{path} -> {backend_url}")
    
    resp = requests.request(
        method=request.method,
        url=backend_url,
        headers={key: value for key, value in request.headers if key.lower() != 'host'},
        data=request.get_data(),
        params=request.args
    )
    
    print(f"[FLASK PROXY] Backend responded: {resp.status_code}, {resp.text[:100]}")
    
    return Response(
        resp.content,
        status=resp.status_code,
        headers=dict(resp.headers)
    )

if __name__ == '__main__':
    print("Starting Flask Dashboard")
    print("Running on http://localhost:5000/dashboard")
    print("Dashboard fetches from Python backend at http://127.0.0.1:8000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
