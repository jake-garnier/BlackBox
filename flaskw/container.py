import docker
import boto3
import base64
from flaskw import constants as constants
from flaskw import secret_constants as secret_constants
import os
from shutil import copyfile, rmtree
import sh
import sys

# docker build -t jakegarnier/test2 .
# docker manifest create jakegarnier/test2 --amend jakegarnier/test2
# docker manifest push jakegarnier/test2
# docker manifest inspect jakegarnier/test2

# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 147315719954.dkr.ecr.us-east-2.amazonaws.com
# docker tag c1b584db2b6f 147315719954.dkr.ecr.us-east-2.amazonaws.com/blackbox_lambda_repository
# docker push 147315719954.dkr.ecr.us-east-2.amazonaws.com/blackbox_lambda_repository

# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 147315719954.dkr.ecr.us-east-2.amazonaws.com

s3_client = boto3.client('s3', region_name='us-east-2',
    aws_access_key_id=secret_constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=secret_constants.AWS_SECRET_ACCESS_KEY)

ecr_client = boto3.client('ecr', region_name='us-east-2',
    aws_access_key_id=secret_constants.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=secret_constants.AWS_SECRET_ACCESS_KEY)

def build_image(path, uri, ecr_repository_name):

    print(path)
    print(uri)
    print(ecr_repository_name)

    if os.path.exists('~/.docker/config.json'):
        os.remove('~/.docker/config.json')

    docker_client = docker.from_env()
    docker_api = docker.APIClient()

    token = ecr_client.get_authorization_token()

    username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')
    registry = token['authorizationData'][0]['proxyEndpoint'].replace("https://", "")

    # Requires ~/.docker/config.json is deleted
    docker_client.login(
        username=username,
        password=password,
        registry=registry
    )

    baseline_tag = uri + ':baseline'

    docker_client.images.build(
        path=path,
        tag=baseline_tag
    )

    for line in docker_client.images.push(repository=uri, stream=True, decode=True, tag='baseline'):
        print(line)

    return 'Success'

def add_attempt_to_image(attempt_id, attempt_file, uri):

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

    image = docker_client.images.pull(
        repository=uri,
        tag='baseline'
    )

    return 'Success'

def build_local_contract_directory(test_file, dockerfile, additional_files, directoryName):
    os.mkdir(directoryName)

    dockerfile.save(directoryName + '/Dockerfile')
    test_file.save(directoryName + '/test.py')

    for additional_file in additional_files:
        additional_file.save(directoryName + '/' + additional_file.filename)

    cur_path = os.getcwd()

    copyfile(cur_path + '/flaskw/testingTemplates/pythonTestingTemplateLambda.py', directoryName + '/app.py')


def prune_docker_images():
    try:
        docker.client.images.prune(filters='dangling')
        return 'Success'
    except Exception as err:
        return str(err)


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

from contextlib import contextmanager
import json
import os.path as Path

# From: https://github.com/docker/docker-py/issues/2256

@contextmanager
def _flush_existing_login(registry: str) -> None:
    """ handles the known bug 
        where existing stale creds cause login
        to fail.
        https://github.com/docker/docker-py/issues/2256
    """
    config = Path(Path.home() / ".docker" / "config.json") 
    original = config.read_text()
    as_json = json.loads(original)
    as_json['auths'].pop(registry, None)
    config.write_text(json.dumps(as_json))
    try:
        yield
    finally:
        config.write_text(original)