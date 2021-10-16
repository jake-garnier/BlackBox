"""
File Name: aws.py
Description: Contains the interaction between the application and aws.
"""

import boto3
import json
import yaml
import os
from zipfile import ZipFile
from flaskw import db as db
import shutil


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
def create_lambda(contract_id, attempt_id, contract_files_path):

    # Initialize lambda and iam client
    lam_client = boto3.client('lambda')
    iam_client = boto3.client('iam')

    # Create the lambda iam user and role if it does not exist
    role = iam_client.get_role(RoleName='lambda_executer')
    if role is None:
        create_lambda_executer_iam_user()
        role = iam_client.get_role(RoleName='lambda_executer')

    contract = db.get_contract(contract_id)
    test_file = contract['test_filename']

    attempt = db.get_attempt(attempt_id)
    attempt_file = attempt['attempt_filename']
    attempt_function_name = attempt['function_name']

    # Creates a temporaty file which imports the attempted function 
    shutil.copyfile(contract_files_path + '/' + test_file, contract_files_path + '/tmp')
    line_prepender(contract_files_path + '/tmp', 'from attempt import ' + attempt_function_name)

    # Create a zip file containing the test_file with the appended import, the attempt file, and the testing template
    # which has the lambda handler function
    zipObj = ZipFile(str(attempt_id) + '.zip', 'w')
    zipObj.write(contract_files_path + '/tmp', test_file)
    zipObj.write(contract_files_path + '/' + str(attempt_id) + '/' + attempt_file, attempt_file)
    zipObj.write(PYTHON_TESTING_TEMPLATE_PATH, PYTHON_TESTING_TEMPLATE_NAME)
    zipObj.close()

    # Read in the zip file
    with open(str(attempt_id) + '.zip', 'rb') as f: 
        code = f.read()

    lam_client.create_function(
        FunctionName=str(attempt_id) + '_lambda',
        Runtime='python3.7',
        Role=role['Role']['Arn'],
        Handler=PYTHON_TESTING_TEMPLATE_HANDLER_PATH,
        Code={'ZipFile':code})

    os.remove(str(attempt_id) + '.zip')


"""
Description: Executes the Lambda Function associated with the attempt ID
@arg (int) attempt_id: Identifies the attempt being executed
"""
def execute_lambda(attempt_id):
    lam_client = boto3.client('lambda')

    return lam_client.invoke(
        FunctionName=str(attempt_id) + '_lambda',
        InvocationType='RequestResponse',
        LogType='Tail'
    )


"""
Description: Deletes the Lambda Function associated with the attempt ID
@arg (int) attempt_id: Identifies the attempt being deleted
"""
def delete_lambda(attempt_id):
    lam_client = boto3.client('lambda')

    return lam_client.delete_function(
        FunctionName=str(attempt_id) + '_lambda',
    )


"""
Description: Prepends a line to the top of a file
@arg (str) filename: The path to the file being prepended
     (str) line: The line being prepended
"""
def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)