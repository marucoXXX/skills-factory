---
name: logic-tree-pptx
description: >
  帰納法によるロジックツリー（Logic Tree）のPowerPointスライドを生成するスキル。
  複数のSub Logic（具体的事実・根拠）からMain Logic（結論）を帰納的に導出し、
  意味合い（Implications）とともに1枚のロジックツリースライドにまとめる。
  Barbara MintoのPyramid Principleに基づくボトムアップ型の論理構成。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - 「ロジックツリー」「Logic Tree」「ロジツリー」「帰納法スライド」という言葉が出た場合
  - 「根拠から結論をまとめてスライドにして」「議事録からロジックツリーを作りたい」という要望
  - 「ピラミッドストラクチャーのスライド」「ボトムアップで論理を組み立てて」という要望
  - ユーザーが議事録・文字起こしを貼り付けて、ロジックツリーやロジック整理のスライド化を求めた場合
  - 既にロジックツリー形式で整理されたテキストが提示され、PowerPoint化を求められた場合
  - 「主張と根拠をスライドにまとめて」「So What?でまとめて」という要望
---

# Logic Tree PowerPoint ジェネレーター

Barbara Mintoの**Pyramid Principle**に基づく帰納法ロジックツリーを使い、複数の根拠から結論を導出するPowerPointスライドを生成するスキル。

---

## 帰納法によるロジックツリーとは

帰納法（Inductive Reasoning）は、複数の**具体的な事実・観察事項**から共通点や法則を見出し、**一般的な結論**を導き出す論理的推論手法。ロジックツリーにおいては、下位の具体的根拠（Sub Logic）から上位の結論（Main Logic）を「So What?（だから何が言えるか？）」で導出する。

**ロジックツリーの論理構造（ボトムアップ）：**

```
Sub Logic 1（事実・根拠）─┐
Sub Logic 2（事実・根拠）─┼─→ Main Logic（帰納的結論）─→ 意味合い（Implications）
Sub Logic 3（事実・根拠）─┘
```

各Sub Logicはさらに3つの具体的根拠で裏付けられる。Main Logicは3つのSub Logicを帰納的にまとめた結論であり、3つの要素で構成される。

**帰納法で結論を導く際のポイント：**
- 根拠となる事実は**客観的で具体的**であること（数値・データ・ファクトベース）
- 3つのSub Logicは**MECE（漏れなくダブりなく）**を意識して選ぶ
- Main Logicは根拠の**共通点を抽出して一般化**したものであること
- 「So What?」（だから何？）と「Why So?」（なぜそう言えるのか？）の双方向で論理が通ること
- **飛躍のない納得感**が最も重要（無理な一般化は禁物）

---

## テンプレート要素と記述ルール

| 要素 | 定義 | ルール |
|------|------|--------|
| **Main Message** | スライド全体の主張。聴き手にアクションを促す一文 | 最大70文字。必ず「〜すべき」で締める |
| **Chart Title** | スライドのサブタイトル。テーマや文脈を端的に示す | 10〜20文字程度 |
| **Main Logic** | 3つのSub Logicから帰納的に導出された結論。3つの要素で構成 | タイトル（太字）+ 3つの根拠要素 |
| **Sub Logic 1〜3** | 具体的事実・データに基づく根拠群。各3つの要素で構成 | 各Sub Logicにタイトル（太字）+ 3つの具体的事実 |
| **意味合い** | Main Logicから導かれる示唆・次のアクション。**3項目** | 各項目は具体的なアクションや示唆を簡潔に記述 |

### 記述の詳細ルール

- **Main Message**: 最大70文字。ロジックツリー全体の結論を一言で総括し、「〜すべき」で終える
- **Chart Title**: 10〜20文字。Main Messageの文脈を補足するフレーズ
- **Main Logic**:
  - タイトル（Para[0]）: Sub Logic群を総括した結論ラベル（太字、16pt）
  - 要素1〜3（Para[1]〜[3]）: 各Sub Logicから導出された主要ポイント（12pt）
