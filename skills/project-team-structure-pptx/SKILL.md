---
name: project-team-structure-pptx
description: >
  プロジェクト体制図（Project Team Structure）のPowerPointスライドを生成するスキル。
  プロジェクトスポンサー・オーナー・PMO・ワーキンググループの階層構造と、
  各グループのメンバー名、および意味合い（Implications）を1枚のスライドに整理する。
  3WG版と5WG版のテンプレートをワーキンググループ数に応じて自動選択する。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - 「プロジェクト体制図」「体制図」「Project Team Structure」「チーム体制図」「体制スライド」という言葉が出た場合
  - 「プロジェクトの体制をスライドにして」「体制をパワポにまとめて」「チーム構成をスライドに」という要望
  - 「プロジェクトスポンサー」「PMO」「ワーキンググループ」「WG」の体制を可視化したいという要望
  - ユーザーが議事録・文字起こしを貼り付けて、プロジェクト体制のスライド化を求めた場合
  - 既にプロジェクト体制情報が整理されたテキストが提示され、PowerPoint化を求められた場合
  - 「誰がスポンサーで誰がオーナーか」「WGメンバーをスライドにまとめて」という要望
  - 「推進体制」「実行体制」「プロジェクト組織図」をスライドにしたいという要望
---

# プロジェクト体制図 PowerPoint ジェネレーター

プロジェクトの推進体制（スポンサー・オーナー・PMO・ワーキンググループ）を階層図として1枚のPowerPointスライドに整理するスキル。

---

## プロジェクト体制図とは

プロジェクトの意思決定構造と実行体制を一覧で示すスライド。以下の要素で構成される。

| 要素 | 定義 | ポイント |
|------|------|------|
| **Main Message** | 体制図全体を総括し、読み手にアクションを促す一文。最大70文字 | 必ず「〜すべき」で締める |
| **Chart Title** | スライドのサブタイトル。体制図のテーマや文脈を端的に示す短いフレーズ（10〜20文字） | Main Messageを補足する文脈を示す |
| **Project Sponsor** | プロジェクトの最高意思決定者・出資責任者 | 役職名＋氏名（例：「取締役 山田太郎」） |
| **Project Owner** | プロジェクトの推進責任者 | 役職名＋氏名 |
| **PMO** | プロジェクトマネジメントオフィス。進捗管理・品質管理の事務局 | 組織名または役職名＋氏名 |
| **Working Group（WG）** | 各テーマ別の実行チーム（3〜5グループ） | WG名＋メンバー最大5名 |
| **意味合い（Implications）** | この体制の特徴・留意点・成功のポイント（最大5点） | 体制の設計意図や注意点を記述 |

### 記述ルール

- **Main Message**: 最大70文字。体制図全体を一言で総括し、必ず「〜すべき」で終える。ユーザーが指定した場合はそのまま使用、指定がない場合は内容をもとにドラフトして確認を取る。
- **Chart Title**: 10〜20文字程度。Main Messageのテーマを補足する文脈フレーズ。ユーザーが指定しない場合はドラフトして確認を取る。
- **WG数は3〜5**（3WG版テンプレートまたは5WG版テンプレートを使用。4WGの場合は5WG版テンプレートを使い、WG5を空欄にして非表示にする）
- **各WGのメンバーは最大5名**
- **意味合いは最大5点**
- **WG名のフォーマット**: WG名を `[WG名]` の `[]` なしで記述する（例: `データ基盤構築`）
- **メンバー名のフォーマット**: 氏名をそのまま記述（例: `佐藤花子`）。空欄のメンバー枠は空文字列にする。

---

## 入力パターンと処理フロー

### パターンA：議事録・文字起こしが入力された場合

**いきなりPowerPointを作成しない**

1. **Step 1: 体制情報ドラフトを作成する**（後述の抽出ガイドラインに従う）
2. **Step 2: Markdownでユーザーに提示**し、確認・修正を求める
3. **Step 3: ユーザーの承認後**、PowerPointを生成する

### パターンB：体制情報が整理されたテキストが入力された場合

1. **Step 1: 内容を確認**し、必要な要素が揃っているか確認
2. 不足・曖昧な点があれば修正提案を行う
3. **Step 2: 確認後、PowerPointを生成する**

---

## Step 1: 議事録からプロジェクト体制を抽出する

### スポンサー・オーナー・PMOの抽出

議事録から**意思決定構造**を読み取る。以下のような表現を探す：
- 「〜が責任者」「〜がスポンサー」「〜が統括」「〜がオーナー」
- 「PMO は〜」「事務局は〜」「進捗管理は〜が担当」
- 役職・肩書の言及（部長、取締役、マネージャーなど）

### ワーキンググループの抽出

議事録から**チーム構成**を読み取る：
- 「〜チーム」「〜WG」「〜グループ」「〜班」
- メンバーの名前とチーム配属の言及
- 各チームの役割・担当領域

ポイント: WG名はそのチームの担当領域を端的に示す名称にする（例: 「データ基盤構築WG」「業務プロセス改革WG」）。

### 意味合い（Implications）の抽出・ドラフト

議事録に体制の留意点・設計意図が明示されていれば抽出。**明示されていない場合は、戦略コンサルタントとして論理的にドラフトする**：
- この体制構成の狙い・メリット
- 横断的な連携ポイント
- リスクや留意事項
- ドラフトした場合は「※ドラフト」と明記する

