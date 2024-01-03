################################################
# @FileName : /jecheon_web/app/views/cmm/notice_views.py
# @Project : 제천(전광판) 주민참여 프로그램
# @Date : 2023-08-17
# @author : 김상희
# @History :
# 2023-08-17|김상희|최초작성
# @Description : 공지사항
################################################
import os.path

from flask import Blueprint, url_for, render_template, flash, request, g, send_file
from flask_paginate import Pagination, get_page_args
from werkzeug.utils import redirect, secure_filename
from app.forms.notice_forms import NoticeForm
from app.lib.common import file_info, allowed_file
from app.lib.db_function import sql_query, sql_fetch, sql_fetch_array
from app.lib import common
from datetime import datetime
from app.views.auth_views import login_required
from config import ROOT_PATH, UPLOAD_FOLDER

noti_tbl = "tapp_noti010"
file_tbl = "tapp_file010"
now = datetime.now()

bp = Blueprint('notice', __name__, url_prefix='/cmm/notice')


@bp.route('/list/', methods=('GET', 'POST'))
def _list():
    sql_search = ""
    s_gubun = request.args.get('s_gubun')
    stx = request.args.get('stx')
    if stx is not None and stx != "":
        if s_gubun is not None and s_gubun != "":
            sql_search += f" and a.{s_gubun} like '%%{stx}%%'"
        else:
            sql_search += f" and (a.ds_subject like '%%{stx}%%' or a.ds_content like '%%{stx}%%' )"
    per_page = 10
    page, _, offset = get_page_args(per_page=per_page)
    total_sql = f"select count(*) as total from {noti_tbl} a where 1=1 and a.yn_removed = 'N' {sql_search}"
    total = sql_fetch(total_sql)

    sql = f"SELECT a.*, (select ds_name from tapp_memb010 where id_user=a.id_create) as ds_name FROM {noti_tbl} a where 1=1 and a.yn_removed = 'N' {sql_search} order by a.seq_noti desc limit %s offset %s;"
    sql_common = (per_page, offset)
    notice_list = sql_fetch_array(sql, sql_common)

    pagination = Pagination(
        page=page,  # 지금 우리가 보여줄 페이지는 1 또는 2, 3, 4, ... 페이지인데,
        total=total['total'],  # 총 몇 개의 포스트인지를 미리 알려주고,
        per_page=per_page,  # 한 페이지당 몇 개의 포스트를 보여줄지 알려주고,
        prev_label="이전",  # 전 페이지와,
        next_label="다음",  # 후 페이지로 가는 링크의 버튼 모양을 알려주고,
        format_total=True,  # 총 몇 개의 포스트 중 몇 개의 포스트를 보여주고있는지 시각화,
    )
    return render_template('cmm/notice/notice_list.html', notice_list=notice_list, total=total['total'], pagination=pagination, search=True, bs_version=5, search_list=request.args)


@bp.route('/ins/', methods=('GET', 'POST'))
@login_required
def ins():
    ip = common.get_ip()
    form = NoticeForm()
    if request.method == 'POST' and form.validate_on_submit():
        save_path = ROOT_PATH + UPLOAD_FOLDER + noti_tbl
        os.makedirs(save_path, exist_ok=True)
        os.chmod(save_path, 0o0777)
        files = request.files.getlist("file[]")

        ds_subject = form.ds_subject.data
        ds_content = form.ds_content.data

        sql = "INSERT INTO " + noti_tbl + " " \
                "(ds_subject, ds_content, id_create, dt_create, ip_create) " \
                "VALUES " \
                "(%s, %s, %s, %s, %s) RETURNING seq_noti;"
        sql_common = (ds_subject, ds_content, g.user['id_user'], now, ip)
        seq_noti = sql_query(sql, sql_common)

        if seq_noti:
            for f in files:
                if f and allowed_file(f.filename):
                    ori_name = secure_filename(f.filename)
                    ori_arr = os.path.splitext(ori_name)
                    suffix = datetime.now().timestamp()
                    ds_chafile = str(suffix).replace(".","") + ori_arr[1]
                    f.save(os.path.join(ROOT_PATH, (UPLOAD_FOLDER + noti_tbl), ori_name))
                file_info_data = file_info(ori_name)
                no_size = file_info_data['file_size']
                ty_file = file_info_data['file_type']
                seq_num = 0
                sql = "insert into " + file_tbl + " " \
                    "(ty_tbl, seq_num, seq_tbl, ds_orifile, ds_chafile, no_size, no_imgwidth, no_imgheight, ty_file, id_create, dt_create, ip_create) " \
                    "VALUES " \
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING seq_file;"
                sql_common = (
                    noti_tbl, seq_num, seq_noti, ori_name, ds_chafile, no_size, 0, 0, ty_file,
                    g.user['id_user'], now, ip)
                sql_query(sql, sql_common)
            return redirect(url_for('notice._list'))
    return render_template('cmm/notice/notice_form.html', form=form)



