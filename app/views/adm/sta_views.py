################################################
# @FileName : /user_app/views/adm/sta_views.py
# @Project : 제천(전광판) 주민참여 프로그램
# @Date : 2023-08-16
# @author : 김상희
# @History :
# 2023-08-16|김상희|최초작성
# @Description : 관리자 : 통계
################################################
from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify, Flask
from app.lib.db_function import sql_fetch_array

bp = Blueprint('sta', __name__, url_prefix='/adm/sta')
@bp.route('/list/', methods=('GET', 'POST'))
def _list():
    sql = "select te.ds_title, " \
              "(select count(*) from tapp_appl010 where seq_elet = te.seq_elet) as tot, " \
              "(select count(*) from tapp_appl010 where seq_elet = te.seq_elet and ty_stat='승인') as a_tot, " \
              "(select count(*) from tapp_appl010 where seq_elet = te.seq_elet and ty_stat='미승인') as u_tot, " \
              "(select count(*) from tapp_appl010 where seq_elet = te.seq_elet and ty_stat='보류') as h_tot " \
          "from tapp_appl010 ta " \
          "left join tapp_elet010 te " \
          "on ta.seq_elet = te.seq_elet " \
          "and ta.yn_removed = 'N' " \
          "and te.yn_removed = 'N' " \
          "group by te.seq_elet, te.ds_title"
    sta_list = sql_fetch_array(sql, )

    return render_template('adm/sta/sta_list.html', sta_list=sta_list)