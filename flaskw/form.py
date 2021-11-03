"""
File Name: form.py
Description: Contains functions which manage the various forms in the application.
"""

import os
import io
import datetime
import base64
import json
from flaskw import sql as sql
from flaskw import aws as aws
from flaskw import paypal as paypal
from flask import flash, render_template, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlite3 import IntegrityError
import importlib.util
from flask_mysqldb import MySQLdb

ALLOWED_EXTENSIONS = {'java', 'zip', 'py'}


"""
Description: Checks to see if the filename's extension is supported.
@arg filename (str): The filename being checked.
@return (bool): True if the filename is supported.
"""
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

"""
Description: The form view/handler for viewing a contract.
@arg contract_id (int): The id of the contract being viewed.
@arg request (POST request): The request containing the information for the submittion.
@return (template): The view contract template (auto updates upon success).
"""
def attempt_view(contract_id, request, db):
    if request.method == 'POST':
        uploaded_file = request.files['file'] 
        uploaded_file_extension = uploaded_file.filename.rsplit('.', 1)[1].lower()
        contract_files_dir = 'files/' + str(contract_id) + '_files'
        payment_email = request.form['payment_email']

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

        if error is None:
            attempt_info = (contract_id, session['user_id'], 'attempt.' + uploaded_file_extension, 'test_func', payment_email)
            attempt_id = sql.insert_attempt(attempt_info, db)

            uploaded_filename = 'attempt_' + str(attempt_id) + '.' + uploaded_file_extension
            uploaded_file.save(uploaded_filename)

            spec = importlib.util.spec_from_file_location("attempt", uploaded_filename)
            attempt_test = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(attempt_test)
            
            try:
                test_func = getattr(attempt_test, 'test_func')
                if not callable(test_func):
                    error = 'test_func() is not callable in your inputed file'
                
            except AttributeError:
                error = 'test_func() is not in your inputed file'

            if error is None:    
                aws.upload_attempt_to_s3(contract_id, uploaded_filename, db)

                    
            else:
                flash(error)
                sql.delete_attempt(attempt_id, db)

        else:
            flash(error)


    return render_template('contractView.html',
                           contract=sql.get_contract(contract_id, db),
                           attempts=sql.get_contract_attempts(contract_id, db))


"""
Description: The form view/handler for creating a contract.
@arg request (POST request): The request containing the information for the submittion.
@return (template): The template for the create_contract_view if there is an error, else the table template.
"""
def create_contract_view(request, db):
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

            contract_info = (title, description, difficulty,
                             datetime.datetime.now(), expiration_date,
                             session['user_id'], payout, 'test.' + uploaded_file_extension, None, None)

            contract_id = sql.insert_contract(contract_info, db)

            aws_contract_info = aws.create_lambda(contract_id, uploaded_file, db)

            sql.add_aws_contract_info(contract_id, aws_contract_info, db)

            return redirect(url_for('paypal_create', id=contract_id))

        flash(error)

    return render_template('form.html')

"""
Description: THe form/view for registering a new account.
@arg: request (POST request): The request containing the information about the submission.
@return (template): The template for registration if there is an error, else the table template.
"""
def register_user_view(request, db):
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
                sql.insert_user((username, generate_password_hash(password)), db)
            except MySQLdb._exceptions.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("login"))

        flash(error)

    return render_template('register.html')


"""
Description: THe form/view for loging into an account.
@arg: request (POST request): The request containing the information about the submission.
@return (template): The template for registration if there is an error, else the table template.
"""
def login_user_view(request, db):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        user = sql.get_user(username, db)

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
