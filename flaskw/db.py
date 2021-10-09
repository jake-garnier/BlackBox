import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import shutil
import os
from sqlite3 import IntegrityError


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    shutil.rmtree('files')
    os.makedirs('files')
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


"""
Start of db manipulation functions
"""

"""
Inserts an contract into the contract table
@arg contract_info: (title, description, difficulty, creation_date,
                     expiration_date, payout, test_filename, payment_id, payer_id)
"""
def insert_contract(contract_info):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO contract (title, description, difficulty, \
        creation_date, expiration_date, creater_user_id, payout, test_filename, \
        payment_id, payer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        contract_info
    )
    db.commit()

    return cursor.lastrowid

"""
Inserts an attempt into the attemptstable
@arg attempt_info: (contract_id, creater_user_id, attempt_filename, function_name)
"""
def insert_attempt(attempt_info):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO attempt (contract_id, creater_user_id, attempt_filename, function_name) VALUES (?, ?, ?, ?)',
        attempt_info
    )
    db.commit()
    
    return cursor.lastrowid

def insert_user(user_info):
    db = get_db()
    cursor = db.cursor()
    db.execute(
        "INSERT INTO user (username, password) VALUES (?, ?)",
        user_info,
    )
    db.commit()

    return cursor.lastrowid

def delete_contract(contract_id):
    db = get_db()
    db.execute(
        "DELETE FROM contract WHERE id = ?",
        (contract_id, )
    )
    db.commit()

def delete_attempt(attempt_id):
    db = get_db()
    db.execute(
        "DELETE FROM attempt WHERE id = ?",
        (attempt_id, )
    )
    db.commit()

def add_payment_id_to_contract(contract_id, payment_id):
    db = get_db()
    db.execute(
        'UPDATE contract SET payment_id = ? WHERE id = ?',
        (payment_id, contract_id)
    )
    db.commit()

def add_result_to_attempt(attempt_id, failed_tests, success):
    db = get_db()
    db.execute(
        'UPDATE attempt SET ran = 1 WHERE id = ?',
        (attempt_id, )
    )
    db.execute(
        'UPDATE attempt SET failed_tests = ? WHERE id = ?',
        (failed_tests, attempt_id)
    )
    db.execute(
        'UPDATE attempt SET success = ? WHERE id = ?',
        (success, attempt_id)
    )
    db.commit()

def get_contract(id):
    db = get_db()
    cursor = db.cursor()
    row = cursor.execute(
        'SELECT * from contract WHERE id = ?', (id, )
    ).fetchone()

    if not row:
        return []

    return parse_row(cursor.description, row)

def get_attempt(id):
    db = get_db()
    cursor = db.cursor()
    row = cursor.execute(
        'SELECT * from attempt WHERE id = ?', (id, )
    ).fetchone()

    if not row:
        return []

    return parse_row(cursor.description, row)

def get_user(username):
    db = get_db()
    cursor = db.cursor()
    row = cursor.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if not row:
        return []

    return parse_row(cursor.description, row)

def print_contract_table():
    db = get_db()
    contracts = db.execute('SELECT * FROM contract').fetchall()

    ret = list()
    for contract in contracts:
        ret.append((list(contract)[0], list(contract)[1]))

    return str(ret)

def get_contracts():
    db = get_db()
    cursor = db.cursor()
    rows = cursor.execute('SELECT * FROM contract').fetchall()
    
    ret = list()
    for row in rows:
        ret.append(parse_row(cursor.description, row))

    return ret
    
def get_contract_attempts(contract_id):
    db = get_db()
    cursor = db.cursor()
    rows = cursor.execute(
        'SELECT * FROM attempt WHERE contract_id = ?',
        (contract_id, )
    )

    ret = list()
    for row in rows:
        ret.append(parse_row(cursor.description, row))
    
    return ret

def parse_row(description, row):
    ret_dict = dict()
    for column, value in zip(description, row):
        ret_dict[column[0]] = value
    return ret_dict