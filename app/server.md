### APIサーバー (FastAPI) 概要

本ディレクトリ配下には、`nespe_db_reservation` の機能を公開する FastAPI アプリが配置されています。第一希望/第二希望の更新や予約情報取得を、HTTP API として提供します。

### ディレクトリ構成

```text
app/
  main.py                   # FastAPIエントリポイント（CORS設定・ルーター登録・ヘルスチェック）
  routers/
    first_choice.py         # 第一希望更新 API（公開/認証あり）
    second_choice.py        # 第二希望更新/取得/クリア/履歴 API（公開/認証あり）
    reservation.py          # 予約情報取得 API（公開/認証あり）
```

### 依存関係
- FastAPI / Uvicorn は `requirements.txt` に追加済みです。
  - `fastapi>=0.110.0`
  - `uvicorn[standard]>=0.23.0`

### 起動方法（ローカル開発）
1) 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

2) 開発サーバー起動（ホットリロード）
```bash
uvicorn app.main:app --reload
```

3) 動作確認
- OpenAPI ドキュメント: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- ヘルスチェック: `GET http://localhost:8000/api/v1/health`

### CORS
- すべて許可（`*`）の設定になっています。必要に応じて `app/main.py` の設定を絞ってください。

### エンドポイント概要
- ヘルスチェック
  - `GET /api/v1/health`

- 第一希望（first_choice）
  - 公開: `POST /api/v1/public/first-choice/update`
  - 公開: `GET  /api/v1/public/first-choice/slots`
  - 認証: `POST /api/v1/auth/first-choice/update`

- 第二希望（second_choice）
  - 公開: `POST /api/v1/public/second-choice/update`
  - 公開: `GET  /api/v1/public/second-choice/current`
  - 公開: `POST /api/v1/public/second-choice/clear`
  - 公開: `GET  /api/v1/public/second-choice/history`
  - 認証: `POST /api/v1/auth/second-choice/update`
  - 認証: `GET  /api/v1/auth/second-choice/current`
  - 認証: `POST /api/v1/auth/second-choice/clear`
  - 認証: `GET  /api/v1/auth/second-choice/history`

- 予約情報（reservation）
  - 公開: `GET /api/v1/public/reservation/date`
  - 公開: `GET /api/v1/public/reservation/history`
  - 公開: `GET /api/v1/public/reservation/status`
  - 公開: `GET /api/v1/public/reservation/upcoming`
  - 公開: `GET /api/v1/public/reservation/summary`
  - 認証: `GET /api/v1/auth/reservation/date`
  - 認証: `GET /api/v1/auth/reservation/history`
  - 認証: `GET /api/v1/auth/reservation/status`
  - 認証: `GET /api/v1/auth/reservation/upcoming`
  - 認証: `GET /api/v1/auth/reservation/summary`

### リクエスト例（第二希望の公開更新）
```bash
curl -X POST http://localhost:8000/api/v1/public/second-choice/update \
  -H "Content-Type: application/json" \
  -d '{
    "room_number": "103",
    "building_id": "3760",
    "date1": "2025-06-12",
    "time1": "09:00～12:00",
    "date2": "2025-06-13",
    "time2": "13:00～16:00"
  }'
```

### 補足
- `waku_pattern_id` は API リクエストで省略可能です。未指定時は内部で `PatternUtils.get_waku_pattern_id(building_id, connection)` を用いて物件ごとに自動解決されます。
- DB 接続や業務ロジックは既存モジュール（例: `second_choice_updater.py` 等）をそのまま利用しています。
