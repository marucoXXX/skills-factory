# Template Mapping: issue-risk-template.pptx

## スライド構造（確認済み）

### 保持するShape（スクリプトがテキストを上書き）

| Shape名 | 型 | 用途 | JSON キー |
|---|---|---|---|
| Title 1 | PLACEHOLDER | Main Message | `main_message` |
| Text Placeholder 2 | PLACEHOLDER | Chart Title | `chart_title` |

### 削除＆動的再構築するShape

以下のShapeはスクリプト実行時にすべて削除され、JSONの `columns` と `rows` に基づいて動的に再構築される。

#### ヘッダー列（テンプレートのデフォルト5列）

| Shape名 | テキスト | Left | Top | Width |
|---|---|---|---|---|
| TextBox 4 | カテゴリ | 370800 | 1425630 | 713337 |
| TextBox 5 | 概要 | 1606746 | 1425630 | 1534387 |
| TextBox 26 | 詳細 | 3566609 | 1425630 | 3031899 |
| TextBox 23 | 担当 | 7649088 | 1425630 | 461665 |
| TextBox 25 | 対応期日 | 9623207 | 1425630 | 923330 |

#### ヘッダー下セパレーター

| Shape名 | 型 | Top | 線幅 | スタイル |
|---|---|---|---|---|
| Straight Connector 28 | LINE | 1796644 | 15875 (1.25pt) | 実線・schemeClr tx1 |

#### データ行グループ（6行分）

| Shape名 | Top | 子TextBox |
|---|---|---|
| Group 8 | 1956367 | TextBox 3(カテゴリ), TextBox 6(概要), TextBox 32(詳細), TextBox 33(担当), TextBox 34(期日) |
| Group 15 | 2706700 | 同構造 |
| Group 57 | 3457033 | 同構造 |
| Group 64 | 4207366 | 同構造 |
| Group 71 | 4957699 | 同構造 |
| Group 78 | 5708030 | 同構造 |

#### 行間セパレーター（破線）

| Shape名 | Top | 線幅 | スタイル |
|---|---|---|---|
| Straight Connector 7 | 2546977 | 9525 (0.75pt) | 破線・schemeClr tx1 |
| Straight Connector 51 | 3297310 | 同上 | 同上 |
| Straight Connector 63 | 4047643 | 同上 | 同上 |
| Straight Connector 70 | 4797976 | 同上 | 同上 |
| Straight Connector 77 | 5548309 | 同上 | 同上 |

## レイアウト定数

| 定数名 | 値 | 説明 |
|---|---|---|
| MARGIN_LEFT | 370800 | 左マージン |
| CONTENT_WIDTH | 11616153 | コンテンツ領域の幅 |
| HEADER_TOP | 1425630 | ヘッダー行のY座標 |
| HEADER_HEIGHT | 369332 | ヘッダー行の高さ |
| HEADER_SEP_TOP | 1796644 | ヘッダー下セパレーターのY座標 |
| FIRST_ROW_TOP | 1956367 | 最初のデータ行のY座標 |
| ROW_HEIGHT | 430887 | 各データ行の高さ |
| ROW_SPACING | 750333 | 行間（top to top） |

## セルスタイル

### ヘッダー列
- フォントサイズ: 11pt (1100 hundredths)
- Bold: Yes
- lang: en-GB
- typeface: +mn-ea

### データ行
- フォントサイズ: 10.5pt (1050 hundredths)
- Bold: No
- lang: en-GB
- typeface: +mn-ea
- wrap: square（詳細列）/ none（カテゴリ・概要列）
