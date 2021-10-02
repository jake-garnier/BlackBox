import unittest
import json


def lambda_handler(event, context):
    function_name = json.loads(event['body']).get('function_name')

    result = unittest.main(module='test', exit=False).result

    failed_test_names = []
    for test in result.failures:
        failed_test_names.append(str(test[0]))

    return {
        'statusCode': 200,
        'failed_test_names': failed_test_names,
        'function_name': function_name
    }