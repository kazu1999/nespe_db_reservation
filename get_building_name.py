"""
建物名（MansionName）取得ユーティリティ
"""

from typing import Optional

from utils.db_utils import db_connection, DBUtils


@db_connection
def get_building_name(clientCD: str, connection=None) -> Optional[str]:
    """
    指定されたクライアントコード（ClientCD）に基づいて、データベースから建物名（MansionName）を取得します。

    Args:
        clientCD (str): クライアントコード。tClientMテーブルのClientCD列に対応します。

    Returns:
        Optional[str]: クライアントに関連付けられた建物名（MansionName）。
                        クライアントコードが見つからない場合、もしくはエラー時は None。

    注意:
        - 本関数はプロジェクトの DB 接続デコレーター（@db_connection）を利用します。
        - 実際の接続情報は `utils/db_utils.py` 側の設定/環境変数等に従います。
        - 直接カーソルは使用せず、`DBUtils.execute_single_query` により安全に取得します。
    """
    try:
        sql = (
            """
            SELECT MansionName
            FROM tClientM
            WHERE ClientCD = %s
            LIMIT 1
            """
        )
        result = DBUtils.execute_single_query(connection, sql, (clientCD,))
        if result and result.get("MansionName"):
            return result["MansionName"]
        return None
    except Exception:
        return None


def main() -> None:
    """CLI からの簡易テスト用エントリポイント。"""
    # ClientCD: 3760
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Get MansionName by ClientCD")
    parser.add_argument("clientCD", help="tClientM.ClientCD")
    args = parser.parse_args()

    name = get_building_name(args.clientCD)
    if name:
        print(name)
        sys.exit(0)
    else:
        print("NOT FOUND")
        sys.exit(1)


if __name__ == "__main__":
    main()
