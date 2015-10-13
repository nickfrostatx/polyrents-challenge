from util import app


def test_home(app):
    rv = app.get('/')
    assert rv.status_code == 301


def test_404(app):
    rv = app.get('/asdf')
    assert rv.status_code == 404
