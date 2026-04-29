---
name: visual-quality-reviewer
description: >
  PowerPointデッキのビジュアル品質を戦略コンサルタントの基準でレビューするスキル。
  マージ済みPPTX（または個別スライドPPTX）をスライド単位でPNG画像に変換し、
  文字溢れ・要素の重なり・配色崩れ・中扉の密度過多・チャート数値の可読性・マージン崩れ等を
  チェックリストに沿って目視評価し、不備のあるスライドと再生成ヒントをJSONレポートとして返す。
  `strategy-report-agent` のマージ後フェーズで呼び出されることを主用途とするが、
  任意のPPTXに対して単独でも起動できる。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - 「ビジュアルレビュー」「ビジュアル品質レビュー」「visual review」「visual quality」という言葉が出た場合
  - 「PPTが崩れていないかチェック」「スライドの見た目を確認」「コンサル品質でレビュー」という要望
  - `strategy-report-agent` のマージ後フェーズから呼び出される場合
  - 任意の `.pptx` に対する品質チェック要望
---

# Visual Quality Reviewer

PowerPointデッキのビジュアル品質を、戦略コンサルティングファームのデリバリー基準で評価するレビュアー。

**出力はPPTXではなくJSONレポート**（`visual_review_report.json`）。オーケストレーターが
このレポートを読み取り、必要に応じて該当スライドの再生成を判断する。

---

## 前提

- **実行主体**: Claude 本体。本スキルの Python スクリプトは画像化とコンテキスト収集のみを担い、
  **ビジュアル判定そのものは Claude が multimodal 能力で行う**（Read ツールで PNG を直接参照）
- **依存**: LibreOffice（`soffice` コマンド）が PATH にあること。`troubleshooting-pptx-repair.md` で使われている経路と同じ
- **作業ディレクトリ**: `{{WORK_DIR}}/`

---

## 入力

オーケストレーター側から本スキルへの入力（パラメータ）。各パラメータがどのスクリプトに渡されるかを明記:

| 項目 | 形式 | 必須 | 渡し先スクリプト | 説明 |
|---|---|---|---|---|
| `merged_pptx` | ファイルパス | 必須 | `render_pptx.py` (`--pptx`) | レビュー対象の PPTX（通常は `StrategyReport_*.pptx`） |
| `merge_order` | JSONパス | 任意 | **`collect_context.py` (`--merge-order`)** | Step 最終-1 で作成される `merge_order.json`（スライド番号 ↔ ファイル名の対応表）|
| `data_dir` | ディレクトリ | 任意 | **`collect_context.py` (`--data-dir`)** | `data_NN_*.json` 群の配置場所。与えられた場合、スライド番号とJSONを紐づけてコンテキストに含める |

**スクリプト構成**: 本スキルは 2 つのスクリプトを別々に呼び分ける設計:
- `render_pptx.py`: `--pptx` / `--out-dir` / `--dpi` のみ受け取る（PNG 化専用）
- `collect_context.py`: `--merge-order` / `--data-dir` / `--out` を受け取る（context.json 構築専用）

`merge_order` / `data_dir` は **`render_pptx.py` には渡さない**（CLI 引数として受け付けない）。

---

## 処理フロー

### Step 1: スライド画像化

```bash
{{PYTHON_BIN}} {{SKILL_DIR}}/scripts/render_pptx.py \
  --pptx <merged_pptx> \
  --out-dir {{WORK_DIR}}/pages
```

LibreOffice で PPTX → PDF → PNG（200 DPI, スライドごと `page_NN.png`）に変換する。
DPI 200 はフォント可読性の確保が目的（v0.1 で 150 だと小フォント誤検出が発生したため引き上げ）。

### Step 2: コンテキスト収集（任意）

`data_dir` と `merge_order` が与えられた場合:

```bash
{{PYTHON_BIN}} {{SKILL_DIR}}/scripts/collect_context.py \
  --merge-order <merge_order_json> \
  --data-dir <data_dir> \
  --out {{WORK_DIR}}/context.json
```

`context.json` はスライド番号 → `{file_name, skill_name, data_file, data_preview}` のマップ。
後続の判定ステップで「どの data を直せば再生成できるか」のヒント出力に使用する。

### Step 3: 目視レビュー（Claude本体）

`{{WORK_DIR}}/pages/page_NN.png` を `Read` ツールで**順番に全ページ**参照し、以下のチェックリストに
沿って不備を洗い出す。

#### チェックリスト（重要度付き）

