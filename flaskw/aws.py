import boto3
import json
import yaml

import os

from zipfile import ZipFile

from flaskw import db as db


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

    test_file = db.get_contract(contract_id)[7]
    attempt_file = db.get_attempt(attempt_id)[2]

    zipObj = ZipFile(str(attempt_id) + '.zip', 'w')
    zipObj.write(contract_files_dir + '/' + test_file, test_file)
    zipObj.write(contract_files_dir + '/' + str(attempt_id) + '/' + attempt_file, attempt_file)
    zipObj.close()

    with open(str(attempt_id) + '.zip', 'rb') as f: 
        code = f.read()

    return lam_client.create_function(
        FunctionName=str(attempt_id) + '_lambda',
        Runtime='python3.7',
        Role=role['Role']['Arn'],
        Handler= test_file.rsplit('.', 1)[0] + '.lambda_handler',
        Code={'ZipFile':code})