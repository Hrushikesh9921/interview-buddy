#!/usr/bin/env python
"""
Setup verification script.
Checks that all components are properly configured.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from utils.logger import logger
from models import init_db


def verify_setup():
    """Verify that the project setup is complete."""
    
    print("=" * 60)
    print("Interview Buddy - Setup Verification")
    print("=" * 60)
    print()
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Python version
    checks_total += 1
    print(f"[{checks_total}] Checking Python version...")
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 9:
        print(f"    ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        checks_passed += 1
    else:
        print(f"    ❌ Python version {python_version.major}.{python_version.minor} is too old (need 3.9+)")
    print()
    
    # Check 2: Environment variables
    checks_total += 1
    print(f"[{checks_total}] Checking environment configuration...")
    try:
        print(f"    App Name: {settings.app_name}")
        print(f"    Version: {settings.app_version}")
        print(f"    Database: {settings.database_url}")
        print(f"    Model: {settings.openai_model}")
        print("    ✅ Configuration loaded")
        checks_passed += 1
    except Exception as e:
        print(f"    ❌ Configuration error: {e}")
    print()
    
    # Check 3: OpenAI API Key
    checks_total += 1
    print(f"[{checks_total}] Checking OpenAI API key...")
    if settings.validate_openai_key():
        print("    ✅ OpenAI API key is set")
        checks_passed += 1
    else:
        print("    ⚠️  OpenAI API key not set (required for full functionality)")
        print("    💡 Add OPENAI_API_KEY to your .env file")
    print()
    
    # Check 4: Database
    checks_total += 1
    print(f"[{checks_total}] Checking database...")
    try:
        if settings.database_path and settings.database_path.exists():
            print(f"    ✅ Database exists at {settings.database_path}")
            checks_passed += 1
        else:
            print(f"    ⚠️  Database not found, will be created on first run")
            checks_passed += 1
    except Exception as e:
        print(f"    ❌ Database error: {e}")
    print()
    
    # Check 5: Required packages
    checks_total += 1
    print(f"[{checks_total}] Checking required packages...")
    required_packages = [
        "streamlit",
        "openai",
        "tiktoken",
        "sqlalchemy",
        "pydantic",
        "plotly",
        "pandas"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if not missing_packages:
        print(f"    ✅ All required packages installed")
        checks_passed += 1
    else:
        print(f"    ❌ Missing packages: {', '.join(missing_packages)}")
        print(f"    💡 Run: pip install -r requirements.txt")
    print()
    
    # Check 6: Directory structure
    checks_total += 1
    print(f"[{checks_total}] Checking directory structure...")
    required_dirs = [
        "pages", "services", "api", "models", "components",
        "utils", "config", "tests", "data", "scripts"
    ]
    
    project_root = Path(__file__).parent.parent
    missing_dirs = [d for d in required_dirs if not (project_root / d).exists()]
    
    if not missing_dirs:
        print(f"    ✅ All directories present")
        checks_passed += 1
    else:
        print(f"    ❌ Missing directories: {', '.join(missing_dirs)}")
    print()
    
    # Summary
    print("=" * 60)
    print(f"Verification Complete: {checks_passed}/{checks_total} checks passed")
    print("=" * 60)
    print()
    
    if checks_passed == checks_total:
        print("✅ Setup is complete! You're ready to start development.")
        print()
        print("Next steps:")
        print("  1. Add your OpenAI API key to .env file (if not done)")
        print("  2. Run: streamlit run app.py")
        print("  3. Open http://localhost:8501 in your browser")
        return 0
    elif checks_passed >= checks_total - 1:
        print("⚠️  Setup is mostly complete with minor issues.")
        print("   The app should work, but you may need to configure OpenAI API.")
        return 0
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(verify_setup())

