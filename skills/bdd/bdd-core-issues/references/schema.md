# BDD プロジェクト状態ファイル スキーマ

全BDDスキル（bdd-init / bdd-ingest-* / bdd-financial-model / bdd-report）が共通で参照・更新するファイル仕様。各スキルはこのスキーマに従ってファイルを読み書きする。

## ディレクトリ構造（プロジェクトルート固定）

```
bdd-project/
├── meta.json                   # プロジェクトメタ情報
├── issues.json                 # 論点ツリー
├── hypotheses.json             # 仮説（current + history）
├── facts.json                  # 事実
├── sources/                    # 元資料置き場
│   ├── im/
│   ├── web/
│   ├── minutes/
│   └── disclosure/
├── financial-model/
│   ├── model.xlsx              # 財務モデル本体（フォーマットは別途定義）
│   └── drivers.json            # ドライバーと論点の紐付け
└── outputs/                    # 最終アウトプット（PPTX等）
```

## 1. meta.json

```json
{
  "project_name": "X社BDD",
  "target_company": {
    "name": "株式会社X",
    "industry": "化学メーカー",
    "ticker": "0000",
    "listed": true
  },
  "client": "Y社",
  "phase": "Phase1_PublicInfo | Phase2_IM | Phase3_ManagementInterview | Phase4_Final",
  "started_at": "2026-04-29",
  "updated_at": "2026-04-29",
  "lead_consultant": "（任意）"
}
```

`phase` はBDDの進捗フェーズを示す。スキルは現在のフェーズに応じて挙動を変えてよい（例: Phase1なら数値の不確実性を強調、Phase4なら確度の高い記述に切り替え）。

## 2. issues.json

```json
{
  "version": "1.0",
  "updated_at": "2026-04-29",
  "issues": [
    {
      "id": "L1-01",
      "level": "L1",
      "name": "市場環境",
      "purpose": "対象会社が戦う市場の魅力度・成長性・構造を理解する",
      "source": "core | project_added",
      "priority": "High | Mid | Low",
      "children": ["L2-01-01", "L2-01-02", "L2-01-03", "L2-01-04"]
    },
    {
      "id": "L2-01-01",
      "level": "L2",
      "parent_id": "L1-01",
      "name": "市場規模と成長性",
      "key_questions": [
        "対象会社が戦う市場の現在の規模はいくらか",
        "..."
      ],
      "typical_verification_approach": "...",
      "typical_data_sources": ["..."],
      "priority": "High",
      "source": "core | project_added",
      "added_at": "2026-04-29",
      "added_reason": "（project_addedの場合のみ）追加理由",
      "linked_hypothesis_id": "H-L2-01-01"
    }
  ]
}
```

**フィールド説明**:
- `source`: `core` = bdd-core-issuesからコピーされたもの、`project_added` = プロジェクト固有で追加されたもの
- `priority`: bdd-reportの`--exec-summary`モードで使う重要度。デフォルトはコアの`default_priority`をコピー
- `linked_hypothesis_id`: 1論点に1仮説の対応（L2のみ）。L1には付かない

**編集ポリシー**: コア由来の論点もプロジェクトで編集可能（priority変更・削除含む）。削除する場合は対応する仮説も削除する。

## 3. hypotheses.json

```json
{
  "version": "1.0",
  "updated_at": "2026-04-29",
  "hypotheses": {
    "H-L2-01-01": {
      "issue_id": "L2-01-01",
      "current": {
        "statement": "市場CAGRは5%程度で安定成長",
        "confidence": "Mid",
        "supporting_facts": ["F-0012", "F-0023"],
        "updated_at": "2026-04-29",
        "updated_by_source": "S-MIN-002"
      },
      "history": [
        {
          "statement": "市場CAGRは8%程度で高成長",
          "confidence": "Low",
          "supporting_facts": ["F-0003"],
          "updated_at": "2026-04-15",
          "updated_by_source": "S-IM-001",
          "superseded_at": "2026-04-29",
          "superseded_reason": "マネイン議事録で社長が5%程度と言及"
        }
      ]
    }
  }
}
```

