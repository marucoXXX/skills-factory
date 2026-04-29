---
name: business-overview-pptx
description: >
  事業セグメント概要（Business Overview）の PowerPoint スライドを 1 枚で生成するスキル。
  企業内の特定の事業セグメント（有報の報告セグメント単位）について、
  事業概要・主要数字・主要製品/サービスを左右 2 カラムで整理する。
  会社全体ではなく「○○社の○○事業」という事業単位の概要を 1 枚で示す用途。
  customer-profile-pptx の事業版に相当し、business-deepdive-agent から呼ばれる
  「事業の概要は？」論点 1 枚スライドを担う。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - 「事業概要」「Business Overview」「セグメント概要」「事業セグメント」という言葉が出た場合
  - 「○○社の○○事業の概要をスライドに」「事業セグメント単位の概要を 1 枚で」という要望
  - business-deepdive-agent から呼び出された場合
  - 多角化企業の事業ポートフォリオ内訳の各事業を 1 枚ずつスライド化する要望
---

# 事業セグメント概要 PowerPoint ジェネレーター

ISSUE-004（v0.3）における新規 PPTX 単体スキル。`business-deepdive-agent` の
「事業の概要は？」論点（5 論点中 1 番目）を 1 枚スライドで埋める用途。

`customer-profile-pptx` の構造を継承（左カラム: key-value テーブル / 右カラム: 業績 or KPI）。
会社全体ではなく**事業セグメント単位**であることが本スキルの差別化ポイント。

---

## スライド構成

| セクション | 位置 | 内容 |
|---|---|---|
| **メインメッセージ** | 最上部 | **最大 65 文字（hard-fail）**、事実記述ベース |
| **チャートタイトル** | メインメッセージ直下 | デフォルト「○○社：○○事業の概要」 |
| **事業の概要** | 左側 | ブレットポイント形式の key-value テーブル（枠線なし） |
| **業績 or 主要 KPI** | 右側 | mode に応じて切替（下記） |
| **出典** | 左下 | 有報・決算短信・公式 HP 等 |

### 左側: 事業の概要（典型的な項目）

- セグメント名・親会社名
- 事業内容（1〜2 行）
- セグメント開始年（事業発足 or 親会社の事業開始年）
- 主要拠点（本社・主要工場・主要営業所）
- 主要製品 / サービス
- 主要顧客（B2B の場合）
- セグメント従業員数（開示があれば）
- セグメント長 / 事業責任者（開示があれば）

### 右側: 業績 or 主要 KPI

JSON の `performance.mode` で切り替え:

- **`revenue_chart`** — 棒グラフ（セグメント売上高）+ 折れ線（セグメント営業利益率）+ CAGR 注釈
  - `customer-profile-pptx` と同等の複合チャート
  - 開示があるセグメント（上場親会社のセグメント情報）向け
- **`kpi_cards`** — 1〜6 個の KPI カードを 2 列グリッドに配置
  - 売上開示なしのセグメント、定性指標中心の事業向け
  - 各カード: 名称（上）/ 値（中央大）/ 補足（下）

---

## JSON データ仕様

`{{WORK_DIR}}/data_NN_business_overview.json` に以下の形式で保存する：

### 共通フィールド

| フィールド | 型 | 必須 | 備考 |
|---|---|---|---|
| `source` | string | 任意 | 出典テキスト（左下に表示） |
| `main_message` | string | 必須 | **最大 65 文字（hard-fail）**、事実記述ベース |
| `chart_title` | string | 任意 | デフォルト `"{parent_company}：{segment_name}の概要"` |
| `parent_company` | string | 必須 | 親会社名 |
| `segment_name` | string | 必須 | 対象セグメント名 |
| `overview.section_title` | string | 任意 | デフォルト「事業の概要」 |
| `overview.items[]` | array | 必須 | `{label, value}` の配列、5〜8 項目推奨 |
| `performance.mode` | string | 必須 | `"revenue_chart"` or `"kpi_cards"` |
| `performance.section_title` | string | 任意 | デフォルト「業績」または「主要 KPI」 |

### `mode = "revenue_chart"` 固有

```json
{
  "performance": {
    "mode": "revenue_chart",
    "unit_label": "（単位：億円、%）",
    "bar_label": "セグメント売上高",
    "line_label": "セグメント営業利益率",
    "data": [
      {"year": "2020", "revenue": 460, "op_margin": -1.5},
      {"year": "2021", "revenue": 442, "op_margin": -2.0}
    ]
  }
}
```

| フィールド | 型 | 必須 | 備考 |
|---|---|---|---|
| `data[].year` | string | 必須 | 年度ラベル |
| `data[].revenue` | number | 必須 | セグメント売上高 |
| `data[].op_margin` | number | 必須 | セグメント営業利益率（%） |

### `mode = "kpi_cards"` 固有

