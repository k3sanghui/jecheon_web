################################################
# @FileName : /jecheon_web/app/user_app/views/user_info/user_info_views.py
# @Project : 제천(전광판) 주민참여 프로그램
# @Date : 2023-08-17
# @author : 김상희
# @History :
# 2023-12-20|김상희|최초작성
# @Description : 회원정보수정
################################################
import time
from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify, Flask
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect

from app.forms.auth_forms import UserUpdateForm, UserInfoPassChk
from app.lib import common
from app.lib.common import generate_otp, send_mail
from app.lib.db_function import sql_fetch, sql_fetch_array, sql_query
from datetime import datetime
from app.views.auth_views import login_required
from config import FROM_MAIL

mem_tbl = "tapp_memb010"
now = datetime.now()

bp = Blueprint('user_info', __name__, url_prefix='/user_info')
@bp.route('/info/', methods=('GET', 'POST'))
@login_required
def info():
    form = UserInfoPassChk()
    if request.method == 'POST' and form.validate_on_submit():
        ds_password = form.ds_password.data
        if ds_password:
            sql=f"select a.seq_user, a.id_user, a.ds_password from {mem_tbl} a where a.id_user = %s and a.yn_withraw='N' and a.yn_removed='N'"
            sql_common=(session['id_user'],)
            user=sql_fetch(sql, sql_common)

            if not check_password_hash(user['ds_password'], ds_password):
                flash("현재 비밀번호가 맞지 않습니다.")
            else:
                return redirect(url_for('user_info.mod'))
        else:
            flash("현재 비밀번호를 입력하세요.")
    return render_template('user_info/user_info_passchk.html', form=form)

@bp.route('/mod/', methods=('GET', 'POST'))
@login_required
def mod():
    error = None
    ip = common.get_ip()
    form = UserUpdateForm()
    if request.method == 'POST' and form.validate_on_submit():
        ds_password = ""
        if form.ds_password.data != form.ds_password_check.data:
            error = "변경할 비밀번호를 확인해 주시길 바랍니다."
            flash(error)
        else:
            if form.ds_password.data != "":
                ds_password = generate_password_hash(form.ds_password.data)
        ds_tel = form.ds_tel.data
        ds_email = form.ds_email.data
        yn_emailcertify = form.yn_emailcertify.data
        seq_certify = form.seq_certify.data
        no_codenum = form.no_codenum.data

        chk_tel = common.hyphen_hp_number(ds_tel)
        if session['ds_tel'] != chk_tel:
            hp_chk = common.hp_number_chk(ds_tel)
            if hp_chk == "Y":
                error = "연락처 형식이 올바르지 않습니다."
                flash(error)

        if session['ds_email'] != ds_email:
            if yn_emailcertify =="N":
                error = "이메일 인증을 진행 하시길 바랍니다."
                flash(error)
            else:
                session_otp = session.get(f'otp_{ds_email}')  # 세션에 저장된 인증번호 가져오기
                session_time = session.get(f'time_{ds_email}')  # 세션에 저장된 생성 시간 가져오기

                # 세션에 인증번호와 생성 시간이 저장되어 있지 않은 경우
                if not session_otp or not session_time:
                    error = "인증정보가 존재하지 않습니다."
                    flash(error)

                # 시간이 만료된 경우
                if time.time() - session_time > 180:
                    # 세션에서 인증번호와 생성 시간을 삭제
                    session.pop(f'otp_{ds_email}')
                    session.pop(f'time_{ds_email}')
                    error = "인증번호 인증 시간이 만료 되었습니다."
                    flash(error)

                if no_codenum == session_otp:
                    # 세션에서 인증번호와 생성 시간을 삭제
                    session.pop(f'otp_{ds_email}')
                    session.pop(f'time_{ds_email}')

        if error is None:
            if yn_emailcertify:
                certify_sql = "update tapp_mail010 set dt_certify =  %s," \
                              "yn_certify = %s," \
                              "ty_certify = %s" \
                              "where seq_certify = %s RETURNING seq_certify;"
                certify_common = (now, yn_emailcertify, 'email', seq_certify)
                sql_query(certify_sql, certify_common)
            ds_tel = common.hyphen_hp_number(ds_tel)
            if ds_password == "":
                sql = f"update {mem_tbl} set ds_name = %s," \
                                          " ds_tel = %s, " \
                                          " ds_email = %s, " \
                                          " yn_emailcertify = %s, " \
                                          " id_update = %s, " \
                                          " dt_update = %s, " \
                                          " ip_update = %s " \
                                          " where seq_user = %s and yn_withraw='N' and yn_removed='N' RETURNING seq_user;"
                sql_common = (form.ds_name.data, ds_tel, form.ds_email.data,
                                  form.yn_emailcertify.data, session['id_user'], now, ip, session['seq_user'],)
            else:
                sql = f"update {mem_tbl} set ds_name = %s," \
                                          " ds_password = %s, " \
                                          " ds_tel = %s, " \
                                          " ds_email = %s, " \
                                          " yn_emailcertify = %s, " \
                                          " id_update = %s, " \
                                          " dt_update = %s, " \
                                          " ip_update = %s " \
                                          " where seq_user = %s and yn_withraw='N' and yn_removed='N' RETURNING seq_user;"
                sql_common = (form.ds_name.data, ds_password, ds_tel, form.ds_email.data,
                                  form.yn_emailcertify.data, session['id_user'], now, ip, session['seq_user'],)
            seq_user = sql_query(sql, sql_common)
            if seq_user:
                sql = "SELECT seq_user, id_user, ds_password, no_level, ds_email, ds_tel FROM tapp_memb010 where id_user = %s and yn_withraw='N' and yn_removed='N'"
                sql_common = (session['id_user'],)
                user = sql_fetch(sql, sql_common)

                if not user:
                    error = "존재하지 않는 사용자입니다."
                if error is None:
                    session.clear()
                    session['seq_user'] = user['seq_user']
                    session['id_user'] = user['id_user']
                    session['no_level'] = user['no_level']
                    session['ds_email'] = user['ds_email']
                    session['ds_tel'] = user['ds_tel']
        else:
            error = "비정상적인 동작입니다."
            flash(error)
        return redirect(url_for('user_app._list'))
    else:
        sql=f"select * from {mem_tbl} a where a.id_user=%s and a.yn_withraw='N' and a.yn_removed='N'"
        sql_common=(session['id_user'],)
        data=sql_fetch(sql, sql_common)

        form.seq_user.data = data['seq_user']
        form.id_user.data = data['id_user']
        form.ds_name.data = data['ds_name']
        form.ds_password.data = ""
        form.ds_tel.data = data['ds_tel']
        form.ds_email.data = data['ds_email']
        form.yn_emailcertify.data = data['yn_emailcertify']

    return render_template('user_info/user_info_form.html', form=form)

