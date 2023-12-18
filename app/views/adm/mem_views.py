################################################
# @FileName : /user_app/views/adm/mem_views.py
# @Project : 제천(전광판) 주민참여 프로그램
# @Date : 2023-08-16
# @author : 김상희
# @History :
# 2023-08-16|김상희|최초작성
# @Description : 관리자 : 회원관리
################################################
from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify, Flask
from flask_paginate import Pagination, get_page_args

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from app.forms.mem_forms import AdmMemForm
from app.module import dbModule
from app.lib import common
from datetime import datetime
from app.views.auth_views import login_required

tbl = "tapp_memb010"
now = datetime.now()

bp = Blueprint('mem', __name__, url_prefix='/adm/mem')


@bp.route('/list/', methods=('GET', 'POST'))
@login_required
def _list():
    db_class = dbModule.Database()
    per_page = 10
    page, _, offset = get_page_args(per_page=per_page)
    total_sql = "select count(*) as total from "+tbl+" where 1=1 and yn_removed = 'N'"
    total = db_class.executeOne(total_sql)

    sql = "SELECT * FROM "+tbl+" where 1=1 and yn_removed = 'N' order by seq_user desc limit %s offset %s;"
    sql_common = (per_page, offset)
    eld_list = db_class.executeAll(sql, sql_common)
    db_class.close()

    pagination = Pagination(
        page=page,  # 지금 우리가 보여줄 페이지는 1 또는 2, 3, 4, ... 페이지인데,
        total=total['total'],  # 총 몇 개의 포스트인지를 미리 알려주고,
        per_page=per_page,  # 한 페이지당 몇 개의 포스트를 보여줄지 알려주고,
        prev_label="이전",  # 전 페이지와,
        next_label="다음",  # 후 페이지로 가는 링크의 버튼 모양을 알려주고,
        format_total=True,  # 총 몇 개의 포스트 중 몇 개의 포스트를 보여주고있는지 시각화,
    )
    return render_template('adm/mem/mem_list.html', mem_list=eld_list, pagination=pagination, search=True, bs_version=5,)


@bp.route('/ins/', methods=('GET', 'POST'))
@login_required
def ins():
    error = None
    form = AdmMemForm()
    if request.method == 'POST' and form.validate_on_submit():
        id_user = form.id_user.data
        ds_name = form.ds_name.data
        ds_password = generate_password_hash(form.ds_password.data)
        ds_tel = form.ds_tel.data
        ds_email = form.ds_email.data
        no_level = form.no_level.data
        yn_emailcertify = form.yn_emailcertify.data

        hp_chk = common.hp_number_chk(ds_tel)
        if hp_chk == "Y":
            error = "잘못된 연락처 입니다."
            flash(error)

        if error is None:
            ds_tel = common.hyphen_hp_number(ds_tel)
            db_class = dbModule.Database()
            sql = "INSERT INTO tapp_memb010 " \
                  "(id_user, ds_name, ds_password, ds_tel, ds_email, no_level, yn_emailcertify) " \
                  "VALUES " \
                  "(%s, %s, %s, %s, %s, %s, %s) RETURNING seq_user;"
            sql_common = (id_user, ds_name, ds_password, ds_tel, ds_email, no_level, yn_emailcertify)
            seq_user = db_class.execute(sql, sql_common)
            db_class.commit()
            db_class.close()
            if seq_user:
                return redirect(url_for('mem._list'))
    return render_template('adm/mem/mem_form.html', form=form)


@bp.route('/view/<int:seq_user>/', methods=('GET', 'POST'))
@login_required
def view(seq_user):
    db_class = dbModule.Database()
    sql = "SELECT * FROM " + tbl + " where 1=1 and yn_removed = 'N' and seq_user = %s;"
    sql_common = (seq_user,)
    data = db_class.executeOne(sql, sql_common)
    db_class.close()
    return render_template('adm/mem/mem_view.html', mem=data)


@bp.route('/mod/<int:seq_user>', methods=('GET', 'POST'))
@login_required
def mod(seq_user):
    error = None
    ip = common.get_ip()
    form = AdmMemForm()
    if request.method == 'POST':  # POST 요청
        if form.validate_on_submit():
            db_class = dbModule.Database()
            hp_chk = common.hp_number_chk(form.ds_tel.data)
            if hp_chk == "Y":
                error = "잘못된 연락처 입니다."
                flash(error)
            if error is None:
                ds_password = generate_password_hash(form.ds_password.data)
                ds_tel = common.hyphen_hp_number(form.ds_tel.data)
                sql = "update " + tbl + " set ds_name = %s," \
                                            " ds_password = %s, " \
                                            " ds_tel = %s, " \
                                            " ds_email = %s, " \
                                            " no_level = %s, " \
                                            " yn_emailcertify = %s, " \
                                            " ds_bigo = %s, " \
                                            " id_update = %s, " \
                                            " dt_update = %s, " \
                                            " ip_update = %s " \
                                            " where seq_user = %s RETURNING seq_user;"

                sql_common = (form.ds_name.data, ds_password, ds_tel, form.ds_email.data, form.no_level.data, form.yn_emailcertify.data, form.ds_bigo.data, "a", now, ip, seq_user,)
                data = db_class.execute(sql, sql_common)
                db_class.commit()
                db_class.close()
                return redirect(url_for('mem.view', seq_user=seq_user))
    else:  # GET 요청
        db_class = dbModule.Database()
        sql = "select * from " + tbl + " where seq_user = %s"
        sql_common = (seq_user,)
        data = db_class.executeOne(sql, sql_common)
        db_class.close()

        form.id_user.data = data['id_user']
        form.ds_name.data = data['ds_name']
        form.ds_password.data = ""
        form.ds_tel.data = data['ds_tel']
        form.ds_email.data = data['ds_email']
        form.no_level.data = data['no_level']
        form.yn_emailcertify.data = data['yn_emailcertify']

    return render_template('adm/mem/mem_form.html', form=form, seq_user=seq_user)


@bp.route('/overlap/', methods=('GET', 'POST'))
@login_required
def over_lap():
    msg = None
    result = "fail"
    if request.method == 'POST':
        id_user = request.form['id_user']
        if id_user:
            db_class = dbModule.Database()
            sql = "SELECT id_user FROM tapp_memb010 where id_user = %s"
            sql_common = (id_user,)
            data = db_class.executeOne(sql, sql_common)
            db_class.commit()
            db_class.close()
            if data:
                msg = "사용할 수 없는 아이디 입니다.";
            else:
                result = "success"
                msg = "사용할수 있는 아이디 입니다.";
        else:
            msg = "아이디를 입력하시길 바랍니다.";
    else:
        msg = "비정상적인 동작입니다.";
    return jsonify({'result': result, 'msg': msg})