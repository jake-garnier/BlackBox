"""
File Name: form.py
Description: Contains functions which manage the various forms in the application.
"""
import datetime
from flaskw import sql as sql
from flaskw import aws as aws
from flaskw import paypal as paypal
from flaskw import container as container
from flaskw.forms import CreateContractForm, AttemptForm, RegisterForm, LoginForm
from flask import flash, render_template, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
import importlib.util
from flask_mysqldb import MySQLdb
import shutil

ALLOWED_TEST_FILE_EXTENSIONS = {'py'}
ALLOWED_ATTEMPT_FILE_EXTENSIONS = {'py'}
ALLOWED_REQUIREMENTS_FILE_EXTENSIONS = {'txt'}


"""
Description: The form view/handler for viewing a contract.
@arg contract_id (int): The id of the contract being viewed.
@arg request (POST request): The request containing the information for the submittion.
@return (template): The view contract template (auto updates upon success).
"""
def attempt_view(contract_id, request, get_db_func):
    form = AttemptForm()
    
    if 'user_id' not in session:
        flash('Please log in or register before creating a contract')
        return redirect(url_for('login'))
    
    if form.validate_on_submit():
        attempt_file = form.file.data
        attempt_file_extension = attempt_file.filename.rsplit('.', 1)[1].lower()
        payment_email = form.payment_email.data

        attempt_info = (contract_id, session['user_id'], 'attempt.' + attempt_file_extension, payment_email, 'Created')
        attempt_id = sql.insert_attempt(attempt_info, get_db_func)

        uploaded_filename = 'attempt_' + str(attempt_id) + '.' + attempt_file_extension
        attempt_file.save(uploaded_filename)

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
            aws.upload_attempt_to_s3(contract_id, attempt_id, uploaded_filename, get_db_func)
            aws.create_ecs_task(contract_id, attempt_id, sql.get_contract(contract_id, get_db_func)['ecr_repository_uri'])
        else:
            flash(error)
            sql.delete_attempt(attempt_id, get_db_func)
    
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}")


    return render_template('contractView.html',
                           contract=sql.get_contract(contract_id, get_db_func),
                           attempts=sql.get_contract_attempts(contract_id, get_db_func),
                           form=form)


"""
Description: The form view/handler for creating a contract.
@arg request (POST request): The request containing the information for the submittion.
@return (template): The template for the create_contract_view if there is an error, else the table template.
"""
def create_contract_view(request, get_db_func):
    form = CreateContractForm()
    
    if 'user_id' not in session:
        flash('Please log in or register before creating a contract')
        return redirect(url_for('login'))
    
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        difficulty = form.difficulty.data
        expiration_date = form.expiration_date.data
        payout = form.payout.data
        test_file = form.test_file.data
        test_code = form.test_code.data
        dockerfile = form.dockerfile.data
        additional_files = request.files.getlist("additional_files")
        
        # Handle test file vs test code
        if test_code and test_code.strip():
            # Create a temporary file from the test code
            import tempfile
            import os
            from werkzeug.datastructures import FileStorage
            from io import BytesIO
            
            # Write test code to a temporary file-like object
            test_content = test_code.encode('utf-8')
            test_file = FileStorage(
                stream=BytesIO(test_content),
                filename='test.py',
                content_type='text/plain'
            )
            test_file_extension = 'py'
        elif test_file and test_file.filename:
            test_file_extension = test_file.filename.rsplit('.', 1)[1].lower()
        else:
            flash('Please provide either test code or upload a test file')
            return render_template('form.html', form=form)

        # WTF Forms handles validation, so we can proceed directly
        contract_info = (title, description, difficulty,
                         datetime.datetime.now(), expiration_date, session['user_id'], payout, 
                         'test.' + test_file_extension, None, None, 'Created')

        contract_id = sql.insert_contract(contract_info, get_db_func)

        repository_name = 'blackbox_contract_' + str(contract_id)
        local_directory_path = 'flaskw/cached_contract_repositories/blackbox_contract_' + str(contract_id)

        container.build_local_contract_directory(test_file, dockerfile, additional_files, local_directory_path)

        uri = aws.create_ecr_repository(repository_name)

        sql.update_contract_status(contract_id, 'Building Container', get_db_func)   

        container.build_image(local_directory_path, uri, repository_name)

        aws_contract_info = {
            's3_bucket_name': aws.create_s3_bucket(contract_id),
            'ecr_repository_name': repository_name,
            'ecr_repository_uri': uri
        }

        sql.add_aws_contract_info(contract_id, aws_contract_info, get_db_func)
        sql.update_contract_status(contract_id, 'Online', get_db_func)

        shutil.rmtree(local_directory_path) 

        return redirect(url_for('paypal_create', id=contract_id))
    
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}")

    return render_template('form.html', form=form)

"""
Description: THe form/view for registering a new account.
@arg: request (POST request): The request containing the information about the submission.
@return (template): The template for registration if there is an error, else the table template.
"""
def register_user_view(request, db):
    form = RegisterForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            sql.insert_user((username, generate_password_hash(password)), db)
            flash('Registration successful! Please log in.')
            return redirect(url_for("login"))
        except MySQLdb._exceptions.IntegrityError:
            flash(f"User {username} is already registered.")
    
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}")

    return render_template('register.html', form=form)


"""
Description: THe form/view for loging into an account.
@arg: request (POST request): The request containing the information about the submission.
@return (template): The template for registration if there is an error, else the table template.
"""
def login_user_view(request, get_db_func):
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = sql.get_user(username, get_db_func)

        if user is None:
            flash('Incorrect username.')
        elif not check_password_hash(user['password'], password):
            flash('Incorrect password.')
        else:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('table'))
    
    elif form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}")
        
    return render_template('login.html', form=form)
