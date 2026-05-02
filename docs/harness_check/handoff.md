# harness_check ブランチ 引き継ぎノート

**作成日**: 2026-05-02 / **作成セッション**: harness_check / md-llm-melodic-twilight

このファイルは `harness_check` ブランチの **次セッション継続のための引き継ぎノート**。Phase B-6 まで完了した状態で、残るは Phase B 検証 (β / γ — 実 E2E) のみ。

---

## 1. 現状サマリー

### ブランチ状態

- **ブランチ**: `harness_check`(main から派生)
- **未マージコミット数**: 9 本
- **作業ディレクトリ**: clean（uncommitted changes 無し前提）
- **install 済**: `~/.claude/skills/business-deepdive-agent` / `company-deepdive-agent` / `market-overview-agent` の 3 本は新規約版に install 済
- **scoped 設定有効**: `.claude/settings.json` がリポ管理されているため、本リポを cwd にしたセッションでは hooks が自動発火する

### コミット一覧（main 派生から）

```
bc292d1 docs(market-overview): Phase B-6 (3/3)
563454d docs(company-deepdive): Phase B-6 (2/3)
fc0bb7b docs(business-deepdive): Phase B-6 prototype
9f62d2a feat(hooks): Phase B-2-d check_task_progression.py 実装
159154e feat(agent): Phase B-3 research-subagent
df7c692 docs(harness): Phase B-4/B-5 規約
de325ca feat(hooks): Phase B-2 hooks 3 本
948d2b8 feat(harness): Phase B-1 .claude/settings.json + スタブ
3cbd079 docs(harness_check): Phase A/A.5 ヒートマップ
```

### Phase 進捗（実装完了 = ✅、未実施 = ⏳）

| Phase | 内容 | 状態 |
|---|---|---|
| A | 12箇条 × 3 層 ヒートマップ | ✅ |
| A.5 | 12箇条 × 3 レバー 打ち手マトリクス | ✅ |
| B-1 | `.claude/settings.json` ひな形 + hooks スタブ | ✅ |
| B-2 | hooks 3 本実装 (merge_order / pptx validate / session context) | ✅ |
| B-2-d | check_task_progression.py 実装（4 本目）| ✅ |
| B-3 | `.claude/agents/research-subagent.md` 試作 | ✅ |
| B-4 | `step_state_tracking.md` 規約 | ✅ |
| B-5 | description / triggers 精緻化規約（B-4 に統合） | ✅ |
| B-6 | 既存 orchestrator 3 本 (business / company / market deepdive) に新規約適用 | ✅ |
| B 検証 α | smoke test + doc 整合性 + 引き継ぎ作成（本コミット）| ✅ |
| **B 検証 β** | **business-deepdive-agent で短時間 E2E 1 本（hooks 発火・task_state.json 実測）** | **⏳ 次セッション** |
| **B 検証 γ** | **market-overview-agent で本格 E2E、context 削減効果 before/after 計測** | **⏳ 次セッション** |
| Phase B 総括 | ISSUES.md / dependency_map.md / lever_mapping.md の最終確定、ISSUE-001 起票判断 | ⏳ |

---

## 2. 次セッションでやるべきこと（β / γ）

### 2-1. Phase B 検証 β（軽い E2E、1〜2 時間）

**目的**: hooks と task_state.json が実 orchestrator 起動時に期待通り動くことを確認。

**手順**:
1. cwd を `/Users/nakamaru/Developer/projects/skills_factory` にして Claude Code を起動（`.claude/settings.json` が有効になる前提）
2. 短い対象会社を選んで起動: 「二幸産業の施設運営事業を business-deepdive-agent で深掘りして」
3. 各 Step で以下を **観察記録**:
   - LLM が `TaskCreate(subject="business-deepdive: Step N - <topic>")` を実際に呼ぶか
   - `{{WORK_DIR}}/company-deepdive-agent/<run_id>/segments/<slug>/task_state.json` がディスクに作成されるか
   - Step 1 で `Agent(subagent_type="research-subagent", ...)` が呼ばれて要約 JSON が返ってくるか
   - Step 4 の `fill_*.py` 実行時に `validate_pptx_after_fill.py` hook が発火するか
4. 期待外動作があれば `docs/harness_check/handoff.md` の Section 5 に追記

