import subprocess
import os
import time
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Configuration (Keep these lines as they are) ---
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
DEPLOYMENT_SCRIPT_PATH = os.path.join(CODE_DIR, 'deploy_sorter.py')
LIVE_LOG_FILE = os.path.join(CODE_DIR, 'live_output.log')

@app.route('/api/start_sort', methods=['POST'])
def start_sort():
    # 1. Clear previous log file
    if os.path.exists(LIVE_LOG_FILE):
        os.remove(LIVE_LOG_FILE)

    # 2. Execute the deployment script using subprocess.Popen
    try:
        # Open the log file for writing
        log_file = open(LIVE_LOG_FILE, 'w')

        # Start the subprocess, redirecting its output to the log file handle
        subprocess.Popen(
            ['python', DEPLOYMENT_SCRIPT_PATH], 
            cwd=CODE_DIR, 
            stdout=log_file,
            stderr=log_file, # Direct errors to the same log file for debugging
            close_fds=True # Ensure file descriptor is closed when process exits
        )
        
        # NOTE: We do NOT close log_file here; the subprocess controls it.

        time.sleep(1) # Give it time to start writing

        return jsonify({
            "status": "success",
            "message": "Classification script executed successfully. Logs streaming now."
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server failed to execute Python script: {str(e)}. Check system PATH."
        }), 500

@app.route('/api/get_logs', methods=['GET'])
def get_logs():
    # ... (Keep this function exactly as it was in the previous step) ...
    # This polling function remains correct and handles reading the file.
    if not os.path.exists(LIVE_LOG_FILE):
        return jsonify({
            "logs": ["Status: Server is running. Awaiting start signal..."],
            "running": False
        })
    
    try:
        with open(LIVE_LOG_FILE, 'r') as f:
            logs = f.readlines()
            is_running = not any("CLASSIFICATION BATCH COMPLETE" in line for line in logs)

            return jsonify({
                "logs": [line.strip() for line in logs],
                "running": is_running
            })
    except Exception as e:
        return jsonify({"logs": [f"Error reading log file: {str(e)}"], "running": True})


if __name__ == '__main__':
    print(f"Flask server started. Ready to execute: {DEPLOYMENT_SCRIPT_PATH}")
    app.run(debug=True, port=5000)