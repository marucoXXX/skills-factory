# skills_factory プロジェクト懸案管理

このファイルは skills_factory プロジェクトで判断保留した事項・将来検討事項をセッション横断で蓄積するためのものです。

**運用ルール**:
- セッション開始時に必ず本ファイルを読み込み、未解決事項を確認する（プロジェクト直下 CLAUDE.md からも参照）
- 新規イシューは末尾に追記。Status は `保留` / `進行中` / `クローズ` のいずれか
- クローズしたイシューも履歴として残す（削除しない）

---

## ISSUE-001: build_skill.py への `@import` 機構導入

**Status**: 保留 / **Priority**: P3 / **Decided**: 2026-04-27

### 背景
v0.2 Phase D で 3 orchestrator（market-overview-agent / strategy-report-agent / smallcap-strategy-research）の重複ブロックを `skills/_common/` に集約する作業を、**手動コピペ運用（D1）** で開始した。`build_skill.py` への `@import` 自動化（D2）は、今セッション（2026-04-27）で **判断保留** に決定。

### D2 を保留した理由（後で変更しづらい設計判断 5 つ）
1. **パスの基準** — `@import` パスをソースファイル相対 / `skills/` ルート / リポジトリルートのどれを基準に解決するか。最初に決めた基準を後で変えると、既に書いた `@import` 文を全部書き換えになる。
2. **import と {{VAR}} 置換の合成順序** — imported ファイル内の `{{VAR}}` を import 前/後どちらで解決するか。imported ファイル内の `{{VAR}}` が新たな `@import` を生成するケースの可否。
3. **循環インポート検出** — `a → b → a` を検出して停止するロジックの追加。現状の build_skill.py には依存関係追跡機構がない。
4. **キャッシュ無効化** — `_common/*` を変更したとき、被参照スキルを自動再ビルドする仕組み。現状の `build_skill.py install <name>` は単一スキルのみ対象なので、`_common/` 変更時に手動で全部 install しないと反映されない。
5. **エラーメッセージの追跡可能性** — ネスト import で未解決変数が出たときに、どのファイル経由で持ち込まれたかを辿れるか。

### v0.3 で D2 着手するトリガー（どちらかを満たしたら起票）
- `skills/_common/` 配下のファイル数が **8 ファイル以上** に膨らむ
- 手動コピペ運用で **3 回以上の同期漏れインシデント** が発生する

### 参考ファイル
- `tools/build_skill.py`(現状: {{VAR}} 3パス置換 + @if/@endif 実装)
- `skills/_common/`(v0.2 D1 で新設、手動運用)
- `/Users/nakamaru/.claude/plans/4-market-overview-v0.2.md` P3-9 セクション
- `/Users/nakamaru/.claude/plans/fancy-cooking-walrus.md` Phase D1 セクション

---

## ISSUE-002: Web 検索深度の動的制御

**Status**: 保留 / **Priority**: P3 / **Decided**: 2026-04-27

### 背景
v0.1 で「次フェーズで議論」と保留した項目。現状は market-overview-agent / strategy-report-agent で論点別に Web 検索コール数を 5〜8 で固定している。

### 検討内容
fact-check-reviewer の severity が `high` の論点については追加で Web 検索コールを発射する動的拡張を入れるか。コスト・所要時間とのトレードオフをどう設計するか。

### 参考ファイル
- `skills/market-overview-agent/SKILL.md` Step 2 の Web 検索セクション
- `skills/fact-check-reviewer/SKILL.md`
- `/Users/nakamaru/.claude/plans/4-market-overview-v0.2.md` 「v0.2 で扱わないこと」セクション

---

## ISSUE-003: AI による自動 main_message 短縮

**Status**: 保留 / **Priority**: P3 / **Decided**: 2026-04-27

### 背景
v0.2 Phase B で `skills/_common/prompts/main_message_principles.md` を整備し、LLM 出力をルール強制（4 原則）で 65字以内に収める方針を採用。一方で、超過時に AI が自動で短縮するヘルパースキルを別途作る選択肢もある。

### 検討内容
- 現状: ルール強制（プロンプトで 4 原則を厳守させる + fill_*.py 入口で hard-fail）
- 代替: 短縮専用の補助スキル（main_message を入力 → 65字以内の候補を 3 案返す）
- どちらが運用負荷が低いか、LLM 呼び出しコストとの兼ね合いで再検討

### 参考ファイル
- `skills/_common/prompts/main_message_principles.md`(v0.2 Phase B で作成予定)
- `/Users/nakamaru/.claude/plans/4-market-overview-v0.2.md` 「v0.2 で扱わないこと」セクション

---

## ISSUE-004: Company Overview Agent の設計

**Status**: 保留 / **Priority**: P2 / **Decided**: 2026-04-27

### 背景
v0.2 完了後、`skills/_common/` が整備された状態で Company Overview Agent を薄く実装可能になる。`strategy-report-agent v5.1` を Company Overview Agent としてリネーム/再定義するアプローチが有力。

### 検討内容
- 既存 `strategy-report-agent` を改名するか、新規スキルとして並走させるか
- 上場企業（有報あり）と非上場企業（smallcap-strategy-research）の境界をどう設計するか

### 参考ファイル
- `skills/strategy-report-agent/SKILL.md`
- `/Users/nakamaru/.claude/plans/5-company-overview.md`(別途計画ファイル予定)

---

## ISSUE-005: 市場スコープの事業モデル境界確認（Phase F 主タスク）

**Status**: 進行中（F-1〜F-4 完了 / F-5 E2E 未実施） / **Priority**: P1 / **Decided**: 2026-04-27 / **Updated**: 2026-04-28

