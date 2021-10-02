import os
import datetime
import base64
import json
from flaskw import db as db
from flaskw import aws as aws
from flaskw import paypal as paypal
from flask import flash, render_template, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlite3 import IntegrityError
import importlib.util

ALLOWED_EXTENSIONS = {'java', 'zip', 'py'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def show_contract_view(contract_id, request):
    if request.method == 'POST':
        function_name = request.form['function_name']
        uploaded_file = request.files['file']
        uploaded_file_extension = uploaded_file.filename.rsplit('.', 1)[1].lower()
        contract_files_dir = 'files/' + str(contract_id) + '_files'

        error = None

        if 'user_id' not in session:
            flash('Please log in or register before creating a contract')
            return redirect(url_for('login'))
        elif not uploaded_file:
            error = 'Attempt file is required'
        elif not allowed_file(uploaded_file.filename):
            error = 'Attempt file is not a Java file'
        elif uploaded_file.filename is '':
            error = 'Attempt file has no name'
        elif not os.path.isdir(contract_files_dir):
            error = '{Internal Error} Contract does not have file directory'

        if error is None:
            attempt_info = (contract_id, session['user_id'], 'attempt.' + uploaded_file_extension, function_name)
            attempt_id = db.insert_attempt(attempt_info)

            contract_path = contract_files_dir + '/' + str(attempt_id)

            os.makedirs(contract_files_dir + '/' + str(attempt_id))
            uploaded_file.save(contract_path + '/' + 'attempt.' + uploaded_file_extension)

            spec = importlib.util.spec_from_file_location("attempt", contract_path + '/' + 'attempt.' + uploaded_file_extension)
            attempt_test = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(attempt_test)
            
            try:
                test_func = getattr(attempt_test, function_name)
                if not callable(test_func):
                    error = 'Function name: ' + function_name + ' is not callable in your inputed file'
                
            except AttributeError:
                error = 'Function name: ' + function_name + ' is not in your inputed file'

            if error is None:    
                aws.create_lambda(contract_id, attempt_id, contract_files_dir)

                response = aws.execute_lambda(attempt_id)
                payload = json.loads(response["Payload"].read())

                logs_bytes = response['LogResult'].encode('ascii')
                logs_base64_bytes = base64.b64decode(logs_bytes)
                logs = logs_base64_bytes.decode('ascii')

                aws.delete_lambda(attempt_id)

                success = len(payload['failed_test_names']) == 0
                db.add_result_to_attempt(attempt_id, str(payload['failed_test_names']), success)

                for test_name in payload['failed_test_names']:
                    flash(test_name + ' FAIL')

                if success:
                    flash('Success!')
            else:
                flash(error)
                db.delete_attempt(attempt_id)

        else:
            flash(error)


    return render_template('contractView.html',
                           contract=db.get_contract(contract_id),
                           attempts=db.get_contracts_attempts(contract_id))


def create_contract_view(request):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        difficulty = request.form['difficulty']
        expiration_date = request.form['expiration_date']
        payout = request.form['payout']
        uploaded_file = request.files['file']
        uploaded_file_extension = uploaded_file.filename.rsplit('.', 1)[1].lower()

        error = None

        if 'user_id' not in session:
            flash('Please log in or register before creating a contract')
            return redirect(url_for('login'))
        elif not title:
            error = 'Title is required'
        elif not description:
            error = 'Description is required'
        elif not difficulty:
            error = 'Difficulty is required'
        elif not expiration_date:
            error = 'Expiration Date is required'
        elif not payout:
            error = 'Payout is required'
        elif not uploaded_file:
            error = 'Test file is required'
        elif not allowed_file(uploaded_file.filename):
            error = 'Test file is not a Java file'
        elif uploaded_file.filename is '':
            error = 'Test file has no name'

        if error is None:
            paypal.create_payment(payout)

            contract_info = (title, description, difficulty,
                             datetime.datetime.now(), expiration_date,
                             session['user_id'], payout, 'test.' + uploaded_file_extension)

            contract_id = db.insert_contract(contract_info)

            contract_files_folder = 'files/' + str(contract_id) + '_files'
            os.makedirs(contract_files_folder)

            if uploaded_file.filename != '':
                uploaded_file.save(contract_files_folder + '/' + 'test.' + uploaded_file_extension)

            return redirect(url_for('table'))

        flash(error)

    return render_template('form.html')

def register_user_view(request):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.insert_user((username, generate_password_hash(password)))
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("login"))

        flash(error)

    return render_template('register.html')

def login_user_view(request):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        user = db.get_user(username)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('table'))

        flash(error)
        
    return render_template('login.html')
