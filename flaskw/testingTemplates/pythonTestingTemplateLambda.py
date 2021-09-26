import json
from importlib import import_module
import test_test
import importlib

def lambda_handler(event, context):
    # TODO implement

    # import_module('test')

    importlib.reload(test_test)

    return test_test.main('arg1 arg2 arg3 arg4'.split(' '))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }