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
echo "=== Outputs ===" && ls -lt /mnt/user-data/outputs/*.pptx 2>/dev/null
echo "=== Working ===" && ls -lt /home/claude/*.pptx 2>/dev/null
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
  /mnt/user-data/outputs/[output_filename].pptx \
  [input1.pptx] [input2.pptx] [input3.pptx] ...
```

引数:
1. 第1引数: 出力ファイルパス
2. 第2引数以降: 入力ファイル（順番通りに並べる）

### Step 5: QA

スクリプトが自動で検証結果を出力する（スライド数・シェイプ数・参照整合性）。

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
