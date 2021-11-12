"""
File Name: sql.py
Description: Contains functions which manage the SQLite3 database
"""

import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
import shutil
import os
from flask_mysqldb import MySQL
from flaskw import __init__ as init

# sudo mysql.server start 
# sudo mysql.server stop
# mysql -u root -p  
# ps aux | grep mysql  
# sudo kill #

"""
Description: Flask command to initalize the database, and delete the cached files associated with the database.
"""
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    shutil.rmtree('files')
    os.makedirs('files')
    click.echo('Initialized the database.')


"""
Description: Initializes the flask application and sets the closed_db function as the handler for tearing down
the appcontext.
@arg (flask application) app: The flask application the handlers are being added to.
"""
def init_app(app):
    app.cli.add_command(init_db_command)


"""
Start of db manipulation functions
"""

"""
Description: Inserts a contract into the contracts table.
@arg contract_info: (title, _description, difficulty, creation_date,
                     expiration_date, payout, test_filename, payment_id, payer_id, _status).
@return (int): The row id of the inserted contract.
"""
def insert_contract(contract_info, db):
    cursor = db.connection.cursor()
    cursor.execute(
        'INSERT INTO contracts (title, description, difficulty, \
        creation_date, expiration_date, creater_user_id, payout, test_filename, \
        payment_id, payer_id, _status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
        contract_info
    )
    db.connection.commit()

    return cursor.lastrowid


"""
Description: Inserts an attempt into the attempts table.
@arg attempt_info: (contract_id, creater_user_id, attempt_filename, function_name, payment_email).
@return (int): The row id of the inserted attempt.
"""
def insert_attempt(attempt_info, db):
    cursor = db.connection.cursor()
    cursor.execute(
        'INSERT INTO attempts (contract_id, creater_user_id, attempt_filename, payment_email) \
        VALUES (%s, %s, %s, %s)',
        attempt_info
    )
    db.connection.commit()
    
    return cursor.lastrowid


"""
Description: Inserts a user into the user table.
@arg user_info: (username, password).
@return (int): The row id of the inserted user.
"""
def insert_user(user_info, db):
    cursor = db.connection.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        user_info,
    )
    db.connection.commit()

    return cursor.lastrowid

def update_contract_status(contract_id, status, db):
    cursor = db.connection.cursor()
    cursor.execute(
        'UPDATE contracts SET status = %s WHERE id = %s',
        (status, contract_id)
    )
    db.connection.commit()


"""
Description: Deletes a contract from the contracts table.
@arg (int) contract_id: The row id of the contract.
"""
def delete_contract(contract_id, db):
    cursor = db.connection.cursor()
    cursor.execute(
        "DELETE FROM contracts WHERE id = %s",
        (contract_id, )
    )
    db.connection.commit()


"""
Description: Deletes an attempt from the attempts table.
@arg (int) attempt_id: The row id of the attempt.
"""
def delete_attempt(attempt_id, db):
    cursor = db.connection.cursor()
    cursor.execute(
        "DELETE FROM attempts WHERE id = %s",
        (attempt_id, )
    )
    db.connection.commit()


"""
Description: Deletes a user from the users table.
@arg (int) user_id: The row id of the user.
"""
def delete_user(user_id, db):
    cursor = db.connection.cursor()
    cursor.execute(
        "DELETE FROM users WHERE id = %s",
        (user_id, )
    )
    db.connection.commit()


"""
Description: Adds the results of the attempt to the attempt row.
@arg (int) attempt_id: The id of the attempt.
@arg (str) failed_tests: The method names of the failed tests.
@arg (bool) success: True if the attempt was successful
"""
def add_result_to_attempt(attempt_id, failed_tests, success, db):
    cursor = db.connection.cursor()
    cursor.execute(
        'UPDATE attempts SET ran = 1 WHERE id = %s',
        (attempt_id, )
    )
    cursor.execute(
        'UPDATE attempts SET failed_tests = %s WHERE id = %s',
        (failed_tests, attempt_id)
    )
    cursor.execute(
        'UPDATE attempts SET success = %s WHERE id = %s',
        (success, attempt_id)
    )
    db.connection.commit()


