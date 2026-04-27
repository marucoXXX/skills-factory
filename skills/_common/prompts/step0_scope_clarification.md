# Step 0: スコープ確認（共通パターン）

> **このファイルは `skills/_common/prompts/step0_scope_clarification.md` です。**
> オーケストレータースキル（market-overview-agent / strategy-report-agent / smallcap-strategy-research 等）の SKILL.md の Step 0 から、`<!-- source: skills/_common/prompts/step0_scope_clarification.md (manual sync until D2) -->` コメント付きで**手動コピペ**してください。
> このファイルを変更したら `grep -rn "source: skills/_common/prompts/step0_scope_clarification.md" skills/*/SKILL.md` で被参照スキルを全て検出し、コピペし直すこと（ISSUE-001 D2 で自動化検討中）。

調査開始前にユーザーから調査スコープを確定し、`scope.json` として作業ディレクトリに保存する。
スコープを文書化する目的は (1) 後続 Step（Web 検索・データ生成・fill_*.py）で参照する単一の真実源、
(2) 中断・再開時のコンテキスト復元、(3) 最終納品物のメタデータ。

## 共通原則

1. **AskUserQuestion で確定**: スコープに関する質問は対話のテキスト出力ではなく `AskUserQuestion` ツールで聞く。単一選択は `single_select`、複数選択は `multi_select`。
2. **`scope.json` に保存**: 確定したスコープは作業ディレクトリ（`{{WORK_DIR}}/<run_id>/`）の `scope.json` に書き出し、後続 Step は必ずこのファイルを参照する。
3. **`run_id` と `started_at` を必ず含める**: `run_id` は YYYY-MM-DD_<topic> 形式（例: `2026-04-27_taxi_industry`）、`started_at` は ISO 8601 with timezone。
4. **`limits` 範囲外の値は再確認**: 各スキルの `references/deck_skeleton_standard.json` 等で定義された `limits.<param>.{min, max}` の範囲外を選ばれたら、AskUserQuestion で再確認する。デフォルト値（`limits.<param>.default`）はユーザーが明示しない場合に採用する。
5. **`max_competitors` / `kbf_count` 等の共有制約は scope.json で一元管理**: 複数スライド間で一貫させたいパラメータ（例: market-share / positioning-map / competitor-summary / market-kbf で同じ競合数を使う）は scope.json で確定し、各 fill_*.py が読み込む。

## scope.json の最小スキーマ

```json
{
  "topic_name": "国内タクシー市場",
  "run_id": "2026-04-27_taxi_industry",
  "started_at": "2026-04-27T10:00:00+09:00"
}
```

各オーケストレーターは上記に独自フィールドを追加する。例:
- market-overview-agent: `geography`, `segment`, `analysis_years`, `max_competitors`, `kbf_count`
- strategy-report-agent: `report_type`, `deck_depth`, `data_availability_position`
- smallcap-strategy-research: `target_company`, `depth`, `agents`

## オーケストレーター固有の質問項目

各オーケストレーターは本ファイルを継承した上で、自身の SKILL.md に固有の質問テーブル
（`AskUserQuestion` の questions 配列または対応表）を必ず明示すること。質問の **既定値**
は `references/deck_skeleton_standard.json` の `limits.<param>.default` から採るのが望ましい。

## アンチパターン

- ❌ Step 0 を省略して即 Web 検索に入る（後で「全社シェアを揃える」等の制約が破綻する）
- ❌ scope.json を作らず会話メモリだけで進める（中断時に復元不能）
- ❌ `limits` 範囲外の値を黙って受け付ける（fill_*.py が hard-fail する）
- ❌ run_id を秒単位 timestamp で作る（同日複数実行の名前衝突回避が目的なら、トピック名で区別する方が読みやすい）
