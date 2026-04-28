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

# 会社深掘りオーケストレーター（skeleton）

> ⚠️ **このファイルは Phase 1 (skeleton) です**。実装は Phase 4 で完成させる。
> 関連計画: `/Users/nakamaru/.claude/plans/tidy-soaring-elephant.md`

ISSUE-004（v0.3）における新規オーケストレーター。`market-overview-agent` の下流で各社ドリルダウンを担う。

## 設計原則

- **会社レベル 5 論点 + 事業セグメント単位 5 論点 × N 事業** を 1 つの結合デッキに集約
- 上場・非上場問わず、**取れる公開情報から最大限作成**
- 取れなかった項目は `data-availability-pptx` で「✗未取得」明示（smallcap の三角測量は使わない、シンプルに公開情報をそのまま記述）
- セグメントの検出は本スキルの責務（business-deepdive-agent への引き渡しは本スキル経由）

---

## 会社レベル 5 論点 → PPTX マッピング

| # | 論点 | PPTX スキル |
|---|---|---|
| 1 | 会社の概要は？ | `customer-profile-pptx` または `company-overview-pptx-v2` |
| 2 | 会社の沿革は？ | `company-history-pptx` |
| 3 | 事業ポートフォリオは？ | `business-portfolio-pptx` |
| 4 | 会社としての収益性は？ | `revenue-analysis-pptx` + `financial-benchmark-pptx` |
| 5 | 株主・役員は？ | `shareholder-structure-pptx` |

---

## デッキ構成（標準版）

```
[Section 1] 会社概要レイヤー（会社レベル）
01 エグゼクティブサマリー (executive-summary-pptx)
02 目次 (table-of-contents-pptx)
03 (中扉) 会社の概要 (section-divider-pptx)
04 会社プロファイル (customer-profile-pptx)
05 会社の沿革 (company-history-pptx)
06 事業ポートフォリオ (business-portfolio-pptx)
07 収益性推移 (revenue-analysis-pptx)
08 業界内財務ベンチマーク (financial-benchmark-pptx)
09 株主・役員構成 (shareholder-structure-pptx)

[Section 2..N+1] 各事業セグメント深掘り（business-deepdive-agent から委譲）
10 (中扉) ○○事業 1 (section-divider-pptx)
11..15 ○○事業 1 の 5 論点 (business-deepdive-agent 経由)
16 (中扉) ○○事業 2
17..21 ○○事業 2 の 5 論点
...

[末尾]
末 データアベイラビリティ (data-availability-pptx)
```

スライド総数の目安: 9 (会社レベル) + (1 + 5) × N (事業数) + 1 (data avail) = 概ね **15〜30 枚**。

---

## Step 構造

### Step 0: 対象会社・出力先確認

`AskUserQuestion` で以下を確定:

| 質問 | 選択肢 |
|---|---|
| 対象会社名 | テキスト入力 |
| 出力ディレクトリ | `outputs/Deepdive_<会社名>_<date>/` |
| デッキ深度 | 標準（推奨）/ 簡易（会社レベルのみ）/ 拡張（中扉あり） |
| 事業セグメント深掘りを含めるか | A. 含める（推奨）/ B. 会社レベルのみ |

### Step 0.5: 同名異社の確認（任意）

検索結果に複数の同名企業がある場合、ユーザーに正式名称・本社所在地・上場区分で確認。
（market-overview-agent の Step 0.5 とは別の問題で、ここでは事業モデル境界ではなく企業特定が論点）

### Step 1: Web 検索による会社レベル 5 論点の情報収集

| 論点 | 優先ソース |
|---|---|
| 会社の概要 | 公式 HP / 会社案内 / 有報冒頭 |
| 沿革 | 公式 HP / 統合報告書 / Wikipedia（一次ソース確認必須） |
| 事業ポートフォリオ | 有報「事業の状況」/ 決算短信セグメント情報 |
| 収益性 | 有報・決算短信・SPEEDA / EDINET |
| 株主・役員 | 有報「株主構成」「役員構成」/ 統合報告書 |

非上場の場合は公式 HP・プレスリリース・業界誌・帝国データバンクで埋められる範囲のみ。

### Step 2: データアベイラビリティ整理

`data_NN_data_availability.json` に集計。`status` は `complete` / `partial` / `missing` の 3 値。

### Step 2.5: ファクトチェック（任意）

`fact-check-reviewer` を呼ぶ。ユーザーに `high_risk` / `all` / `skip` を選ばせる。

### Step 3: 会社レベル 5 論点のスライド生成

各論点を対応 PPTX スキル（上記マッピング）の `fill_*.py` で生成。

### Step 4: セグメント検出

`business-portfolio-pptx` の入力データから報告セグメント一覧を抽出。複数事業の場合はユーザーに最終確認。

### Step 5: 各セグメントについて business-deepdive-agent を起動

