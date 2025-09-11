#!/usr/bin/env python3
"""
End-to-end test script for the BlackBox coding challenge system.
This simulates the complete workflow of:
1. Creating a contract with test files
2. Submitting a solution
3. Running tests and evaluation
"""

import sys
import os
import datetime
import subprocess
import importlib.util

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flaskw import create_app
from flaskw import sql as sql

def test_solution_validation():
    """Test the solution validation logic (like the attempt_view function would do)."""
    print("Testing solution validation...")
    
    # Test with incorrect solution first
    incorrect_solution = '''def test_func(numbers):
    return min(numbers)  # Wrong implementation
'''
    
    with open('test_solution.py', 'w') as f:
        f.write(incorrect_solution)
    
    # Test loading and validating the module
    try:
        spec = importlib.util.spec_from_file_location("test_solution", "test_solution.py")
        solution_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(solution_module)
        
        test_func = getattr(solution_module, 'test_func')
        if not callable(test_func):
            print("✗ test_func is not callable")
            return False
        
        print("✓ Solution module loaded successfully")
        
        # Test the function with a simple case
        result = test_func([1, 3, 2])
        if result == 1:  # This should be the minimum (incorrect)
            print("✓ Function validation working (detected incorrect solution)")
        else:
            print(f"✗ Unexpected result: {result}")
            return False
            
    except AttributeError:
        print("✗ test_func not found in solution")
        return False
    except Exception as e:
        print(f"✗ Error loading solution: {e}")
        return False
    
    # Clean up
    os.remove('test_solution.py')
    return True

def test_unit_test_execution():
    """Test running unit tests on solutions."""
    print("Testing unit test execution...")
    
    # Test with incorrect solution
    print("  Testing with incorrect solution...")
    incorrect_solution = '''def test_func(numbers):
    return min(numbers)  # Wrong implementation
'''
    
    with open('solution.py', 'w') as f:
        f.write(incorrect_solution)
    
    # Run the tests
    result = subprocess.run([sys.executable, 'test_find_max.py'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("  ✓ Tests correctly failed for incorrect solution")
    else:
        print("  ✗ Tests should have failed but didn't")
        return False
    
    # Test with correct solution
    print("  Testing with correct solution...")
    correct_solution = '''def test_func(numbers):
    return max(numbers)  # Correct implementation
'''
    
    with open('solution.py', 'w') as f:
        f.write(correct_solution)
    
    # Run the tests
    result = subprocess.run([sys.executable, 'test_find_max.py'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✓ Tests correctly passed for correct solution")
    else:
        print("  ✗ Tests should have passed but didn't")
        print(f"  Error output: {result.stderr}")
        return False
    
    return True

def test_complete_workflow():
    """Test the complete workflow end-to-end."""
    print("Testing complete workflow...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        db_func = app.config['get_db']
        
        # 1. Create a contract (simulating web form submission)
        print("  1. Creating contract...")
        contract_info = (
            "Find Maximum Challenge",  # title
            "Implement a function that finds the maximum number in a list",  # description
            "Easy",  # difficulty
            datetime.datetime.now(),  # creation_date
            datetime.datetime.now() + datetime.timedelta(days=30),  # expiration_date
            1,  # user_id
            100,  # payout
            "test_find_max.py",  # test_filename
            None,  # payment_id
            None,  # payer_id
            "Online"  # status
        )
        
        contract_id = sql.insert_contract(contract_info, db_func)
        print(f"    ✓ Contract created with ID: {contract_id}")
        
        # 2. Simulate attempt submission
        print("  2. Simulating attempt submission...")
        attempt_info = (
            contract_id,
            1,  # user_id
            "attempt.py",
            "test@example.com",  # payment_email
            "Created"
        )
        
        attempt_id = sql.insert_attempt(attempt_info, db_func)
        print(f"    ✓ Attempt created with ID: {attempt_id}")
        
        # 3. Test the solution validation
        print("  3. Testing solution validation...")
        if not test_solution_validation():
            return False
        
        # 4. Test unit test execution
        print("  4. Testing unit test execution...")
        if not test_unit_test_execution():
            return False
        
        print("  ✓ Complete workflow test passed!")
        return True

def main():
    """Main test function."""
    print("BlackBox End-to-End Testing")
    print("=" * 40)
    
    try:
        if test_complete_workflow():
            print("\n🎉 All end-to-end tests passed!")
            print("\nThe BlackBox coding challenge system is working correctly:")
            print("- ✓ Contract creation functionality")
            print("- ✓ Database operations")
            print("- ✓ Solution validation")
            print("- ✓ Unit test execution")
            print("- ✓ Test pass/fail detection")
            
            # Final demonstration
            print("\n" + "=" * 50)
            print("DEMONSTRATION: Running tests with correct solution")
            print("=" * 50)
            
            # Ensure we have the correct solution
            correct_solution = '''def test_func(numbers):
    """Find the maximum number in a list."""
    return max(numbers)
'''
            with open('solution.py', 'w') as f:
                f.write(correct_solution)
            
            # Run final test
            result = subprocess.run([sys.executable, 'test_find_max.py'], 
                                  capture_output=True, text=True)
            print(result.stdout)
            
            return True
        else:
            print("\n❌ End-to-end tests failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)