"""
Description: Adds the names of the s3 bucket and lambda function to the contract row.
@arg (int) contract_id: The id of the contract.
@arg (dict) aws_contract_info: dict with the s3 name under 's3' and lambda name under 'lambda'
"""
def add_aws_contract_info(contract_id, aws_contract_info, db):
    cursor = db.connection.cursor()
    cursor.execute(
        'UPDATE contracts SET s3_bucket_name = %s WHERE id = %s',
        (aws_contract_info['s3'], contract_id)
    )
    cursor.execute(
        'UPDATE contracts SET lambda_name = %s WHERE id = %s',
        (aws_contract_info['lambda'], contract_id)
    )
    db.connection.commit()


"""
Description: Gets a dictionary of the row's columns;
@arg contract_id: The row id of the contract.
@return (dict): The row's fields in dictionary form.
"""
def get_contract(contract_id, db):
    cursor = db.connection.cursor()
    cursor.execute(
        'SELECT * from contracts WHERE id = %s', (contract_id, )
    )
    row = cursor.fetchone()

    if not row:
        return None

    return parse_row(cursor.description, row)


"""
Description: Gets a dictionary of the row's columns
@arg attempt_id: The row id of the attempt.
@return (dict): The row's fields in dictionary form.
"""
def get_attempt(attempt_id, db):
    cursor = db.connection.cursor()
    cursor.execute(
        'SELECT * from attempts WHERE id = %s', (attempt_id, )
    )
    row = cursor.fetchone()

    if not row:
        return None

    return parse_row(cursor.description, row)


"""
Description: Gets a dictionary of the row's columns
@arg username: The user's username.
@return (dict): The row's fields in dictionary form.
"""
def get_user(username, db):
    cursor = db.connection.cursor()
    cursor.execute(
        'SELECT * FROM users WHERE username = %s', (username,)
    )
    row = cursor.fetchone()

    if not row:
        return None

    return parse_row(cursor.description, row)


"""
Description: Gets a list of dictionaries of all the contracts in the contract table.
@return (list(dict)): The information about all the contracts in the contract table.
"""
def get_contracts(db):
    cursor = db.connection.cursor()
    cursor.execute('SELECT * FROM contracts')
    rows = cursor.fetchall()
    
    ret = list()
    for row in rows:
        ret.append(parse_row(cursor.description, row))

    return ret


"""
Description: Gets a list of dictionaries of all the attempts for a cetain contract.
@arg (int) contract_id: The row id of the contract.
@return (list(dict)): The information about all the attempts for a cetain contract.
"""
def get_contract_attempts(contract_id, db):
    cursor = db.connection.cursor()
    cursor.execute(
        'SELECT * FROM attempts WHERE contract_id = %s',
        (contract_id, )
    )
    rows = cursor.fetchall()

    ret = list()
    for row in rows:
        ret.append(parse_row(cursor.description, row))
    
    return ret

def get_user_balance(user_id, db):
    cursor = db.connection.cursor()
    cursor.execute(
        'SELECT SUM(amount) FROM transactions WHERE receiver_user_id = %s',
        (user_id, )
    )
    received = cursor.fetchone()[0]

    cursor.execute(
        'SELECT SUM(amount) FROM transactions WHERE sender_user_id = %s',
        (user_id, )
    )
    sent = cursor.fetchone()[0]

    return received - sent

"""
Description: Converts the row in a table to a dictionary representation.
@arg (list) description: The cursor.description when pointing at the said row.
@arg (SQL Row) row: The row being converted.
@return (dict): The row converted to a dictionary representation.
"""
def parse_row(description, row):
    ret_dict = dict()
    for column, value in zip(description, row):
        ret_dict[column[0]] = value
    return ret_dict