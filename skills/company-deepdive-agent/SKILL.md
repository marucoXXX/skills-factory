---
name: company-deepdive-agent
description: >
  対象会社 1 社を「会社レベル + 全事業セグメント」の両軸で深掘り調査し、
  1 つの結合済み PowerPoint デッキを生成するオーケストレータースキル。
  本スキル自体はスクリプトを持たず、Web 検索と複数の既存スキル
  （customer-profile / company-history / business-portfolio / revenue-analysis /
   financial-benchmark / shareholder-structure 等）+ business-deepdive-agent を
  呼び出してデッキ全体を組み立てる役割に特化する。

  market-overview-agent でプレイヤーリストが確定した後、A 社・B 社・C 社と
  繰り返し起動して各社の戦略が透けて見える深さの調査を行う用途。
  上場・非上場問わず公開情報から取れる範囲で作成し、取れなかった項目は
  data-availability-pptx で「✗未取得」と明示する設計。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - 「○○社の深掘り」「○○社のコーポレート分析」「会社の戦略を透視」という言葉が出た場合
  - 「対象会社 1 社を深く調べて」「マーケットの中で○○社を分析して」という要望
  - market-overview-agent でプレイヤー特定後、各社の深掘りに進む場合
  - 複数社を横並び比較する前段として、各社個別のデッキを作る場合
---

# 会社深掘りオーケストレーター

ISSUE-004（v0.3）における新規オーケストレーター。`market-overview-agent` の下流で各社ドリルダウン、
`comparison-synthesis-agent` の上流で各社個別デッキを作る位置付け。

## 設計原則

- **会社レベル 5 論点 + 事業セグメント単位 5 論点 × N 事業** を 1 つの結合デッキに集約
- 上場・非上場問わず、**取れる公開情報から最大限作成**
- 取れなかった項目は `data-availability-pptx` で「✗未取得」明示（smallcap の三角測量は使わない、シンプルに公開情報をそのまま記述）
- セグメント検出は本スキルの責務（`business-deepdive-agent` への引き渡しは本スキル経由）
- merge-pptxv2 / visual-quality-reviewer / fact-check-reviewer の呼び出しも本スキル責務（business-deepdive-agent は個別 PPTX のみ返却）

---

## 会社レベル 5 論点 → PPTX マッピング

| # | 論点 | PPTX スキル |
|---|---|---|
| 1 | 会社の概要は？ | `customer-profile-pptx` または `company-overview-pptx-v2` |
| 2 | 会社の沿革は？ | `company-history-pptx` |
| 3 | 事業ポートフォリオは？ | `business-portfolio-pptx` |
| 4 | 会社としての収益性は？ | `revenue-analysis-pptx` + `financial-benchmark-pptx`（**2 枚**） |
| 5 | 株主・役員は？ | `shareholder-structure-pptx` |

---

## デッキ構成（標準版、N=セグメント数）

```
[Section 1] 会社レベル
01 エグゼクティブサマリー (executive-summary-pptx)
02 目次 (table-of-contents-pptx)
03 会社プロファイル (customer-profile-pptx or company-overview-pptx-v2)
04 会社の沿革 (company-history-pptx)
05 事業ポートフォリオ (business-portfolio-pptx)
06 収益性推移 (revenue-analysis-pptx)
07 業界内財務ベンチマーク (financial-benchmark-pptx)
08 株主・役員構成 (shareholder-structure-pptx)

[Section 2..N+1] 各事業セグメント深掘り（business-deepdive-agent から委譲）
09 (中扉) ○○事業 1 (section-divider-pptx)
10..14 ○○事業 1 の 5 論点 (business-deepdive-agent 経由)
15 (中扉) ○○事業 2
16..20 ○○事業 2 の 5 論点
...

[末尾]
末 データアベイラビリティ (data-availability-pptx)
```

スライド総数の目安: 8（会社レベル）+ (1+5)×N（事業数）+ 1（data avail）= **9 + 6N 枚**。

| N | 標準デッキ枚数 |
|---|---|
| 1 | 15 枚 |
| 2 | 21 枚 |
| 3 | 27 枚 |
| 4 | 33 枚 |

---

## Step 構造

### Step 0: 対象会社・出力先確認

