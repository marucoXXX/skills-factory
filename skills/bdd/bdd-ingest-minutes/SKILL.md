---
name: bdd-ingest-minutes
description: マネジメントインタビュー（マネイン）の議事録・文字起こしを読み込み、BDDプロジェクトの仮説と事実をアップデートするスキル。議事録から発言を「事実（quote）」として抽出し、関連する論点に紐付け、その上で既存仮説の更新（古い仮説をhistoryに退避し、新しい仮説をcurrentに記録、superseded_reasonを必須記入）を行う。議事録から見えた新しい論点があればissues.jsonにも追加する。以下のいずれかのトリガーで必ずこのスキルを使うこと：「議事録を取り込んで」「マネインの結果を反映」「インタビュー議事録から仮説を更新」「マネジメントインタビューを取り込んで」「ヒアリング結果を反映」「議事録ベースで論点を更新」「bdd-ingest-minutes」。BDDプロジェクトのbdd-projectディレクトリが既に存在し、新たな議事録ファイルを読み込ませたい場合に呼び出すこと。
---

# bdd-ingest-minutes: 議事録から仮説をアップデート

マネジメントインタビュー（マネイン）議事録を読み込み、BDDプロジェクト状態を更新するスキル。

## 入力

1. **議事録ファイル**: テキスト・PDF・Word等。マネジメントとの対話形式が一般的
2. **議事録メタ情報**: インタビュー日、対象者（社長・CFO等）、時間、参加者
3. **bdd-projectディレクトリ**: 既存のプロジェクトディレクトリパス（デフォルト: `./bdd-project/`）

ファイル仕様は `bdd-core-issues/references/schema.md` を参照すること。

## 出力

このスキル実行後の変更:
- `sources/minutes/` に議事録ファイルが追加される
- `sources/index.json` に新ソースが登録される
- `facts.json` に発言由来のFactが追加される（type: `quote` 中心）
- `hypotheses.json` の該当仮説が更新される（古い仮説は `history` に退避）
- `issues.json` に新規論点が追加される場合がある
- `meta.json` の `phase` を `Phase3_ManagementInterview` に更新

## 実行手順

### Step 1: プロジェクトの存在確認

`bdd-project/meta.json` が存在しない場合はエラー。`bdd-init` の実行を促す。

### Step 2: 議事録の取り込み

1. 議事録ファイルを `sources/minutes/S-MIN-NNN_{description}.{ext}` にコピー
   - NNNは既存の最大番号 + 1（ゼロ埋め3桁）
2. `sources/index.json` に新規ソースを登録:
   ```json
   {
     "id": "S-MIN-002",
     "type": "minutes",
     "title": "CFOマネジメントインタビュー",
     "filename": "S-MIN-002_cfo_interview.txt",
     "interview_date": "2026-04-30",
     "interviewees": ["CFO ○○"]
   }
   ```

### Step 3: 議事録から事実（Fact）を抽出

議事録を読み込み、以下を Fact として抽出:

**Fact化すべき発言の例**:
- 数値情報の言及: 「売上は来年120億円を目指す」→ `quantitative` Fact
- 戦略・方針の表明: 「価格競争には参加しない」→ `quote` Fact
- 顧客・競合等の固有名詞: 「主要顧客はA社・B社・C社」→ `qualitative` Fact
- 過去の事実の追認: 「2023年に新工場を稼働」→ `qualitative` Fact

**Factとして抽出しない発言**:
- 雑談・社交辞令
- 質問内容そのもの（インタビュアー側の発言は基本除外）
- 推測・仮定の話（「もしかしたら〜かもしれない」レベル）

各Factに付ける情報:
- `source_id`: このS-MIN-NNN
- `source_location`: タイムスタンプ・行番号（特定可能なら）
- `linked_issues`: その発言が関連する論点ID（複数可、最大3つに絞る）
- `type`: 数値なら `quantitative`、引用したい発言なら `quote`、それ以外は `qualitative`

ID採番: `facts.json` の既存最大ID + 1から連番（`F-NNNN`、ゼロ埋め4桁）

### Step 4: 仮説のアップデート

