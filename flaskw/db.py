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
Inserts an contract into the contracts table
@arg contract_info: (title, descript, difficulty,
                     creation_date, expiration_date, payout, test_filename)
"""
def insert_contract(contract_info):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO contracts (title, descript, difficulty, \
        creation_date, expiration_date, creater_user_id, payout, test_filename) \
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        contract_info
    )
    db.commit()

    return cursor.lastrowid

"""
Inserts an attempt into the attempts table
@arg attempt_info: (contract_id, creater_user_id, attempt_filename)
"""
def insert_attempt(attempt_info):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO attempts (contract_id, creater_user_id, attempt_filename) VALUES (?, ?, ?)',
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
        'UPDATE attempts SET success = ? WHERE id = ?',
        (success, attempt_id)
    )
    db.commit()

def get_contract(id):
    db = get_db()
    return db.execute(
        'SELECT * from contracts WHERE id = ?', (id, )
    ).fetchone()

def get_attempt(id):
    db = get_db()
    return db.execute(
        'SELECT * from attempts WHERE id = ?', (id, )
    ).fetchone()

def get_user(username):
    db = get_db()
    return db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

def print_contract_table():
    db = get_db()
    contracts = db.execute('SELECT * FROM contracts').fetchall()

    ret = list()
    for contract in contracts:
        ret.append((list(contract)[0], list(contract)[1]))

    return str(ret)

def get_contracts():
    db = get_db()
    contracts = db.execute('SELECT * FROM contracts').fetchall()
    
    ret = list()
    for contract in contracts:
        ret.append(list(contract))

    return ret
    
def get_contracts_attempts(contract_id):
    db = get_db()
    attempts = db.execute(
        'SELECT * FROM attempts WHERE contract_id = ?',
        (contract_id, )
    )

    ret = list()
    for attempt in attempts:
        ret.append(list(attempt))
    
    return ret