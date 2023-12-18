################################################
# @FileName : /jecheon_web/app/lib/user_funtion.py
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
