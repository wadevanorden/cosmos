from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import urlencode

app = Flask(__name__)


@app.route("/")
def overview():
    return render_template('index.html')

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
        'openid.return_to': 'http://127.0.0.1:5000/steam_authorized',
        'openid.realm': 'http://127.0.0.1:5000'
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