**期待**:
- 既存 orchestrator のコア機能（5 PPTX 生成）は破綻しない
- hooks 発火による副作用なし
- task_state.json が steps[] にリアルタイムで append される

**失敗時の挙動**: hooks がブロックを返したら、stderr メッセージに従ってJSON / ファイルを修正して再実行（hooks は backward compat により task_state.json 不在では素通り）

### 2-2. Phase B 検証 γ（本格 E2E、半日以上）

**目的**: market-overview-agent の Step 1 (25-40 件 Web 検索) で **research-subagent 経由による親 context 削減効果** を実測。

**手順**:
1. **Before**(対照): 旧版（subagent 化前のコミット tip 159154e^ あたり）の market-overview-agent で「国内タクシー市場（事業者のみ）」を実行。総 token 数を記録
2. **After**(本実装): 現 tip (bc292d1) で同じ市場を実行。総 token 数を記録
3. **比較**:
   - 親 context に積まれた token 数の差分
   - 最終 PPTX デッキの品質劣化が無いこと
   - 所要時間の差（subagent 起動オーバーヘッド vs context 削減）
4. **記録先**: `outputs/harness_check/e2e_phase_b_verification.md`(新規、commit する場合は docs/ に移動)

**注意**:
- E2E は Web 検索コール 25-40 件 + LibreOffice レンダリング + visual review を含むため、**半日〜1 日** 想定
- 失敗時は `outputs/<run_id>/` 配下を完全保存し、handoff の Section 5 にエラー詳細を残す

### 2-3. Phase B 総括（β / γ 完了後）

1. **ISSUE-001 起票判断**:
   - β / γ で `_common/` 手動コピペの不便さが顕在化したか？
   - していれば D2 (`@import` 機構) を着手 ISSUE として `Status: 進行中検討` に格上げ
   - していなければ「ファイル数増加でも同期漏れ無し」のまま `保留` 継続
2. **`lever_mapping.md` 最終 Status**:
   - 「Phase B 完了時の期待 Status」表を **実測の Status** に書き換え
   - E2E で確認できなかった項目は `🟡 (実装済、E2E未確認)` で残す
3. **PR 作成 (任意)**:
   - 本ブランチを main にマージするなら PR 作成
   - main 側には `99bc374 docs(overview): 主軸 3 + 補助 3 体制への再整理` が独立で入っているため、merge 時に conflict は無い見通し

---

## 3. 重要な前提・注意点

### 3-1. hostname 自動検出の不安定さ（commit 失敗リスク）

セッション中に hostname が `AIZ2026MARUCO` → `Mac` → `AIZ2026MARUCO` のように一時的に変動する事象を確認済（システムアップデート等が原因と推察）。このときに git commit を実行すると `nakamaru@Mac.(none)` を auto-detect して失敗する。

**回避策**:
- **推奨**: 別ターミナルで `git config --global user.email "shunichi.nakamaru@stellar-aiz.com"` と `user.name` を設定。永続的に解消
- 暫定: `git -c user.email=... -c user.name=... commit ...` を inline で
- もし失敗したら: `scutil --get HostName` などで状態確認、`hostname` コマンドが正常値を返していれば retry で通る

CLAUDE.md の規約により私（Claude）は `git config` を変更しない方針なので、ユーザーが明示的に設定しない限り再発する可能性あり。

### 3-2. 一時的なブランチ切替の事象（再発するか不明）

Phase B-4/B-5 のコミット (df7c692) 直後に、**セッション内で意図せず `harness_check` → `main` への checkout が発生**する事象を観測。原因不明。reflog に残っている。データ損失はなし（コミットは harness_check に残った）。

**対処法**: セッション開始時に `git branch --show-current` で確認、`harness_check` でない場合 `git checkout harness_check`。

### 3-3. .claude/settings.json の hooks 自動発火

`.claude/settings.json` がリポにコミットされているため、cwd を本リポに合わせて Claude Code を起動した瞬間から **4 つの hooks が全 Bash 呼び出しに対して発火**する:

