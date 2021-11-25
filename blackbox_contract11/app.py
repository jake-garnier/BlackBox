import unittest
import json
import boto3
import urllib
import pymysql
import logging
import sys
import re

# rds_host='blackboxdatabase-1.cdnyxpurbpvu.us-east-2.rds.amazonaws.com'
# name='blackboxadmin'
# password='x6978293',
# db_name='blackbox_database'

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

# try:
#     conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
# except pymysql.MySQLError as e:
#     logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
#     logger.error(e)
#     sys.exit()

# s3 = boto3.client('s3')

def lambda_handler(event, context):

    # bucket = event['Records'][0]['s3']['bucket']['name']
    # key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    # attempt_id = int(key.replace('.', '_').split('_')[1])

    # success = False
    # try:
    #     response = s3.get_object(Bucket=bucket, Key=key)
    #     print("CONTENT TYPE: " + response['ContentType'])
    #     success = True
    # except Exception as e:
    #     print(e)
    #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e

    # with conn.cursor() as cur:

    #     cur.execute(
    #         'UPDATE attempts SET ran = 1 WHERE id = %s',
    #         (attempt_id, )
    #     )
    #     cur.execute(
    #         'UPDATE attempts SET failed_tests = %s WHERE id = %s',
    #         ('failed_tests', attempt_id)
    #     )
    #     cur.execute(
    #         'UPDATE attempts SET success = %s WHERE id = %s',
    #         (success, attempt_id)
    #     )

    #     conn.commit()


    # body = json.loads(event['body'])

    # try:
    #     response = s3.get_object(Bucket=body.get('s3'), Key=body.get('s3_file'))
    #     print("CONTENT TYPE: " + response['ContentType'])
    #     return response
    # except Exception as e:
    #     print(e)
    #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e

    # result = unittest.main(module='test', exit=False).result

    # failed_test_names = []
    # for test in result.failures:
    #     failed_test_names.append(str(test[0]))

    return {
        'statusCode': 200,
        # 'failed_test_names': failed_test_names
    }