`AskUserQuestion` で以下を確定:

| 質問 | 選択肢 |
|---|---|
| 対象会社の正式名称 | テキスト入力 |
| 対象会社の業種・主力事業 | テキスト入力（任意、検索精度向上用） |
| 競合社（financial-benchmark 用） | 5 社程度をユーザーが提示 or オーケストレーターが提案 |
| 分析年数 | 5 / 7（推奨）/ 10 年 |
| 深掘りセグメント | A. 全セグメント / B. ユーザー指定（事業名）/ C. 会社レベルのみ |
| デッキ深度 | 簡易（中扉なし）/ 標準（推奨、9+6N 枚）/ 拡張（全社 PEST/SWOT 追加） |

`run_id` は `YYYY-MM-DD_<company_slug>` 形式で自動生成。
`{{WORK_DIR}}/company-deepdive-agent/<run_id>/` を作業ディレクトリ。
`{{WORK_DIR}}/company-deepdive-agent/<run_id>/scope.json` に Step 0 の確定値を保存。

### Step 0.5: 同名異社の確認（任意）

検索結果に複数の同名企業がある場合、ユーザーに正式名称・本社所在地・上場区分で確認。
（market-overview-agent の Step 0.5 とは別の問題で、ここでは事業モデル境界ではなく企業特定が論点）

### Step 1: Web 検索による会社レベル 5 論点の情報収集

`prompts/step1_research_template.md` のクエリテンプレートに `{company_name}` / `{industry}` / `{competitors[]}` を展開し、5 論点それぞれ **5-8 件** WebSearch を実行。

| 論点 | 優先ソース |
|---|---|
| 会社の概要 | 公式 HP / 会社案内 / 有報冒頭（上場の場合） |
| 沿革 | 公式 HP / 統合報告書 / Wikipedia（一次ソース確認必須） |
| 事業ポートフォリオ | 有報「事業の状況」/ 決算短信セグメント情報 / HP「事業内容」 |
| 収益性 | 有報・決算短信・SPEEDA / EDINET / 競合社の同種データ |
| 株主・役員 | 有報「株主構成」「役員構成」/ 統合報告書 / 会社案内 |

**非上場の場合**は公式 HP・プレスリリース・業界誌・FUMA・Baseconnect・帝国データバンク・官報決算公告で埋められる範囲のみ取得。

### Step 2: データアベイラビリティ整理

`{{WORK_DIR}}/company-deepdive-agent/<run_id>/data_15_data_availability.json` に集計。
`status` は `obtained` / `partial` / `missing` の 3 値。事業セグメント分（business-deepdive-agent の `segment_data_availability.json`）も統合する。

### Step 2.5: ファクトチェック（推奨実施）

`fact-check-reviewer` を呼ぶ。下記の共通パターンに従う。

<!-- source: skills/_common/prompts/step2_5_factcheck_invocation.md (manual sync until D2) -->

スライド生成に入る前に、Web 取得情報の真偽を `fact-check-reviewer` スキルで再検索ベースに裏取りする。
`fact_check_report.json` で `severity=high` / `medium` のフラグが立った主張は、Step 3 の Markdown
ユーザー確認時に提示し、JSON 修正・出典追加・スキップの 3 択を取る。

#### Step 2.5-a: スコープ選択（AskUserQuestion）

| 選択肢 | 内容 | コスト |
|---|---|---|
| **high_risk**（推奨） | 数値・シェア・市場規模・日付・固有名詞のみ検証 | 中（5 カテゴリのみ） |
| **all** | 上記 + テキスト主張も全件検証 | 高（時間がかかる） |
| **skip** | ファクトチェック省略 | ゼロ |

既定は `high_risk`。

#### Step 2.5-b: fact-check-reviewer 起動

入力:
- `data_dir`: `{{WORK_DIR}}/company-deepdive-agent/<run_id>/`（Step 2 で書き出された会社レベル `data_NN_*.json` 群）
- `scope`: ユーザー選択値（`high_risk` / `all`）
- `target_company`: 対象会社の正式名称

<!-- @if:claude_code -->
出力: `{{FACTORY_ROOT}}/work/fact-check-reviewer/fact_check_report.json`
<!-- @endif -->