- **Sub Logic 1〜3**: 各ボックスに4段落
  - タイトル（Para[0]）: そのSub Logicのテーマ（太字、16pt）
  - 要素1〜3（Para[1]〜[3]）: 具体的事実・データ・根拠（12pt）
- **意味合い**: Main Logicから導かれるビジネス上の示唆やNext Step。**3項目**で記述
  - タイトル（Para[0]）: 「意味合い」固定（太字、20pt）※編集不要
  - 項目1〜3（Para[1]〜[3]）: 各示唆・アクション（16pt）。具体的かつ実行可能な打ち手にする

---

## 入力パターンと処理フロー

### パターンA：議事録・文字起こしが入力された場合

**いきなりPowerPointを作成しない**

1. **Step 1: ロジックツリーのドラフトを作成する**（後述の抽出ガイドラインに従う）
2. **Step 2: Markdownでユーザーに提示**し、確認・修正を求める
3. **Step 3: ユーザーの承認後**、PowerPointを生成する

### パターンB：ロジックツリーの内容が直接指定された場合

1. **Step 1: 内容を確認**し、Sub Logic→Main Logicの帰納的論理が通っているか確認
2. 不足・曖昧な点があれば修正提案を行う
3. **Step 2: 確認後、PowerPointを生成する**

---

## Step 1: 議事録からロジックツリーを抽出する

### 抽出の考え方

議事録からロジックツリーを構築する際は、**ボトムアップ**で考える：
1. まず議事録から**具体的事実・データ・意見**を拾い出す
2. それらを**3つのテーマ（Sub Logic）にグルーピング**する（MECEを意識）
3. 各Sub Logicから**「So What?」で上位のMain Logic**を導出する
4. Main Logicから**意味合い（示唆・Next Step）**を導出する
5. 最後にMain Messageを策定する

### Sub Logicの抽出

議事録から**客観的事実・データ・具体的根拠**を探す：
- 数字・指標・市場データ・調査結果
- 「〜というデータがある」「〜の実績がある」「〜が判明した」
- 参加者が提示したファクトベースの情報
- 3つのSub Logicは**異なる視点・切り口**でグルーピングする

### Main Logicの導出

3つのSub Logicから**帰納的に結論を導く**：
- 「Sub Logic 1, 2, 3から何が言えるか？（So What?）」
- 共通するパターン・傾向・法則性を見出す
- **飛躍なく、納得感のある一般化**にする
- Main Logic内の3つの要素は、各Sub Logicの要約に対応する

### 意味合いの導出

Main Logicから**ビジネス上の示唆・アクション**を**3項目**導く：
- 明示されていれば議事録から抽出
- 明示されていなければ、コンサルタントとしてドラフトし「※ドラフト」と明記
- 各項目は**具体的かつ実行可能な打ち手・提言**にする（「検討する」ではなく「実施する」）
- Main Logicの各要素に対応する示唆を1つずつ導くと整理しやすい

---

## Step 2: ロジックツリーのMarkdown出力フォーマット

ユーザーに確認を求める際は、以下のフォーマットで出力する：

```markdown
## ロジックツリー整理結果

**Main Message（※ドラフト）**
〜すべき（最大70文字）

**Chart Title（※ドラフト）**
〜のテーマ（10〜20文字）

### Main Logic: [タイトル]
1. [要素1: 各Sub Logicの要約に対応するポイント]
2. [要素2: 各Sub Logicの要約に対応するポイント]
3. [要素3: 各Sub Logicの要約に対応するポイント]

### Sub Logic 1: [タイトル]
1. [具体的事実/データ]
2. [具体的事実/データ]
3. [具体的事実/データ]

### Sub Logic 2: [タイトル]
1. [具体的事実/データ]
2. [具体的事実/データ]
3. [具体的事実/データ]

### Sub Logic 3: [タイトル]
1. [具体的事実/データ]
2. [具体的事実/データ]
3. [具体的事実/データ]

### 意味合い
1. [示唆・アクション1]
2. [示唆・アクション2]
3. [示唆・アクション3]
```

