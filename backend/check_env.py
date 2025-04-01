import os
import subprocess
import sys

import pkg_resources

print("=" * 80)
print("ENVIRONMENT DIAGNOSTIC INFO")
print("=" * 80)
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
print(f"Virtual env: {os.environ.get('VIRTUAL_ENV', 'Not in a virtual environment')}")
print("=" * 80)

# Check if we're in a virtual environment
if not os.environ.get("VIRTUAL_ENV"):
    print("WARNING: Not running in a virtual environment!")

# List installed packages
print("\nINSTALLED PACKAGES:")
print("-" * 40)
installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
print(f"Total packages: {len(installed_packages)}")

# Check for critical packages
critical_packages = [
    "openai",
    "fastapi",
    "uvicorn",
    "python-docx",
    "python-multipart",
    "sqlalchemy",
    "pydantic",
]

for package in critical_packages:
    version = installed_packages.get(package, "NOT INSTALLED")
    status = "✓" if package in installed_packages else "✗"
    print(f"{status} {package}: {version}")

# List all packages
print("\nAll installed packages:")
for pkg, version in sorted(installed_packages.items()):
    print(f"  {pkg}: {version}")

# Check for 'python-docx' specifically to diagnose the docx import error
print("\nSpecific check for python-docx:")
try:
    import docx

    print(f"✓ 'docx' module can be imported. Version: {docx.__version__}")
    print(f"  Module location: {docx.__file__}")
except ImportError as e:
    print(f"✗ Failed to import 'docx': {str(e)}")
    # Try to find all installed packages with 'docx' in the name
    docx_packages = [p for p in installed_packages.keys() if "docx" in p]
    if docx_packages:
        print(f"  Found docx-related packages: {', '.join(docx_packages)}")
    else:
        print("  No docx-related packages found")

print("\nDone with environment check.")
