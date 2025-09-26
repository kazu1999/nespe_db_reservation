# ishoku フォルダー

## 概要
第一希望更新、第二希望更新、予約日程取得の3つの機能を独立したPythonファイルとして移植したフォルダーです。

## ファイル構成

### メインファイル
- **first_choice_updater.py** - 第一希望更新機能
- **second_choice_updater.py** - 第二希望更新機能
- **reservation_fetcher.py** - 予約日程取得機能

### 依存ファイル
- **user.py** - ユーザー認証機能
- **taio_record.py** - 対応履歴記録機能
- **connection.py** - データベース接続機能
- **utils.py** - ユーティリティ機能

### utilsフォルダー
- **utils/db_utils.py** - データベース操作ユーティリティ
- **utils/pattern_utils.py** - パターン処理ユーティリティ
- **utils/time_utils.py** - 時間処理ユーティリティ

## セットアップ

### 必要なライブラリのインストール

#### 1. 最小限のインストール（推奨）
```bash
# ishokuフォルダーに移動
cd ishoku

# 最小限のライブラリをインストール
pip install -r requirements-minimal.txt
```

#### 2. 完全版のインストール（開発用）
```bash
# すべてのライブラリをインストール
pip install -r requirements.txt
```

#### 3. 仮想環境でのインストール（推奨）
```bash
# 仮想環境を作成
python -m venv ishoku_env

# 仮想環境をアクティベート
# Linux/Mac
source ishoku_env/bin/activate
# Windows
ishoku_env\Scripts\activate

# ライブラリをインストール
pip install -r requirements-minimal.txt
```

### データベース接続テスト

```bash
# データベース接続をテスト
python connection.py
```

## 使用方法

### 基本的なインポート
```python
# 第一希望更新機能
from first_choice_updater import update_first_choice, get_available_slots

# 第二希望更新機能
from second_choice_updater import update_second_choice, get_current_second_choice, clear_second_choice

# 予約日程取得機能
from reservation_fetcher import get_reservation_date, get_reservation_history, get_reservation_status
```

### 第一希望更新の使用例
```python
from first_choice_updater import update_first_choice, get_available_slots

# 利用可能な時間枠を取得
slots = get_available_slots("12345", "2024-01-15")
print(f"利用可能な時間枠: {slots}")

# 第一希望を更新
result = update_first_choice("101", "password123", "12345", "2024-01-15 10:00")
if "error" in result:
    print(f"エラー: {result['error']}")
else:
    print(f"更新成功: {result['message']}")
```

### 第二希望更新の使用例
```python
from second_choice_updater import update_second_choice, get_current_second_choice, clear_second_choice

# 現在の第二希望を取得
current = get_current_second_choice("101", "password123", "12345")
print(f"現在の第二希望: {current}")

# 第二希望を更新
result = update_second_choice("101", "password123", "12345", "午前中希望、午後は不可")
if "error" in result:
    print(f"エラー: {result['error']}")
else:
    print(f"更新成功: {result['message']}")

# 第二希望をクリア
clear_result = clear_second_choice("101", "password123", "12345")
print(f"クリア結果: {clear_result}")
```

### 予約日程取得の使用例
```python
from reservation_fetcher import get_reservation_date, get_reservation_status, get_reservation_summary

# 予約日程を取得
date_result = get_reservation_date("101", "password123", "12345")
print(f"予約日程: {date_result}")

# 予約状況を取得
status_result = get_reservation_status("101", "password123", "12345")
print(f"予約状況: {status_result}")

# 予約サマリーを取得
summary_result = get_reservation_summary("101", "password123", "12345")
print(f"予約サマリー: {summary_result}")
```

## 各ファイルの主要機能

### first_choice_updater.py
- `update_first_choice()`: 第一希望の日時を更新
- `get_available_slots()`: 利用可能な時間枠を取得

### second_choice_updater.py
- `update_second_choice()`: 第二希望を更新
- `get_current_second_choice()`: 現在の第二希望を取得
- `clear_second_choice()`: 第二希望をクリア
- `get_second_choice_history()`: 第二希望の変更履歴を取得

### reservation_fetcher.py
- `get_reservation_date()`: 予約日程を取得
- `get_reservation_history()`: 予約履歴を取得
- `get_reservation_status()`: 予約状況を取得
- `get_upcoming_reservations()`: 今後の予約を取得
- `get_reservation_summary()`: 予約サマリーを取得

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

1. **認証**: すべての機能で部屋番号・パスワード・物件IDの認証が必要です
2. **データベース接続**: 各ファイルは独立して動作しますが、データベース接続が必要です
3. **エラーハンドリング**: 各関数は適切なエラーハンドリングを行います
4. **ログ記録**: 更新操作は自動的にログに記録されます

## テスト実行

各ファイルは独立してテスト実行可能です：

```bash
# 第一希望更新機能のテスト
python first_choice_updater.py

# 第二希望更新機能のテスト
python second_choice_updater.py

# 予約日程取得機能のテスト
python reservation_fetcher.py
```

## 依存関係

- **user.py**: 認証機能
- **taio_record.py**: ログ記録機能
- **utils.py**: エラーハンドリング
- **connection.py**: データベース接続
- **utils/**: ユーティリティ機能（db_utils, pattern_utils, time_utils）

## ファイル構造

```
ishoku/
├── first_choice_updater.py      ← 第一希望更新機能
├── second_choice_updater.py     ← 第二希望更新機能
├── reservation_fetcher.py       ← 予約日程取得機能
├── user.py                      ← ユーザー認証機能
├── taio_record.py              ← 対応履歴記録機能
├── connection.py               ← データベース接続機能
├── utils.py                    ← ユーティリティ機能
├── utils/
│   ├── db_utils.py             ← データベース操作ユーティリティ
│   ├── pattern_utils.py        ← パターン処理ユーティリティ
│   └── time_utils.py           ← 時間処理ユーティリティ
├── requirements.txt            ← 完全版ライブラリリスト
├── requirements-minimal.txt    ← 最小限ライブラリリスト
└── README.md                   ← 使用方法ガイド
```

## ライセンス

このプロジェクトの一部として、元のプロジェクトのライセンスに従います。
