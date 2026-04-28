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

# 事業セグメント概要 PowerPoint ジェネレーター（skeleton）

> ⚠️ **このファイルは Phase 1 (skeleton) です**。実装は Phase 2 で完成させる。
> 関連計画: `/Users/nakamaru/.claude/plans/tidy-soaring-elephant.md`

ISSUE-004（v0.3）における新規 PPTX 単体スキル。`business-deepdive-agent` の
「事業の概要は？」論点（5 論点中 1 番目）を 1 枚スライドで埋める用途。

`customer-profile-pptx` の構造を継承（左カラム: key-value テーブル / 右カラム: 業績チャート or 主要 KPI）。
会社全体ではなく**事業セグメント単位**であることが本スキルの差別化ポイント。

---

## スライド構成

| セクション | 位置 | 内容 |
|---|---|---|
| **メインメッセージ** | 最上部 | 最大 65 文字（hard-fail）、事実記述ベース |
| **チャートタイトル** | メインメッセージ直下 | 「○○社：○○事業の概要」 |
| **事業の概要** | 左側 | ブレットポイント形式の key-value テーブル |
| **業績 or 主要 KPI** | 右側 | セグメント別売上推移のネイティブチャート（営業利益率折れ線オプション）|
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

選択可（JSON で指定）:
- **(a) セグメント別売上推移**（棒グラフ + 営業利益率折れ線、customer-profile-pptx 同等）
- **(b) 主要 KPI 4-6 個のカード表示**（kpi-dashboard-pptx 風、KPI 名 + 値 + 目標）

---

## JSON データ仕様（skeleton）

```json
{
  "source": "出典：第一交通産業 有価証券報告書 第65期、決算短信",
  "main_message": "<= 65字、事実記述ベース",
  "chart_title": "第一交通産業：タクシー事業の概要",
  "parent_company": "第一交通産業株式会社",
  "segment_name": "タクシー事業",
  "overview": {
    "section_title": "事業の概要",
    "items": [
      {"label": "セグメント名", "value": "タクシー事業"},
      {"label": "事業内容", "value": "..."},
      {"label": "セグメント開始年", "value": "1960 年（創業時）"},
      {"label": "主要拠点", "value": "..."},
      {"label": "主要製品/サービス", "value": "..."},
      {"label": "主要顧客", "value": "..."},
      {"label": "セグメント従業員数", "value": "..."}
    ]
  },
  "performance": {
    "mode": "revenue_chart",
    "section_title": "業績",
    "unit_label": "（単位：億円、%）",
    "bar_label": "セグメント売上高",
    "line_label": "セグメント営業利益率",
    "data": [
      {"year": "2020", "revenue": 0, "op_margin": 0}
    ]
  }
}
```

### JSON フィールド仕様（Phase 2 で詳細化）

| フィールド | 型 | 必須 | 備考 |
|---|---|---|---|
| `source` | string | 任意 | 出典テキスト |
| `main_message` | string | 必須 | 最大 65 文字（hard-fail）、事実記述 |
| `chart_title` | string | 任意 | デフォルト「事業の概要」 |
| `parent_company` | string | 必須 | 親会社名（business-deepdive-agent から渡される） |
| `segment_name` | string | 必須 | 対象セグメント名 |
| `overview.items[]` | array | 必須 | key-value 形式、5〜8 項目推奨 |
| `performance.mode` | string | 必須 | `revenue_chart` または `kpi_cards` |
| `performance.data[]` | array | 必須 | mode に応じた構造 |

---

## 実装パターン（Phase 2 で完成）

`customer-profile-pptx/scripts/fill_customer_profile.py` を雛形とする:
- python-pptx ネイティブテーブル + 複合チャート
- フォント: Meiryo UI / Arial、テンプレ継承
- LibreOffice roundtrip で OOXML 正規化

テンプレ `assets/business-overview-template.pptx` は `customer-profile-pptx/assets/` をベースに
セグメント単位の表示に合わせて Title 1 / shape 名を調整。

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
作業ディレクトリは `company-deepdive-agent` 配下のセグメント別 subdir に統一（comparison-synthesis-agent からも参照しやすい構造）。

---

## アセット（Phase 2 で作成）

| ファイル | 用途 |
|---|---|
| `assets/business-overview-template.pptx` | スライドテンプレ（customer-profile-pptx ベース） |
| `scripts/fill_business_overview.py` | fill スクリプト |
| `references/sample_data.json` | サンプルデータ（タクシー事業 or 製造業セグメント） |

---

## 品質チェックリスト（Phase 2 完成時）

- [ ] メインメッセージが 65 字以内（hard-fail で機械検証）
- [ ] テーブル左カラム: 5〜8 項目が枠線なしで整列
- [ ] 右側: revenue_chart モード or kpi_cards モードの両方が動作
- [ ] PowerPoint で開いた際に修復ダイアログが出ない
- [ ] LibreOffice 経由でも崩れない
