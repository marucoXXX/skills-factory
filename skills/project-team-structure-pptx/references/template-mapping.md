# テンプレートShape名マッピング表

ProjectTeamStructure3.pptx / ProjectTeamStructure5.pptx を実際に検査して確認済み。

---

## 3WG版テンプレート（ProjectTeamStructure3.pptx）

### 共通要素

| 体制要素 | Shape名 | Shape種別 | 内容 |
|---|---|---|---|
| Main Message | `Title 1` | PLACEHOLDER | para[0] にメインメッセージ |
| Chart Title | `Text Placeholder 2` | PLACEHOLDER | para[0] にチャートタイトル |
| Project Sponsor | `Rectangle 3` | AUTO_SHAPE | para[0] にスポンサー名 |
| Project Owner | `Rectangle 5` | AUTO_SHAPE | para[0] にオーナー名 |
| PMO | `Rectangle 6` | AUTO_SHAPE | para[0] にPMO名 |
| 意味合い | `TextBox 9` | TEXT_BOX | para[0]=見出し（編集不要）, para[1]〜para[5]=Implication 5件 |

### ワーキンググループ

| WG | Shape名 | para[0] | para[1]〜para[5] |
|---|---|---|---|
| WG1（中央） | `Rectangle 12` | WG名 | メンバー5名 |
| WG2（左） | `Rectangle 22` | WG名 | メンバー5名 |
| WG3（右） | `Rectangle 23` | WG名 | メンバー5名 |

### コネクタ（編集不要）

| Shape名 | 用途 |
|---|---|
| `Straight Connector 10` | Sponsor→Owner 縦線 |
| `Straight Connector 13` | Owner→WG 縦線 |
| `Straight Connector 16` | WG 横線 |

### フォント情報

- Sponsor/Owner/PMO/WG: 14pt（177800 EMU）
- 意味合い見出し: 20pt（254000 EMU）Bold
- 意味合い本文: 16pt（203200 EMU）

---

## 5WG版テンプレート（ProjectTeamStructure5.pptx）

### 共通要素

3WG版と同一のShape名・構造。

### ワーキンググループ

| WG | Shape名 | 位置（左から順） |
|---|---|---|
| WG4（最左） | `Rectangle 4` | x=370800 |
| WG2 | `Rectangle 22` | x=1919277 |
| WG1（中央） | `Rectangle 12` | x=3467755 |
| WG3 | `Rectangle 23` | x=5016232 |
| WG5（最右） | `Rectangle 8` | x=6564709 |

### テンプレートでのWG番号と画面位置の対応

左から右への並び順:  WG4 → WG2 → WG1 → WG3 → WG5

**スクリプトでのマッピング（ユーザー入力のWG順序 → テンプレートShape）:**

| ユーザー入力順 | 画面位置 | テンプレートShape |
|---|---|---|
| WG[0]（1番目） | 最左 | `Rectangle 4` |
| WG[1]（2番目） | 左寄り | `Rectangle 22` |
| WG[2]（3番目） | 中央 | `Rectangle 12` |
| WG[3]（4番目） | 右寄り | `Rectangle 23` |
| WG[4]（5番目） | 最右 | `Rectangle 8` |

3WG版でのマッピング:

| ユーザー入力順 | 画面位置 | テンプレートShape |
|---|---|---|
| WG[0]（1番目） | 左 | `Rectangle 22` |
| WG[1]（2番目） | 中央 | `Rectangle 12` |
| WG[2]（3番目） | 右 | `Rectangle 23` |

### フォント情報

- Sponsor/Owner/PMO/WG: 12pt（152400 EMU）
- 意味合い見出し: 20pt（254000 EMU）Bold
- 意味合い本文: 16pt（203200 EMU）
