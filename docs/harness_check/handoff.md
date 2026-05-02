# harness_check ブランチ 引き継ぎノート

**作成日**: 2026-05-02 / **更新日**: 2026-05-02（β E2E 完了後）

このファイルは `harness_check` ブランチの **次セッション継続のための引き継ぎノート**。Phase B-6 + β 検証 完了状態で、残るは **γ E2E + 総括** のみ。

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
| B 検証 α | smoke test + doc 整合性 + 引き継ぎ作成 | ✅ |
| B 検証 β | business-deepdive-agent で短時間 E2E（二幸産業 × 施設運営事業）、hooks 発火・task_state.json・subagent 動作実測 | ✅ (2026-05-02) |
| **B 検証 γ** | **market-overview-agent で本格 E2E、context 削減効果 before/after 計測** | **⏳ 次セッション** |
| Phase B 総括 | ISSUES.md / dependency_map.md / lever_mapping.md の最終確定、ISSUE-001 起票判断、β で発見した subagent return value 説明文混入 ISSUE の処理 | ⏳ γ 完了後 |

---

## 2. 次セッションでやるべきこと（γ + 総括）

### 2-1. Phase B 検証 β — **完了 (2026-05-02)**

business-deepdive-agent / 二幸産業 × 施設運営事業 で実施。

- 10 観察ポイントすべて ✅（TaskCreate / task_state.json / AskUserQuestion / 並列 + 順次 subagent / validate hook / 整合性ルール 等）
- 5 PPTX 生成成功（59-378KB）、所要時間 約 20 分
- Phase 3 で発生していた「論点 5 = ビルメンテ市場（自社市場）」の混同は構造的に防止できた
- 期待外動作 1 件: subagent return value に説明文混入（Section 5 / Section 6 に ISSUE 候補として記録、γ で再現性を観察）

詳細は Section 5「2026-05-02 β E2E 観察」参照。成果物は `work/business-deepdive-agent/company-deepdive-agent/2026-05-02_nikoo-sangyo/segments/facility-management/` に保存。

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

### 2026-05-02 β E2E 観察（business-deepdive-agent 単独起動）

- **対象**: 二幸産業株式会社 / 施設運営事業
- **所要時間**: 約 20 分（Step 0〜6 の単独起動）
- **作業ディレクトリ**: `work/business-deepdive-agent/company-deepdive-agent/2026-05-02_nikoo-sangyo/segments/facility-management/`

#### 観察結果（期待 vs 実態）

| 観察ポイント | 期待挙動 | 実態 | 判定 |
|---|---|---|---|
| TaskCreate / TaskUpdate 発火 | 各 Step で開始/完了マーカーを呼ぶ | Step 0-6 すべて呼べた（task_id 1-7） | ✅ |
| task_state.json 生成・更新 | ディスクに作成 → steps[] に append → 最終化 | 期待通り。Step ごとに started_at / completed_at を記録 | ✅ |
| AskUserQuestion 発火 | Step 0（単独起動の対話）/ Step 3（5 論点承認）| 両方で対話成立、Step 3 で整合性確認表も提示 | ✅ |
| research-subagent 並列起動 | 論点 1-3 を Agent ツール経由で並列 | 3 並列で起動成功、最大 83 秒で完了。生 HTML は親 context に流入せず | ✅ |
| research-subagent 順序起動 | 論点 4 → customer_industry 確定 → 論点 5 | 期待通り。`customer_industry` = 不動産業 を確定して論点 5 へ | ✅ |
| validate_pptx_after_fill hook | 5 fill_*.py 後に PPTX 整合性検証 | 5 回とも exit 2 ブロックなし = PASS | ✅ |
| check_task_progression hook | step ordering inversion 検出 | 順序通り走行のため発動せず（素通り） | ✅ |
| check_merge_order_exists hook | merge_pptx_v2 直前に merge_order.json 検証 | 単独起動で merge せずなので発動せず（素通り） | ✅ |
| 5 PPTX 生成 | 各 fill_*.py が 0-exit で PPTX を出力 | 5 PPTX 生成成功（59-378KB） | ✅ |
| 論点間整合性ルール | 主語 / 顧客業種 / 自社業界の 3 項目チェック | Step 3 で 3 項目すべて ✅、Phase 3 の混同を構造的に防止 | ✅ |

#### 期待外動作

- **research-subagent の return value に説明文が付いた**: 5 つの subagent すべてで「Based on my comprehensive web research...」「Sources: ...」のような前後文章が付加され、純粋な JSON 単体ではなくマークダウン化された JSON ブロックが返却された。`research-subagent.md` のアンチパターン「親への返却 message に説明文を付ける」に該当。`json.loads(result)` は失敗するため、親側で JSON ブロック抽出が必要。今回は LLM が手動で JSON 部分を context から拾って Write したため進行は妨げられず、本流の β 検証は完遂。
- **修正候補**: (a) `research-subagent.md` の制約をより強い言葉に書き換える、(b) 親オーケストレータ側に JSON 抽出 helper（例: regex で ```json ... ``` ブロックを取り出す）を持たせる、(c) subagent の最後の指示に「JSON テキスト以外は一切出力しないこと」を verbatim で繰り返す。次セッション以降で要検討（γ E2E でも同様の事象が起きる可能性高い）。

#### Phase 3 混同問題の防止確認

Phase 3 で発生した「論点 5 に自社市場（ビルメンテ市場）を入れる混同」は今回構造的に防止できた:

- Step 1 で論点 4 → 5 を逐次起動 → `customer_industry` = 不動産業 を確定
- Step 3 整合性確認表で 3 項目すべて ✅
- 論点 5 の subagent 起動時に `parent_context.industry` = 不動産業（商業用不動産）を渡し、`scope_constraints.excluded_segments` に「ビルメンテナンス業（自社の事業市場、論点 5 の対象外）」を明示
- 結果、論点 5 = 商業用不動産市場（収益不動産 275.5→315.1 兆円、CAGR +6.9%）で正しく取得

規約（`skills/_common/prompts/cross_topic_consistency_check.md` 相当 / business-deepdive SKILL.md の「論点間整合性ルール」）の効果を実証。

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
| 検証 β | **完了 (2026-05-02)** | Section 5 観察ログ参照、Phase B 規約は本流で機能 |
| 検証 γ | 未実施 | 次セッション、market-overview-agent で context 削減効果を実測 |
| ISSUE 候補（β で発見）: subagent return value に説明文混入 | 起票候補 | Section 5「期待外動作」参照。`research-subagent.md` 制約強化 or 親側 JSON 抽出 helper を要検討 |
| commit author 自動検出の不安定さ | 既知の事象 | hostname 一時変動時に再発の可能性、Section 3-1 参照 |
| ブランチ意図せぬ切替 | 既知の事象、原因不明 | Section 3-2 参照 |

---

## 7. 関連 plan ファイル

- `~/.claude/plans/md-llm-melodic-twilight.md` — 元の harness_check 計画書（Phase B-6 まで反映済）
- `~/.claude/plans/harness-check-verification-next-session.md` — β / γ 検証の最初の plan（β 完了で役目を終え、γ 部分のみ参照価値）
- `~/.claude/plans/harness-check-gamma-and-closure.md` — **次セッション用（γ E2E + 総括）**。本セッションで作成
