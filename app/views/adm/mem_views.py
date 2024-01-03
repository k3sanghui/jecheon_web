################################################
# @FileName : /jecheon_web/app/views/adm/mem_views.py
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
from app.lib.db_function import sql_fetch, sql_query, sql_fetch_array, over_lap_tel, over_lap_email
from app.lib import common
from datetime import datetime
from app.views.auth_views import login_required

mem_tbl = "tapp_memb010"
now = datetime.now()

bp = Blueprint('mem', __name__, url_prefix='/adm/mem')


@bp.route('/list/', methods=('GET', 'POST'))
@login_required
def _list():
    sql_search = ""
    s_gubun = request.args.get('s_gubun')
    stx = request.args.get('stx')
    if stx is not None and stx != "":
        if s_gubun is not None and s_gubun != "":
            sql_search += f" and a.{s_gubun} like '%%{stx}%%'"
        else:
            sql_search += f" and (a.id_user like '%%{stx}%%' or a.ds_name like '%%{stx}%%' or a.ds_tel like '%%{stx}%%' or a.ds_email like '%%{stx}%%')"

    per_page = 10
    page, _, offset = get_page_args(per_page=per_page)
    total_sql = f"select count(*) as total from {mem_tbl} a where 1=1 and a.yn_removed = 'N' {sql_search}"
    total = sql_fetch(total_sql, )

    sql = f"SELECT * FROM {mem_tbl} a where 1=1 and a.yn_removed = 'N' {sql_search} order by a.seq_user desc limit %s offset %s;"
    sql_common = (per_page, offset)
    mem_list = sql_fetch_array(sql, sql_common)

    pagination = Pagination(
        page=page,  # 지금 우리가 보여줄 페이지는 1 또는 2, 3, 4, ... 페이지인데,
        total=total['total'],  # 총 몇 개의 포스트인지를 미리 알려주고,
        per_page=per_page,  # 한 페이지당 몇 개의 포스트를 보여줄지 알려주고,
        prev_label="이전",  # 전 페이지와,
        next_label="다음",  # 후 페이지로 가는 링크의 버튼 모양을 알려주고,
        format_total=True,  # 총 몇 개의 포스트 중 몇 개의 포스트를 보여주고있는지 시각화,
    )
    return render_template('adm/mem/mem_list.html', mem_list=mem_list, total=total['total'], pagination=pagination, search=True,
                           bs_version=5, search_list=request.args)


@bp.route('/ins/', methods=('GET', 'POST'))
@login_required
def ins():
    ip = common.get_ip()
    form = AdmMemForm()
    if request.method == 'POST' and form.validate_on_submit():
        id_user = form.id_user.data
        ds_name = form.ds_name.data
        ds_password = ""
        if form.ds_password.data != form.ds_password_check.data:
            error = "비밀번호를 확인해 주시길 바랍니다."
            flash(error)
        else:
            if form.ds_password.data != "":
                ds_password = generate_password_hash(form.ds_password.data)
            else:
                error = "비밀번호는 필수 입력입니다."
                flash(error)

        ds_tel = form.ds_tel.data
        ds_email = form.ds_email.data
        no_level = form.no_level.data
        yn_emailcertify = form.yn_emailcertify.data

        hp_chk = common.hp_number_chk(ds_tel)
        if hp_chk == "Y":
            error = "잘못된 연락처 입니다."
            flash(error)
        else:
            chk_tel = common.hyphen_hp_number(ds_tel)
            error = over_lap_tel(chk_tel)
            if error is not None:
                flash(error)

        email_chk = common.email_chk(ds_email)
        if not email_chk:
            error = "유효하지 않은 이메일 주소입니다."
            flash(error)
        else:
            error = over_lap_email(ds_email)
            if error is not None:
                flash(error)

        if error is None:
            ds_tel = common.hyphen_hp_number(ds_tel)
            sql = f"INSERT INTO {mem_tbl} " \
                  "(id_user, ds_name, ds_password, ds_tel, ds_email, no_level, yn_emailcertify, id_create, dt_create, ip_create) " \
                  "VALUES " \
                  "(%s, %s, %s, %s, %s, %s, %s) RETURNING seq_user;"
            sql_common = (id_user, ds_name, ds_password, ds_tel, ds_email, no_level, yn_emailcertify, g.user['id_user'], now, ip)
            seq_user = sql_query(sql, sql_common)
            if seq_user:
                return redirect(url_for('mem._list'))
    return render_template('adm/mem/mem_form.html', form=form)


