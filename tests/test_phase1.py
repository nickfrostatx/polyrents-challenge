from util import app


def test_unauthed(app):
    rv = app.get('/phase1/')
    assert rv.status_code == 200
    assert b'Not authenticated' in rv.data


def test_authed(app):
    rv = app.get('/phase1/', headers={'Cookie': 'uid=0'})
    assert rv.status_code == 200
    assert b'Authenticated' in rv.data
