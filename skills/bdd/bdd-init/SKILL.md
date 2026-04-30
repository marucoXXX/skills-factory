---
name: bdd-init
description: BDD（ビジネスデュー・ディリジェンス）プロジェクトの初期化スキル。コア論点マスター（bdd-core-issues）をプロジェクトの`issues.json`にコピーし、IM（Information Memorandum）とWeb調査結果から初期仮説を生成し、IM/Webから新たな論点も抽出して追加する。プロジェクトの状態ファイル一式（meta.json / issues.json / hypotheses.json / facts.json / sources/index.json）をbdd-projectディレクトリ配下に作成する。以下のいずれかのトリガーで必ずこのスキルを使うこと：「BDDを始めたい」「BDDプロジェクトを立ち上げて」「IMを読み込んで論点と仮説を作って」「ティザーから初期仮説を作って」「BDDの初期化」「bdd-init」「対象会社の論点ツリーを作って」「コア論点をコピーしてプロジェクト用に展開して」。BDDの第1段階（Phase1: Public Info / Phase2: IM）で対象会社の名前とIM・Web情報が示された場合に呼び出すこと。
---

# bdd-init: BDDプロジェクト初期化

IM・Web情報からBDDプロジェクトの状態ファイル一式を初期化するスキル。

## 入力

ユーザーから以下を受け取る（不足分は必ず聞く）:
1. **対象会社情報**: 会社名、業界、上場区分、ティッカー（任意）、所在地（任意）
2. **クライアント情報**: BDDの依頼主
3. **IM/ティザー**: PDFまたはテキスト（任意。なければWebのみで進める）
4. **プロジェクトディレクトリ**: 作成先のパス（デフォルト: `./bdd-project/`）

## 出力（生成する状態ファイル）

このスキルが実行後に存在を保証するファイル:

- `bdd-project/meta.json`
- `bdd-project/issues.json`
- `bdd-project/hypotheses.json`
- `bdd-project/facts.json`
- `bdd-project/sources/index.json`
- `bdd-project/sources/im/`、`sources/web/`、`sources/minutes/`、`sources/disclosure/`（空ディレクトリ含め作成）
- `bdd-project/financial-model/`（空）
- `bdd-project/outputs/`（空）

ファイル仕様の詳細は `bdd-core-issues/references/schema.md` を参照すること。

## 実行手順

### Step 1: ディレクトリ構造を作成

```bash
mkdir -p bdd-project/sources/{im,web,minutes,disclosure}
mkdir -p bdd-project/financial-model
mkdir -p bdd-project/outputs
```

### Step 2: meta.json を作成

ユーザー入力から `meta.json` を作成。`phase` の初期値:
- IM入手前 = `Phase1_PublicInfo`
- IM入手済み = `Phase2_IM`

### Step 3: コア論点を issues.json にコピー

`bdd-core-issues/assets/core_issues.json` を読み、以下のフォーマットで `issues.json` に変換:

- L1カテゴリは10件すべてコピー（`source: "core"`）
- L2論点は41件すべてコピー（`source: "core"`、`priority` には `default_priority` をコピー）
- 各L2論点には `linked_hypothesis_id: "H-{l2_id}"` を設定

### Step 4: IMとWebから事実（Fact）を抽出

IMが提供されている場合:
1. IMのファイルを `bdd-project/sources/im/S-IM-001_{filename}` にコピー
2. `sources/index.json` にIMを登録
3. IMから事実を抽出し、`facts.json` に追加（ID: F-0001から）
4. 各Factには出典（source_id・source_location）と関連論点（linked_issues）を必ず付ける

Web調査が必要な場合:
1. 対象会社・業界に関するWeb検索を実施（市場規模・競合・規制等の基本情報）
2. 検索結果を `sources/web/S-WEB-001_{topic}.md` 等として保存
3. `sources/index.json` に登録
4. 事実を `facts.json` に追加

**抽出すべき事実の優先度**:
- 必ず取る: 売上規模、従業員数、設立年、株主構成、主要事業、主要顧客、市場規模、主要競合
- できれば取る: 経営陣、財務指標推移、戦略の柱、リスク要因、最近のM&A・大型契約

### Step 5: 各L2論点について初期仮説を生成

41のL2論点それぞれについて、`hypotheses.json` に初期仮説を作成:

**仮説生成ロジック**:
1. その論点に紐づくFactが存在する場合:
   - Factを根拠に仮説を立てる（`confidence: "Mid"` または `"Low"`）
   - `supporting_facts` に該当FactのIDを列挙
2. その論点に紐づくFactが存在しない場合:
   - 業界一般論ベースで仮説を立てる（`confidence: "Low"`）
   - `supporting_facts` は空配列
   - `statement` 末尾に「(要検証)」を付ける

**重要**: 初期仮説は「無理に書かない」より「Lowでも書く」方が後段で議論しやすい。書けない論点ほど次の調査優先度が上がる。

### Step 6: プロジェクト固有論点を追加

IM・Webを読んでいる過程で、コア論点に含まれていない重要論点が見つかった場合、`issues.json` に追加する:

- 新規L2論点のIDは、最も近いL1配下の連番続き（例: L1-03配下に既にL2-03-04まであるなら次はL2-03-05）
- `source: "project_added"`、`added_reason` に追加理由を明記
- 対応する仮説も `hypotheses.json` に追加

**追加判断の基準**: 業界・対象会社固有の事情でクリティカルな論点（例: 化学メーカーなら「主要原料の長期供給契約の有無」、SaaSなら「Net Revenue Retention」など）。一般論で済むものは追加しない。

### Step 7: サマリーをユーザーに提示

最後に以下を報告:
- 作成した状態ファイル一覧
- 取得できたFact数（type別）
- L2論点41件のうち、Factに基づく仮説（Mid/High）の数 vs 一般論ベース（Low）の数
- 追加したプロジェクト固有論点があればその件数と内容
- 次のアクション提案（例: 「○○の論点はFactが薄いので、Web追加調査を推奨」）

## 注意事項

- **既存プロジェクトへの上書きを防ぐ**: `bdd-project/meta.json` が既に存在する場合は、ユーザーに確認してから進める
- **IDの一貫性**: コア論点のID体系を絶対に崩さない。プロジェクト追加分のみ連番を伸ばす
- **Factと仮説の混同を防ぐ**: IMに「市場規模は1兆円」と書いてあったらそれは事実。「だから対象会社は十分なヘッドルームがある」は仮説
- **不確実性の明示**: Lowの仮説は積極的に「(要検証)」「(推測)」等を付け、後段の議事録でアップデート対象であることを明確にする
