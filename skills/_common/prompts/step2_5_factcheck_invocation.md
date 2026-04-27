# Step 2.5: ファクトチェック起動（共通パターン）

> **このファイルは `skills/_common/prompts/step2_5_factcheck_invocation.md` です。**
> オーケストレータースキル（market-overview-agent / strategy-report-agent 等）の SKILL.md の Step 2.5 から、`<!-- source: skills/_common/prompts/step2_5_factcheck_invocation.md (manual sync until D2) -->` コメント付きで**手動コピペ**してください。
> このファイルを変更したら `grep -rn "source: skills/_common/prompts/step2_5_factcheck_invocation.md" skills/*/SKILL.md` で被参照スキルを全て検出し、コピペし直すこと（ISSUE-001 D2 で自動化検討中）。
>
> **smallcap-strategy-research** は Phase 別マルチエージェント構成のため、Step 2.5 を持たない（裏取りは Synthesis Agent の triangulation で代替）。本共通ファイルは適用対象外。

スライド生成に入る前に、Web 取得情報の真偽を `fact-check-reviewer` スキルで再検索ベースに裏取りする。
`fact_check_report.json` で `severity=high` / `medium` のフラグが立った主張は、Step 3 の Markdown
ユーザー確認時に提示し、JSON 修正・出典追加・スキップの 3 択を取る。

## Step 2.5-a: スコープ選択（AskUserQuestion）

| 選択肢 | 内容 | コスト |
|---|---|---|
| **high_risk**（推奨） | 数値・シェア・市場規模・日付・固有名詞のみ検証 | 中（5 カテゴリのみ） |
| **all** | 上記 + テキスト主張も全件検証 | 高（時間がかかる） |
| **skip** | ファクトチェック省略 | ゼロ |

既定は `high_risk`。深度モードや調査タイプによっては `all` を推奨する場合があるが、
原則は `high_risk` でコストを抑え、`severity=high` のみ追加検証で深掘りする。

## Step 2.5-b: fact-check-reviewer 起動

入力:
- `data_dir`: `{{WORK_DIR}}/<run_id>/` （Step 2 で書き出された `data_NN_*.json` 群）
- `scope`: ユーザー選択値（`high_risk` / `all`）
- `target_company`（オプション）: 主要競合の中で最大シェアのプレイヤー名（検索精度向上）

出力: `{{FACTORY_ROOT}}/work/fact-check-reviewer/fact_check_report.json`

## Step 2.5-c: フラグ項目の取り扱い

`fact_check_report.json.flags[]` を以下に分配:

- `severity=high` または `medium` → **Step 3 の Markdown に「要確認項目」セクションとして差し込む**
- 全件 → Step 9（または相当ステップ）で `FactCheck_Report.md` に転記（最終納品物）

`overall_verdict=pass` の場合は Step 3 への差し込みを省略し、末尾に
「ファクトチェック結果: 問題なし」の一文のみ添える。

## アンチパターン

- ❌ Step 2.5 をスキップしてスライド生成に入る（数値の誤りが PPTX に固着する）
- ❌ severity=low のフラグまで Step 3 に差し込む（ユーザーの意思決定をノイズで埋める）
- ❌ `target_company` に対象会社の正式名称ではなく英訳・略称を渡す（検索精度が落ちる）
- ❌ `fact_check_report.json` を最終納品物に同梱しない（裏取り工程の透明性が失われる）
