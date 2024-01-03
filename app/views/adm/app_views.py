################################################
# @FileName : /jecheon_web/app/views/adm/app_views.py
# @Project : 제천(전광판) 주민참여 프로그램
# @Date : 2023-08-16
# @author : 김상희
# @History :
# 2023-08-16|김상희|최초작성
# @Description : 관리자 신청관리
################################################
import os
import shutil

import requests
from bs4 import BeautifulSoup
from html2image import Html2Image
from flask import Blueprint, url_for, render_template, request, g, jsonify, send_from_directory
from flask_paginate import Pagination, get_page_args
from werkzeug.utils import redirect, secure_filename
from app.forms.app_forms import AdmAppForm, AdmAppInsForm
from app.lib.common import file_info
from app.lib.db_function import get_elet_select, get_title_select, sql_query, sql_fetch, sql_fetch_array
from app.module import dbModule
from app.lib import common
from datetime import datetime
from app.views.auth_views import login_required
from config import ROOT_PATH, APP_EXT_URL, UPLOAD_FOLDER, BASE_DIR

appl_tbl = "tapp_appl010"
elet_tbl = "tapp_elet010"
file_tbl = "tapp_file010"
now = datetime.now()

bp = Blueprint('app', __name__, url_prefix='/adm/app')


@bp.route('/list/', methods=('GET', 'POST'))
@login_required
def _list():
    search_list = {}
    now_day = now.strftime("%Y-%m-%d")
    sql_search = ""
    s_app_title = request.args.get('s_app_title')
    s_stat = request.args.get('s_stat')
    s_start = request.args.get('s_start')
    s_end = request.args.get('s_end')
    s_gubun = request.args.get('s_gubun')
    stx = request.args.get('stx')
    chk = request.args.get('chk')
    
    # 대시보드 더보기 누를시
    if chk == "now_app":
        s_start = now_day
        s_end = now_day
        s_stat = '신청'
    elif chk == "now_info":
        sql_search += f"and to_char(ta.dt_start, 'YYYY-MM-DD') <= '{now_day}' "
        sql_search += f"and to_char(ta.dt_end, 'YYYY-MM-DD') >= '{now_day}' "

    if s_app_title is not None and s_app_title != "":
        sql_search += f" and ta.ds_app_title = '{s_app_title}'"
    if s_stat is not None and s_stat != "":
        sql_search += f" and ta.ty_stat = '{s_stat}'"
    else:
        sql_search += " and ta.ty_stat<>'임시저장'"

    if s_start is not None and s_start != "":
        sql_search += f" and to_char(ta.dt_create, 'YYYY-MM-DD') >= '{s_start}' "
    if s_end is not None and s_end != "":
        sql_search += f" and to_char(ta.dt_create, 'YYYY-MM-DD') <= '{s_end}' "

    if stx is not None and stx != "":
        if s_gubun is not None and s_gubun != "":
            sql_search += f" and ta.{s_gubun} like '%%{stx}%%'"
        else:
            sql_search += f" and (ta.ds_app_name like '%%{stx}%%' or ta.ds_text like '%%{stx}%%' )"

    per_page = 10
    page, _, offset = get_page_args(per_page=per_page)
    total_sql = f"select count(*) as total from {appl_tbl} ta where 1=1 and ta.yn_removed = 'N' {sql_search} "
    total = sql_fetch(total_sql)

    sql = f"SELECT * FROM {appl_tbl} ta where 1=1 and ta.yn_removed = 'N' {sql_search} order by ta.seq_app desc limit %s offset %s;"
    sql_common = (per_page, offset)
    app_list = sql_fetch_array(sql, sql_common)

    title_list = get_title_select()

    pagination = Pagination(
        page=page,  # 지금 우리가 보여줄 페이지는 1 또는 2, 3, 4, ... 페이지인데,
        total=total['total'],  # 총 몇 개의 포스트인지를 미리 알려주고,
        per_page=per_page,  # 한 페이지당 몇 개의 포스트를 보여줄지 알려주고,
        prev_label="이전",  # 전 페이지와,
        next_label="다음",  # 후 페이지로 가는 링크의 버튼 모양을 알려주고,
        format_total=True,  # 총 몇 개의 포스트 중 몇 개의 포스트를 보여주고있는지 시각화,
    )

    search_list['s_app_title'] = request.args.get('s_app_title')
    search_list['s_stat'] = s_stat
    search_list['s_start'] = s_start
    search_list['s_end'] = s_end
    search_list['s_gubun'] = request.args.get('s_gubun')
    search_list['stx'] = request.args.get('stx')
    return render_template('adm/app/app_list.html', app_list=app_list, total=total['total'], pagination=pagination, search=True, bs_version=5,
                           title_list=title_list, search_list=search_list)


