#!/usr/bin/env python3
"""
FastAPI Gateway Test Runner
Runs comprehensive test suite with coverage reporting
"""

import subprocess
import sys
import os

def run_tests():
    """Run FastAPI gateway tests with coverage"""
    
    # Change to api-gateway directory
    api_gateway_dir = os.path.join(os.path.dirname(__file__), 'api-gateway')
    os.chdir(api_gateway_dir)
    
    print("🧪 Running FastAPI Gateway Tests...")
    print("=" * 50)
    
    # Install test dependencies
    print("📦 Installing test dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Run tests with coverage
    test_commands = [
        # Run validation tests
        [sys.executable, "-m", "pytest", "tests/test_validation.py", "-v"],
        
        # Run edge case tests  
        [sys.executable, "-m", "pytest", "tests/test_edge_cases.py", "-v"],
        
        # Run all tests with coverage
        [sys.executable, "-m", "pytest", "--cov=gateway", "--cov-report=html", "--cov-report=term-missing", "--cov-fail-under=80", "-v"]
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n🔍 Running test suite {i}/{len(test_commands)}...")
        try:
            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                print(f"❌ Test suite {i} failed with return code {result.returncode}")
            else:
                print(f"✅ Test suite {i} passed")
        except Exception as e:
            print(f"❌ Error running test suite {i}: {e}")
    
    # Generate coverage report
    print("\n📊 Generating coverage report...")
    try:
        subprocess.run([sys.executable, "-m", "coverage", "html"], check=True)
        print("✅ Coverage report generated in htmlcov/index.html")
    except Exception as e:
        print(f"❌ Error generating coverage report: {e}")
    
    print("\n🎯 Test Summary:")
    print("- Input validation tests: Username/password formats, field lengths, data types")
    print("- Business rule tests: Book availability, request type validation, ID constraints") 
    print("- Error handling tests: gRPC failures, service unavailable, unexpected errors")
    print("- Edge case tests: Missing data, concurrent operations, boundary conditions")
    print("- Security tests: SQL injection, XSS attempts, input sanitization")
    print("- Performance tests: Large datasets, connection limits, resource usage")

if __name__ == "__main__":
    run_tests()