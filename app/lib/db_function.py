################################################
# @FileName : /jecheon_web/app/lib/db_funtion.py
# @Project : 제천(전광판) 주민참여 프로그램
# @Date : 2023-08-23
# @author : 김상희
# @History :
# 2023-08-23|김상희|최초작성
# @Description : 공통 DB 조회 함수 관련
################################################
from app.module import dbModule


# 쿼리 isert, update, delete 처리
def sql_query(sql, sql_common=None):
    db_class = dbModule.Database()
    result = db_class.execute(sql, sql_common)
    db_class.commit()
    db_class.close()
    return result


# 쿼리 여러 행 조회
def sql_fetch_array(sql, sql_common=None):
    db_class = dbModule.Database()
    result = db_class.executeAll(sql, sql_common)
    db_class.close()
    return result


# 쿼리 단일 행 조회
def sql_fetch(sql, sql_common=None):
    db_class = dbModule.Database()
    result = db_class.executeOne(sql, sql_common)
    db_class.close()
    return result


# 전광판 개소명 목록 조회
def get_title_select():
    tbl = "tapp_elet010"
    db_class = dbModule.Database()
    sql = "select seq_elet, ds_title, ds_addr, no_width, no_height " \
          f"from {tbl}" \
          f" where yn_removed = 'N'" \
          f" order by seq_elet asc"
    ret = db_class.executeAll(sql, )
    db_class.close()
    return ret


# 특정 전광판 정보 조회
def get_elet_select(seq_elet):
    tbl = "tapp_elet010"
    db_class = dbModule.Database()
    sql = "select seq_elet, ds_title, ds_addr, no_width, no_height " \
          f"from {tbl}" \
          f" where yn_removed = 'N' " \
          f"and seq_elet={seq_elet} " \
          f"order by seq_elet asc"
    data = db_class.executeOne(sql, )
    db_class.close()
    return data


# 연락처 중복체크
def over_lap_tel(tel, id_user=None):
    msg = None
    tbl = "tapp_memb010"
    if id_user is None:
        sql = f"select count(*) as cnt from {tbl} where ds_tel = %s"
        sql_common = (tel,)
    else:
        sql = f"select count(*) as cnt from {tbl} where ds_tel = %s and id_user<>%s"
        sql_common = (tel, id_user,)
    data = sql_fetch(sql, sql_common)
    if data['cnt'] > 0:
        msg = "등록된 연락처 입니다."
    return msg


# 이메일 중복체크
def over_lap_email(email, id_user=None):
    msg = None
    if id_user is None:
        sql = "select count(*) as cnt from tapp_memb010 where ds_email = %s"
        sql_common = (email,)
    else:
        sql = "select count(*) as cnt from tapp_memb010 where ds_email = %s and id_user <>%s"
        sql_common = (email, id_user,)
    data = sql_fetch(sql, sql_common)
    if data['cnt'] > 0:
        msg = "이미 가입된 이메일 입니다."
    return msg
