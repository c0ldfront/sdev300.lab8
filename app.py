import logging
import time
from functools import wraps
import os

from flask import Flask, make_response, redirect, \
    render_template, \
    request, \
    url_for
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect()

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'AreVerySecretKey'

# using this config for setting the logging output for werkqeug requests.
# by doing this it allows the log files to only contain INFO warnings.
# This allows the logs to be cleaner only with logs which we set for the,
# auth error.
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.basicConfig(filename=os.path.dirname(__file__) + '/flask_server.log', level=logging.INFO)

csrf.init_app(app)

# use the eval function to open and read the txt file, we save the user file
# as a raw dict->text, by doing so allows us to join dump the text->dict.
# i like this option for now because no iteration over the text file.
# it also allows for cleaner saves its a 1:1.
user_db = eval(open(os.path.dirname(__file__) + '/users.txt', 'r').read())

# init the set and dict for storing common passwords in memory and user
# throttling.
common_password_db: set = set()
user_rate_db: dict = dict()


# here is the custom class struct we use to store the rate limits
# for each failed attempt. with a few helper functions for checking
# conditionals.
class UserRateLimit:
    tries = 0
    ip_address = None
    last_attempt = None

    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.last_attempt = time.time()

    def log_attempt(self):
        self.tries += 1
        self.last_attempt = time.time()
        logging.info(f'[AUTH]: {self.ip_address} failed to login at '
                     f'{self.last_attempt} epoch time.')

    def get_tries(self):
        return self.tries

    def reduce_rate(self):
        # limit lock 2 mins
        if time.time() - self.last_attempt > 120:
            self.tries -= 1

    def clear_rate(self):
        self.tries = 0

    def over_rate(self):
        self.reduce_rate()
        if self.tries > 30:
            return True
        return False

    def __str__(self):
        return self.ip_address

    def __repr__(self):
        return self.ip_address


# log an attempt into the rate table
def set_log_rate():
    user_rate_db[request.environ['REMOTE_ADDR']].log_attempt()


# create a request user inside of the rate db.
def set_rate_user():
    if request.environ['REMOTE_ADDR'] not in user_rate_db:
        user_rate_db[request.environ['REMOTE_ADDR']] = UserRateLimit(
                request.environ['REMOTE_ADDR'])

# ((?:[0-9]{1,3}\.){3}[0-9]{1,3})
# returns a given ip address for a user.
def get_rate():
    return user_rate_db[request.environ['REMOTE_ADDR']]


# load the common passwords into memory so we don't have to keep
# opening the file
with open(os.path.dirname(__file__) + '/CommonPassword.txt', 'r') as password:
    for line in password:
        common_password = line.rstrip("\n")
        common_password_db.add(common_password)
    password.close()


# saving function for dict->text file, overwrite the entire file not the most
# affective way.
def save_user(user_name, password):
    user_db[user_name] = password
    with open(os.path.dirname(__file__) + '/users.txt', 'w') as user:
        user.write(str(user_db))


# These two functions are custom python decorator, they allow us to intercept
# the requests before it even hits the route function logic.
# with the login_req function bellow we check to make sure the
# cookies are set with a userName, this lets us pull the username
# from the cookies seeing I didn't really want to implement session tokens
# to kep track of the users between browsers. this allows me to easily
# see if a user is logged in, also this isn't really secure, because anyone
# can go into their cookies and set their userName to any user in the database.
# thus, allowing them to masquerade as any user
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(*args, **kwargs)
        if not request.cookies.get('userName'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# check rate just checks ot see if there is a remote user inside the dict i
# declared at the top of the python file. we create a custom data struct class,
# and track the login based on remote_addr. we also remove one retry if
# 30 seconds has passed.
def check_rate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(*args, **kwargs)
        if len(user_rate_db) > 0 and \
                user_rate_db[request.environ['REMOTE_ADDR']].over_rate():
            error = 'too many login attempts... please wait 30 seconds ' \
                    'before trying again.'
            return render_template('login.html', error=error)
        return f(*args, **kwargs)

    return decorated_function


# simple function for checking if a user is valid within side are user db.
def valid_user(post_user, post_pass):
    valid = False
    if post_user in user_db:
        if post_pass == user_db[post_user]:
            valid = True
    return valid


# simple function for checking passwords against the common set.
def check_common_passwords(post_pass):
    if post_pass not in common_password_db:
        return False
    return True


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
@check_rate
def login():
    error = None
    if request.method == 'POST':
        set_rate_user()
        if not valid_user(request.form['username'], request.form['password']):
            set_log_rate()
            error = 'invalid creds, please try again.'
        else:
            get_rate().clear_rate()
            resp = make_response(redirect(url_for('profile')))
            resp.set_cookie('userName', request.form['username'])
            return resp
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('userName', '')
    return resp


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    error = None
    if request.method == 'POST':
        if len(request.form['password']) < 8 \
                or len(request.form['password']) > 64:
            error = 'password should be longer longer than 8 but less than 64'
        elif check_common_passwords(request.form['password']):
            error = 'common password detected'
        else:
            save_user(request.cookies.get('userName'),
                      request.form['password'])
            return redirect(url_for('profile'))
    return render_template('profile.html',
                           userName=request.cookies.get('userName'),
                           error=error)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
