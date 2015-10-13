from flask import Flask
from . import __name__ as package_name

app = Flask(package_name)