| # | 観点 | 説明 | 標準 severity |
|---|---|---|---|
| 1 | **text_overflow** | テキストボックス枠外へのはみ出し、セル内テキストの上下切れ | high |
| 2 | **overlap** | 図形・テキスト・チャートの意図しない重なり | high |
| 3 | **chart_readability** | チャートの軸ラベル・凡例・データラベルが潰れて読めない、数値が重なって判読不能 | high |
| 4 | **density** | 中扉（section-divider）スライドにコンテンツが詰め込まれすぎ。本来は大きな番号＋タイトル＋トピックの3要素のみ | high |
| 5 | **alignment** | 左右マージン崩れ、複数カラムの縦軸ズレ、ブレットインデント崩れ | medium |
| 6 | **color** | ブランドパレット逸脱（本デッキは Accent2 系）。意味を持たない色の乱用 | medium |
| 7 | **typography** | フォントサイズの極端な不統一、タイトル階層の逆転、日本語フォントの英字化け | medium |
| 8 | **brand** | ロゴ位置、ヘッダー／フッター欠落、ページ番号の欠落 | low |

#### 判定基準

- **pass**: `high` issue 0 件、`medium` issue 3 件以下、`low` は無制限
- **needs_fixes**: `high` issue が 1 件以上、または `medium` 4 件以上
- **reject**: スライド半数以上で `high` issue（通常は発生しない。LibreOffice レンダリング失敗を疑う）

#### `regeneration_hint` の書き方

- 該当スライドが特定可能で、かつ `context.json` から `data_file` と `skill_name` が取れる場合のみ書く
- 「どのJSONフィールドをどう変えれば直るか」をオーケストレーターが機械的に解釈できるレベルまで具体化する
  - 良い例: `"data_07_pest.json の factors[2].bullets を3項目 → 2項目に短縮。長い方を要約"`
  - 悪い例: `"内容を減らす"`

### Step 4: レポート出力

`{{WORK_DIR}}/visual_review_report.json` に以下の形式で書き出す:

```json
{
  "overall_verdict": "pass",
  "total_slides": 22,
  "issues_count_by_severity": {"high": 0, "medium": 2, "low": 5},
  "issues": [
    {
      "slide_number": 7,
      "file_name": "slide_07_section2_external.pptx",
      "skill_name": "pest-analysis-pptx",
      "data_file": "data_07_pest.json",
      "severity": "high",
      "category": "text_overflow",
      "description": "右下象限 'Technological' の bullets[2] が枠外にはみ出している",
      "recommended_action": "regenerate",
      "regeneration_hint": "data_07_pest.json の factors[3].bullets[2] を40文字以内に要約"
    }
  ]
}
```

### Step 5: 結果のMarkdownサマリ

オーケストレーターに返す最終出力として、以下のMarkdownを標準出力に表示する:

```markdown
## ビジュアル品質レビュー結果

- **総合判定**: pass / needs_fixes / reject
- **総スライド数**: NN
- **重大度別件数**: high=N, medium=N, low=N

### 要修正スライド（high）

| 通し番号 | スキル | カテゴリ | 概要 | 再生成ヒント |
|---|---|---|---|---|

（表は `issues` の high のみ抽出）

レポート全文: `{{WORK_DIR}}/visual_review_report.json`
```

---

## 単独起動時のフロー

`strategy-report-agent` を経由せず、任意の PPTX に対して呼び出された場合:

1. ユーザーから対象 PPTX のパスを受け取る（`merge_order` / `data_dir` は無し）
2. Step 1（画像化）→ Step 3（目視レビュー）→ Step 4（レポート出力）→ Step 5（Markdown）
3. この場合 `regeneration_hint` は空欄または「手動修正を推奨」の文言になる

---

## 出力先

- 中間画像: `{{WORK_DIR}}/pages/page_NN.png`
- コンテキスト: `{{WORK_DIR}}/context.json`（ある場合のみ）
- レポート: `{{WORK_DIR}}/visual_review_report.json`

---

## 制約・留意事項

- LibreOffice のレンダリング結果は PowerPoint と完全一致しない場合がある（フォント代替等）。
  日本語フォント未インストール環境では「フォント代替に起因する見た目の崩れ」を誤検出しないよう、
  **フォント字形そのもの**より **配置・密度・はみ出し**を優先的に評価する
- 1スライドあたりの画像は最大 2MB を想定。それ以上は DPI を 100 に落とす
- `high` issue が同じスライドで複数検出された場合も `issues[]` には個別エントリとして列挙する