抽出したFactを使って `hypotheses.json` の該当仮説を更新する。

**更新ロジック**:

各Factについて、その `linked_issues` にあるL2論点の仮説を見直す:

1. **既存仮説と整合する場合（Factが仮説を補強）**:
   - `current.supporting_facts` に新FactのIDを追加
   - `current.confidence` を1段階上げる（Low→Mid、Mid→High）
   - `current.updated_at` を更新
   - `current.updated_by_source` を新議事録のIDに更新
   - **`history` には移動しない**（仮説の中身が変わっていないため）

2. **既存仮説と矛盾する場合（Factが仮説を覆す）**:
   - 既存の `current` を `history` 配列の末尾に追加
     - その際 `superseded_at` と `superseded_reason` を必ず記入
     - `superseded_reason` の例: 「マネイン（S-MIN-002）でCFOがCAGR3%と明言、従来の5%仮説を修正」
   - 新しい `current` を作成:
     - `statement`: 新しい仮説の文章
     - `confidence`: Factの強度に応じて（マネジメント直接発言は通常 `High`、ニュアンス込みなら `Mid`）
     - `supporting_facts`: 新FactのIDのみ（古い根拠は引き継がない）
     - `updated_at`: 今日の日付
     - `updated_by_source`: 新議事録のID

3. **新しい仮説の追加（既存仮説では捉えきれない側面）**:
   - 現状の運用では1論点1仮説なので、基本は更新で対応
   - ただし、まったく新しい論点が出た場合は次のStep 5で論点追加+仮説追加

**confidence判定ガイド**:
- `High`: 経営陣の直接発言＋数値で確認＋他ソースとも整合
- `Mid`: 経営陣の発言ベースだが、定性的または1ソースのみ
- `Low`: 推測ベース・ニュアンスからの解釈

### Step 5: 新規論点の追加（必要な場合）

議事録の中で、既存のissues.jsonでカバーされていない重要論点が出てきた場合:

- 議事録に「○○のリスクを最近強く認識している」と社長が言及したが、対応する論点が`issues.json`にない場合
- 議事録に「△△という新規事業の構想がある」と出てきたが、現状のL1-08（成長戦略）配下に該当論点がない場合

このような場合、新規L2論点を `issues.json` に追加:
- ID: 最も適切なL1配下の連番続き
- `source: "project_added"`
- `added_reason`: 「S-MIN-NNN（マネイン）にて○○が言及されたため」
- 同時に `hypotheses.json` にも対応する仮説を追加

### Step 6: meta.json のphase更新

`meta.json` の `phase` を `Phase3_ManagementInterview` に更新（既にPhase3以上なら変更不要）。
`updated_at` も更新。

### Step 7: サマリーをユーザーに提示

実行後の報告内容:

1. **議事録の取り込み**: ソースID、議事録タイトル、対象者
2. **追加されたFact数**: type別（quantitative / qualitative / quote）
3. **更新された仮説**:
   - 強化された仮説（confidenceが上がったもの）の件数とID
   - 修正された仮説（statement自体が変わったもの）の件数と、変更内容のサマリー
4. **追加された新規論点**: あれば件数とID・名前
5. **注目すべき変化**:
   - confidence: High に到達した重要仮説
   - 矛盾が解消されなかった論点（議事録でも答えが出なかった論点）
   - 次回のマネインで深掘りすべき論点の提案

## 注意事項

- **発言の文脈を保持**: 「価格競争には参加しない」だけだとFactとして弱い。「（業界全体が値下げ圧力にある中で）価格競争には参加しない方針」のように、前後の文脈を `statement` に含める
- **仮説の歴史性を守る**: 古い `current` を捨てない。必ず `history` に退避し `superseded_reason` を書く。これが後の説明責任を担保する
- **Factと仮説の境界を死守**: 「社長は○○と言った」は事実。「だから○○の戦略がうまくいく」は仮説。発言内容の評価・判断は仮説側に書く
- **マネジメントの主観バイアスに注意**: マネジメントは自社の戦略を肯定的に語る傾向がある。confidence判定では「経営陣の発言だから即High」とせず、検証可能性で評価する
