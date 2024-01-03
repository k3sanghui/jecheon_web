from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, EmailField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email

# 전광판 관리 등록
class EldForm(FlaskForm):
    seq_elet = IntegerField('번호')
    id_settop = StringField('셋탑ID', validators=[DataRequired("셋탑ID는 필수 입력입니다."), Length(min=3, max=25)])
    ty_gubun = StringField('구분', validators=[DataRequired("구분은 필수 입력입니다."), Length(min=3, max=25)])
    ds_title = StringField('개소명', validators=[DataRequired("개소명은 필수 입력입니다."), Length(min=3, max=25)])
    ds_addr = StringField('설치장소', validators=[DataRequired("설치장소는 필수 입력입니다."), Length(min=3, max=255)])
    no_width = IntegerField('가로', validators=[DataRequired("가로는 필수 입력입니다.")])
    no_height = IntegerField('세로', validators=[DataRequired("세로는 필수 입력입니다.")])
    ds_bigo = StringField('비고')
    yn_removed = StringField('삭제여부')
    id_create = StringField('생성자')
    dt_create = StringField('등록일시')
    ip_create = StringField('등록IP')
    id_update = StringField('수정자')
    dt_update = StringField('수정일시')
    ip_update = StringField('수정IP')