#### Step 2.5-c: フラグ項目の取り扱い

`fact_check_report.json.flags[]` を以下に分配:
- `severity=high` または `medium` → Step 3 の Markdown に「要確認項目」セクションとして差し込む
- 全件 → Step 8 で `FactCheck_Report.md` に転記（最終納品物）

`overall_verdict=pass` の場合は Step 3 への差し込みを省略し、末尾に「ファクトチェック結果: 問題なし」の一文のみ添える。

### Step 3: ユーザーに会社レベル情報を Markdown で提示・承認

会社レベル 5 論点と検証論点（fact-check 結果）を統合した Markdown をユーザーに提示し、修正・承認を得る。

### Step 4: 会社レベル Key Findings + 検証論点整理

`executive-summary-pptx` 用に Key Findings 3-5 個を整理。会社レベル + 各セグメントの戦略的論点を統合。

### Step 5: 会社レベル PPTX 生成

各論点を対応 PPTX スキル（上記マッピング）の `fill_*.py` で生成。

| Slide | スキル | data ファイル | output ファイル |
|---|---|---|---|
| 01 | executive-summary-pptx | `data_01_exec_summary.json` | `slide_01_exec_summary.pptx` |
| 02 | table-of-contents-pptx | `data_02_toc.json` | `slide_02_toc.pptx` |
| 03 | customer-profile-pptx OR company-overview-pptx-v2 | `data_03_company_profile.json` | `slide_03_company_profile.pptx` |
| 04 | company-history-pptx | `data_04_company_history.json` | `slide_04_company_history.pptx` |
| 05 | business-portfolio-pptx | `data_05_business_portfolio.json` | `slide_05_business_portfolio.pptx` |
| 06 | revenue-analysis-pptx | `data_06_revenue_analysis.json` | `slide_06_revenue_analysis.pptx` |
| 07 | financial-benchmark-pptx | `data_07_financial_benchmark.json` | `slide_07_financial_benchmark.pptx` |
| 08 | shareholder-structure-pptx | `data_08_shareholder_structure.json` | `slide_08_shareholder_structure.pptx` |

### Step 6: セグメント検出 + business-deepdive-agent を起動

Step 5 で生成した `business-portfolio-pptx` の入力データから報告セグメント一覧を抽出。
複数事業の場合は Step 0 で確定した深掘りセグメント（A. 全 / B. ユーザー指定 / C. なし）に従い、対象セグメントごとに `business-deepdive-agent` を起動。

`business-deepdive-agent` への引数（JSON で渡す）:
```json
{
  "parent_company_name": "<対象会社名>",
  "segment_name": "<セグメント名>",
  "segment_slug": "<ASCII slug、例: facilities, taxi, real_estate>",
  "parent_run_id": "<run_id>",
  "global_slide_offset": 9,
  "is_listed": <bool>,
  "industry": "<業種>",
  "analysis_years": 7
}
```

`global_slide_offset` は会社レベルブロック（中扉込み）の枚数 = 9（会社 8 枚 + 中扉 1 枚）。
2 セグメント目以降は `+ 6` ずつ加算（中扉 1 + 5 論点）。

`business-deepdive-agent` は各セグメント別 subdir に 5 PPTX を書き出す:
```
{{WORK_DIR}}/company-deepdive-agent/<run_id>/segments/<segment_slug>/
├── data_<NN+1>..data_<NN+5>_*.json
├── slide_<NN+1>..slide_<NN+5>_*.pptx
├── segment_data_availability.json
└── segment_summary.json
```

並列起動可（複数セグメントを並列で深掘り、終了を待つ）。

#### Phase 3 で既に生成済の `business-deepdive-agent` 出力を流用する場合

既に `business-deepdive-agent` で生成済の `slide_01..05_*.pptx`（暫定番号）が `segments/<slug>/` にある場合、再起動は不要。`global_slide_offset` 加算後の通し番号で**コピー & リネーム** し、merge_order.json に組み込む:

```bash
# 例: Phase 3 出力 slide_01..05 を会社レベル 8 枚 + 中扉 1 枚の後ろ（slide_10..14）にリネーム
SEG_DIR=$WORK_DIR/segments/<slug>
cp $SEG_DIR/slide_01_business_overview.pptx $SEG_DIR/slide_10_business_overview.pptx
cp $SEG_DIR/slide_02_business_model.pptx $SEG_DIR/slide_11_business_model.pptx
# ...etc
```

