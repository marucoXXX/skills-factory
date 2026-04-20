---
name: fact-check-reviewer
description: >
  Web検索で収集された事実主張（数値・シェア・市場規模・日付・固有名詞・引用）を
  再度Web検索で裏取りし、疑わしい主張をJSONレポートとしてフラグするファクトチェック用スキル。
  `strategy-report-agent` の Step 2.5 で呼び出され、スライド生成前に情報の信頼性を担保する用途が主。
  任意の JSON データ群に対しても単独起動可能。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - 「ファクトチェック」「fact check」「情報の真偽確認」「裏取り」という言葉が出た場合
  - 「Web情報が正しいか確認」「数値の検証」「シェアの裏取り」という要望
  - `strategy-report-agent` のStep 2.5から呼び出される場合
  - 調査メモや JSON 群に対する事実検証要望
---

# Fact-Check Reviewer

Web検索で集めた情報の真偽を再検証する専用レビュアー。

**出力は JSON レポート**（`fact_check_report.json`）。オーケストレーターや
ユーザーがこれを読んで修正・追加調査の判断に使う。

---

## 前提

- **実行主体**: Claude 本体。本スキルの Python スクリプトは**ファクト候補の抽出**のみを担い、
  **実際の裏取り（WebSearch / WebFetch）は Claude が行う**
- **作業ディレクトリ**: `{{WORK_DIR}}/`（= `{{FACTORY_ROOT}}/work/fact-check-reviewer/`）

---

## 入力

| 項目 | 形式 | 必須 | 説明 |
|---|---|---|---|
| `data_dir` | ディレクトリ | 必須 | 検証対象の `data_*.json` を含むディレクトリ（通常は `{{FACTORY_ROOT}}/work/strategy-report-agent/`） |
| `scope` | 文字列 | 必須 | `high_risk` / `all` / `skip` のいずれか。`strategy-report-agent` が `AskUserQuestion` で取得したユーザー選択値 |
| `target_company` | 文字列 | 任意 | 対象会社名（裏取り検索クエリの精度向上に使用） |

### スコープの定義

| スコープ | 検証対象 |
|---|---|
| `high_risk` | **数値**（売上・シェア・市場規模・成長率）、**日付**（沿革年・設立年）、**シェア出典**、**固有名詞**（競合社名・役員名） |
| `all` | `high_risk` + テキスト主張（定性的な業界記述・顧客層・戦略方針等） |
| `skip` | 何もしない。スキルは `overall_verdict=skipped` の空レポートを返す |

---

## 処理フロー

### Step 1: ファクト候補の抽出

```bash
{{PYTHON_BIN}} {{SKILL_DIR}}/scripts/extract_claims.py \
  --data-dir <data_dir> \
  --scope <scope> \
  --out {{WORK_DIR}}/claims.json
```

`claims.json` の形式:

```json
{
  "scope": "high_risk",
  "claims": [
    {
      "claim_id": "c001",
      "data_file": "data_12_market_share.json",
      "json_path": "$.shares[0].value",
      "claim_text": "A社 国内シェア 32%",
      "claim_type": "numeric_share",
      "context_hint": "2024年度・国内・ソフトウェア業界"
    }
  ]
}
```

抽出ルールは `extract_claims.py` に実装されているが、概要は:
- **numeric**: 数値＋単位（%, 億円, 兆円, 人, 年）を含むリーフ値
- **date**: `YYYY`/`YYYY年`/`YYYY/MM`/`YYYY-MM-DD` 形式
- **proper_noun**: 企業名の典型パターン（株式会社〜 / 〜Corporation / 〜Inc.）
- `scope=all` のときは上記に加え、テキストフィールドの主張文（句読点を含む10文字以上の文字列）も対象

### Step 2: 裏取り検索（Claude本体）

`claims.json` の各 `claim` に対して、Claude が **WebSearch** を実行する。

#### 検索クエリの組み立て指針

