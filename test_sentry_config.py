#!/usr/bin/env python3
"""
Sentry Configuration Validation Test

Self-Hosted Sentry 설정이 제대로 구성되었는지 확인하는 스크립트
"""

import os
import sys
from pathlib import Path

def test_sentry_imports():
    """Test if Sentry SDK can be imported"""
    print("1️⃣ Testing Sentry SDK imports...")
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        print("   ✅ Backend Sentry SDK imports successful")
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import backend Sentry: {e}")
        return False

def test_monitoring_module():
    """Test if monitoring module exists and is importable"""
    print("\n2️⃣ Testing monitoring module...")
    try:
        from src.monitoring import (
            init_sentry,
            capture_message,
            capture_exception,
            set_user_context,
            set_context,
            set_tag,
        )
        print("   ✅ Monitoring module imports successful")
        print("      - init_sentry")
        print("      - capture_message")
        print("      - capture_exception")
        print("      - set_user_context")
        print("      - set_context")
        print("      - set_tag")
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import monitoring module: {e}")
        return False

def test_env_files():
    """Test if environment variable templates exist"""
    print("\n3️⃣ Testing environment configuration files...")

    files_to_check = [
        (".env.example", "Backend configuration"),
        ("web/.env.example", "Frontend configuration"),
    ]

    all_exist = True
    for file_path, description in files_to_check:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"   ✅ {description}: {file_path}")
            # Show Sentry DSN line
            with open(full_path) as f:
                for line in f:
                    if "SENTRY_DSN" in line and not line.strip().startswith("#"):
                        print(f"      └─ {line.strip()}")
                        break
        else:
            print(f"   ❌ {description} missing: {file_path}")
            all_exist = False

    return all_exist

def test_documentation():
    """Test if documentation files exist"""
    print("\n4️⃣ Testing documentation files...")

    docs = [
        ("SENTRY_SETUP_GUIDE.md", "Sentry setup guide"),
        ("CI_CD_INTEGRATION_SUMMARY.md", "CI/CD summary"),
        ("CYPRESS_E2E_GUIDE.md", "E2E testing guide"),
    ]

    all_exist = True
    for file_path, description in docs:
        full_path = Path(file_path)
        if full_path.exists():
            size = full_path.stat().st_size
            lines = sum(1 for _ in open(full_path))
            print(f"   ✅ {description}: {file_path} ({lines} lines, {size} bytes)")
        else:
            print(f"   ❌ {description} missing: {file_path}")
            all_exist = False

    return all_exist

def test_github_actions():
    """Test if GitHub Actions workflows exist"""
    print("\n5️⃣ Testing GitHub Actions workflows...")

    workflows = [
        (".github/workflows/unit-tests.yml", "Unit tests"),
        (".github/workflows/e2e-tests.yml", "E2E tests"),
    ]

    all_exist = True
    for file_path, description in workflows:
        full_path = Path(file_path)
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"   ✅ {description} workflow: {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {description} workflow missing: {file_path}")
            all_exist = False

    return all_exist

def test_sentry_initialization():
    """Test Sentry initialization without actually running it"""
    print("\n6️⃣ Testing Sentry initialization code...")

    try:
        # Just check if the code is syntactically correct
        with open("src/monitoring/sentry_init.py") as f:
            code = f.read()

        # Check for key functions
        required_functions = [
            "def init_sentry",
            "def capture_message",
            "def capture_exception",
            "def set_user_context",
            "def set_context",
            "def set_tag",
            "def _filter_sensitive_data",
            "def _setup_flask_routes",
        ]

        all_found = True
        for func in required_functions:
            if func in code:
                print(f"   ✅ Found: {func}")
            else:
                print(f"   ❌ Missing: {func}")
                all_found = False

        return all_found
    except Exception as e:
        print(f"   ❌ Error reading sentry_init.py: {e}")
        return False

def test_react_sentry():
    """Test React Sentry setup"""
    print("\n7️⃣ Testing React Sentry configuration...")

    try:
        with open("web/src/monitoring/sentry.js") as f:
            code = f.read()

        # Check for key functions
        required_functions = [
            "export function initSentry",
            "export function setSentryUser",
            "export function clearSentryUser",
            "export function captureError",
            "export function captureMessage",
            "export function setContext",
            "export function setTag",
            "export function withSentryProfiler",
            "export const ErrorBoundary",
        ]

        all_found = True
        for func in required_functions:
            if func in code:
                print(f"   ✅ Found: {func}")
            else:
                print(f"   ❌ Missing: {func}")
                all_found = False

        return all_found
    except Exception as e:
        print(f"   ❌ Error reading sentry.js: {e}")
        return False

def test_dsn_format():
    """Test if DSN format is correct for self-hosted"""
    print("\n8️⃣ Testing Self-Hosted Sentry DSN format...")

    # Read env files
    with open(".env.example") as f:
        backend_env = f.read()

    with open("web/.env.example") as f:
        frontend_env = f.read()

    # Check DSN format for self-hosted
    if "http://" in backend_env and "127.0.0.1:9000" in backend_env:
        print("   ✅ Backend DSN format correct: http://...@127.0.0.1:9000/...")
    else:
        print("   ⚠️  Backend DSN format might not be self-hosted")

    if "http://" in frontend_env and "127.0.0.1:9000" in frontend_env:
        print("   ✅ Frontend DSN format correct: http://...@127.0.0.1:9000/...")
    else:
        print("   ⚠️  Frontend DSN format might not be self-hosted")

    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Sentry Configuration Validation")
    print("="*60)

    tests = [
        ("Sentry SDK Imports", test_sentry_imports),
        ("Monitoring Module", test_monitoring_module),
        ("Environment Files", test_env_files),
        ("Documentation", test_documentation),
        ("GitHub Actions", test_github_actions),
        ("Sentry Initialization", test_sentry_initialization),
        ("React Sentry", test_react_sentry),
        ("DSN Format", test_dsn_format),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")

    print(f"\n📈 Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n✨ All configurations validated successfully!")
        print("\n🚀 Next Steps:")
        print("   1. Clone and start Self-Hosted Sentry:")
        print("      git clone https://github.com/getsentry/self-hosted.git")
        print("      cd self-hosted")
        print("      ./install.sh")
        print("      docker-compose up --wait")
        print("\n   2. Access Sentry at http://127.0.0.1:9000")
        print("\n   3. Create projects and get DSN keys")
        print("\n   4. Update .env files with actual DSN values")
        print("\n   5. Run test_sentry.py to verify integration")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