---

## Step 2: 体制情報のMarkdown出力フォーマット

ユーザーに確認を求める際は、以下のフォーマットで出力する：

```markdown
## プロジェクト体制図 整理結果

**Main Message（※ドラフト）**
〜すべき（最大70文字）

**Chart Title（※ドラフト）**
〜のテーマ

### 体制

| 役割 | 担当 |
|------|------|
| Project Sponsor | 取締役 山田太郎 |
| Project Owner | 部長 鈴木一郎 |
| PMO | 経営企画部 |

### ワーキンググループ

**WG1: データ基盤構築**
1. 佐藤花子
2. 田中次郎
3. 高橋三郎

**WG2: 業務プロセス改革**
1. 伊藤四郎
2. 渡辺五郎

**WG3: チェンジマネジメント**
1. 小林六子
2. 加藤七郎
3. 吉田八郎

### 意味合い（Implications）
1. 意味合い1
2. 意味合い2
3. 意味合い3
4. 意味合い4
5. 意味合い5
```

確認メッセージ例：
> 上記のプロジェクト体制図でよろしいでしょうか？Main MessageとChart Titleも含めて修正があればお知らせください。確認後にPowerPointを生成します。

---

## Step 3: PowerPointの生成

### テンプレートの選択

WG数に応じてテンプレートを選択する：

| WG数 | テンプレート |
|------|------|
| 3 | `assets/ProjectTeamStructure3.pptx` |
| 4〜5 | `assets/ProjectTeamStructure5.pptx` |

```bash
# 3WGの場合
TEMPLATE="/mnt/skills/organization/project-team-structure-pptx/assets/ProjectTeamStructure3.pptx"
# 4〜5WGの場合
TEMPLATE="/mnt/skills/organization/project-team-structure-pptx/assets/ProjectTeamStructure5.pptx"
```

テンプレートを初めて使う前に、以下で構造を確認すること：

```bash
pip install "markitdown[pptx]" -q --break-system-packages
python -m markitdown <TEMPLATE_PATH>
```

テンプレートのShape名は実際に確認してからマッピングすること。`references/template-mapping.md` に確認後の対応表を記載する。

### 体制データのJSON化

体制内容を `/home/claude/team_data.json` に以下の形式で保存する：

```json
{
  "main_message": "〜すべき（最大70文字）",
  "chart_title": "〜のテーマ（10〜20文字）",
  "project_sponsor": "取締役 山田太郎",
  "project_owner": "部長 鈴木一郎",
  "pmo": "経営企画部",
  "working_groups": [
    {
      "name": "データ基盤構築",
      "members": ["佐藤花子", "田中次郎", "高橋三郎", "", ""]
    },
    {
      "name": "業務プロセス改革",
      "members": ["伊藤四郎", "渡辺五郎", "", "", ""]
    },
    {
      "name": "チェンジマネジメント",
      "members": ["小林六子", "加藤七郎", "吉田八郎", "", ""]
    }
  ],
  "implications": [
    "意味合い1",
    "意味合い2",
    "意味合い3",
    "意味合い4",
    "意味合い5"
  ]
}
```

**注意事項：**
- `working_groups` は3〜5個。`members` は常に5要素の配列にする（不足分は空文字列 `""` で埋める）
- `implications` は最大5個の配列
- 4WGの場合、5WGテンプレートを使い、5番目のWGは `name: ""`, `members: ["","","","",""]` とする

### スクリプト実行コマンド

```bash
python /mnt/skills/organization/project-team-structure-pptx/scripts/fill_team.py \
  --data /home/claude/team_data.json \
  --template <TEMPLATE_PATH> \
  --output /mnt/user-data/outputs/ProjectTeamStructure_output.pptx
```

### 出力確認

```bash
python -m markitdown /mnt/user-data/outputs/ProjectTeamStructure_output.pptx
```

内容が正しく反映されているか確認し、ユーザーに提示する。

---

## 品質チェックリスト

PowerPoint生成後、以下を確認：

- [ ] Main Messageが70文字以内で「〜すべき」で終わっているか
- [ ] Chart Titleが10〜20文字程度で文脈を的確に示しているか
- [ ] Project Sponsor / Owner / PMO が正しく記入されているか
- [ ] WG数に応じた正しいテンプレートが選択されているか
- [ ] 各WGの名前とメンバーが正しく記入されているか
- [ ] 意味合いが最大5点記述されているか
- [ ] PPTXのmarkitdown出力でプレースホルダーが残っていないか（WG4-Name1等のプレースホルダテキストが残っていないか）

---

## アセット

| ファイル名 | 用途 |
|---|---|
| `assets/ProjectTeamStructure3.pptx` | 3WG版テンプレート |
| `assets/ProjectTeamStructure5.pptx` | 5WG版テンプレート |

## スクリプト

| ファイル名 | 用途 |
|---|---|
| `scripts/fill_team.py` | team_data.jsonの内容をテンプレートに流し込み、PPTXを出力する |

## 参考

| ファイル名 | 内容 |
|---|---|
| `references/template-mapping.md` | テンプレートのShape名と体制要素のマッピング表 |
| `references/examples.md` | プロジェクト体制図の良い例・悪い例 |
