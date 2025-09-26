"""
枠パターン関連のユーティリティ関数
"""
from chatbot_scripts.logic.wakupattern import get_waku_pattern_id, load_wakupatterns_from_php
from chatbot_scripts.models.reservation.reservation_pattern_utils import WakuPatternHelper


class PatternUtils:
    """枠パターン関連の処理をまとめたユーティリティクラス"""
    
    @staticmethod
    def get_minute_unit(building_id, connection):
        """分単位を取得（短縮版）"""
        try:
            return WakuPatternHelper.get_minute_unit(building_id, connection)
        except ImportError:
            # フォールバック実装（簡略化）
            with connection.cursor() as cursor:
                cursor.execute("SELECT MinuteUnit FROM tSettingM WHERE ClientCD = %s", (building_id,))
                row = cursor.fetchone()
                if row and row.get('MinuteUnit') not in (None, '', 0, '0'):
                    return int(row['MinuteUnit'])
                return 60  # デフォルト値
    
    @staticmethod
    def get_minute_type(menu_cd, building_id, connection):
        """メニューの分タイプを取得"""
        with connection.cursor() as cursor:
            sql = "SELECT MinuteType FROM tMenuM WHERE MenuCD = %s AND ClientCD = %s AND MukouFlg = 0"
            cursor.execute(sql, (menu_cd, building_id))
            row = cursor.fetchone()
            return int(row['MinuteType']) if row and row.get('MinuteType') else 1
    
    @staticmethod
    def get_pattern_info(building_id, connection):
        """枠パターン情報を取得"""
        try:
            return WakuPatternHelper.get_pattern_info(building_id, connection)
        except ImportError:
            # フォールバック実装
            waku_pattern_id = get_waku_pattern_id(building_id, connection)
            wakupatterns = load_wakupatterns_from_php()
            if waku_pattern_id is None or waku_pattern_id >= len(wakupatterns):
                return None
            pattern = wakupatterns[waku_pattern_id]
            return {
                'pattern_id': waku_pattern_id,
                'pattern': pattern,
                'start_times': pattern.get("StartTime", []),
                'end_times': pattern.get("EndTime", [])
            }
