import unittest


def lambda_handler(event, context):
    result = unittest.main(module='test', exit=False).result

    failed_test_names = []
    for test in result.failures:
        failed_test_names.append(str(test[0]))

    return {
        'statusCode': 200,
        'failed_test_names': failed_test_names
    }