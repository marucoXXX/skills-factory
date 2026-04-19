# Template Mapping: gantt-chart-template.pptx

## スライド構造

### テンプレートのShape

| Shape名 | 型 | 用途 | JSON キー |
|---|---|---|---|
| Title 1 | PLACEHOLDER | Main Message | `main_message` |
| Text Placeholder 2 | PLACEHOLDER | Chart Title | `chart_title` |

### 動的生成（HTML→スクリーンショット→画像挿入）

ガントチャートは全てHTML/CSSで描画し、Playwrightでスクリーンショットを撮影して画像としてスライドに挿入する。

## 画像挿入位置

| 定数 | 値 (EMU) | 説明 |
|---|---|---|
| CHART_LEFT | 370,800 | 画像の左位置 |
| CHART_TOP | 1,350,000 | 画像の上位置 |
| CHART_WIDTH | 11,450,400 | 画像の幅 |
| CHART_HEIGHT | 5,100,000 | 画像の高さ |

## HTML描画設定

| 定数 | 値 | 説明 |
|---|---|---|
| VP_WIDTH | 1800px | HTMLビューポート幅 |
| VP_HEIGHT | 動的計算 | 行数に応じて自動調整 |
| DEVICE_SCALE | 2 | Retina相当の高解像度 |
| MAX_ROWS_PER_PAGE | 15 | 1スライドあたりの最大行数 |

## ガントチャートHTML構造

| 要素 | 高さ | 説明 |
|---|---|---|
| 月ヘッダー | 48px | タイムラインの月区切り |
| フェーズヘッダー行 | 36px | フェーズ名（色付き全幅バー） |
| タスク行 | 36px | タスク名 + タスクバー |
| タスクバー | 20px (行内) | 進捗率を濃淡で表現 |

## デフォルトフェーズ色

| 順番 | 色コード | 色名 |
|---|---|---|
| 1 | #1A3C6E | ダークネイビー |
| 2 | #1565C0 | ブルー |
| 3 | #00695C | ティール |
| 4 | #6A1B9A | パープル |
| 5 | #E65100 | ディープオレンジ |
| 6 | #2E7D32 | グリーン |
| 7 | #AD1457 | ピンク |
| 8 | #283593 | インディゴ |