確認メッセージ例：
> 上記のロジックツリー整理でよろしいでしょうか？Main MessageとChart Titleも含めて修正があればお知らせください。確認後にPowerPointを生成します。

---

## Step 3: PowerPointの生成

### テンプレートの参照

テンプレートは `assets/logic-tree-template.pptx` を使用する。

```bash
TEMPLATE="<SKILL_DIR>/assets/logic-tree-template.pptx"
```

※ `<SKILL_DIR>` はスキルがインストールされたディレクトリパスに読み替えること。

テンプレートを初めて使う前に、以下で構造を確認すること：

```bash
pip install "markitdown[pptx]" python-pptx -q --break-system-packages
python -m markitdown <SKILL_DIR>/assets/logic-tree-template.pptx
```

テンプレートのShape名は `references/template-mapping.md` に記載済み。

### ロジックツリーデータのJSON化

ロジックツリーの内容を `{{WORK_DIR}}/logic_tree_data.json` に以下の形式で保存する：

```json
{
  "main_message": "〜すべき（最大70文字）",
  "chart_title": "〜のテーマ（10〜20文字）",
  "main_logic": {
    "title": "Main Logicのタイトル",
    "points": [
      "要素1の文章",
      "要素2の文章",
      "要素3の文章"
    ]
  },
  "sub_logics": [
    {
      "title": "Sub Logic 1のタイトル",
      "points": [
        "具体的事実1",
        "具体的事実2",
        "具体的事実3"
      ]
    },
    {
      "title": "Sub Logic 2のタイトル",
      "points": [
        "具体的事実1",
        "具体的事実2",
        "具体的事実3"
      ]
    },
    {
      "title": "Sub Logic 3のタイトル",
      "points": [
        "具体的事実1",
        "具体的事実2",
        "具体的事実3"
      ]
    }
  ],
  "implications": [
    "示唆1の文章",
    "示唆2の文章",
    "示唆3の文章"
  ]
}
```

### スクリプト実行コマンド

```bash
python <SKILL_DIR>/scripts/fill_logic_tree.py \
  --data {{WORK_DIR}}/logic_tree_data.json \
  --template <SKILL_DIR>/assets/logic-tree-template.pptx \
  --output {{OUTPUT_DIR}}/LogicTree_output.pptx
```

### 出力確認

```bash
python -m markitdown {{OUTPUT_DIR}}/LogicTree_output.pptx
```

内容が正しく反映されているか確認し、ユーザーに提示する。

---

## 品質チェックリスト

PowerPoint生成後、以下を確認：

- [ ] Main Messageが70文字以内で「〜すべき」で終わっているか
- [ ] Chart Titleが10〜20文字程度で文脈を的確に示しているか
- [ ] Main Logicのタイトルが各Sub Logicを総括した結論になっているか
- [ ] Main Logicの3要素が各Sub Logicの「So What?」に対応しているか
- [ ] 各Sub Logicが3つずつの具体的事実・データで構成されているか
- [ ] Sub Logic → Main Logicの帰納的論理が通っているか（飛躍がないか）
- [ ] Main Logic → Sub Logicの「Why So?」が成り立つか
- [ ] Sub Logic間がMECEを意識して分類されているか
- [ ] 意味合いが3項目あり、論理的にMain Logicから導かれているか
- [ ] ドラフト項目に「※ドラフト」が付いているか
- [ ] PPTXのmarkitdown出力でプレースホルダーテキストが残っていないか

---

## アセット

| ファイル名 | 用途 |
|---|---|
| `assets/logic-tree-template.pptx` | ロジックツリースライドテンプレート（Shape構造は references/template-mapping.md 参照） |

## スクリプト

| ファイル名 | 用途 |
|---|---|
| `scripts/fill_logic_tree.py` | logic_tree_data.jsonの内容をlogic-tree-template.pptxに流し込み、PPTXを出力する |

## 参考

| ファイル名 | 内容 |
|---|---|
| `references/template-mapping.md` | テンプレートのShape名とロジックツリー各要素のマッピング表 |
| `references/logic-tree-examples.md` | ロジックツリー整理の良い例・悪い例集 |
