"""
File Name: aws.py
Description: Contains the interaction between the application and aws.
"""

import boto3
import json
import yaml
import os
from zipfile import ZipFile
from flaskw import sql as sql
import shutil
import io


PYTHON_TESTING_TEMPLATE_PATH = 'flaskw/testingTemplates/pythonTestingTemplateLambda.py'
PYTHON_TESTING_TEMPLATE_NAME = 'pythonTestingTemplateLambda.py'
PYTHON_TESTING_TEMPLATE_HANDLER_PATH = 'pythonTestingTemplateLambda.lambda_handler'


"""
Description: Creates the lambda_executer role that has the permission to create and run lambda functions.
I believe it errors out if you run it and the role is already created.
"""
def create_lambda_executer_iam_user():
    iam_client = boto3.client('iam')

    basic_role = """
    Version: '2012-10-17'
    Statement:
        - Effect: Allow
          Principal: 
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    """

    # lambda.awazonaws.com can assume this role. 
    iam_client.create_role(RoleName='lambda_executer', 
        AssumeRolePolicyDocument=json.dumps(yaml.load(basic_role)))

    # This role has the AWSLambdaBasicExecutionRole managed policy.
    iam_client.attach_role_policy(RoleName='lambda_executer', 
        PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')


"""
Description: Creates Lambda Function to execute an attempt
@arg (int) contract_id: Identifies the associated contract
     (int) attempt_id: Identifies the attempt being executed
     (str) contract_files_path: The path to the files associated with the contract
"""
def create_lambda(contract_id, test_file, db):

    # Initialize lambda and iam client
    lam_client = boto3.client('lambda')
    iam_client = boto3.client('iam')
    s3_client = boto3.client('s3')

    # Create the lambda iam user and role if it does not exist
    try:
        role = iam_client.get_role(RoleName='lambda_executer')
    except:
        create_lambda_executer_iam_user()
        role = iam_client.get_role(RoleName='lambda_executer')

    test_file_str = line_prepender(test_file.read().decode('utf-8'), 'from attempt import test_func')

    # Create a zip file containing the test_file with the appended import and the testing template
    # which has the lambda handler function
    zipObj = ZipFile(str(contract_id) + '.zip', 'w')
    zipObj.writestr('test_file.py', test_file_str)
    zipObj.write(PYTHON_TESTING_TEMPLATE_PATH, PYTHON_TESTING_TEMPLATE_NAME)
    zipObj.close()

    # Read in the zip file
    with open(str(contract_id) + '.zip', 'rb') as f: 
        code = f.read()

    response = lam_client.create_function(
        FunctionName=str(contract_id) + '_lambda',
        Runtime='python3.7',
        Role=role['Role']['Arn'],
        Handler=PYTHON_TESTING_TEMPLATE_HANDLER_PATH,
        Code={'ZipFile':code})

    s3_client.create_bucket(
        ACL='private',
        Bucket='blackbox-contract-function' + str(contract_id),
        CreateBucketConfiguration={
            'LocationConstraint': 'us-east-2'
        }
    )

    lam_client.add_permission(
        FunctionName=str(contract_id) + '_lambda',
        StatementId=str(contract_id),
        Action='lambda:InvokeFunction',
        Principal='s3.amazonaws.com',
        SourceArn='arn:aws:s3:::' + 'blackbox-contract-function' + str(contract_id)
    )

    s3_client.put_bucket_notification_configuration(
        Bucket='blackbox-contract-function' + str(contract_id),
        NotificationConfiguration= {'LambdaFunctionConfigurations':[{'LambdaFunctionArn': response['FunctionArn'], 'Events': ['s3:ObjectCreated:*']}]})

    os.remove(str(contract_id) + '.zip')

    return {
        's3': 'blackbox-contract-function' + str(contract_id),
        'lambda': str(contract_id) + '_lambda'
    }


"""
Description: Executes the Lambda Function associated with the attempt ID
@arg (int) attempt_id: Identifies the attempt being executed
"""
def upload_attempt_to_s3(contract_id, attempt_file, db):
    contract = sql.get_contract(contract_id, db)
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(attempt_file, contract['s3_bucket_name'], attempt_file)


"""
Description: Deletes the Lambda Function associated with the attempt ID
@arg (int) attempt_id: Identifies the attempt being deleted
"""
def delete_lambda(name):
    lam_client = boto3.client('lambda')

    return lam_client.delete_function(
        FunctionName=name,
    )

def delete_s3(name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(name)
    bucket.objects.all().delete()
    bucket.delete()    


def delete_contract_resources(contract_id, db):
    contract_info = sql.get_contract(contract_id, db)

    delete_lambda(contract_info['lambda_name'])
    delete_s3(contract_info['s3_bucket_name'])

"""
Description: Prepends a line to the top of a file
@arg (str) filename: The path to the file being prepended
     (str) line: The line being prepended
"""
def line_prepender(file, line):
    return line.rstrip('\r\n') + '\n' + file