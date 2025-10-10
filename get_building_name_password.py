"""
建物名（MansionName）取得ユーティリティ（認証あり版）
"""

from typing import Optional

from user import authenticate_user
from utils import handle_db_exception
from utils.db_utils import db_connection, DBUtils


@db_connection
def get_building_name(room_number: str, password: str, building_id: str, connection=None) -> dict:
    """
    ユーザー認証後、指定された ClientCD（= building_id）に対応する建物名（MansionName）を取得します。

    Args:
        room_number (str): 部屋番号（UserCD）
        password (str): パスワード
        building_id (str): 物件ID（ClientCD）

    Returns:
        dict: { "result": "ok", "mansion_name": str | null } もしくは { "error": str }
    """
    try:
        # 認証チェック
        auth_result = authenticate_user(room_number, password, building_id, connection)
        if "error" in auth_result:
            return {"error": "認証に失敗しました。部屋番号・パスワード・物件管理番号をご確認ください。"}

        # 建物名取得
        sql = (
            """
            SELECT MansionName
            FROM tClientM
            WHERE ClientCD = %s
            LIMIT 1
            """
        )
        result = DBUtils.execute_single_query(connection, sql, (building_id,))
        if result and result.get("MansionName"):
            return {"result": "ok", "mansion_name": result["MansionName"]}
        return {"result": "ok", "mansion_name": None}

    except Exception as e:
        return handle_db_exception(e, context_message="建物名取得", input_params={"building_id": building_id})


def main() -> None:
    """CLI からの簡易テスト用エントリポイント。"""
    # ClientCD: 3760
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Get MansionName by ClientCD (with auth)")
    parser.add_argument("room_number", help="tUserM.UserCD")
    parser.add_argument("password", help="tUserM.Passwd")
    parser.add_argument("building_id", help="tClientM.ClientCD")
    args = parser.parse_args()

    res = get_building_name(args.room_number, args.password, args.building_id)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
