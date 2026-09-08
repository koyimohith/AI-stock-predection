import subprocess
import time
import sys
import os

def run_project():
    print("=======================================================")
    print("   Launching NIFTY AI Stock Predictor Full Project")
    print("=======================================================")
    print()

    # Determine paths and commands
    python_executable = sys.executable
    
    print("1. Starting Flask API Backend...")
    # Run the API
    api_process = subprocess.Popen(
        [python_executable, "api.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    time.sleep(2) # Give API a moment to spin up
    
    print("2. Starting Streamlit Frontend Dashboard...")
    # Run Streamlit
    streamlit_process = subprocess.Popen(
        [python_executable, "-m", "streamlit", "run", "app.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

    print("\nBoth services are fully launched.")
    print("You can access the Dashboard at: http://localhost:8501")
    print("The backend API is running on: http://localhost:5000")
    print("\nPress Ctrl+C to stop the servers at any time.")
    
    try:
        # Keep the main process alive while the sub-processes are running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")
        api_process.terminate()
        streamlit_process.terminate()
        api_process.wait()
        streamlit_process.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    run_project()
