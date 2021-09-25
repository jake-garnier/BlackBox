import os
import flaskw.db as db
import flaskw.form as form
from flask import Flask, request, render_template, redirect, url_for, flash
import datetime

import boto3
import json
import yaml

# export FLASK_APP=flaskw && export FLASK_ENV=development
# flask run

# Commands to run build and run server in docker
# docker build -t flask-container .
# docker run -p 5000:5000 flask-container


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/create', methods=('GET', 'POST'))
    def create():
        return form.create_contract_view(request)

    @app.route('/table')
    def table():
        return render_template('basicTable.html',
                               contracts=db.get_contracts())

    @app.route('/table/<int:id>', methods=('GET', 'POST'))
    def viewContract(id):
        return form.show_contract_view(id, request)

    """
    Helper Endpoints
    """
    @app.route('/addContracts', methods=['POST'])
    def addContracts():
        body = request.get_json(force=True)
        contracts = body["contracts"]
        for contract in contracts:
            contract[3] = datetime.datetime.now()
            contract[4] = datetime.datetime.now()
            db.insert_contract(contract)

        return "inserted contracts"

    @app.route('/printContracts')
    def printContracts():
        return db.print_contract_table()

    @app.route('/test')
    def test():
        lam_client = boto3.client('lambda')
        iam_client = boto3.client('iam')

        # basic_role = """
        # Version: '2012-10-17'
        # Statement:
        #     - Effect: Allow
        #       Principal: 
        #         Service: lambda.amazonaws.com
        #       Action: sts:AssumeRole
        # """

        # # lambda.awazonaws.com can assume this role. 
        # iam_client.create_role(RoleName='test_role2', 
        #     AssumeRolePolicyDocument=json.dumps(yaml.load(basic_role)))

        # # This role has the AWSLambdaBasicExecutionRole managed policy.
        # iam_client.attach_role_policy(RoleName='test_role2', 
        #     PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')


        path = os.path.abspath(os.getcwd())

        with open(path + '/flaskw/test.zip', 'rb') as f: 
            code = f.read()

        role = iam_client.get_role(RoleName='test_role')
        return lam_client.create_function(
            FunctionName='test_lambda',
            Runtime='python3.7',
            Role=role['Role']['Arn'],
            Handler='test.lambda_handler',
            Code={'ZipFile':code})
        
    db.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv('LISTEN', '0.0.0.0'),
        port=int(os.getenv('PORT', '5000'))
    )
