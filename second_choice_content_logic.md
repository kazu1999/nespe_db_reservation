# 第二希望文字列組み立てロジック

## 概要
第二希望の文字列は「①②③」形式で組み立てられ、データベースの`tReservationF`テーブルの`SecondChoice`カラムに保存されます。

## 文字列形式
```
①MM/DD時間帯②MM/DD時間帯③MM/DD時間帯
```

### 例
- **第三希望あり**: `①06/12午前②06/13午後③06/14夜間`
- **第三希望なし**: `①06/12午前②06/13午後③入力無し`

## 処理フロー

### 1. 入力データの取得
```php
$wDate1 = SPFWParameter::getValues('wDate1'); // 第一希望日
$wDate2 = SPFWParameter::getValues('wDate2'); // 第二希望日
$wDate3 = SPFWParameter::getValues('wDate3'); // 第三希望日
$wTime1 = SPFWParameter::getValues('wTime1'); // 第一希望時間帯
$wTime2 = SPFWParameter::getValues('wTime2'); // 第二希望時間帯
$wTime3 = SPFWParameter::getValues('wTime3'); // 第三希望時間帯
```

### 2. 第三希望の有無判定
```php
$IfDate3Ari = TRUE;   // 第3希望がありフラグ
$Date3Nashi = FALSE;  // 第3希望がないフラグ

if (!$wTime3 or !$wDate3) {
    $IfDate3Ari = FALSE;
    $Date3Nashi = TRUE;
    $wDate3 = $wDate1;  // 第一希望をコピー
    $wTime3 = $wTime1;  // 第一希望をコピー
}
```

### 3. 時間帯の解析
```php
// 第一希望
if ($wDate1 != '') {
    $wTime1StartArr = explode('～', $wTime1);
    $MailTime1 = $wTime1StartArr[0];      // 開始時間
    $MailTimeTo1 = $wTime1StartArr[1];   // 終了時間
}

// 第二希望
if ($wDate2) {
    $wTime2StartArr = explode('～', $wTime2);
    $MailTime2 = $wTime2StartArr[0];      // 開始時間
    $MailTimeTo2 = $wTime2StartArr[1];   // 終了時間
}

// 第三希望
if ($wDate3 != '') {
    $wTime3StartArr = explode('～', $wTime3);
    $MailTime3 = $wTime3StartArr[0];      // 開始時間
    $MailTimeTo3 = $wTime3StartArr[1];   // 終了時間
}
```

### 4. 枠パターンとの照合
```php
for ($i = 0; $i < $WakuSuu; $i++) {
    if ($wTime1StartArr[0] == $WAKUPATTERN[$WakuPattern]['StartTime'][$i]) {
        $wTimeAMPM1 = $WAKUPATTERN[$WakuPattern]['AMPM'][$i];  // "午前"
    }
    if ($wTime2StartArr[0] == $WAKUPATTERN[$WakuPattern]['StartTime'][$i]) {
        $wTimeAMPM2 = $WAKUPATTERN[$WakuPattern]['AMPM'][$i];  // "午後"
    }
    if ($wTime3StartArr[0] == $WAKUPATTERN[$WakuPattern]['StartTime'][$i]) {
        $wTimeAMPM3 = $WAKUPATTERN[$WakuPattern]['AMPM'][$i];  // "夜間"
    }
}
```

### 5. 日付フォーマット変換
```php
// 変換ロジック
str_replace("-", "/", substr($wDate1, 5, 5))

// 例: "2025-06-12" → "06/12"
// 1. substr("2025-06-12", 5, 5) → "06-12"
// 2. str_replace("-", "/", "06-12") → "06/12"
```

### 6. 文字列組み立て
```php
$SecondChoice  = "①" . str_replace("-", "/", substr($wDate1, 5, 5)) . $wTimeAMPM1;
$SecondChoice .= "②" . str_replace("-", "/", substr($wDate2, 5, 5)) . $wTimeAMPM2;

if ($Date3Nashi) { // 第三希望入力無し
    $SecondChoice .= "③入力無し";
} else { // 第三希望入力あり
    $SecondChoice .= "③" . str_replace("-", "/", substr($wDate3, 5, 5)) . $wTimeAMPM3;
}
```

## 具体例

### 入力データ
```php
$wDate1 = "2025-06-12";
$wDate2 = "2025-06-13";
$wDate3 = "2025-06-14";
$wTime1 = "09:00～12:00";
$wTime2 = "13:00～16:00";
$wTime3 = "18:00～21:00";
```

### 処理ステップ
1. **日付変換**:
   - `"2025-06-12"` → `"06/12"`
   - `"2025-06-13"` → `"06/13"`
   - `"2025-06-14"` → `"06/14"`

2. **時間帯照合**:
   - `09:00` → `"午前"`
   - `13:00` → `"午後"`
   - `18:00` → `"夜間"`

3. **文字列組み立て**:
   - `"①" + "06/12" + "午前"` → `"①06/12午前"`
   - `"②" + "06/13" + "午後"` → `"②06/13午後"`
   - `"③" + "06/14" + "夜間"` → `"③06/14夜間"`

### 最終結果
```
①06/12午前②06/13午後③06/14夜間
```

## 第三希望なしの場合

### 入力データ
```php
$wDate1 = "2025-06-12";
$wDate2 = "2025-06-13";
$wDate3 = "";  // 空
$wTime3 = "";  // 空
```

### 処理結果
```
①06/12午前②06/13午後③入力無し
```

## データベース保存

