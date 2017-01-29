# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import re

app = Flask(__name__) # create the application instance
app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable.

# Because you can have multiple applications running in the same process you need to specify the path of the application
# You should use app.root_path, thanks to this, the program can easily find the path.

# For real world applications you should consider to use "Instance Folders".
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'database'),
    SECRET_KEY='development key', # Keep the client-side sessions secure.
    USERNAME='admin',
    PASSWORD='default'
    ))

# You can import multiple configurations for an specific environment.
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# Connects to the specific database.
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

"""
It's very inefficient to create and close a connection at a time, so you better use application context;
only one request at a time uses the connection.
"""
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

"""
The app context is created before the request comes in and is destroyed (torn down) whenever the request finishes.
"""
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


"""
You can use the command "sqlite3 /tmp/flaskr.db < schema.sql" to init the database, but this is not handy.
"""
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

# Flask comes with click, you can run command line code. Inits the database
@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select * from agenda')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    name = request.form['name'];
    last_name = request.form['last_name'];
    address = request.form['address'];
    email = request.form['email'];
    phone_number = request.form['phone_number'];
    phone_type = request.form['phone_type'];

    if (re.search("^[a-zA-Z\-'\s]+$", name) and re.search("^[a-zA-Z\-'\s]+$", last_name) and re.search(
            "^([a-zA-Z\-'\s]|\.|\#|[0-9]|\-)+$", address) and re.search("^(\w|\.|\-)+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$", email)
        and re.search("^((52)?(-?\d{3})-?)?(\d{3})(-?\d{4})$",phone_number) and re.search("^(Work|Home|Other)$", phone_type)):
            db.execute('insert into agenda (name, last_name, address, email, phone_number, phone_type) values (?, ?, ?, ?, ?, ?)',
                    [name, last_name, address, email, phone_number, phone_type])
            db.commit()
            flash('New entry was successfully posted')
    else:
        flash('Request error')
    return redirect(url_for('show_entries'))

@app.route('/edit', methods=['POST'])
def edit_entry():

    name = request.form['name_edit'];
    last_name = request.form['last_name_edit'];
    address = request.form['address_edit'];
    email = request.form['email_edit'];
    phone_number = request.form['phone_number_edit'];
    phone_type = request.form['phone_type_edit'];

    if (re.search("^[a-zA-Z\-'\s]+$", name) and re.search("^[a-zA-Z\-'\s]+$", last_name) and re.search("^([a-zA-Z\-'\s]|\.|\#|[0-9]|\-)+$", address)
                 and re.search("^(\w|\.|\-)+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$", email) and re.search("^((52)?(-?\d{3})-?)?(\d{3})(-?\d{4})$", phone_number)
                 and re.search("^(Work|Home|Other)$", phone_type)):
        db = get_db()
        db.execute(
            'update agenda set name = (?), last_name = (?), address= (?), email= (?), phone_number= (?), phone_type = (?)'+
            ' where id = (?)',
            [name, last_name, address, email, phone_number, phone_type, request.form['id_user']])
        db.commit()
        flash('Entry was successfully updated')
    else:
        flash('Request error')
    return redirect(url_for('show_entries'))

@app.route('/delete', methods=['POST'])
def delete_entry():
    db = get_db()
    db.execute('delete from agenda where id = (?)', request.form['id_user'])
    db.commit()
    flash('Entry was successfully deleted')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
