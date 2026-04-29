---
name: business-deepdive-agent
description: >
  対象会社の特定の事業セグメント（有報の報告セグメント単位）について
  「事業の概要・ビジネスモデル・差別化・顧客・顧客成長」の 5 論点を深掘りし、
  5 枚の PowerPoint スライドを生成するオーケストレータースキル。

  単独でも起動可能だが、主には company-deepdive-agent から各セグメントごとに
  並列起動される。出力 PPTX 群は親オーケストレータが merge-pptxv2 で他セグメント分や
  会社レベル分と結合する設計（本スキルは結合まで行わない）。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - 「○○社の○○事業の深掘り」「事業セグメント分析」「事業の戦略を透視」という言葉が出た場合
  - company-deepdive-agent から呼び出された場合
  - 多角化企業の特定セグメントの戦略を、会社全体ではなく事業単位で深く調べたい場合
  - 顧客市場・差別化・ビジネスモデルを 1 つの事業セグメントに絞って整理したい場合
---

# 事業セグメント深掘りオーケストレーター

ISSUE-004（v0.3）における新規オーケストレーター。`company-deepdive-agent` の下流で
各事業セグメントを深掘りし、5 枚の個別 PPTX を返却する。

## 設計原則

- **対象は単一の事業セグメント** のみ。複数事業の場合は親が本スキルを N 回呼ぶ
- **結合は本スキルでは行わない**: 5 枚の個別 PPTX を出力し、merge は親（`company-deepdive-agent`）が担当
- **fact-check / visual-review は本スキルでは呼ばない**: 親オーケストレーターが統合デッキに対して一括実施する（重複コール削減）
- 公開情報のみ。取れない項目は data-availability に「✗」記録（親オーケストレータに引き渡す）

---

## 事業レベル 5 論点 → PPTX マッピング

| # | 論点 | PPTX スキル |
|---|---|---|
| 1 | 事業の概要は？ | `business-overview-pptx` |
| 2 | その事業のビジネスモデルは？ | `business-model-pptx` |
| 3 | その事業の差別化ポイントは？ | `value-chain-matrix-pptx`（バリューチェーン上のポジショニング） |
| 4 | その事業の顧客は誰か？ | `customer-profile-pptx`（顧客企業 / 顧客セグメントのプロファイル）|
| 5 | その事業の顧客は成長するか？ | `market-environment-pptx`（**顧客側市場**の規模・成長率推移）|

「顧客は誰か」「顧客は成長するか」は **顧客側** の情報。本スキルの対象事業の顧客
（B2B なら主要取引先・B2C なら顧客セグメント）を扱う。

---

## 出力スライド構成（5 枚）

```
B-01 事業の概要 (business-overview-pptx)
B-02 ビジネスモデル (business-model-pptx)
B-03 差別化（バリューチェーン上のポジション）(value-chain-matrix-pptx)
B-04 主要顧客プロファイル (customer-profile-pptx)
B-05 顧客市場の成長性 (market-environment-pptx)
```

ファイル番号は親 `company-deepdive-agent` のグローバル通し番号で書き換えられる
（B-01..B-05 は本スキル内での暫定番号）。

エグゼクティブサマリーは Phase 4 の `company-deepdive-agent` で
「会社レベル+全セグメント」の文脈で生成する設計のため、本スキルでは生成しない。

---

## 作業ディレクトリ規約

本スキルは独自の work dir を持たず、**親 `company-deepdive-agent` 配下のセグメント別 subdir** に
全ファイルを書き込む。これにより `comparison-synthesis-agent` や `merge-pptxv2` が一元的に参照可能。

```
{{WORK_DIR}}/company-deepdive-agent/<parent_run_id>/segments/<segment_slug>/
├── data_<NN>_business_overview.json
├── data_<NN+1>_business_model.json
├── data_<NN+2>_value_chain_matrix.json
├── data_<NN+3>_customer_profile.json
├── data_<NN+4>_market_environment.json
├── slide_<NN>_business_overview.pptx
├── slide_<NN+1>_business_model.pptx
├── slide_<NN+2>_value_chain_matrix.pptx
├── slide_<NN+3>_customer_profile.pptx
├── slide_<NN+4>_market_environment.pptx
├── segment_data_availability.json
└── segment_summary.json
```