### 背景
v0.2 Phase E（国内タクシー市場 E2E）で、handoff の想定プレイヤー欄に従い「タクシー事業者（5社）」と「配車アプリ事業者（4社）」を混在させてレポート化したところ、ユーザーから「タクシー事業者の市場を見たかった、アプリは除外」との指摘を受けた。シェア表で第一交通産業 4.7% と GO 1.2% を同列に並べる構図は、収益構造（営業収入 vs 配車手数料）が異なるため誤解を招く。

現状の `market-overview-agent` Step 0 は地理スコープ・セグメント粒度・分析年数・max_competitors・kbf_count のみを聞き、**同一業界内の異なる事業モデルを含めるかの確認質問が存在しない**。

### 採用アプローチ（B+C ハイブリッド、ユーザー承認済 2026-04-27）

**B**: Step 0.5（事前スコーピング Web 検索）追加
- `market_name` 確定後 Step 1 の前に「市場構造ザックリ把握」用 Web 検索 1-2 件を走らせ、事業モデルの heterogeneity を検知したらユーザーに再確認

**C**: `scope.json` schema 拡張
- `included_business_models[]` / `excluded_segments[]` を必須フィールドとして追加
- `step0_scope_clarification.md` に必須質問を追加し永続化
- 後続スライドはこの境界を尊重する責務をオーケストレーターに置く

### Phase F 実装タスク
1. ✅ `step0_scope_clarification.md` に Step 0.5 節 + 新フィールド追加（2026-04-28 完了）
2. ✅ `market-overview-agent/SKILL.md` Step 0 を更新（2026-04-28 完了）
3. ✅ `strategy-report-agent/SKILL.md` Step 0 を同様更新（2026-04-28 完了）
4. ✅ `smallcap-strategy-research/SKILL.md` には適用範囲注記のみ追加（2026-04-28 完了）
5. ✅ `orchestrator_contract.md` にセクション 4「scope.json の責務分担」追記、チェックリストに 4 項目追加（2026-04-28 完了）
6. ⏳ E2E リラン（国内タクシー市場・事業者のみ 5 社）でシェア表が事業者ベースで構成されることを確認 → **次セッションへ繰越**

### 参考ファイル
- `skills/_common/prompts/step0_scope_clarification.md`
- `skills/market-overview-agent/SKILL.md` Step 0
- `skills/_common/references/orchestrator_contract.md`
- 関連 memory: `feedback_market_scope_business_model_boundary.md`

---

## ISSUE-006: render_pptx.py CLI と SKILL.md の引数不整合

**Status**: 保留 / **Priority**: P2 / **Decided**: 2026-04-27

### 背景
v0.2 Phase E E2E で `visual-quality-reviewer/scripts/render_pptx.py` を起動した際、SKILL.md の説明（`--merge-order` / `--data-dir` を受ける）と実際の CLI（`--pptx --out-dir --dpi` のみ）が一致しないことが判明。

### 検討事項
- SKILL.md と実装のどちらを正とするか
- 自動修正ループ（visual-quality-reviewer が下流で merge_order / data_dir を読む）の実現可否

### 修正方針候補
- (a) `render_pptx.py` に `--merge-order` / `--data-dir` を追加し、`context.json` を別途出力する
- (b) SKILL.md を `--pptx --out-dir` のみ受ける仕様に修正し、merge_order/data_dir はオーケストレーターが LLM 経由で渡す運用とする

### 参考ファイル
- `skills/visual-quality-reviewer/scripts/render_pptx.py`
- `skills/visual-quality-reviewer/SKILL.md`

---

## ISSUE-007: market-environment-pptx の bars/line Y軸スケール乖離

**Status**: 保留 / **Priority**: P3 / **Decided**: 2026-04-27

### 背景
v0.2 Phase E E2E のスライド 4（市場規模推移）で、棒グラフ（営業収入 1.45-1.93兆円）と折れ線（2019年比回復率 75-99%）が同じ Y 軸を共有するため、棒の差分が視認しづらい。Y軸 0-120 で線は明瞭だが棒は底辺に張り付く。

### 検討事項
- データ単位を 兆円→千億円 に変換（推奨、データ側で対応可能）
- テンプレート側で dual-axis（左軸=兆円、右軸=%）対応を入れるか
- `unit_label` / `total_label` の自動推奨ロジックを fill_market_environment.py に入れるか

### 参考ファイル
- `skills/market-environment-pptx/scripts/fill_market_environment.py`
- `skills/market-environment-pptx/assets/market-environment-template.pptx`

---

## ISSUE-008: competitor-summary 30字 cell 制限が 9 列構成で厳しい

**Status**: 保留 / **Priority**: P3 / **Decided**: 2026-04-27

### 背景
v0.2 Phase A で `max_competitors` を 5→10 に拡張した結果、9 列構成（target+8）でフォントが 9pt まで自動縮小されるが、`事業内容` / `強み・差別化` の cell 30字制限が運用上厳しい。E2E で「タクシー配車アプリ（DiDi Global＋ソフトバンク合弁）」（31字）等が hard-fail で何度も書き直しが発生。

### 検討事項
- cell 制限を競合数に応じて動的化（5社=40字、8-10社=30字 等）
- フォント自動縮小と cell 文字数の連動を見直し
- 事業内容と強み・差別化を改行可とし 2 段表示にする

### 参考ファイル
- `skills/competitor-summary-pptx/scripts/fill_competitor_summary.py`
- `skills/competitor-summary-pptx/SKILL.md`
