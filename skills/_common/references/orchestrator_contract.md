# Orchestrator Contract — オーケストレーター間の共通契約

> **このファイルは `skills/_common/references/orchestrator_contract.md` です。**
> オーケストレータースキル（market-overview-agent / strategy-report-agent / smallcap-strategy-research 等）の SKILL.md からは、`<!-- source: skills/_common/references/orchestrator_contract.md (manual sync until D2) -->` コメント付きで**手動コピペ**してください。
> このファイルを変更したら `grep -rn "source: skills/_common/references/orchestrator_contract.md" skills/*/SKILL.md` で被参照スキルを全て検出し、コピペし直すこと（ISSUE-001 D2 で自動化検討中）。

オーケストレーターと下流ツール（`merge-pptxv2` / `visual-quality-reviewer`）の間で
受け渡す中間ファイルの正規スキーマを定義する。本ファイルが不変点であり、
個別スキルは本ファイルに準拠した構造で出力すること。

---

## 1. `merge_order.json` — オーケストレーター → merge-pptxv2 / visual-quality-reviewer

### 配置

`{{WORK_DIR}}/<run_id>/merge_order.json`

### スキーマ

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

### フィールド定義

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `slide_number` | int | ✓ | 通し番号（1始まり）。`merge_warnings.json.slide_index` に転写される |
| `file_name` | str | ✓ | 個別 PPTX のファイル名（`{{WORK_DIR}}/<run_id>/` 配下） |
| `skill_name` | str | ✓ | 生成元スキル名。`visual-quality-reviewer` の自動修正ループが該当スキルの `fill_*.py` を再実行するために使う |
| `data_file` | str | ✓ | 入力 JSON のファイル名。自動修正ループで `regeneration_hint` に従って書き換える対象 |
| `category` | str | ✓ | デッキ内での役割。下記 4 値のいずれか |

### `category` の値域

| 値 | 用途 |
|---|---|
| `header` | エグゼクティブサマリー・目次など、セクション開始前の冒頭スライド |
| `content` | 通常のコンテンツスライド（チャート・テーブル・分析） |
| `section_divider` | 中扉（セクション区切り） |
| `footer` | データアベイラビリティ・付録など、末尾スライド |

正規ソース: `skills/market-overview-agent/references/deck_skeleton_standard.json`

### 検証ルール（merge-pptxv2 が assert）

- `category=section_divider` の **直後** のエントリは `category=content` でなければならない
  （中扉の連続、中扉直後の `header` / `footer`、中扉が末尾エントリは違反）
- 違反は `merge_warnings.json` に記録され、マージは継続する（`ValueError` を投げない）

---

## 2. `merge_warnings.json` — merge-pptxv2 → 下流（visual-quality-reviewer / ユーザー）

### 配置

出力 PPTX と同じディレクトリ（`{{OUTPUT_DIR}}/merge_warnings.json` または `{{WORK_DIR}}/<run_id>/merge_warnings.json`、merge-pptxv2 の第 1 引数で決まる）

### スキーマ

```json
[
  {
    "slide_index": 5,
    "type": "section_divider_position",
    "message": "slide 5 (section_divider) is followed by slide 6 (category='section_divider'); expected category='content'."
  }
]
```

### フィールド定義

| フィールド | 型 | 説明 |
|---|---|---|
| `slide_index` | int | 違反した `section_divider` の `slide_number`（merge_order.json から転写） |
| `type` | str | 警告種別。現在は `section_divider_position` のみ。将来追加される可能性あり |
| `message` | str | 人間可読な違反内容 |

### 重要な前提

- **常時書き出される**: `--merge-order` 指定時は違反 0 件でも `[]` で出力される
- 下流（visual-quality-reviewer 等）は本ファイルの**存在**を前提に分岐できる
- マージ自体は警告があっても継続する。警告を無視するか、JSON を修正して再生成するかはオーケストレーターの判断

---

## 3. `regeneration_hint` — visual-quality-reviewer → 自動修正ループ

### 配置

`visual_review_report.json.issues[i].regeneration_hint`（visual-quality-reviewer の出力内）

### スキーマ（参考）

```json
{
  "slide_number": 4,
  "skill_name": "market-environment-pptx",
  "data_file": "data_04_market_environment.json",
  "severity": "high",
  "category": "text_overflow",
  "issue_summary": "main_message が 80 字で 65 字制限を超過、テンプレ枠から溢れている",
  "regeneration_hint": {
    "field": "main_message",
    "action": "shorten_to",
    "max_chars": 65,
    "guidance": "主語を1つに絞る、修飾語を削除（『主要な』『重要な』等）、数値は1つだけ残す"
  }
}
```

### 自動修正ループでの使い方

1. `slide_number` から `merge_order.json.entries[].slide_number` を引いて該当エントリを特定
2. `data_file` を `{{WORK_DIR}}/<run_id>/<data_file>` から読み込み
3. `regeneration_hint.field` を `regeneration_hint.action` に従って書き換える
4. `skill_name` の `fill_*.py` を**同じ `file_name` 出力で**再実行
5. 全修正完了後、`merge-pptxv2 --merge-order` を再実行
6. `visual-quality-reviewer` を再起動して `severity=high` が 0 になるまで（最大 2 ラウンド）繰り返す

詳細は `skills/_common/prompts/step_final_visual_review_loop.md` を参照。

---

## 4. オーケストレーター実装時のチェックリスト

新規オーケストレーターを書く際 / 既存オーケストレーターを改修する際は、以下を満たすこと:

- [ ] `merge_order.json` を `{{WORK_DIR}}/<run_id>/` に書き出している
- [ ] `merge_order.json` の各 entry に `slide_number` / `file_name` / `skill_name` / `data_file` / `category` が揃っている
- [ ] `category` は `header` / `content` / `section_divider` / `footer` のいずれか
- [ ] `merge-pptxv2` を `--merge-order` 付きで起動している
- [ ] マージ後 `merge_warnings.json` を確認している（`section_divider_position` 違反 0 件）
- [ ] `visual-quality-reviewer` に `merge_order` パスを渡している
- [ ] 自動修正ループのカウンタを持っている（無限ループ防止、最大 2 ラウンド）
