import os
import flaskw.db as db
from flask import Flask, request, render_template, redirect, url_for, flash
import datetime

# export FLASK_APP=flaskw && export FLASK_ENV=development
# flask run

# Commands to run build and run server in docker
# docker build -t flask-container .
# docker run -p 5000:5000 flask-container

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

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

    @app.route('/form', methods=('GET', 'POST'))
    def form():
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            difficulty = request.form['difficulty']
            expiration_date = request.form['expiration_date']
            payout = request.form['payout']

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
            
            if error is None:
                box_info = (title, description, difficulty, datetime.datetime.now(), 
                            expiration_date, payout)

                db.insert_box_contract(box_info)

                return redirect(url_for('table'))
            
            flash(error)
        
        return render_template('form.html')

    @app.route('/table')
    def table():
        return render_template('basicTable.html', box_contracts=db.get_box_contracts())

    @app.route('/table/<int:id>')
    def view_contract(id):
        return render_template('contractView.html', box_contract=db.get_box_contract(id))

    @app.route('/addBoxContracts', methods = ['POST'])
    def add_box_contracts():
        body = request.get_json(force=True)
        box_contracts = body["box_contracts"]
        for box_contract in box_contracts:
            box_contract[3] = datetime.datetime.now()
            box_contract[4] = datetime.datetime.now()
            db.insert_box_contract(box_contract)

        return "inserted contracts"

    @app.route('/printBoxContracts')
    def print_box_contracts():
        return db.print_box_contract_table()

    @app.route('/test')
    def test():
        return str(db.get_box_contracts())

    db.init_app(app)

    # from . import auth
    # app.register_blueprint(auth.bp)

    # from . import blog
    # app.register_blueprint(blog.bp)
    # app.add_url_rule('/', endpoint='index')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv('LISTEN', '0.0.0.0'),
        port=int(os.getenv('PORT', '5000'))
    )