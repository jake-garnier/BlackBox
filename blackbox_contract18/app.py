import unittest
import sys

# s3_client = boto3.client('s3')

def lambda_handler(event, context):

    # bucket = event['Bucket']
    # key    = event['Key']

    response_body = event['ResponseBody']

    # try:
    #     response = s3_client.get_object(Bucket=bucket, Key=key)
    # except Exception as e:
    #     print(e)
    #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e

    filedata = response_body.read()
    
    contents = filedata.decode('utf-8')
    
    with open('/tmp/attempt.py', 'w') as f:
        f.write(contents)
    
    print('CONTESTS: ' + str(contents))
    
    prepend_line('test.py', 'from attempt import test_func')
    
    sys.path.append("/tmp")
    
    result = unittest.main(module='test', exit=False).result

    failed_test_names = []
    for test in result.failures:
        failed_test_names.append(str(test[0]))
        
    print('FAILED TESTS: ' + str(failed_test_names))
   
    return {
        'statusCode': 200,
        'failed_test_names': failed_test_names
    }

def prepend_line(file_name, line):
    """ Insert given string as a new line at the beginning of a file """
    # define name of temporary dummy file
    dummy_file = '/tmp/' + file_name
    # open original file in read mode and dummy file in write mode
    with open(file_name, 'r') as read_obj, open(dummy_file, 'w') as write_obj:
        # Write given line to the dummy file
        write_obj.write(line + '\n')
        # Read lines from original file one by one and append them to the dummy file
        for line in read_obj:
            write_obj.write(line)