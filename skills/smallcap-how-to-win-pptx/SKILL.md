---
name: smallcap-how-to-win-pptx
description: >
  smallcap-strategy-research スキル専用の How to win（差別化軸・戦い方）詳細スライド生成スキル。
  1つのJSONから3スライド（Main / Detail / Evidence）を出力する。
  Main page は Main message + コア narrative + 価値連鎖の進化フロー（横軸タイムライン + 各ステージの profit pool size を縦棒可視化） + 3行 Evidence summary。
  Detail page は narrative_full（500字以上） + Sub-arguments 3-5個 + Caveats。
  Evidence page は finding 4件以上のテーブル + triangulation note + 関連 data gaps。
  Phase 3.4-a で導入。HTML→Playwright スクリーンショット方式で生成。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - smallcap-strategy-research のオーケストレーターから呼び出された場合
  - 「How to win」「差別化軸」「価値連鎖の進化」「価値連鎖フロー」という言葉が出た場合
  - BDD/M&Aデューデリジェンス文脈で対象会社のHow to win詳細スライド3枚セットを求められた場合
---

# smallcap-how-to-win-pptx — How to win 詳細（Main/Detail/Evidence 3スライド）

## 用途

- BDD調査の「How to win」次元を 3 ページ展開で深掘り表示
- Main：1枚で結論と価値連鎖進化フローを伝える
- Detail：narrative_full と sub-arguments で論拠を展開
- Evidence：根拠 finding を表組みで全件提示

## 入力 JSON スキーマ

`smallcap-where-to-play-pptx` と **共通形**。違いは `main.visual_data` のみ:

```json
{
  "main": {
    "main_message": "<= 100字、How to win の結論",
    "narrative_short": "300字以上",
    "evidence_summary_3lines": ["...", "...", "..."],
    "visual_data": {
      "stages": [
        {"label": "OEM下請", "year_range": "1916-2002", "profit_pool": 1, "color": "#999", "note": ""},
        {"label": "自社ブランド転換", "year_range": "2002-2017", "profit_pool": 4, "color": "#5B8FF9"},
        {"label": "産業観光統合", "year_range": "2017-現在", "profit_pool": 8, "color": "#1565C0"},
        {"label": "海外BtoC", "year_range": "2025-", "profit_pool": null, "color": "#FFA940", "note": "拡大中・採算未確認"}
      ]
    }
  },
  "detail": { /* where-to-play と同形式 */ },
  "evidence": { /* where-to-play と同形式 */ },
  "source": "..."
}
```

`profit_pool: null` のステージは「採算未確認」として薄色＋斜線で描画される。

### 必須要件（v5.0 知的誠実性）

| 項目 | 制約 |
|---|---|
| `main.narrative_short` | **200字以上**（Phase 3.2b 逆戻り防止） |
| `detail.narrative_full` | **500字以上**（Phase 3.2b 逆戻り防止） |
| `detail.sub_arguments[]` | **3個以上** |
| `evidence.findings[]` | **4個以上** |
| `detail.caveats[]` | **1個以上** |
| `main_message` | 「〜すべき」禁止 |
| `visual_data.stages[]` | **3〜6 ステージ**を推奨 |

## レイアウト

### Main page (slide 1/3)
- 上 1/8: Main message
- 中央左 1/2: narrative_short
- 中央右 1/2: 価値連鎖進化フロー SVG（X軸=タイムライン、各ステージのラベル+年範囲+profit_pool 縦棒）
- 下 1/8: Evidence summary 3行

### Detail / Evidence page
- where-to-play と同形式

## スクリプト実行

```bash
python3 {{SKILL_DIR}}/scripts/fill_how_to_win.py \
  --data {{WORK_DIR}}/how_to_win_data.json \
  --template {{SKILL_DIR}}/assets/how-to-win-template.pptx \
  --output {{OUTPUT_DIR}}/HowToWin_output.pptx
```

出力 PPTX は **3 スライド構成**。
