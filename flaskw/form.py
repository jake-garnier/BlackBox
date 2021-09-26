import os
import datetime
from flaskw import db as db
from flaskw import aws as aws
from flask import flash, render_template, redirect, url_for

ALLOWED_EXTENSIONS = {'java', 'zip', 'py'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def show_contract_view(contract_id, request):
    if request.method == 'POST':
        uploaded_file = request.files['file']
        contract_files_dir = 'files/' + str(contract_id) + '_files'

        error = None

        if not uploaded_file:
            error = 'Attempt file is required'
        elif not allowed_file(uploaded_file.filename):
            error = 'Attempt file is not a Java file'
        elif uploaded_file.filename is '':
            error = 'Attempt file has no name'
        elif not os.path.isdir(contract_files_dir):
            error = '{Internal Error} Contract does not have file directory'

        if error is None:
            attempt_id = db.insert_attempt((contract_id, 'attempt_' + uploaded_file.filename))

            contract_path = contract_files_dir + '/' + str(attempt_id)

            os.makedirs(contract_files_dir + '/' + str(attempt_id))
            uploaded_file.save(contract_path + '/' + 'attempt_' + uploaded_file.filename)

            aws.create_lambda(contract_id, attempt_id, contract_files_dir)

            flash('Success!')

        else:
            flash(error)

    return render_template('contractView.html',
                           contract=db.get_contract(contract_id))


def create_contract_view(request):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        difficulty = request.form['difficulty']
        expiration_date = request.form['expiration_date']
        payout = request.form['payout']
        uploaded_file = request.files['file']

        error = None

        if not title:
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
                             payout, 'test_' + uploaded_file.filename)

            contract_id = db.insert_contract(contract_info)

            contract_files_folder = 'files/' + str(contract_id) + '_files'
            os.makedirs(contract_files_folder)

            if uploaded_file.filename != '':
                uploaded_file.save(contract_files_folder + '/' + 'test_' + uploaded_file.filename)

            return redirect(url_for('table'))

        flash(error)

    return render_template('form.html')
