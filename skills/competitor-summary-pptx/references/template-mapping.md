# competitor-summary-template.pptx Shape マッピング

テンプレート `assets/competitor-summary-template.pptx` のShape構造と、`fill_competitor_summary.py` が行う処理の対応表。

## テンプレートShape一覧

| Shape名 | 種別 | 位置 (in) | サイズ (in) | スクリプトでの扱い |
|---|---|---|---|---|
| `Title 1` | PLACEHOLDER | L=0.41, T=0.61 | W=12.52, H=0.44 | Main Message を `set_textbox_text` で設定 |
| `Text Placeholder 2` | PLACEHOLDER | L=0.41, T=1.07 | W=12.52, H=0.31 | Chart Title を `set_textbox_text` で設定 |
| `Content Area` | AUTO_SHAPE | L=0.41, T=1.50 | W=12.52, H=5.40 | **削除して `add_table()` でネイティブテーブルに置換** |
| `Source` | TEXT_BOX | L=0.41, T=7.05 | W=8.00, H=0.30 | 出典テキストを `set_textbox_text` で設定 |

## スライドサイズ

- 幅: 13.33 inch
- 高さ: 7.50 inch（ワイドスクリーン 16:9）

## テーブル生成後のShape構成（生成後）

| Shape名 | 種別 | 内容 |
|---|---|---|
| `Title 1` | PLACEHOLDER | メインメッセージ |
| `Text Placeholder 2` | PLACEHOLDER | チャートタイトル |
| `CompetitorSummaryTable` | TABLE | 動的生成した競合比較テーブル |
| `Source` | TEXT_BOX | 出典 |

## テーブルの列構成（動的）

左から:
1. 比較項目ラベル列（幅 = 全幅 × 14%）
2. 対象会社列（残り幅 ÷ (競合数+1)、**イエロー背景 #FFF4C2**）
3〜N. 競合企業列（残り幅 ÷ (競合数+1)、交互にグレー背景）

## テーブルの行構成（動的）

- 行0: ヘッダー行（企業名、高さ0.40"）
- 行1〜N: データ行（比較項目、残り高さを等分）

## 変更時の注意事項

テンプレートを編集する場合は以下を保持すること：
- Shape名（特に `Content Area` は削除対象として参照される）
- スライドサイズ（13.33 × 7.50）
- Title 1 と Text Placeholder 2 の位置・サイズ
- Source の位置（左下）