### Step 7: 中扉 + data-availability + merge_order.json 構築

中扉スライド（各セグメント冒頭）を `section-divider-pptx` で生成し、最終 data-availability スライドを `data-availability-pptx` で生成。

`merge_order.json` を `{{WORK_DIR}}/company-deepdive-agent/<run_id>/merge_order.json` に書き出す。
スキーマは下記の `orchestrator_contract.md` 規約に準拠。

<!-- source: skills/_common/references/orchestrator_contract.md (manual sync until D2) -->

`merge_order.json` のスキーマ:

```json
{
  "entries": [
    {
      "slide_number": 1,
      "file_name": "slide_01_exec_summary.pptx",
      "skill_name": "executive-summary-pptx",
      "data_file": "data_01_exec_summary.json",
      "category": "header"
    }
  ]
}
```

`category` の値域: `header` / `content` / `section_divider` / `footer`。

検証ルール（merge-pptxv2 が assert）:
- `category=section_divider` の **直後** のエントリは `category=content` でなければならない
- 違反は `merge_warnings.json` に記録、マージは継続

#### 標準版 15 枚（@N=1）の merge_order.json サンプル

```json
{
  "entries": [
    {"slide_number": 1, "file_name": "slide_01_exec_summary.pptx", "skill_name": "executive-summary-pptx", "data_file": "data_01_exec_summary.json", "category": "header"},
    {"slide_number": 2, "file_name": "slide_02_toc.pptx", "skill_name": "table-of-contents-pptx", "data_file": "data_02_toc.json", "category": "header"},
    {"slide_number": 3, "file_name": "slide_03_company_profile.pptx", "skill_name": "customer-profile-pptx", "data_file": "data_03_company_profile.json", "category": "content"},
    {"slide_number": 4, "file_name": "slide_04_company_history.pptx", "skill_name": "company-history-pptx", "data_file": "data_04_company_history.json", "category": "content"},
    {"slide_number": 5, "file_name": "slide_05_business_portfolio.pptx", "skill_name": "business-portfolio-pptx", "data_file": "data_05_business_portfolio.json", "category": "content"},
    {"slide_number": 6, "file_name": "slide_06_revenue_analysis.pptx", "skill_name": "revenue-analysis-pptx", "data_file": "data_06_revenue_analysis.json", "category": "content"},
    {"slide_number": 7, "file_name": "slide_07_financial_benchmark.pptx", "skill_name": "financial-benchmark-pptx", "data_file": "data_07_financial_benchmark.json", "category": "content"},
    {"slide_number": 8, "file_name": "slide_08_shareholder_structure.pptx", "skill_name": "shareholder-structure-pptx", "data_file": "data_08_shareholder_structure.json", "category": "content"},
    {"slide_number": 9, "file_name": "slide_09_section_divider.pptx", "skill_name": "section-divider-pptx", "data_file": "data_09_section_divider.json", "category": "section_divider"},
    {"slide_number": 10, "file_name": "segments/<slug>/slide_10_business_overview.pptx", "skill_name": "business-overview-pptx", "data_file": "segments/<slug>/data_01_business_overview.json", "category": "content"},
    {"slide_number": 11, "file_name": "segments/<slug>/slide_11_business_model.pptx", "skill_name": "business-model-pptx", "data_file": "segments/<slug>/data_02_business_model.json", "category": "content"},
    {"slide_number": 12, "file_name": "segments/<slug>/slide_12_value_chain_matrix.pptx", "skill_name": "value-chain-matrix-pptx", "data_file": "segments/<slug>/data_03_value_chain_matrix.json", "category": "content"},
    {"slide_number": 13, "file_name": "segments/<slug>/slide_13_customer_profile.pptx", "skill_name": "customer-profile-pptx", "data_file": "segments/<slug>/data_04_customer_profile.json", "category": "content"},
    {"slide_number": 14, "file_name": "segments/<slug>/slide_14_market_environment.pptx", "skill_name": "market-environment-pptx", "data_file": "segments/<slug>/data_05_market_environment.json", "category": "content"},
    {"slide_number": 15, "file_name": "slide_15_data_availability.pptx", "skill_name": "data-availability-pptx", "data_file": "data_15_data_availability.json", "category": "footer"}
  ]
}
```