### 保存処理
```php
$myReservation->SecondChoice = $SecondChoice;
$myReservation->Updater = $UserCD;

if (!$myReservation->executeUpdate())
    trigger_error("Updating Reservation Failed.", E_USER_ERROR);
```

### 保存先
- **テーブル**: `tReservationF`
- **カラム**: `SecondChoice`
- **形式**: `VARCHAR`

## 文字列の特徴

### 丸数字の使用
- `①`: 第一希望
- `②`: 第二希望
- `③`: 第三希望

### 日付フォーマット
- **入力**: `Y-m-d` (2025-06-12)
- **出力**: `M/d` (06/12)

### 時間帯表現
- 枠パターンから取得: "午前", "午後", "夜間"
- ユーザー入力の時間帯文字列は使用せず、枠パターンの時間帯名を使用

### 第三希望の自動処理
- **入力なし**: `"③入力無し"`を自動付与
- **入力あり**: 通常の日付+時間帯形式

## 注意事項

1. **日付フォーマット**: 必ず`Y-m-d`形式で入力する必要がある
2. **時間帯照合**: 枠パターンに登録されている時間帯のみ使用可能
3. **第三希望**: 入力がない場合は自動的に`"③入力無し"`が付与される
4. **文字列長**: データベースの`SecondChoice`カラムの文字数制限に注意
5. **特殊文字**: 丸数字（①②③）は特殊文字として扱われる

## 関連ファイル

- **メイン処理**: `org_data/reserve_finish_new.php` (611-618行目)
- **レガシー処理**: `org_data/reserve_finish.php` (577-592行目)
- **表示処理**: `chatbot_scripts/flex/textinput.py` (103-145行目)
- **解析処理**: `chatbot_scripts/utils/text_utils.py` (46行目)

## 枠パターン対応状況

### 対応枠パターン数
- **総数**: 67個の枠パターン（ID: 0-66）
- **実装状況**: 全ての枠パターンに対応完了

### 枠パターンの種類
#### **2枠パターン** (最も一般的)
- 基本的な午前・午後の2枠構成
- 例: `2枠( AM 9:00-12:00, PM 13:00-17:00)`

#### **3枠パターン**
- 午前・午後1・午後2の3枠構成
- 例: `3枠( AM 9:00-12:00, PM1 13:00-15:00, PM2 15:00-17:00)`

#### **4枠パターン**
- 午前1・午前2・午後1・午後2の4枠構成
- 例: `4枠( AM1 9:00-10:30, AM2 10:30-12:00, PM1 13:00-15:00, PM2 15:00-17:00)`

#### **5枠パターン**
- より細かい時間帯分割
- 例: `5枠( AM1 9:00-10:30, AM2 10:30-12:00, PM1 13:00-14:30, PM2 14:30-16:00, PM3 16:00-17:00)`

#### **6枠パターン**
- 1時間単位の細かい分割
- 例: `6枠( AM1 9:00-10:00, AM2 10:00-11:00, PM1 12:00-13:00, PM2 13:00-14:00, PM3 14:00-15:00, PM4 15:00-16:00)`

#### **9枠パターン**
- 45分単位の非常に細かい分割
- 例: `9枠( AM1 9:00-09:45, AM2 9:45-10:30, AM3 10:30-11:15, AM4 11:15-12:00, PM1 13:00-13:45, PM2 13:45-14:30, PM3 14:30-15:30, PM4 15:30-16:15, PM5 16:15-17:00)`

#### **10枠パターン**
- 45分単位の午前・午後分割
- 例: `10枠( AM1 9:00-09:45, AM2 09:45-10:30, AM3 10:30-11:15, AM4 11:15-12:00, PM1 13:00-13:45, PM2 13:45-14:30, PM3 14:30-15:15, PM4 15:15-16:00, PM5 16:00-16:45, PM6 16:45-17:30)`

#### **14枠パターン**
- 30分単位の非常に細かい分割
- 例: `14枠( AM1 9:00-09:30, AM2 09:30-10:00, AM3 10:00-10:30, AM4 10:30-11:00, AM5 11:00-11:30, AM6 11:30-12:00, PM1 13:00-13:30, PM2 13:30-14:00, PM3 14:00-14:30, PM4 14:30-15:00, PM5 15:00-15:30, PM6 15:30-16:00, PM7 16:00-16:30, PM8 16:30-17:00)`

#### **1枠パターン**
- 終日対応
- 例: `1枠(9:00-17:00)`

### 時間単位（JikanTani）
- **15分**: 最も細かい時間単位
- **30分**: 中間的な時間単位
- **60分**: 標準的な時間単位

### 特殊な枠パターン
- **作業時間パターン**: 建装さん用の8:30-17:30作業時間
- **夜間対応**: 19:00-21:00などの夜間時間帯
- **早朝対応**: 8:00開始の早朝時間帯
- **長時間対応**: 9:00-13:00の4時間連続枠

## 実装ファイル

### Python実装
- **ファイル**: `nespe_db_reservation/second_choice_content_logic.py`
- **クラス**: `SecondChoiceContentLogic`
- **機能**: 全67個の枠パターンに対応した文字列組み立てロジック

### 主要メソッド
- `build_second_choice_string()`: 第二希望文字列の組み立て
- `parse_second_choice_string()`: 第二希望文字列の解析
- `get_time_ampm()`: 時間帯名の取得
- `validate_second_choice_input()`: 入力データの検証

## 更新履歴

- **2024-01-15**: 初版作成
- **2024-01-20**: 第三希望なしの場合の処理を追加
- **2024-01-25**: 具体例と注意事項を追加
- **2024-01-30**: 全67個の枠パターン対応完了、Python実装追加
