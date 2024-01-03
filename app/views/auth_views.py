import functools
import time

from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from app.forms.auth_forms import UserLoginForm, UserCreateForm, UserFindForm
from app.lib import common
from app.lib.common import generate_otp, send_mail
from app.lib.db_function import sql_fetch, sql_query
from datetime import datetime

from config import FROM_MAIL

now = datetime.now()
mem_tbl = "tapp_memb010"
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup/', methods=('GET', 'POST'))
def signup():
    error = None
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        id_user = form.id_user.data
        ds_name = form.ds_name.data
        ds_password = generate_password_hash(form.ds_password.data)
        ds_tel = form.ds_tel.data
        ds_email = form.ds_email.data
        yn_emailcertify = form.yn_emailcertify.data
        seq_certify = form.seq_certify.data
        no_codenum = form.no_codenum.data

        session_otp = session.get(f'otp_{ds_email}')  # 세션에 저장된 인증번호 가져오기
        session_time = session.get(f'time_{ds_email}')  # 세션에 저장된 생성 시간 가져오기

        hp_chk = common.hp_number_chk(ds_tel)
        if hp_chk == "Y":
            error = "연락처 형식이 올바르지 않습니다."
            flash(error)

        email_chk = common.email_chk(ds_email)
        if not email_chk:
            error = "유효하지 않은 이메일 주소입니다."
            flash(error)

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
            certify_sql = "update tapp_mail010 set dt_certify =  %s," \
                          "yn_certify = %s," \
                          "ty_certify = %s" \
                          "where seq_certify = %s RETURNING seq_certify;"
            certify_common = (now, yn_emailcertify, 'email', seq_certify)
            certify = sql_query(certify_sql, certify_common)
            if certify:
                ds_tel = common.hyphen_hp_number(ds_tel)
                sql = "INSERT INTO tapp_memb010 " \
                      "(id_user, ds_name, ds_password, ds_tel, ds_email, no_level, yn_emailcertify) " \
                      "VALUES " \
                      "(%s, %s, %s, %s, %s, %s, %s) RETURNING seq_user;"
                sql_common = (id_user, ds_name, ds_password, ds_tel, ds_email, 2, yn_emailcertify)
                seq_user = sql_query(sql, sql_common)
                if seq_user:
                    return redirect(url_for('main.index'))
            else:
                error = "비정상적인 동작입니다."
                flash(error)
    return render_template('auth/signup.html', form=form)


@bp.route('/overlap/', methods=('GET', 'POST'))
def over_lap():
    result = "fail"
    if request.method == 'POST':
        id_user = request.form['id_user']
        if id_user:
            sql = "SELECT id_user FROM tapp_memb010 where id_user = %s"
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


@bp.route('/sendOtp/', methods=('GET', 'POST'))
def send_otp():
    result = {"code": 500, "msg": ""}
    ip = common.get_ip()
    if request.method == 'POST':
        id_user = request.form['id_user']
        ds_email = request.form['ds_email']
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

@bp.route('/login/', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        id_user = form.id_user.data
        ds_password = form.ds_password.data
        sql = "SELECT seq_user, id_user, ds_password, no_level, ds_email, ds_tel FROM tapp_memb010 where yn_withraw='N' and yn_removed='N' and id_user = %s"
        sql_common = (id_user,)
        user = sql_fetch(sql, sql_common)

        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user['ds_password'], ds_password):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            up_sql="update tapp_memb010 set dt_today = %s where id_user=%s RETURNING seq_user;"
            up_sql_common=(now, user['id_user'])
            sql_query(up_sql, up_sql_common)
            session.clear()
            session['seq_user'] = user['seq_user']
            session['id_user'] = user['id_user']
            session['no_level'] = user['no_level']
            session['ds_email'] = user['ds_email']
            session['ds_tel'] = user['ds_tel']
            _next = request.args.get('next', '')
            if _next:
                return redirect(_next)
            else:
                return redirect(url_for('main.index'))
        flash(error)
    return render_template('auth/login.html', form=form)


