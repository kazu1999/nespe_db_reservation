"""
時間処理関連のユーティリティ関数
"""
from datetime import datetime, timedelta
import re


class TimeUtils:
    """時間処理関連のユーティリティクラス"""
    
    @staticmethod
    def parse_datetime(dt_str):
        """日時文字列を解析"""
        if not dt_str:
            return None
        
        # 複数のフォーマットを試行
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        
        # パターンマッチングで柔軟に解析
        try:
            # "2024-01-15 10:30" のような形式
            match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})', dt_str)
            if match:
                year, month, day, hour, minute = map(int, match.groups())
                return datetime(year, month, day, hour, minute)
            
            # "2024/01/15 10:30" のような形式
            match = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{1,2})', dt_str)
            if match:
                year, month, day, hour, minute = map(int, match.groups())
                return datetime(year, month, day, hour, minute)
        except:
            pass
        
        return None
    
    @staticmethod
    def format_datetime(dt, fmt="%Y-%m-%d %H:%M:%S"):
        """日時をフォーマット"""
        if dt is None:
            return None
        return dt.strftime(fmt)
    
    @staticmethod
    def calculate_end_time(start_dt, minute_unit, minute_type):
        """終了時間を計算"""
        if start_dt is None:
            return None
        total_minutes = minute_unit * minute_type
        return start_dt + timedelta(minutes=total_minutes)
    
    @staticmethod
    def is_within_period(now, start_date, end_date):
        """期間内かどうかを判定"""
        if not all([now, start_date, end_date]):
            return False
        
        # 日付のみの比較（時刻を無視）
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        if isinstance(now, datetime):
            now = now.date()
        
        return start_date <= now <= end_date