### Step 8: merge-pptxv2 で結合

```bash
python3 ~/.claude/skills/merge-pptxv2/scripts/merge_pptx_v2.py \
  outputs/<run_id>/CompanyDeepDive_<会社名>_<date>.pptx \
  --merge-order {{WORK_DIR}}/company-deepdive-agent/<run_id>/merge_order.json \
  <slide_01.pptx> <slide_02.pptx> ... <slide_NN.pptx>
```

完了後、`{{OUTPUT_DIR}}/<run_id>/merge_warnings.json` を確認（`section_divider_position` 違反 0 件であること）。

### Step 9: visual-quality-reviewer + 自動修正ループ（最大 2 ラウンド）

下記の共通パターンに従う。

<!-- source: skills/_common/prompts/step_final_visual_review_loop.md (manual sync until D2) -->

`merge-pptxv2` 完了後、`visual-quality-reviewer` を呼び出してデッキ全体をページ画像化 → 目視レビューする。
文字溢れ・要素重なり・配色崩れ等の `severity=high` issue が残ると最終納品の品質に直結するため、
最大 2 ラウンドの自動修正ループで `severity=high` を 0 件まで下げる。

#### 起動

入力:
- `merged_pptx`: `{{OUTPUT_DIR}}/<run_id>/CompanyDeepDive_<会社名>_<date>.pptx`
- `merge_order`: `{{WORK_DIR}}/company-deepdive-agent/<run_id>/merge_order.json`
- `data_dir`: `{{WORK_DIR}}/company-deepdive-agent/<run_id>/`

<!-- @if:claude_code -->
出力: `{{FACTORY_ROOT}}/work/visual-quality-reviewer/visual_review_report.json`
<!-- @endif -->

#### レビュー結果の分岐

| `overall_verdict` | 処理 |
|---|---|
| `pass` | 終了。完成デッキをユーザーに提示 |
| `needs_fixes` かつ `severity=high` ≥ 1 件 | 自動修正ループへ |
| `needs_fixes` かつ `severity=high` = 0 件 | ユーザーに差分レポート提示、手動修正 or 許容を選ばせる |
| `reject` | LibreOffice レンダリング失敗を疑いユーザーに報告して停止 |

#### 自動修正ループ（最大 2 ラウンド）

`severity=high` の各 issue について:
1. `issues[i].skill_name` と `issues[i].data_file` から、該当スライド生成に使った JSON を特定
2. `issues[i].regeneration_hint` に従って `data_NN_*.json` を修正
3. 該当スキルの `fill_*.py` を**同じ `slide_NN_*.pptx` ファイル名で再実行** → 既存スライドを上書き
4. 全修正完了後、`merge-pptxv2 --merge-order` を再実行
5. 再度 `visual-quality-reviewer` を起動

**2 ラウンド終了時点で `severity=high` が残存する場合**: ユーザーに残存 issue を提示し、手動修正か許容の判断を仰ぐ。

### Step 10: ユーザーへ最終納品

- `outputs/<run_id>/CompanyDeepDive_<会社名>_<date>.pptx`（結合デッキ、N=1 なら 15 枚）
- `outputs/<run_id>/FactCheck_Report.md`（fact-check 全件レポート、Step 2.5 の最終出力）
- `outputs/<run_id>/merge_warnings.json`（section_divider 検証ログ）

---

## main_message 共通ルール（全 PPTX 横断、厳守）

<!-- source: skills/_common/prompts/main_message_principles.md (manual sync until D2) -->

### ルール1: 長さは **65 文字以内**（厳格）

- 句読点・記号・スペースを含めて 65 文字以内
- 65 文字を 1 字でも超えた状態で `fill_*.py` に渡すと ValueError で hard-fail する

### ルール2: トーンは **事実記述ベース**（「〜すべき」禁止）

- 公開情報のみで断定できないアクションや戦略示唆は書かない
- 不明な点は「〜は公開情報からは確定できず追加調査が必要」と率直に書く

