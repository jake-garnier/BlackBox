"""
File Name: __init__.py
Description: Contains the initialization functions and endpoints of the flask application.
"""

import os
from flaskw import sql as sql
from flaskw import form as form
from flaskw import paypal as paypal
from flaskw import aws as aws
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, g
from flask_mysqldb import MySQL
import boto3

# export FLASK_APP=flaskw && export FLASK_ENV=development && flask run
# Jake's computer's alias for above command is "bb"

# Commands to run build and run server in docker
# docker build -t flask-container .
# docker run -p 5000:5000 flask-container

"""
Description: Default flask create function, inilizes the paypal client, the endpoints, and the database
@arg (mapping) test_config: A potential test configuration input if I eventually implement testing
"""
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        MYSQL_HOST='blackboxdatabase-1.cdnyxpurbpvu.us-east-2.rds.amazonaws.com',
        MYSQL_USER='blackboxadmin',
        MYSQL_PASSWORD='x6978293',
        MYSQL_DB='blackbox_database'
    )

    db = MySQL(app)

    payouts_client = paypal.configure()

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


    """
    Description: The view for creating a contract
    """
    @app.route('/create', methods=('GET', 'POST'))
    def create():
        return form.create_contract_view(request, db)


    """
    Description: The view for the table containing all contracts
    """
    @app.route('/table')
    def table():
        return render_template('table.html',
                               contracts=sql.get_contracts(db),
                               session=session)


    """
    Description: The view for veiwing a certain contract
    @arg (int) id: The id of the contract being viewed
    """
    @app.route('/table/<int:id>', methods=('GET', 'POST'))
    def viewContract(id):
        return form.attempt_view(id, request, db)


    """
    Description: Deletes a contract
    @arg (int) id: The id of the contract being deleted
    @return redirects to the table view
    """
    @app.route('/delete/<int:id>', methods=('GET', 'POST'))
    def deleteContract(id):
        aws.delete_contract_resources(id, db)
        sql.delete_contract(id, db)
        return redirect(url_for('table'))


    """
    Description: The view for registering an account
    """
    @app.route('/register', methods=('GET', 'POST'))
    def register(): 
        return form.register_user_view(request, db)


    """
    Description: The view for logging into an account
    """
    @app.route('/login', methods=('GET', 'POST'))
    def login():
        return form.login_user_view(request, db)


    """
    Description: Logs the user out of their account
    @return redirects to the table view
    """
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('table'))


    """
    Description: Create a payment for the specified contract
    @arg (int) id: The id of the contract being payed for
    """
    @app.route('/paypal/create/<int:id>')
    def paypal_create(id):
        return render_template('paypal_create.html', id=id)


    @app.route('/paypal/payment', methods=['POST'])
    def payment():
        return paypal.create_payment(request, db)


    @app.route('/paypal/execute', methods=['POST'])
    def execute():
        return paypal.execute_payment(request)


    @app.route('/paypal/payout/<int:id>'   )
    def payout(id):
        return paypal.make_payout(payouts_client, id)

    """
    Helper Endpoints
    """
    @app.route('/test')
    def test():
        return "test"

    sql.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv('LISTEN', '0.0.0.0'),
        port=int(os.getenv('PORT', '5000'))
    )
