# テンプレートShape名マッピング表

GateProcess3.pptx / GateProcess5.pptx を実際に検査して確認済み。

---

## 共通構造

両テンプレートとも1枚スライド構成。左側にファネル図（台形＋楕円）、中央にフィルター詳細、右側に意味合い。

### 共通Shape

| セクション | Shape名 | Shape種別 | 内容 |
|---|---|---|---|
| Main Message | `Title 1` | PLACEHOLDER | スライドタイトル（Main Message） |
| Chart Title | `Text Placeholder 2` | PLACEHOLDER | サブタイトル（Chart Title） |
| フィルター詳細 | `TextBox 9` | TEXT_BOX | フィルターごとの名前＋Feature 2つ（3行 × フィルター数） |
| 意味合い | `TextBox 29` | TEXT_BOX | para[0]「意味合い」固定、para[1]〜para[3]にImplication 3つ |

---

## 3フィルター版（gate-process-3.pptx）

### TextBox 9 の段落構成（9段落）

| 段落 | 内容 | フォントサイズ | Bold |
|---|---|---|---|
| para[0] | Filter1 名前 | 継承（Bold） | True |
| para[1] | Filter1-Feature1 | 14pt (177800) | False |
| para[2] | Filter1-Feature2 | 14pt (177800) | False |
| para[3] | Filter2 名前 | 継承（Bold） | True |
| para[4] | Filter2-Feature1 | 14pt (177800) | False |
| para[5] | Filter2-Feature2 | 14pt (177800) | False |
| para[6] | Filter3 名前 | 継承（Bold） | True |
| para[7] | Filter3-Feature1 | 14pt (177800) | False |
| para[8] | Filter3-Feature2 | 14pt (177800) | False |

### ファネル内のフィルター名ラベル（スライド直下）

| Shape名 | 内容 | フォントサイズ |
|---|---|---|
| `Oval 11` | Filter1 名前 | 14pt (177800) Bold |
| `Oval 3` | Filter2 名前 | 14pt (177800) Bold |
| `Oval 4` | Filter3 名前 | 14pt (177800) Bold |

---

## 5フィルター版（gate-process-5.pptx）

### TextBox 9 の段落構成（15段落）

| 段落 | 内容 | フォントサイズ | Bold |
|---|---|---|---|
| para[0] | Filter1 名前 | 16pt (203200) | True |
| para[1] | Filter1-Feature1 | 12pt (152400) | False |
| para[2] | Filter1-Feature2 | 12pt (152400) | False |
| para[3] | Filter2 名前 | 16pt (203200) | True |
| para[4] | Filter2-Feature1 | 12pt (152400) | False |
| para[5] | Filter2-Feature2 | 12pt (152400) | False |
| para[6] | Filter3 名前 | 16pt (203200) | True |
| para[7] | Filter3-Feature1 | 12pt (152400) | False |
| para[8] | Filter3-Feature2 | 12pt (152400) | False |
| para[9] | Filter4 名前 | 16pt (203200) | True |
| para[10] | Filter4-Feature1 | 12pt (152400) | False |
| para[11] | Filter4-Feature2 | 12pt (152400) | False |
| para[12] | Filter5 名前 | 16pt (203200) | True |
| para[13] | Filter5-Feature1 | 12pt (152400) | False |
| para[14] | Filter5-Feature2 | 12pt (152400) | False |

### ファネル内のフィルター名ラベル（スライド直下）

| Shape名 | 内容 | フォントサイズ |
|---|---|---|
| `Oval 11` | Filter1 名前 | 14pt (177800) Bold |
| `Oval 3` | Filter2 名前 | 14pt (177800) Bold |
| `Oval 40` | Filter3 名前 | 14pt (177800) Bold |
| `Oval 52` | Filter4 名前 | 14pt (177800) Bold |
| `Oval 4` | Filter5 名前 | 14pt (177800) Bold |

**注意**: 両テンプレートともファネル図形はグループ化されておらず、スライド直下に配置。

---

## TextBox 29（意味合い）の段落構成（共通）

| 段落 | 内容 | フォントサイズ | Bold |
|---|---|---|---|
| para[0] | 「意味合い」固定ラベル（編集不要） | 20pt (254000) | True |
| para[1] | Implication 1 | 16pt (203200) | False |
| para[2] | Implication 2 | 16pt (203200) | False |
| para[3] | Implication 3 | 16pt (203200) | False |
