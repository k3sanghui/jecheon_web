from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, EmailField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email

# 공지사항
class NoticeForm(FlaskForm):
    seq_noti = StringField('번호')
    ds_subject = StringField('제목', validators=[DataRequired("제목은 필수 입력입니다."), Length(min=3, max=100)])
    ds_content = StringField('내용', validators=[DataRequired("내용은 필수 입력입니다."), Length(min=3, max=1000)])
    yn_removed = StringField('삭제여부')
    id_create = StringField('생성자')
    dt_create = StringField('등록일시')
    ip_create = StringField('등록IP')
    id_update = StringField('수정자')
    dt_update = StringField('수정일시')
    ip_update = StringField('수정IP')