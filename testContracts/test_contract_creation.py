#!/usr/bin/env python3
"""
Test script to verify contract creation functionality works end-to-end.
This will test the database connections and core functionality.
"""

import sys
import os
import datetime
from io import StringIO
from werkzeug.datastructures import FileStorage

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flaskw import create_app
from flaskw import sql as sql

def test_contract_creation():
    """Test contract creation functionality."""
    print("Testing contract creation functionality...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        print("✓ Flask app created successfully")
        
        # Test database connection
        try:
            db_func = app.config['get_db']
            connection = db_func()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            connection.close()
            print("✓ Database connection successful")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
        
        # Test contract insertion
        try:
            contract_info = (
                "Test Find Maximum",  # title
                "Find the maximum number in a list",  # description
                "Easy",  # difficulty
                datetime.datetime.now(),  # creation_date
                datetime.datetime.now() + datetime.timedelta(days=30),  # expiration_date
                1,  # user_id (assuming testuser2 has id 1)
                100,  # payout
                "test_find_max.py",  # test_filename
                None,  # payment_id
                None,  # payer_id
                "Created"  # status
            )
            
            contract_id = sql.insert_contract(contract_info, db_func)
            print(f"✓ Contract created with ID: {contract_id}")
            
            # Test contract retrieval
            contract = sql.get_contract(contract_id, db_func)
            if contract:
                print(f"✓ Contract retrieved: {contract['title']}")
            else:
                print("✗ Failed to retrieve created contract")
                return False
                
            # Test AWS info update (simulate what would happen)
            aws_info = {
                's3_bucket_name': f'test-bucket-{contract_id}',
                'ecr_repository_name': f'test-repo-{contract_id}',
                'ecr_repository_uri': f'123456.dkr.ecr.us-east-1.amazonaws.com/test-repo-{contract_id}'
            }
            
            sql.add_aws_contract_info(contract_id, aws_info, db_func)
            print("✓ AWS contract info updated")
            
            # Test status update
            sql.update_contract_status(contract_id, 'Online', db_func)
            print("✓ Contract status updated")
            
            # Verify final state
            final_contract = sql.get_contract(contract_id, db_func)
            if final_contract['_status'] == 'Online':
                print("✓ Contract creation workflow completed successfully")
                return True
            else:
                print(f"✗ Contract status not updated correctly: {final_contract['_status']}")
                return False
                
        except Exception as e:
            print(f"✗ Contract creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_contract_creation()
    if success:
        print("\n🎉 All tests passed! Contract creation functionality is working.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Contract creation needs fixes.")
        sys.exit(1)