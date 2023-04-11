from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb as mysqlDB
import uuid
import requests
import os
from urllib.parse import urlencode
from werkzeug.security import generate_password_hash, check_password_hash
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.config.from_pyfile('config.py')

mysql = MySQL(app)


@app.route("/")
def index():
    loggedin = session.get('loggedin')
    apps_processed = list()
    if not loggedin:
        return redirect(url_for('login'))
    else:
        user_id = session.get('id')
        cursor = mysql.connection.cursor(mysqlDB.cursors.DictCursor)
        cursor.execute('SELECT * FROM User_Apps WHERE user_id = %s', [user_id])
        apps = cursor.fetchall()
        for app in apps:
            cursor.execute(
                'SELECT * FROM App_Data WHERE app_id = %s', [app['app_id']])
            app_data = cursor.fetchone()
            if app_data:
                apps_processed.append(app_data)
    return render_template('index.html', authenticated=loggedin, apps=apps_processed)


@app.route("/account")
def account():
    return render_template('account.html', authenticated=session.get('loggedin'))


@app.route("/login", methods=['POST', 'GET'])
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


@app.route("/signup", methods=['POST', 'GET'])
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
    cursor.execute(
        'SELECT * FROM App_Achievement_Data WHERE app_id = %s', [app_id])
    app_achievement_data = cursor.fetchall()
    cursor.execute('SELECT * FROM App_Data WHERE app_id = %s', [app_id])
    app_data = cursor.fetchone()

    achievement_data = list()
    if app_achievement_data:
        for app_achievement in app_achievement_data:
            achievement_data.append({
                'app_id': app_achievement['app_id'],
                'achievement_id': app_achievement['achievement_id'],
                'achievement_title': app_achievement['achievement_title'],
                'achievement_description': app_achievement['achievement_description'],
                'art': app_achievement['$ref_art'],
                'hidden': app_achievement['hidden'],
                'cosmos_percent': app_achievement['cosmos_percent'],
                'source_percent': app_achievement['source_percent'],
                'source_system': app_data['source_system'],
            })
    else:
        loggedin = session.get('loggedin')
        if loggedin:
            user_id = session.get('id')
            cursor.execute(
                'SELECT * FROM Connections WHERE user_id = %s', [user_id])
            user_connections = cursor.fetchone()
            user_achievement_details = dict()
            if user_connections:
                try:
                    source_id = app_data['source_id']
                    steam_id = user_connections['steam_id']
                    user_achievement_data_url = f'https://steamcommunity.com/profiles/{steam_id}/stats/{source_id}/achievements/?xml=1'
                    user_game_achievements = requests.get(
                        user_achievement_data_url)
                    tree = ET.fromstring(user_game_achievements.content)
                    achievement_details = dict()
                    for item in tree.findall('./achievements/achievement'):
                        for child in item:
                            if child.tag == 'description':
                                achievement_description = child.text
                            if child.tag == 'iconClosed':
                                art = child.text
                            if child.tag == 'name':
                                name = child.text
                        user_achievement_details[name] = {
                            "achievement_description": achievement_description,
                            "art": art
                        }
                except Exception as e:
                    print(e)
        cursor.execute(
            'SELECT * FROM App_Data WHERE app_id = %s', [app_id])
        app_Data = cursor.fetchone()
        source_id = ''
        if app_Data:
            source_id = app_Data['source_id']
        else:
            return 'App Not Found'
        api_key = os.getenv('STEAM_API_KEY')
        game_schema_url = f'https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={source_id}'
        achievement_percentages_url = f'http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={source_id}&format=json'
        game_schema = requests.get(game_schema_url).json()
        try:
            achievement_percentages = requests.get(achievement_percentages_url).json()[
                'achievementpercentages']['achievements']
            for achievement in game_schema['game']['availableGameStats']['achievements']:
                achievement_id = uuid.uuid4().hex
                achievement_title = achievement.get('displayName')
                achievement_description = achievement.get('description')
                if not achievement_description:
                    achievement_description = user_achievement_details[
                        achievement_title]['achievement_description']
                art = achievement.get('icon')
                if not art:
                    art = user_achievement_details[achievement_title]['art']
                hidden = False
                if achievement.get('hidden') == 1:
                    hidden = True
                cosmos_percent = 0.0
                source_percent = 0.0
                for achievement_percent in achievement_percentages:
                    if achievement_percent['name'] == achievement['name']:
                        source_percent = achievement_percent['percent']
                cursor.execute('INSERT INTO App_Achievement_Data (app_id,achievement_id,achievement_title,achievement_description,$ref_art,hidden,cosmos_percent,source_percent) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                               (app_id, achievement_id, achievement_title, achievement_description, art, hidden, cosmos_percent, source_percent))
                mysql.connection.commit()
                achievement_data.append({
                    'app_id': app_id,
                    'achievement_id': achievement_id,
                    'achievement_title': achievement_title,
                    'achievement_description': achievement_description,
                    'art': art,
                    'hidden': hidden,
                    'cosmos_percent': cosmos_percent,
                    'source_percent': source_percent,
                    'source_system': 'Steam',
                })
        except Exception as e:
            print(e)
    min_percent = -1
    hardest_achievement = {
        'app_id': None,
        'achievement_id': None,
        'achievement_title': None,
        'achievement_description': None,
        'art': None,
        'hidden': None,
        'cosmos_percent': 0,
        'source_percent': 0,
        'source_system': None,
    }
    achievement_percent_total = 0
    achievement_hidden_total = 0
    for achievement in achievement_data:
        achievement_percent_total += achievement['source_percent']
        if achievement['hidden']:
            achievement_hidden_total += 1
        if min_percent == -1:
            min_percent = achievement['source_percent']
            hardest_achievement = achievement
        elif achievement['source_percent'] < min_percent:
            min_percent = achievement['source_percent']
            hardest_achievement = achievement
    if len(achievement_data) > 0:
        achievement_percent_total = achievement_percent_total / \
            len(achievement_data)
    else:
        achievement_percent_total = 0
    app_overview_details = {
        'average_achivement_percent': achievement_percent_total,
        'hidden_total': achievement_hidden_total,
    }

    return render_template('app.html', authenticated=session.get('loggedin'), app_data=app_data, app_achievement_data=achievement_data, hardest_achievement=hardest_achievement, app_overview_details=app_overview_details)


@app.route("/steam_auth")
def auth_with_steam():
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
    cursor.execute(
        'SELECT * FROM Connections WHERE user_id = %s', [session['id']])
    connection_entry = cursor.fetchone()
    if connection_entry:
        cursor.execute(
            'UPDATE Connections SET steam_id = %s WHERE user_id = %s', (steam_id, session['id']))
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
                cursor.execute(
                    'SELECT * FROM Connections_Mapping WHERE appid = %s', [app['appid']])
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
                    cursor.execute(
                        'INSERT INTO Connections_Mapping (app_id,appid) VALUES (%s, %s)', (new_app_id, app['appid']))
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
                cursor.execute(
                    'SELECT * FROM App_Data WHERE app_id = %s', [app_details['app_id']])
                app_data = cursor.fetchone()
                if app_data:
                    continue
                else:
                    cursor.execute('INSERT INTO App_Data (app_id,app_title,$ref_art,$ref_art_alt,source_system,source_id) VALUES (%s, %s, %s, %s, %s, %s)',
                                   (app_details['app_id'], app_details['app_title'], app_details['$ref_art'], app_details['$ref_art_alt'], app_details['source_system'], app_details['source_id']))
                    mysql.connection.commit()
            for app_id in input_apps:
                cursor.execute(
                    'SELECT * FROM User_Apps WHERE app_id = %s', [app_id])
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
