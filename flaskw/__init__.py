import os
from flaskw import db as db
from flaskw import form as form
from flaskw import paypal as paypal
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
import datetime
import importlib.util
import paypalrestsdk

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

    paypal.configure()

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
        return render_template('table.html',
                               contracts=db.get_contracts(),
                               session=session)

    @app.route('/table/<int:id>', methods=('GET', 'POST'))
    def viewContract(id):
        return form.show_contract_view(id, request)

    @app.route('/delete/<int:id>', methods=('GET', 'POST'))
    def deleteContract(id):
        db.delete_contract(id)
        return redirect(url_for('table'))

    @app.route('/register', methods=('GET', 'POST'))
    def register(): 
        return form.register_user_view(request)

    @app.route('/login', methods=('GET', 'POST'))
    def login():
        return form.login_user_view(request)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('table'))

    @app.route('/paypal/create/<int:id>')
    def paypal_create(id):
        return render_template('paypal_create.html', id=id)

    # @app.route('/paypal/payment', methods=['POST'])
    # def payment():
    #     return paypal.create_payment(16)

    # @app.route('/paypal/execute', methods=['POST'])
    # def execute():
    #     return paypal.execute_payment(request)

    @app.route('/paypal/payment', methods=['POST'])
    def payment():
        return paypal.create_payment(request)

    @app.route('/paypal/execute', methods=['POST'])
    def execute():
        return paypal.execute_payment(request)

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
        return str(db.get_contracts())
        
    db.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv('LISTEN', '0.0.0.0'),
        port=int(os.getenv('PORT', '5000'))
    )