`<NN>` = `global_slide_offset + 1`。`<segment_slug>` は親が決定（事業名 → URL-safe ASCII）。

**単独起動の場合**も同じ構造を擬似生成する（後述）。

---

## Step 構造

### Step 0: 引数受領 / 単独起動時の対話

#### 内部呼び出しの場合（推奨）

`company-deepdive-agent` から以下のパラメータを JSON で受け取る:

```json
{
  "parent_company_name": "第一交通産業株式会社",
  "segment_name": "タクシー事業",
  "segment_slug": "taxi",
  "parent_run_id": "2026-04-29_daiichikoutsu",
  "global_slide_offset": 11,
  "is_listed": true,
  "industry": "陸運業",
  "analysis_years": 7
}
```

#### 単独起動の場合

AskUserQuestion で以下を聞く:

1. `parent_company_name` — 対象会社の正式名（例: 「第一交通産業株式会社」）
2. `segment_name` — 深掘り対象のセグメント名（例: 「タクシー事業」）
3. `industry` — 業種（任意、検索クエリ精度向上用）
4. `analysis_years` — 顧客市場分析の年数（任意、default 7 年）

`parent_run_id` は `YYYY-MM-DD_<parent_company_slug>` 形式で自動生成（`<parent_company_slug>` は会社名を ASCII slug 化した値）。
`segment_slug` は `segment_name` を ASCII 化した値（例: タクシー事業 → `taxi`）を生成し、ユーザーに確認して必要なら修正させる。
`global_slide_offset = 0`（単独起動なので NN = 1..5）。

### Step 1: Web 検索でセグメント別 5 論点情報収集

5 論点それぞれについて、`prompts/step1_research_template.md` のクエリテンプレートに `{parent_company_name}` / `{segment_name}` / `{industry}` を展開して **5-8 件** WebSearch を実行する。

| 論点 | 優先ソース |
|---|---|
| 事業の概要 | 有報「事業の状況」/ セグメント情報 / 公式 HP の事業説明ページ |
| ビジネスモデル | 統合報告書 / セグメント別事業説明 / IR Day 資料 |
| 差別化 | 業界レポート / IR Q&A / メディアインタビュー |
| 顧客 | 有報「主要販売先」/ 業界レポート / 顧客側 IR 資料 |
| 顧客の成長 | 顧客側市場の業界レポート（矢野経済・富士経済・官公庁統計等）|

検索結果から JSON 化に必要な情報（数値・期間・出典）を抽出する。

### Step 2: data-availability セグメント単位記録

各論点について「取得済(✓) / 一部取得(△) / 未取得(✗)」を `segment_data_availability.json` に記録:

```json
{
  "segment_name": "タクシー事業",
  "parent_company_name": "第一交通産業株式会社",
  "segment_slug": "taxi",
  "items": [
    {"topic": "business_overview", "status": "obtained", "source": "有報 第65期 セグメント情報"},
    {"topic": "business_model", "status": "partial", "source": "公式HP"},
    {"topic": "value_chain_matrix", "status": "partial", "source": "業界レポート 推測込み"},
    {"topic": "customer_profile", "status": "obtained", "source": "有報 主要販売先"},
    {"topic": "market_environment", "status": "obtained", "source": "国土交通省 タクシー事業概況"}
  ]
}
```

親 `company-deepdive-agent` が全社統合の data-availability スライドに転記する。

### Step 3: 5 つの data_NN_*.json を作成 → ユーザー承認

各論点について、対応 PPTX スキルの SKILL.md に従って `data_NN_<topic>.json` を作成。
ファイル名:

| 論点 | data ファイル名 |
|---|---|
| 1 事業の概要 | `data_<NN>_business_overview.json` |
| 2 ビジネスモデル | `data_<NN+1>_business_model.json` |
| 3 差別化 | `data_<NN+2>_value_chain_matrix.json` |
| 4 顧客 | `data_<NN+3>_customer_profile.json` |
| 5 顧客成長 | `data_<NN+4>_market_environment.json` |

`<NN>` = `global_slide_offset + 1`。

5 枚分の `main_message` / 主要内容を Markdown でユーザーに提示し、承認を得る。

### Step 4: 5 つの fill_*.py を順次実行

承認後、5 つの PPTX を生成:

```bash
# 1. 事業の概要
python ~/.claude/skills/business-overview-pptx/scripts/fill_business_overview.py \
  --data <work_dir>/data_<NN>_business_overview.json \
  --template ~/.claude/skills/business-overview-pptx/assets/business-overview-template.pptx \
  --output <work_dir>/slide_<NN>_business_overview.pptx

# 2. ビジネスモデル
python ~/.claude/skills/business-model-pptx/scripts/fill_business_model.py \
  --data <work_dir>/data_<NN+1>_business_model.json \
  --template ~/.claude/skills/business-model-pptx/assets/business-model-template.pptx \
  --output <work_dir>/slide_<NN+1>_business_model.pptx

# 3. 差別化（バリューチェーン上のポジション）
python ~/.claude/skills/value-chain-matrix-pptx/scripts/fill_value_chain_matrix.py \
  --data <work_dir>/data_<NN+2>_value_chain_matrix.json \
  --template ~/.claude/skills/value-chain-matrix-pptx/assets/value-chain-matrix-template.pptx \
  --output <work_dir>/slide_<NN+2>_value_chain_matrix.pptx

# 4. 主要顧客プロファイル
python ~/.claude/skills/customer-profile-pptx/scripts/fill_customer_profile.py \
  --data <work_dir>/data_<NN+3>_customer_profile.json \
  --template ~/.claude/skills/customer-profile-pptx/assets/customer-profile-template.pptx \
  --output <work_dir>/slide_<NN+3>_customer_profile.pptx

# 5. 顧客市場の成長性
python ~/.claude/skills/market-environment-pptx/scripts/fill_market_environment.py \
  --data <work_dir>/data_<NN+4>_market_environment.json \
  --template ~/.claude/skills/market-environment-pptx/assets/market-environment-template.pptx \
  --output <work_dir>/slide_<NN+4>_market_environment.pptx
```

`<work_dir>` = `{{WORK_DIR}}/company-deepdive-agent/<parent_run_id>/segments/<segment_slug>/`

各 fill_*.py が成功したか確認（exit code 0、出力 PPTX 存在）。`main_message` 65 字超過時の hard-fail は本スキルの想定エラーとして再生成ループで対処する（`prompts/main_message_principles.md` を参照して書き直し → 該当 fill_*.py を再実行）。

### Step 5: segment_summary.json を出力

