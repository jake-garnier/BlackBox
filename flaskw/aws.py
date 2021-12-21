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
from shutil import rmtree

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
        StatementId=str(contract_id) + s3_name,
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
        's3_bucket_name': s3_name,
        'lambda_name': str(contract_id) + '_lambda'
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

    os.remove(attempt_file)


"""
Description: Creates an aws ecr repository
@arg (str) repositoryName: The name of the repository being built
@return (str): The uri of the built repository
"""
def create_ecr_repository(repositoryName):
    
    return ecr_client.create_repository(
        repositoryName=repositoryName,
        tags=[
            {
                'Key': 'ecr-repository',
                'Value': 'ecr-repository'
            },
        ]
    )['repository']['repositoryUri']


"""
Description: Deletes the Lambda Function associated with the inputted name.
@arg (int) attempt_id: The name of the Lambda Function being deleted.
"""
def delete_lambda(function_name):

    lam_client.delete_function(
        FunctionName=function_name,
    )


def delete_all_contract_lambda_functions():

    functions = lam_client.list_functions()['Functions']

    function_names = [function["FunctionName"] for function in functions]
    delete_functions = [function_name for function_name in function_names 
                        if len(function_name.split('_')) > 1 and function_name.split('_')[1] == "lambda"]

    try:
        for function_name in delete_functions:
            delete_lambda(function_name)
        return 'Success'
    except Exception as err:
        return str(err)


"""
Description: Deletes the s3 bucket associated with the inputted name.
@arg (str) name: The name of the s3 bucket being deleted.
"""
def delete_s3_bucket(name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(name)
    bucket.objects.all().delete()
    bucket.delete()


def delete_all_contract_s3_buckets():

    buckets = s3_client.list_buckets()['Buckets']

    bucket_names = [bucket['Name'] for bucket in buckets 
                    if len(bucket['Name'].split('-')) > 3 and bucket['Name'].split('-')[0] == 'blackbox']

    try:
        for bucket_name in bucket_names:
            delete_s3_bucket(bucket_name)
        return 'Success'
    except Exception as err:
        return str(err)
    

def delete_ecr_repository(repositoryName):

    return ecr_client.delete_repository(
        repositoryName=repositoryName,
        force=True
    )


def delete_all_contract_ecr_repositories():
    
    repositories = ecr_client.describe_repositories()['repositories']

    try:
        for repo in repositories:
            delete_ecr_repository(repo['repositoryName'])
        return 'Success'
    except Exception as err:
        return str(err)


def delete_local_directory(repository_name):
    curPath = os.getcwd()
    if os.path.exists(curPath + '/flaskw/cached_contract_repositories/' + repository_name):
        rmtree('flaskw/cached_contract_repositories/' + repository_name)


def delete_all_local_contract_directories():
    curPath = os.getcwd()
    local_directories = os.listdir(curPath + '/flaskw/cached_contract_repositories')

    try:
        for local_directory in local_directories:
            delete_local_directory(local_directory)
        return 'Success'
    except Exception as err:
        return str(err)


"""
Description: Deletes the aws resources associated with the contract.
@arg (int) contract_id: The id of the associated contract.
"""
def delete_contract_resources(contract_id, db):
    contract_info = sql.get_contract(contract_id, db)

    delete_lambda(contract_info['lambda_name'])
    delete_s3_bucket(contract_info['s3_bucket_name'])
    delete_ecr_repository(contract_info['ecr_repository_name'])
    delete_local_directory(contract_info['local_repository_name'])


def hard_reset_application(db):
    results = [
        delete_all_contract_lambda_functions(),
        delete_all_contract_s3_buckets(),
        delete_all_contract_ecr_repositories(),
        delete_all_local_contract_directories(),
        sql.reset_database(db)
    ]

    return str(results)


def soft_reset_application(db):
    contracts = sql.get_contracts()

    try:
        for contract in contracts:
            delete_contract_resources(contract['id', db])
        return sql.reset_database(db)
    except Exception as err:
        return str(err) + ' on contract: ' + str(contract['id'])


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