---
name: smallcap-strategy-summary-pptx
description: >
  smallcap-strategy-research スキル専用の戦略仮説サマリースライド生成スキル。
  Where to play / How to win / Capability & Resource / Aspiration & Trajectory の4次元を
  2×2グリッドカードで1枚のスライドに俯瞰表示する。
  Phase 3.4-a で pyramid-structure-pptx の代替として導入。
  各カードは次元名 + 1-2行 hypothesis サマリー + confidence バッジ + 詳細ページ番号で構成され、
  読み手は4次元の戦略骨子を1枚で把握した後、各次元の詳細ページに進める階層構造を実現する。
  HTML→Playwright スクリーンショット方式で生成。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - smallcap-strategy-research のオーケストレーターから呼び出された場合
  - 「戦略仮説サマリー」「4次元戦略カード」「strategy summary」という言葉が出た場合
  - BDD/M&Aデューデリジェンス文脈で4次元戦略仮説の俯瞰スライドを求められた場合
---

# smallcap-strategy-summary-pptx — 戦略仮説サマリーカード（4次元俯瞰）

## 用途

- BDD調査の戦略仮説章の冒頭に配置し、Where to play / How to win / Capability & Resource / Aspiration & Trajectory の4次元を1枚で俯瞰
- 読み手は本スライドで戦略骨子を把握 → 各次元の詳細ページ（`smallcap-where-to-play-pptx` 等）へ進む階層構造

## 入力 JSON スキーマ

```json
{
  "main_message": "<= 100字、4次元統合の全体結論（v5.0ルールで『〜すべき』禁止）",
  "chart_title": "戦略仮説：<対象会社名>の戦い方",
  "dimensions": [
    {
      "key": "where_to_play",
      "label": "Where to play",
      "summary": "1-2行 hypothesis 圧縮（80-150字）",
      "confidence": "high | medium | low",
      "detail_page": 9
    },
    {"key": "how_to_win", "label": "How to win", "summary": "...", "confidence": "medium", "detail_page": 12},
    {"key": "capability_resource", "label": "Capability & Resource", "summary": "...", "confidence": "medium", "detail_page": null},
    {"key": "aspiration_trajectory", "label": "Aspiration & Trajectory", "summary": "...", "confidence": "medium", "detail_page": null}
  ],
  "source": "出典：BDD調査、Web公開情報のみ（YYYY年MM月）"
}
```

### フィールド仕様

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `main_message` | string | ✓ | 全体結論（最大100字、「〜すべき」禁止） |
| `chart_title` | string | 任意 | チャートタイトル。デフォルト「戦略仮説：戦い方」 |
| `dimensions` | array | ✓ | 4次元固定（順序: where_to_play / how_to_win / capability_resource / aspiration_trajectory） |
| `dimensions[].key` | string | ✓ | 次元キー（4種固定） |
| `dimensions[].label` | string | ✓ | 表示ラベル |
| `dimensions[].summary` | string | ✓ | 80-150字の hypothesis サマリー |
| `dimensions[].confidence` | string | ✓ | `high` / `medium` / `low` |
| `dimensions[].detail_page` | int / null | 任意 | 詳細スライドのページ番号。null なら「詳細ページ準備中」と表示 |
| `source` | string | 任意 | 出典 |

## レイアウト

- 上1/8: Main message（28pt Bold）
- 中央6/8: 2×2グリッドの4次元カード（各カード: 次元ラベル / summary / confidence バッジ / 詳細ページ番号 or「準備中」）
- 下1/8: Source（10pt）

confidence バッジ色:
- `high` → 緑系（#52C41A）
- `medium` → 黄系（#FAAD14）
- `low` → 赤系（#FF4D4F）

## スクリプト実行

```bash
python3 {{SKILL_DIR}}/scripts/fill_strategy_summary.py \
  --data {{WORK_DIR}}/strategy_summary_data.json \
  --template {{SKILL_DIR}}/assets/strategy-summary-template.pptx \
  --output {{OUTPUT_DIR}}/StrategySummary_output.pptx
```

## アセット

| ファイル | 用途 |
|---|---|
| `assets/strategy-summary-template.pptx` | 1スライドのPPTXテンプレ（Title 1 / Text Placeholder 2 / Rectangle 4 / Source） |
| `scripts/fill_strategy_summary.py` | HTML生成→Playwright→PPTX出力 |
| `references/sample_data.json` | 能作のサンプルデータ |
