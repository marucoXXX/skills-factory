---
name: bdd-report
description: BDDプロジェクトの最終アウトプット（PowerPointデッキ）を生成するオーケストレータースキル。issues.json / hypotheses.json / facts.json / financial-model を読み込み、選択モード（全体・エグゼクティブサマリー・特定L1のみ・特定論点のみ・低信頼度仮説のみ）に応じて、既存のBDD向けPPTXスキル群（market-environment-pptx / swot-pptx / company-overview-pptx-v2 / customer-profile-pptx / valuation-summary-pptx / executive-summary-pptx 等）を呼び出してデッキを組み立てる。論点ベースで内容を構造化し、仮説のconfidence・出典を明示する。以下のいずれかのトリガーで必ずこのスキルを使うこと：「BDDレポートを作って」「BDDの最終アウトプットを生成」「論点ベースでスライドを作って」「エグゼクティブサマリーだけ作って」「L1-XXのスライドだけ作って」「信頼度Lowの論点だけ抽出して」「bdd-report」「BDDデッキを生成」。bdd-projectディレクトリの状態ファイルが揃っているタイミングで呼び出すこと。
---

# bdd-report: BDDレポート生成オーケストレーター

BDDプロジェクトの状態ファイル（issues / hypotheses / facts / financial-model）を読み、PowerPointデッキを生成するオーケストレータースキル。本スキル自体はPPTX生成を行わず、既存のPPTXスキル群を選択して呼び出す。

## 入力

1. **bdd-projectディレクトリ**: 既存プロジェクト
2. **モード**（必須、対話で選択）:
   - `--all`: 全論点をフル展開（最大規模、L1×10、L2×40+で50枚以上）
   - `--exec-summary`: エグゼクティブサマリー（priority: High の論点のみ、5〜10枚）
   - `--l1 <L1-ID>`: 特定L1配下のみ（例: `--l1 L1-07` で財務だけ）
   - `--issue <L2-ID>`: 特定L2論点のみ（1論点で1〜2枚）
   - `--confidence-low`: 信頼度Lowの仮説だけ（追加調査論点リスト用、3〜5枚）
3. **出力先**: `bdd-project/outputs/{mode}_{timestamp}.pptx`

## 出力

- 選択モードに応じたPPTXファイル
- 出力サマリー（生成スライド数、含まれる論点数、信頼度別仮説数）

## 実行手順

### Step 1: プロジェクト状態の読み込み

以下を読み込む:
- `meta.json`: 対象会社・クライアント・フェーズ
- `issues.json`: 論点ツリー
- `hypotheses.json`: 仮説とその根拠
- `facts.json`: 事実
- `sources/index.json`: ソース一覧
- `financial-model/drivers.json`: 財務ドライバー（あれば）
- `financial-model/model.xlsx`: 財務モデル（あれば）

### Step 2: モード別の論点フィルタリング

モードに応じて表示対象論点を絞る:

| モード | 抽出ロジック |
|---|---|
| `--all` | issues.json のL2全件 |
| `--exec-summary` | priority: "High" の L2 のみ |
| `--l1 <ID>` | 指定L1の children に含まれるL2のみ |
| `--issue <ID>` | 指定L2のみ |
| `--confidence-low` | hypotheses.json で current.confidence == "Low" のL2のみ |

### Step 3: スライド構成の決定

#### 全モード共通の前段スライド

1. **表紙**: title-slide-pptx（[skill: title-slide-pptx]）
   - クライアント、対象会社、タイトル「○○社 BDD レポート」、日付
2. **目次**: table-of-contents-pptx（[skill: table-of-contents-pptx]）
3. **データアベイラビリティ**: data-availability-pptx（[skill: data-availability-pptx]）
   - sources/index.json に基づき、取得済みソースの網羅度を表示

#### `--exec-summary` モードの中段

4. **エグゼクティブサマリー**: executive-summary-pptx（[skill: executive-summary-pptx]）
   - priority: High の論点について、各仮説のcurrent.statementを Key Findings として列挙
   - confidence別の色分けを工夫

#### L1別の本論セクション（`--all` / `--l1` / `--exec-summary` の場合）

各L1ごとに:
- **中扉**: section-divider-pptx（[skill: section-divider-pptx]）
- **L2論点ごとのスライド**: L1ごとに最適なPPTXスキルを選定（下記マッピング参照）

#### L1×L2と既存PPTXスキルのマッピング

