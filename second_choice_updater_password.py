"""
第二希望更新機能の専用ファイル（認証あり版）
ishokuフォルダー用に移植された第二希望更新処理
"""
import sys
import os

# ローカルモジュールをインポート
from user import authenticate_user
from taio_record import insert_taio_record
from utils import handle_db_exception
from utils.db_utils import db_connection, DBUtils


class SecondChoiceUpdater:
    """第二希望更新処理を管理するクラス"""
    
    @staticmethod
    @db_connection
    def update_second_choice(room_number: str, password: str, building_id: str, 
                           second_choice_text: str, connection=None) -> dict:
        """
        第二希望を更新する
        
        Args:
            room_number: 部屋番号
            password: パスワード
            building_id: 物件ID
            second_choice_text: 第二希望のテキスト
            connection: データベース接続
            
        Returns:
            dict: 更新結果
        """
        try:
            # 1. 認証チェック
            auth_result = authenticate_user(room_number, password, building_id, connection)
            if "error" in auth_result:
                return {"error": "認証に失敗しました。部屋番号・パスワード・物件管理番号をご確認ください。"}
            
            # 2. 現在の予約情報を取得
            current_reservation = SecondChoiceUpdater._get_current_reservation(
                room_number, building_id, connection)
            if "error" in current_reservation:
                return current_reservation
            
            # 3. 第二希望テキストの検証
            validation_result = SecondChoiceUpdater._validate_second_choice_text(second_choice_text)
            if "error" in validation_result:
                return validation_result
            
            # 4. 第二希望更新実行
            update_result = SecondChoiceUpdater._execute_second_choice_update(
                room_number, building_id, second_choice_text, current_reservation["datetime"], connection)
            if "error" in update_result:
                return update_result
            
            # 5. 対応履歴登録
            SecondChoiceUpdater._log_second_choice_update(
                room_number, building_id, second_choice_text, connection)
            
            return {
                "result": "ok",
                "message": "第二希望を更新しました。",
                "reservation_date": current_reservation["datetime"],
                "second_choice": second_choice_text
            }
            
        except Exception as e:
            return handle_db_exception(e, context_message="第二希望更新", 
                                     input_params={"room_number": room_number, "building_id": building_id})
    
    @staticmethod
    def _get_current_reservation(room_number, building_id, connection):
        """現在の予約情報を取得"""
        try:
            sql = """
            SELECT TimeFrom, SecondChoice
            FROM tReservationF 
            WHERE UserCD = %s AND ClientCD = %s AND MukouFlg = 0 
            ORDER BY TimeFrom DESC LIMIT 1
            """
            result = DBUtils.execute_single_query(connection, sql, (room_number, building_id))
            
            if not result or not result.get("TimeFrom"):
                return {"error": "現在の予約情報が見つかりません。"}
            
            return {
                "datetime": result["TimeFrom"].strftime("%Y-%m-%d %H:%M"),
                "current_second_choice": result.get("SecondChoice")
            }
            
        except Exception as e:
            return {"error": f"予約情報取得エラー: {str(e)}"}
    
    @staticmethod
    def _validate_second_choice_text(second_choice_text):
        """第二希望テキストの検証"""
        try:
            if not second_choice_text or not second_choice_text.strip():
                return {"error": "第二希望の内容を入力してください。"}
            
            # 長さチェック
            if len(second_choice_text) > 500:
                return {"error": "第二希望の内容が長すぎます。500文字以内で入力してください。"}
            
            # 禁止文字チェック（必要に応じて）
            forbidden_chars = ['<', '>', '&', '"', "'"]
            for char in forbidden_chars:
                if char in second_choice_text:
                    return {"error": f"使用できない文字 '{char}' が含まれています。"}
            
            return {"valid": True, "cleaned_text": second_choice_text.strip()}
            
        except Exception as e:
            return {"error": f"第二希望テキスト検証エラー: {str(e)}"}
    
    @staticmethod
    def _execute_second_choice_update(room_number, building_id, second_choice_text, reservation_date, connection):
        """第二希望更新の実行"""
        try:
            # 第二希望を更新
            update_sql = """
            UPDATE tReservationF 
            SET SecondChoice = %s, Updated = NOW(), Updater = %s 
            WHERE TimeFrom = %s AND UserCD = %s AND ClientCD = %s
            """
            row_count = DBUtils.execute_update(connection, update_sql, (
                second_choice_text,
                room_number,
                reservation_date,
                room_number,
                building_id
            ))
            
            if row_count == 0:
                return {"error": "第二希望の更新に失敗しました。予約情報が見つかりません。"}
            
            return {"result": "ok"}
            
        except Exception as e:
            return {"error": f"第二希望更新エラー: {str(e)}"}
    
    @staticmethod
    def _log_second_choice_update(room_number, building_id, second_choice_text, connection):
        """第二希望更新履歴をログに記録"""
        try:
            # 第二希望の内容をマスク（個人情報保護）
            masked_choice = second_choice_text[:50] + "..." if len(second_choice_text) > 50 else second_choice_text
            notes = f"[AI電話第二希望更新] {masked_choice}"
            
            insert_taio_record(
                room_number=room_number,
                building_id=building_id,
                notes=notes,
                category="|2|",
                creator=0,
                updater=0,
                connection=connection
            )
        except Exception as e:
            print(f"[_log_second_choice_update] ログ記録エラー: {e}")
    
    @staticmethod
    @db_connection
    def get_current_second_choice(room_number: str, password: str, building_id: str, connection=None) -> dict:
        """
        現在の第二希望を取得
        
        Args:
            room_number: 部屋番号
            password: パスワード
            building_id: 物件ID
            connection: データベース接続
            
        Returns:
            dict: 現在の第二希望情報
        """
        try:
            # 1. 認証チェック
            auth_result = authenticate_user(room_number, password, building_id, connection)
            if "error" in auth_result:
                return {"error": "認証に失敗しました。部屋番号・パスワード・物件管理番号をご確認ください。"}
            
            # 2. 現在の予約情報を取得
            current_reservation = SecondChoiceUpdater._get_current_reservation(
                room_number, building_id, connection)
            if "error" in current_reservation:
                return current_reservation
            
            return {
                "result": "ok",
                "reservation_date": current_reservation["datetime"],
                "second_choice": current_reservation.get("current_second_choice"),
                "has_second_choice": current_reservation.get("current_second_choice") is not None
            }
            
        except Exception as e:
            return {"error": f"第二希望取得エラー: {str(e)}"}
    
    @staticmethod
    @db_connection
    def clear_second_choice(room_number: str, password: str, building_id: str, connection=None) -> dict:
        """
        第二希望をクリアする
        
        Args:
            room_number: 部屋番号
            password: パスワード
            building_id: 物件ID
            connection: データベース接続
            
        Returns:
            dict: クリア結果
        """
        try:
            # 1. 認証チェック
            auth_result = authenticate_user(room_number, password, building_id, connection)
            if "error" in auth_result:
                return {"error": "認証に失敗しました。部屋番号・パスワード・物件管理番号をご確認ください。"}
            
            # 2. 現在の予約情報を取得
            current_reservation = SecondChoiceUpdater._get_current_reservation(
                room_number, building_id, connection)
            if "error" in current_reservation:
                return current_reservation
            
            # 3. 第二希望をクリア
            clear_sql = """
            UPDATE tReservationF 
            SET SecondChoice = NULL, Updated = NOW(), Updater = %s 
            WHERE TimeFrom = %s AND UserCD = %s AND ClientCD = %s
            """
            row_count = DBUtils.execute_update(connection, clear_sql, (
                room_number,
                current_reservation["datetime"],
                room_number,
                building_id
            ))
            
            if row_count == 0:
                return {"error": "第二希望のクリアに失敗しました。予約情報が見つかりません。"}
            
            # 4. 対応履歴登録
            SecondChoiceUpdater._log_second_choice_clear(room_number, building_id, connection)
            
            return {
                "result": "ok",
                "message": "第二希望をクリアしました。",
                "reservation_date": current_reservation["datetime"]
            }
            
        except Exception as e:
            return {"error": f"第二希望クリアエラー: {str(e)}"}
    
    @staticmethod
    def _log_second_choice_clear(room_number, building_id, connection):
        """第二希望クリア履歴をログに記録"""
        try:
            notes = "[AI電話第二希望クリア] 第二希望を削除しました"
            
            insert_taio_record(
                room_number=room_number,
                building_id=building_id,
                notes=notes,
                category="|2|",
                creator=0,
                updater=0,
                connection=connection
            )
        except Exception as e:
            print(f"[_log_second_choice_clear] ログ記録エラー: {e}")
    
    @staticmethod
    @db_connection
    def get_second_choice_history(room_number: str, password: str, building_id: str, 
                                limit: int = 10, connection=None) -> dict:
        """
        第二希望の変更履歴を取得
        
        Args:
            room_number: 部屋番号
            password: パスワード
            building_id: 物件ID
            limit: 取得件数上限
            connection: データベース接続
            
        Returns:
            dict: 第二希望変更履歴
        """
        try:
            # 1. 認証チェック
            auth_result = authenticate_user(room_number, password, building_id, connection)
            if "error" in auth_result:
                return {"error": "認証に失敗しました。部屋番号・パスワード・物件管理番号をご確認ください。"}
            
            # 2. 対応履歴から第二希望関連の記録を取得
            sql = """
            SELECT TaioNotes, Created, Category
            FROM tTaioF 
            WHERE UserCD = %s AND ClientCD = %s AND MukouFlg = 0 
            AND (Category LIKE '%|2|%' OR TaioNotes LIKE '%第二希望%')
            ORDER BY Created DESC 
            LIMIT %s
            """
            history = DBUtils.execute_query(connection, sql, (room_number, building_id, limit))
            
            return {
                "result": "ok",
                "history": history,
                "total_count": len(history)
            }
            
        except Exception as e:
            return {"error": f"第二希望履歴取得エラー: {str(e)}"}


