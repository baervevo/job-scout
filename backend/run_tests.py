#!/usr/bin/env python3
"""
Test runner script for JobScout backend tests
"""
import sys
import subprocess
import os
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)
        return False

def main():
    """Main test runner function."""
    print("🧪 JobScout Backend Test Suite")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    success = True
    
    # Install test dependencies
    if not run_command("poetry install --with test", "Installing test dependencies"):
        success = False
    
    # Set PYTHONPATH for tests
    env_vars = "PYTHONPATH=."
    
    # Run unit tests
    if not run_command(
        f"{env_vars} poetry run pytest tests/unit/ -v --tb=short", 
        "Running unit tests"
    ):
        success = False
    
    # Run integration tests
    if not run_command(
        f"{env_vars} poetry run pytest tests/integration/ -v --tb=short", 
        "Running integration tests"
    ):
        success = False
    
    # Run all tests with coverage
    if not run_command(
        f"{env_vars} poetry run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html", 
        "Running full test suite with coverage"
    ):
        success = False
    
    # Run specific test categories
    print("\n📊 Test Category Results:")
    
    # Authentication tests
    run_command(
        f"{env_vars} poetry run pytest tests/unit/test_auth.py -v", 
        "Authentication tests"
    )
    
    # Resume processing tests
    run_command(
        f"{env_vars} poetry run pytest tests/unit/test_resume_processing.py -v", 
        "Resume processing tests"
    )
    
    # Matching tests
    run_command(
        f"{env_vars} poetry run pytest tests/unit/test_matching_processor.py -v", 
        "Matching processor tests"
    )
    
    # API route tests
    run_command(
        f"{env_vars} poetry run pytest tests/unit/test_resume_routes.py -v", 
        "API route tests"
    )
    
    # Scraping tests
    run_command(
        f"{env_vars} poetry run pytest tests/unit/test_scraping.py -v", 
        "Scraping functionality tests"
    )
    
    # Model and utility tests
    run_command(
        f"{env_vars} poetry run pytest tests/unit/test_models_and_utils.py -v", 
        "Data models and utility tests"
    )
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests completed successfully!")
        print("📄 Coverage report available in htmlcov/index.html")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()