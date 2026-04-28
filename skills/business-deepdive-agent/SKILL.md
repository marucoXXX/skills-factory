---
name: business-deepdive-agent
description: >
  対象会社の特定の事業セグメント（有報の報告セグメント単位）について
  「事業の概要・ビジネスモデル・差別化・顧客・顧客成長」の 5 論点を深掘りし、
  6 枚の PowerPoint スライド（エグサマ + 5 論点）を生成するオーケストレータースキル。

  単独でも起動可能だが、主には company-deepdive-agent から各セグメントごとに
  並列起動される。出力 PPTX 群は親オーケストレータが merge-pptxv2 で他セグメント分や
  会社レベル分と結合する設計（本スキルは結合まで行わない）。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - 「○○社の○○事業の深掘り」「事業セグメント分析」「事業の戦略を透視」という言葉が出た場合
  - company-deepdive-agent から呼び出された場合
  - 多角化企業の特定セグメントの戦略を、会社全体ではなく事業単位で深く調べたい場合
  - 顧客市場・差別化・ビジネスモデルを 1 つの事業セグメントに絞って整理したい場合
---

# 事業セグメント深掘りオーケストレーター（skeleton）

> ⚠️ **このファイルは Phase 1 (skeleton) です**。実装は Phase 3 で完成させる。
> 関連計画: `/Users/nakamaru/.claude/plans/tidy-soaring-elephant.md`

ISSUE-004（v0.3）における新規オーケストレーター。`company-deepdive-agent` の下流で各事業セグメントを深掘り。

## 設計原則

- **対象は単一の事業セグメント** のみ。複数事業の場合は親が本スキルを N 回呼ぶ
- **結合は本スキルでは行わない**: 6 枚の個別 PPTX を出力し、merge は親（`company-deepdive-agent`）が担当
- 公開情報のみ。取れない項目は data-availability に「✗」記録（親オーケストレータに引き渡す）

---

## 事業レベル 5 論点 → PPTX マッピング

| # | 論点 | PPTX スキル |
|---|---|---|
| 1 | 事業の概要は？ | `business-overview-pptx` ⭐**新規**（Phase 2 で実装） |
| 2 | その事業のビジネスモデルは？ | `business-model-pptx` |
| 3 | その事業の差別化ポイントは？ | `value-chain-matrix-pptx`（バリューチェーン上のポジショニング） |
| 4 | その事業の顧客は誰か？ | `customer-profile-pptx`（顧客企業 / 顧客セグメントのプロファイル）|
| 5 | その事業の顧客は成長するか？ | `market-environment-pptx`（**顧客市場**の規模・成長率推移）|

「顧客は誰か」「顧客は成長するか」は **顧客側** の情報。本スキルの対象事業の顧客（B2B なら主要取引先・B2C なら顧客セグメント）を扱う。

---

## 出力スライド構成（標準: 6 枚）

```
B-01 事業エグゼクティブサマリー (executive-summary-pptx)
B-02 事業の概要 (business-overview-pptx ⭐新規)
B-03 ビジネスモデル (business-model-pptx)
B-04 差別化（バリューチェーン上のポジション）(value-chain-matrix-pptx)
B-05 主要顧客プロファイル (customer-profile-pptx)
B-06 顧客市場の成長性 (market-environment-pptx)
```

ファイル番号は親 `company-deepdive-agent` のグローバル通し番号で書き換えられる（B-01..B-06 は本スキル内での暫定番号）。

---

## Step 構造

### Step 0: 引数受領

`company-deepdive-agent` から渡されるパラメータ:

```json
{
  "parent_company_name": "第一交通産業株式会社",
  "segment_name": "タクシー事業",
  "segment_slug": "taxi",
  "parent_run_id": "2026-04-29_daiichikoutsu",
  "global_slide_offset": 11,
  "is_listed": true,
  "industry": "陸運業",
  "include_overview": true
}
```

`segment_slug` は親 `company-deepdive-agent` が決定し、本スキルが書き込む作業ディレクトリ
`{{WORK_DIR}}/company-deepdive-agent/<parent_run_id>/segments/<segment_slug>/` のパスに使う。

単独起動の場合は AskUserQuestion で対話確認 + 自前で run_id / segment_slug を生成する。

### Step 1: Web 検索でセグメント別 5 論点情報収集

| 論点 | 優先ソース |
|---|---|
| 事業の概要 | 有報「事業の状況」/ セグメント情報 / 公式 HP の事業説明ページ |
| ビジネスモデル | 統合報告書 / セグメント別事業説明 / IR Day 資料 |
| 差別化 | 業界レポート / IR Q&A / メディアインタビュー |
| 顧客 | 有報「主要販売先」/ 業界レポート / 顧客側 IR 資料 |
| 顧客の成長 | 顧客側市場の業界レポート（矢野経済・富士経済等）|

