import docker
import boto3
import base64
from flaskw import constants as constants
from flaskw import secret_constants as secret_constants
import os
from shutil import copyfile, rmtree

# docker build -t jakegarnier/test2 .
# docker manifest create jakegarnier/test2 --amend jakegarnier/test2
# docker manifest push jakegarnier/test2
# docker manifest inspect jakegarnier/test2

# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 147315719954.dkr.ecr.us-east-2.amazonaws.com
# docker tag c1b584db2b6f 147315719954.dkr.ecr.us-east-2.amazonaws.com/blackbox_lambda_repository
# docker push 147315719954.dkr.ecr.us-east-2.amazonaws.com/blackbox_lambda_repository

s3_client = boto3.client('s3', region_name='us-east-2',
    aws_access_key_id=secret_constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=secret_constants.AWS_SECRET_ACCESS_KEY)

ecr_client = boto3.client('ecr', region_name='us-east-2',
    aws_access_key_id=secret_constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=secret_constants.AWS_SECRET_ACCESS_KEY)

def build_image(path, uri):

    if os.path.exists('~/.docker/config.json'):
        os.remove('~/.docker/config.json')

    docker_client = docker.from_env()

    token = ecr_client.get_authorization_token()

    username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    registry = token['authorizationData'][0]['proxyEndpoint'].replace("https://", "")

    # Requires ~/.docker/config.json is deleted
    docker_client.login(
        username=username,
        password=password,
        registry=registry
    )

    print(dir(docker_client))
    print(dir(docker_client.images))

    docker_client.images.build(
        path=path,
        tag=uri
    )

    for line in docker_client.images.push(repository=uri, stream=True, decode=True):
        print(line)

    rmtree(path)

    return 'Success'

def build_local_repository(requirements_file, test_file, repositoryName):
    os.mkdir(repositoryName)

    requirements_file.save(repositoryName + '/requirements.txt')
    test_file.save(repositoryName + '/test.py')

    cur_path = os.getcwd()

    copyfile(cur_path + '/flaskw/testingTemplates/pythonTestingTemplateLambda.py', repositoryName + '/app.py')
    copyfile(cur_path + '/flaskw/lambda/Dockerfile', repositoryName + '/Dockerfile')

def delete_all_buckets():

    buckets = s3_client.list_buckets()

    bucket_names = []

    for bucket in buckets['Buckets']:
        s3_client.delete_bucket(Bucket=bucket['Name'])
        bucket_names.append(bucket['Name'])

    return ("Deleted: " + str(bucket_names))

def printDirectory(startpath):
    ret = ''
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        ret = ret + '{}{}/'.format(indent, os.path.basename(root)) + '\n'
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            ret = ret + '{}{}'.format(subindent, f) + '\n'

    return ret