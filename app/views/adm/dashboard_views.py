from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify, Flask

from app.lib.db_function import sql_query, sql_fetch_array
from app.views.auth_views import login_required
from datetime import datetime

bp = Blueprint('adm', __name__, url_prefix='/adm')
now = datetime.now()
@login_required
@bp.route('/', methods=('GET', 'POST'))
def index():
    now_day = now.strftime("%Y-%m-%d")
    # 당일신청건 10건 조회
    day_sql="select * from tapp_appl010 ta where ta.ty_stat='신청' and to_char(ta.dt_create, 'YYYY-MM-DD') = %s order by ta.seq_app desc limit 10"
    day_sql_common = (now_day,)
    day_ret = sql_fetch_array(day_sql, day_sql_common)

    # 현재일자 포함 전광판 적용 출력 정보 조회
    now_sql="select ta.*, tf.seq_file, tf.ds_orifile, tf.ds_chafile " \
              "from tapp_appl010 ta, "\
                   "tapp_file010 tf "\
             "where ta.seq_app = tf.seq_tbl "\
               "and tf.ty_tbl='tapp_appl010' "\
               "and ta.ty_stat='승인' "\
               "and to_char(ta.dt_start, 'YYYY-MM-DD') <= %s "\
               "and to_char(ta.dt_end, 'YYYY-MM-DD') >= %s "\
             "order by ta.seq_app desc limit 10 "
    now_sql_common=(now_day, now_day,)
    now_ret=sql_fetch_array(now_sql, now_sql_common)

    return render_template('adm/dashboard.html', day_list=day_ret, now_list=now_ret)