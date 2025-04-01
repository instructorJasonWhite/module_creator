import logging
import os
import sys

import uvicorn

logging.basicConfig(level=logging.DEBUG)

# Add environment diagnostics
print("=" * 80)
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
print(f"Virtual env: {os.environ.get('VIRTUAL_ENV', 'Not in a virtual environment')}")
print("=" * 80)

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info"
    )
