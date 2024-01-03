from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email

# 회원가입
class AdmMemForm(FlaskForm):
    seq_user = IntegerField('번호')
    id_user = StringField('아이디', validators=[DataRequired('아이디는 필수 입력입니다.'), Length(min=3, max=25)])
    ds_name = StringField('이름', validators=[DataRequired('이름은 필수 입력입니다.'), Length(min=3, max=25)])
    ds_password = PasswordField('비밀번호')
    ds_password_check = PasswordField('비밀번호확인')
    ds_tel = StringField('연락처', validators=[DataRequired('연락처는 필수 입력입니다.')])
    ds_email = EmailField('이메일', validators=[DataRequired('이메일은 필수 입력입니다.')])
    no_level = IntegerField('권한')
    yn_withraw = StringField('탈퇴여부')
    yn_emailcertify = StringField('이메일인증여부')
    ds_bigo = StringField('비고')
