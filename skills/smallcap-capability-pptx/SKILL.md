---
name: smallcap-capability-pptx
description: >
  smallcap-strategy-research スキル専用の Capability & Resource（ケイパビリティ・資源配分）詳細スライド生成スキル。
  1つのJSONから3スライド（Main / Detail / Evidence）を出力する。
  Main page は メッセージ + タイトル + 意味合い 3 点 + ケイパビリティ・レーダーチャート（6軸：製造力／意匠力／ブランド力／投資体力／海外販路／DX力 等のカスタム軸）。
  Detail page は ケイパビリティ別の構造化マトリクス。
  Evidence page は メッセージ + タイトル + findings 一覧表（フルワイド）。
  Phase 3.4-b で導入。HTML→Playwright スクリーンショット方式で生成。

  以下のいずれかのトリガーで必ずこのスキルを使うこと：
  - smallcap-strategy-research のオーケストレーターから呼び出された場合
  - 「Capability」「ケイパビリティ」「資源配分」「Capability & Resource」「ケイパビリティ・レーダー」という言葉が出た場合
  - BDD/M&Aデューデリジェンス文脈で対象会社の Capability 詳細スライド3枚セットを求められた場合
---

# smallcap-capability-pptx — Capability & Resource 詳細（Main/Detail/Evidence 3スライド）

## レイアウト（business-model-template ベース）

各スライド共通:
- `Title 1` (PPTX native): Main Message
- `Text Placeholder 2` (PPTX native): Chart Title
- `TextBox 9` (PPTX native, Main/Detail): 意味合い 3 点（Evidence では使わない）
- `Rectangle 4` (image area): HTML キャプチャ画像（Evidence は TextBox 9 領域も覆ってフルワイド）

## 入力 JSON スキーマ

```json
{
  "main": {
    "main_message": "<= 100字、Capability の結論",
    "chart_title": "Capability & Resource：ケイパビリティ・レーダー（1/3）",
    "implications": [{"label": "...", "detail": "..."}, ...3個],
    "visual_data": {
      "axes": ["製造力", "意匠力", "ブランド力", "投資体力", "海外販路", "DX力"],
      "scores": [9, 9, 9, 7, 6, 3],
      "max_score": 10
    }
  },
  "detail": {
    "main_message": "...",
    "chart_title": "Capability & Resource：強み弱み詳細（2/3）",
    "implications": [{"label": "...", "detail": "..."}, ...3個],
    "visual_data": {
      "capabilities": [
        {"name": "製造力", "score": 9, "evidence": "...", "level": "高"}
      ]
    }
  },
  "evidence": {
    "main_message": "...",
    "chart_title": "Capability & Resource：根拠 finding 一覧（3/3）",
    "findings": [{"id": "F1", "agent": "...", "source": "...", "source_type": "...", "confidence": "...", "excerpt": "..."}]
  }
}
```

## スクリプト

```bash
python3 {{SKILL_DIR}}/scripts/fill_capability.py \
  --data {{WORK_DIR}}/capability_data.json \
  --template {{SKILL_DIR}}/assets/capability-template.pptx \
  --output {{OUTPUT_DIR}}/Capability_output.pptx
```

出力 PPTX は **3 スライド構成**。
