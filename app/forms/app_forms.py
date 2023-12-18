from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, EmailField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email

# 관리자 - 신청관리
class AdmAppForm(FlaskForm):
    seq_app = StringField('번호')
    seq_user = StringField('회원번호')
    seq_elet = StringField('전광판번호')
    ds_text = StringField('신청문구', validators=[DataRequired("신청문구는 필수 입력입니다.")])
    ds_reason = StringField('신청사유', validators=[DataRequired("신청사유는 필수 입력입니다.")])
    ds_addr = StringField('설치장소')
    no_width = StringField('가로')
    no_height = StringField('세로')
    dt_start = StringField('출력시작', validators=[DataRequired("출력시작일은 필수 입력입니다.")])
    dt_end = StringField('출력종료', validators=[DataRequired("출력종료일은 필수 입력입니다.")])
    ds_real_text = StringField('적용문구', validators=[DataRequired("적용문구는 필수 입력입니다.")])
    ty_stat = StringField('신청상태')
    dt_statdate = StringField('상태변경일자')
    ds_bigo = StringField('비고')
    ds_app_name = StringField('신청자')
    ds_app_title = StringField('개소명')
    ds_app_tel = StringField('연락처')
    yn_removed = StringField('삭제여부')
    id_create = StringField('생성자')
    dt_create = StringField('생성일시')
    ip_create = StringField('생성IP')
    id_update = StringField('수정자')
    dt_update = StringField('수정일시')
    ip_update = StringField('수정IP')
    file_name = StringField('파일명')