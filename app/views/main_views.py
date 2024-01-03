from flask import Blueprint, url_for, session, g
from werkzeug.utils import redirect

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
def index():
    if 'id_user' in session:
        if session.get('no_level') == 2:
            return redirect(url_for('user_app._list'))
        elif session.get('no_level') > 5:
            return redirect(url_for('adm.index'))
    else:
        session['no_level'] = 1
        return redirect(url_for('auth.login'))