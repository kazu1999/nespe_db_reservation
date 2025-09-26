# ishoku 予約管理システム - プロセス詳細説明書

## 概要
このドキュメントでは、ishokuフォルダーの3つの主要機能（第一希望更新、第二希望更新、予約日程取得）の詳細な処理フローと挙動について説明します。

## バージョン構成
- **認証なし版（推奨）**: 部屋番号と物件IDのみで動作する軽量版
- **認証あり版**: 部屋番号・パスワード・物件IDの認証が必要な従来版

---

## 1. first_choice_updater.py - 第一希望更新機能

### 主要機能
- 予約の第一希望日時を更新
- 利用可能な時間枠の取得
- 日時検証と空き枠チェック

### 処理フロー

#### 1.1 update_first_choice() メイン処理（認証なし版）

```
1. 現在の予約情報取得
   ├── _get_current_reservation() を呼び出し
   ├── tReservationF テーブルから最新の予約を取得
   └── 予約情報が存在しない場合はエラーを返す

2. 新しい日時の検証
   ├── _validate_new_datetime() を呼び出し
   ├── 日時形式の検証（YYYY-MM-DD HH:MM）
   ├── 過去日時のチェック
   └── 営業時間の検証（必要に応じて）

3. 空き枠チェック
   ├── _check_availability() を呼び出し
   ├── パターン情報の取得
   └── 指定日時の空き枠確認

4. 第一希望更新実行
   ├── _execute_first_choice_update() を呼び出し
   ├── tReservationF テーブルの TimeFrom を更新
   └── 更新件数が0の場合はエラーを返す

5. 対応履歴登録
   ├── _log_first_choice_update() を呼び出し
   ├── tTaioF テーブルにログを記録
   └── カテゴリ「|1|」で分類
```

#### 1.1.1 update_first_choice() メイン処理（認証あり版）

```
1. 認証チェック
   ├── authenticate_user() を呼び出し
   ├── 部屋番号・パスワード・物件IDの検証
   └── 認証失敗時はエラーを返す

2. 現在の予約情報取得
   ├── _get_current_reservation() を呼び出し
   ├── tReservationF テーブルから最新の予約を取得
   └── 予約情報が存在しない場合はエラーを返す

3. 新しい日時の検証
   ├── _validate_new_datetime() を呼び出し
   ├── 日時形式の検証（YYYY-MM-DD HH:MM）
   ├── 過去日時のチェック
   └── 営業時間の検証（必要に応じて）

4. 空き枠チェック
   ├── _check_availability() を呼び出し
   ├── パターン情報の取得
   └── 指定日時の空き枠確認

5. 第一希望更新実行
   ├── _execute_first_choice_update() を呼び出し
   ├── tReservationF テーブルの TimeFrom を更新
   └── 更新件数が0の場合はエラーを返す

6. 対応履歴登録
   ├── _log_first_choice_update() を呼び出し
   ├── tTaioF テーブルにログを記録
   └── カテゴリ「|1|」で分類
```

#### 1.2 get_available_slots() 時間枠取得

```
1. パターン情報取得
   ├── PatternUtils を使用
   └── 物件IDに基づくパターン設定を取得

2. 時間枠生成
   ├── _generate_time_slots() を呼び出し
   ├── 基本的な時間枠を生成（9:00-17:00の1時間刻み）
   └── 実際の実装ではパターン情報に基づいて生成
```

### データベース操作

#### 使用テーブル
- **tReservationF**: 予約情報の更新
- **tTaioF**: 対応履歴の記録
- **tUserM**: ユーザー認証

#### 主要SQL
```sql
-- 現在の予約情報取得
SELECT TimeFrom, SecondChoice
FROM tReservationF 
WHERE UserCD = %s AND ClientCD = %s AND MukouFlg = 0 
ORDER BY TimeFrom DESC LIMIT 1

-- 第一希望更新
UPDATE tReservationF 
SET TimeFrom = %s, Updated = NOW(), Updater = %s 
WHERE TimeFrom = %s AND UserCD = %s AND ClientCD = %s
```

