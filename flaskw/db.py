import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

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
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


"""
Start of db manipulation functions
"""

"""
Inserts an box contract into the box contract table
@arg box_info: (title, descript, difficulty, creation_date, expiration_date, payout)
"""
def insert_box_contract(box_info):
    db = get_db()
    if db.execute(
        'SELECT id FROM box_contract WHERE title = ?', (box_info[0], )
    ).fetchone() is None:
        db.execute(
            'INSERT INTO box_contract (title, descript, difficulty, \
            creation_date, expiration_date, payout) VALUES (?, ?, ?, ?, ?, ?)',
            box_info
        )
        db.commit()

    return list(db.execute(
        'SELECT id FROM box_contract WHERE title = ?', (box_info[0], )
    ).fetchone())[0]
    

def get_box_contract(id):
    db = get_db()
    return db.execute(
        'SELECT * from box_contract WHERE id = ?', (id, )
    ).fetchone()

def print_box_contract_table():
    db = get_db()
    box_contracts = db.execute('SELECT * FROM box_contract').fetchall()

    ret = list()
    for box_contract in box_contracts:
        ret.append((list(box_contract)[0], list(box_contract)[1]))

    return str(ret)

def get_box_contracts():
    db = get_db()
    box_contracts = db.execute('SELECT * FROM box_contract').fetchall()
    
    ret = list()
    for box_contract in box_contracts:
        ret.append(list(box_contract))

    return ret