@bp.route('/view/<int:seq_app>/')
@login_required
def view(seq_app):
    sql = "select * from " + appl_tbl + " where seq_app = %s"
    sql_common = (seq_app,)
    data = sql_fetch(sql, sql_common)
    rm_html = BeautifulSoup(data['ds_real_text'], "lxml").text
    data['ds_real_text'] = rm_html
    elet_sql = "select * from " + elet_tbl + " where seq_elet = %s"
    sql_common = (data['seq_elet'],)
    elet = sql_fetch(elet_sql, sql_common)
    file_sql = "select * from " + file_tbl + " where ty_tbl= %s and seq_tbl = %s limit 1"
    sql_common = (appl_tbl, seq_app)
    file_data = sql_fetch(file_sql, sql_common)
    return render_template('adm/app/app_view.html', app=data, elet=elet, file_name=file_data['ds_orifile'])


@bp.route('/view_file/<filename>')
@login_required
def view_file(filename):
    path = ROOT_PATH + UPLOAD_FOLDER + appl_tbl + "\\"
    return send_from_directory(path, filename)


@bp.route('/ins/', methods=('GET', 'POST'))
@login_required
def ins():
    error = None
    ip = common.get_ip()
    form = AdmAppInsForm()
    if request.method == 'POST' and form.validate_on_submit():
        seq_user = form.seq_user.data
        seq_elet = form.seq_elet.data
        ds_app_name = form.ds_app_name.data
        ds_app_title = form.ds_app_title.data
        ds_app_tel = form.ds_app_tel.data
        dt_start = form.dt_start.data
        dt_end = form.dt_end.data
        ds_text = form.ds_text.data
        ds_reason = form.ds_reason.data
        ty_stat = "신청"
        id_create = g.user['id_user']
        sql = "INSERT INTO " + appl_tbl + " " \
                                          "(seq_user, seq_elet, ds_app_name, ds_app_title, ds_app_tel, dt_start, dt_end, ty_stat, ds_text, ds_reason, id_create, dt_create, ip_create) " \
                                          "VALUES " \
                                          "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING seq_app;"
        sql_common = (
        seq_user, seq_elet, ds_app_name, ds_app_title, ds_app_tel, dt_start, dt_end, ty_stat, ds_text, ds_reason,
        id_create, now, ip)
        seq_noti = sql_query(sql, sql_common)
        if seq_noti:
            return redirect(url_for('app._list'))
    title_list = get_title_select()
    return render_template('adm/app/app_form_ins.html', form=form, title_list=title_list)


@bp.route('/mod/<int:seq_app>', methods=('GET', 'POST'))
@login_required
def mod(seq_app):
    ip = common.get_ip()
    form = AdmAppForm()
    if request.method == 'POST':  # POST 요청
        if form.validate_on_submit():
            sql = "update " + appl_tbl + " set seq_elet = %s, " \
                                         " ds_app_name = %s, " \
                                         " ds_app_title = %s, " \
                                         " ds_app_tel = %s, " \
                                         " dt_start = %s, " \
                                         " dt_end = %s, " \
                                         " ty_stat = %s, " \
                                         " dt_statdate = %s, " \
                                         " ds_text = %s, " \
                                         " ds_reason = %s, " \
                                         " ds_real_text = %s, " \
                                         " ds_bigo = %s, " \
                                         " id_update = %s, " \
                                         " dt_update = %s, " \
                                         " ip_update = %s " \
                                         " where seq_app = %s RETURNING seq_app;"
            sql_common = (form.seq_elet.data, form.ds_app_name.data, form.ds_app_title.data, form.ds_app_tel.data,
                          form.dt_start.data, form.dt_end.data, form.ty_stat.data, now, form.ds_text.data,
                          form.ds_reason.data, form.ds_real_text.data, form.ds_bigo.data, g.user['id_user'], now, ip,
                          seq_app)
            sql_query(sql, sql_common)

            if form.ty_stat.data == "승인":
                file_path = ROOT_PATH + UPLOAD_FOLDER + appl_tbl + "\\" + form.file_name.data
                photoimg = open(file_path, 'rb')
                sql = "select id_settop from " + elet_tbl + " where seq_elet = %s "
                sql_common = (form.seq_elet.data,)
                data = sql_fetch(sql, sql_common)
                url = APP_EXT_URL
                field_data = {"settop_id": data['id_settop'], "sdate": form.dt_start.data, "edate": form.dt_end.data}
                file_data = {"photoimg": photoimg}
                res = requests.post(url, data=field_data, files=file_data)
                res.close()
            return redirect(url_for('app.view', seq_app=seq_app))
    else:  # GET 요청
        db_class = dbModule.Database()
        sql = "select seq_app, seq_user, seq_elet, ds_app_name, ds_app_title, ds_app_tel, dt_start, dt_end, ty_stat, ds_text, ds_reason, ds_real_text  from " + appl_tbl + " where seq_app = %s"
        sql_common = (seq_app,)
        data = db_class.executeOne(sql, sql_common)
        db_class.close()
        form.seq_app.data = data['seq_app']
        form.seq_user.data = data['seq_user']
        form.seq_elet.data = data['seq_elet']
        form.ds_app_name.data = data['ds_app_name']
        form.ds_app_title.data = data['ds_app_title']
        form.ds_app_tel.data = data['ds_app_tel']
        form.dt_start.data = data['dt_start']
        form.dt_end.data = data['dt_end']
        form.ty_stat.data = data['ty_stat']
        form.ds_text.data = data['ds_text']
        form.ds_reason.data = data['ds_reason']
        form.ds_real_text.data = data['ds_real_text']
        elet = get_elet_select(data['seq_elet'])
        if elet:
            form.ds_addr.data = elet['ds_addr']
            form.no_width.data = elet['no_width']
            form.no_height.data = elet['no_height']
    return render_template('adm/app/app_form.html', form=form)


