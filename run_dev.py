import os
import subprocess
import sys
import time


def run_backend():
    os.chdir("backend")
    subprocess.Popen([sys.executable, "run.py"])
    os.chdir("..")


def run_frontend():
    os.chdir("frontend")
    subprocess.Popen(["npm", "start"])
    os.chdir("..")


if __name__ == "__main__":
    print("Starting development servers...")

    # Start backend
    print("Starting backend server...")
    run_backend()

    # Wait a bit for backend to start
    time.sleep(2)

    # Start frontend
    print("Starting frontend server...")
    run_frontend()

    print("\nDevelopment servers are running!")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:3000")
    print("\nPress Ctrl+C to stop both servers")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)
