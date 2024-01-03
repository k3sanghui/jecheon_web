################################################
# @FileName : /jecheon_web/app/lib/common.py
# @Project : 제천(전광판) 주민참여 프로그램
# @Date : 2023-08-11
# @author : 김상희
# @History :
# 2023-08-11|김상희|최초작성
# @Description : 공통 함수 및 사용자 함수 정의
################################################
import base64
import math
import os
import re
import sys
import smtplib
import fleep as fleep
from random import randint
from flask import request, render_template
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ALLOWED_FILE_TYPE_MAPPING = {
    'pdf': 'application/pdf',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
}
ALLOWED_EXTENSIONS = set(ALLOWED_FILE_TYPE_MAPPING.keys())
ALLOWED_MIME_TYPES = set(ALLOWED_FILE_TYPE_MAPPING.values())


# 전화번호 유효성 체크
def hp_number_chk(hp):
    err = None
    phone_regex = re.compile('^(01)\d{1}\d{3,4}\d{4}$')
    phone_validation = phone_regex.search(re.sub("\s|-", '', hp))
    if not phone_validation:
        err = "Y"
    return err


# 전화번호의 숫자만 취한 후 중간에 하이픈(-)을 넣는다.
def hyphen_hp_number(hp):
    str_hp = hp.replace('-', '')
    return re.sub('(\d{3})(\d{4})(\d{4})', r'\1-\2-\3', str_hp)


# 이메일 유효성 체크
def email_chk(email):
    reg = "^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$"
    return bool(re.match(reg, email))

# ip 조회
def get_ip():
    return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)


# 현재시간 조회
def now_date():
    now = datetime.now()
    str_now = now.strftime('%Y-%m-%d %H:%M:%S')
    return str_now


# 권한 select box 생성
def get_level_select():
    html = "<select id='no_level' name='no_level' title='권한'>"
    i = 1
    for i in range(11):
        html += "<option value='{i}'>{i}</a>"
    return html


# 신청상태 select box 생성
def get_stat_select():
    html = "<select id='ty_stat' name='ty_stat' title='신청상태'>"
    return html


# 메일발송
def send_mail(to, otp):
    result = {"code": 500}
    try:
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        # 임시로 개인계정 키 사용
        smtp.login('k3sanghee@gmail.com', 'gayaixcqanqgnatc') 

        msg = MIMEMultipart()
        msg['Subject'] = '[제천시 대시민서비스] 이메일 인증번호 발송'
        msg['To'] = to
        contt = MIMEText(f"인증번호를 입력하여 이메일 인증을 완료해 주세요.\n인증번호 : {otp}")
        msg.attach(contt)

        smtp.sendmail('k3sanghee@gmail.com', to, msg.as_string().encode('utf-8'))
        smtp.quit()

        result['code'] = 200
    except BaseException as e:
        print(e)
    return result


# 인증번호 생성
def generate_otp(email_address, otp_create_time):
    otp = str(randint(100000, 999999))
    from flask import session
    session[f'otp_{email_address}'] = otp  # 세션에 인증번호 저장
    session[f'time_{email_address}'] = otp_create_time  # 인증번호 생성 시간 저장

    return otp


# 이미지 base64 변환
def base64_encode(img_path):
    with open(img_path, 'rb') as img:
        base64_str = f"data:image/jpeg;base64,{base64.b64encode(img.read())}"
    return base64_str


# 문자열 일시 형식 변환 ex) 202309111110 -> 2023-09-11 11:11:10
# 2023 10 26 17 36 38
def date_conversion(str_date):
    cv_date = str_date[:4] + "-" + str_date[4:6] + "-" + str_date[6:8] + " " + str_date[8:10] + ":" + str_date[10:12]
    return cv_date


# 폴더 생성
def create_dir(path):
    try:
        os.mkdir(path)
        print(f"dir : {path}")
    except Exception as e:
        print(f"Error create dir : {e}")


def root_path():
    # Infer the root path from the run file in the project root (e.g. manage.py)
    fn = getattr(sys.modules['__main__'], '__file__')
    root_path = os.path.abspath(os.path.dirname(fn))
    return root_path


def allowed_mime(mime_type):
    return len(set(mime_type).intersection(ALLOWED_MIME_TYPES)) == len(mime_type)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 첨부파일 정보 추출
def file_info(file):
    data = {"code": 400, "file_size": 0, "file_width": 0, "file_height": 0, "file_type": None}
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    if os.path.isfile(file):
        file_size = os.path.getsize(file)
        i = int(math.floor(math.log(file_size, 1024)))
        p = math.pow(1024, i)
        s = round(file_size / p, 2)
        info_data = os.stat(file)
        with open(file, "rb") as file:
            info = fleep.get(file.read(128))
            mime_type = info.mime
        if mime_type and allowed_mime(mime_type):
            data['code'] = 200
            data['file_type'] = mime_type[0]
            data['file_size'] = info_data.st_size
        else:
            os.remove(file)
    return data

# SSTI 공격 제한
def ssti_check(txt):
    if re.search('[-=+,#/\?:^$.@*\"※~&%·!』\\´\(\)\[\]<\>`\'…》{}]', txt):
        return render_template('error.html'), 403