| L1カテゴリ | 推奨PPTXスキル | 内容 |
|---|---|---|
| L1-01 市場環境 | market-environment-pptx, pest-analysis-pptx | 市場規模推移、ドライバー分析、PEST |
| L1-02 競争環境 | financial-benchmark-pptx, market-share-pptx, positioning-map-pptx, five-forces-pptx | 競合比較、シェア、ポジショニング、5フォース |
| L1-03 ビジネスモデル | business-model-pptx, business-portfolio-pptx, value-chain-pptx, swot-pptx | 事業モデル図、セグメント分析、バリューチェーン、SWOT |
| L1-04 商流・顧客 | customer-profile-pptx, customer-sales-detail-pptx, sales-by-customer-pptx | 顧客プロファイル、顧客別売上 |
| L1-05 オペレーション | value-chain-matrix-pptx, table-chart-pptx | バリューチェーン配置、設備・拠点 |
| L1-06 組織・人材 | shareholder-structure-pptx, workforce-composition-pptx | 株主・役員、人員構成 |
| L1-07 財務 | revenue-analysis-pptx, sga-breakdown-pptx, cost-breakdown-pptx, growth-driver-pptx, financial-benchmark-pptx | 売上分析、販管費、原価、成長ドライバー、ベンチマーク |
| L1-08 成長戦略 | scenario-forecast-pptx, current-period-forecast-pptx, recommendation-action-pptx | シナリオ予測、当期着地、推奨アクション |
| L1-09 リスク | issue-risk-list-pptx, table-chart-pptx | リスク一覧 |
| L1-10 ESG・規制 | table-chart-pptx, swot-pptx | 規制・ESG整理 |
| 全体 | executive-summary-pptx, valuation-summary-pptx | サマリー、バリュエーション |
| 結論 | recommendation-action-pptx | 検証論点・追加調査推奨 |

実際にどのスキルを使うかは、各L2論点で集まっているFactの種類・量に応じて柔軟に判断する。例:
- L2-07-01（売上推移）でFactが揃っているなら revenue-analysis-pptx
- L2-09-03（訴訟）でリスクが複数あるなら issue-risk-list-pptx

#### 後段スライド

- **検証論点（残された問い）**: confidence: Low の論点をリスト化（recommendation-action-pptx または issue-risk-list-pptx）
- **データアベイラビリティ（再掲・詳細版）**: 取得できなかった情報の整理

### Step 4: 各スライドへのコンテンツ供給

各PPTXスキルを呼び出す際、以下の情報をコンテンツとして渡す:

- **論点（issue）**: 対応するL2論点のname、key_questions
- **仮説（hypothesis）**: current.statement、confidence
- **根拠（facts）**: supporting_facts に含まれるFact群（statement、source）
- **過去仮説（history）**: 重要な仮説変遷があれば「当初は○○と考えていたが、△△により××に修正」の形で1行加える

confidence の表示ルール:
- High: マーカーや色なしで断定的に書く
- Mid: 「と推察される」「と考えられる」等の表現
- Low: 「(要検証)」を末尾に付ける、または別色

### Step 5: スライド生成の実行

選択された各PPTXスキルを順次呼び出し、`bdd-project/outputs/` 内に個別スライドを生成。
最後に `merge-pptxv2` スキル（[skill: merge-pptxv2]）でひとつのPPTXに結合する。

ファイル名: `{mode}_{YYYYMMDD}_{HHMM}.pptx`
例: `exec_summary_20260429_1430.pptx`

### Step 6: サマリーをユーザーに提示

実行後の報告:

1. **生成したPPTX**: ファイルパス、総スライド数
2. **モード別の結果**:
   - `--all`: 含まれた論点数（L1×10, L2×N）
   - `--exec-summary`: priority Highの論点数、サマリーで触れた仮説の confidence 分布
   - `--l1`: 該当L1配下の論点カバー率
   - `--confidence-low`: Low仮説の数とリスト
3. **品質警告**:
   - Factが不足していてスライドの内容が薄い論点
   - confidenceが揃っていない論点（同じL1内でばらつきが大きい）
   - 古い `history` を参照すべき重要な仮説変遷
4. **次のアクション提案**:
   - confidence Lowが多い論点 → 追加調査
   - Fact数が少ない論点 → 追加開示資料・追加マネイン依頼
   - 矛盾しているFact同士 → 再確認

## 注意事項

- **本スキルはオーケストレーター**: 自身でPPTXは作らない。既存のPPTXスキル群を呼び出す
- **論点ID・仮説IDをスライド内に必ず明記**: 各スライドの右下や脚注に「Issue: L2-XX-XX」を入れることで、どの論点のスライドかをトレース可能にする
- **出典の表示**: 各Factをスライドに使う際、source_idを脚注として表示（例: 「出典: 有報 p.45 (S-DISC-001)」）
- **confidence Lowの扱い**: Low仮説は「言い切らない」ことが重要。「○○である」ではなく「○○の可能性がある（要検証）」のように書く
- **仮説の history を活かす**: マネインで覆った重要仮説は、エグゼクティブサマリーで「当初仮説 vs 現在仮説」の対比を見せる場面で価値が出る
- **既存PPTXスキルの呼び出し**: 各PPTXスキル（market-environment-pptx等）は独立した別スキル。本スキルから自然言語で「market-environment-pptxを使って○○のスライドを作って」と呼び出す形を取る
