#!/usr/bin/env python3
import unittest
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def run_tests():
    """Run all domain-specific service tests"""
    
    # Test discovery
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Test categories
    test_modules = [
        'tests.test_auth_service',
        'tests.test_book_service', 
        'tests.test_transaction_service',
        'tests.test_request_service',
        'tests.test_user_service'
    ]
    
    print("Running gRPC Service Tests...")
    print("=" * 50)
    
    # Load tests from each module
    for module in test_modules:
        try:
            suite = test_loader.loadTestsFromName(module)
            test_suite.addTest(suite)
            print(f"Loaded tests from {module}")
        except Exception as e:
            print(f"Failed to load {module}: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)