### 65 字オーバー時の短縮原則 4 つ

1. **主語は 1 つだけ** — 「市場は」「対象会社は」のいずれか 1 つに絞る
2. **修飾語を削除** — 「主要な」「重要な」「大きな」「急速な」等を落とす
3. **数値は 1 つだけ残す** — CAGR と シェアを両方載せず、より重要な 1 つを選ぶ
4. **結論を述べる、根拠は本文スライドに任せる**

注: 個別 PPTX スキル SKILL.md は「〜すべきで締める / 70 字」と書かれているものもあるが、本オーケストレーターから呼ぶ場合は **本ルールで上書き**（65 字・事実記述）。

---

## scope.json（本オーケストレータ内部、`orchestrator_contract.md` 準拠）

`{{WORK_DIR}}/company-deepdive-agent/<run_id>/scope.json`:

```json
{
  "company_name": "二幸産業株式会社",
  "company_aliases": ["二幸産業"],
  "is_listed": false,
  "ticker": null,
  "exchange": null,
  "industry": "ビルメンテナンス業",
  "competitors": ["イオンディライト", "東急不動産HD", "東洋テック", "大成", "日本ハウズイング"],
  "deck_depth": "standard",
  "include_segments": "specified",
  "segments_to_deepdive": [
    {"name": "施設運営事業", "slug": "facilities", "include": true}
  ],
  "analysis_years": 7,
  "run_id": "2026-04-29_nikoh_sangyo",
  "started_at": "2026-04-29T10:00:00+09:00"
}
```

`is_listed` は判定するだけで分岐ロジックには使わない（取れる公開情報から作る原則）。
`segments_to_deepdive[].include=true` のセグメントだけ business-deepdive-agent を起動する。

---

## 依存スキル一覧

### コア（必須）

| スキル名 | 役割 |
|---|---|
| `executive-summary-pptx` | デッキ冒頭サマリー |
| `table-of-contents-pptx` | 目次 |
| `section-divider-pptx` | 中扉（標準版・拡張版で各セグメント冒頭に挿入） |
| `customer-profile-pptx` または `company-overview-pptx-v2` | 会社プロファイル |
| `company-history-pptx` | 沿革 |
| `business-portfolio-pptx` | 事業ポートフォリオ |
| `revenue-analysis-pptx` | 収益性推移 |
| `financial-benchmark-pptx` | 業界内ベンチマーク |
| `shareholder-structure-pptx` | 株主・役員 |
| `data-availability-pptx` | データ取得状況 |
| `business-deepdive-agent` | 各事業セグメント深掘り（**本スキルから呼ぶ**） |
| `merge-pptxv2` | 結合 |

### 品質レビュー

| スキル名 | 呼び出し位置 |
|---|---|
| `fact-check-reviewer` | Step 2.5 |
| `visual-quality-reviewer` | Step 9 |

---

## 単独起動 vs 内部呼び出し

### 単独起動の場合

```
ユーザー: 「○○社を深掘りして」
→ Step 0 (AskUserQuestion で対話) → Step 1..10
```

### 内部呼び出しの場合（Phase 5 で実装される `comparison-synthesis-agent` から）

```
comparison-synthesis-agent → Task tool で本スキルを A/B/C 社それぞれに起動
→ 各社の company_name / 共通 industry / 共通 competitors を JSON で受領
```

---

## 注意事項

- **公開情報主義**: Web 情報・ユーザーアップロード情報のみで分析する
- **検証論点の置き場所**: 本スキルでは「検証論点」スライドは作らない（`comparison-synthesis-agent` が全社統合で扱う）
- **「〜すべき」表現禁止**: main_message は事実記述ベース（上記ルール）
- **無限ループ防止**: visual-review 自動修正ループは最大 2 ラウンド、カウンタ必須
- **section_divider の位置**: 各セグメント冒頭（直後は必ず content）。末尾配置・連続配置は `merge_warnings.json` に記録される

---

## アセット

| ファイル | 内容 |
|---|---|
| `prompts/step1_research_template.md` | 5 論点別の Web 検索クエリテンプレ |
| `references/deck_skeleton.json` | 標準デッキ構成（会社 8 + 中扉 + (5)×N + footer 1） |