各事業について `business-deepdive-agent` を起動し、6 枚の PPTX 群を返却させる。

**作業ディレクトリ規約**:
```
{{WORK_DIR}}/company-deepdive-agent/<run_id>/
├── scope.json                     # 本スキルが管理
├── data_01_exec_summary.json
├── data_NN_*.json                 # 会社レベル 5 論点
├── slide_NN_*.pptx                # 会社レベルスライド
├── data_NN_data_availability.json # 全社統合データアベイラビリティ
├── merge_order.json               # 本スキルが構築
└── segments/
    ├── taxi/                      # business-deepdive-agent が書き込む
    │   ├── data_NN_business_overview.json
    │   ├── data_NN_business_model.json
    │   ├── ...
    │   ├── slide_NN_*.pptx
    │   ├── segment_data_availability.json
    │   └── segment_summary.json
    ├── bus/
    └── real_estate/
```

`segment_slug` は本スキルが決定（事業名 → ASCII slug 化、衝突時は連番付与）。

並列起動可（事業 1 / 事業 2 / 事業 3 を並列で深掘り、終了を待つ）。

### Step 6: merge_order.json 構築 + merge-pptxv2 で結合

会社レベル 9 枚 + 事業ごとの 6 枚 × N + データアベイラビリティ 1 枚 を順序通りに結合。

`skills/_common/references/orchestrator_contract.md` の merge_order.json スキーマに準拠。

```bash
python3 ~/.claude/skills/merge-pptxv2/scripts/merge_pptx_v2.py \
  --merge-order {{WORK_DIR}}/<run_id>/merge_order.json \
  outputs/Deepdive_<社名>_<date>.pptx \
  <slide_01> <slide_02> ... <slide_N>
```

### Step 7: visual-quality-reviewer + 自動修正ループ

最大 2 ラウンド。`severity=high` の issue は自動で JSON を修正して該当スキル再 fill → 再 merge → 再 review。

### Step 8: ユーザーへ提示

- `outputs/Deepdive_<社名>_<date>.pptx`（結合デッキ）
- `outputs/Deepdive_<社名>_<date>/data-availability.md`（取得状況のサマリー）

---

## `_common/` 再利用

```
<!-- source: skills/_common/prompts/main_message_principles.md (manual sync until D2) -->
<!-- source: skills/_common/prompts/step2_5_factcheck_invocation.md (manual sync until D2) -->
<!-- source: skills/_common/prompts/step_final_visual_review_loop.md (manual sync until D2) -->
<!-- source: skills/_common/references/orchestrator_contract.md (manual sync until D2) -->
```

`step0_scope_clarification.md` は market 系の事業モデル境界検知が中心のため、本スキルでは流用せず、Step 0.5（同名異社確認）として別途定義する。

---

## scope.json（本オーケストレータ内部）

`{{WORK_DIR}}/company-deepdive-agent/<run_id>/scope.json`:

```json
{
  "company_name": "第一交通産業株式会社",
  "company_aliases": ["第一交通産業", "第一交通"],
  "is_listed": true,
  "ticker": "9035",
  "exchange": "東証スタンダード",
  "deck_depth": "standard",
  "include_segments": true,
  "segments": [
    {"name": "タクシー事業", "include": true},
    {"name": "バス事業", "include": true},
    {"name": "不動産事業", "include": true},
    {"name": "介護・福祉事業", "include": true},
    {"name": "その他", "include": false}
  ],
  "run_id": "2026-04-29_daiichikoutsu",
  "started_at": "2026-04-29T10:00:00+09:00"
}
```

`is_listed` は判定するだけで分岐ロジックには使わない（取れる公開情報から作る原則）。
`include` フラグでセグメント深掘りの対象を絞れる。

---

## 依存スキル一覧

### コア（必須）

| スキル名 | 役割 |
|---|---|
| `executive-summary-pptx` | デッキ冒頭サマリー |
| `table-of-contents-pptx` | 目次 |
| `section-divider-pptx` | 中扉（拡張版のみ） |
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
| `fact-check-reviewer` | Step 2.5（任意） |
| `visual-quality-reviewer` | Step 7 |

---

## 注意事項

- **公開情報主義**: Web 情報・ユーザーアップロード情報のみで分析する
- **検証論点の置き場所**: 本スキルでは「検証論点」スライドは作らない（`comparison-synthesis-agent` が全社統合で扱う）
- **「〜すべき」表現禁止**: main_message は事実記述ベース（`_common/prompts/main_message_principles.md`）
- **無限ループ防止**: 自動修正ループは最大 2 ラウンド

---

## アセット（Phase 4 で作成）

| ファイル | 内容 |
|---|---|
| `prompts/step1_research_template.md` | 5 論点別の Web 検索クエリテンプレ |
| `references/deck_skeleton.json` | 標準・簡易・拡張のスライド配列定義 |
