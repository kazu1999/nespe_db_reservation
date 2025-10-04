"""
第二希望文字列組み立てロジックの実装
PHPのreserve_finish_new.phpの文字列組み立て処理をPythonで実装
"""
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class SecondChoiceContentLogic:
    """第二希望の文字列組み立てロジックを管理するクラス"""
    
    def __init__(self):
        """初期化"""
        self.waku_patterns = {}
        self.time_slots = {}
    
    def set_waku_patterns(self, waku_patterns: Dict):
        """枠パターンを設定"""
        self.waku_patterns = waku_patterns
    
    def set_time_slots(self, time_slots: Dict):
        """時間帯スロットを設定"""
        self.time_slots = time_slots
    
    def parse_date_input(self, date_str: str) -> str:
        """
        日付文字列を解析してY-m-d形式に変換
        
        Args:
            date_str: 日付文字列
            
        Returns:
            str: Y-m-d形式の日付文字列
        """
        try:
            # 様々な日付形式に対応
            if not date_str:
                return ""
            
            # 既にY-m-d形式の場合
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                return date_str
            
            # その他の形式をY-m-dに変換
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
            return parsed_date.strftime('%Y-%m-%d')
            
        except ValueError:
            raise ValueError(f"無効な日付形式: {date_str}")
    
    def parse_time_input(self, time_str: str) -> Tuple[str, str]:
        """
        時間帯文字列を解析して開始時間と終了時間を取得
        
        Args:
            time_str: 時間帯文字列 (例: "09:00～12:00")
            
        Returns:
            Tuple[str, str]: (開始時間, 終了時間)
        """
        if not time_str:
            return "", ""
        
        # ～で分割
        time_parts = time_str.split('～')
        if len(time_parts) != 2:
            raise ValueError(f"無効な時間帯形式: {time_str}")
        
        start_time = time_parts[0].strip()
        end_time = time_parts[1].strip()
        
        return start_time, end_time
    
    def convert_date_format(self, date_str: str) -> str:
        """
        日付フォーマットを変換 (Y-m-d → M/d)
        
        Args:
            date_str: Y-m-d形式の日付文字列
            
        Returns:
            str: M/d形式の日付文字列
        """
        if not date_str:
            return ""
        
        try:
            # Y-m-d形式をM/d形式に変換
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%m/%d')
        except ValueError:
            raise ValueError(f"日付変換エラー: {date_str}")
    
    def get_time_ampm(self, start_time: str, waku_pattern_id: int) -> str:
        """
        開始時間から時間帯名を取得
        
        Args:
            start_time: 開始時間 (例: "09:00")
            waku_pattern_id: 枠パターンID (数値)
            
        Returns:
            str: 時間帯名 (例: "AM", "PM", "PM1", "AM1"など)
        """
        if not start_time or waku_pattern_id is None:
            return ""
        
        # 枠パターンから時間帯を取得
        if waku_pattern_id in self.waku_patterns:
            pattern_data = self.waku_patterns[waku_pattern_id]
            if 'StartTime' in pattern_data and 'AMPM' in pattern_data:
                start_times = pattern_data['StartTime']
                ampm_list = pattern_data['AMPM']
                
                for i, pattern_start_time in enumerate(start_times):
                    if start_time == pattern_start_time and i < len(ampm_list):
                        return ampm_list[i]
        
        # フォールバック: 時間帯を推定
        return self._estimate_time_ampm(start_time)
    
    def _estimate_time_ampm(self, start_time: str) -> str:
        """
        開始時間から時間帯を推定
        
        Args:
            start_time: 開始時間 (例: "09:00")
            
        Returns:
            str: 推定された時間帯名
        """
        try:
            hour = int(start_time.split(':')[0])
            if 6 <= hour < 12:
                return "AM"
            elif 12 <= hour < 18:
                return "PM"
            else:
                return "PM2"
        except (ValueError, IndexError):
            return "AM"
    
    def check_third_choice_availability(self, date3: str, time3: str) -> bool:
        """
        第三希望の有無を判定
        
        Args:
            date3: 第三希望日
            time3: 第三希望時間帯
            
        Returns:
            bool: 第三希望がある場合True
        """
        return bool(date3 and time3 and date3.strip() and time3.strip())
    
    def build_second_choice_string(self, 
                                 date1: str, time1: str,
                                 date2: str, time2: str,
                                 date3: str = "", time3: str = "",
                                 waku_pattern_id: int = 0) -> str:
        """
        第二希望文字列を組み立て
        
        Args:
            date1: 第一希望日
            time1: 第一希望時間帯
            date2: 第二希望日
            time2: 第二希望時間帯
            date3: 第三希望日 (オプション)
            time3: 第三希望時間帯 (オプション)
            waku_pattern_id: 枠パターンID (数値)
            
        Returns:
            str: 組み立てられた第二希望文字列
        """
        try:
            # 第一希望の処理
            first_choice = self._build_single_choice(date1, time1, waku_pattern_id, "①")
            if not first_choice:
                raise ValueError("第一希望の情報が不足しています")
            
            # 第二希望の処理
            second_choice = self._build_single_choice(date2, time2, waku_pattern_id, "②")
            if not second_choice:
                raise ValueError("第二希望の情報が不足しています")
            
            # 第三希望の処理
            third_choice = self._build_third_choice(date3, time3, waku_pattern_id)
            
            # 文字列を結合
            result = first_choice + second_choice + third_choice
            
            return result
            
        except Exception as e:
            raise ValueError(f"第二希望文字列組み立てエラー: {str(e)}")
    
    def _build_single_choice(self, date: str, time: str, waku_pattern_id: int, prefix: str) -> str:
        """
        単一の希望を組み立て
        
        Args:
            date: 希望日
            time: 希望時間帯
            waku_pattern_id: 枠パターンID (数値)
            prefix: プレフィックス (①, ②, ③)
            
        Returns:
            str: 組み立てられた希望文字列
        """
        if not date or not time:
            return ""
        
        # 日付を変換
        converted_date = self.convert_date_format(date)
        if not converted_date:
            return ""
        
        # 時間帯を解析
        start_time, _ = self.parse_time_input(time)
        if not start_time:
            return ""
        
        # 時間帯名を取得
        ampm = self.get_time_ampm(start_time, waku_pattern_id)
        
        return f"{prefix}{converted_date}{ampm}"
    
    def _build_third_choice(self, date3: str, time3: str, waku_pattern_id: int) -> str:
        """
        第三希望を組み立て
        
        Args:
            date3: 第三希望日
            time3: 第三希望時間帯
            waku_pattern_id: 枠パターンID (数値)
            
        Returns:
            str: 組み立てられた第三希望文字列
        """
        if self.check_third_choice_availability(date3, time3):
            return self._build_single_choice(date3, time3, waku_pattern_id, "③")
        else:
            return "③入力無し"
    
    def parse_second_choice_string(self, second_choice_str: str) -> Dict[str, str]:
        """
        第二希望文字列を解析
        
        Args:
            second_choice_str: 第二希望文字列
            
        Returns:
            Dict[str, str]: 解析された希望情報
        """
        if not second_choice_str:
            return {}
        
        # ①②③で分割
        pattern = r'①(.+?)②(.+?)③(.+)'
        match = re.match(pattern, second_choice_str)
        
        if match:
            first, second, third = match.groups()
            return {
                'first_choice': first.strip(),
                'second_choice': second.strip(),
                'third_choice': third.strip()
            }
        else:
            # フォーマットが不正な場合
            return {
                'first_choice': second_choice_str,
                'second_choice': '',
                'third_choice': ''
            }
    
    def validate_second_choice_input(self, 
                                   date1: str, time1: str,
                                   date2: str, time2: str,
                                   date3: str = "", time3: str = "") -> Dict[str, any]:
        """
        第二希望入力の検証
        
        Args:
            date1: 第一希望日
            time1: 第一希望時間帯
            date2: 第二希望日
            time2: 第二希望時間帯
            date3: 第三希望日
            time3: 第三希望時間帯
            
        Returns:
            Dict[str, any]: 検証結果
        """
        errors = []
        warnings = []
        
        # 第一希望の検証
        if not date1 or not time1:
            errors.append("第一希望の日付と時間帯は必須です")
        
        # 第二希望の検証
        if not date2 or not time2:
            errors.append("第二希望の日付と時間帯は必須です")
        
        # 第三希望の検証
        if date3 and not time3:
            warnings.append("第三希望の日付は入力されていますが、時間帯が入力されていません")
        elif time3 and not date3:
            warnings.append("第三希望の時間帯は入力されていますが、日付が入力されていません")
        
        # 日付形式の検証
        try:
            if date1:
                self.parse_date_input(date1)
            if date2:
                self.parse_date_input(date2)
            if date3:
                self.parse_date_input(date3)
        except ValueError as e:
            errors.append(f"日付形式エラー: {str(e)}")
        
        # 時間帯形式の検証
        try:
            if time1:
                self.parse_time_input(time1)
            if time2:
                self.parse_time_input(time2)
            if time3:
                self.parse_time_input(time3)
        except ValueError as e:
            errors.append(f"時間帯形式エラー: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# 便利関数
def build_second_choice_string(date1: str, time1: str,
                             date2: str, time2: str,
                             date3: str = "", time3: str = "",
                             waku_pattern_id: int = 0) -> str:
    """
    第二希望文字列を組み立て（外部呼び出し用）
    
    Args:
        date1: 第一希望日
        time1: 第一希望時間帯
        date2: 第二希望日
        time2: 第二希望時間帯
        date3: 第三希望日 (オプション)
        time3: 第三希望時間帯 (オプション)
        waku_pattern_id: 枠パターンID (数値)
        
    Returns:
        str: 組み立てられた第二希望文字列
    """
    logic = SecondChoiceContentLogic()
    return logic.build_second_choice_string(date1, time1, date2, time2, date3, time3, waku_pattern_id)


def parse_second_choice_string(second_choice_str: str) -> Dict[str, str]:
    """
    第二希望文字列を解析（外部呼び出し用）
    
    Args:
        second_choice_str: 第二希望文字列
        
    Returns:
        Dict[str, str]: 解析された希望情報
    """
    logic = SecondChoiceContentLogic()
    return logic.parse_second_choice_string(second_choice_str)


def validate_second_choice_input(date1: str, time1: str,
                                date2: str, time2: str,
                                date3: str = "", time3: str = "") -> Dict[str, any]:
    """
    第二希望入力の検証（外部呼び出し用）
    
    Args:
        date1: 第一希望日
        time1: 第一希望時間帯
        date2: 第二希望日
        time2: 第二希望時間帯
        date3: 第三希望日
        time3: 第三希望時間帯
        
    Returns:
        Dict[str, any]: 検証結果
    """
    logic = SecondChoiceContentLogic()
    return logic.validate_second_choice_input(date1, time1, date2, time2, date3, time3)


# テスト用のメイン関数
if __name__ == "__main__":
    # テストデータ
    test_data = {
        'date1': '2025-06-12',
        'time1': '09:00～12:00',
        'date2': '2025-06-13',
        'time2': '13:00～16:00',
        'date3': '2025-06-14',
        'time3': '18:00～21:00',
        'waku_pattern_id': 0
    }
    
    # 枠パターンの設定（元のsystem.propertiesから全パターン移植）
    waku_patterns = {
        0: {
            'Name': '2枠( AM 9:00-12:00, PM 13:00-17:00)',
            'StartTime': ['09:00', '13:00'],
            'EndTime': ['12:00', '17:00'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        1: {
            'Name': '2枠( AM 9:00-12:00, PM 13:00-17:30)',
            'StartTime': ['09:00', '13:00'],
            'EndTime': ['12:00', '17:30'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '30'
        },
        2: {
            'Name': '2枠( AM 9:00-12:00, PM 13:00-18:00)',
            'StartTime': ['09:00', '13:00'],
            'EndTime': ['12:00', '18:00'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        3: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:00, PM2 15:00-17:00)',
            'StartTime': ['09:00', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '17:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        4: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:00, PM2 15:00-17:30)',
            'StartTime': ['09:00', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '17:30'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '30'
        },
        5: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:00, PM2 15:00-18:00)',
            'StartTime': ['09:00', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '18:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        6: {
            'Name': '4枠( AM1 9:00-10:30, AM2 10:30-12:00, PM1 13:00-15:00, PM2 15:00-18:00)',
            'StartTime': ['09:00', '10:30', '13:00', '15:00'],
            'EndTime': ['10:30', '12:00', '15:00', '18:00'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2'],
            'JikanTani': '30'
        },
        7: {
            'Name': '5枠( AM1 9:00-10:30, AM2 10:30-12:00, PM1 13:00-14:30, PM2 14:30-16:00, PM3 16:00-17:30)',
            'StartTime': ['09:00', '10:30', '13:00', '14:30', '16:00'],
            'EndTime': ['10:30', '12:00', '14:30', '16:00', '17:30'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2', 'PM3'],
            'JikanTani': '30'
        },
        8: {
            'Name': '7枠( AM1 9:00-10:00, AM2 10:00-11:00, AM3 11:00-12:00, PM1 13:00-14:00, PM2 14:00-15:00, PM3 15:00-16:00, PM4 16:00-17:00)',
            'StartTime': ['09:00', '10:00', '11:00', '13:00', '14:00', '15:00', '16:00'],
            'EndTime': ['10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00'],
            'AMPM': ['AM1', 'AM2', 'AM3', 'PM1', 'PM2', 'PM3', 'PM4'],
            'JikanTani': '60'
        },
        9: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:30, PM2 15:30-18:00)',
            'StartTime': ['09:00', '13:00', '15:30'],
            'EndTime': ['12:00', '15:30', '18:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '30'
        },
        10: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:15, PM2 15:15-17:30)',
            'StartTime': ['09:00', '13:00', '15:15'],
            'EndTime': ['12:00', '15:15', '17:30'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '15'
        },
        11: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-16:00, PM2 16:00-19:00)',
            'StartTime': ['09:00', '13:00', '16:00'],
            'EndTime': ['12:00', '16:00', '19:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        12: {
            'Name': '3枠( AM 11:00-12:00, PM1 13:00-15:00, PM2 15:00-17:00)',
            'StartTime': ['11:00', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '17:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        13: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:30, PM2 15:30-17:30)',
            'StartTime': ['09:00', '13:00', '15:30'],
            'EndTime': ['12:00', '15:30', '17:30'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '30'
        },
        14: {
            'Name': '2枠( AM 9:00-12:00, PM 13:00-16:00)',
            'StartTime': ['09:00', '13:00'],
            'EndTime': ['12:00', '16:00'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        15: {
            'Name': '5枠( AM 9:00-12:00, PM1 13:00-15:00, PM2 15:00-17:00, PM3 17:00-19:00, PM4 19:00-21:00)',
            'StartTime': ['09:00', '13:00', '15:00', '17:00', '19:00'],
            'EndTime': ['12:00', '15:00', '17:00', '19:00', '21:00'],
            'AMPM': ['AM', 'PM1', 'PM2', 'PM3', 'PM4'],
            'JikanTani': '60'
        },
        16: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:15, PM2 15:15-16:45)',
            'StartTime': ['09:00', '13:00', '15:15'],
            'EndTime': ['12:00', '15:15', '16:45'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '15'
        },
        17: {
            'Name': '10枠( AM1 9:00-09:45, AM2 09:45-10:30, AM3 10:30-11:15, AM4 11:15-12:00, PM1 13:00-13:45, PM2 13:45-14:30, PM3 14:30-15:15, PM4 15:15-16:00, PM5 16:00-16:45, PM6 16:45-17:30)',
            'StartTime': ['09:00', '09:45', '10:30', '11:15', '13:00', '13:45', '14:30', '15:15', '16:00', '16:45'],
            'EndTime': ['09:45', '10:30', '11:15', '12:00', '13:45', '14:30', '15:15', '16:00', '16:45', '17:30'],
            'AMPM': ['AM1', 'AM2', 'AM3', 'AM4', 'PM1', 'PM2', 'PM3', 'PM4', 'PM5', 'PM6'],
            'JikanTani': '15'
        },
        18: {
            'Name': '14枠( AM1 9:00-09:30, AM2 09:30-10:00, AM3 10:00-10:30, AM4 10:30-11:00, AM5 11:00-11:30, AM6 11:30-12:00, PM1 13:00-13:30, PM2 13:30-14:00, PM3 14:00-14:30, PM4 14:30-15:00, PM5 15:00-15:30, PM6 15:30-16:00, PM7 16:00-16:30, PM8 16:30-17:00)',
            'StartTime': ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'],
            'EndTime': ['09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00'],
            'AMPM': ['AM1', 'AM2', 'AM3', 'AM4', 'AM5', 'AM6', 'PM1', 'PM2', 'PM3', 'PM4', 'PM5', 'PM6', 'PM7', 'PM8'],
            'JikanTani': '30'
        },
        19: {
            'Name': '作業時間 (8:30-17:30)',
            'StartTime': ['09:00', '12:00'],
            'EndTime': ['12:00', '17:30'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '30'
        },
        20: {
            'Name': '4枠( AM1 9:00-10:30, AM2 10:30-12:00, PM1 13:00-15:00, PM2 15:00-17:00)',
            'StartTime': ['09:00', '10:30', '13:00', '15:00'],
            'EndTime': ['10:30', '12:00', '15:00', '17:00'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2'],
            'JikanTani': '30'
        },
        21: {
            'Name': '10枠( AM1 9:00-10:00, AM2 10:00-11:00, AM3 11:00-12:00, PM1 13:00-14:00, PM2 14:00-15:00, PM3 15:00-16:00, PM4 16:00-17:00, PM5 17:00-18:00, PM6 18:00-19:00, PM7 19:00-20:00)',
            'StartTime': ['09:00', '10:00', '11:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00'],
            'EndTime': ['10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00'],
            'AMPM': ['AM1', 'AM2', 'AM3', 'PM1', 'PM2', 'PM3', 'PM4', 'PM5', 'PM6', 'PM7'],
            'JikanTani': '60'
        },
        22: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-16:00, PM2 16:00-18:00)',
            'StartTime': ['09:00', '13:00', '16:00'],
            'EndTime': ['12:00', '16:00', '18:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        23: {
            'Name': '8枠( AM1 9:00-10:00, AM2 10:00-11:00, AM3 11:00-12:00, PM1 13:00-14:00, PM2 14:00-15:00, PM3 15:00-16:00, PM4 16:00-17:00, PM5 17:00-18:00)',
            'StartTime': ['09:00', '10:00', '11:00', '13:00', '14:00', '15:00', '16:00', '17:00'],
            'EndTime': ['10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00', '18:00'],
            'AMPM': ['AM1', 'AM2', 'AM3', 'PM1', 'PM2', 'PM3', 'PM4', 'PM5'],
            'JikanTani': '60'
        },
        24: {
            'Name': '1枠(9:00-17:00)',
            'StartTime': ['09:00'],
            'EndTime': ['17:00'],
            'AMPM': ['終日'],
            'JikanTani': '60'
        },
        25: {
            'Name': '3枠( AM 09:00-12:00, PM1 13:00-16:00, PM2 16:00-20:00)',
            'StartTime': ['09:00', '13:00', '16:00'],
            'EndTime': ['12:00', '16:00', '20:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        26: {
            'Name': '4枠( AM1 09:00-11:00, AM2 11:15-13:15, PM1 13:30-15:30, PM2 15:45-17:45)',
            'StartTime': ['09:00', '11:15', '13:30', '15:45'],
            'EndTime': ['11:00', '13:15', '15:30', '17:45'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        27: {
            'Name': '5枠( AM1 09:00-10:30, AM2 10:45-12:15, PM1 12:30-14:00, PM2 14:15-15:30, PM3 15:45-17:00)',
            'StartTime': ['09:00', '10:45', '12:30', '14:15', '15:45'],
            'EndTime': ['10:30', '12:15', '14:00', '15:30', '17:00'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2', 'PM3'],
            'JikanTani': '60'
        },
        28: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:15, PM2 15:15-18:15)',
            'StartTime': ['09:00', '13:00', '15:15'],
            'EndTime': ['12:00', '15:15', '18:15'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '15'
        },
        29: {
            'Name': '3枠( AM 9:30-12:00, PM1 13:00-15:00, PM2 15:00-16:30)',
            'StartTime': ['09:30', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '16:30'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        30: {
            'Name': '5枠( AM1 09:00-10:30, AM2 10:30-12:00, PM1 13:00-14:20, PM2 14:20-15:40, PM3 15:40-17:00)',
            'StartTime': ['09:00', '10:30', '13:00', '14:20', '15:40'],
            'EndTime': ['10:30', '12:00', '14:20', '15:40', '17:00'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2', 'PM3'],
            'JikanTani': '60'
        },
        31: {
            'Name': '3枠( AM 09:00-12:00, PM1 13:00-15:15, PM2 15:15-17:00)',
            'StartTime': ['09:00', '13:00', '15:15'],
            'EndTime': ['12:00', '15:15', '17:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        32: {
            'Name': '3枠( AM 09:00-12:00, PM1 13:00-16:00, PM2 16:00-18:00)',
            'StartTime': ['09:00', '13:00', '16:00'],
            'EndTime': ['12:00', '16:00', '18:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        33: {
            'Name': '3枠( AM 09:00-12:00, PM1 13:00-15:00, PM2 15:00-16:00)',
            'StartTime': ['09:00', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '16:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        34: {
            'Name': '2枠( AM 9:00-12:00, PM 13:00-16:45)',
            'StartTime': ['09:00', '13:00'],
            'EndTime': ['12:00', '16:45'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        35: {
            'Name': '3枠( AM 09:00-12:00, PM1 13:00-15:15, PM2 15:15-17:00)',
            'StartTime': ['09:00', '13:00', '15:15'],
            'EndTime': ['12:00', '15:15', '17:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        36: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:30, PM2 15:30-17:00)',
            'StartTime': ['09:00', '13:00', '15:30'],
            'EndTime': ['12:00', '15:30', '17:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        37: {
            'Name': '3枠( AM 9:30-12:00, PM1 13:00-15:00, PM2 15:00-17:00)',
            'StartTime': ['09:30', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '17:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        38: {
            'Name': '2枠( AM 8:00-12:00, PM 13:00-18:00)',
            'StartTime': ['08:00', '13:00'],
            'EndTime': ['12:00', '18:00'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        39: {
            'Name': '9枠( AM1 8:00-9:00,  AM2 9:00-10:00, AM3 10:00-11:00, AM4 11:00-12:00, PM1 13:00-14:00, PM2 14:00-15:00, PM3 15:00-16:00, PM4 16:00-17:00, PM5 17:00-18:00)',
            'StartTime': ['08:00', '09:00', '10:00', '11:00', '13:00', '14:00', '15:00', '16:00', '17:00'],
            'EndTime': ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00', '18:00'],
            'AMPM': ['AM1', 'AM2', 'AM3', 'AM4', 'PM1', 'PM2', 'PM3', 'PM4', 'PM5'],
            'JikanTani': '60'
        },
        40: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:00, PM2 15:00-16:30)',
            'StartTime': ['09:00', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '16:30'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        41: {
            'Name': '4枠( AM1 9:00-11:00, AM2 11:00-13:00, PM1 14:00-16:00, PM2 16:00-18:00)',
            'StartTime': ['09:00', '11:00', '14:00', '16:00'],
            'EndTime': ['11:00', '13:00', '16:00', '18:00'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        42: {
            'Name': '2枠( AM 9:00-12:00, PM 13:00-15:00)',
            'StartTime': ['09:00', '13:00'],
            'EndTime': ['12:00', '15:00'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        43: {
            'Name': '2枠( AM 9:00-12:00, PM 13:00-16:30)',
            'StartTime': ['09:00', '13:00'],
            'EndTime': ['12:00', '16:30'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        44: {
            'Name': '9枠( AM1 9:00-09:45, AM2 9:45-10:30, AM3 10:30-11:15, AM4 11:15-12:00, PM1 13:00-13:45, PM2 13:45-14:30, PM3 14:30-15:30, PM4 15:30-16:15, PM5 16:15-17:00)',
            'StartTime': ['09:00', '09:45', '10:30', '11:15', '13:00', '13:45', '14:30', '15:30', '16:15'],
            'EndTime': ['09:45', '10:30', '11:15', '12:00', '13:45', '14:30', '15:30', '16:15', '17:00'],
            'AMPM': ['AM1', 'AM2', 'AM3', 'AM4', 'PM1', 'PM2', 'PM3', 'PM4', 'PM5'],
            'JikanTani': '15'
        },
        45: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:30, PM2 15:30-16:30)',
            'StartTime': ['09:00', '13:00', '15:30'],
            'EndTime': ['12:00', '15:30', '16:30'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        46: {
            'Name': '3枠( AM 11:00-12:00, PM1 13:00-15:00, PM2 15:00-17:30)',
            'StartTime': ['11:00', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '17:30'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        47: {
            'Name': '2枠( AM 10:00-12:00, PM 13:00-16:00)',
            'StartTime': ['10:00', '13:00'],
            'EndTime': ['12:00', '16:00'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        48: {
            'Name': '2枠( AM 09:30-12:00, PM 13:00-16:30)',
            'StartTime': ['09:30', '13:00'],
            'EndTime': ['12:00', '16:30'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        49: {
            'Name': '2枠( AM 10:00-12:00, PM 13:00-17:00)',
            'StartTime': ['10:00', '13:00'],
            'EndTime': ['12:00', '17:00'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        50: {
            'Name': '2枠( AM 9:00-12:00, PM 13:00-15:30)',
            'StartTime': ['09:00', '13:00'],
            'EndTime': ['12:00', '15:30'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        51: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-16:00, PM2 16:00-17:00)',
            'StartTime': ['09:00', '13:00', '16:00'],
            'EndTime': ['12:00', '16:00', '17:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        52: {
            'Name': '2枠( AM 10:00-12:00, PM 13:00-15:00)',
            'StartTime': ['10:00', '13:00'],
            'EndTime': ['12:00', '15:00'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        53: {
            'Name': '4枠( AM1 9:00-10:30,  AM2 10:30-12:00, PM1 13:00-14:30, PM2 14:30-16:00)',
            'StartTime': ['09:00', '10:30', '13:00', '14:30'],
            'EndTime': ['10:30', '12:00', '14:30', '16:00'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        54: {
            'Name': '3枠( AM 8:30-12:00, PM1 13:00-15:00, PM2 15:00-17:30)',
            'StartTime': ['08:30', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '17:30'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        55: {
            'Name': '5枠( AM1 9:00-10:30,  AM2 10:30-12:00, PM1 13:00-14:30, PM2 14:30-16:00, PM2 16:00-17:00)',
            'StartTime': ['09:00', '10:30', '13:00', '14:30', '16:00'],
            'EndTime': ['10:30', '12:00', '14:30', '16:00', '17:00'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2', 'PM3'],
            'JikanTani': '60'
        },
        56: {
            'Name': '3枠( AM 10:00-12:00, PM1 13:00-15:00, PM2 15:00-17:00)',
            'StartTime': ['10:00', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '17:00'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        57: {
            'Name': '4枠( AM 8:30-12:00,  PM1 13:00-15:00, PM2 15:00-17:00, PM3 17:00-19:30)',
            'StartTime': ['08:30', '13:00', '15:00', '17:00'],
            'EndTime': ['12:00', '15:00', '17:00', '19:30'],
            'AMPM': ['AM', 'PM1', 'PM2', 'PM3'],
            'JikanTani': '60'
        },
        58: {
            'Name': '4枠( AM1 9:30-11:30,  AM2 11:30-13:30, PM1 13:30-15:30, PM2 15:30-17:30)',
            'StartTime': ['09:30', '11:30', '13:30', '15:30'],
            'EndTime': ['11:30', '13:30', '15:30', '17:30'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        59: {
            'Name': '3枠( AM 09:00-13:00, PM1 13:30-15:30, PM2 15:30-17:30)',
            'StartTime': ['09:00', '13:30', '15:30'],
            'EndTime': ['13:00', '15:30', '17:30'],
            'AMPM': ['AM', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        60: {
            'Name': '5枠( AM1 9:00-10:30, AM2 10:30-12:00, PM1 13:00-14:20, PM2 14:20-15:40, PM3 15:40-17:00)',
            'StartTime': ['09:00', '10:30', '13:00', '14:20', '15:40'],
            'EndTime': ['10:30', '12:00', '14:20', '15:40', '17:00'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2', 'PM3'],
            'JikanTani': '60'
        },
        61: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-15:00, PM2 15:00-19:00)',
            'StartTime': ['09:00', '13:00', '15:00'],
            'EndTime': ['12:00', '15:00', '19:00'],
            'AMPM': ['AM1', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        62: {
            'Name': '4枠( AM1 9:00-10:30,  AM2 10:30-12:00, PM1 13:00-15:15, PM2 15:15-16:45)',
            'StartTime': ['09:00', '10:30', '13:00', '15:15'],
            'EndTime': ['10:30', '12:00', '15:15', '16:45'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        63: {
            'Name': '2枠( AM 08:40-12:00, PM 13:00-17:00)',
            'StartTime': ['08:40', '13:00'],
            'EndTime': ['12:00', '17:00'],
            'AMPM': ['AM', 'PM'],
            'JikanTani': '60'
        },
        64: {
            'Name': '3枠( AM 9:00-12:00, PM1 13:00-14:30, PM2 14:30-17:30)',
            'StartTime': ['09:00', '13:00', '14:30'],
            'EndTime': ['12:00', '14:30', '17:30'],
            'AMPM': ['AM1', 'PM1', 'PM2'],
            'JikanTani': '60'
        },
        65: {
            'Name': '6枠( AM1 9:00-10:00,  AM2 10:00-11:00, PM1 12:00-13:00, PM2 13:00-14:00, PM3 14:00-15:00, PM4 15:00-16:00)',
            'StartTime': ['09:00', '10:00', '12:00', '13:00', '14:00', '15:00'],
            'EndTime': ['10:00', '11:00', '13:00', '14:00', '15:00', '16:00'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2', 'PM3', 'PM4'],
            'JikanTani': '60'
        },
        66: {
            'Name': '4枠( AM1 9:00-10:30,  AM2 10:30-12:00, PM1 13:00-15:00, PM2 15:00-16:30)',
            'StartTime': ['09:00', '10:30', '13:00', '15:00'],
            'EndTime': ['10:30', '12:00', '15:00', '16:30'],
            'AMPM': ['AM1', 'AM2', 'PM1', 'PM2'],
            'JikanTani': '60'
        }
    }
    
    # テスト実行
    logic = SecondChoiceContentLogic()
    logic.set_waku_patterns(waku_patterns)
    
    # 文字列組み立てテスト
    result = logic.build_second_choice_string(
        test_data['date1'], test_data['time1'],
        test_data['date2'], test_data['time2'],
        test_data['date3'], test_data['time3'],
        test_data['waku_pattern_id']
    )
    
    print(f"組み立て結果: {result}")
    
    # 文字列解析テスト
    parsed = logic.parse_second_choice_string(result)
    print(f"解析結果: {parsed}")
    
    # 入力検証テスト
    validation = logic.validate_second_choice_input(
        test_data['date1'], test_data['time1'],
        test_data['date2'], test_data['time2'],
        test_data['date3'], test_data['time3']
    )
    
    print(f"検証結果: {validation}")
