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

### API仕様（リクエスト/レスポンス）

- 共通エラー形式
```json
{
  "error": "エラーメッセージ",
  "details": { "任意の補足情報": "..." }
}
```

#### 第一希望（first_choice）

- 公開: POST `/api/v1/public/first-choice/update`
  - Request JSON
    ```json
    {
      "room_number": "103",
      "building_id": "3760",
      "new_datetime": "2025-06-12 10:00"
    }
    ```
  - Success Response
    ```json
    {
      "result": "ok",
      "message": "第一希望を更新しました。",
      "old_datetime": "2025-06-01 11:00",
      "new_datetime": "2025-06-12 10:00"
    }
    ```

- 公開: GET `/api/v1/public/first-choice/slots`
  - Query Params: `building_id` (str), `date` (YYYY-MM-DD)
  - Success Response（抜粋）
    ```json
    {
      "result": "ok",
      "date": "2025-06-12",
      "time_slots": [
        {
          "time": "2025-06-12 09:00",
          "start_time": "09:00",
          "end_time": "12:00",
          "available": true,
          "stylist_cd": 1,
          "type": "normal",
          "stylists": [
            {
              "stylist_cd": 1,
              "stylist_name": "Aさん",
              "available": true,
              "current_reservations": 0,
              "max_reservations": 2
            }
          ],
          "slot_index": 0
        }
      ],
      "total_slots": 8,
      "available_slots": 5
    }
    ```

- 認証: POST `/api/v1/auth/first-choice/update`
  - Request JSON
    ```json
    {
      "room_number": "103",
      "password": "***",
      "building_id": "3760",
      "new_datetime": "2025-06-12 10:00"
    }
    ```
  - Response: 公開版と同様

#### 第二希望（second_choice）

- 公開: POST `/api/v1/public/second-choice/update`
  - Request JSON（`date3`/`time3`/`waku_pattern_id` は任意）
    ```json
    {
      "room_number": "103",
      "building_id": "3760",
      "date1": "2025-06-12",
      "time1": "09:00～12:00",
      "date2": "2025-06-13",
      "time2": "13:00～16:00",
      "date3": "2025-06-14",
      "time3": "18:00～21:00",
      "waku_pattern_id": 1
    }
    ```
  - Success Response
    ```json
    {
      "result": "ok",
      "message": "第二希望を更新しました。",
      "reservation_date": "2025-06-20 11:00",
      "second_choice": "①06/12午前②06/13午後③06/14夜"
    }
    ```

- 公開: GET `/api/v1/public/second-choice/current`
  - Query Params: `room_number` (str), `building_id` (str)
  - Success Response
    ```json
    {
      "result": "ok",
      "reservation_date": "2025-06-20 11:00",
      "second_choice": null,
      "has_second_choice": false
    }
    ```

- 公開: POST `/api/v1/public/second-choice/clear`
  - Request JSON
    ```json
    { "room_number": "103", "building_id": "3760" }
    ```
  - Success Response
    ```json
    {
      "result": "ok",
      "message": "第二希望をクリアしました。",
      "reservation_date": "2025-06-20 11:00"
    }
    ```

- 公開: GET `/api/v1/public/second-choice/history`
  - Query Params: `room_number` (str), `building_id` (str), `limit` (int, default 10)
  - Success Response（抜粋）
    ```json
    {
      "result": "ok",
      "history": [
        { "TaioNotes": "[AI電話第二希望更新] ...", "Created": "2025-06-01 12:34:56", "Category": "|2|" }
      ],
      "total_count": 1
    }
    ```

- 認証版（`/api/v1/auth/second-choice/...`）
  - `update`/`clear` は Request に `password` を含む以外は公開版と同様
  - `current`/`history` は Query に `password` を含む以外は公開版と同様

#### 予約情報（reservation）

- 公開: GET `/api/v1/public/reservation/date`
  - Query Params: `room_number` (str), `building_id` (str)
  - Success Response
    ```json
    {
      "result": "ok",
      "reservation_date": "2025-06-20 11:00",
      "reservation_date_raw": "2025-06-20 11:00:00",
      "second_choice": null,
      "stylist_cd": 1,
      "time_to": "2025-06-20 12:00",
      "has_reservation": true
    }
    ```
  - 予約なし例
    ```json
    {
      "datetime": null,
      "datetime_raw": null,
      "second_choice": null,
      "stylist_cd": null,
      "time_to": null,
      "has_reservation": false
    }
    ```

- 公開: GET `/api/v1/public/reservation/history`
  - Query Params: `room_number` (str), `building_id` (str), `limit` (int, default 50)
  - Success Response（抜粋）
    ```json
    {
      "result": "ok",
      "history": [
        {
          "datetime": "2025-06-20 11:00",
          "datetime_to": "2025-06-20 12:00",
          "second_choice": null,
          "stylist_cd": 1,
          "status": 1,
          "created": "2025-06-01 12:34:56",
          "updated": "2025-06-01 12:34:56"
        }
      ],
      "total_count": 1
    }
    ```

- 公開: GET `/api/v1/public/reservation/status`
  - Query Params: `room_number` (str), `building_id` (str)
  - Success Response
    ```json
    {
      "result": "ok",
      "total_reservations": 5,
      "active_reservations": 2,
      "with_second_choice": 1,
      "latest_reservation": "2025-06-20 11:00",
      "earliest_reservation": "2024-12-01 10:00",
      "has_reservations": true
    }
    ```

- 公開: GET `/api/v1/public/reservation/upcoming`
  - Query Params: `room_number` (str), `building_id` (str), `days_ahead` (int, default 30)
  - Success Response（抜粋）
    ```json
    {
      "result": "ok",
      "upcoming_reservations": [
        {
          "datetime": "2025-06-20 11:00",
          "datetime_to": "2025-06-20 12:00",
          "second_choice": null,
          "stylist_cd": 1,
          "status": 1,
          "days_from_now": 7
        }
      ],
      "total_count": 1,
      "days_ahead": 30
    }
    ```

- 公開: GET `/api/v1/public/reservation/summary`
  - Query Params: `room_number` (str), `building_id` (str)
  - Success Response（抜粋）
    ```json
    {
      "result": "ok",
      "current_reservation": { "result": "ok", "reservation_date": "2025-06-20 11:00", "has_reservation": true },
      "status": { "result": "ok", "total_reservations": 5, "has_reservations": true },
      "upcoming": { "result": "ok", "total_count": 1 },
      "summary": {
        "has_current_reservation": true,
        "total_reservations": 5,
        "upcoming_count": 1
      }
    }
    ```

- 認証版（`/api/v1/auth/reservation/...`）
  - 各エンドポイントは Query に `password` を含む以外は公開版と同様

### 本番公開URLと動作確認

- ベースURL: `https://call-api.489501.jp/nespe_db_reservation`
- 例: ヘルスチェック
  ```bash
  curl -s https://call-api.489501.jp/nespe_db_reservation/api/v1/health
  ```
- 例: 第二希望の公開更新
  ```bash
  curl -X POST https://call-api.489501.jp/nespe_db_reservation/api/v1/public/second-choice/update \
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
- 例: 第一希望の空き枠取得
  ```bash
  curl "https://call-api.489501.jp/nespe_db_reservation/api/v1/public/first-choice/slots?building_id=3760&date=2025-06-12"
  ```
