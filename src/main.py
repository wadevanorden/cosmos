from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb as mysqlDB
import uuid
import requests
import os
from urllib.parse import urlencode
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL(app)

@app.route("/")
def index():
    loggedin = session.get('loggedin')
    apps_processed = list()
    if loggedin:
        user_id = session.get('id')
        cursor = mysql.connection.cursor(mysqlDB.cursors.DictCursor)
        cursor.execute('SELECT * FROM User_Apps WHERE user_id = %s', [user_id])
        apps = cursor.fetchall()
        for app in apps:
            cursor.execute('SELECT * FROM App_Data WHERE app_id = %s', [app['app_id']])
            app_data = cursor.fetchone()
            if app_data:
                apps_processed.append(app_data)
    return render_template('index.html', authenticated=loggedin, apps=apps_processed)


@app.route("/account")
def account():
    return render_template('account.html', authenticated=session.get('loggedin'))


@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html', authenticated=session.get('loggedin'))
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
        return render_template('login.html', authenticated=session.get('loggedin'))


@app.route("/signup", methods = ['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html', authenticated=session.get('loggedin'))
    if request.method == 'POST':
        email = request.form['email']
        cursor = mysql.connection.cursor(mysqlDB.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE email = %s', [email])
        user = cursor.fetchone()
        if user:
            error_msg = "User exists with that email"
            return render_template('signup.html', authenticated=session.get('loggedin'))
        else:
            user_id = uuid.uuid4().hex
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


@app.route('/app/<app_id>')
def app_route(app_id):
    cursor = mysql.connection.cursor(mysqlDB.cursors.DictCursor)
    cursor.execute('SELECT * FROM App_Achievement_Data WHERE app_id = %s', [app_id])
    app_achievement_data = cursor.fetchall()
    achievement_data = list()
    if app_achievement_data:
        for app in app_achievement_data:
            achievement_data.append({
                'app_id': app['app_id'],
                'achievement_id': app['achievement_id'],
                'achievement_title': app['achievement_title'],
                'achievement_description': app['achievement_description'],
                'art': app['$ref_art'],
                'hidden': app['hidden'],
                'cosmos_percent': app['cosmos_percent'],
                'source_percent': app['source_percent'],
            })
    else:
        cursor.execute('SELECT * FROM App_Data WHERE app_id = %s', [app_id])
        mapping = cursor.fetchone()
        source_id = ''
        if mapping:
            source_id = mapping['source_id']
        else:
            return 'Error'
        api_key = os.getenv('STEAM_API_KEY')
        url = f'https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={source_id}'
        url_2 = f'http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={source_id}&format=json'
        response = requests.get(url).json()
        response_2 = requests.get(url_2).json()['achievementpercentages']['achievements']
        for achievement in response['game']['availableGameStats']['achievements']:
            achivement_id = uuid.uuid4().hex
            achievement_title = achievement.get('displayName')
            achievement_description = achievement.get('description')
            art = achievement.get('icon')
            hidden = False
            if achievement.get('hidden') == 1:
                hidden = True
            cosmos_percent = 0.0
            source_percent = 0.0
            for achievement_percent in response_2:
                if achievement_percent['name'] == achievement['name']:
                    source_percent = achievement_percent['percent']
            cursor.execute('INSERT INTO App_Achievement_Data (app_id,achievement_id,achievement_title,achievement_description,$ref_art,hidden,cosmos_percent,source_percent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
                           (app_id, achivement_id, achievement_title, achievement_description, art, hidden, cosmos_percent, source_percent))
            mysql.connection.commit()
            achievement_data.append({
                'app_id': app_id,
                'achievement_id': achivement_id,
                'achievement_title': achievement_title,
                'achievement_description': achievement_description,
                'art': art,
                'hidden': hidden,
                'cosmos_percent': cosmos_percent,
                'source_percent': source_percent,
            })
    return render_template('app.html', authenticated=session.get('loggedin'), app_achievement_data=achievement_data)


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
    url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&include_appinfo=1&include_played_free_games=1&format=json'
    try:
        response = requests.get(url).json()
        if len(response['response']['games']) == 0:
            redirect(url_for('account'))
        else:
            input_apps = list()
            for app in response['response']['games']:
                cursor.execute('SELECT * FROM Connections_Mapping WHERE appid = %s', [app['appid']])
                connection_mapping = cursor.fetchone()
                app_details = dict()
                img_hash = str(app.get('img_icon_url'))
                name = str(app.get('name'))
                if connection_mapping:
                    input_apps.append(connection_mapping['app_id'])
                    app_details = {
                        "app_id": connection_mapping['app_id'],
                        "app_title": name,
                        "$ref_art": f"https://steamcdn-a.akamaihd.net/steam/apps/{app['appid']}/library_600x900_2x.jpg",
                        "$ref_art_alt": f"https://media.steampowered.com/steamcommunity/public/images/apps/{app['appid']}/{img_hash}.jpg",
                        "source_system": "Steam",
                        "source_id": app['appid']
                    }
                else:
                    new_app_id = uuid.uuid4().hex
                    cursor.execute('INSERT INTO Connections_Mapping (app_id,appid) VALUES (%s, %s)', (new_app_id, app['appid']))
                    mysql.connection.commit()
                    input_apps.append(new_app_id)
                    app_details = {
                        "app_id": new_app_id,
                        "app_title": name,
                        "$ref_art": f"https://steamcdn-a.akamaihd.net/steam/apps/{app['appid']}/library_600x900_2x.jpg",
                        "$ref_art_alt": f"https://media.steampowered.com/steamcommunity/public/images/apps/{app['appid']}/{img_hash}.jpg",
                        "source_system": "Steam",
                        "source_id": app['appid']
                    }
                cursor.execute('SELECT * FROM App_Data WHERE app_id = %s', [app_details['app_id']])
                app_data = cursor.fetchone()
                if app_data:
                    continue
                else:
                    cursor.execute('INSERT INTO App_Data (app_id,app_title,$ref_art,$ref_art_alt,source_system,source_id) VALUES (%s, %s, %s, %s, %s, %s)', 
                           (app_details['app_id'], app_details['app_title'], app_details['$ref_art'], app_details['$ref_art_alt'], app_details['source_system'], app_details['source_id']))
                    mysql.connection.commit()
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