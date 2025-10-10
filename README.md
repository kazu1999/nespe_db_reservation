# ishoku フォルダー

## 概要
第一希望更新、第二希望更新、予約日程取得の3つの機能を独立したPythonファイルとして移植したフォルダーです。

## ファイル構成

### メインファイル（認証なし版）
- **first_choice_updater.py** - 第一希望更新機能（認証なし）
- **second_choice_updater.py** - 第二希望更新機能（認証なし）
- **reservation_fetcher.py** - 予約日程取得機能（認証なし）
- **get_building_name.py** - `ClientCD` から建物名（MansionName）取得（認証なし）

### メインファイル（認証あり版）
- **first_choice_updater_password.py** - 第一希望更新機能（認証あり）
- **second_choice_updater_password.py** - 第二希望更新機能（認証あり）
- **reservation_fetcher_password.py** - 予約日程取得機能（認証あり）
- **get_building_name_password.py** - 認証後に建物名（MansionName）取得（認証あり）

### 依存ファイル
- **user.py** - ユーザー認証機能
- **taio_record.py** - 対応履歴記録機能
- **connection.py** - データベース接続機能（`utils/db_utils.py` から呼び出し）
- **utils/** - パッケージ。`from utils import handle_db_exception` が利用可能
- **utils.py** - 追加ユーティリティ（パッケージ `utils/` とは別。基本は参照不要）

### utilsフォルダー
- **utils/__init__.py** - 共通公開関数（`handle_db_exception` をエクスポート）
- **utils/db_utils.py** - データベース操作ユーティリティ（接続はローカルの `connection.get_connection` を使用）
- **utils/pattern_utils.py** - パターン処理ユーティリティ
- **utils/time_utils.py** - 時間処理ユーティリティ

## 使用方法（抜粋）

### 建物名取得（認証なし）
```bash
python get_building_name.py 3760
```
Python から:
```python
from get_building_name import get_building_name
name = get_building_name("3760")
print(name)
```

### 建物名取得（認証あり）
```bash
python get_building_name_password.py 103 password123 3760
```
Python から:
```python
from get_building_name_password import get_building_name
res = get_building_name("103", "password123", "3760")
print(res)
# {"result":"ok","mansion_name":"..."} or {"error":"..."}
```

### API（FastAPI）
- サーバー起動: `uvicorn app.main:app --reload`
- 仕様・エンドポイント: `app/server.md` を参照
- 本番ベースURL: `https://call-api.489501.jp/nespe_db_reservation`

## セットアップ

### 必要なライブラリのインストール

#### 1. 最小限のインストール（推奨）
```bash
pip install -r requirements-minimal.txt
```

#### 2. 完全版のインストール（開発用）
```bash
pip install -r requirements.txt
```

#### 3. 仮想環境でのインストール（推奨）
```bash
python -m venv ishoku_env
source ishoku_env/bin/activate  # Mac/Linux
# Windows: ishoku_env\Scripts\activate
pip install -r requirements-minimal.txt
```

### データベース接続テスト

```bash
# データベース接続をテスト
python connection.py
```

## 使用方法

### 基本的なインポート

#### 認証なし版（推奨）
```python
# 第一希望更新機能（認証なし）
from first_choice_updater import update_first_choice, get_available_slots

# 第二希望更新機能（認証なし）
from second_choice_updater import update_second_choice, get_current_second_choice, clear_second_choice

# 予約日程取得機能（認証なし）
from reservation_fetcher import get_reservation_date, get_reservation_history, get_reservation_status
```

#### 認証あり版
```python
# 第一希望更新機能（認証あり）
from first_choice_updater_password import update_first_choice, get_available_slots

# 第二希望更新機能（認証あり）
from second_choice_updater_password import update_second_choice, get_current_second_choice, clear_second_choice

# 予約日程取得機能（認証あり）
from reservation_fetcher_password import get_reservation_date, get_reservation_history, get_reservation_status
```

### 第一希望更新の使用例

#### 認証なし版（推奨）
```python
from first_choice_updater import update_first_choice, get_available_slots

# 利用可能な時間枠を取得
slots = get_available_slots("12345", "2024-01-15")
print(f"利用可能な時間枠: {slots}")

# 第一希望を更新（認証不要）
result = update_first_choice("101", "12345", "2024-01-15 10:00")
if "error" in result:
    print(f"エラー: {result['error']}")
else:
    print(f"更新成功: {result['message']}")
```

#### 認証あり版
```python
from first_choice_updater_password import update_first_choice, get_available_slots

# 利用可能な時間枠を取得
slots = get_available_slots("12345", "2024-01-15")
print(f"利用可能な時間枠: {slots}")

# 第一希望を更新（認証必要）
result = update_first_choice("101", "password123", "12345", "2024-01-15 10:00")
if "error" in result:
    print(f"エラー: {result['error']}")
else:
    print(f"更新成功: {result['message']}")
```

### 第二希望更新の使用例

#### 認証なし版（推奨）
```python
from second_choice_updater import update_second_choice, get_current_second_choice, clear_second_choice

# 現在の第二希望を取得（認証不要）
current = get_current_second_choice("101", "12345")
print(f"現在の第二希望: {current}")

# 第二希望を更新（認証不要）
result = update_second_choice("101", "12345", "午前中希望、午後は不可")
if "error" in result:
    print(f"エラー: {result['error']}")
else:
    print(f"更新成功: {result['message']}")

# 第二希望をクリア（認証不要）
clear_result = clear_second_choice("101", "12345")
print(f"クリア結果: {clear_result}")
```

#### 認証あり版
```python
from second_choice_updater_password import update_second_choice, get_current_second_choice, clear_second_choice

# 現在の第二希望を取得（認証必要）
current = get_current_second_choice("101", "password123", "12345")
print(f"現在の第二希望: {current}")

# 第二希望を更新（認証必要）
result = update_second_choice("101", "password123", "12345", "午前中希望、午後は不可")
if "error" in result:
    print(f"エラー: {result['error']}")
else:
    print(f"更新成功: {result['message']}")

# 第二希望をクリア（認証必要）
clear_result = clear_second_choice("101", "password123", "12345")
print(f"クリア結果: {clear_result}")
```

### 予約日程取得の使用例

#### 認証なし版（推奨）
```python
from reservation_fetcher import get_reservation_date, get_reservation_status, get_reservation_summary

# 予約日程を取得（認証不要）
date_result = get_reservation_date("101", "12345")
print(f"予約日程: {date_result}")

# 予約状況を取得（認証不要）
status_result = get_reservation_status("101", "12345")
print(f"予約状況: {status_result}")

# 予約サマリーを取得（認証不要）
summary_result = get_reservation_summary("101", "12345")
print(f"予約サマリー: {summary_result}")
```

#### 認証あり版
```python
from reservation_fetcher_password import get_reservation_date, get_reservation_status, get_reservation_summary

# 予約日程を取得（認証必要）
date_result = get_reservation_date("101", "password123", "12345")
print(f"予約日程: {date_result}")

# 予約状況を取得（認証必要）
status_result = get_reservation_status("101", "password123", "12345")
print(f"予約状況: {status_result}")

# 予約サマリーを取得（認証必要）
summary_result = get_reservation_summary("101", "password123", "12345")
print(f"予約サマリー: {summary_result}")
```

## 各ファイルの主要機能

### 認証なし版（推奨）

#### first_choice_updater.py
- `update_first_choice(room_number, building_id, new_datetime)`: 第一希望の日時を更新
- `get_available_slots(building_id, date)`: 利用可能な時間枠を取得

#### second_choice_updater.py
- `update_second_choice(room_number, building_id, second_choice_text)`: 第二希望を更新
- `get_current_second_choice(room_number, building_id)`: 現在の第二希望を取得
- `clear_second_choice(room_number, building_id)`: 第二希望をクリア
- `get_second_choice_history(room_number, building_id, limit)`: 第二希望の変更履歴を取得

#### reservation_fetcher.py
- `get_reservation_date(room_number, building_id)`: 予約日程を取得
- `get_reservation_history(room_number, building_id, limit)`: 予約履歴を取得
- `get_reservation_status(room_number, building_id)`: 予約状況を取得
- `get_upcoming_reservations(room_number, building_id, days_ahead)`: 今後の予約を取得
- `get_reservation_summary(room_number, building_id)`: 予約サマリーを取得
  - 実装メモ: デコレータ付き関数の内部呼び出しでは `connection=...` のキーワード引数で渡しています

### 認証あり版

#### first_choice_updater_password.py
- `update_first_choice(room_number, password, building_id, new_datetime)`: 第一希望の日時を更新
- `get_available_slots(building_id, date)`: 利用可能な時間枠を取得

#### second_choice_updater_password.py
- `update_second_choice(room_number, password, building_id, second_choice_text)`: 第二希望を更新
- `get_current_second_choice(room_number, password, building_id)`: 現在の第二希望を取得
- `clear_second_choice(room_number, password, building_id)`: 第二希望をクリア
- `get_second_choice_history(room_number, password, building_id, limit)`: 第二希望の変更履歴を取得

#### reservation_fetcher_password.py
- `get_reservation_date(room_number, password, building_id)`: 予約日程を取得
- `get_reservation_history(room_number, password, building_id, limit)`: 予約履歴を取得
- `get_reservation_status(room_number, password, building_id)`: 予約状況を取得
- `get_upcoming_reservations(room_number, password, building_id, days_ahead)`: 今後の予約を取得
- `get_reservation_summary(room_number, password, building_id)`: 予約サマリーを取得
  - 実装メモ: デコレータ付き関数の内部呼び出しでは `connection=...` のキーワード引数で渡しています

## 戻り値の形式

### 成功時
```python
{
    "result": "ok",
    "message": "処理が完了しました",
    # その他のデータ
}
```

### エラー時
```python
{
    "error": "エラーメッセージ"
}
```

## 注意事項

### 認証なし版（推奨）
1. **認証不要**: 部屋番号と物件IDのみで動作します
2. **データベース接続**: 各ファイルは独立して動作しますが、データベース接続が必要です
3. **エラーハンドリング**: 各関数は適切なエラーハンドリングを行います
4. **ログ記録**: 更新操作は自動的にログに記録されます
5. **空き枠/営業時間**: 営業時間設定（`tSettingM`）と空き枠（スタイリスト枠・`WakuRange`・予約件数）を考慮

### 認証あり版
1. **認証必要**: 部屋番号・パスワード・物件IDの認証が必要です
2. **データベース接続**: 各ファイルは独立して動作しますが、データベース接続が必要です
3. **エラーハンドリング**: 各関数は適切なエラーハンドリングを行います
4. **ログ記録**: 更新操作は自動的にログに記録されます
5. **空き枠/営業時間**: 認証後に同様の検証・チェックを実施

## テスト実行

各ファイルは独立してテスト実行可能です：

### 認証なし版（推奨）
```bash
# 第一希望更新機能のテスト
python first_choice_updater.py

# 第二希望更新機能のテスト
python second_choice_updater.py

# 予約日程取得機能のテスト
python reservation_fetcher.py
```

### 認証あり版
```bash
# 第一希望更新機能のテスト（認証あり）
python first_choice_updater_password.py

# 第二希望更新機能のテスト（認証あり）
python second_choice_updater_password.py

# 予約日程取得機能のテスト（認証あり）
python reservation_fetcher_password.py
```

## 依存関係

- **user.py**: 認証機能
- **taio_record.py**: ログ記録機能
- **utils/__init__.py**: エラーハンドリング（`handle_db_exception`）
- **connection.py**: データベース接続
- **utils/**: ユーティリティ機能（db_utils, pattern_utils, time_utils）

## ファイル構造

```
ishoku/
├── first_choice_updater.py              ← 第一希望更新機能（認証なし）
├── first_choice_updater_password.py    ← 第一希望更新機能（認証あり）
├── second_choice_updater.py            ← 第二希望更新機能（認証なし）
├── second_choice_updater_password.py   ← 第二希望更新機能（認証あり）
├── reservation_fetcher.py               ← 予約日程取得機能（認証なし）
├── reservation_fetcher_password.py      ← 予約日程取得機能（認証あり）
├── user.py                      ← ユーザー認証機能
├── taio_record.py              ← 対応履歴記録機能
├── connection.py               ← データベース接続機能
├── utils.py                    ← ユーティリティ機能
├── utils/
│   ├── db_utils.py             ← データベース操作ユーティリティ
│   ├── pattern_utils.py        ← パターン処理ユーティリティ
│   └── time_utils.py           ← 時間処理ユーティリティ
├── requirements.txt                    ← 完全版ライブラリリスト
├── requirements-minimal.txt            ← 最小限ライブラリリスト
├── README.md                           ← 使用方法ガイド
└── process.md                          ← プロセス詳細説明書
```

## ライセンス

このプロジェクトの一部として、元のプロジェクトのライセンスに従います。
