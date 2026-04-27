# Step 0: 市場スコープ確認 プロンプト雛形

`market-overview-agent` の起動直後に AskUserQuestion で確定する4項目。

## 質問1: 地理スコープ

```
question: 「どの地理スコープで市場を分析しますか？」
header: "地理スコープ"
multiSelect: false
options:
  - label: "国内（日本）"
    description: "日本市場のみを対象とする。各社IR・矢野経済・富士経済の国内データを優先"
  - label: "グローバル"
    description: "全世界の市場を対象。IDC / Gartner / 業界団体のグローバル統計を優先"
  - label: "アジア・パシフィック"
    description: "APAC 地域を対象。日中韓・東南アジアの統計と各社IRをカバー"
  - label: "北米・欧州"
    description: "Western 主要市場。Gartner / Forrester / IDC のレポートを優先"
```

## 質問2: セグメント粒度

```
question: 「セグメントの粒度はどうしますか？」
header: "セグメント"
multiSelect: false
options:
  - label: "業界全体ザックリ（推奨）"
    description: "BtoB/BtoC・製品カテゴリ等で分けず、市場全体を1つの集合として扱う。10〜12枚デッキの標準"
  - label: "BtoB のみ"
    description: "BtoB セグメントに絞り込んで分析。BtoC のプレイヤー・データは除外する"
  - label: "BtoC のみ"
    description: "BtoC セグメントに絞り込んで分析。BtoB は除外する"
  - label: "特定セグメント名で絞る（自由記述）"
    description: "Other で具体名を入力（例: 「中小企業向けクラウドERP」「ハイクラス転職」「製造業向けIoT」）"
```

## 質問3: 分析年数

```
question: 「過去・将来それぞれ何年分を分析しますか？」
header: "分析年数"
multiSelect: false
options:
  - label: "過去5年＋今後5年（推奨）"
    description: "業界統計・IR が揃いやすく、CAGR の傾向が読み取りやすい標準レンジ"
  - label: "過去3年＋今後3年"
    description: "短期トレンド重視。直近の変化点（コロナ後等）を強調したい場合"
  - label: "過去10年＋今後10年"
    description: "中長期の構造変化を捉える。データソースが10年分揃わない場合は ✗/△ で明示"
```

## 質問4: 主要競合の上限

```
question: 「主要プレイヤーは何社まで取り上げますか？」
header: "競合数"
multiSelect: false
options:
  - label: "5社まで（推奨・全PPTXで統一）"
    description: "positioning-map / market-share / competitor-summary / market-kbf すべてで同じ5社を採用。スライド上の視認性も担保される"
  - label: "3社まで"
    description: "シェアトップ3に絞り込む。ロングテールの新興プレイヤーは扱わない"
  - label: "4社まで"
    description: "中程度の絞り込み"
```

## 結果の保存先

`{{WORK_DIR}}/<run_id>/scope.json` に保存（`run_id = <日付>_<スネークケース化した市場名>`）：

```json
{
  "market_name": "国内HR Tech市場",
  "geography": "国内",
  "segment": "業界全体",
  "analysis_years": { "past": 5, "future": 5 },
  "max_competitors": 5,
  "run_id": "2026-04-26_hr_tech",
  "started_at": "2026-04-26T22:30:00+09:00"
}
```

## 注意

- ユーザーが「6社以上を取り上げたい」とOther で指定した場合は、5社上限の設計理由（視認性・データ取得コスト）を説明したうえで5社に絞り込む（v0.1の方針）。
- 「もっと細かいセグメント」を指定された場合は、データソースが薄くなる可能性があることを `Step 2 Data Availability` で明示する。
