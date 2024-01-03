################################################
# @FileName : /jecheon_app/config.py
# @Project : 제천시 대시민서비스
# @Date : 2023-08-16
# @author : 김상희
# @History :
# 2023-08-16|김상희|최초작성
# @Description : 프로젝트 기본 경로 설정 및 업로드 폴더, 기타 필요 설정
################################################
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ROOT_PATH = BASE_DIR+"jecheon_web\\app"
UPLOAD_FOLDER = "/uploads/"
#APP_EXT_URL = "http://172.16.1.75/api/set_app_extdata.php" #제천운영서버
APP_EXT_URL = "http://172.168.0.181/api/set_app_extdata.php"#로컬서버
SECRET_KEY = "dev"
FROM_MAIL = "k3sanghee@gmail.com"