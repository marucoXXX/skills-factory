---
name: smallcap-aspiration-pptx
description: >
  smallcap-strategy-research スキル専用の Aspiration & Trajectory（経営意図と時間軸）詳細スライド生成スキル。
  1つのJSONから3スライド（Main / Detail / Evidence）を出力する。
  Main page は メッセージ + タイトル + 意味合い 3 点 + 時間軸ロードマップ（過去-現在-将来のイベント配置）。
  Detail page はフェーズ別の構造化マトリクス（過去/現在/将来 × 戦略軸）。
  Evidence page は メッセージ + タイトル + findings 一覧表（フルワイド）。
  Phase 3.4-b で導入。HTML→Playwright スクリーンショット方式で生成。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - smallcap-strategy-research のオーケストレーターから呼び出された場合
  - 「Aspiration」「経営意図」「時間軸ロードマップ」「Aspiration & Trajectory」という言葉が出た場合
  - BDD/M&Aデューデリジェンス文脈で対象会社の Aspiration 詳細スライド3枚セットを求められた場合
---

# smallcap-aspiration-pptx — Aspiration & Trajectory 詳細（Main/Detail/Evidence 3スライド）

## レイアウト

各スライド共通（business-model-template ベース、Evidence はフルワイド）:
- `Title 1`: Main Message ← PPTX native
- `Text Placeholder 2`: Chart Title ← PPTX native
- `TextBox 9` (Main/Detail): 意味合い 3 点 ← PPTX native
- `Rectangle 4`: HTML キャプチャ画像

## 入力 JSON スキーマ

```json
{
  "main": {
    "main_message": "...",
    "chart_title": "Aspiration & Trajectory：時間軸ロードマップ（1/3）",
    "implications": [{"label": "...", "detail": "..."}, ...3個],
    "visual_data": {
      "milestones": [
        {"year": "2017年", "label": "本社新工場", "phase": "past", "note": "16億円投資"},
        {"year": "2022年", "label": "HD設立", "phase": "past"},
        {"year": "2023年", "label": "5代目承継", "phase": "past"},
        {"year": "2025年", "label": "東京・金沢展開", "phase": "current"},
        {"year": "2026年", "label": "ミラノ展", "phase": "current"},
        {"year": "2030年〜", "label": "海外BtoCスケール", "phase": "future", "note": "推定"}
      ]
    }
  },
  "detail": {
    "main_message": "...",
    "chart_title": "Aspiration & Trajectory：フェーズ別の戦略軸（2/3）",
    "implications": [{"label": "...", "detail": "..."}, ...3個],
    "visual_data": {
      "phases": [
        {"label": "過去（〜2023）", "color": "#999999", "actions": ["..."]},
        {"label": "現在（2024-2026）", "color": "#1565C0", "actions": ["..."]},
        {"label": "将来（2027〜、推定）", "color": "#FFA940", "actions": ["..."]}
      ]
    }
  },
  "evidence": {
    "main_message": "...",
    "chart_title": "Aspiration & Trajectory：根拠 finding 一覧（3/3）",
    "findings": [...]
  }
}
```

## スクリプト

```bash
python3 {{SKILL_DIR}}/scripts/fill_aspiration.py \
  --data {{WORK_DIR}}/aspiration_data.json \
  --template {{SKILL_DIR}}/assets/aspiration-template.pptx \
  --output {{OUTPUT_DIR}}/Aspiration_output.pptx
```

出力 PPTX は **3 スライド構成**。
