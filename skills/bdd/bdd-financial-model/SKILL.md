---
name: bdd-financial-model
description: BDDプロジェクトの中間成果物として財務モデル（Excel）を構築・更新するスキル。facts.jsonの数値データとhypotheses.jsonの仮説を入力に、過去実績期と将来予測期を含む財務モデルを生成し、各ドライバー（売上成長率・原価率・販管費率等）と論点・仮説の紐付けをdrivers.jsonで管理する。仮説が更新されたら、影響を受けるドライバーを逆引きで特定できる。以下のいずれかのトリガーで必ずこのスキルを使うこと：「財務モデルを作って」「財務モデルを更新して」「BDDの財務モデル」「ドライバーを論点に紐付けて」「仮説の変化が財務モデルに与える影響を見たい」「bdd-financial-model」。BDDプロジェクトでfacts.jsonに財務数値が一定揃ったタイミングで呼び出す。詳細フォーマットはユーザーから後日提供される予定のため、現状はインターフェース定義のみ。
---

# bdd-financial-model: 財務モデル構築

BDDの中間成果物として財務モデル（Excel）を構築・更新するスキル。

## ステータス

**現状: 詳細フォーマット定義待ち**

財務モデルExcelの具体的なシート構成・セル配置・計算ロジックは、ユーザーから別途提供される予定。本SKILL.mdはインターフェース（入出力・他スキルとの連携）のみを定義する。フォーマット提供後に本ファイルを更新する。

## 入力

1. **bdd-projectディレクトリ**: 既存プロジェクト
2. **financial-model template**（後日提供）: 財務モデルのExcelテンプレート
3. **モード**:
   - `--create`: 新規モデル作成（初回）
   - `--update`: 既存モデルの更新（仮説変更後）

## 出力

- `bdd-project/financial-model/model.xlsx`: 財務モデル本体
- `bdd-project/financial-model/drivers.json`: ドライバーと論点・仮説の紐付け

## drivers.json のスキーマ

```json
{
  "version": "1.0",
  "updated_at": "2026-04-29",
  "drivers": [
    {
      "id": "D-revenue-growth",
      "name": "売上成長率",
      "category": "revenue | cost | sga | capex | working_capital | other",
      "current_value": 0.05,
      "current_unit": "ratio | jpy | count",
      "scenario_values": {
        "base": 0.05,
        "upside": 0.08,
        "downside": 0.02
      },
      "linked_issues": ["L2-01-03", "L2-04-01"],
      "linked_hypotheses": ["H-L2-01-01", "H-L2-04-01"],
      "rationale": "市場CAGR仮説と顧客集中度仮説に依存",
      "excel_cell_reference": "PL_Forecast!B12",
      "updated_at": "2026-04-29"
    }
  ]
}
```

## 機能

### 1. 新規モデル作成（--create）

`facts.json` の過去実績数値を読み、過去5期のPL・BSを Excel に転記。
仮説に基づいて将来3〜5期分の予測を入れる。
ドライバーを drivers.json に登録し、各ドライバーを論点・仮説に紐付ける。

### 2. モデル更新（--update）

仮説が更新されたとき、影響を受けるドライバーを逆引き:
1. `hypotheses.json` を読み、`updated_at` が drivers.json の `updated_at` より新しい仮説を抽出
2. それら仮説を `linked_hypotheses` に持つドライバーを特定
3. ユーザーに「以下のドライバーを再計算する必要があります」と提示
4. 新しい仮説に基づいてドライバー値を更新し、Excelを再計算

### 3. 整合性チェック

- `linked_issues` の論点が `issues.json` に存在するか
- `linked_hypotheses` の仮説が `hypotheses.json` に存在するか
- `current_value` が `scenario_values.base` と一致しているか
- 仮説の confidence が Low なのに base シナリオで使われていないか（Lowは downside/upside でレンジ取り）

### 4. シナリオ管理

base / upside / downside の3シナリオを各ドライバーで保持。
シナリオ別のPL・BS・CF・バリュエーションをExcelで自動計算（テンプレートに組み込む想定）。

## 他スキルとの連携

- **bdd-ingest-disclosure**: 開示資料から数値Factが大量に入ったタイミングで、本スキルの `--create` または `--update` を提案
- **bdd-ingest-minutes**: マネインで仮説が変わったとき、本スキルの `--update` を提案
- **bdd-report**: レポート出力時に、財務モデルから売上推移・利益率推移のチャートデータを取得してPPTXに反映

## 実装上の方針（フォーマット確定後の方向性）

- Excelテンプレートは `financial-model/template.xlsx` として保持
- `openpyxl` で セル単位で値を書き込む（数式は壊さない）
- ドライバーセルには名前付き範囲（Named Range）を使い、`drivers.json` の `excel_cell_reference` でマッピング
- シナリオ切り替えは Excelの INDEX/MATCH で実装（VBAは使わない）

## 注意事項

- **数値の出典管理を厳守**: モデルの全セルが、どのFactまたはどの仮説に紐付くかをトレース可能にする
- **仮説の confidence をモデルに反映**: Low confidence の仮説に依存するセルはセル背景色を変える等、視覚的に区別する
- **モデル更新の履歴**: 更新時には旧モデルを `model_v{N}.xlsx` としてアーカイブする
