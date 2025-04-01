"""Build environment verification script for the module creator project."""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version meets the minimum requirement."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_node_version():
    """Check if Node.js version meets the minimum requirement."""
    print("\nChecking Node.js version...")
    try:
        result = subprocess.run(
            ['node', '--version'], capture_output=True, text=True
        )
        version = result.stdout.strip().replace('v', '')
        major = int(version.split('.')[0])
        if major < 16:
            print("❌ Node.js 16.x or higher is required")
            return False
        print(f"✅ Node.js {version} detected")
        return True
    except FileNotFoundError:
        print("❌ Node.js is not installed")
        return False


def check_required_files():
    """Check if all required files are present in the project."""
    print("\nChecking required files...")
    required_files = [
        '.env.example',
        'requirements.txt',
        'backend/requirements.txt',
        'frontend/package.json',
        'backend/app/main.py',
        'frontend/src/App.tsx',
        'alembic.ini',
        'backend/model_settings.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("✅ All required files present")
    return True


def check_env_file():
    """Check if the .env file is properly set up."""
    print("\nChecking .env file...")
    if not os.path.exists('.env'):
        print("❌ .env file is missing. Please copy .env.example to .env and fill in the values")
        return False
    print("✅ .env file present")
    return True


def check_dependencies():
    """Check if dependencies can be installed."""
    print("\nChecking dependencies...")
    
    # Check Python dependencies
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'list'], check=True)
        print("✅ Python dependencies can be installed")
    except subprocess.CalledProcessError:
        print("❌ Error checking Python dependencies")
        return False
    
    # Check Node.js dependencies
    try:
        subprocess.run(['npm', 'list'], check=True)
        print("✅ Node.js dependencies can be installed")
    except subprocess.CalledProcessError:
        print("❌ Error checking Node.js dependencies")
        return False
    
    return True


def main():
    """Run all build environment checks."""
    print("🔍 Starting build environment verification...")
    
    checks = [
        ("Python Version", check_python_version),
        ("Node.js Version", check_node_version),
        ("Required Files", check_required_files),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n=== Checking {check_name} ===")
        if not check_func():
            all_passed = False
    
    print("\n=== Build Environment Summary ===")
    if all_passed:
        print("✅ All checks passed! The build environment is ready.")
    else:
        print("❌ Some checks failed. Please address the issues above before building.")
        sys.exit(1)


if __name__ == "__main__":
    main()