@bp.route('/view/<int:seq_noti>/')
def view(seq_noti):
    sql = "select *, (select ds_name from tapp_memb010 where id_user=a.id_create) as ds_name from " + noti_tbl + " a where seq_noti = %s"
    sql_common = (seq_noti,)
    data = sql_fetch(sql, sql_common)
    file_sql = "select * from " + file_tbl + " where ty_tbl = %s and seq_tbl = %s order by seq_num asc"
    sql_common = (noti_tbl, seq_noti)
    file_list = sql_fetch_array(file_sql, sql_common)

    return render_template('cmm/notice/notice_view.html', notice=data, file_list=file_list)


@bp.route('/mod/<int:seq_noti>', methods=('GET', 'POST'))
@login_required
def mod(seq_noti):
    form = NoticeForm()
    ip = common.get_ip()
    if request.method == 'POST':  # POST 요청
        if form.validate_on_submit():
            sql = "update " + noti_tbl + " set ds_subject = %s, " \
                                         " ds_content = %s," \
                                         " id_update = %s, " \
                                         " dt_update = %s, " \
                                         " ip_update = %s " \
                                         " where seq_noti = %s RETURNING seq_noti;"

            sql_common = (form.ds_subject.data, form.ds_content.data, g.user['id_user'], now, ip, seq_noti,)
            seq_noti = sql_query(sql, sql_common)
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(ROOT_PATH, (UPLOAD_FOLDER + noti_tbl), filename))

            file_sql = "select * from " + file_tbl + " where ty_tbl = %s and seq_tbl = %s order by seq_num asc"
            sql_common = (noti_tbl, seq_noti)
            file_list = sql_fetch_array(file_sql, sql_common)

            return redirect(url_for('notice.view', seq_noti=seq_noti, file_list=file_list))
    else:  # GET 요청
        sql = "select seq_noti, ds_subject, ds_content from " + noti_tbl + " where seq_noti = %s"
        sql_common = (seq_noti,)
        data = sql_fetch(sql, sql_common)

        form.seq_noti.data = data['seq_noti']
        form.ds_subject.data = data['ds_subject']
        form.ds_content.data = data['ds_content']

        file_sql = "select * from " + file_tbl + " where ty_tbl = %s and seq_tbl = %s order by seq_num asc"
        sql_common = (noti_tbl, seq_noti)
        file_list = sql_fetch_array(file_sql, sql_common)

    return render_template('cmm/notice/notice_form.html', form=form, file_list=file_list)


@bp.route('/del/<int:seq_noti>/')
@login_required
def _del(seq_noti):
    ip = common.get_ip()
    if g.user['no_level'] > 5:
        sql = "update " + noti_tbl + " set yn_removed = 'Y', " \
                                " id_update = %s, " \
                                " dt_update = %s, " \
                                " ip_update = %s " \
                                " where seq_noti = %s RETURNING seq_noti;"

        sql_common = (g.user['id_user'], now, ip, seq_noti,)
        seq_noti = sql_query(sql, sql_common)
    else:
        flash('삭제권한이 없습니다')
        return redirect(url_for('notice.mod', seq_noti=seq_noti))
    return redirect(url_for('notice._list'))


@bp.route('/download/<int:seq_file>/')
def download(seq_file):
    file_sql = "select * from " + file_tbl + " where ty_tbl = %s and seq_file = %s order by seq_num asc"
    sql_common = (noti_tbl, seq_file)
    file_data = sql_fetch(file_sql, sql_common)
    path = ROOT_PATH + UPLOAD_FOLDER + noti_tbl + "\\" + file_data['ds_chafile']
    if os.path.isfile(path):
        return send_file(path, download_name=file_data['ds_orifile'], as_attachment=True)