"""
対応履歴記録機能
ishokuフォルダー用に移植されたinsert_taio_record関数
"""
import sys
import os

# ローカルモジュールをインポート
from connection import get_connection
from utils import handle_db_exception
from utils.db_utils import DBUtils


def insert_taio_record(room_number: str, building_id: str, notes: str, category: str, 
                      creator: str, updater: str, last_time_nittei=None, connection=None) -> dict:
    """
    tTaioF（対応履歴）テーブルにレコードを登録する
    TaioCDは最新値+1で採番する
    
    Args:
        room_number: 部屋番号
        building_id: 物件ID
        notes: 対応内容
        category: カテゴリ
        creator: 作成者
        updater: 更新者
        last_time_nittei: 最終日時
        connection: データベース接続
        
    Returns:
        dict: 登録結果
    """
    close_conn = False
    if connection is None:
        connection = get_connection()
        close_conn = True
    
    try:
        print(f"[insert_taio_record] params: room_number={room_number}, building_id={building_id}, notes={notes}, category={category}, creator={creator}, updater={updater}, last_time_nittei={last_time_nittei}")
        
        # TaioCDの最新値を取得し+1
        row = DBUtils.execute_single_query(connection, "SELECT MAX(TaioCD) AS max_taio_cd FROM tTaioF", None)
        new_taio_cd = (row["max_taio_cd"] or 0) + 1
        
        sql = """
            INSERT INTO tTaioF (
                TaioCD, ClientCD, UserCD, Category, TaioNotes, LastTimeNittei, Creator, Updater, Created, Updated
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            )
        """
        last_time_value = last_time_nittei if last_time_nittei and str(last_time_nittei).strip() else None
        print(f"[insert_taio_record] LastTimeNittei処理: 元の値='{last_time_nittei}', 設定値='{last_time_value}'")
        
        params = [new_taio_cd, building_id, room_number, category, notes, last_time_value, creator, updater]
        print(f"[insert_taio_record] SQL params: {params}")
        
        DBUtils.execute_update(connection, sql, tuple(params))
        print(f"[insert_taio_record] 登録完了: TaioCD={new_taio_cd}")
        
        return {"result": "ok", "TaioCD": new_taio_cd}
            
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"[insert_taio_record] 例外発生: {e}")
        return handle_db_exception(e, context_message="tTaioF登録", 
                                 input_params={"room_number": room_number, "building_id": building_id, 
                                             "notes": notes, "category": category, "creator": creator, 
                                             "updater": updater, "last_time_nittei": last_time_nittei})
    finally:
        if close_conn:
            connection.close()


if __name__ == "__main__":
    # テスト用のサンプル実行
    print("対応履歴記録機能のテスト")
    
    # 対応履歴を記録
    result = insert_taio_record(
        room_number="101",
        building_id="12345",
        notes="テスト対応履歴",
        category="|1|",
        creator="0",
        updater="0"
    )
    print(f"対応履歴記録結果: {result}")
