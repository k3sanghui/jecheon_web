from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email

# 회원가입
class AdmMemForm(FlaskForm):
    seq_user = IntegerField('번호')
    id_user = StringField('아이디', validators=[DataRequired(), Length(min=3, max=25)])
    ds_name = StringField('이름', validators=[DataRequired(), Length(min=3, max=25)])
    ds_password = PasswordField('비밀번호', validators=[DataRequired('비밀번호는 필수 입력입니다.'), EqualTo('ds_password_check', '비밀번호가 일치하지 않습니다')])
    ds_password_check = PasswordField('비밀번호확인', validators=[DataRequired('비밀번호확인은 필수 입력입니다.')])
    ds_tel = StringField('연락처', validators=[DataRequired()])
    ds_email = EmailField('이메일', validators=[DataRequired(), Email()])
    no_level = IntegerField('권한')
    yn_emailcertify = StringField('이메일인증여부')
    ds_bigo = StringField('비고')
