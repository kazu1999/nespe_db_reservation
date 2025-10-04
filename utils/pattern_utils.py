"""
枠パターン関連のユーティリティ関数
"""
import requests
import json
from utils.db_utils import DBUtils


class PatternUtils:
    """枠パターン関連の処理をまとめたユーティリティクラス"""
    
    @staticmethod
    def get_minute_unit(building_id, connection):
        """分単位を取得"""
        try:
            row = DBUtils.execute_single_query(connection, "SELECT MinuteUnit FROM tSettingM WHERE ClientCD = %s", (building_id,))
            if row and row.get('MinuteUnit') not in (None, '', 0, '0'):
                return int(row['MinuteUnit'])
            return 60  # デフォルト値
        except Exception:
            return 60  # デフォルト値
    
    @staticmethod
    def get_minute_type(menu_cd, building_id, connection):
        """メニューの分タイプを取得"""
        try:
            sql = "SELECT MinuteType FROM tMenuM WHERE MenuCD = %s AND ClientCD = %s AND MukouFlg = 0"
            row = DBUtils.execute_single_query(connection, sql, (menu_cd, building_id))
            return int(row['MinuteType']) if row and row.get('MinuteType') else 1
        except Exception:
            return 1  # デフォルト値
    
    @staticmethod
    def get_waku_pattern_id(building_id, connection):
        """枠パターンIDを取得"""
        # WakuPatternIDではなくWakuPatternを取得するように修正
        try:
            row = DBUtils.execute_single_query(connection, "SELECT WakuPattern FROM tSettingM WHERE ClientCD = %s", (building_id))
            if row and 'WakuPattern' in row:
                return row['WakuPattern']
        except Exception:
            return None
    
    @staticmethod
    def load_wakupatterns_from_php():
        """PHPスクリプトから枠パターンを読み込み"""
        try:
            # PHPスクリプトのURL（実際の環境に合わせて調整）
            php_url = "http://localhost/wakupatterns.php"  # 実際のURLに変更
            
            response = requests.get(php_url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                # フォールバック: デフォルトパターン
                return PatternUtils._get_default_patterns()
        except Exception:
            # フォールバック: デフォルトパターン
            return PatternUtils._get_default_patterns()
    
    @staticmethod
    def _get_default_patterns():
        """デフォルトの枠パターンを返す"""
        return [
            {
                "StartTime": ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"],
                "EndTime": ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
            }
        ]
    
    @staticmethod
    def get_pattern_info(building_id, connection):
        """枠パターン情報を取得"""
        try:
            waku_pattern_id = PatternUtils.get_waku_pattern_id(building_id, connection)
            wakupatterns = PatternUtils.load_wakupatterns_from_php()
            
            if waku_pattern_id is None or waku_pattern_id >= len(wakupatterns):
                return None
            
            pattern = wakupatterns[waku_pattern_id]
            return {
                'pattern_id': waku_pattern_id,
                'pattern': pattern,
                'start_times': pattern.get("StartTime", []),
                'end_times': pattern.get("EndTime", [])
            }
        except Exception:
            return None
