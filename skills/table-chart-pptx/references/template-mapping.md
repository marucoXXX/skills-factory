# テンプレートShape名マッピング表

TableChart.pptx を実際に検査して確認済み（2026-03）。

## スライド構成

1枚スライド構成。左側にテーブル、右側に意味合いボックス。

## マッピング表（確認済み）

| セクション | Shape名 | Shape Type | 内容 |
|---|---|---|---|
| Main Message | `Title 1` | PLACEHOLDER | スライド全体の主張（最大70文字、「〜すべき」で終える） |
| Chart Title | `Text Placeholder 2` | PLACEHOLDER | スライドのサブタイトル（10〜20文字） |
| テーブルラベル | `TextBox 6` | TEXT_BOX | テーブルセクションの見出し（太字、動的変更可、テーブル幅に合わせた広幅） |
| 水平線 | `Straight Connector 26` | LINE | テーブルラベルとテーブル本体の区切り線（編集不要） |
| 意味合い | `TextBox 29` | TEXT_BOX | para[0]=タイトル「意味合い」(bold,20pt) + para[1..N]=Bullet付き項目(16pt) |
| テーブル | `Table 10` | TABLE | 動的テーブル（スクリプトで削除→再構築） |
| think-cell | `think-cell data - do not delete` | EMBEDDED_OLE | think-cellデータ（編集不要） |

## テーブルのスタイル情報

- テーブル位置: left=364742, top=2091822, width=7909602, height=1371600
- ヘッダー行: accent2塗りつぶし、四辺白罫線(solid, FFFFFF, 9525幅)、**白文字**(FFFFFF)
- データ行: bg1塗りつぶし、上下罫線(solid, tx1色, 9525幅)
- セルフォント: 12pt (sz=1200), lang=en-GB
- tblPr: firstRow=1, bandRow=1
- 列幅: テーブル総幅 ÷ 列数で均等配分

## 意味合いボックスのスタイル情報

- 位置: left=8705088, top=1659114, width=3113712, height=4774938
- 背景: bg1 lumMod=95000（薄いグレー）
- タイトル「意味合い」: bold, 20pt (sz=2000), spcAft=600pt
- Bullet項目: 16pt (sz=1600), marL=285750, indent=-285750, buChar="•", spcAft=600pt
