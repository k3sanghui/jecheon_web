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
from app.lib.db_function import sql_fetch_array, get_title_select
from datetime import datetime

now = datetime.now()

bp = Blueprint('sta', __name__, url_prefix='/adm/sta')
@bp.route('/list/', methods=('GET', 'POST'))
def _list():
    search_list = {}
    sql_search = ""
    s_app_title = request.args.get('s_app_title')
    s_start = request.args.get('s_start')
    s_end = request.args.get('s_end')

    if s_app_title is not None and s_app_title != "":
        sql_search += f" and ta.ds_app_title = '{s_app_title}'"
    if s_start is not None and s_start != "":
        sql_search += f" and to_char(ta.dt_create, 'YYYY-MM-DD') >= '{s_start}' "
    else:
        s_start = now.strftime("%Y-%m-%d")
        sql_search += f" and to_char(ta.dt_create, 'YYYY-MM-DD') >= '{s_start}' "
    if s_end is not None and s_end != "":
        sql_search += f" and to_char(ta.dt_create, 'YYYY-MM-DD') <= '{s_end}' "
    else:
        s_end = now.strftime("%Y-%m-%d")
        sql_search += f" and to_char(ta.dt_create, 'YYYY-MM-DD') <= '{s_end}' "

    sql = f"select te.ds_title, " \
              f"(select count(*) from tapp_appl010 ta where ta.seq_elet = te.seq_elet {sql_search}) as tot, " \
              f"(select count(*) from tapp_appl010 ta where ta.seq_elet = te.seq_elet and ty_stat='승인' {sql_search}) as a_tot, " \
              f"(select count(*) from tapp_appl010 ta where ta.seq_elet = te.seq_elet and ty_stat='미승인' {sql_search}) as u_tot, " \
              f"(select count(*) from tapp_appl010 ta where ta.seq_elet = te.seq_elet and ty_stat='보류' {sql_search}) as h_tot " \
          "from tapp_appl010 ta " \
          "left join tapp_elet010 te " \
          "on ta.seq_elet = te.seq_elet " \
          "and ta.yn_removed = 'N' " \
          "and te.yn_removed = 'N' " \
          "group by te.seq_elet, te.ds_title"
    sta_list = sql_fetch_array(sql, )

    title_list = get_title_select()

    search_list['s_app_title'] = request.args.get("s_app_title")
    search_list['s_start'] = s_start
    search_list['s_end'] = s_end

    return render_template('adm/sta/sta_list.html', title_list=title_list, sta_list=sta_list, search_list=search_list)