- `check_merge_order_exists.py`(PreToolUse) — merge_pptx_v2 でなければ素通り
- `check_task_progression.py`(PreToolUse) — fill_*.py / merge_pptx_v2.py でなければ素通り
- `validate_pptx_after_fill.py`(PostToolUse) — fill_*.py / merge_pptx_v2.py でなければ素通り
- `load_session_context.py`(SessionStart) — 起動時 1 回のみ

**通常は問題ないが**、意図しない exit 2 ブロックを観測した場合:
- stderr ログを Claude のレスポンスに転載してデバッグ
- 緊急時は `.claude/settings.json` の `hooks` セクションを一時的に空 `{}` に書き換えて回避（コミットしない）

### 3-4. business-deepdive-agent / company-deepdive-agent の連動

両者の Step 6 で親→子起動関係。子（business-deepdive）が `task_state.json` を `segments/<slug>/` 配下に持ち、親（company-deepdive）は `step_6` で子の起動・完了のみ記録する規約。**E2E でこの責務分離が実際に機能するか**を β で確認すべき。

---

## 4. 重要ファイルへの参照

### 設計ドキュメント

| ファイル | 役割 |
|---|---|
| `docs/harness_check/dependency_map.md` | 12箇条 × 3 層 ヒートマップ（A.5 で改訂版） |
| `docs/harness_check/lever_mapping.md` | 12箇条 × 3 レバー 打ち手マトリクス + Phase B 期待 Status |
| `docs/harness_check/settings_design.md` | `.claude/settings.json` の設計メモ + 状態表 |
| `docs/harness_check/handoff.md`(本ファイル) | 次セッション引き継ぎ |

### 規約ドキュメント

| ファイル | 役割 |
|---|---|
| `skills/_common/references/harness_levers.md` | 横断ハーネス利用規約（hooks / subagent / TaskCreate / AskUserQuestion 必須地点 / description 規約）|
| `skills/_common/prompts/step_state_tracking.md` | TaskCreate / TaskUpdate / task_state.json スキーマ |
| `tools/hooks/README.md` | hooks 入出力 contract と実装規約 |

### 実装

| ファイル | 役割 |
|---|---|
| `.claude/settings.json` | hooks 配線 + permissions + env |
| `tools/hooks/check_merge_order_exists.py` | PreToolUse: merge_order.json 存在 assert |
| `tools/hooks/check_task_progression.py` | PreToolUse: Step ordering inversion 検出 |
| `tools/hooks/validate_pptx_after_fill.py` | PostToolUse: PPTX 整合性自動検証 |
| `tools/hooks/load_session_context.py` | SessionStart: ISSUES + 直近 plan 注入 |
| `tools/hooks/_test_hooks.py` | 26 ユニットテスト |
| `.claude/agents/research-subagent.md` | Web 検索専用 subagent |

### 既存 orchestrator（B-6 で更新）

| ファイル | 行数 |
|---|---|
| `skills/business-deepdive-agent/SKILL.md` | 539 |
| `skills/company-deepdive-agent/SKILL.md` | 553 |
| `skills/market-overview-agent/SKILL.md` | 881 |

---

## 5. 既知の留意点・観察ログ

セクション 5 は次セッションで追記される。テンプレ:

### 2026-05-XX β E2E 観察

- 対象: `<company / segment>`
- 期待外動作: `<...>`
- 修正/対処: `<...>`

### 2026-05-XX γ E2E 観察

- 対象: `<market>`
- before token 数: `<...>`
- after token 数: `<...>`
- 削減率: `<...%>`
- 品質差分: `<...>`

---

## 6. ISSUE / 保留事項

| ID | 状態 | 関連 |
|---|---|---|
| ISSUE-001 (`@import` 機構) | 保留 / トリガー条件 1 達成 (2026-05-02) | β / γ で同期漏れインシデントが顕在化したら起票判断 |
| 検証 β/γ | 未実施 | 次セッション最優先 |
| commit author 自動検出の不安定さ | 既知の事象 | hostname 一時変動時に再発の可能性、Section 3-1 参照 |
| ブランチ意図せぬ切替 | 既知の事象、原因不明 | Section 3-2 参照 |

---

## 7. 関連 plan ファイル

- `~/.claude/plans/md-llm-melodic-twilight.md` — 元の harness_check 計画書（Phase B-6 まで反映済）
- `~/.claude/plans/<次セッション用>.md` — 本コミットで併せて作成（ファイル名はランダム）
