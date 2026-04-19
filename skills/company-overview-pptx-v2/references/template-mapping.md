# テンプレートShape名マッピング表

company-overview-template.pptx（business-model-template.pptxベース）を検査して確認済み（2026-04）。

## スライド構成

1枚スライド構成。business-model-template.pptxのスライドマスター/テーマを継承。
タイトル・メインメッセージはPLACEHOLDER型でテーマフォント（Arial / Meiryo UI）を自動適用。

## マッピング表

| セクション | Shape名 | Type | 内容 |
|---|---|---|---|
| タイトル | `Title 1` | PLACEHOLDER | スライドタイトル（左寄せ、24pt Bold、テーマフォント継承） |
| メインメッセージ | `Text Placeholder 2` | PLACEHOLDER | メインメッセージ（左寄せ、テーマフォント継承） |
| コンテンツエリア | `Content Area` | AUTO_SHAPE | HTML screenshot挿入先（テーブル＋写真） |
| 出典 | `Source` | TEXT_BOX | 出典テキスト（左寄せ、10pt） |
| think-cell | `think-cell data - do not delete` | EMBEDDED_OLE_OBJECT | 削除しない |

## テーマフォント

| 用途 | Latin | EA (日本語) |
|---|---|---|
| Major (タイトル) | Arial | Meiryo UI |
| Minor (本文) | Arial | Meiryo UI |

## HTMLスクリーンショットの挿入

Content Area（12.52" × 5.40"）にHTMLスクリーンショットを画像挿入。
ビューポート 2504px × 1080px、デバイススケール 2。1pt ≈ 2.78 CSS px。
