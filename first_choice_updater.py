"""
第一希望更新機能の専用ファイル
ishokuフォルダー用に移植された第一希望更新処理
"""
import sys
import os
from datetime import datetime, timedelta

# ローカルモジュールをインポート
from user import authenticate_user
from taio_record import insert_taio_record
from utils import handle_db_exception
from utils.pattern_utils import PatternUtils
from utils.time_utils import TimeUtils
from utils.db_utils import db_connection, DBUtils


class FirstChoiceUpdater:
    """第一希望更新処理を管理するクラス"""
    
    @staticmethod
    @db_connection
    def update_first_choice(room_number: str, password: str, building_id: str, 
                           new_datetime: str, connection=None) -> dict:
        """
        第一希望の日時を更新する
        
        Args:
            room_number: 部屋番号
            password: パスワード
            building_id: 物件ID
            new_datetime: 新しい日時（YYYY-MM-DD HH:MM形式）
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
            current_reservation = FirstChoiceUpdater._get_current_reservation(
                room_number, building_id, connection)
            if "error" in current_reservation:
                return current_reservation
            
            # 3. 新しい日時の検証
            validation_result = FirstChoiceUpdater._validate_new_datetime(
                new_datetime, building_id, connection)
            if "error" in validation_result:
                return validation_result
            
            # 4. 空き枠チェック
            availability_result = FirstChoiceUpdater._check_availability(
                building_id, new_datetime, connection)
            if "error" in availability_result:
                return availability_result
            
            # 5. 第一希望更新実行
            update_result = FirstChoiceUpdater._execute_first_choice_update(
                room_number, building_id, new_datetime, current_reservation["datetime"], connection)
            if "error" in update_result:
                return update_result
            
            # 6. 対応履歴登録
            FirstChoiceUpdater._log_first_choice_update(
                room_number, building_id, new_datetime, connection)
            
            return {
                "result": "ok",
                "message": "第一希望を更新しました。",
                "old_datetime": current_reservation["datetime"],
                "new_datetime": new_datetime
            }
            
        except Exception as e:
            return handle_db_exception(e, context_message="第一希望更新", 
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
                "second_choice": result.get("SecondChoice")
            }
            
        except Exception as e:
            return {"error": f"予約情報取得エラー: {str(e)}"}
    
    @staticmethod
    def _validate_new_datetime(new_datetime, building_id, connection):
        """新しい日時の検証"""
        try:
            # 日時形式の検証
            try:
                parsed_datetime = datetime.strptime(new_datetime, "%Y-%m-%d %H:%M")
            except ValueError:
                return {"error": "日時の形式が正しくありません。YYYY-MM-DD HH:MM形式で入力してください。"}
            
            # 過去日時のチェック
            if parsed_datetime <= datetime.now():
                return {"error": "過去の日時は選択できません。未来の日時を選択してください。"}
            
            # 物件の営業時間チェック（必要に応じて）
            # ここで営業時間の検証ロジックを追加可能
            
            return {"valid": True, "parsed_datetime": parsed_datetime}
            
        except Exception as e:
            return {"error": f"日時検証エラー: {str(e)}"}
    
    @staticmethod
    def _check_availability(building_id, new_datetime, connection):
        """空き枠のチェック"""
        try:
            # パターン情報を取得
            pattern_utils = PatternUtils()
            pattern_info = pattern_utils.get_pattern_info(building_id, connection)
            if "error" in pattern_info:
                return pattern_info
            
            # 空き枠チェック（簡易版）
            # 実際の空き枠チェックロジックをここに実装
            # ここでは基本的な検証のみ行う
            
            return {"available": True}
            
        except Exception as e:
            return {"error": f"空き枠チェックエラー: {str(e)}"}
    
    @staticmethod
    def _execute_first_choice_update(room_number, building_id, new_datetime, old_datetime, connection):
        """第一希望更新の実行"""
        try:
            # 第一希望を更新
            update_sql = """
            UPDATE tReservationF 
            SET TimeFrom = %s, Updated = NOW(), Updater = %s 
            WHERE TimeFrom = %s AND UserCD = %s AND ClientCD = %s
            """
            row_count = DBUtils.execute_update(connection, update_sql, (
                new_datetime,
                room_number,
                old_datetime,
                room_number,
                building_id
            ))
            
            if row_count == 0:
                return {"error": "第一希望の更新に失敗しました。予約情報が見つかりません。"}
            
            return {"result": "ok"}
            
        except Exception as e:
            return {"error": f"第一希望更新エラー: {str(e)}"}
    
    @staticmethod
    def _log_first_choice_update(room_number, building_id, new_datetime, connection):
        """第一希望更新履歴をログに記録"""
        try:
            notes = f"[LINE第一希望更新] {new_datetime}"
            
            insert_taio_record(
                room_number=room_number,
                building_id=building_id,
                notes=notes,
                category="|1|",
                creator=0,
                updater=0,
                connection=connection
            )
        except Exception as e:
            print(f"[_log_first_choice_update] ログ記録エラー: {e}")
    
    @staticmethod
    @db_connection
    def get_available_slots(building_id: str, date: str, connection=None) -> dict:
        """
        指定日の利用可能な時間枠を取得
        
        Args:
            building_id: 物件ID
            date: 日付（YYYY-MM-DD形式）
            connection: データベース接続
            
        Returns:
            dict: 利用可能な時間枠
        """
        try:
            # パターン情報を取得
            pattern_utils = PatternUtils()
            pattern_info = pattern_utils.get_pattern_info(building_id, connection)
            if "error" in pattern_info:
                return pattern_info
            
            # 時間枠を生成（簡易版）
            # 実際の時間枠生成ロジックをここに実装
            time_slots = FirstChoiceUpdater._generate_time_slots(date, pattern_info)
            
            return {
                "result": "ok",
                "date": date,
                "time_slots": time_slots,
                "total_slots": len(time_slots)
            }
            
        except Exception as e:
            return {"error": f"時間枠取得エラー: {str(e)}"}
    
    @staticmethod
    def _generate_time_slots(date, pattern_info):
        """時間枠を生成（簡易版）"""
        try:
            # 基本的な時間枠を生成
            # 実際の実装では、パターン情報に基づいて時間枠を生成
            time_slots = []
            
            # 例：9:00-17:00の1時間刻み
            for hour in range(9, 17):
                time_slots.append({
                    "time": f"{date} {hour:02d}:00",
                    "available": True,
                    "stylist": "ST001"
                })
            
            return time_slots
            
        except Exception as e:
            return []


# 便利関数（外部から直接呼び出し可能）
def update_first_choice(room_number: str, password: str, building_id: str, 
                       new_datetime: str, connection=None) -> dict:
    """第一希望の日時を更新（外部呼び出し用）"""
    updater = FirstChoiceUpdater()
    return updater.update_first_choice(room_number, password, building_id, new_datetime, connection)


def get_available_slots(building_id: str, date: str, connection=None) -> dict:
    """指定日の利用可能な時間枠を取得（外部呼び出し用）"""
    updater = FirstChoiceUpdater()
    return updater.get_available_slots(building_id, date, connection)


if __name__ == "__main__":
    # テスト用のサンプル実行
    print("第一希望更新機能のテスト")
    
    # 利用可能な時間枠を取得
    slots_result = get_available_slots("12345", "2024-01-15")
    print(f"時間枠取得結果: {slots_result}")
    
    # 第一希望を更新
    update_result = update_first_choice("101", "password123", "12345", "2024-01-15 10:00")
    print(f"第一希望更新結果: {update_result}")
