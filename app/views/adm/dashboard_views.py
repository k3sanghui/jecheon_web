import functools
import json
import re

from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify, Flask
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from app.forms.auth_forms import UserLoginForm, UserCreateForm
from app.lib import common
from app.module import dbModule
from flask_mail import Mail, Message

bp = Blueprint('adm', __name__, url_prefix='/adm')

@bp.route('/', methods=('GET', 'POST'))
def index():
    return render_template('adm/dashboard.html')