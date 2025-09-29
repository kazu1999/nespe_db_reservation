"""
空き枠チェック機能を担当するクラス
ishokuフォルダー用に移植された空き枠チェック機能
"""
from datetime import datetime, timedelta
from collections import Counter
from utils.pattern_utils import PatternUtils
from utils.time_utils import TimeUtils
from utils.db_utils import db_connection, DBUtils


class SlotAvailabilityChecker:
    """空き枠チェック機能をまとめたクラス"""
    
    def __init__(self, building_id, connection=None):
        self.building_id = building_id
        self.connection = connection
        self._close_conn = False
        
        if connection is None:
            from connection import get_connection
            self.connection = get_connection()
            self._close_conn = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._close_conn and self.connection:
            self.connection.close()
    
    def check_slot_availability(self, target_datetime, exclude_usercd=None, menu_cd=None):
        """
        指定の物件・日時で予約枠に空きがあるか判定する
        """
        try:
            # パターン情報を取得
            pattern_utils = PatternUtils()
            pattern_info = pattern_utils.get_pattern_info(self.building_id, self.connection)
            
            if not pattern_info or "error" in pattern_info:
                return {"available": False, "type": None}
            
            start_times = pattern_info['start_times']
            end_times = pattern_info['end_times']
            
            # 枠範囲設定を取得
            waku_range_list = self._get_wakurange_from_db()
            
            # 日付時刻の分割
            try:
                date_part, time_part = target_datetime.split()
            except Exception:
                return {"available": False, "type": None}
            
            # スロットインデックスの決定
            slot_index = self._get_slot_index(time_part, start_times, end_times)
            if slot_index is None:
                return {"available": False, "type": None}
            
            # 枠の時間範囲を取得
            slot_start_str = f"{date_part} {start_times[slot_index]}"
            slot_end_str = f"{date_part} {end_times[slot_index]}"
            slot_start_dt = datetime.strptime(slot_start_str, "%Y-%m-%d %H:%M")
            slot_end_dt = datetime.strptime(slot_end_str, "%Y-%m-%d %H:%M")
            
            # 連続枠数を取得
            minute_type = 1
            if menu_cd is not None:
                minute_type = self._get_minute_type(menu_cd)
            
            # 分単位を取得
            minute_unit = pattern_utils.get_minute_unit(self.building_id, self.connection)
            
            # 枠全体の満枠チェック
            waku_range_max = waku_range_list[slot_index] if slot_index < len(waku_range_list) else None
            if self._is_slot_full(slot_start_dt, slot_end_dt, minute_unit, waku_range_max, exclude_usercd):
                return {"available": False, "type": None}
            
            # 時間帯ごとの空き枠チェック
            return self._check_time_slots(slot_start_dt, slot_end_dt, minute_unit, minute_type, waku_range_max, exclude_usercd)
            
        except Exception as e:
            print(f"[SlotAvailabilityChecker] エラー: {e}")
            return {"available": False, "type": None}
    
    def _get_wakurange_from_db(self):
        """tSettingMのWakuRangeカラムを取得し、'-'で分割してリスト化して返す"""
        try:
            sql = "SELECT WakuRange FROM tSettingM WHERE ClientCD = %s"
            result = DBUtils.execute_single_query(self.connection, sql, (self.building_id,))
            
            if not result or not result.get('WakuRange'):
                return []
            
            waku_range_str = result['WakuRange']
            return [int(x) if x.isdigit() else 0 for x in waku_range_str.split('-')]
        except Exception:
            return []
    
    def _get_minute_type(self, menu_cd):
        """メニューの分タイプを取得"""
        try:
            sql = "SELECT MinuteType FROM tMenuM WHERE MenuCD = %s AND ClientCD = %s AND MukouFlg = 0"
            result = DBUtils.execute_single_query(self.connection, sql, (menu_cd, self.building_id))
            
            if result and result.get('MinuteType'):
                return int(result['MinuteType'])
            return 1  # デフォルト1枠
        except Exception:
            return 1
    
    def _get_slot_index(self, time_part, start_times, end_times):
        """スロットインデックスを取得"""
        # 完全一致チェック
        for idx, st in enumerate(start_times):
            if time_part == st:
                return idx
        
        # 範囲内チェック
        try:
            t_time = datetime.strptime(time_part, "%H:%M")
            for idx, (st, et) in enumerate(zip(start_times, end_times)):
                st_time = datetime.strptime(st, "%H:%M")
                et_time = datetime.strptime(et, "%H:%M")
                if st_time <= t_time < et_time:
                    return idx
        except Exception:
            pass
        
        return None
    
    def _is_slot_full(self, slot_start_dt, slot_end_dt, minute_unit, waku_range_max, exclude_usercd):
        """枠全体の満枠チェック"""
        if waku_range_max is None:
            return False
        
        all_times = []
        t_time = slot_start_dt
        while t_time < slot_end_dt:
            all_times.append(t_time)
            t_time += timedelta(minutes=minute_unit)
        
        total_reserved = 0
        for t in all_times:
            tstr = t.strftime("%Y-%m-%d %H:%M")
            reserved_count = self._get_reservation_count(tstr, exclude_usercd)
            total_reserved += reserved_count
        
        return total_reserved >= waku_range_max
    
    def _check_time_slots(self, slot_start_dt, slot_end_dt, minute_unit, minute_type, waku_range_max, exclude_usercd):
        """時間帯ごとの空き枠チェック"""
        t_time = slot_start_dt
        while t_time + timedelta(minutes=minute_unit * minute_type) <= slot_end_dt:
            ss_times = [t_time + timedelta(minutes=minute_unit * j) for j in range(minute_type)]
            
            total_reserved = sum(self._get_reservation_count(t.strftime("%Y-%m-%d %H:%M"), exclude_usercd) for t in ss_times)
            
            # 枠全体の予約数が上限より少ない場合のみスタイリストごとにチェック
            if waku_range_max is None or total_reserved < waku_range_max:
                # 通常枠のスタイリストごとに空き判定
                result = self._check_stylist_availability(t_time, minute_unit, minute_type, exclude_usercd)
                if result:
                    return result
            
            t_time += timedelta(minutes=minute_unit)
        
        return {"available": False, "type": None}
    
    def _check_stylist_availability(self, t_time, minute_unit, minute_type, exclude_usercd):
        """スタイリストごとの空き枠チェック"""
        try:
            # 通常のスタイリストのみ取得（WakugoeFlg != 1）
            sql = """
                SELECT StylistCD, NumberOfLines 
                FROM tStylistM 
                WHERE ClientCD = %s AND MukouFlg = 0 
                AND (WakugoeFlg IS NULL OR WakugoeFlg = 0)
                ORDER BY StylistCD
            """
            stylists = DBUtils.execute_query(self.connection, sql, (self.building_id,))
            
            for stylist in stylists:
                stylist_cd = stylist["StylistCD"]
                number_of_lines = stylist["NumberOfLines"]
                
                # 連続枠チェック
                if self._is_stylist_available_php_style(t_time, minute_unit, minute_type, stylist_cd, number_of_lines, exclude_usercd):
                    return {
                        "available": True, 
                        "type": "normal", 
                        "actual_time_from": t_time.strftime("%Y-%m-%d %H:%M"), 
                        "stylist_cd": stylist_cd
                    }
            
            return None
        except Exception as e:
            print(f"[_check_stylist_availability] エラー: {e}")
            return None
    
    def _is_stylist_available_php_style(self, t_time, minute_unit, minute_type, stylist_cd, number_of_lines, exclude_usercd):
        """PHPのgetAkiWakuAMPMTime2関数と同様のスタイリスト空き判定"""
        try:
            # 連続枠の各時間で予約をチェック
            for j in range(minute_type):
                check_time = t_time + timedelta(minutes=minute_unit * j)
                tstr = check_time.strftime("%Y-%m-%d %H:%M")
                
                # このスタイリストのこの時間の予約数を取得
                reserved_count = self._get_stylist_reservation_count(tstr, stylist_cd, exclude_usercd)
                
                # 予約数がNumberOfLinesを超えているかチェック
                if reserved_count >= number_of_lines:
                    return False
            
            return True
        except Exception as e:
            print(f"[_is_stylist_available_php_style] エラー: {e}")
            return False
    
    def _get_reservation_count(self, datetime_str, exclude_usercd=None):
        """指定時刻の予約数を取得"""
        try:
            if exclude_usercd:
                sql = '''SELECT COUNT(*) AS cnt FROM tReservationF WHERE MukouFlg = 0 AND Status = 1 AND ClientCD = %s AND DATE_FORMAT(TimeFrom, '%%Y-%%m-%%d %%H:%%i') = %s AND UserCD != %s'''
                result = DBUtils.execute_single_query(self.connection, sql, (self.building_id, datetime_str, exclude_usercd))
            else:
                sql = '''SELECT COUNT(*) AS cnt FROM tReservationF WHERE MukouFlg = 0 AND Status = 1 AND ClientCD = %s AND DATE_FORMAT(TimeFrom, '%%Y-%%m-%%d %%H:%%i') = %s'''
                result = DBUtils.execute_single_query(self.connection, sql, (self.building_id, datetime_str))
            
            return result["cnt"] if result else 0
        except Exception:
            return 0
    
    def _get_stylist_reservation_count(self, datetime_str, stylist_cd, exclude_usercd=None):
        """特定スタイリストの指定時刻の予約数を取得"""
        try:
            if exclude_usercd:
                sql = '''SELECT COUNT(*) AS cnt FROM tReservationF WHERE MukouFlg = 0 AND Status = 1 AND ClientCD = %s AND DATE_FORMAT(TimeFrom, '%%Y-%%m-%%d %%H:%%i') = %s AND StylistCD = %s AND UserCD != %s'''
                result = DBUtils.execute_single_query(self.connection, sql, (self.building_id, datetime_str, stylist_cd, exclude_usercd))
            else:
                sql = '''SELECT COUNT(*) AS cnt FROM tReservationF WHERE MukouFlg = 0 AND Status = 1 AND ClientCD = %s AND DATE_FORMAT(TimeFrom, '%%Y-%%m-%%d %%H:%%i') = %s AND StylistCD = %s'''
                result = DBUtils.execute_single_query(self.connection, sql, (self.building_id, datetime_str, stylist_cd))
            
            return result["cnt"] if result else 0
        except Exception:
            return 0


def is_slot_available(building_id: str, target_datetime: str, connection=None, exclude_usercd=None, menu_cd=None):
    """
    指定の物件・日時で予約枠に空きがあるか判定する（レガシー関数）
    """
    with SlotAvailabilityChecker(building_id, connection) as checker:
        return checker.check_slot_availability(target_datetime, exclude_usercd, menu_cd)
