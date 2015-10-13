from flask import Flask, redirect, url_for
from . import __name__ as package_name
from .phase1 import phase1
from .phase2 import phase2


app = Flask(package_name)

app.register_blueprint(phase1)
app.register_blueprint(phase2)


@app.route('/')
def root():
    return redirect(url_for('phase1.home'), code=301)
