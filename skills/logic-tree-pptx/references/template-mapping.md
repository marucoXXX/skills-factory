# テンプレートShape名マッピング表

LogicTree.pptx を実際に検査して確認済み。

## スライド構成

1枚スライド構成。上部にMain Logic、下部に3つのSub Logic、右側に意味合い（3項目）。
矢印（Straight Arrow Connector）でSub Logic → Main Logicの帰納的関係を示す。

## マッピング表（確認済み）

| ロジックツリー要素 | Shape名 | Shape Type | 内容 |
|---|---|---|---|
| Main Message | `Title 1` | PLACEHOLDER | スライドの主張（1段落） |
| Chart Title | `Text Placeholder 2` | PLACEHOLDER | サブタイトル（1段落） |
| Main Logic | `Rectangle 4` | AUTO_SHAPE | Para[0]: タイトル（太字、16pt）、Para[1]〜[3]: 3つの要素（12pt）。width=4115016, height=1645160 |
| Sub Logic 1 | `Rectangle 3` | AUTO_SHAPE | Para[0]: タイトル（太字、16pt）、Para[1]〜[3]: 3つの具体的事実（12pt）。width=2326446, height=2664417 |
| Sub Logic 2 | `Rectangle 5` | AUTO_SHAPE | Para[0]: タイトル（太字、16pt）、Para[1]〜[3]: 3つの具体的事実（12pt）。width=2326446, height=2664417 |
| Sub Logic 3 | `Rectangle 18` | AUTO_SHAPE | Para[0]: タイトル（太字、16pt）、Para[1]〜[3]: 3つの具体的事実（12pt）。width=2326446, height=2664417 |
| 意味合い | `TextBox 23` | TEXT_BOX | Para[0]: 「意味合い」ラベル（太字、20pt）、Para[1]〜[3]: 3つの示唆（16pt） |
| 矢印（左） | `Straight Arrow Connector 15` | LINE | Sub Logic 1 → Main Logic（編集不要） |
| 矢印（中） | `Straight Arrow Connector 46` | LINE | Sub Logic 2 → Main Logic（編集不要） |
| 矢印（右） | `Straight Arrow Connector 17` | LINE | Sub Logic 3 → Main Logic（編集不要） |
| think-cell data | `think-cell data - do not delete` | EMBEDDED_OLE | think-cellデータ（編集不要・削除不可） |

## フォント情報

- Main Logic / Sub Logic タイトル: 16pt（203200 EMU）、Bold
- Main Logic / Sub Logic 要素: 12pt（152400 EMU）
- 意味合いタイトル「意味合い」: 20pt（254000 EMU）、Bold、フォント=+mn-ea
- 意味合い各項目: 16pt（203200 EMU）、フォント=+mn-ea
- スタイルはテンプレートの既存runから継承されるため、スクリプトでは run.text だけを上書きする

## テキスト記述フォーマット

各段落は簡潔な文章形式。例:
```
Main Logic タイトル: 当社のデジタル変革は事業成長に直結している
Main Logic 要素: 顧客接点のデジタル化が売上増に貢献
Sub Logic タイトル: 顧客チャネル分析
Sub Logic 要素: EC売上比率が前年比20%増加し全体の35%を占める
Implication 1: FY2025Q2までにパイロットプログラムを開始すべき
Implication 2: シンガポール拠点を起点に展開体制を構築する
Implication 3: 初期導入候補45社へのアプローチを即座に開始する
```
