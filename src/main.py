from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb as mysqlDB
import os
from urllib.parse import urlencode
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/account")
def account():
    return render_template('account.html')


@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        cursor = mysql.connection.cursor(mysqlDB.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE email = % s', (email))
        users = cursor.fetchall()
        for user in users:
            if not check_password_hash(user['password'], request.form.get('password')):
                continue
            else:
                session['loggedin'] = True
                session['id'] = user['user_id']
                return redirect(url_for('index'))

    return render_template('login.html')




@app.route("/steam_auth")
def auth_with_steam():
    '''os.environ['openid.ns'] = 'http://specs.openid.net/auth/2.0'
    os.environ['openid.identity'] = 'http://specs.openid.net/auth/2.0/identifier_select'
    os.environ['openid.mode'] = 'checkid_setup'
    os.environ['openid.claimed_id'] = 'http://specs.openid.net/auth/2.0/identifier_select'
    os.environ['openid.return_to'] = 'http://127.0.0.1:5000/steam_authorized'
    os.environ['openid.realm'] = 'http://127.0.0.1:5000'''
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.mode': 'checkid_setup',
        'openid.return_to': 'http://cosmos-alb-1623670014.us-east-1.elb.amazonaws.com/steam_authorized',
        'openid.realm': 'http://cosmos-alb-1623670014.us-east-1.elb.amazonaws.com/'
    }
    query_string = urlencode(params)
    steam_openid_url = 'https://steamcommunity.com/openid/login'
    auth_url = steam_openid_url + "?" + query_string
    return redirect(auth_url)

@app.route("/steam_authorized")
def steam_authorize():
    steam_id = {
        'steam_id': request.args.get('openid.claimed_id').split('/')[-1]
    }
    return steam_id 

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')