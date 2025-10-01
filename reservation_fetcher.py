"""
予約日程取得機能の専用ファイル
ishokuフォルダー用に移植された予約日程取得処理
"""
import sys
import os
from datetime import datetime, timedelta

# ローカルモジュールをインポート
from utils import handle_db_exception
from utils.db_utils import db_connection, DBUtils


class ReservationFetcher:
    """予約日程取得処理を管理するクラス"""
    
    @staticmethod
    @db_connection
    def get_reservation_date(room_number: str, building_id: str, connection=None) -> dict:
        """
        予約日程を取得する
        
        Args:
            room_number: 部屋番号
            building_id: 物件ID
            connection: データベース接続
            
        Returns:
            dict: 予約日程情報
        """
        try:
            # 予約情報を取得
            reservation_info = ReservationFetcher._get_reservation_info(room_number, building_id, connection)
            if "error" in reservation_info:
                return reservation_info
            
            return {
                "result": "ok",
                "reservation_date": reservation_info["datetime"],
                "reservation_date_raw": reservation_info["datetime_raw"],
                "second_choice": reservation_info.get("second_choice"),
                "stylist_cd": reservation_info.get("stylist_cd"),
                "time_to": reservation_info.get("time_to"),
                "has_reservation": True
            }
            
        except Exception as e:
            return handle_db_exception(e, context_message="予約日程取得", 
                                     input_params={"room_number": room_number, "building_id": building_id})
    
    @staticmethod
    def _get_reservation_info(room_number, building_id, connection):
        """予約情報を取得"""
        try:
            sql = """
            SELECT 
                rf.TimeFrom AS bookingDateTime,
                rf.TimeTo AS bookingDateTimeTo,
                rf.SecondChoice AS secondChoiceText,
                rf.StylistCD AS stylistCD
            FROM tReservationF rf
            JOIN tClientM cm ON rf.ClientCD = cm.ClientCD
            WHERE rf.UserCD = %s AND rf.ClientCD = %s AND rf.MukouFlg = 0
            ORDER BY rf.TimeFrom DESC
            LIMIT 1
            """
            result = DBUtils.execute_single_query(connection, sql, (room_number, building_id))
            
            if not result or not result.get("bookingDateTime"):
                return {
                    "datetime": None,
                    "datetime_raw": None,
                    "second_choice": None,
                    "stylist_cd": None,
                    "time_to": None,
                    "has_reservation": False
                }
            
            booking_datetime = result["bookingDateTime"]
            booking_datetime_to = result.get("bookingDateTimeTo")
            
            return {
                "datetime": booking_datetime.strftime("%Y-%m-%d %H:%M"),
                "datetime_raw": booking_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "second_choice": result.get("secondChoiceText"),
                "stylist_cd": result.get("stylistCD"),
                "time_to": booking_datetime_to.strftime("%Y-%m-%d %H:%M") if booking_datetime_to else None,
                "has_reservation": True
            }
            
        except Exception as e:
            return {"error": f"予約情報取得エラー: {str(e)}"}
    
    @staticmethod
    @db_connection
    def get_reservation_history(room_number: str, building_id: str, 
                               limit: int = 10, connection=None) -> dict:
        """
        予約履歴を取得する
        
        Args:
            room_number: 部屋番号
            building_id: 物件ID
            limit: 取得件数上限
            connection: データベース接続
            
        Returns:
            dict: 予約履歴情報
        """
        try:
            # 予約履歴を取得
            sql = """
            SELECT 
                TimeFrom,
                TimeTo,
                SecondChoice,
                StylistCD,
                Status,
                Created,
                Updated
            FROM tReservationF 
            WHERE UserCD = %s AND ClientCD = %s AND MukouFlg = 0
            ORDER BY TimeFrom DESC
            LIMIT %s
            """
            history = DBUtils.execute_query(connection, sql, (room_number, building_id, limit))
            
            # 履歴を整形
            formatted_history = []
            for record in history:
                formatted_history.append({
                    "datetime": record["TimeFrom"].strftime("%Y-%m-%d %H:%M") if record.get("TimeFrom") else None,
                    "datetime_to": record["TimeTo"].strftime("%Y-%m-%d %H:%M") if record.get("TimeTo") else None,
                    "second_choice": record.get("SecondChoice"),
                    "stylist_cd": record.get("StylistCD"),
                    "status": record.get("Status"),
                    "created": record["Created"].strftime("%Y-%m-%d %H:%M:%S") if record.get("Created") else None,
                    "updated": record["Updated"].strftime("%Y-%m-%d %H:%M:%S") if record.get("Updated") else None
                })
            
            return {
                "result": "ok",
                "history": formatted_history,
                "total_count": len(formatted_history)
            }
            
        except Exception as e:
            return {"error": f"予約履歴取得エラー: {str(e)}"}
    
    @staticmethod
    @db_connection
    def get_reservation_status(room_number: str, building_id: str, connection=None) -> dict:
        """
        予約状況を取得する
        
        Args:
            room_number: 部屋番号
            building_id: 物件ID
            connection: データベース接続
            
        Returns:
            dict: 予約状況情報
        """
        try:
            # 予約状況を取得
            sql = """
            SELECT 
                COUNT(*) as total_reservations,
                COUNT(CASE WHEN Status = 1 THEN 1 END) as active_reservations,
                COUNT(CASE WHEN SecondChoice IS NOT NULL THEN 1 END) as with_second_choice,
                MAX(TimeFrom) as latest_reservation,
                MIN(TimeFrom) as earliest_reservation
            FROM tReservationF 
            WHERE UserCD = %s AND ClientCD = %s AND MukouFlg = 0
            """
            result = DBUtils.execute_single_query(connection, sql, (room_number, building_id))
            
            if not result:
                return {"error": "予約状況の取得に失敗しました。"}
            
            return {
                "result": "ok",
                "total_reservations": result.get("total_reservations", 0),
                "active_reservations": result.get("active_reservations", 0),
                "with_second_choice": result.get("with_second_choice", 0),
                "latest_reservation": result["latest_reservation"].strftime("%Y-%m-%d %H:%M") if result.get("latest_reservation") else None,
                "earliest_reservation": result["earliest_reservation"].strftime("%Y-%m-%d %H:%M") if result.get("earliest_reservation") else None,
                "has_reservations": result.get("total_reservations", 0) > 0
            }
            
        except Exception as e:
            return {"error": f"予約状況取得エラー: {str(e)}"}
    
    @staticmethod
    @db_connection
    def get_upcoming_reservations(room_number: str, building_id: str, 
                                 days_ahead: int = 30, connection=None) -> dict:
        """
        今後の予約を取得する
        
        Args:
            room_number: 部屋番号
            building_id: 物件ID
            days_ahead: 何日先まで取得するか
            connection: データベース接続
            
        Returns:
            dict: 今後の予約情報
        """
        try:
            # 今後の予約を取得
            now = datetime.now()
            future_date = now + timedelta(days=days_ahead)
            
            sql = """
            SELECT 
                TimeFrom,
                TimeTo,
                SecondChoice,
                StylistCD,
                Status
            FROM tReservationF 
            WHERE UserCD = %s AND ClientCD = %s AND MukouFlg = 0
            AND TimeFrom >= %s AND TimeFrom <= %s
            ORDER BY TimeFrom ASC
            """
            reservations = DBUtils.execute_query(connection, sql, (
                room_number, building_id, now.strftime("%Y-%m-%d %H:%M:%S"), 
                future_date.strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            # 予約を整形
            formatted_reservations = []
            for record in reservations:
                formatted_reservations.append({
                    "datetime": record["TimeFrom"].strftime("%Y-%m-%d %H:%M") if record.get("TimeFrom") else None,
                    "datetime_to": record["TimeTo"].strftime("%Y-%m-%d %H:%M") if record.get("TimeTo") else None,
                    "second_choice": record.get("SecondChoice"),
                    "stylist_cd": record.get("StylistCD"),
                    "status": record.get("Status"),
                    "days_from_now": (record["TimeFrom"] - now).days if record.get("TimeFrom") else None
                })
            
            return {
                "result": "ok",
                "upcoming_reservations": formatted_reservations,
                "total_count": len(formatted_reservations),
                "days_ahead": days_ahead
            }
            
        except Exception as e:
            return {"error": f"今後の予約取得エラー: {str(e)}"}
    
    @staticmethod
    @db_connection
    def get_reservation_summary(room_number: str, building_id: str, connection=None) -> dict:
        """
        予約サマリーを取得する（現在の予約 + 状況 + 今後の予約）
        
        Args:
            room_number: 部屋番号
            building_id: 物件ID
            connection: データベース接続
            
        Returns:
            dict: 予約サマリー情報
        """
        try:
            # 1. 現在の予約を取得
            current_reservation = ReservationFetcher.get_reservation_date(room_number, building_id, connection=connection)
            if "error" in current_reservation:
                return current_reservation
            
            # 2. 予約状況を取得
            status_info = ReservationFetcher.get_reservation_status(room_number, building_id, connection=connection)
            if "error" in status_info:
                return status_info
            
            # 3. 今後の予約を取得
            upcoming_reservations = ReservationFetcher.get_upcoming_reservations(room_number, building_id, connection=connection)
            if "error" in upcoming_reservations:
                return upcoming_reservations
            
            return {
                "result": "ok",
                "current_reservation": current_reservation,
                "status": status_info,
                "upcoming": upcoming_reservations,
                "summary": {
                    "has_current_reservation": current_reservation.get("has_reservation", False),
                    "total_reservations": status_info.get("total_reservations", 0),
                    "upcoming_count": upcoming_reservations.get("total_count", 0)
                }
            }
            
        except Exception as e:
            return {"error": f"予約サマリー取得エラー: {str(e)}"}


# 便利関数（外部から直接呼び出し可能）
def get_reservation_date(room_number: str, building_id: str, connection=None) -> dict:
    """予約日程を取得（外部呼び出し用）"""
    fetcher = ReservationFetcher()
    return fetcher.get_reservation_date(room_number, building_id, connection=connection)


def get_reservation_history(room_number: str, building_id: str, 
                          limit: int = 10, connection=None) -> dict:
    """予約履歴を取得（外部呼び出し用）"""
    fetcher = ReservationFetcher()
    return fetcher.get_reservation_history(room_number, building_id, limit, connection=connection)


def get_reservation_status(room_number: str, building_id: str, connection=None) -> dict:
    """予約状況を取得（外部呼び出し用）"""
    fetcher = ReservationFetcher()
    return fetcher.get_reservation_status(room_number, building_id, connection=connection)


def get_upcoming_reservations(room_number: str, building_id: str, 
                             days_ahead: int = 30, connection=None) -> dict:
    """今後の予約を取得（外部呼び出し用）"""
    fetcher = ReservationFetcher()
    return fetcher.get_upcoming_reservations(room_number, building_id, days_ahead, connection=connection)


def get_reservation_summary(room_number: str, building_id: str, connection=None) -> dict:
    """予約サマリーを取得（外部呼び出し用）"""
    fetcher = ReservationFetcher()
    return fetcher.get_reservation_summary(room_number, building_id, connection=connection)


if __name__ == "__main__":
    # テスト用のサンプル実行
    print("予約日程取得機能のテスト")
    
    # 予約日程を取得
    date_result = get_reservation_date("103", "3760")
    print(f"予約日程: {date_result}")
    
    # 予約状況を取得
    status_result = get_reservation_status("103", "3760")
    print(f"予約状況: {status_result}")
    
    # 今後の予約を取得
    upcoming_result = get_upcoming_reservations("103", "3760", days_ahead=7)
    print(f"今後の予約: {upcoming_result}")
    
    # 予約サマリーを取得
    summary_result = get_reservation_summary("103", "3760")
    print(f"予約サマリー: {summary_result}")
