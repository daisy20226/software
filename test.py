import pymysql
from pymysql.cursors import DictCursor

def get_connection():
    """每次获取新连接"""
    return pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="123456",
        database="demo01",
        charset="utf8mb4",
        cursorclass=DictCursor
    )

def con_my_sql(sql_code, params=None):
    """安全执行SQL"""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql_code, params)
            conn.commit()
            return cursor
    except Exception as e:
        if conn:  # 仅在连接存在时回滚
            conn.rollback()
        raise e  # 重新抛出异常供上层处理
    finally:
        if conn and conn.open:
            conn.close()

def get_user_id(username):
    """获取用户ID（修复版）"""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM login_user WHERE username = %s", (username,))
            user = cursor.fetchone()
            return user['id'] if user else None
    finally:
        if conn and conn.open:
            conn.close()