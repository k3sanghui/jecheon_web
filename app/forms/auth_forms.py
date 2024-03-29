from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email


# 회원가입
class UserCreateForm(FlaskForm):
    id_user = StringField('아이디', validators=[DataRequired('아이디는 필수 입력입니다.'), Length(min=3, max=25)])
    ds_name = StringField('이름', validators=[DataRequired('이름은 필수 입력입니다.'), Length(min=3, max=25)])
    ds_password = PasswordField('비밀번호', validators=[DataRequired('비밀번호는 필수 입력입니다.'), EqualTo('ds_password_check', '비밀번호가 일치하지 않습니다')])
    ds_password_check = PasswordField('비밀번호확인', validators=[DataRequired('비밀번호확인은 필수 입력입니다.')])
    ds_tel = StringField('연락처', validators=[DataRequired('연락처는 필수 입력입니다.')])
    ds_email = EmailField('이메일', validators=[DataRequired('이메일은 필수입력입니다.'), Email()])
    no_level = IntegerField('권한')
    yn_emailcertify = StringField('이메일인증여부')
    seq_certify = StringField('이메일인증')
    no_codenum = StringField('이메일인증번호')

# 로그인
class UserLoginForm(FlaskForm):
    id_user = StringField('아이디', validators=[DataRequired('아이디는 필수 입력입니다.'), Length(min=3, max=25)])
    ds_password = PasswordField('비밀번호', validators=[DataRequired('비밀번호는 필수 입력입니다.')])

# 정보수정 - 현재비밀번호 확인
class UserInfoPassChk(FlaskForm):
    ds_password = StringField('현재비밀번호' , validators=[DataRequired("현재 비밀번호 입력은 필수 입니다.")])

# 회원정보수정
class UserUpdateForm(FlaskForm):
    seq_user = StringField('회원SEQ')
    id_user = StringField('아이디', validators=[DataRequired('아이디는 필수 입력입니다.'), Length(min=3, max=25)])
    ds_name = StringField('이름', validators=[DataRequired('이름은 필수 입력입니다.'), Length(min=3, max=25)])
    ds_password = PasswordField('비밀번호')
    ds_password_check = PasswordField('비밀번호확인')
    ds_tel = StringField('연락처', validators=[DataRequired('연락처는 필수 입력입니다.')])
    ds_email = EmailField('이메일', validators=[DataRequired('이메일은 필수입력입니다.'), Email()])
    yn_emailcertify = StringField('이메일인증여부')
    seq_certify = StringField('이메일인증')
    no_codenum = StringField('이메일인증번호')

# 아이디 / 비밀번호 찾기
class UserFindForm(FlaskForm):
    id_user = StringField('아이디')
    ds_name = StringField('이름')
    ds_password = PasswordField('비밀번호')
    ds_password_check = PasswordField('비밀번호확인')
    ds_email = EmailField('이메일', validators=[DataRequired('이메일은 필수입력입니다.'), Email()])
    yn_emailcertify = StringField('이메일인증여부')
    seq_certify = StringField('이메일인증')
    no_codenum = StringField('이메일인증번호')


# 아이디 찾기 조회
class UserIdFindForm(FlaskForm):
    id_user = StringField('아이디')
    dt_create = StringField('가입일시')


