from flask import Blueprint, abort, current_app, g, request, redirect, \
                  render_template, url_for
from werkzeug.security import safe_str_cmp
from functools import wraps
import hashlib
import os
import random
import string


url_prefix = '/phase2-%s/' % os.environ.get('PHASE2_TOKEN')
phase2 = Blueprint('phase2', __name__, url_prefix=url_prefix)


def random_string():
    """Return 32 random alphanumeric characters"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for x in range(32))


def test_login(username, password):
    password = password.encode('utf-8')
    pw_hash = current_app.redis.get('user:%s:password' % username)
    if not pw_hash:
        return False
    if not safe_str_cmp(hashlib.sha1(password).hexdigest(), pw_hash):
        return False
    return True


def require_auth(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        session_token = request.cookies.get('session')
        if not session_token:
            abort(403)
        g.username = current_app.redis.get('session:%s' % session_token)
        if not g.username:
            abort(403)
        g.username = g.username.decode('utf-8')
        return fn(*args, **kwargs)
    return inner


@phase2.route('')
def home():
    return render_template('phase2/home.html')


@phase2.route('login/', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    if test_login(username, password):
        session_token = random_string()
        current_app.redis.set('session:%s' % session_token, username)
        resp = redirect(url_for('phase2.dashboard'), code=303)
        resp.set_cookie('session', session_token)
        return resp
    else:
        return redirect(url_for('phase2.home'), code=303)


@phase2.route('dashboard/')
@require_auth
def dashboard():
    if g.username == 'admin':
        return render_template('phase2/success.html')
    else:
        ids = current_app.redis.lrange('items:%s' % g.username, 0, -1)
        items = {}
        for i in ids:
            i = i.decode('utf-8')
            message = current_app.redis.get('user:%s:%s' % (g.username, i))
            items[i] = message.decode('utf-8')
        return render_template('phase2/dashboard.html', items=items)


@phase2.route('dashboard/<username>/<item_id>/')
@require_auth
def todo_item(username, item_id):
    message = current_app.redis.get('user:%s:%s' % (username, item_id))
    if not message:
        abort(404)
    message = message.decode('utf-8')
    return render_template('phase2/item.html', item=item_id, message=message)
