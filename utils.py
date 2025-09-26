import json
import logging
import re
import requests
try:
    import fasttext
    fasttext_model = fasttext.load_model('lid.176.bin')  # fastTextの言語識別モデル（要ダウンロード）
except Exception:
    fasttext = None
    fasttext_model = None

def to_json(data):
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return ""

def from_json(data):
    try:
        return json.loads(data)
    except Exception:
        return None

def safe_json_loads(data):
    for _ in range(5):
        if isinstance(data, str):
            try:
                data = from_json(data)
            except Exception:
                break
        else:
            break
    return data if isinstance(data, dict) else {}

def format_with_weekday(dt_or_str) -> str:
    """
    日付(datetimeまたはstr)を「YYYY年MM月DD日（曜）HH:MM」形式で日本語曜日付きで返す
    """
    import datetime
    if isinstance(dt_or_str, str):
        try:
            from dateutil.parser import parse
            dt = parse(dt_or_str, fuzzy=True)
        except Exception:
            return dt_or_str  # パースできなければそのまま返す
    else:
        dt = dt_or_str
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    weekday = weekdays[dt.weekday()]
    return dt.strftime(f"%Y年%m月%d日（{weekday}）%H:%M")

class DatabaseManager:
    """データベース接続を一元管理するクラス"""
    _connections = {}

    @classmethod
    def get_connection(cls, db_name: str):
        import pymysql
        import os
        # db_nameによって接続先を切り替える
        if db_name == 'chatbot_db':
            DB_HOST = os.getenv("DB_HOST_chatbot")
            DB_USER = os.getenv("DB_USER_chatbot")
            DB_PASSWORD = os.getenv("DB_PASSWORD_chatbot")
            DB_NAME_MAIN = os.getenv("DB_NAME_MAIN_chatbot")
            DB_CHARSET = os.getenv("DB_CHARSET_chatbot")
        else:
            DB_HOST = os.getenv("DB_HOST")
            DB_USER = os.getenv("DB_USER")
            DB_PASSWORD = os.getenv("DB_PASSWORD")
            DB_NAME_MAIN = os.getenv("DB_NAME_MAIN")
            DB_CHARSET = os.getenv("DB_CHARSET")

        if db_name not in cls._connections:
            try:
                cls._connections[db_name] = pymysql.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    db=db_name,
                    charset=DB_CHARSET,
                    cursorclass=pymysql.cursors.DictCursor
                )
            except pymysql.MySQLError as e:
                logging.error("[ERROR] Failed to connect to database %s: %s", db_name, e)
                raise
        else:
            try:
                cls._connections[db_name].ping(reconnect=True)
            except Exception as e:
                cls._connections[db_name] = pymysql.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    db=db_name,
                    charset=DB_CHARSET,
                    cursorclass=pymysql.cursors.DictCursor
                )
        return cls._connections[db_name]

    @classmethod
    def close_all(cls):
        for conn in cls._connections.values():
            try:
                conn.close()
            except Exception as e:
                logging.error("[ERROR] Failed to close database connection: %s", e)
        cls._connections.clear()

def handle_db_exception(e, context_message=None, input_params=None, sql=None):
    """
    DB例外発生時の共通エラーハンドラ。
    エラー内容・入力値・SQL・スタックトレースをログ出力し、ユーザー向けエラー辞書を返す。
    """
    import traceback
    error_log = f"[DB ERROR] {context_message or ''}\n"
    error_log += f"Exception: {e}\n"
    if input_params:
        error_log += f"Input: {input_params}\n"
    if sql:
        error_log += f"SQL: {sql}\n"
    error_log += f"Traceback:\n{traceback.format_exc()}"
    logging.error(error_log)
    return {"error": "データベースエラーが発生しました。運営までご連絡ください。"}

class DateTimeHandler:
    """日付時刻処理を一元管理するクラス"""
    import datetime
    JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

    @classmethod
    def now_jst(cls) -> "datetime.datetime":
        import datetime
        return datetime.datetime.now(cls.JST)

    @classmethod
    def parse_datetime(cls, text: str) -> "datetime.datetime":
        from dateutil.parser import parse
        dt = parse(text, fuzzy=True)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=cls.JST)
        else:
            dt = dt.astimezone(cls.JST)
        return dt

    @classmethod
    def format_datetime(cls, dt: "datetime.datetime", fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=cls.JST)
        else:
            dt = dt.astimezone(cls.JST)
        return dt.strftime(fmt)

    @classmethod
    def check_within_period(cls, now: "datetime.datetime", start: str, end: str) -> dict:
        try:
            start_dt = cls.parse_datetime(start)
            end_dt = cls.parse_datetime(end)
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
        except Exception as e:
            return {"error": f"日付の解析に失敗しました: {e}"}
        if now < start_dt:
            return {"error": "現在は受付期間外です。", "reason": "受付開始前です。"}
        if now > end_dt:
            return {"error": "現在は受付期間外です。", "reason": "受付期間は終了しています。"}
        return {"ok": True}

def reset_session(session_data_dict, keep_keys=None):
    """
    セッションリセット時に指定したキーのみ保持し、auth_statusを'reset'にする共通関数。
    デフォルトはuser_languageのみ保持。
    """
    if keep_keys is None:
        keep_keys = ["user_language"]
    new_session = {k: session_data_dict[k] for k in keep_keys if k in session_data_dict}
    new_session["auth_status"] = "reset"
    return new_session

def normalize_phone_number(phone: str) -> str:
    """
    電話番号を全角→半角、数字以外除去、ハイフン付与（携帯/市外局番対応）で正規化
    """
    # 全角→半角
    phone = phone.translate(str.maketrans(
        '０１２３４５６７８９－ー―−',
        '0123456789----'
    ))
    # 数字以外除去
    phone = re.sub(r'[^0-9]', '', phone)
    # ハイフン付与
    if phone.startswith('0'):
        if len(phone) == 11:  # 携帯
            return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
        elif len(phone) == 10:
            if phone[:2] in ['03', '06']:
                return f"{phone[:2]}-{phone[2:6]}-{phone[6:]}"
            else:
                return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    return phone

def send_slack_notification(message: str, hook_url: str) -> bool:
    """
    指定したSlackのWebhook URLにメッセージを送信する関数
    """
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {"text": message}
        response = requests.post(hook_url, headers=headers, data=json.dumps(payload))
        return response.status_code == 200
    except Exception as e:
        logging.error(f"[Slack通知エラー] {e}")
        return False
