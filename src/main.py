from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def overview():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')


'''''''''
@app.route("/steam_auth")
@login_required
def auth_with_steam():
    os.environ['openid.ns'] = 'http://specs.openid.net/auth/2.0'
    os.environ['openid.identity'] = 'http://specs.openid.net/auth/2.0/identifier_select'
    os.environ['openid.mode'] = 'checkid_setup'
    os.environ['openid.claimed_id'] = 'http://specs.openid.net/auth/2.0/identifier_select'
    os.environ['openid.return_to'] = 'http://127.0.0.1:5000/steam_authorized'
    os.environ['openid.realm'] = 'http://127.0.0.1:5000'
    params = {
        'openid.ns': os.environ['openid.ns'],
        'openid.identity': os.environ['openid.identity'],
        'openid.claimed_id': os.environ['openid.claimed_id'],
        'openid.mode': os.environ['openid.mode'],
        'openid.return_to': os.environ['openid.return_to'],
        'openid.realm': os.environ['openid.realm']
    }
    query_string = urlencode(params)
    steam_openid_url = 'https://steamcommunity.com/openid/login'
    auth_url = steam_openid_url + "?" + query_string
    return redirect(auth_url)

@app.route("/steam_authorized")
@login_required
def steam_authorize():
    steam_id = {
        'steam_id': request.args.get('openid.claimed_id').split('/')[-1]
    }
    return redirect(url_for('overview'))
'''''''''

