# テンプレートShape名マッピング表

shareholder-structure-template.pptx（company-history-template.pptxベース）。

## スライド構成

1枚スライド構成。company-history-template.pptxのスライドマスター/テーマを継承。
タイトル・メインメッセージはPLACEHOLDER型でテーマフォント（Arial / Meiryo UI）を自動適用。
テーブルはPPTXネイティブテーブルオブジェクトで動的生成（人間が編集可能）。

## テンプレート上のShape（スクリプト実行前）

| セクション | Shape名 | Type | 用途 |
|---|---|---|---|
| メインメッセージ | `Title 1` | PLACEHOLDER | メインメッセージ（テーマフォント継承） |
| チャートタイトル | `Text Placeholder 2` | PLACEHOLDER | チャートタイトル（テーマフォント継承） |
| テーブル（テンプレート） | `Table 1` | TABLE | スタイル複製元。スクリプト実行時に削除される |

## スクリプト実行後に生成されるShape

| セクション | Type | 内容 |
|---|---|---|
| ■株主構成タイトル | TEXT_BOX | セクションタイトル（14pt Bold） |
| 株主構成テーブル | TABLE | ネイティブテーブル（7列 × N行）。ヘッダー背景 #F5F0D0 |
| ■役員構成タイトル | TEXT_BOX | セクションタイトル（14pt Bold） |
| 役員構成テーブル | TABLE | ネイティブテーブル（6列 × N行）。ヘッダー背景 #F5F0D0 |
| 出典 | TEXT_BOX | 出典テキスト（10pt、#666666） |

## テーマフォント

| 用途 | Latin | EA (日本語) |
|---|---|---|
| Major (タイトル) | Arial | Meiryo UI |
| Minor (本文) | Arial | Meiryo UI |

## セルスタイル

| 要素 | 背景色 | フォント | 罫線 |
|---|---|---|---|
| ヘッダー行 | #F5F0D0 | 11〜13pt Bold | #CCCCCC 0.5pt |
| データ行 | なし（白） | 11〜13pt | #CCCCCC 0.5pt |
| 合計行 | #F0F0F0 | 11〜13pt Bold | #CCCCCC 0.5pt |
