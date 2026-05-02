# skills_factory × 12箇条 依存度マップ（Phase A）

**目的**: skills_factory の各構成要素が Claude Code ランタイムにどれだけ依存しているかを 12箇条 × 3層で評価し、runtime 非依存化のための修正方針を立てる前段とする。

**読み方**: 🟢=非依存（既に良い）/ 🟡=部分依存（軽微な修正で済む）/ 🔴=強く依存（設計変更レベル）

**サンプル対象**: Orchestrator は `market-overview-agent` (793行) / `company-deepdive-agent` (465行) / `business-deepdive-agent` (462行) の3本、PPTX は `market-environment-pptx` / `competitor-summary-pptx`、ビルドは `tools/build_skill.py` を depth-first で精読。

---

## 0. 3層の定義

| 層 | 何か | 該当ファイル例 |
|---|---|---|
| **L1: Pythonスクリプト層** | argparse でJSONを受けてPPTXを吐く確定的な計算 | `fill_*.py`, `merge_pptx_v2.py`, `render_pptx.py`, `build_skill.py` |
| **L2: 個別PPTXスキル SKILL.md** | LLMがJSONを組み立てる手順書＋スクリプトのCLI仕様 | `market-environment-pptx/SKILL.md` 等 50+ 個 |
| **L3: Orchestrator SKILL.md** | 10ステップ以上の調査→生成→マージ→レビューの長い手順書 | `market-overview-agent` / `company-deepdive-agent` / `business-deepdive-agent` / `strategy-report-agent` / `smallcap-strategy-research` / `bdd-report` / `market-overview-agent` 等 |

---

## 1. 12箇条 × 3層 ヒートマップ

| # | 原則 | L1 Script | L2 PPTX SKILL | L3 Orchestrator |
|---|---|---|---|---|
| 1 | 自然言語→ツール呼び出し変換 | 🟢 | 🟡 | 🟡 |
| 2 | プロンプトをコードとして管理 | 🟢 | 🟢 | 🟡 |
| 3 | コンテキストウィンドウ制御 | 🟢 | 🟡 | 🔴 |
| 4 | ツール=構造化出力（単一関数） | 🟢 | 🟢 | 🔴 |
| 5 | 実行状態と業務状態の統合 | 🟢 | 🟢 | 🟡 |
| 6 | 開始・停止・再開シンプル | 🟢 | 🟢 | 🟡 |
| 7 | 人間とのやり取り=ツール | 🟢 N/A | 🟡 | 🟡 |
| 8 | 制御フローはアプリ側 | 🟢 | 🟡 | 🔴 |
| 9 | エラーをコンテキストに圧縮 | 🟢 | 🟢 | 🟡 |
| 10 | 小さく責務明確（3-10ステップ） | 🟢 | 🟢 | 🔴 |
| 11 | どこからでも起動 | 🟢 | 🟡 | 🔴 |
| 12 | ステートレス・リデューサ | 🟢 | 🟢 | 🟡 |

**集計**: L1=12🟢 / L2=8🟢 4🟡 0🔴 / L3=0🟢 7🟡 5🔴

---

## 2. 詳細所見

### L1: Pythonスクリプト層 — 全項目🟢

`fill_market_environment.py:566-600` の `main()` が代表例:

- argparse で `--data --template --output` を受ける CLI（#11どこからでも起動 ✓）
- `len(main_message) > 65` を `ValueError` で hard-fail（#9 エラー圧縮 ✓、#1 構造化検証 ✓）
- 状態を持たない純粋関数: `(data, template) → pptx`（#12 ステートレス ✓）
- LLMに依存しない（#3 コンテキスト N/A）

`tools/build_skill.py` も同様に純粋: `{{VAR}}` 置換 + `@if/@endif` フィルタの確定的処理。`profiles/claude_code.json` と `profiles/claude_ai.json` で **ターゲットランタイムを既に分離している**（runtime非依存化を意識した設計が一部存在する証拠）。

**結論**: L1は既に runtime 非依存。修正不要。

### L2: 個別PPTXスキル SKILL.md — 大半🟢、対話部分のみ🟡

`market-environment-pptx/SKILL.md` を例に:

- **🟢 強い点**: JSONスキーマが完全に書かれていて型・必須・制約が明示されている (`SKILL.md:300-333`)。fill_*.py への CLI 仕様も明示 (`SKILL.md:340-346`)。出力は単一関数 (#4 ✓)。
- **🟡 弱い点1（#1, #7）**: Step 1-4 のフロー（ソース探索 → 候補提示 → ユーザー選択 → データ収集 → Markdown承認）が **「LLMが web_search / web_fetch / ask_user_input を順に呼ぶ」前提**で書かれている。`ask_user_input` は擬似名で、実体は AskUserQuestion (Claude Code) または手動入力。
- **🟡 弱い点2（#11）**: 「業界名のみ」入力からの起動はLLM対話前提。「整理済みデータJSON」を直接渡す Pattern C は CLI起動可能だが、Pattern A (web探索フロー) はチャットUI依存。

**結論**: L2は **「fill_*.py CLIが入口」のパスは既に runtime非依存**。「web探索→対話→JSON組立」のパスだけが harness 依存。

### L3: Orchestrator SKILL.md — 半数が🔴

代表例 `market-overview-agent/SKILL.md` 793行 / 10ステップ:

#### 🔴 #3 コンテキストウィンドウ制御

- SKILL.md 793行が trigger phrase で **全文** がLLM context にロードされる
- `_common/prompts/*.md` (5本) も `<!-- source: ... -->` コメントで手動コピペで埋め込まれている → SKILL.md内に重複展開
- Step 1 の Web検索結果（5論点 × 5-8件 = 25-40件）が context に積まれる
- Step ごとに必要な情報をフィルタする機構は無い
- **問題**: 「とりあえず大量のコンテクストをLLMに渡してあとはよしなに」のアンチパターンに該当

#### 🔴 #4 ツール=構造化出力

- Orchestrator自体が「複数のツールと判断ロジックを内包する10ステップ手順書」になっている
- `Step 0 → Step 0.5 → Step 1 → Step 2 → Step 2.5 → Step 3 → ... → Step 10` を LLM が SKILL.md を読みながら順次実行する設計
- **単一の関数として説明できない**

#### 🔴 #8 制御フローはアプリ側

- 中核問題。LLM が SKILL.md を読んで分岐・ループ・順序を決める
- 例: `Step 8-b` の overall_verdict 分岐 (`pass`/`needs_fixes`/`reject`) → LLMが判断
- 例: 自動修正ループのカウンタは「LLMが必ず持つこと」と明記 (`SKILL.md:782`) — **強制機構なし**
- 「他の開発者から『これはどういう処理フローなの？』と聞かれたら？」 → 「SKILL.md を読んでください」としか答えられない

#### 🔴 #10 小さく責務明確（3-10ステップ）

- market-overview-agent: Step 0 / 0.5 / 1 / 2 / 2.5 / 3 / 4 / 5 / 6 (a/b) / 7 / 8 (a/b/loop) / 9 / 10 = 実質 14+ ステップ
- 「巨大な万能エージェント」に該当

#### 🔴 #11 どこからでも起動

- トリガー: チャット内の自然文（「XX市場を調べて」）
- Step 0 の AskUserQuestion で対話必須 → cron / webhook / Slack 起動不可
- programmatic entry point 無し

#### 🟡 良い点（部分対応済み）

- **#5 実行状態統合（🟡）**: `{{WORK_DIR}}/<run_id>/` 配下に `scope.json` / `data_NN_*.json` / `merge_order.json` / `fact_check_report.json` / `visual_review_report.json` を吐く。**ファイルベースの中間状態が比較的整理されている**
- **#9 エラー圧縮（🟡）**: visual-quality-reviewer 自動修正ループ (max 2 round) は良い設計。`regeneration_hint` で構造化されたフィードバックを次の実行に渡す
- **#7 人間とのやり取り（🟡）**: AskUserQuestion での Step 0 / 2.5 / 3 の構造化承認ポイントは設計されている。ただし AskUserQuestion 自体が harness ツール
- **#12 ステートレス（🟡）**: 状態はファイルに永続化されている。ただし「resume(state, input)→new_state」のインターフェースは無く、LLM が dir を読んで「Step 5 の続きから」を自分で判断する

---

## 3. 依存パターン分類（Phase A.5 改訂版）

> **改訂経緯（4/30 セッション後半）**: ユーザー指摘により framing を修正。当初の「Python state machine 化」案を撤回し、**SKILL.md は宣言的手順書として残す + Claude Code ハーネス側の機構（hooks / settings / subagent / TaskCreate / AskUserQuestion）で LLM の遵守を強制する** 方向で再分類。詳細は Section 4 と `~/.claude/plans/md-llm-melodic-twilight.md` 参照。

ヒートマップを根本原因でグルーピングし、各パターンに対する **3 レバー（①②③）** での打ち手を整理:

### パターン①: 「LLMが SKILL.md を読んで手順を解釈する」依存

- **影響項目**: #3, #4, #8, #10
- **どこで起きる**: L3 Orchestrator
- **根本原因**: 制御フローが SKILL.md の自然言語手順書として表現されており、LLMが手順を端折っても検出機構がない
- **修正方向**:
  - **レバー①（hooks + settings.json）**: PreToolUse hook で「Step N+1 のツールを呼ぶ前に Step N の前提条件（ファイル存在 / TaskUpdate 完了 等）を assert」。description を絞って context 過剰ロードを防ぐ
  - **レバー②（subagent 分割）**: 10 ステップ超の orchestrator のうち、Web 検索や要約等の独立フェーズを subagent に切り出し、context と責務を分割
  - **レバー③（TaskCreate）**: 各 Step を TaskCreate で起こし、Step 完了時に TaskUpdate(completed) を必須化。違反は hook で検知
- **規模感**: 中（SKILL.md に規約マーカーを追加 + hooks 4 本 + subagent 1 個）

### パターン②: harness 提供ツール（AskUserQuestion / WebSearch / Skill / Agent）への直接依存

- **影響項目**: #7, #11
- **どこで起きる**: L3 全部 / L2 の対話パス
- **根本原因**: ハーネス機能を「裏でこっそり使う」のではなく「明示的な接点として活用する」のが本来の設計思想
- **修正方向**:
  - **レバー③（AskUserQuestion 構造化）**: 自由対話を構造化選択肢に変換し、Step 0 / 2.5 / 3 の対話ポイントを SKILL.md で明示。これは **依存を解消するのではなく、依存を構造化する**方向
  - **レバー④（起動経路拡張）**: 本フェーズでは扱わない。チャットUI離脱（cron / SDK / RemoteTrigger）は将来 Phase
- **規模感**: 小（既存 AskUserQuestion 利用を SKILL.md で明示するだけ）

### パターン③: コンテキスト管理を harness 任せ

- **影響項目**: #3, #6, #12
- **どこで起きる**: L3 Orchestrator
- **根本原因**: 状態はファイルに置かれているが「現在何 Step まで終わったか」「どこから resume するか」を構造化して **ハーネスに見えるようにしていない**（LLM が会話履歴で覚える運用）
- **修正方向**:
  - **レバー①（SessionStart hook）**: SessionStart 時に run_id 配下の中間状態（scope.json / data_NN_*.json / merge_order.json の有無）を context に提示
  - **レバー③（TaskCreate）**: 各 Step を TaskCreate で起こし、TaskList が state machine の真実源になる。会話履歴に依存せずに resume 地点が判定できる
- **規模感**: 小（SessionStart hook 1 本 + 規約整備）

### パターン④: 純粋に skill 設計の問題（runtime に関係しない）

- **影響項目**: #2 の `_common/prompts/*.md` 手動コピペ運用 (ISSUE-001 で既知)
- **修正方向**: build_skill.py に @import 機構を入れる (ISSUE-001 D2、トリガー条件未達で保留中)
- **規模感**: 小、かつ既に保留中。本フェーズでは触らない（ただし B-4 で `_common/` に 2 ファイル追加するため、トリガー再評価のタイミングが近づく）

---

## 4. 結論と Phase B への申し送り（改訂版）

### 良いニュース

- **L1 (Python scripts) と L2 (個別PPTX) のスクリプト経路は既に運用上問題なし**。`profiles/claude_code.json` / `profiles/claude_ai.json` で2ランタイムをサポートしており、CLI として直接起動できる
- L3 でも中間ファイル (scope.json / merge_order.json / fact_check_report.json / regeneration_hint) は構造化されており、ハーネスから見える「状態」として既に整っている

### 課題

- **L3 Orchestrator の手順遵守が LLM の自発性任せ**になっている。SKILL.md に「Step N で X を必ずせよ」と書いてあっても、LLM が端折っても検出する機構がない
- 12箇条のうち **#3, #4, #8, #10 の核心問題は L3 に集中**。core 原因は「ハーネス側の強制機構が手薄」

### Phase B 方針（改訂後）

> **撤回**: 当初提案の「Orchestrator を Python class with state machine に書き換え」案は **撤回**。SKILL.md を Python に置き換えると、人間と LLM が同じ手順書を読める利点・git で版管理する軽さ・編集の容易さが失われる。

**新方針**: **SKILL.md は宣言的手順書として残し、Claude Code ハーネス側の機構を skills_factory リポで版管理して LLM の遵守を強制する**。

具体的には 3 レバーで打つ:
- **レバー①** hooks + settings.json + description 精緻化 → SKILL.md の手順を機械的にチェック
- **レバー②** subagent 分割 → 大 orchestrator の context・責務を分割
- **レバー③** AskUserQuestion / TaskCreate 構造化運用 → 対話と進捗を可視化

**移行イメージ**:
```
旧: trigger phrase → LLM reads SKILL.md → LLM が手順を解釈（端折っても検出されない）
新: trigger phrase → LLM reads SKILL.md（変わらず）
    + PreToolUse hook で前提条件 assert
    + 各 Step で TaskCreate / AskUserQuestion を必須化
    + Web 検索フェーズ等を subagent に切り出して context 軽量化
    → SKILL.md の手順遵守がハーネス側で構造的に担保される
```

**最小プロトタイプ案**: `business-deepdive-agent` (462 行 / 6 Step) を最初の適用対象とし、hooks + research-subagent + TaskCreate マーカーが期待通り機能することを確認 → `company-deepdive-agent` / `market-overview-agent` へ展開。

### 詳細は別ドキュメントへ

- 12箇条 × 3レバーの具体マッピング → `outputs/harness_check/lever_mapping.md`（A.5-2 で作成）
- 実装計画とスケジュール → `~/.claude/plans/md-llm-melodic-twilight.md`
