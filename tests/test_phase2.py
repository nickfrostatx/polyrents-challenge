from util import app
import hashlib
import os

phase2_url = '/phase2-%s/' % os.environ.get('PHASE2_TOKEN')
admin_password = u'adminpass'
admin_hash = hashlib.sha1(admin_password.encode('utf-8')).hexdigest()
session_key = 'sessionkey'
admin_session_key = 'adminsessionkey'


def init_data(redis):
    redis.set('user:test:password', hashlib.sha1(b'test').hexdigest())
    redis.set('user:admin:password', admin_hash)
    redis.set('user:test:1', 'Buy groceries')
    redis.set('user:test:2', 'Clean the patio')
    redis.set('user:test:3', 'Take over the world')
    redis.rpush('items:test', 1, 2, 3)
    redis.set('session:%s' % session_key, 'test')
    redis.set('session:%s' % admin_session_key, 'admin')
    return app


def test_home(app):
    rv = app.get(phase2_url)
    assert rv.status_code == 200
    assert b'Sign In' in rv.data


def test_404(app):
    rv = app.get(phase2_url + 'asdf')
    assert rv.status_code == 404


def test_get_405(app):
    rv = app.get(phase2_url + 'login/')
    assert rv.status_code == 405


def test_403s(app):
    """These should return 403 instead of 404."""
    for url in ('dashboard/', 'dashboard/test/1/', 'dashboard/abc/def/'):
        rv = app.get(phase2_url + url)
        assert rv.status_code == 403
        rv = app.get(phase2_url + url, headers={'Cookie': 'session=asdf'})
        assert rv.status_code == 403


def test_post_405(app):
    """Be sure this returns 405, instead of 404 or 403."""
    for url in ('', 'dashboard/', 'dashboard/test/1/', 'dashboard/abc/def/'):
        rv = app.post(phase2_url + url)
        assert rv.status_code == 405


def test_bad_login(app):
    url = phase2_url + 'login/'
    init_data(app.application.redis)

    rv = app.post(url)
    assert rv.status_code == 303
    assert 'dashboard' not in rv.headers.get('Location')

    rv = app.post(url, data={'username': 'abcdef', 'password': 'abcdef'})
    assert rv.status_code == 303
    assert 'dashboard' not in rv.headers.get('Location')

    rv = app.post(url, data={'username': 'test'})
    assert rv.status_code == 303
    assert 'dashboard' not in rv.headers.get('Location')

    rv = app.post(url, data={'username': 'test', 'password': 'abcdef'})
    assert rv.status_code == 303
    assert 'dashboard' not in rv.headers.get('Location')


def test_good_login(app):
    url = phase2_url + 'login/'
    init_data(app.application.redis)

    rv = app.post(url, data={'username': 'test', 'password': 'test'})
    assert rv.status_code == 303
    assert 'session=' in rv.headers.get('Set-Cookie')
    assert 'dashboard' in rv.headers.get('Location')

    rv = app.post(url, data={'username': 'admin', 'password': admin_password})
    assert rv.status_code == 303
    assert 'session=' in rv.headers.get('Set-Cookie')
    assert 'dashboard' in rv.headers.get('Location')


def test_dashboard(app):
    url = phase2_url + 'dashboard/'
    init_data(app.application.redis)

    rv = app.get(url, headers={'Cookie': 'session=%s' % session_key})
    assert rv.status_code == 200
    assert b'Buy groceries' in rv.data
    assert b'Take over the world' in rv.data


def test_item_404(app):
    url = phase2_url + 'dashboard/'
    init_data(app.application.redis)

    rv = app.get(url + 'abcdef/0/', headers={
                                        'Cookie': 'session=%s' % session_key})
    assert rv.status_code == 404

    rv = app.get(url + 'test/0/', headers={
                                        'Cookie': 'session=%s' % session_key})
    assert rv.status_code == 404

    rv = app.get(url + 'admin/1/', headers={
                                        'Cookie': 'session=%s' % session_key})
    assert rv.status_code == 404


def test_solution(app):
    url = phase2_url + 'dashboard/admin/password/'
    init_data(app.application.redis)

    rv = app.get(url, headers={'Cookie': 'session=%s' % session_key})
    assert rv.status_code == 200
    assert admin_hash.encode('utf-8') in rv.data


def test_admin_dashboard(app):
    url = phase2_url + 'dashboard/'
    init_data(app.application.redis)

    rv = app.get(url, headers={'Cookie': 'session=%s' % admin_session_key})
    assert rv.status_code == 200
    assert b'Challenge complete!' in rv.data
