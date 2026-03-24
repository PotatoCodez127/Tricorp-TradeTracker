from flask import Flask, send_from_directory
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__, static_folder=None)
CORS(app)

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return send_from_directory(SCRIPT_DIR, 'tricorp-tradetracker-live.html')

if __name__ == '__main__':
    print("Starting Flask Dashboard")
    print("Running on http://localhost:5000/dashboard")
    print("Dashboard fetches from Python backend at http://127.0.0.1:8000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
