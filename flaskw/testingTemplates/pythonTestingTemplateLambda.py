import unittest
import json
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):

    body = json.loads(event['body'])

    try:
        response = s3.get_object(Bucket=body.get('s3'), Key=body.get('s3_file'))
        print("CONTENT TYPE: " + response['ContentType'])
        return response
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

    result = unittest.main(module='test', exit=False).result

    failed_test_names = []
    for test in result.failures:
        failed_test_names.append(str(test[0]))

    return {
        'statusCode': 200,
        'failed_test_names': failed_test_names
    }