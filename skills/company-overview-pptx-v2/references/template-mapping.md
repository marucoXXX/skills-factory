# テンプレートShape名マッピング表

company-overview-template.pptx（business-model-template.pptxベース）を検査して確認済み（2026-04）。

## スライド構成

1枚スライド構成。business-model-template.pptxのスライドマスター/テーマを継承。
Main Message と Chart Title はスクリプト側で `rPr` に `sz`/`b` を明示書き込みする
（テンプレート継承任せにすると PowerPoint 環境によって Office 標準値にフォールバックする事象があるため）。

## マッピング表

| セクション | Shape名 | Type | 内容 |
|---|---|---|---|
| Main Message | `Title 1` | PLACEHOLDER | 上段、26pt Bold、Meiryo UI / Arial（スクリプトで明示） |
| Chart Title  | `Text Placeholder 2` | PLACEHOLDER | 下段、18pt Bold、Meiryo UI / Arial（スクリプトで明示） |
| テーブル | `Overview Table` | TABLE | 会社概要2列テーブル（ラベル / 値）。14pt |
| 写真キャプション | `Photo Caption 1` / `Photo Caption 2` | TEXT_BOX | 14pt Bold |
| 写真エリア | `Photo Area 1` / `Photo Area 2` | AUTO_SHAPE | プレースホルダー枠。写真挿入時は同位置に Picture が重ねられる |
| 出典 | `Source` | TEXT_BOX | 出典テキスト（左寄せ、10pt） |

※ テンプレートから think-cell 関連 graphicFrame は slide/slideLayout/slideMaster の
3 階層すべてから削除済み。rels 側の orphan エントリは残す（company-history-pptx等と同じ扱い）。
詳細は `memory/feedback_pptx_template_repair.md` を参照。

## テーマフォント

| 用途 | Latin | EA (日本語) |
|---|---|---|
| Major (タイトル) | Arial | Meiryo UI |
| Minor (本文) | Arial | Meiryo UI |

## HTMLスクリーンショットの挿入

Content Area（12.52" × 5.40"）にHTMLスクリーンショットを画像挿入。
ビューポート 2504px × 1080px、デバイススケール 2。1pt ≈ 2.78 CSS px。