### エラーハンドリング

#### 認証なし版
- 予約情報なし: "現在の予約情報が見つかりません。"
- 日時形式エラー: "日時の形式が正しくありません。YYYY-MM-DD HH:MM形式で入力してください。"
- 過去日時: "過去の日時は選択できません。未来の日時を選択してください。"

#### 認証あり版
- 認証失敗: "認証に失敗しました。部屋番号・パスワード・物件管理番号をご確認ください。"
- 予約情報なし: "現在の予約情報が見つかりません。"
- 日時形式エラー: "日時の形式が正しくありません。YYYY-MM-DD HH:MM形式で入力してください。"
- 過去日時: "過去の日時は選択できません。未来の日時を選択してください。"

---

## 2. second_choice_updater.py - 第二希望更新機能

### 主要機能
- 第二希望のテキスト更新
- 現在の第二希望取得
- 第二希望のクリア機能
- 第二希望の変更履歴取得

### 処理フロー

#### 2.1 update_second_choice() メイン処理（認証なし版）

```
1. 現在の予約情報取得
   ├── _get_current_reservation() を呼び出し
   └── 予約情報が存在しない場合はエラーを返す

2. 第二希望テキストの検証
   ├── _validate_second_choice_text() を呼び出し
   ├── 空文字チェック
   ├── 文字数制限（500文字以内）
   └── 禁止文字チェック（<, >, &, ", '）

3. 第二希望更新実行
   ├── _execute_second_choice_update() を呼び出し
   ├── tReservationF テーブルの SecondChoice を更新
   └── 更新件数が0の場合はエラーを返す

4. 対応履歴登録
   ├── _log_second_choice_update() を呼び出し
   ├── 個人情報保護のため内容をマスク（50文字まで）
   └── カテゴリ「|2|」で分類
```

#### 2.1.1 update_second_choice() メイン処理（認証あり版）

```
1. 認証チェック
   ├── authenticate_user() を呼び出し
   └── 認証失敗時はエラーを返す

2. 現在の予約情報取得
   ├── _get_current_reservation() を呼び出し
   └── 予約情報が存在しない場合はエラーを返す

3. 第二希望テキストの検証
   ├── _validate_second_choice_text() を呼び出し
   ├── 空文字チェック
   ├── 文字数制限（500文字以内）
   └── 禁止文字チェック（<, >, &, ", '）

4. 第二希望更新実行
   ├── _execute_second_choice_update() を呼び出し
   ├── tReservationF テーブルの SecondChoice を更新
   └── 更新件数が0の場合はエラーを返す

5. 対応履歴登録
   ├── _log_second_choice_update() を呼び出し
   ├── 個人情報保護のため内容をマスク（50文字まで）
   └── カテゴリ「|2|」で分類
```

#### 2.2 get_current_second_choice() 現在の第二希望取得（認証なし版）

```
1. 現在の予約情報取得
2. 第二希望情報の返却
   ├── 予約日時
   ├── 第二希望テキスト
   └── 第二希望の有無フラグ
```

#### 2.2.1 get_current_second_choice() 現在の第二希望取得（認証あり版）

```
1. 認証チェック
2. 現在の予約情報取得
3. 第二希望情報の返却
   ├── 予約日時
   ├── 第二希望テキスト
   └── 第二希望の有無フラグ
```

#### 2.3 clear_second_choice() 第二希望クリア（認証なし版）

```
1. 現在の予約情報取得
2. 第二希望クリア実行
   ├── SecondChoice を NULL に設定
   └── 更新件数が0の場合はエラーを返す
3. 対応履歴登録
   └── クリア操作をログに記録
```

#### 2.3.1 clear_second_choice() 第二希望クリア（認証あり版）

```
1. 認証チェック
2. 現在の予約情報取得
3. 第二希望クリア実行
   ├── SecondChoice を NULL に設定
   └── 更新件数が0の場合はエラーを返す
4. 対応履歴登録
   └── クリア操作をログに記録
```

