"""
File Name: db.py
Description: Contains functions which manage the SQLite3 database
"""

import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
import shutil
import os

# sudo mysql.server start 
# sudo mysql.server stop
# mysql -u root -p  
# ps aux | grep mysql  
# sudo kill #

"""
Description: Gets the SQLite3 database, initializing it if it doesn't exist.
@return (SQLite3 Connection) The database connection object.
"""
def get_db():
    if 'db' not in g:
        # g.db = sqlite3.connect(
        #     current_app.config['DATABASE'],
        #     detect_types=sqlite3.PARSE_DECLTYPES
        # )
        # g.db.row_factory = sqlite3.Row
        g.db = current_app.config['DATABASE'].get_db()

    return g.db


"""
Description: Closes the SQLite3 database connection.
"""
def close_db(self):
    db = g.pop('db', None)

    if db is not None:
        db.close()


"""
Description: Initializes the database connection if it doesn't already exist, and creates the tables in the schema.
"""
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.cursor().execute(f.read().decode('utf8'))


"""
Description: Flask command to initalize the database, and delete the cached files associated with the database.
"""
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    shutil.rmtree('files')
    os.makedirs('files')
    click.echo('Initialized the database.')


"""
Description: Initializes the flask application and sets the closed_db function as the handler for tearing down
the appcontext.
@arg (flask application) app: The flask application the handlers are being added to.
"""
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


"""
Start of db manipulation functions
"""

"""
Description: Inserts a contract into the contracts table.
@arg contract_info: (title, description, difficulty, creation_date,
                     expiration_date, payout, test_filename, payment_id, payer_id).
@return (int): The row id of the inserted contract.
"""
def insert_contract(contract_info):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO contracts (title, description, difficulty, \
        creation_date, expiration_date, creater_user_id, payout, test_filename, \
        payment_id, payer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        contract_info
    )
    db.commit()

    return cursor.lastrowid


"""
Description: Inserts an attempt into the attempts table.
@arg attempt_info: (contract_id, creater_user_id, attempt_filename, function_name, payment_email).
@return (int): The row id of the inserted attempt.
"""
def insert_attempt(attempt_info):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO attempts (contract_id, creater_user_id, attempt_filename, function_name, payment_email) \
        VALUES (?, ?, ?, ?, ?)',
        attempt_info
    )
    db.commit()
    
    return cursor.lastrowid


"""
Description: Inserts a user into the user table.
@arg user_info: (username, password).
@return (int): The row id of the inserted user.
"""
def insert_user(user_info):
    db = get_db()
    cursor = db.cursor()
    db.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        user_info,
    )
    db.commit()

    return cursor.lastrowid


"""
Description: Deletes a contract from the contracts table.
@arg (int) contract_id: The row id of the contract.
"""
def delete_contract(contract_id):
    db = get_db()
    db.execute(
        "DELETE FROM contracts WHERE id = ?",
        (contract_id, )
    )
    db.commit()


"""
Description: Deletes an attempt from the attempts table.
@arg (int) attempt_id: The row id of the attempt.
"""
def delete_attempt(attempt_id):
    db = get_db()
    db.execute(
        "DELETE FROM attempts WHERE id = ?",
        (attempt_id, )
    )
    db.commit()


"""
Description: Deletes a user from the users table.
@arg (int) user_id: The row id of the user.
"""
def delete_user(user_id):
    db = get_db()
    db.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id, )
    )
    db.commit()


"""
Description: Adds the results of the attempt to the attempt row.
@arg (int) attempt_id: The id of the attempt.
@arg (str) failed_tests: The method names of the failed tests.
@arg (bool) success: True if the attempt was successful
"""
def add_result_to_attempt(attempt_id, failed_tests, success):
    db = get_db()
    db.execute(
        'UPDATE attempts SET ran = 1 WHERE id = ?',
        (attempt_id, )
    )
    db.execute(
        'UPDATE attempts SET failed_tests = ? WHERE id = ?',
        (failed_tests, attempt_id)
    )
    db.execute(
        'UPDATE attempt SET success = ? WHERE id = ?',
        (success, attempt_id)
    )
    db.commit()


"""
Description: Gets a dictionary of the row's columns;
@arg contract_id: The row id of the contract.
@return (dict): The row's fields in dictionary form.
"""
def get_contract(contract_id):
    db = get_db()
    cursor = db.cursor()
    row = cursor.execute(
        'SELECT * from contracts WHERE id = ?', (contract_id, )
    ).fetchone()

    if not row:
        return None

    return parse_row(cursor.description, row)


"""
Description: Gets a dictionary of the row's columns
@arg attempt_id: The row id of the attempt.
@return (dict): The row's fields in dictionary form.
"""
def get_attempt(attempt_id):
    db = get_db()
    cursor = db.cursor()
    row = cursor.execute(
        'SELECT * from attempts WHERE id = ?', (attempt_id, )
    ).fetchone()

    if not row:
        return None

    return parse_row(cursor.description, row)


"""
Description: Gets a dictionary of the row's columns
@arg username: The user's username.
@return (dict): The row's fields in dictionary form.
"""
def get_user(username):
    db = get_db()
    cursor = db.cursor()
    row = cursor.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()

    if not row:
        return None

    return parse_row(cursor.description, row)


"""
Description: Gets a list of dictionaries of all the contracts in the contract table.
@return (list(dict)): The information about all the contracts in the contract table.
"""
def get_contracts():
    db = get_db()
    cursor = db.cursor()
    rows = cursor.execute('SELECT * FROM contracts').fetchall()
    
    ret = list()
    for row in rows:
        ret.append(parse_row(cursor.description, row))

    return ret


"""
Description: Gets a list of dictionaries of all the attempts for a cetain contract.
@arg (int) contract_id: The row id of the contract.
@return (list(dict)): The information about all the attempts for a cetain contract.
"""
def get_contract_attempts(contract_id):
    db = get_db()
    cursor = db.cursor()
    rows = cursor.execute(
        'SELECT * FROM attempts WHERE contract_id = ?',
        (contract_id, )
    )

    ret = list()
    for row in rows:
        ret.append(parse_row(cursor.description, row))
    
    return ret

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