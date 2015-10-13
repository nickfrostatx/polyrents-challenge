from flask import Blueprint
import os


url_prefix = '/phase2-%s/' % os.environ.get('PHASE2_TOKEN')
phase2 = Blueprint('phase2', __name__, url_prefix=url_prefix)


@phase2.route('')
def home():
    return 'TODO'