#### 2.4 get_second_choice_history() 第二希望履歴取得（認証なし版）

```
1. 対応履歴から第二希望関連の記録を取得
   ├── カテゴリ「|2|」または「第二希望」を含む記録
   └── 作成日時の降順でソート
```

#### 2.4.1 get_second_choice_history() 第二希望履歴取得（認証あり版）

```
1. 認証チェック
2. 対応履歴から第二希望関連の記録を取得
   ├── カテゴリ「|2|」または「第二希望」を含む記録
   └── 作成日時の降順でソート
```

### データベース操作

#### 使用テーブル
- **tReservationF**: 第二希望の更新・取得
- **tTaioF**: 対応履歴の記録・取得
- **tUserM**: ユーザー認証

#### 主要SQL
```sql
-- 第二希望更新
UPDATE tReservationF 
SET SecondChoice = %s, Updated = NOW(), Updater = %s 
WHERE TimeFrom = %s AND UserCD = %s AND ClientCD = %s

-- 第二希望クリア
UPDATE tReservationF 
SET SecondChoice = NULL, Updated = NOW(), Updater = %s 
WHERE TimeFrom = %s AND UserCD = %s AND ClientCD = %s

-- 第二希望履歴取得
SELECT TaioNotes, Created, Category
FROM tTaioF 
WHERE UserCD = %s AND ClientCD = %s AND MukouFlg = 0 
AND (Category LIKE '%|2|%' OR TaioNotes LIKE '%第二希望%')
ORDER BY Created DESC
```

### エラーハンドリング

#### 認証なし版
- 予約情報なし: "現在の予約情報が見つかりません。"
- 空の第二希望: "第二希望の内容を入力してください。"
- 文字数制限: "第二希望の内容が長すぎます。500文字以内で入力してください。"
- 禁止文字: "使用できない文字 '{char}' が含まれています。"

#### 認証あり版
- 認証失敗: "認証に失敗しました。部屋番号・パスワード・物件管理番号をご確認ください。"
- 予約情報なし: "現在の予約情報が見つかりません。"
- 空の第二希望: "第二希望の内容を入力してください。"
- 文字数制限: "第二希望の内容が長すぎます。500文字以内で入力してください。"
- 禁止文字: "使用できない文字 '{char}' が含まれています。"

---

## 3. reservation_fetcher.py - 予約日程取得機能

### 主要機能
- 現在の予約日程取得
- 予約履歴の取得
- 予約状況の確認
- 今後の予約一覧取得
- 予約サマリー取得

### 処理フロー

#### 3.1 get_reservation_date() 予約日程取得（認証なし版）

```
1. 予約情報取得
   ├── _get_reservation_info() を呼び出し
   ├── tReservationF と tClientM をJOIN
   ├── 最新の予約情報を取得
   └── 予約情報が存在しない場合は適切な値を返す

2. 結果の整形
   ├── 日時フォーマット（YYYY-MM-DD HH:MM）
   ├── 第二希望テキスト
   ├── スタイリストコード
   └── 終了時間
```

#### 3.1.1 get_reservation_date() 予約日程取得（認証あり版）

```
1. 認証チェック
   ├── authenticate_user() を呼び出し
   └── 認証失敗時はエラーを返す

2. 予約情報取得
   ├── _get_reservation_info() を呼び出し
   ├── tReservationF と tClientM をJOIN
   ├── 最新の予約情報を取得
   └── 予約情報が存在しない場合は適切な値を返す

3. 結果の整形
   ├── 日時フォーマット（YYYY-MM-DD HH:MM）
   ├── 第二希望テキスト
   ├── スタイリストコード
   └── 終了時間
```

#### 3.2 get_reservation_history() 予約履歴取得

```
1. 認証チェック
2. 予約履歴取得
   ├── 指定件数分の履歴を取得
   ├── 無効フラグ（MukouFlg = 0）のレコードのみ
   └── 日時の降順でソート
3. 履歴の整形
   ├── 各レコードの日時フォーマット
   ├── 第二希望、スタイリスト、ステータス
   └── 作成・更新日時
```

