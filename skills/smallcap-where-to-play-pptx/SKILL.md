---
name: smallcap-where-to-play-pptx
description: >
  smallcap-strategy-research スキル専用の Where to play（事業領域・顧客・地域の選択）詳細スライド生成スキル。
  1つのJSONから3スライド（Main / Detail / Evidence）を出力する。
  Main page は Main message + コア narrative + 事業領域マップ（X=BtoB↔BtoC、Y=国内↔海外の2軸バブル配置） + 3行 Evidence summary。
  Detail page は narrative_full（500字以上） + Sub-arguments 3-5個 + Caveats。
  Evidence page は finding 4件以上のテーブル + triangulation note + 関連 data gaps。
  Phase 3.4-a で導入。HTML→Playwright スクリーンショット方式で生成。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - smallcap-strategy-research のオーケストレーターから呼び出された場合
  - 「Where to play」「事業領域マップ」「事業領域・顧客・地域の選択」という言葉が出た場合
  - BDD/M&Aデューデリジェンス文脈で対象会社のWhere to play詳細スライド3枚セットを求められた場合
---

# smallcap-where-to-play-pptx — Where to play 詳細（Main/Detail/Evidence 3スライド）

## 用途

- BDD調査の「Where to play」次元を 3 ページ展開で深掘り表示
- Main：1枚で結論と事業領域マップを伝える
- Detail：narrative_full と sub-arguments で論拠を展開
- Evidence：根拠 finding を表組みで全件提示

## 入力 JSON スキーマ

```json
{
  "main": {
    "main_message": "<= 100字、Where to play の結論",
    "narrative_short": "300字以上、hypothesis 原文の論理を保持",
    "evidence_summary_3lines": ["...", "...", "..."],
    "visual_data": {
      "x_axis_label": "顧客タイプ",
      "x_axis_left": "BtoB",
      "x_axis_right": "BtoC",
      "y_axis_label": "地理",
      "y_axis_bottom": "国内",
      "y_axis_top": "海外",
      "segments": [
        {"name": "国内BtoC雑貨", "x": 0.85, "y": 0.2, "size": 12, "highlight": true, "note": "プレミアム生活雑貨"},
        {"name": "産業観光", "x": 0.7, "y": 0.15, "size": 8, "highlight": true},
        {"name": "海外BtoC", "x": 0.85, "y": 0.85, "size": 6, "highlight": true},
        {"name": "医療[縮退]", "x": 0.15, "y": 0.2, "size": 2, "highlight": false, "note": "縮退中"}
      ]
    }
  },
  "detail": {
    "subtitle": "Where to play：詳細論点",
    "narrative_full": "500字以上、原文の論点を省略禁止",
    "sub_arguments": [
      {"heading": "...", "body": "200-300字"}
    ],
    "caveats": ["...", "..."]
  },
  "evidence": {
    "findings": [
      {"id": "F1", "agent": "...", "metric": "...", "source": "...",
       "source_type": "...", "confidence": "...", "excerpt": "..."}
    ],
    "triangulation_note": "...",
    "related_data_gaps": ["...", "..."]
  },
  "source": "出典：BDD調査、Web公開情報のみ（YYYY年MM月）"
}
```

### 必須要件（v5.0 知的誠実性）

| 項目 | 制約 |
|---|---|
| `main.narrative_short` | **200字以上**（Phase 3.2b 逆戻り防止） |
| `detail.narrative_full` | **500字以上**（Phase 3.2b 逆戻り防止） |
| `detail.sub_arguments[]` | **3個以上** |
| `evidence.findings[]` | **4個以上** |
| `detail.caveats[]` | **1個以上** |
| `main_message` | 「〜すべき」禁止（事実型「〜である」「〜と推定される」で締める） |

## レイアウト（HTML→Playwright）

### Main page (slide 1/3)
- 上 1/8: Main message（28pt Bold）
- 中央左 1/2: narrative_short（17pt 段落）
- 中央右 1/2: 事業領域マップ SVG（X=BtoB↔BtoC、Y=国内↔海外、バブルサイズ=segments[].size、ハイライト=濃色＋太字、非ハイライト=薄色＋斜線）
- 下 1/8: Evidence summary 3行（小さめテキスト、F# 付き）

### Detail page (slide 2/3)
- 上 1/8: subtitle
- 中央: narrative_full + sub_arguments（カード3-5個、heading 太字＋body 段落）
- 下 1/8: Caveats 注記（薄黄色背景）

### Evidence page (slide 3/3)
- 上 1/8: 「Evidence Trail：Where to play」
- 中央左 2/3: findings テーブル（F# / Agent / Metric / Source / Type / Confidence / Excerpt の 7 列）
- 中央右 1/3: triangulation_note + related_data_gaps

## スクリプト実行

```bash
python3 {{SKILL_DIR}}/scripts/fill_where_to_play.py \
  --data {{WORK_DIR}}/where_to_play_data.json \
  --template {{SKILL_DIR}}/assets/where-to-play-template.pptx \
  --output {{OUTPUT_DIR}}/WhereToPlay_output.pptx
```

出力 PPTX は **3 スライド構成**。

## アセット

| ファイル | 用途 |
|---|---|
| `assets/where-to-play-template.pptx` | 1スライドのPPTXテンプレ（fill 内で dup_slide で 3 枚に展開） |
| `scripts/fill_where_to_play.py` | HTML×3生成→Playwright×3スクショ→PPTX 3スライド出力 |
| `references/sample_data.json` | 能作のサンプルデータ |