```json
{
  "segment_name": "タクシー事業",
  "parent_company_name": "第一交通産業株式会社",
  "segment_slug": "taxi",
  "parent_run_id": "2026-04-29_daiichikoutsu",
  "global_slide_offset": 0,
  "slide_files": [
    "slide_01_business_overview.pptx",
    "slide_02_business_model.pptx",
    "slide_03_value_chain_matrix.pptx",
    "slide_04_customer_profile.pptx",
    "slide_05_market_environment.pptx"
  ],
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

### Step 6: 終了

#### 単独起動の場合
- ユーザーに 5 PPTX のフルパスを提示して終了
- merge は実施しない（必要なら別途 merge-pptxv2 を起動）

#### 内部呼び出しの場合
- 親 `company-deepdive-agent` に以下を返却:
  - 5 枚の `slide_*.pptx`（フルパス）
  - `segment_data_availability.json`（フルパス）
  - `segment_summary.json`（フルパス）
- 親が merge_order.json を組み、merge-pptxv2 と visual-quality-reviewer を呼ぶ

---

## main_message 共通ルール（5 PPTX 全てに適用、厳守）

<!-- source: skills/_common/prompts/main_message_principles.md (manual sync until D2) -->

### ルール1: 長さは **65 文字以内**（厳格）

- 句読点・記号・スペースを含めて 65 文字以内
- テンプレート最上部のメッセージ枠が固定幅のため、超えた場合は要約や段落分けではなく **書き直し**
- 65 文字を 1 字でも超えた状態で `fill_*.py` に渡すと ValueError で hard-fail する

### ルール2: トーンは **事実記述ベース**（「〜すべき」禁止）

- 公開情報のみで断定できないアクションや戦略示唆は書かない
- 不明な点は「〜は公開情報からは確定できず追加調査が必要」と率直に書く（検証論点として明示）

**例**:
- ✗ 「対象会社は海外展開を加速すべき」（公開情報では断定不可）
- ✓ 「対象会社は国内売上比率が 90% と高く、海外展開の実績は限定的である」（事実記述）
- ✓ 「対象会社の海外展開方針は Web 情報では限定的、マネジメントインタビューで確認が必要」（検証論点）

### 65 字オーバー時の短縮原則 4 つ

1. **主語は 1 つだけ** — 「市場は」「主要プレイヤーは」「対象会社は」のいずれか 1 つに絞る
2. **修飾語を削除** — 「主要な」「重要な」「大きな」「急速な」等の主観的な修飾語を落とす
3. **数値は 1 つだけ残す** — CAGR と シェアを両方載せず、より重要な 1 つを選ぶ
4. **結論を述べる、根拠は本文スライドに任せる** — 「〜だから〜である」の前段を切り、結論部のみ残す

注: `business-model-pptx` / `value-chain-matrix-pptx` / `customer-profile-pptx` の SKILL.md は「〜すべきで締める / 70 字」と書かれているが、本オーケストレーターから呼ぶ場合は **本ルールで上書き**（65 字・事実記述）。

---

## オーケストレーター契約（merge_order.json は親が組む）

<!-- source: skills/_common/references/orchestrator_contract.md (manual sync until D2) -->

本スキルは個別 PPTX のみ返却し、`merge_order.json` の生成は親 `company-deepdive-agent` の責務。
親が組む `merge_order.json.entries[]` の本セグメント部分は以下のような形式になる:

```json
{
  "slide_number": 11,
  "file_name": "slide_11_business_overview.pptx",
  "skill_name": "business-overview-pptx",
  "data_file": "data_11_business_overview.json",
  "category": "content"
}
```

- `category` は本セグメントの 5 枚すべて `content`（中扉は親側で別途追加）
- `data_file` / `file_name` のパスは親から見て `segments/<segment_slug>/` 相対 or 絶対パスで解決可能とする

詳細は `skills/_common/references/orchestrator_contract.md` を参照。

---

## 単独起動 vs 内部呼び出し

### 単独起動の場合

```
ユーザー: 「第一交通産業のタクシー事業を深掘りして」
→ Step 0 (AskUserQuestion で対話) → Step 1..6
```

`parent_run_id` を `YYYY-MM-DD_<parent_company_slug>` で自動生成し、
`{{WORK_DIR}}/company-deepdive-agent/<parent_run_id>/segments/<segment_slug>/` 構造を
business-deepdive-agent 自身が作る。Phase 4（company-deepdive-agent 実装後）はそのまま流用可。

### 内部呼び出しの場合（推奨）

```
company-deepdive-agent → Task tool で本スキルを起動
→ parent_run_id / segment_slug / global_slide_offset を JSON で受領 → Step 1..6
```

並列起動可（同じ会社の複数セグメントを並列で深掘り）。

---

## 注意事項

- **対象は単一の事業セグメント**: 複数事業を扱う場合は親が本スキルを複数回呼ぶ
- **顧客 = 対象事業の顧客**: 本スキルが扱う「顧客」は会社全体の顧客ではなく、対象セグメントの顧客
- **顧客の成長 = 顧客市場の成長**: market-environment-pptx を顧客側市場（例: タクシー事業なら「観光・交通需要」市場）に向けて使用
- **「〜すべき」表現禁止**: 上記 main_message ルールに従う
- **fact-check / visual-review は親が実施**: 本スキル単体では fact-check-reviewer / visual-quality-reviewer を呼ばない

---

## 依存スキル一覧

### コア（必須）

| スキル名 | 役割 |
|---|---|
| `business-overview-pptx` | 事業概要 |
| `business-model-pptx` | ビジネスモデル |
| `value-chain-matrix-pptx` | 差別化（バリューチェーン上のポジション） |
| `customer-profile-pptx` | 顧客プロファイル |
| `market-environment-pptx` | 顧客市場の成長性 |

### 任意

`section-divider-pptx`（拡張版で各セグメント冒頭に中扉を入れる場合、親 `company-deepdive-agent` が制御）

---

## アセット

| ファイル | 内容 |
|---|---|
| `prompts/step1_research_template.md` | セグメント単位の 5 論点別 Web 検索クエリテンプレート |
| `references/deck_skeleton.json` | 5 枚の標準スライド構造定義（merge_order.json の素材） |
