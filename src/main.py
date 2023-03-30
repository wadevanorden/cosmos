from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb as mysqlDB
import random
import requests
import os
from urllib.parse import urlencode
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL(app)

@app.route("/")
def index():
    try:
        loggedin = session['loggedin']
    except:
        loggedin = False
    return render_template('index.html', authenticated=loggedin)


@app.route("/account")
def account():
    return render_template('account.html', authenticated=session['loggedin'])


@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html', authenticated=session['loggedin'])
    if request.method == 'POST':
        email = request.form.get('email')
        cursor = mysql.connection.cursor(mysqlDB.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
        users = cursor.fetchall()
        for user in users:
            if not check_password_hash(user['password'], request.form.get('password')):
                continue
            else:
                session['loggedin'] = True
                session['id'] = user['user_id']
                return redirect(url_for('index'))
        return render_template('login.html', authenticated=session['loggedin'])


@app.route("/signup", methods = ['POST', 'GET'])
def signup():
    error_msg = ""
    if request.method == 'GET':
        return render_template('signup.html', authenticated=session['loggedin'])
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor(mysqlDB.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
        user = cursor.fetchone()
        if user:
            error_msg = "User exists with that email"
            return render_template('signup.html', authenticated=session['loggedin'])
        else:
            user_id = random.getrandbits(64)
            username = request.form['username']
            first_name = request.form['first-name']
            last_name = request.form['last-name']
            enabled = True
            password = generate_password_hash(request.form['password'])
            cursor.execute('INSERT INTO Users (user_id,first_name,last_name,email,username,password,enabled) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                           (user_id, first_name, last_name, email, username, password, enabled))
            mysql.connection.commit()
            return redirect(url_for('login'))


@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   return redirect(url_for('login'))


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
        'openid.return_to': 'https://cosmos-achievement.com/steam_authorized',
        'openid.realm': 'https://cosmos-achievement.com'
    }
    query_string = urlencode(params)
    steam_openid_url = 'https://steamcommunity.com/openid/login'
    auth_url = steam_openid_url + "?" + query_string
    return redirect(auth_url)

@app.route("/steam_authorized")
def steam_authorize():
    try:
        steam_id = request.args.get('openid.claimed_id').split('/')[-1]
    except:
        redirect(url_for('account'))
    cursor = mysql.connection.cursor(mysqlDB.cursors.DictCursor)
    cursor.execute('SELECT * FROM Connections WHERE user_id = %s', [session['id']])
    connection_entry = cursor.fetchone()
    if connection_entry:
        cursor.execute('UPDATE Connections SET steam_id = %s WHERE user_id = %s', (steam_id, session['id']))
        mysql.connection.commit()
    else:
        cursor.execute('INSERT INTO Connections (user_id,steam_id) VALUES (%s, %s)', 
                           (session['id'], steam_id))
        mysql.connection.commit()
    
    api_key = os.getenv('STEAM_API_KEY')
    url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&format=json'
    try:
        response = requests.get(url).json()
        if len(response['response']['games']) == 0:
            redirect(url_for('account'))
        else:
            input_apps = list()
            for app in response['response']['games']:
                cursor.execute('SELECT * FROM Connections_Mapping WHERE appid = %s', [app['appid']])
                connection_mapping = cursor.fetchone()
                if connection_mapping:
                    print('1')
                    input_apps.append(connection_mapping['app_id'])
                else:
                    print('2')
                    new_app_id = random.getrandbits(64)
                    cursor.execute('INSERT INTO Connections_Mapping (app_id,appid) VALUES (%s, %s)', 
                           (new_app_id, app['appid']))
                    mysql.connection.commit()
                    print('3')
                    input_apps.append(new_app_id)
                    print(input_apps)
            for app_id in input_apps:
                cursor.execute('SELECT * FROM User_Apps WHERE app_id = %s', [app_id])
                user_app = cursor.fetchone()
                if user_app:
                    continue
                else:
                    cursor.execute('INSERT INTO User_Apps (user_id,app_id) VALUES (%s, %s)', 
                           (session['id'], app_id))
                    mysql.connection.commit()
            redirect(url_for('account'))
    except:
        redirect(url_for('index'))
    

    return redirect(url_for('account'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')