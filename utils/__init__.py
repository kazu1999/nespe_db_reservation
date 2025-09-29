# Utility functions for reservation

import logging


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


__all__ = [
    "handle_db_exception",
]
