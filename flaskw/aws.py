"""
File Name: aws.py
Description: Contains the interaction between the application and aws.
"""
import boto3
import json
import yaml
import os
import time
from flaskw import sql as sql
from random import randint
from botocore.exceptions import ClientError
from flaskw import constants as constants
from flaskw import secret_constants as secret_constants

PYTHON_TESTING_TEMPLATE_PATH = 'flaskw/testingTemplates/pythonTestingTemplateLambda.py'
PYTHON_TESTING_TEMPLATE_NAME = 'pythonTestingTemplateLambda.py'
PYTHON_TESTING_TEMPLATE_HANDLER_PATH = 'pythonTestingTemplateLambda.lambda_handler'

lam_client = boto3.client('lambda', region_name='us-east-2', 
    aws_access_key_id=secret_constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=secret_constants.AWS_SECRET_ACCESS_KEY)

iam_client = boto3.client('iam', region_name='us-east-2',
    aws_access_key_id=secret_constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=secret_constants.AWS_SECRET_ACCESS_KEY)

s3_client  = boto3.client('s3', region_name='us-east-2',
    aws_access_key_id=secret_constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=secret_constants.AWS_SECRET_ACCESS_KEY)

ecr_client = boto3.client('ecr', region_name='us-east-2',
    aws_access_key_id=secret_constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=secret_constants.AWS_SECRET_ACCESS_KEY)

"""
Description: Creates the lambda_executer role that has the permission to create and run lambda functions.
I believe it errors out if you run it and the role is already created.
"""
def create_lambda_executer_iam_user():

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
Description: Creates Lambda Function through ECR for a contract.
@arg (int) contract_id: The id for the associated contract
     (str) uri: The uri of the image in the ECR
"""
def create_lambda(contract_id, uri):

    # Create the lambda iam user and role if it does not exist
    try:
        role = iam_client.get_role(RoleName='lambda_executer')
    except:
        create_lambda_executer_iam_user()
        role = iam_client.get_role(RoleName='lambda_executer')

    response = lam_client.create_function(
        PackageType='Image',
        FunctionName=str(contract_id) + '_lambda',
        Role=role['Role']['Arn'],
        Code={'ImageUri':uri+':latest'}
    )

    while True:
        s3_name = "blackbox-contract-" + str(contract_id) + "-bucket-" + str(random_with_N_digits(5))
        try:
            s3_client.create_bucket(
                ACL='private',
                Bucket=s3_name,
                CreateBucketConfiguration={
                    'LocationConstraint': 'us-east-2'
                }
            )
            break
        except ClientError as e:
            error = e.response['Error']['Code']
            if error not in ["BucketAlreadyExists", "BucketAlreadyOwnedByYou"]:
                break

    lam_client.add_permission(
        FunctionName='blackbox_attempt_handler',
        StatementId=str(contract_id),
        Action='lambda:InvokeFunction',
        Principal='s3.amazonaws.com',
        SourceArn='arn:aws:s3:::' + s3_name
    )

    while True:
        try:
            s3_client.put_bucket_notification_configuration(
                Bucket=s3_name,
                NotificationConfiguration= {
                    'LambdaFunctionConfigurations':[{
                        'LambdaFunctionArn': constants.attempt_handler_arn,
                        'Events': ['s3:ObjectCreated:*']
                    }]
                }
            )
            break
        except ClientError as e:
            time.sleep(10)

    return {
        's3': s3_name,
        'lambda': str(contract_id) + '_lambda'
    }

"""
Description: Executes the Lambda Function associated with the attempt ID.
@arg (int) attempt_id: Identifies the attempt being executed.
"""
def upload_attempt_to_s3(contract_id, attempt_id, attempt_file, db):
    contract = sql.get_contract(contract_id, db)

    key = "attempt_" + str(attempt_id)

    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(attempt_file, contract['s3_bucket_name'], key)

    os.remove(key)


"""
Description: Deletes the Lambda Function associated with the inputted name.
@arg (int) attempt_id: The name of the Lambda Function being deleted.
"""
def delete_lambda(name):

    lam_client.delete_function(
        FunctionName=name,
    )


"""
Description: Deletes the s3 bucket associated with the inputted name.
@arg (str) name: The name of the s3 bucket being deleted.
"""
def delete_s3(name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(name)
    bucket.objects.all().delete()
    bucket.delete()    


"""
Description: Deletes the aws resources associated with the contract.
@arg (int) contract_id: The id of the associated contract.
"""
def delete_contract_resources(contract_id, db):
    contract_info = sql.get_contract(contract_id, db)

    delete_lambda(contract_info['lambda_name'])
    delete_s3(contract_info['s3_bucket_name'])

"""
Description: Creates an aws ecr repository
@arg (str) repositoryName: The name of the repository being built
@return (str): The uri of the built repository
"""
def create_ecr_repository(repositoryName):
    
    return ecr_client.create_repository(
        repositoryName=repositoryName
    )['repository']['repositoryUri']

"""
Description: Prepends a line to the top of a file
@arg (str) filename: The path to the file being prepended
     (str) line: The line being prepended
"""
def line_prepender(file, line):
    return line.rstrip('\r\n') + '\n' + file

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)