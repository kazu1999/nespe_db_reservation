"""
第一希望更新機能の専用ファイル
ishokuフォルダー用に移植された第一希望更新処理
"""
import sys
import os
from datetime import datetime, timedelta

# ローカルモジュールをインポート
from taio_record import insert_taio_record
from utils import handle_db_exception
from utils.pattern_utils import PatternUtils
from utils.time_utils import TimeUtils
from utils.db_utils import db_connection, DBUtils
from availability_checker import SlotAvailabilityChecker


class FirstChoiceUpdater:
    """第一希望更新処理を管理するクラス"""
    
    @staticmethod
    @db_connection
    def update_first_choice(room_number: str, building_id: str, 
                           new_datetime: str, connection=None) -> dict:
        """
        第一希望の日時を更新する
        
        Args:
            room_number: 部屋番号
            building_id: 物件ID
            new_datetime: 新しい日時（YYYY-MM-DD HH:MM形式）
            connection: データベース接続
            
        Returns:
            dict: 更新結果
        """
        try:
            # 1. 現在の予約情報を取得
            current_reservation = FirstChoiceUpdater._get_current_reservation(
                room_number, building_id, connection)
            if "error" in current_reservation:
                return current_reservation
            
            # 2. 新しい日時の検証
            validation_result = FirstChoiceUpdater._validate_new_datetime(
                new_datetime, building_id, connection)
            if "error" in validation_result:
                return validation_result
            
            # 3. 空き枠チェック
            availability_result = FirstChoiceUpdater._check_availability(
                building_id, new_datetime, connection)
            if "error" in availability_result:
                return availability_result
            
            # 4. 第一希望更新実行
            update_result = FirstChoiceUpdater._execute_first_choice_update(
                room_number, building_id, new_datetime, current_reservation["datetime"], connection)
            if "error" in update_result:
                return update_result
            
            # 5. 対応履歴登録
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
            
            # 物件の営業時間チェック
            business_hours_result = FirstChoiceUpdater._check_business_hours(
                parsed_datetime, building_id, connection)
            if "error" in business_hours_result:
                return business_hours_result
            
            return {"valid": True, "parsed_datetime": parsed_datetime}
            
        except Exception as e:
            return {"error": f"日時検証エラー: {str(e)}"}
    
    @staticmethod
    def _check_business_hours(parsed_datetime, building_id, connection):
        """営業時間チェック"""
        try:
            # 営業時間設定を取得
            business_hours = FirstChoiceUpdater._get_business_hours(building_id, connection)
            if "error" in business_hours:
                return business_hours
            
            # 曜日を取得（0=月曜日, 6=日曜日）
            weekday = parsed_datetime.weekday()
            time_str = parsed_datetime.strftime("%H:%M")
            
            # 営業時間チェック
            if weekday in business_hours["weekdays"]:
                # 平日の営業時間チェック
                if not FirstChoiceUpdater._is_within_business_hours(
                    time_str, business_hours["weekday_hours"]):
                    return {"error": f"平日の営業時間外です。営業時間: {business_hours['weekday_hours']['start']}-{business_hours['weekday_hours']['end']}"}
            elif weekday == 6:  # 日曜日
                if business_hours["sunday_hours"]:
                    if not FirstChoiceUpdater._is_within_business_hours(
                        time_str, business_hours["sunday_hours"]):
                        return {"error": f"日曜日の営業時間外です。営業時間: {business_hours['sunday_hours']['start']}-{business_hours['sunday_hours']['end']}"}
                else:
                    return {"error": "日曜日は営業していません。"}
            else:  # 土曜日
                if business_hours["saturday_hours"]:
                    if not FirstChoiceUpdater._is_within_business_hours(
                        time_str, business_hours["saturday_hours"]):
                        return {"error": f"土曜日の営業時間外です。営業時間: {business_hours['saturday_hours']['start']}-{business_hours['saturday_hours']['end']}"}
                else:
                    return {"error": "土曜日は営業していません。"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"error": f"営業時間チェックエラー: {str(e)}"}
    
    @staticmethod
    def _get_business_hours(building_id, connection):
        """物件の営業時間設定を取得"""
        try:
            # tSettingMテーブルから営業時間設定を取得
            sql = """
            SELECT 
                BusinessStartTime, BusinessEndTime,
                SaturdayStartTime, SaturdayEndTime,
                SundayStartTime, SundayEndTime,
                BusinessWeekdays
            FROM tSettingM 
            WHERE ClientCD = %s
            """
            result = DBUtils.execute_single_query(connection, sql, (building_id,))
            
            if not result:
                return {"error": "物件の営業時間設定が見つかりません。"}
            
            # デフォルト値の設定
            weekday_hours = {
                "start": result.get("BusinessStartTime", "09:00"),
                "end": result.get("BusinessEndTime", "18:00")
            }
            
            saturday_hours = None
            if result.get("SaturdayStartTime") and result.get("SaturdayEndTime"):
                saturday_hours = {
                    "start": result["SaturdayStartTime"],
                    "end": result["SaturdayEndTime"]
                }
            
            sunday_hours = None
            if result.get("SundayStartTime") and result.get("SundayEndTime"):
                sunday_hours = {
                    "start": result["SundayStartTime"],
                    "end": result["SundayEndTime"]
                }
            
            # 営業曜日の取得（デフォルトは月-金）
            business_weekdays_str = result.get("BusinessWeekdays", "0,1,2,3,4")
            weekdays = [int(x.strip()) for x in business_weekdays_str.split(",") if x.strip().isdigit()]
            
            return {
                "weekday_hours": weekday_hours,
                "saturday_hours": saturday_hours,
                "sunday_hours": sunday_hours,
                "weekdays": weekdays
            }
            
        except Exception as e:
            return {"error": f"営業時間設定取得エラー: {str(e)}"}
    
    @staticmethod
    def _is_within_business_hours(time_str, hours):
        """指定時間が営業時間内かチェック"""
        try:
            target_time = datetime.strptime(time_str, "%H:%M").time()
            start_time = datetime.strptime(hours["start"], "%H:%M").time()
            end_time = datetime.strptime(hours["end"], "%H:%M").time()
            
            return start_time <= target_time < end_time
        except Exception:
            return False
    
    @staticmethod
    def _check_availability(building_id, new_datetime, connection):
        """空き枠のチェック"""
        try:
            # パターン情報を取得
            pattern_utils = PatternUtils()
            pattern_info = pattern_utils.get_pattern_info(building_id, connection)
            if not pattern_info or (isinstance(pattern_info, dict) and "error" in pattern_info):
                return pattern_info
            
            # 空き枠チェックの実行
            availability_checker = SlotAvailabilityChecker(building_id, connection)
            result = availability_checker.check_slot_availability(new_datetime)
            
            if not result.get("available"):
                return {"error": "選択された日時は満枠です。別の日時を選択してください。"}
            
            return {
                "available": True,
                "stylist_cd": result.get("stylist_cd"),
                "type": result.get("type", "normal")
            }
            
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
            notes = f"[AI電話第一希望更新] {new_datetime}"
            
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
            # 日付の検証
            try:
                parsed_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return {"error": "日付の形式が正しくありません。YYYY-MM-DD形式で入力してください。"}
            
            # 過去日付のチェック
            if parsed_date.date() < datetime.now().date():
                return {"error": "過去の日付は選択できません。未来の日付を選択してください。"}
            
            # パターン情報を取得
            pattern_utils = PatternUtils()
            pattern_info = pattern_utils.get_pattern_info(building_id, connection)
            if "error" in pattern_info:
                return pattern_info
            
            # 営業時間設定を取得
            business_hours = FirstChoiceUpdater._get_business_hours(building_id, connection)
            if "error" in business_hours:
                return business_hours
            
            # 時間枠を生成
            time_slots = FirstChoiceUpdater._generate_time_slots(
                date, pattern_info, business_hours, building_id, connection)
            
            return {
                "result": "ok",
                "date": date,
                "time_slots": time_slots,
                "total_slots": len(time_slots),
                "available_slots": len([slot for slot in time_slots if slot.get("available", False)])
            }
            
        except Exception as e:
            return {"error": f"時間枠取得エラー: {str(e)}"}
    
    @staticmethod
    def _generate_time_slots(date, pattern_info, business_hours, building_id, connection):
        """時間枠を生成（完全版）"""
        try:
            time_slots = []
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            weekday = parsed_date.weekday()
            
            # 曜日別の営業時間を取得
            if weekday in business_hours["weekdays"]:
                # 平日
                start_time = business_hours["weekday_hours"]["start"]
                end_time = business_hours["weekday_hours"]["end"]
            elif weekday == 6:  # 日曜日
                if not business_hours["sunday_hours"]:
                    return []  # 日曜日は営業していない
                start_time = business_hours["sunday_hours"]["start"]
                end_time = business_hours["sunday_hours"]["end"]
            else:  # 土曜日
                if not business_hours["saturday_hours"]:
                    return []  # 土曜日は営業していない
                start_time = business_hours["saturday_hours"]["start"]
                end_time = business_hours["saturday_hours"]["end"]
            
            # パターン情報から時間枠を生成
            start_times = pattern_info.get('start_times', [])
            end_times = pattern_info.get('end_times', [])
            
            if not start_times or not end_times:
                return []
            
            # 各時間枠をチェック
            for i, (start_time_pattern, end_time_pattern) in enumerate(zip(start_times, end_times)):
                # 営業時間内かチェック
                if not FirstChoiceUpdater._is_within_business_hours(start_time_pattern, {
                    "start": start_time, "end": end_time
                }):
                    continue
                
                # 空き枠チェック
                datetime_str = f"{date} {start_time_pattern}"
                availability_result = FirstChoiceUpdater._check_slot_availability(
                    building_id, datetime_str, connection)
                
                # スタイリスト情報を取得
                stylist_info = FirstChoiceUpdater._get_available_stylists(
                    building_id, datetime_str, connection)
                
                time_slots.append({
                    "time": datetime_str,
                    "start_time": start_time_pattern,
                    "end_time": end_time_pattern,
                    "available": availability_result.get("available", False),
                    "stylist_cd": availability_result.get("stylist_cd"),
                    "type": availability_result.get("type", "normal"),
                    "stylists": stylist_info,
                    "slot_index": i
                })
            
            return time_slots
            
        except Exception as e:
            print(f"[_generate_time_slots] エラー: {e}")
            return []
    
    @staticmethod
    def _check_slot_availability(building_id, datetime_str, connection):
        """指定日時の空き枠をチェック"""
        try:
            availability_checker = SlotAvailabilityChecker(building_id, connection)
            result = availability_checker.check_slot_availability(datetime_str)
            return result
        except Exception as e:
            print(f"[_check_slot_availability] エラー: {e}")
            return {"available": False, "type": None}
    
    @staticmethod
    def _get_available_stylists(building_id, datetime_str, connection):
        """指定日時に利用可能なスタイリスト一覧を取得"""
        try:
            sql = """
            SELECT 
                sm.StylistCD,
                sm.StylistName,
                sm.NumberOfLines,
                COUNT(rf.UserCD) as current_reservations
            FROM tStylistM sm
            LEFT JOIN tReservationF rf ON (
                sm.StylistCD = rf.StylistCD 
                AND rf.ClientCD = %s 
                AND DATE_FORMAT(rf.TimeFrom, '%%Y-%%m-%%d %%H:%%i') = %s
                AND rf.MukouFlg = 0 
                AND rf.Status = 1
            )
            WHERE sm.ClientCD = %s 
            AND sm.MukouFlg = 0 
            AND (sm.WakugoeFlg IS NULL OR sm.WakugoeFlg = 0)
            GROUP BY sm.StylistCD, sm.StylistName, sm.NumberOfLines
            HAVING current_reservations < sm.NumberOfLines
            ORDER BY sm.StylistCD
            """
            stylists = DBUtils.execute_query(connection, sql, (building_id, datetime_str, building_id))
            
            return [
                {
                    "stylist_cd": stylist["StylistCD"],
                    "stylist_name": stylist["StylistName"],
                    "available": True,
                    "current_reservations": stylist["current_reservations"],
                    "max_reservations": stylist["NumberOfLines"]
                }
                for stylist in stylists
            ]
            
        except Exception as e:
            print(f"[_get_available_stylists] エラー: {e}")
            return []


# 便利関数（外部から直接呼び出し可能）
def update_first_choice(room_number: str, building_id: str, 
                       new_datetime: str, connection=None) -> dict:
    """第一希望の日時を更新（外部呼び出し用）"""
    updater = FirstChoiceUpdater()
    return updater.update_first_choice(room_number, building_id, new_datetime, connection=connection)


def get_available_slots(building_id: str, date: str, connection=None) -> dict:
    """指定日の利用可能な時間枠を取得（外部呼び出し用）"""
    updater = FirstChoiceUpdater()
    return updater.get_available_slots(building_id, date, connection=connection)


if __name__ == "__main__":
    # テスト用のサンプル実行
    print("第一希望更新機能のテスト")
    
    # 利用可能な時間枠を取得
    slots_result = get_available_slots("3760", "2024-01-15")
    print(f"時間枠取得結果: {slots_result}")
    
    # 第一希望を更新
    update_result = update_first_choice("103", "3760", "2024-01-15 10:00")
    print(f"第一希望更新結果: {update_result}")