@bp.route('/del/<int:seq_app>')
@login_required
def _del(seq_app):
    ip = common.get_ip()
    sql = "update " + appl_tbl + " set yn_removed = 'Y', " \
                                 " id_update = %s, " \
                                 " dt_update = %s, " \
                                 " ip_update = %s " \
                                 " where seq_app = %s RETURNING seq_app;"
    sql_common = (g.user['id_user'], now, ip, seq_app,)
    data = sql_query(sql, sql_common)
    return redirect(url_for('app._list'))


# 웹에디터 미리보기 버튼 클릭시 작성한 html 이미지 저장 및 출력
@bp.route('/preview/', methods=('GET', 'POST'))
@login_required
def preview():
    ip = common.get_ip()
    result = {"code": 400, "no_width": "", "no_height": "", "txt": "", "msg": "", "file": ""}
    if request.method == 'POST':
        seq_app = request.form['seq_app']
        seq_elet = request.form['seq_elet']
        html = request.form['ds_real_text']
        if seq_elet:
            sql = "select id_settop, no_width, no_height from " + elet_tbl + " where seq_elet = %s"
            sql_common = (seq_elet,)
            data = sql_fetch(sql, sql_common)
            if data is not None:
                no_width = data['no_width']
                no_height = data['no_height']
                id_settop = data['id_settop']
                css = "body {background: #000;}"
                hti = Html2Image(size=(int(data['no_width']), int(data['no_height'])))
                str_now_date = datetime.now().strftime('%Y%m%d%H%M%S%f')
                filename = f"temp_{str_now_date}_{id_settop}_{seq_app}.png"
                save_path = ROOT_PATH + UPLOAD_FOLDER + appl_tbl
                os.makedirs(save_path, exist_ok=True)
                os.chmod(save_path, 0o0777)
                try:
                    hti.screenshot(html_str=html, css_str=css,
                                   save_as=secure_filename(filename))
                    shutil.move(os.path.join(BASE_DIR+"jecheon_web", filename), os.path.join(save_path, filename))
                    file_info_data = file_info(filename)
                except BaseException as e:
                    print(e)
                    result['msg'] = "이미지 저장이 실패 하였습니다."
                    return jsonify(result)
                else:
                    sql = "select seq_file from " + file_tbl + " where ty_tbl = %s and seq_tbl = %s limit 1"
                    sql_common = (appl_tbl, seq_app)
                    data = sql_fetch(sql, sql_common)
                    seq_num = 0
                    no_size = file_info_data['file_size']
                    ty_file = file_info_data['file_type']
                    if data is None:
                        # 이전 이미지 저장 내역이 없으면 신규 등록
                        sql = "INSERT INTO " + file_tbl + "(ty_tbl, seq_num, seq_tbl, ds_orifile, ds_chafile, no_size, no_imgwidth, no_imgheight, ty_file, id_create, dt_create, ip_create) " \
                                                          "VALUES " \
                                                          "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING seq_file;"

                        sql_common = (
                            appl_tbl, seq_num, seq_app, filename, filename, no_size, no_width, no_height, ty_file,
                            g.user['id_user'], now, ip)
                        sql_query(sql, sql_common)
                    else:
                        # 이전 이미지 저장 내역이 있으면 업데이트
                        sql = "update " + file_tbl + " set ds_orifile = %s," \
                                                     " ds_chafile = %s," \
                                                     " no_size = %s," \
                                                     " no_imgwidth = %s," \
                                                     " no_imgheight = %s," \
                                                     " ty_file = %s, " \
                                                     " id_update = %s, " \
                                                     " dt_update = %s, " \
                                                     " ip_update = %s " \
                                                     " where seq_file = %s RETURNING seq_file;"
                        sql_common = (
                            filename, filename, no_size, no_width, no_height, ty_file, g.user['id_user'], now, ip,
                            data['seq_file'])
                        sql_query(sql, sql_common)
                    result['code'] = 200
                    result['no_width'] = no_width
                    result['no_height'] = no_height
                    result['file_name'] = filename
                    result['txt'] = html
            else:
                result['msg'] = "비정상적인 동작입니다."
        else:
            result['msg'] = "비정상적인 동작입니다."
    else:
        result['msg'] = "비정상적인 동작입니다."

    return jsonify(result)