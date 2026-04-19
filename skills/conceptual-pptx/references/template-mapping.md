# テンプレートShape名マッピング表

Conceptual3.pptx / Conceptual5.pptx を実際に検査して確認済み。

---

## Conceptual3.pptx（3コンセプト版）— 詳細2行

1枚スライド構成。左側に楕円の重なり図、右側にコンセプト名＋詳細テキスト2行。

### マッピング表（確認済み）

| 要素 | Shape名 | Shape Type | 内容 |
|---|---|---|---|
| Main Message | `Title 1` | PLACEHOLDER | スライド上部のメインメッセージ |
| Chart Title | `Text Placeholder 2` | PLACEHOLDER | サブタイトル |
| Concept1 楕円ラベル | `Oval 4` | AUTO_SHAPE | 楕円内のコンセプト名 |
| Concept2 楕円ラベル | `Oval 6` | AUTO_SHAPE | 楕円内のコンセプト名 |
| Concept3 楕円ラベル | `Oval 7` | AUTO_SHAPE | 楕円内のコンセプト名 |
| Concept1 テキスト | `TextBox 8` | TEXT_BOX | Para[0]: 名前（Bold, 20pt）、Para[1]: 詳細1（16pt）、Para[2]: 詳細2（16pt） |
| Concept2 テキスト | `TextBox 9` | TEXT_BOX | Para[0]: 名前（Bold, 20pt）、Para[1]: 詳細1（16pt）、Para[2]: 詳細2（16pt） |
| Concept3 テキスト | `TextBox 10` | TEXT_BOX | Para[0]: 名前（Bold, 20pt）、Para[1]: 詳細1（16pt）、Para[2]: 詳細2（16pt） |
| think-cell data | `think-cell data - do not delete` | EMBEDDED_OLE_OBJECT | 編集不要 |

---

## Conceptual5.pptx（5コンセプト版）— 詳細1行

1枚スライド構成。左側に楕円の重なり図（5つ）、右側にコンセプト名＋詳細テキスト1行。

### マッピング表（確認済み）

| 要素 | Shape名 | Shape Type | 内容 |
|---|---|---|---|
| Main Message | `Title 1` | PLACEHOLDER | スライド上部のメインメッセージ |
| Chart Title | `Text Placeholder 2` | PLACEHOLDER | サブタイトル |
| Concept1 楕円ラベル | `Oval 4` | AUTO_SHAPE | 楕円内のコンセプト名 |
| Concept2 楕円ラベル | `Oval 6` | AUTO_SHAPE | 楕円内のコンセプト名 |
| Concept3 楕円ラベル | `Oval 7` | AUTO_SHAPE | 楕円内のコンセプト名 |
| Concept4 楕円ラベル | `Oval 11` | AUTO_SHAPE | 楕円内のコンセプト名 |
| Concept5 楕円ラベル | `Oval 12` | AUTO_SHAPE | 楕円内のコンセプト名 |
| Concept1 テキスト | `TextBox 8` | TEXT_BOX | Para[0]: 名前（Bold, 20pt）、Para[1]: 詳細（16pt） |
| Concept2 テキスト | `TextBox 9` | TEXT_BOX | Para[0]: 名前（Bold, 20pt）、Para[1]: 詳細（16pt） |
| Concept3 テキスト | `TextBox 10` | TEXT_BOX | Para[0]: 名前（Bold, 20pt）、Para[1]: 詳細（16pt） |
| Concept4 テキスト | `TextBox 13` | TEXT_BOX | Para[0]: 名前（Bold, 20pt）、Para[1]: 詳細（16pt） |
| Concept5 テキスト | `TextBox 14` | TEXT_BOX | Para[0]: 名前（Bold, 20pt）、Para[1]: 詳細（16pt） |
| think-cell data | `think-cell data - do not delete` | EMBEDDED_OLE_OBJECT | 編集不要 |

---

## フォント情報

- コンセプト名（TextBox Para[0]）: 20pt（254000 EMU）、Bold
- コンセプト詳細（TextBox Para[1], Para[2]）: 16pt（203200 EMU）
- 楕円内ラベル: 16pt（203200 EMU）、Bold
- スタイルはテンプレートの既存runから継承されるため、スクリプトでは run.text だけを上書きする