#### 3.3 get_reservation_status() 予約状況取得

```
1. 認証チェック
2. 予約状況の集計
   ├── 総予約数
   ├── アクティブな予約数（Status = 1）
   ├── 第二希望付き予約数
   ├── 最新予約日時
   └── 最古予約日時
3. 結果の整形
   └── 予約の有無フラグ
```

#### 3.4 get_upcoming_reservations() 今後の予約取得

```
1. 認証チェック
2. 今後の予約取得
   ├── 現在日時から指定日数先まで
   ├── 無効フラグ（MukouFlg = 0）のレコードのみ
   └── 日時の昇順でソート
3. 予約の整形
   ├── 日時フォーマット
   ├── 第二希望、スタイリスト、ステータス
   └── 現在からの日数
```

#### 3.5 get_reservation_summary() 予約サマリー取得

```
1. 現在の予約取得
   ├── get_reservation_date() を呼び出し
   └── エラー時はそのまま返す
2. 予約状況取得
   ├── get_reservation_status() を呼び出し
   └── エラー時はそのまま返す
3. 今後の予約取得
   ├── get_upcoming_reservations() を呼び出し
   └── エラー時はそのまま返す
4. サマリー情報の統合
   ├── 現在の予約の有無
   ├── 総予約数
   └── 今後の予約数
```

### データベース操作

#### 使用テーブル
- **tReservationF**: 予約情報の取得
- **tClientM**: クライアント情報（JOIN用）
- **tUserM**: ユーザー認証

#### 主要SQL
```sql
-- 予約日程取得
SELECT 
    rf.TimeFrom AS bookingDateTime,
    rf.TimeTo AS bookingDateTimeTo,
    rf.SecondChoice AS secondChoiceText,
    rf.StylistCD AS stylistCD
FROM tReservationF rf
JOIN tClientM cm ON rf.ClientCD = cm.ClientCD
WHERE rf.UserCD = %s AND rf.ClientCD = %s AND rf.MukouFlg = 0
ORDER BY rf.TimeFrom DESC
LIMIT 1

-- 予約履歴取得
SELECT 
    TimeFrom, TimeTo, SecondChoice, StylistCD, Status, Created, Updated
FROM tReservationF 
WHERE UserCD = %s AND ClientCD = %s AND MukouFlg = 0
ORDER BY TimeFrom DESC
LIMIT %s

-- 予約状況取得
SELECT 
    COUNT(*) as total_reservations,
    COUNT(CASE WHEN Status = 1 THEN 1 END) as active_reservations,
    COUNT(CASE WHEN SecondChoice IS NOT NULL THEN 1 END) as with_second_choice,
    MAX(TimeFrom) as latest_reservation,
    MIN(TimeFrom) as earliest_reservation
FROM tReservationF 
WHERE UserCD = %s AND ClientCD = %s AND MukouFlg = 0
```

### エラーハンドリング

#### 認証なし版
- 予約情報取得エラー: "予約情報取得エラー: {エラー詳細}"
- 予約履歴取得エラー: "予約履歴取得エラー: {エラー詳細}"
- 予約状況取得エラー: "予約状況取得エラー: {エラー詳細}"

#### 認証あり版
- 認証失敗: "認証に失敗しました。部屋番号・パスワード・物件管理番号をご確認ください。"
- 予約情報取得エラー: "予約情報取得エラー: {エラー詳細}"
- 予約履歴取得エラー: "予約履歴取得エラー: {エラー詳細}"
- 予約状況取得エラー: "予約状況取得エラー: {エラー詳細}"

---

## 共通処理

### 認証フロー（認証あり版のみ）
```
1. 入力パラメータの検証
   ├── 部屋番号（room_number）
   ├── パスワード（password）
   └── 物件ID（building_id）

2. データベース認証
   ├── tUserM テーブルで認証
   ├── UserCD, Passwd, ClientCD の組み合わせ
   └── 認証成功時はユーザー情報を返す

3. 認証結果の処理
   ├── 成功: 処理を継続
   └── 失敗: エラーメッセージを返す
```

