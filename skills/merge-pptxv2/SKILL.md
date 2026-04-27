---
name: merge-pptxv2
description: |
  複数のPowerPointファイル（.pptx）を1つのプレゼンテーションに結合するスキル（v2）。
  v1のmerge-pptxから以下の重大なバグを修正した改良版：
  (1) チャートの_relsファイル（ppt/charts/_rels/）が正しくコピーされるようになった
  (2) Excelデータファイル（.xlsx）がマージ先に正しく含まれるようになった
  (3) Content-Typeデフォルト（.png, .xlsx, .bin等）が全て正しく登録されるようになった
  (4) チャート→Excel→スライドの参照チェーン全体が正しく維持されるようになった
  これにより、チャート付きスライド（customer-profile-pptx等）や画像付きスライド
  （customer-sales-detail-pptx等）を結合してもPowerPointで正しく表示される。
  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - 同一会話内で複数のPPTXスキルを使ってスライドを作成した直後
  - 「スライドを結合して」「PPTXをまとめて」「1つのファイルにして」「デッキにまとめて」「結合」「マージ」という言葉が出た場合
  - 「全部つなげて」「1つのプレゼンにして」「まとめてダウンロードしたい」という要望
  - 複数のPPTXファイルがoutputsディレクトリにある状態で、ユーザーがそれらをまとめたいと示唆した場合
  - BDDレポートや提案書など、複数スライドで構成される資料を一括作成した後
  重要: 同一会話で2つ以上のPPTXスキルを実行した場合、最後のスライド作成完了後に「これらのスライドを1つのファイルに結合しますか？」と自動的に提案すること。
  重要: merge-pptx（v1）が存在する場合でも、このv2を優先的に使用すること。v1にはチャート・画像の結合に関する既知のバグがある。
---

# Merge PPTX Skill v2

複数のPowerPointファイルを1つに結合するスキル。
v1のmerge-pptxの重大なバグ（チャートrels・Excelデータ・Content-Type欠落）を修正した改良版。

---

## v1からの主な修正点

| 問題 | v1の挙動 | v2の修正 |
|------|---------|---------|
| チャート_rels | `ppt/charts/_rels/`がコピーされない | チャートXMLと同時に_relsもコピー・リネーム |
| Excelデータ | `.xlsx`埋め込みファイルがコピーされない | embeddings内のxlsxファイルも正しくコピー |
| Content-Type | `.png`, `.xlsx`, `.bin`のDefault定義が欠落 | アーカイブ内の全拡張子を走査し自動登録 |
| 結果 | スライド4以降が空白表示 | 全スライドが正常表示 |

---

## ワークフロー

### Step 1: 結合対象のファイルを特定する

```bash
echo "=== Outputs ===" && ls -lt {{OUTPUT_DIR}}/*.pptx 2>/dev/null
echo "=== Working ===" && ls -lt {{WORK_DIR}}/*.pptx 2>/dev/null
```

### Step 2: ユーザーに順番を確認する

番号付きのファイル一覧を提示し、並び順を確認する。

### Step 3: ファイル名を自動決定する

- BDD関連: `BDD_Report_[対象会社名].pptx`
- 提案書: `Proposal_[プロジェクト名].pptx`
- その他: `Merged_Presentation_[YYYYMMDD].pptx`

### Step 4: 結合を実行する

```bash
pip install lxml --break-system-packages -q

python <SKILL_DIR>/scripts/merge_pptx_v2.py \
  [--no-roundtrip] [--merge-order <merge_order.json>] \
  {{OUTPUT_DIR}}/[output_filename].pptx \
  [input1.pptx] [input2.pptx] [input3.pptx] ...
```

引数:
1. 位置引数1: 出力ファイルパス
2. 位置引数2以降: 入力ファイル（順番通りに並べる）

オプション:
- `--no-roundtrip`: LibreOffice 経由の OOXML 正規化をスキップする
- `--merge-order <path>`: `merge_order.json` を読み込み、`section_divider` の直後に
  `content` が連続することを検証する（後述のスキーマを参照）。違反は警告として
  `merge_warnings.json` に記録され、マージ自体は継続される

### Step 5: QA

スクリプトが自動で検証結果を出力する（スライド数・シェイプ数・参照整合性）。
`--merge-order` を指定した場合は `section_divider` 位置検証の結果も併せて出力される。

### Step 6: ユーザーに提供する

`present_files`ツールでファイルを提供。枚数と順番を簡潔に報告。

---

## 自動提案のタイミング

同一会話で2つ以上のPPTX生成スキルを使用した場合、最後のスキル実行完了後に結合を提案する。

## 注意事項

- 各スライドのデザイン・テーマ・フォントはソースファイルのものが保持される
- 表紙や目次は自動生成しない（純粋な結合のみ）
- 結合元の個別ファイルはそのまま残る（削除しない）
- lxml が必要（初回実行時に`pip install lxml --break-system-packages -q`）

---

## merge_order.json 入力規約（`--merge-order` 用）

オーケストレーター（market-overview-agent / strategy-report-agent / smallcap-strategy-research）が
出力する `merge_order.json` を読み込み、デッキ構造の妥当性を検証する。

### 必須フィールド

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

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `slide_number` | int | ✓ | 通し番号（1始まり）。`merge_warnings.json` の `slide_index` に転写される |
| `file_name` | str | ✓ | 個別 PPTX のファイル名（参考情報・本検証では未使用） |
| `skill_name` | str | ✓ | 生成元スキル名（参考情報・本検証では未使用） |
| `data_file` | str | ✓ | 入力 JSON 名（参考情報・本検証では未使用） |
| `category` | str | ✓ | `header` / `content` / `section_divider` / `footer` のいずれか |

### `category` 値域

| 値 | 用途 |
|---|---|
| `header` | エグゼクティブサマリー・目次など、セクション開始前の冒頭スライド |
| `content` | 通常のコンテンツスライド（チャート・テーブル・分析） |
| `section_divider` | 中扉（セクション区切り） |
| `footer` | データアベイラビリティ・付録など、末尾スライド |

正規スキーマ: `skills/market-overview-agent/references/deck_skeleton_standard.json`

---

## merge_warnings.json 出力スキーマ

`--merge-order` 指定時、出力 PPTX と同じディレクトリに **常に** 書き出される
（違反ゼロの場合は空配列 `[]`）。下流の `visual-quality-reviewer` がこのファイルの
存在を前提に挙動を分岐できる。

```json
[
  {
    "slide_index": 5,
    "type": "section_divider_position",
    "message": "slide 5 (section_divider) is followed by slide 6 (category='section_divider'); expected category='content'."
  }
]
```

| フィールド | 型 | 説明 |
|---|---|---|
| `slide_index` | int | 違反した `section_divider` の `slide_number` |
| `type` | str | 警告種別。現在は `section_divider_position` のみ |
| `message` | str | 人間可読な違反内容 |

### 検証ルール: `section_divider_position`

`category=section_divider` の **直後** のエントリは `category=content` でなければならない。
中扉の連続、中扉直後の `header` / `footer`、中扉が末尾エントリ、いずれも警告対象。

警告は `ValueError` を投げず、マージは正常完了する。
