################################################
# @FileName : /jecheon_web/app/views/adm/eld_views.py
# @Project : 제천(전광판) 주민참여 프로그램
# @Date : 2023-08-14
# @author : 김상희
# @History :
# 2023-08-14|김상희|최초작성
# @Description : 관리자 전광판관리
################################################
from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify, Flask
from flask_paginate import Pagination, get_page_args
from werkzeug.utils import redirect
from app.forms.eld_forms import EldForm
from app.lib.db_function import sql_fetch, sql_fetch_array, sql_query
from app.module import dbModule
from app.lib import common
from datetime import datetime

from app.views.auth_views import login_required

tbl = "tapp_elet010"
now = datetime.now()

bp = Blueprint('eld', __name__, url_prefix='/adm/eld')


@bp.route('/list/', methods=('GET', 'POST'))
@login_required
def _list():
    sql_search = ""
    s_ty_gubun = request.args.get('s_ty_gubun')
    s_gubun = request.args.get('s_gubun')
    stx = request.args.get('stx')
    if s_ty_gubun is not None and s_ty_gubun != "":
        sql_search += f" and a.ty_gubun = '{s_ty_gubun}'"
    if stx is not None and stx != "":
        if s_gubun is not None and s_gubun != "":
            sql_search += f" and {s_gubun} like '%%{stx}%%'"
        else:
            sql_search += f" and (a.id_settop like '%%{stx}%%' or a.ds_title like '%%{stx}%%' or a.ds_addr like '%%{stx}%%' )"

    per_page = 10
    page, _, offset = get_page_args(per_page=per_page)
    total_sql = "select count(*) as total from " + tbl + " a where 1=1 and a.yn_removed = 'N'" + sql_search
    total = sql_fetch(total_sql)

    sql = "SELECT a.*, " \
          "(select ds_name from tapp_memb010 where id_user=a.id_create) as ds_name " \
          "FROM " + tbl + " a " \
                          "where 1=1" \
                          f" {sql_search} " \
                          "and a.yn_removed = 'N' " \
                          "order by a.seq_elet desc limit {} offset {};".format(per_page, offset)

    eld_list = sql_fetch_array(sql, )

    ty_gubun_list = get_gubun_select()
    pagination = Pagination(
        page=page,  # 지금 우리가 보여줄 페이지는 1 또는 2, 3, 4, ... 페이지인데,
        total=total['total'],  # 총 몇 개의 포스트인지를 미리 알려주고,
        per_page=per_page,  # 한 페이지당 몇 개의 포스트를 보여줄지 알려주고,
        prev_label="이전",  # 전 페이지와,
        next_label="다음",  # 후 페이지로 가는 링크의 버튼 모양을 알려주고,
        format_total=True,  # 총 몇 개의 포스트 중 몇 개의 포스트를 보여주고있는지 시각화,
    )
    return render_template('adm/eld/eld_list.html', eld_list=eld_list, total=total['total'], pagination=pagination, search=True, bs_version=5, ty_gubun_list=ty_gubun_list, search_list=request.args)


@bp.route('/view/<int:seq_elet>/')
@login_required
def view(seq_elet):
    sql = "select seq_elet, id_settop, ty_gubun, ds_title, ds_addr, no_width, no_height, ds_bigo from " + tbl + " where seq_elet = %s"
    sql_common = (seq_elet,)
    data = sql_fetch(sql, sql_common)

    return render_template('adm/eld/eld_view.html', eld=data)


@bp.route('/ins/', methods=('GET', 'POST'))
@login_required
def ins():
    error = None
    ip = common.get_ip()
    form = EldForm()
    if request.method == 'POST' and form.validate_on_submit():
        id_settop = form.id_settop.data
        ty_gubun = form.ty_gubun.data
        ds_title = form.ds_title.data
        ds_addr = form.ds_addr.data
        no_width = form.no_width.data
        no_height = form.no_height.data
        ds_bigo = form.ds_bigo.data

        over_lap_sql = "select count(*) as cnt from " + tbl + " where id_settop = %s"
        sql_common = (id_settop,)
        data = sql_fetch(over_lap_sql, sql_common)

        if data['cnt'] > 0:
            error = "동일한 셋탑ID가 존재합니다."

        if error is None:
            sql = "INSERT INTO " + tbl + " " \
                                         "(id_settop, ty_gubun, ds_title, ds_addr, no_width, no_height, ds_bigo, id_create, dt_create, ip_create) " \
                                         "VALUES " \
                                         "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING seq_elet;"
            sql_common = (
                id_settop, ty_gubun, ds_title, ds_addr, no_width, no_height, ds_bigo, g.user['id_user'], now, ip)
            seq_elet = sql_query(sql, sql_common)
            if seq_elet:
                return redirect(url_for('eld._list'))
        flash(error)
    return render_template('adm/eld/eld_form.html', form=form)


@bp.route('/mod/<int:seq_elet>', methods=('GET', 'POST'))
@login_required
def mod(seq_elet):
    ip = common.get_ip()
    if request.method == 'POST':  # POST 요청
        form = EldForm()
        if form.validate_on_submit():
            sql = "update " + tbl + " set ds_title = %s, " \
                                    " ds_addr = %s," \
                                    " no_width = %s," \
                                    " no_height = %s," \
                                    " ds_bigo = %s" \
                                    " id_update = %s, " \
                                    " dt_update = %s, " \
                                    " ip_update = %s " \
                                    " where seq_elet = %s RETURNING seq_elet;"

            sql_common = (
                form.ds_title.data, form.ds_addr.data, form.no_width.data, form.no_height.data, form.ds_bigo.data,
                g.user['id_user'], now, ip, seq_elet,)
            seq_elet = sql_query(sql, sql_common)
            return redirect(url_for('eld.view', seq_elet=seq_elet))
    else:  # GET 요청
        form = EldForm()
        sql = "select seq_elet, id_settop, ty_gubun, ds_title, ds_addr, no_width, no_height, ds_bigo from " + tbl + " where seq_elet = %s"
        sql_common = (seq_elet,)
        data = sql_fetch(sql, sql_common)
        form.seq_elet.data = data['seq_elet']
        form.id_settop.data = data['id_settop']
        form.ty_gubun.data = data['ty_gubun']
        form.ds_title.data = data['ds_title']
        form.ds_addr.data = data['ds_addr']
        form.no_width.data = data['no_width']
        form.no_height.data = data['no_height']
        form.ds_bigo.data = data['ds_bigo']

    return render_template('adm/eld/eld_form.html', form=form)


@bp.route('/del/<int:seq_elet>')
@login_required
def _del(seq_elet):
    ip = common.get_ip()
    sql = "update " + tbl + " set yn_removed = 'Y', " \
                            " id_update = %s, " \
                            " dt_update = %s, " \
                            " ip_update = %s " \
                            " where seq_elet = %s RETURNING seq_elet;"

    sql_common = (g.user['id_user'], now, ip, seq_elet,)
    data = sql_query(sql, sql_common)
    return redirect(url_for('eld._list'))


# 전광판 구분 조회
def get_gubun_select():
    sql = "select ty_gubun from " + tbl + " where yn_removed ='N' order by ty_gubun asc"
    ret = sql_fetch_array(sql, )
    return ret