@bp.route('/view/<int:seq_user>/', methods=('GET', 'POST'))
@login_required
def view(seq_user):
    sql = f"SELECT * FROM {mem_tbl} a where 1=1 and a.yn_removed = 'N' and a.seq_user = %s;"
    sql_common = (seq_user,)
    data = sql_fetch(sql, sql_common)
    return render_template('adm/mem/mem_view.html', mem=data)


@bp.route('/mod/<int:seq_user>', methods=('GET', 'POST'))
@login_required
def mod(seq_user):
    error = None
    ip = common.get_ip()
    form = AdmMemForm()
    if request.method == 'POST' and form.validate_on_submit():
        ds_password = ""
        if len(form.ds_password.data) == 0:
            ds_password = generate_password_hash(form.ds_password.data)
        elif len(form.ds_password.data) >= 8:
            if form.ds_password.data != form.ds_password_check.data:
                error = "비밀번호를 확인해 주시길 바랍니다."
            else:
                ds_password = generate_password_hash(form.ds_password.data)
        else:
            error = "비밀번호를 8글자 이상 입력 하시길 바랍니다."

        if ds_password != "":
            hp_chk = common.hp_number_chk(form.ds_tel.data)
            if hp_chk == "Y":
                error = "잘못된 연락처 입니다."
            else:
                chk_tel = common.hyphen_hp_number(form.ds_tel.data)
                chk_data = over_lap_tel(chk_tel, form.id_user.data)
                if chk_data is not None:
                    error = chk_data
                else:
                    error = None
            if error is None:
                email_chk = common.email_chk(form.ds_email.data)
                if not email_chk:
                    error = "유효하지 않은 이메일 주소입니다."
                else:
                    chk_data = over_lap_email(form.ds_email.data, form.id_user.data)
                    if chk_data is not None:
                        error = chk_data
                    else:
                        error = None
        if error is None:
            ori_sql = f"select * from {mem_tbl} where seq_user = %s"
            ori_common = (seq_user,)
            ori_data = sql_fetch(ori_sql, ori_common)
            ds_tel = common.hyphen_hp_number(form.ds_tel.data)
            sql = f"update {mem_tbl} set ds_name = %s, ds_tel = %s, ds_email = %s, no_level = %s, yn_emailcertify = %s, ds_bigo = %s"
            sql_common = [form.ds_name.data, ds_tel, form.ds_email.data, form.no_level.data, form.yn_emailcertify.data,
                          form.ds_bigo.data, ]
            if ds_password != "":
                sql = sql + ", ds_password = %s"
                sql_common.append(ds_password, )
            if ori_data['yn_withraw'] != form.yn_withraw.data:
                sql = sql + ", yn_withraw = %s, dt_withraw = %s"
                sql_common.extend([form.yn_withraw.data, now])
            sql = sql + ", id_update = %s, dt_update = %s, ip_update = %s where seq_user = %s RETURNING seq_user;"
            sql_common.extend([g.user['id_user'], now, ip, seq_user])
            seq_user = sql_query(sql, sql_common)
            if seq_user:
                return redirect(url_for('mem.view', seq_user=seq_user))
        flash(error)
    else:  # GET 요청
        sql = f"select * from {mem_tbl} a where a.seq_user = %s"
        sql_common = (seq_user,)
        data = sql_fetch(sql, sql_common)

        form.id_user.data = data['id_user']
        form.ds_name.data = data['ds_name']
        form.ds_password.data = ""
        form.ds_tel.data = data['ds_tel']
        form.ds_email.data = data['ds_email']
        form.no_level.data = data['no_level']
        form.yn_withraw.data = data['yn_withraw']
        form.yn_emailcertify.data = data['yn_emailcertify']

    return render_template('adm/mem/mem_form.html', form=form, seq_user=seq_user)

@bp.route('/del/<int:seq_user>')
@login_required
def _del(seq_user):
    ip = common.get_ip()
    sql = "update " + mem_tbl + " set yn_removed = 'Y', " \
                                 " id_update = %s, " \
                                 " dt_update = %s, " \
                                 " ip_update = %s " \
                                 " where seq_user = %s RETURNING seq_user;"
    sql_common = (g.user['id_user'], now, ip, seq_user,)
    data = sql_query(sql, sql_common)
    return redirect(url_for('mem._list'))


@bp.route('/overlap/', methods=('GET', 'POST'))
@login_required
def over_lap():
    msg = None
    result = "fail"
    if request.method == 'POST':
        id_user = request.form['id_user']
        if id_user:
            sql = f"SELECT a.id_user FROM {mem_tbl} a where a.id_user = %s"
            sql_common = (id_user,)
            data = sql_fetch(sql, sql_common)
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
