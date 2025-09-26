"""
時間処理関連のユーティリティ関数
"""
from datetime import datetime, timedelta
from chatbot_scripts.logic.utils import DateTimeHandler


class TimeUtils:
    """時間処理関連のユーティリティクラス"""
    
    @staticmethod
    def parse_datetime(dt_str):
        """日時文字列を解析"""
        return DateTimeHandler.parse_datetime(dt_str)
    
    @staticmethod
    def format_datetime(dt, fmt="%Y-%m-%d %H:%M:%S"):
        """日時をフォーマット"""
        return DateTimeHandler.format_datetime(dt, fmt)
    
    @staticmethod
    def calculate_end_time(start_dt, minute_unit, minute_type):
        """終了時間を計算"""
        total_minutes = minute_unit * minute_type
        return start_dt + timedelta(minutes=total_minutes)
    
    @staticmethod
    def is_within_period(now, start_date, end_date):
        """期間内かどうかを判定"""
        return DateTimeHandler.check_within_period(now, start_date, end_date)
