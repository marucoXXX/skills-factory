# テンプレートShape名マッピング表

BusinessModel.pptx を実際に検査して確認済み（2026-03）。

## スライド構成

1枚スライド構成。左側に事業モデル図エリア（Rectangle 4）、右側に意味合い（TextBox 9）。

## マッピング表（確認済み）

| セクション | Shape名 | Type | 内容 |
|---|---|---|---|
| Main Message | `Title 1` | PLACEHOLDER | スライドのメインメッセージ（最大70文字、「〜すべき」で締める） |
| Chart Title | `Text Placeholder 2` | PLACEHOLDER | サブタイトル（10〜20文字） |
| 事業モデル図エリア | `Rectangle 4` | AUTO_SHAPE | 事業モデル概要のプレースホルダー。ここに画像を挿入する |
| 意味合い | `TextBox 9` | TEXT_BOX | 4段落構成。Para[0]=「意味合い」見出し（編集不要）、Para[1〜3]=Implication 1〜3 |
| think-cell data | `think-cell data - do not delete` | EMBEDDED_OLE_OBJECT | 削除しない |

## 位置情報（確認済み）

| Shape名 | Left (in) | Top (in) | Width (in) | Height (in) |
|---|---|---|---|---|
| Title 1 | 0.41 | 0.61 | 12.52 | 0.44 |
| Text Placeholder 2 | 0.41 | 1.07 | 12.52 | 0.31 |
| Rectangle 4 | 0.41 | 1.81 | 8.83 | 5.22 |
| TextBox 9 | 9.52 | 1.81 | 3.41 | 5.22 |

## フォント情報

- TextBox 9 の見出し「意味合い」: 20pt（254000 EMU）、Bold
- TextBox 9 の Implication 項目: 16pt（203200 EMU）
- スタイルはテンプレートの既存runから継承されるため、スクリプトでは run.text だけを上書きする

## HTMLスクリーンショットの挿入

Rectangle 4 の領域（8.83" × 5.22"）に、事業モデル図のHTMLスクリーンショットを画像として挿入する。
- HTMLのviewportは 1766px × 1044px（2倍の解像度で 8.83" × 5.22" に対応）
- スクリーンショットはPNG形式で保存
- Rectangle 4 の既存テキスト「事業モデル概要」は画像で覆われる
