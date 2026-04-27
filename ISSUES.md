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
