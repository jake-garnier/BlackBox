"""
File Name: __init__.py
Description: Contains the initialization functions and endpoints of the flask application.
"""

import os
from flaskw import sql as sql
from flaskw import form_handlers as form_handlers
from flaskw import paypal as paypal
from flaskw import aws as aws
from flaskw import constants as constants
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, g
import MySQLdb
from flask_wtf.csrf import CSRFProtect
from flaskw import container as container
from flaskw.config import config
from flaskw.logging_config import setup_logging

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

    # Load configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])

    # Setup logging first
    logger = setup_logging(app)

    # Initialize database connection
    try:
        # Create direct MySQL connection
        db_connection = MySQLdb.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            passwd=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB']
        )
        # Test the connection
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        db_connection.close()
        
        # Store connection function in app config for later use
        def get_db():
            return MySQLdb.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                passwd=app.config['MYSQL_PASSWORD'],
                db=app.config['MYSQL_DB']
            )
        app.config['get_db'] = get_db
        db = True  # Flag to indicate database is available
        logger.info("Database connection successful")
    except Exception as e:
        logger.warning(f"Database connection failed: {e}. Running in demo mode without database.")
        db = None
    csrf = CSRFProtect(app)

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
        return form_handlers.create_contract_view(request, app.config['get_db'])


    """
    Description: The view for the table containing all contracts
    """
    @app.route('/table')
    def table():
        if not db:
            # Demo mode without database
            contracts = [
                {'id': 1, 'title': 'Demo Contract 1', 'description': 'Sample contract for testing', 
                 'difficulty': 'Easy', 'payout': 100, '_status': 'Demo Mode'},
                {'id': 2, 'title': 'Demo Contract 2', 'description': 'Another sample contract', 
                 'difficulty': 'Medium', 'payout': 250, '_status': 'Demo Mode'}
            ]
        else:
            contracts = sql.get_contracts(app.config['get_db'])
        
        return render_template('table.html',
                               contracts=contracts,
                               session=session)


    """
    Description: The view for veiwing a certain contract
    @arg (int) id: The id of the contract being viewed
    """
    @app.route('/table/<int:id>', methods=('GET', 'POST'))
    def viewContract(id):
        return form_handlers.attempt_view(id, request, app.config['get_db'])


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
        if not db:
            from flaskw.forms import RegisterForm
            demo_form = RegisterForm()
            flash('Demo mode: Registration not available without database connection.')
            return render_template('register.html', form=demo_form)
        return form_handlers.register_user_view(request, app.config['get_db'])


    """
    Description: The view for logging into an account
    """
    @app.route('/login', methods=('GET', 'POST'))
    def login():
        if not db:
            flash('Demo mode: Login not available without database connection.')
            return render_template('login.html')
        return form_handlers.login_user_view(request, app.config['get_db'])


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


    """
    Description: Creates a paypal payment
    """
    @app.route('/paypal/payment', methods=['POST'])
    def payment():
        return paypal.create_payment(request, db)


    """
    Description: Executes a paypal payment for the creation of a contract
    """
    @app.route('/paypal/execute', methods=['POST'])
    def execute():
        return paypal.execute_payment(request)

    """
    Description: Make a payment for the specified user
    @arg (int) id: The id of the user being payed
    """
    @app.route('/paypal/payout/<int:id>')
    def payout(id):
        return paypal.make_payout(payouts_client, id)

    """
    Helper Endpoints
    """
    @app.route('/')
    def index():
        return redirect(url_for('table'))
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'BlackBox application is running'}
    
    @app.route('/test')
    def test():
        image_uri = '147315719954.dkr.ecr.us-east-2.amazonaws.com/blackbox_contract_3'
        return aws.create_ecs_task(1, 1, image_uri)

    @app.route('/hard_reset_application')
    def hard_reset_application():
        return aws.hard_reset_application(db)
    
    @app.route('/soft_reset_application')
    def soft_reset_application():
        return aws.soft_reset_application(db)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {request.url}")
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        if db and hasattr(db, 'connection') and db.connection:
            try:
                db.connection.rollback()
            except Exception as e:
                logger.warning(f"Failed to rollback database transaction: {e}")
        return render_template('500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        logger.warning(f"403 error: {request.url}")
        return render_template('403.html'), 403
   
    sql.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv('LISTEN', '0.0.0.0'),
        port=int(os.getenv('PORT', '5000'))
    )
