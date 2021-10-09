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

def create_lambda(contract_id, attempt_id, contract_files_dir):
    lam_client = boto3.client('lambda')
    iam_client = boto3.client('iam')

    role = iam_client.get_role(RoleName='lambda_executer')
    if role is None:
        create_lambda_executer_iam_user()
        role = iam_client.get_role(RoleName='lambda_executer')
    
    path = os.path.abspath(os.getcwd())

    test_file = db.get_contract(contract_id)['test_filename']

    attempt = db.get_attempt(attempt_id)
    attempt_file = attempt['attempt_filename']
    attempt_function_name = attempt['function_name']

    shutil.copyfile(contract_files_dir + '/' + test_file, contract_files_dir + '/tmp')
    line_prepender(contract_files_dir + '/tmp', 'from attempt import ' + attempt_function_name)

    zipObj = ZipFile(str(attempt_id) + '.zip', 'w')
    zipObj.write(contract_files_dir + '/tmp', test_file)
    zipObj.write(contract_files_dir + '/' + str(attempt_id) + '/' + attempt_file, attempt_file)
    zipObj.write(PYTHON_TESTING_TEMPLATE_PATH, PYTHON_TESTING_TEMPLATE_NAME)
    zipObj.close()

    with open(str(attempt_id) + '.zip', 'rb') as f: 
        code = f.read()

    lam_client.create_function(
        FunctionName=str(attempt_id) + '_lambda',
        Runtime='python3.7',
        Role=role['Role']['Arn'],
        Handler=PYTHON_TESTING_TEMPLATE_HANDLER_PATH,
        Code={'ZipFile':code})

    os.remove(str(attempt_id) + '.zip')

def execute_lambda(attempt_id):
    lam_client = boto3.client('lambda')

    # payload = '{ "function_name": "' + db.get_attempt(attempt_id)[7] + '" }'
    # payload = str.encode(payload)

    return lam_client.invoke(
        FunctionName=str(attempt_id) + '_lambda',
        InvocationType='RequestResponse',
        LogType='Tail'
    )

def delete_lambda(attempt_id):
    lam_client = boto3.client('lambda')

    return lam_client.delete_function(
        FunctionName=str(attempt_id) + '_lambda',
    )

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)