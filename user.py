from connection import get_connection
from utils import handle_db_exception
from utils.db_utils import DBUtils

def authenticate_user(room_number: str, password: str, building_id: str, connection=None) -> dict:
    close_conn = False
    if connection is None:
        connection = get_connection()
        close_conn = True
    try:
        sql = """
        SELECT UserCD AS room_number
        FROM tUserM
        WHERE UserCD = %s AND Passwd = %s AND ClientCD = %s;
        """
        result = DBUtils.execute_single_query(connection, sql, (room_number, password, building_id))
        if result:
            return result
        else:
            return {"error": "認証に失敗しました。"}
    except Exception as e:
        return handle_db_exception(e, context_message="ユーザー認証", input_params={"room_number": room_number, "building_id": building_id})
    finally:
        if close_conn:
            connection.close()


def update_user_tel(room_number: str, building_id: str, tel: str, connection=None):
    """
    tUserMのTELカラムを更新する
    """
    close_conn = False
    if connection is None:
        connection = get_connection()
        close_conn = True
    try:
        sql = "UPDATE tUserM SET TEL = %s, Updated = NOW() WHERE UserCD = %s AND ClientCD = %s"
        DBUtils.execute_update(connection, sql, (tel, room_number, building_id))
        return {"result": "ok"}
    except Exception as e:
        if connection:
            connection.rollback()
        return handle_db_exception(e, context_message="電話番号更新", input_params={})
    finally:
        if close_conn:
            connection.close()


def update_user_lastname(room_number: str, building_id: str, last_name: str, connection=None):
    """
    tUserMのLastNameカラムを更新する
    """
    close_conn = False
    if connection is None:
        connection = get_connection()
        close_conn = True
    try:
        sql = "UPDATE tUserM SET LastName = %s, Updated = NOW() WHERE UserCD = %s AND ClientCD = %s"
        DBUtils.execute_update(connection, sql, (last_name, room_number, building_id))
        return {"result": "ok"}
    except Exception as e:
        if connection:
            connection.rollback()
        return handle_db_exception(e, context_message="姓(LastName)更新", input_params={})
    finally:
        if close_conn:
            connection.close()


def set_reply_flg(room_number: str, building_id: str, flg: int = 1, connection=None):
    """
    tUserMのReplyFlgをセットする
    """
    close_conn = False
    if connection is None:
        connection = get_connection()
        close_conn = True
    try:
        sql = "UPDATE tUserM SET ReplyFlg = %s, Updated = NOW() WHERE UserCD = %s AND ClientCD = %s"
        DBUtils.execute_update(connection, sql, (flg, room_number, building_id))
        return {"result": "ok"}
    except Exception as e:
        if connection:
            connection.rollback()
        return handle_db_exception(e, context_message="ReplyFlg更新", input_params={})
    finally:
        if close_conn:
            connection.close()