**フィールド説明**:
- `confidence`: `High`（複数の独立ソースで確認済み）/ `Mid`（1つのソースで確認）/ `Low`（推測ベース・要検証）
- `supporting_facts`: この仮説を支えるFactのID配列
- `updated_by_source`: この仮説を更新したソース（IM・議事録・開示資料等）のID
- `history`: 過去の仮説。新しい順ではなく古い順で並べる。`superseded_reason` は必須

**重要**: 仮説を更新するときは、必ず古い `current` を `history` に移動してから新しい `current` を書く。`superseded_reason` を空にしない。

## 4. facts.json

```json
{
  "version": "1.0",
  "updated_at": "2026-04-29",
  "facts": [
    {
      "id": "F-0001",
      "statement": "対象会社の2024年度売上高は120億円",
      "type": "quantitative | qualitative | quote",
      "value": 12000000000,
      "unit": "円",
      "source_id": "S-IM-001",
      "source_location": "p.15",
      "linked_issues": ["L2-07-01"],
      "added_at": "2026-04-29"
    },
    {
      "id": "F-0002",
      "statement": "社長は『価格競争には参加しない方針』と発言",
      "type": "quote",
      "source_id": "S-MIN-001",
      "source_location": "00:23:45",
      "linked_issues": ["L2-03-04", "L2-08-01"],
      "added_at": "2026-04-29"
    }
  ]
}
```

**フィールド説明**:
- `type`: `quantitative`（数値）/ `qualitative`（定性記述）/ `quote`（発言の引用）
- `value`/`unit`: `quantitative` のときに使う
- `source_location`: ページ番号、タイムスタンプ、URL等、出典の具体的な位置
- `linked_issues`: このFactが関連する論点ID配列（複数可）

**事実 vs 仮説の境界**: 議事録での発言・開示資料の数値・Webソースの記載 = 事実。それを解釈・推論したもの = 仮説。

## 5. sources/

各ソースは `sources/{type}/{S-XXX-NNN}_{description}.{ext}` の形式で保存。

ID命名規則:
- `S-IM-001`: IM・ティザー
- `S-WEB-001`: Web調査
- `S-MIN-001`: マネジメントインタビュー議事録
- `S-DISC-001`: 開示資料（有報・決算短信・統合報告書等）

ソースのメタ情報は `sources/index.json` で管理:

```json
{
  "sources": [
    {
      "id": "S-IM-001",
      "type": "im",
      "title": "X社 Information Memorandum",
      "filename": "S-IM-001_im_main.pdf",
      "received_at": "2026-04-15",
      "from": "FAアドバイザー Z社"
    },
    {
      "id": "S-MIN-001",
      "type": "minutes",
      "title": "社長マネジメントインタビュー第1回",
      "filename": "S-MIN-001_ceo_interview_1.txt",
      "interview_date": "2026-04-25",
      "interviewees": ["代表取締役 ○○"]
    }
  ]
}
```

## 6. financial-model/drivers.json

```json
{
  "version": "1.0",
  "updated_at": "2026-04-29",
  "drivers": [
    {
      "id": "D-revenue-growth",
      "name": "売上成長率",
      "current_value": 0.05,
      "current_unit": "ratio",
      "scenario_values": {
        "base": 0.05,
        "upside": 0.08,
        "downside": 0.02
      },
      "linked_issues": ["L2-01-03", "L2-04-01"],
      "linked_hypotheses": ["H-L2-01-01", "H-L2-04-01"],
      "rationale": "市場CAGR仮説と顧客集中度仮説に依存"
    }
  ]
}
```

`linked_hypotheses` の仮説が更新されたら、対応する `drivers` を見直す必要がある。bdd-financial-model スキルはこの逆引きを支援する。

## ID採番ルール

- 新規Fact追加時: 既存最大ID + 1（ゼロ埋め4桁）
- 新規論点追加時: 親L1配下の最大L2連番 + 1（ゼロ埋め2桁）
- 新規Source追加時: type別に既存最大ID + 1（ゼロ埋め3桁）

複数スキルが同時に書き込むことはないので、楽観的にインクリメントすればよい。