@bp.before_app_request
def load_logged_in_user():
    id_user = session.get('id_user')
    if id_user is None:
        g.user = None
    else:
        sql = "SELECT seq_user, id_user, ds_name, ds_tel, ds_email, no_level FROM tapp_memb010 where id_user = %s"
        sql_common = (id_user,)
        user = sql_fetch(sql, sql_common)
        g.user = user


@bp.route('/logout/')
def logout():
    session.clear()
    session['no_level']=1
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''
            return redirect(url_for('auth.login', next=_next))
        return view(*args, **kwargs)

    return wrapped_view

#이메일 인증
@bp.route('/auth_email/', methods=('GET', 'POST'))
def auth_email():
    error = None
    result = {"code": 500, "msg": ""}
    ip = common.get_ip()
    if request.method == 'POST':
        ty_menu = request.form['ty_menu']
        if ty_menu == "idfind":
            if request.form['ds_name'] or request.form['ds_email']:
                id_create = request.form['ds_name']
                ds_email = request.form['ds_email']
            else:
                error = "이름 또는 이메일은 필수 입력입니다."
        elif ty_menu == "pwdfind":
            if request.form['ds_email']:
                id_create = request.form['id_user']
                ds_email = request.form['ds_email']
            else:
                error = "이메일은 필수 입력입니다."
        email_chk = common.email_chk(ds_email)
        if not email_chk:
            error = "유효하지 않은 이메일 주소입니다."
        if error is None:
            otp_create_time = time.time()
            # 인증 코드 생성 함수 호출
            otp = generate_otp(ds_email, otp_create_time)
            # SMTP 함수 호출
            send_result = send_mail(ds_email, otp)

            if send_result['code'] == 200:
                opt_sql = "insert into tapp_mail010 " \
                          "(ty_menu, ds_from, ds_to, no_codenum, id_create, dt_create, ip_create)" \
                          "VALUES " \
                          "(%s, %s, %s, %s, %s, %s, %s) RETURNING seq_certify;"
                opt_common = (ty_menu, FROM_MAIL, ds_email, otp, id_create, now, ip)
                seq_certify = sql_query(opt_sql, opt_common)
                if seq_certify:
                    result['seq_certify'] = seq_certify
                result['code'] = 200
                result['msg'] = "메일이 발송 되었습니다."
            else:
                result['msg'] = "메일 전송에 실패 하였습니다.\n잠시 후 다시 시도해 주시길 바랍니다."
        else:
            result['msg'] = error
    return jsonify(result)


#아이디 찾기
@bp.route('/idFind/', methods=('GET', 'POST'))
def idFind():
    error = None
    ip = common.get_ip()
    form = UserFindForm()
    if request.method == 'POST' and form.validate_on_submit():
        ds_name = form.ds_name.data
        ds_email = form.ds_email.data
        yn_emailcertify = form.yn_emailcertify.data
        seq_certify = form.seq_certify.data
        no_codenum = form.no_codenum.data

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
            certify_sql = "update tapp_mail010 set dt_certify =  %s," \
                          "yn_certify = %s," \
                          "ty_certify = %s" \
                          "where seq_certify = %s RETURNING seq_certify;"
            certify_common = (now, yn_emailcertify, 'email', seq_certify)
            certify = sql_query(certify_sql, certify_common)

            if certify:
                session['info_name'] = ds_name
                session['info_email'] = ds_email
                return redirect(url_for('auth.idFindInfo'))
            else:
                session.pop('info_name')
                session.pop('info_email')

    return render_template('auth/idfind.html', form=form)

# 아이디 찾기 조회 결과
@bp.route('/idFindInfo/', methods=('GET', 'POST'))
def idFindInfo():
    if session.get('info_name') and session.get('info_email'):
        ds_name = session.get('info_name')
        ds_email = session.get('info_email')
        sql="select id_user, to_char(dt_create, 'YYYY-MM-DD') as dt_create from tapp_memb010 where ds_name= %s and ds_email= %s and yn_removed='N' and yn_withraw='N'"
        sql_common=(ds_name, ds_email)
        data=sql_fetch(sql, sql_common)

        session.pop('info_name')
        session.pop('info_email')
        return render_template('auth/idfind_info.html', data=data)
    else:
        return redirect(url_for('auth.idFind'))


