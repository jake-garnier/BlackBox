import docker
import boto3
import base64
from flaskw import constants as constants
import os
from shutil import copyfile

# docker build -t jakegarnier/test2 .
# docker manifest create jakegarnier/test2 --amend jakegarnier/test2
# docker manifest push jakegarnier/test2
# docker manifest inspect jakegarnier/test2

# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 147315719954.dkr.ecr.us-east-2.amazonaws.com
# docker tag c1b584db2b6f 147315719954.dkr.ecr.us-east-2.amazonaws.com/blackbox_lambda_repository
# docker push 147315719954.dkr.ecr.us-east-2.amazonaws.com/blackbox_lambda_repository


def build_image(path, uri):

    docker_client = docker.from_env()
    ecr_client = boto3.client('ecr')

    token = ecr_client.get_authorization_token()

    username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    registry = token['authorizationData'][0]['proxyEndpoint'].replace("https://", "")

    # Requires ~/.docker/config.json is deleted
    docker_client.login(
        username=username,
        password=password,
        registry=registry
    )

    docker_client.images.build(
        path=path,
        tag=uri
    )

    for line in docker_client.images.push(repository=uri, stream=True, decode=True):
        print(line)

    return 'Success'

def build_local_repository(requirements_file, test_file, repositoryName):
    os.mkdir(repositoryName)

    requirements_file.save(repositoryName + '/requirements.txt')
    test_file.save(repositoryName + '/test.py')

    copyfile('/Users/jakegarnier/home/blackBoxFlask/flaskw/testingTemplates/pythonTestingTemplateLambda.py', repositoryName + '/app.py')
    copyfile('/Users/jakegarnier/home/blackBoxFlask/flaskw/lambda/Dockerfile', repositoryName + '/Dockerfile')

def delete_all_buckets():

    s3_client = boto3.client('s3')

    buckets = s3_client.list_buckets()

    bucket_names = []

    for bucket in buckets['Buckets']:
        s3_client.delete_bucket(Bucket=bucket['Name'])
        bucket_names.append(bucket['Name'])

    return ("Deleted: " + str(bucket_names))