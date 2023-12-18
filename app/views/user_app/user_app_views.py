################################################
# @FileName : /jecheon_web/app/user_app/views/user_app/user_app_views.py
# @Project : 제천(전광판) 주민참여 프로그램
# @Date : 2023-08-17
# @author : 김상희
# @History :
# 2023-08-17|김상희|최초작성
# @Description : 주민참여 신청
################################################
import os.path

from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify, Flask
from flask_paginate import Pagination, get_page_args
from werkzeug.utils import redirect, secure_filename
from app.forms.user_app_forms import UserAppForm
from app.module import dbModule
from app.lib import common
from datetime import datetime
from app.views.auth_views import login_required

global tbl, now
tbl = "tapp_appl010"
elet_tbl = "tapp_elet010"
now = datetime.now()

bp = Blueprint('user_app', __name__, url_prefix='/user_app')
@bp.route('/list/', methods=('GET', 'POST'))
@login_required
def _list():
    db_class = dbModule.Database()
    per_page = 10
    page, _, offset = get_page_args(per_page=per_page)
    total_sql = "select count(*) as total from " + tbl + " where 1=1"
    total = db_class.executeOne(total_sql)
    sql = "SELECT * FROM " + tbl + " where 1=1 and yn_removed = 'N' and seq_user = %s order by seq_app desc limit %s offset %s;"
    sql_common = (g.user['seq_user'], per_page, offset)
    app_list = db_class.executeAll(sql, sql_common)
    db_class.close()

    pagination = Pagination(
        page=page,  # 지금 우리가 보여줄 페이지는 1 또는 2, 3, 4, ... 페이지인데,
        total=total['total'],  # 총 몇 개의 포스트인지를 미리 알려주고,
        per_page=per_page,  # 한 페이지당 몇 개의 포스트를 보여줄지 알려주고,
        prev_label="이전",  # 전 페이지와,
        next_label="다음",  # 후 페이지로 가는 링크의 버튼 모양을 알려주고,
        format_total=True,  # 총 몇 개의 포스트 중 몇 개의 포스트를 보여주고있는지 시각화,
    )
    return render_template('user_app/user_app_list.html', app_list=app_list, pagination=pagination, search=True, bs_version=5, )

@bp.route('/ins/', methods=('GET', 'POST'))
@login_required
def ins():
    error = None
    ip = common.get_ip()
    form = UserAppForm()
    if request.method == 'POST' and form.validate_on_submit():
        db_class = dbModule.Database()
        seq_user = form.seq_user.data
        seq_elet = form.seq_elet.data
        ds_app_name = form .ds_app_name.data
        ds_app_title = form.ds_app_title.data
        ds_app_tel = form.ds_app_tel.data
        dt_start = form.dt_start.data
        dt_end = form.dt_end.data
        ds_text = form.ds_text.data
        ds_reason = form.ds_reason.data
        temp_chk = request.form.get('temp_chk')
        if temp_chk=='Y':
            ty_stat="임시저장"
        else:
            ty_stat = "신청"
        id_create = g.user['id_user']
        sql = "INSERT INTO " + tbl + " " \
                                     "(seq_user, seq_elet, ds_app_name, ds_app_title, ds_app_tel, dt_start, dt_end, ty_stat, ds_text, ds_reason, id_create, dt_create, ip_create) " \
                                     "VALUES " \
                                     "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING seq_app;"
        sql_common = (seq_user, seq_elet, ds_app_name, ds_app_title, ds_app_tel, dt_start, dt_end, ty_stat, ds_text, ds_reason, id_create, now, ip)
        seq_noti = db_class.execute(sql, sql_common)
        db_class.commit()
        db_class.close()
        if seq_noti:
            return redirect(url_for('user_app._list'))
    # flash(error)
    title_list = get_title_select()
    return render_template('user_app/user_app_form.html', form=form, title_list=title_list)

@bp.route('/mod/<int:seq_app>', methods=('GET', 'POST'))
@login_required
def mod(seq_app):
    ip = common.get_ip()
    form = UserAppForm()
    if request.method == 'POST':  # POST 요청
        if form.validate_on_submit():
            if request.form.get('temp_chk')=='Y':
                ty_stat = '임시저장'
                url = 'user_app.ins'
            else:
                ty_stat = '신청'
                url = 'user_app.view'
            db_class = dbModule.Database()
            sql = "update " + tbl + " set seq_elet = %s, " \
                                        " ds_app_name = %s," \
                                        " ds_app_title = %s," \
                                        " ds_app_tel = %s," \
                                        " dt_start = %s," \
                                        " dt_end = %s," \
                                        " ty_stat = %s," \
                                        " ds_text = %s," \
                                        " ds_reason = %s," \
                                        " id_update = %s, " \
                                        " dt_update = %s, " \
                                        " ip_update = %s " \
                                        " where seq_app = %s RETURNING seq_app;"
            sql_common = (form.seq_elet.data, form.ds_app_name.data, form.ds_app_title.data, form.ds_app_tel.data,
                          form.dt_start.data, form.dt_end.data, ty_stat, form.ds_text.data, form.ds_reason.data,
                          g.user['id_user'], now, ip, seq_app,)
            data = db_class.execute(sql, sql_common)
            db_class.commit()
            db_class.close()
            return redirect(url_for(url, seq_app=seq_app))
    else:  # GET 요청
        db_class = dbModule.Database()
        sql = "select seq_app, seq_user, seq_elet, ds_app_name, ds_app_title, ds_app_tel, dt_start, dt_end, ty_stat, ds_text, ds_reason from " + tbl + " where seq_app = %s"
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
        title_list = get_title_select()

    return render_template('user_app/user_app_form.html', form=form, title_list=title_list)

@bp.route('/view/<int:seq_app>/')
@login_required
def view(seq_app):
    db_class = dbModule.Database()
    sql = "select * from " + tbl + " where seq_app = %s"
    sql_common = (seq_app,)
    data = db_class.executeOne(sql, sql_common)
    db_class.close()
    db_class = dbModule.Database()
    elet_sql="select * from " + elet_tbl + " where seq_elet = %s"
    sql_common = (data['seq_elet'],)
    elet = db_class.executeOne(elet_sql, sql_common)
    db_class.close()

    return render_template('user_app/user_app_view.html', user_app=data, elet=elet)

# 개소명 목록 조회
def get_title_select():
    db_class = dbModule.Database()
    sql = "select seq_elet, ds_title, ds_addr, no_width, no_height from " + elet_tbl + " where yn_removed = 'N' order by seq_elet asc"
    ret = db_class.executeAll(sql, )
    db_class.close()
    return ret