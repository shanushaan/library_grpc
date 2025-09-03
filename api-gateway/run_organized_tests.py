#!/usr/bin/env python3
"""
Organized Test Runner for FastAPI Gateway
Runs tests by category with proper coverage reporting
"""

import subprocess
import sys
import os

def run_organized_tests():
    """Run organized test suite with coverage"""
    
    # Change to api-gateway directory
    api_gateway_dir = os.path.dirname(__file__)
    os.chdir(api_gateway_dir)
    
    print("Running Organized FastAPI Gateway Tests...")
    print("=" * 60)
    
    # Test categories
    test_categories = [
        ("Core Tests", "tests/core", "Core validation and utilities"),
        ("Service Tests", "tests/services", "Business logic services"),
        ("Route Tests", "tests/routes", "API endpoint routes"),
        ("Integration Tests", "tests/integration", "End-to-end flows"),
        ("Unit Tests", "tests/unit", "Individual component tests")
    ]
    
    results = []
    
    for category_name, test_path, description in test_categories:
        print(f"\nRunning {category_name}...")
        print(f"Description: {description}")
        print("-" * 40)
        
        try:
            if os.path.exists(test_path):
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    test_path, "-v", "--tb=short"
                ], check=False, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"PASS: {category_name}")
                    results.append((category_name, "PASSED"))
                else:
                    print(f"FAIL: {category_name}")
                    results.append((category_name, "FAILED"))
                    if result.stdout:
                        print("STDOUT:", result.stdout[-500:])  # Last 500 chars
                    if result.stderr:
                        print("STDERR:", result.stderr[-500:])  # Last 500 chars
            else:
                print(f"SKIP: {category_name} directory not found")
                results.append((category_name, "SKIPPED"))
        except Exception as e:
            print(f"ERROR: {category_name}: {e}")
            results.append((category_name, "ERROR"))
    
    # Run full coverage report
    print(f"\nGenerating Coverage Report...")
    print("-" * 40)
    try:
        subprocess.run([
            sys.executable, "-m", "pytest", 
            "--cov=routes", "--cov=services", "--cov=core",
            "--cov-report=html", "--cov-report=term-missing",
            "-v"
        ], check=False)
        print("Coverage report generated in htmlcov/index.html")
    except Exception as e:
        print(f"Error generating coverage report: {e}")
    
    # Summary
    print(f"\nTest Results Summary:")
    print("=" * 60)
    for category, status in results:
        print(f"{category}: {status}")
    
    # Run gRPC server tests
    print(f"\nRunning gRPC Server Tests...")
    print("-" * 40)
    try:
        grpc_server_dir = os.path.join(os.path.dirname(api_gateway_dir), "grpc-server")
        if os.path.exists(grpc_server_dir):
            result = subprocess.run([
                sys.executable, "run_tests.py"
            ], cwd=grpc_server_dir, check=False, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("PASS: gRPC Server Tests")
                results.append(("gRPC Server Tests", "PASSED"))
            else:
                print("FAIL: gRPC Server Tests")
                results.append(("gRPC Server Tests", "FAILED"))
                if result.stdout:
                    print("STDOUT:", result.stdout[-500:])
        else:
            print("SKIP: gRPC server directory not found")
            results.append(("gRPC Server Tests", "SKIPPED"))
    except Exception as e:
        print(f"ERROR: gRPC Server Tests: {e}")
        results.append(("gRPC Server Tests", "ERROR"))
    
    print(f"\nTest Organization:")
    print("FastAPI Gateway:")
    print("- tests/core/: Validation and utility tests")
    print("- tests/services/: Business logic tests") 
    print("- tests/routes/: API endpoint tests")
    print("- tests/integration/: End-to-end flow tests")
    print("- tests/unit/: Individual component tests")
    print("- utils/: Test helpers and mock data")
    print("gRPC Server:")
    print("- tests/test_auth_service.py: Authentication domain tests")
    print("- tests/test_book_service.py: Book management tests")
    print("- tests/test_transaction_service.py: Transaction operation tests")
    print("- tests/test_request_service.py: Request workflow tests")
    print("- tests/test_user_service.py: User management tests")

if __name__ == "__main__":
    run_organized_tests()