### 認証なし版の特徴
```
1. 直接データベース操作
   ├── 部屋番号（room_number）
   └── 物件ID（building_id）

2. 認証処理のスキップ
   ├── パスワード不要
   └── 軽量で高速な処理
```

### ログ記録フロー
```
1. 操作内容の記録
   ├── 第一希望更新: "[LINE第一希望更新] {日時}"
   ├── 第二希望更新: "[LINE第二希望更新] {内容（マスク済み）}"
   └── 第二希望クリア: "[LINE第二希望クリア] 第二希望を削除しました"

2. 対応履歴テーブルへの登録
   ├── tTaioF テーブルに記録
   ├── カテゴリ分類（|1|, |2|）
   └── 作成者・更新者の記録

3. エラーハンドリング
   ├── ログ記録失敗時は警告を出力
   └── メイン処理には影響しない
```

### データベース接続管理
```
1. 接続の取得
   ├── 既存の接続がある場合は再利用
   └── ない場合は新規接続を作成

2. 接続の管理
   ├── デコレータ（@db_connection）で自動管理
   ├── 処理完了後に自動的にクローズ
   └── エラー時も適切にクローズ

3. トランザクション管理
   ├── 更新処理は自動的にコミット
   └── エラー時はロールバック
```

---

## エラー処理の統一

### エラーレスポンス形式
```python
{
    "error": "エラーメッセージ"
}
```

### 成功レスポンス形式
```python
{
    "result": "ok",
    "message": "処理が完了しました",
    # その他のデータ
}
```

### 共通エラーメッセージ

#### 認証なし版
- データベースエラー: "データベースエラーが発生しました。運営までご連絡ください。"
- 予約情報なし: "現在の予約情報が見つかりません。"

#### 認証あり版
- 認証エラー: "認証に失敗しました。部屋番号・パスワード・物件管理番号をご確認ください。"
- データベースエラー: "データベースエラーが発生しました。運営までご連絡ください。"
- 予約情報なし: "現在の予約情報が見つかりません。"

---

## セキュリティ考慮事項

### 認証なし版のセキュリティ
- **直接アクセス**: 部屋番号と物件IDのみでデータベースに直接アクセス
- **軽量性**: 認証処理をスキップすることで高速化
- **シンプル性**: 複雑な認証ロジックが不要

### 認証あり版のセキュリティ
- **3要素認証**: 部屋番号・パスワード・物件IDによる厳格な認証
- **アクセス制御**: 認証されたユーザーのみが操作可能
- **セキュリティ強化**: 不正アクセスの防止

### 共通のセキュリティ対策
- **入力値検証**: 日時形式の厳密な検証、文字数制限、禁止文字チェック
- **SQLインジェクション対策**: パラメータ化クエリの使用
- **個人情報保護**: 第二希望の内容はログでマスク（50文字まで）
- **ログ管理**: すべての操作をログに記録、カテゴリ別分類

---

## パフォーマンス考慮事項

### 認証なし版のパフォーマンス
- **高速処理**: 認証処理をスキップすることで処理速度が向上
- **軽量**: パスワード検証が不要でリソース使用量が削減
- **シンプル**: 複雑な認証フローが不要でコードが簡潔

### 認証あり版のパフォーマンス
- **セキュリティ重視**: 認証処理による若干のオーバーヘッド
- **堅牢性**: 不正アクセスの防止によりシステムの安全性が向上
- **監査性**: すべての操作が認証済みユーザーによって実行される

### 共通のパフォーマンス最適化
- **データベースクエリ最適化**: 適切なインデックスの使用、必要最小限のデータ取得
- **接続管理**: 接続プールの活用、接続の再利用、適切な接続クローズ
- **エラーハンドリング**: 例外の適切な処理、リソースの適切な解放