# 便利関数（外部から直接呼び出し可能）
def update_second_choice(room_number: str, password: str, building_id: str, 
                        second_choice_text: str, connection=None) -> dict:
    """第二希望を更新（外部呼び出し用）"""
    updater = SecondChoiceUpdater()
    return updater.update_second_choice(room_number, password, building_id, second_choice_text, connection=connection)


def get_current_second_choice(room_number: str, password: str, building_id: str, connection=None) -> dict:
    """現在の第二希望を取得（外部呼び出し用）"""
    updater = SecondChoiceUpdater()
    return updater.get_current_second_choice(room_number, password, building_id, connection=connection)


def clear_second_choice(room_number: str, password: str, building_id: str, connection=None) -> dict:
    """第二希望をクリア（外部呼び出し用）"""
    updater = SecondChoiceUpdater()
    return updater.clear_second_choice(room_number, password, building_id, connection=connection)


def get_second_choice_history(room_number: str, password: str, building_id: str, 
                             limit: int = 10, connection=None) -> dict:
    """第二希望の変更履歴を取得（外部呼び出し用）"""
    updater = SecondChoiceUpdater()
    return updater.get_second_choice_history(room_number, password, building_id, limit, connection=connection)


if __name__ == "__main__":
    # テスト用のサンプル実行
    print("第二希望更新機能のテスト（認証あり版）")
    
    # 現在の第二希望を取得
    current_result = get_current_second_choice("103", "password123", "3760")
    print(f"現在の第二希望: {current_result}")
    
    # 第二希望を更新
    update_result = update_second_choice("103", "password123", "3760", "午前中希望、午後は不可")
    print(f"第二希望更新結果: {update_result}")
    
    # 第二希望をクリア
    clear_result = clear_second_choice("103", "password123", "3760")
    print(f"第二希望クリア結果: {clear_result}")
