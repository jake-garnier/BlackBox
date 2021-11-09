import docker
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

    docker_client.images.build(
        path=path,
        tag=uri
    )

    return docker_client.images.push(
        repository=uri
    )

def build_local_repository(requirements_file, test_file, repositoryName):
    os.mkdir(repositoryName)
    # os.write(requirements_file, repo_name + '/requirements.txt')
    # os.write(test_file, repo_name + '/app.py')

    requirements_file.save(repositoryName + '/requirements.txt')
    test_file.save(repositoryName + '/test.py')

    copyfile('/Users/jakegarnier/home/blackBoxFlask/flaskw/testingTemplates/pythonTestingTemplateLambda.py', repositoryName + '/app.py')
    copyfile('/Users/jakegarnier/home/blackBoxFlask/flaskw/lambda/Dockerfile', repositoryName + '/Dockerfile')