**検索クエリのテンプレートは `prompts/step1_research_template.md` に格納（Phase 3 で詳細化）**。

### Step 2: data-availability セグメント単位記録

セグメント単位の取得状況を `segment_data_availability.json` に記録し、
親 `company-deepdive-agent` に引き渡す（親が全社統合で表示）。

### Step 3: 5 論点を既存 PPTX スキルで埋める

各論点について `data_NN_*.json` を生成し、対応 PPTX スキルの `fill_*.py` を実行。

ファイル名: `slide_<global_slide_offset + n>_<論点名>.pptx`（n = 1..6）

**作業ディレクトリ統一規約**: 本スキルは独自の work dir を持たず、親 `company-deepdive-agent` 配下のセグメント別 subdir
`{{WORK_DIR}}/company-deepdive-agent/<parent_run_id>/segments/<segment_slug>/` に全ファイルを書き込む。
これにより comparison-synthesis-agent や merge-pptxv2 が一元的に参照可能。

`<segment_slug>` は `segment_name` を URL-safe な ASCII に変換した値（例: `タクシー事業` → `taxi`）。
slug 化規則は親 `company-deepdive-agent` が決める（Phase 4 で実装）。

### Step 4: 個別 PPTX 6 枚 + サマリー JSON を返却

親オーケストレータに以下を引き渡す（すべて上記 segments/<segment_slug>/ 配下）:
- 6 枚の個別 PPTX（merge-pptxv2 用、merge_order.json は親が組む）
- `segment_data_availability.json`（取得状況の集計）
- `segment_summary.json`（エグサマ生成用、親が会社全体の検証論点に使う）

---

## JSON データ仕様の連携

各論点 PPTX の `data_NN_*.json` は対応 PPTX スキルのスキーマに準拠（`business-model-pptx` / `value-chain-matrix-pptx` 等の SKILL.md 参照）。

本スキル独自の summary 形式 `segment_summary.json`:

```json
{
  "segment_name": "タクシー事業",
  "parent_company_name": "第一交通産業株式会社",
  "key_findings": [
    {"category": "差別化", "finding": "..."},
    {"category": "顧客", "finding": "..."}
  ],
  "open_questions": [
    "公開情報では確認できず、業界ヒアリング推奨の論点 1",
    "..."
  ],
  "data_gaps": [
    "セグメント別営業利益率の詳細内訳",
    "..."
  ]
}
```

`open_questions` は親 `comparison-synthesis-agent` で全社統合の検証論点に集約される。

---

## `_common/` 再利用

```
<!-- source: skills/_common/prompts/main_message_principles.md (manual sync until D2) -->
<!-- source: skills/_common/references/orchestrator_contract.md (manual sync until D2) -->
```

Step 2.5（fact-check）と Step 7（visual-review）は親 `company-deepdive-agent` 側で全体一括実施するため、本スキル単体では呼び出さない（重複コール削減）。

---

## 依存スキル一覧

### コア（必須）

| スキル名 | 役割 |
|---|---|
| `executive-summary-pptx` | セグメントエグサマ |
| `business-overview-pptx` ⭐ | 事業概要（新規、Phase 2 で実装） |
| `business-model-pptx` | ビジネスモデル |
| `value-chain-matrix-pptx` | 差別化（バリューチェーン上のポジション） |
| `customer-profile-pptx` | 顧客プロファイル |
| `market-environment-pptx` | 顧客市場の成長性 |

### 任意

`section-divider-pptx`（拡張版で各セグメント冒頭に中扉を入れる場合、親が制御）

---

## 単独起動 vs 内部呼び出し

### 単独起動の場合

```bash
# AskUserQuestion で対象会社・セグメント・産業を確認 → Step 1 へ
```

### 内部呼び出しの場合（推奨）

```bash
# company-deepdive-agent が Task tool 経由で本スキルを起動、
# parent_company_name / segment_name / parent_run_id / global_slide_offset を JSON で渡す
```

並列起動可（同じ会社の複数セグメントを並列で深掘り）。

---

## 注意事項

- **対象は単一の事業セグメント**: 複数事業を扱う場合は親が本スキルを複数回呼ぶ
- **顧客 = 対象事業の顧客**: 本スキルが扱う「顧客」は会社全体の顧客ではなく、対象セグメントの顧客
- **顧客の成長 = 顧客市場の成長**: market-environment-pptx を顧客側市場（例: タクシー事業なら「外食・観光・交通需要」市場）に向けて使用
- **「〜すべき」表現禁止**

---

## アセット（Phase 3 で作成）

| ファイル | 内容 |
|---|---|
| `prompts/step1_research_template.md` | セグメント単位の 5 論点別 Web 検索クエリ |
| `references/deck_skeleton.json` | 6 枚の標準スライド配列定義 |
