"""
データベース操作関連のユーティリティ関数
"""
from functools import wraps
from chatbot_scripts.models.connection import get_connection


def db_connection(func):
    """データベース接続を自動管理するデコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        connection = kwargs.get('connection')
        close_conn = False
        
        if connection is None:
            connection = get_connection()
            close_conn = True
            kwargs['connection'] = connection
        
        try:
            return func(*args, **kwargs)
        finally:
            if close_conn and connection:
                connection.close()
    
    return wrapper


class DBUtils:
    """データベース操作関連のユーティリティクラス"""
    
    @staticmethod
    def execute_query(connection, sql, params=None):
        """クエリを実行して結果を取得"""
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()
    
    @staticmethod
    def execute_single_query(connection, sql, params=None):
        """単一結果のクエリを実行"""
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()
    
    @staticmethod
    def execute_update(connection, sql, params=None):
        """更新クエリを実行"""
        with connection.cursor() as cursor:
            cursor.execute(sql, params or ())
            connection.commit()
            return cursor.rowcount
