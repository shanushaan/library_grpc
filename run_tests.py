#!/usr/bin/env python3
import subprocess
import sys
import os

def run_tests():
    """Run all unit tests for the library management system"""
    
    print("Running Library Management System Tests\n")
    
    # Test gRPC Service
    print("Testing gRPC Service...")
    grpc_result = subprocess.run([
        sys.executable, "-m", "unittest", 
        "discover", "-s", "grpc-server/tests", "-v"
    ], capture_output=True, text=True)
    
    print(grpc_result.stdout)
    if grpc_result.stderr:
        print(grpc_result.stderr)
    
    # Test API Gateway
    print("\nTesting API Gateway...")
    api_result = subprocess.run([
        sys.executable, "-m", "unittest", 
        "discover", "-s", "api-gateway/tests", "-v"
    ], capture_output=True, text=True)
    
    print(api_result.stdout)
    if api_result.stderr:
        print(api_result.stderr)
    
    # Summary
    grpc_success = grpc_result.returncode == 0
    api_success = api_result.returncode == 0
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"gRPC Service Tests: {'PASSED' if grpc_success else 'FAILED'}")
    print(f"API Gateway Tests:  {'PASSED' if api_success else 'FAILED'}")
    
    if grpc_success and api_success:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())