@bp.route('/withraw/<int:seq_user>')
@login_required
def withraw(seq_user):
    ip = common.get_ip()
    sql = "update " + mem_tbl + " set yn_withraw = 'Y', " \
                                " dt_withraw = %s, " \
                                " id_update = %s, " \
                                " dt_update = %s, " \
                                " ip_update = %s " \
                                " where seq_user = %s RETURNING seq_user;"

    sql_common = (now, g.user['id_user'], now, ip, seq_user,)
    data = sql_query(sql, sql_common)
    if data:
        session.clear()
        session['no_level'] = 1
        return redirect(url_for('auth.login'))

@bp.route('/sendOtp/', methods=('GET', 'POST'))
def send_otp():
    result = {"code": 500, "msg": ""}
    ip = common.get_ip()
    if request.method == 'POST':
        id_user = request.form['id_user']
        ds_email = request.form['ds_email']
        ty_menu = request.form['ds_email']

        otp_create_time = time.time()

        over_lap_sql = "select count(*) as cnt from tapp_memb010 where ds_email = %s"
        over_lap_common = (ds_email,)
        data = sql_fetch(over_lap_sql, over_lap_common)
        if data['cnt'] > 0:
            result['msg'] = "이미 가입된 이메일 입니다."
        else:
            # 인증 코드 생성 함수 호출
            otp = generate_otp(ds_email, otp_create_time)
            # SMTP 함수 호출
            send_result = send_mail(ds_email, otp)

            if send_result['code'] == 200:
                opt_sql = "insert into tapp_mail010 " \
                          "(ty_menu, ds_from, ds_to, no_codenum, id_create, dt_create, ip_create)" \
                          "VALUES " \
                          "(%s, %s, %s, %s, %s, %s, %s) RETURNING seq_certify;"
                opt_common = ('singup', FROM_MAIL, ds_email, otp, id_user, now, ip)
                seq_certify = sql_query(opt_sql, opt_common)
                if seq_certify:
                    result['seq_certify'] = seq_certify
                result['code'] = 200
                result['msg'] = "메일이 발송 되었습니다."
            else:
                result['msg'] = "메일 전송에 실패 하였습니다.\n잠시 후 다시 시도해 주시길 바랍니다."

    return jsonify(result)

