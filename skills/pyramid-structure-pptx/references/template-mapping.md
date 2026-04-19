# テンプレートShape名マッピング表

pyramid-template-universal.pptx 確認済み（2026-04、v4 — ネイティブオブジェクト動的生成方式）。

---

## 概要

**旧方式（v3）**: 3段版/5段版の2テンプレート。各段のTextBox・Triangleを直接テキスト置換。段数が固定。
**新方式（v4）**: 1テンプレートで3〜7段に対応。テンプレートには Title + ChartTitle + DiagramAreaプレースホルダーのみを配置し、ピラミッド図部分はスクリプトがPowerPointネイティブオブジェクト（Rectangle, TextBox, Connector）を動的生成する。

---

## テンプレートの固定Shape

| 要素 | Shape名 | ShapeType | 内容 |
|---|---|---|---|
| Main Message | `Title 1` | PLACEHOLDER | スライドタイトル（テキスト上書き） |
| Chart Title | `Text Placeholder 2` | PLACEHOLDER | スライドサブタイトル（テキスト上書き） |
| ダイアグラムエリア | `Pyramid Diagram Area` | AUTO_SHAPE (Rectangle) | スクリプト実行時に削除され、動的Shapeに置き換わる |

## スクリプトが動的生成するShape

| Shape名パターン | ShapeType | 内容 |
|---|---|---|
| `PyramidTier_N` | RECTANGLE | ピラミッドの段（N=1が最上段）。塗りつぶし色・ラベルテキスト内蔵 |
| `PyramidDetail_N` | TEXT_BOX | 右側詳細カード。タイトル（bold）＋コメント行。背景色あり |
| `AccentLine` | CONNECTOR | 詳細カード左のアクセント縦線 |

## レイアウト定数

| 定数 | 値 | 説明 |
|---|---|---|
| PYRAMID_TOP | 2.38" | ピラミッドエリア上端Y |
| PYRAMID_BOTTOM | 6.27" | ピラミッドエリア下端Y |
| PYRAMID_CENTER_X | 2.65" | ピラミッド中心X |
| PYRAMID_MAX_W | 4.10" | 最下段の幅 |
| DETAIL_TOP | 1.83" | 右側詳細エリア上端Y |
| DETAIL_BOTTOM | 6.82" | 右側詳細エリア下端Y |
| DETAIL_LEFT | 5.30" | 右側詳細エリア左端 |
| DETAIL_RIGHT | 12.80" | 右側詳細エリア右端 |

## 段数別の最上段幅

| 段数 | 最上段の幅 | 最下段の幅 |
|---|---|---|
| 3 | 2.20" | 4.10" |
| 4 | 1.80" | 4.10" |
| 5 | 1.50" | 4.10" |
| 6 | 1.20" | 4.10" |
| 7 | 1.05" | 4.10" |