#비밀번호 찾기
@bp.route('/pwdFind/', methods=('GET', 'POST'))
def pwdFind():
    error = None
    form = UserFindForm()
    if request.method == 'POST' and form.validate_on_submit():
        id_user = form.id_user.data
        ds_email = form.ds_email.data
        yn_emailcertify = form.yn_emailcertify.data
        seq_certify = form.seq_certify.data
        no_codenum = form.no_codenum.data

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
            certify_sql = "update tapp_mail010 set dt_certify =  %s," \
                          "yn_certify = %s," \
                          "ty_certify = %s" \
                          "where seq_certify = %s RETURNING seq_certify;"
            certify_common = (now, yn_emailcertify, 'email', seq_certify)
            certify = sql_query(certify_sql, certify_common)

            if certify:
                session['info_id'] = id_user
                session['info_email'] = ds_email
                return redirect(url_for('auth.pwdFindInfo'))
            else:
                session.pop('info_id')
                session.pop('info_email')

    return render_template('auth/pwdfind.html', form=form)

# 비빌번호 찾기 비밀번호 변경
@bp.route('/pwdFindInfo/', methods=('GET', 'POST'))
def pwdFindInfo():
    error = None
    ip = common.get_ip()
    form = UserFindForm()
    if request.method == 'POST'and form.validate_on_submit():
        ds_password = ""
        if form.ds_password.data == "":
            error = "비밀번호는 필수 입력 입니다."
            flash(error)

        if form.ds_password.data != form.ds_password_check.data:
            error = "변경할 비밀번호를 확인해 주시길 바랍니다."
            flash(error)
        else:
            if len(form.ds_password.data) >= 8:
                ds_password = generate_password_hash(form.ds_password.data)
            else:
                error = "비밀번호를 8글자 이상 입력하세요."
                flash(error)

        if error is None:
            sql = f"update {mem_tbl} set ds_password = %s, " \
                  " id_update = %s, " \
                  " dt_update = %s, " \
                  " ip_update = %s " \
                  " where id_user = %s and yn_withraw='N' and yn_removed='N' RETURNING seq_user;"
            sql_common = (ds_password, session['info_id'], now, ip, session['info_id'],)
            seq_user = sql_query(sql, sql_common)

            if seq_user:
                session.pop('info_id')
                session.pop('info_email')
                flash("정상적으로 비밀번호가 변경되었습니다.\n 변경 하신 비밀번호로 로그인을 하시길 바랍니다.")
    else:
        if session.get('info_id') and session.get('info_email'):
            id_user = session.get('info_id')
            ds_email = session.get('info_email')
            sql="select id_user, ds_email from tapp_memb010 where id_user= %s and ds_email= %s and yn_removed='N' and yn_withraw='N'"
            sql_common=(id_user, ds_email)
            data=sql_fetch(sql, sql_common)

            if data:
                form.ds_email.data = data['ds_email']
                flash("비밀번호 재설정 후 로그인 하시길 바랍니다.")
            else:
                flash("회원정보가 존재하지 않습니다.")
        else:
            flash("비정상적인 동작입니다.")

    return render_template('auth/pwdfind_info.html', form=form)

# 비밀번호찾기 : 아이디 확인
@bp.route('/id_find/', methods=('GET', 'POST'))
def id_find():
    result = {"code": 500, "msg": ""}
    if request.method == 'POST':
        if request.form['id_user']:
            id_user = request.form['id_user']
            sql=f"select count(*) as cnt from {mem_tbl} where id_user=%s and yn_removed='N' and yn_withraw='N'"
            sql_common=(id_user,)
            data=sql_fetch(sql, sql_common)
            if data['cnt'] > 0:
                result['code'] = 200
            else:
                result['msg'] = "입력하신 아이디가 존재하지 않습니다."
        else:
            result['msg'] = "아이디는 필수 입력 입니다."

    return jsonify(result)