- 数値系: `"<target_company> <metric_name> <year>"` を基本形とし、一次情報（IR・有報・公式統計）を優先
- 日付系: 公式沿革 / 有価証券報告書の歴史欄 / 信頼できるビジネス記事
- 固有名詞系: 公式HP、または官報・登記情報に類する一次情報

#### 判定ルール

| `verification_result` | 条件 |
|---|---|
| `confirmed` | 複数の独立ソースで裏付け済み |
| `single_source` | 1ソースのみで裏付け。追加ソースなし |
| `discrepancy` | 信頼できるソースと数値・内容が食い違う |
| `not_found` | どのソースにも該当情報が見つからない |
| `stale` | 情報は存在するが、より新しい数値がある |

#### 重要度付け

- `severity=high`: `discrepancy` または `stale`（差が20%以上または年度が2年以上ズレている）
- `severity=medium`: `not_found`、または `single_source` かつ一次情報でない
- `severity=low`: `single_source` で一次情報、または `confirmed` だが出典が曖昧

### Step 3: レポート出力

`{{WORK_DIR}}/fact_check_report.json` に以下の形式で書き出す:

```json
{
  "overall_verdict": "pass",
  "scope": "high_risk",
  "claims_checked": 47,
  "claims_flagged": 3,
  "flags": [
    {
      "claim_id": "c012",
      "slide_number": 12,
      "data_file": "data_12_market_share.json",
      "json_path": "$.shares[0].value",
      "claim": "A社の国内シェア 32%（2024年）",
      "original_source": "矢野経済（会話内で引用）",
      "verification_result": "discrepancy",
      "verification_note": "富士経済2024年版では A社シェア 28%。矢野経済の該当レポートが特定できず",
      "sources_checked": [
        {"url": "...", "title": "...", "value_found": "28%"},
        {"url": "...", "title": "...", "value_found": "not mentioned"}
      ],
      "severity": "high",
      "recommended_action": "user_confirm"
    }
  ]
}
```

- `overall_verdict`:
  - `pass`: `claims_flagged == 0`、または `severity=high` がゼロ
  - `needs_user_review`: `severity=high` が1件以上
  - `skipped`: `scope=skip` のとき

### Step 4: ユーザー向けMarkdownサマリ

標準出力に以下を表示:

```markdown
## ファクトチェック結果（scope: <scope>）

- **総合判定**: pass / needs_user_review / skipped
- **検証件数**: NN
- **フラグ件数**: NN（high=N, medium=N, low=N）

### 要確認項目（high）

| # | データファイル | 主張 | 検証結果 | メモ |
|---|---|---|---|---|

（表は `flags` の high のみ抽出）

レポート全文: `{{WORK_DIR}}/fact_check_report.json`

**次のアクション**: `strategy-report-agent` の Step 3 へ進む前に、上記 high 項目の扱いを確認してください
（修正してJSONを直す / ソースを追加する / 該当スライドをスキップする）。
```

---

## 単独起動時のフロー

`strategy-report-agent` を経由せず任意の JSON 群に対して呼び出された場合:

1. ユーザーから `data_dir` を受け取る
2. スコープはデフォルト `high_risk`（ユーザーが明示しなければ）
3. Step 1 → Step 2 → Step 3 → Step 4

---

## 出力先

- 抽出結果: `{{WORK_DIR}}/claims.json`
- レポート: `{{WORK_DIR}}/fact_check_report.json`

---

## 制約・留意事項

- **有料レポートの一次情報（矢野経済・富士経済・MMR等）はWeb検索で確認困難**。この場合は
  `not_found` としフラグし、ユーザーに一次情報アクセスを確認してもらう
- **時系列の新旧判定**は基準年を `target_company` の直近決算年度とする（ない場合は現在年）
- **裏取りに使う検索回数**は claim 1件あたり 1〜2 回まで。無駄な検索は避ける
- 本スキルは**断定しない**。疑わしい主張をフラグするだけで、修正判断はユーザーとオーケストレーターに委ねる