```json
{
  "performance": {
    "mode": "kpi_cards",
    "cards": [
      {"name": "保有車両数", "value": "8,400", "unit": "台", "sub": "全国第3位"},
      {"name": "稼働率",    "value": "78.5", "unit": "%",  "sub": "業界平均+5pt"}
    ]
  }
}
```

| フィールド | 型 | 必須 | 備考 |
|---|---|---|---|
| `cards[]` | array | 必須 | 1〜6 個 |
| `cards[].name` | string | 必須 | KPI 名（上部、12pt Bold） |
| `cards[].value` | string\|number | 必須 | 値（中央、28pt Bold、青） |
| `cards[].unit` | string | 任意 | 値に直接連結される単位 |
| `cards[].sub` | string | 任意 | 補足（下部、10pt グレー） |

---

## スクリプト実行コマンド

```bash
pip install python-pptx -q --break-system-packages

python <SKILL_DIR>/scripts/fill_business_overview.py \
  --data {{WORK_DIR}}/data_NN_business_overview.json \
  --template <SKILL_DIR>/assets/business-overview-template.pptx \
  --output {{OUTPUT_DIR}}/slide_NN_business_overview.pptx
```

※ `<SKILL_DIR>` は実際のスキルインストールパスに置き換えること。

### 出力確認

```bash
python -m markitdown {{OUTPUT_DIR}}/slide_NN_business_overview.pptx
```

---

## オーケストレーター連携

`business-deepdive-agent` から呼び出される場合の規約：

| 項目 | 値 |
|---|---|
| 入力 JSON ファイル名 | `data_NN_business_overview.json`（NN は global_slide_offset 経由で親が採番） |
| 出力 PPTX ファイル名 | `slide_NN_business_overview.pptx`（同上） |
| 入力ディレクトリ | `{{WORK_DIR}}/company-deepdive-agent/<parent_run_id>/segments/<segment_slug>/` |
| 出力ディレクトリ | 同上 |

`business-deepdive-agent` は本スキルを **5 論点中 1 番目** として呼び、merge は親（`company-deepdive-agent`）が担当。
作業ディレクトリは `company-deepdive-agent` 配下のセグメント別 subdir に統一。

---

## デザイン仕様

### フォントサイズ一覧

| 要素 | サイズ | 備考 |
|---|---|---|
| メインメッセージ | テンプレート準拠 | Bold、Title 1 |
| チャートタイトル | テンプレート準拠 | |
| セクションタイトル | 14pt | Bold、下線付き |
| 事業概要ラベル | 14pt | Bold、「•」付き |
| 事業概要値 | 14pt | Regular |
| KPI 名 | 12pt | Bold |
| KPI 値 | 28pt | Bold、青 (#4E79A7) |
| KPI 補足 | 10pt | グレー (#666666) |
| データラベル | 12pt | |
| 凡例・単位表記 | 12pt | |
| 軸（年ラベル） | 11pt | 縦書き |
| CAGR 数値 | 16pt | Bold、楕円内 |
| 出典 | 10pt | グレー (#666666) |

### 色

| 要素 | カラーコード |
|---|---|
| テキスト | #333333 |
| 棒グラフ（売上高） | #4E79A7 |
| 折れ線・マーカー（営業利益率） | #003366 |
| 営業利益率データラベル | #FFFFFF（白） |
| KPI カード背景 | #F7F7F7 |
| KPI カード枠線 | #D0D0D0 |
| 出典テキスト | #666666 |

### レイアウト定数

| 要素 | 値 |
|---|---|
| 左パネル開始 X | 0.41in |
| 右パネル開始 X | 6.50in |
| パネル開始 Y | 1.50in |
| 左パネル幅 | 5.80in |
| 右パネル幅 | 6.40in |
| ラベル列幅（左テーブル） | 1.60in（事業向けに広め） |
| CAGR gap_above | 1.20in |

---

## 品質チェックリスト

- [ ] `main_message` が 65 字以内（hard-fail で機械検証）
- [ ] `parent_company` / `segment_name` が両方セットされている
- [ ] 左側: 全項目がブレットポイント形式で表示、枠線なし
- [ ] 右側 (revenue_chart): 棒グラフ＋折れ線、データラベル全点表示、目盛線なし、年ラベル縦書き
- [ ] 右側 (revenue_chart): CAGR が自動計算され矢印＋楕円で表示
- [ ] 右側 (kpi_cards): 1〜6 カードが 2 列グリッドに配置、値が青で中央揃え
- [ ] 出典が左下に表示
- [ ] PowerPoint で開いた際に修復ダイアログが出ない
- [ ] LibreOffice 経由でも崩れない

---

## アセット

| ファイル名 | 用途 |
|---|---|
| `assets/business-overview-template.pptx` | スライドテンプレート（customer-profile ベース） |
| `scripts/fill_business_overview.py` | JSON データから PPTX を生成するスクリプト |
| `references/sample_data.json` | サンプル JSON（第一交通産業 タクシー事業） |
