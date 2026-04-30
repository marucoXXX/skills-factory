# BDD Skills

BDD（ビジネスデュー・ディリジェンス）プロジェクトをファイルベースで支援するスキル群。Claude Codeで使用することを前提に、固定ディレクトリ構造（`bdd-project/`）で状態を管理する。

## 設計思想

- **状態はファイル、スキルは状態を読んで更新する関数**
- **事実（Fact）と仮説（Hypothesis）を厳密に分離**
- **仮説の歴史性を保持**（更新時に古い仮説を捨てない）
- **論点と財務モデルのドライバーを紐付け**（仮説変更時に逆引き可能）
- **既存の40+ PPTXスキルを再利用**（bdd-reportはオーケストレーター）

## スキル構成（3層）

### Layer 1: アセット
- **bdd-core-issues**: 業界横断のコア論点マスター（L1×10、L2×41）+ スキーマ定義

### Layer 2: プロジェクト状態管理
プロジェクトごとに `bdd-project/` 配下で管理:
```
bdd-project/
├── meta.json              # プロジェクトメタ
├── issues.json            # 論点ツリー（コア+追加）
├── hypotheses.json        # 仮説（current + history）
├── facts.json             # 事実
├── sources/               # 元資料
│   ├── index.json
│   ├── im/, web/, minutes/, disclosure/
├── financial-model/
│   ├── model.xlsx
│   └── drivers.json       # ドライバー↔論点の紐付け
└── outputs/               # 最終PPTX
```

### Layer 3: プロセススキル
- **bdd-init**: IM/Webから初期化（コア論点コピー → 初期仮説 → 追加論点抽出）
- **bdd-ingest-minutes**: マネイン議事録から仮説・事実を更新
- **bdd-ingest-disclosure**: 開示資料から事実・仮説を更新
- **bdd-financial-model**: 財務モデル構築（フォーマット定義待ち）
- **bdd-report**: 既存PPTXスキル群を呼び出して最終アウトプット生成

## 典型的なワークフロー

```
[1] bdd-init           → bdd-projectディレクトリ作成、コア論点コピー、IM/Webから初期仮説
[2] bdd-ingest-disclosure → 有報を読み込み、財務Factを大量追加、仮説強化
[3] bdd-financial-model   → 財務モデル初版作成
[4] bdd-ingest-minutes    → 社長マネインを取り込み、仮説アップデート
[5] bdd-financial-model --update  → 仮説変化を反映してモデル更新
[6] bdd-ingest-minutes (CFO・事業部長) → さらなる仮説アップデート
[7] bdd-report --exec-summary → エグゼクティブサマリー生成
[8] bdd-report --all          → 最終フルデッキ生成
```

## ID体系

| 対象 | フォーマット | 例 |
|---|---|---|
| L1論点 | `L1-{NN}` | L1-07 |
| L2論点 | `L2-{L1番号}-{連番}` | L2-07-01 |
| 仮説 | `H-{L2論点ID}` | H-L2-07-01 |
| 事実 | `F-{連番4桁}` | F-0001 |
| ソース（IM） | `S-IM-{連番3桁}` | S-IM-001 |
| ソース（Web） | `S-WEB-{連番3桁}` | S-WEB-001 |
| ソース（議事録） | `S-MIN-{連番3桁}` | S-MIN-001 |
| ソース（開示） | `S-DISC-{連番3桁}` | S-DISC-001 |
| 財務ドライバー | `D-{name}` | D-revenue-growth |

## ファイルスキーマ

詳細は `bdd-core-issues/references/schema.md` を参照。

## 後日対応事項

- [ ] 財務モデルのExcelフォーマット定義（ユーザー提供待ち）→ bdd-financial-model SKILL.md 更新
- [ ] 整合性チェック機能（Fact間矛盾、仮説間矛盾の検出）の実装
- [ ] スキルのインストール方法のドキュメント化

## コア論点（L1×L2）の概要

| L1 | L2数 | 内容 |
|---|---|---|
| L1-01 市場環境 | 4 | 市場規模・セグメント・ドライバー・マクロ |
| L1-02 競争環境 | 4 | 競合・KSF・5フォース・新規参入 |
| L1-03 ビジネスモデル | 4 | 収益モデル・VC・差別化・価格 |
| L1-04 商流・顧客 | 4 | 顧客集中度・関係性・チャネル・ニーズ |
| L1-05 オペレーション | 4 | 調達・生産・設備・IT |
| L1-06 組織・人材 | 4 | 経営・人員・文化・報酬 |
| L1-07 財務 | 5 | 売上・利益・コスト・BS/CF・投資 |
| L1-08 成長戦略 | 4 | 中計・新規事業・海外・M&A |
| L1-09 リスク | 4 | 事業・オペ・法務・財務 |
| L1-10 ESG・規制 | 4 | 規制・E・S・G |
| **計** | **41** | |
