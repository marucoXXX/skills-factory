# 出力スキーマ定義

本スキルの全エージェント・全出力の正式なJSONスキーマ定義。

---

## 1. 各収集エージェントの出力スキーマ

`agents/financial-signals.md` / `strategic-signals.md` / `corporate-registry.md` /
`talent-organization.md` / `industry-context.md` の全てが以下の共通スキーマで出力する。

```json
{
  "agent": "financial_signals | strategic_signals | corporate_registry | talent_organization | industry_context",
  "target": "<対象会社名>",
  "collected_at": "<ISO 8601 タイムスタンプ>",

  "findings": [
    {
      "metric": "<シグナル種類>",
      "value": "<文字列または構造化値>",
      "source": "<出典の具体的記述: URL, PDF名, 公示日, 投稿日など>",
      "source_type": "registry | gazette | press | grant_db | patent_db | web | sns | upload",
      "confidence": "high | medium | low",
      "limitations": "<この情報の解釈上の制約>"
    }
  ],

  "data_gaps": [
    {
      "item": "<取れなかった情報の項目>",
      "reason": "<取得できなかった理由>"
    }
  ]
}
```

### `source_type` の分類

| 値 | 対応ソース | 信頼度の基礎 |
|----|----------|------------|
| `upload` | ユーザーアップロードPDF・ファイル | high（ユーザーが責任を持って提供） |
| `registry` | 公的登記（法人番号公表サイト、EDINET、建設業許可DB等） | high |
| `gazette` | 官報決算公告、官報公告 | high |
| `patent_db` | J-PlatPat（特許情報プラットフォーム） | high |
| `grant_db` | jGrants、ものづくり補助金、事業再構築補助金、NEDO採択DB | high |
| `press` | プレスリリース（PR TIMES, @Press, 共同通信PRワイヤー） | medium |
| `web` | 自社HP、業界紙、地方紙、業界団体HP、Web記事 | medium（単独）〜high（複数一致） |
| `sns` | X, LinkedIn, note, 自社ブログ | low（単独）〜medium（複数一致） |

### `confidence` の決定ルール

- `source_type` が `upload`, `registry`, `gazette`, `patent_db`, `grant_db` のいずれか → **原則 `high`**
- それ以外で、**2ソース以上で同じ内容が確認できた**（`source_type` が異なる） → **`medium` 以上**
- 単独ソースのみ（`press`, `web`, `sns`） → **原則 `low`**

### `limitations` の記入ルール

必ず以下のいずれかの観点で1行以上記入する:
- 情報の粒度の粗さ（例: 「売上高のみ、セグメント別は不明」）
- 情報の時期（例: 「2021年時点の数字で、最新ではない可能性」）
- 発言と実態の乖離可能性（SNS由来の場合、必ず明示）
- 匿名情報のバイアス（退職者レビュー等）

---

## 2. Synthesis Agentの出力スキーマ（`synthesis_output.json`）

```json
{
  "target_company": "<対象会社名>",
  "industry": "<業界>",
  "research_purpose": "<BDD | 競合分析 | M&Aターゲット評価 | 投資検討 | 新規参入>",
  "synthesized_at": "<ISO 8601>",

  "executive_summary": {
    "main_message": "<最大70文字、事実ベース、『〜すべき』禁止>",
    "findings": [
      {
        "category": "対象会社 | 市場 | 競合 | 結論 | 検証論点",
        "heading": "<1行見出し>",
        "detail": "<2〜3行の詳細。confidenceレベルを含める>",
        "evidence_refs": ["<finding ID>", "..."]
      }
    ]
  },

  "strategy_hypotheses": {
    "where_to_play": {
      "hypothesis": "<事業領域・顧客・地域の選択に関する仮説>",
      "evidence_refs": ["F1", "F5"],
      "confidence": "high | medium | low"
    },
    "how_to_win": {
      "hypothesis": "<差別化軸・戦い方に関する仮説>",
      "evidence_refs": [...],
      "confidence": "..."
    },
    "capability_resource": {
      "hypothesis": "<資源配分の重心に関する仮説>",
      "evidence_refs": [...],
      "confidence": "..."
    },
    "aspiration_trajectory": {
      "hypothesis": "<経営意図と時間軸に関する仮説>",
      "evidence_refs": [...],
      "confidence": "..."
    },
    "reality_check": [
      {
        "stated": "<経営者が発信していること（出典付き）>",
        "revealed": "<実際の行動（出典付き）>",
        "gap": "<齟齬の具体的内容>",
        "evidence_refs": ["F2", "F7"]
      }
    ]
  },

  "data_availability_matrix": {
    "categories": [
      {
        "name": "対象会社 | 財務 | 戦略発信 | 登記 | 組織・人材 | 業界ポジション",
        "items": [
          {
            "label": "<項目名>",
            "status": "complete | partial | missing",
            "source": "<取得元 or 取得不可の理由>"
          }
        ]
      }
    ]
  },

  "verification_issues": [
    {
      "id": "V1",
      "category": "収益構造 | 顧客基盤 | オペレーション | 組織・人材 | 競争優位 | M&A関連",
      "issue": "<論点（質問形式でOK）>",
      "current_hypothesis": "<現時点の推定>",
      "verification_method": "<誰にどう聞くか>",
      "priority": "high | medium | low"
    }
  ],

  "triangulation_stats": {
    "total_findings": 0,
    "high_confidence": 0,
    "medium_confidence": 0,
    "low_confidence": 0,
    "triangulation_rate": 0.0
  },

  "all_findings_index": [
    {
      "id": "F1",
      "agent": "financial_signals",
      "metric": "sales_trend",
      "value": "...",
      "source": "...",
      "confidence": "high"
    }
  ]
}
```

### `confidence` 伝播ルール（Synthesis内）

- 仮説の `confidence` = 根拠 finding の最低 `confidence`
  - 全て `high` → 仮説 `high`
  - 最低1つが `medium` → 仮説 `medium`
  - 最低1つが `low` → 仮説 `low`
- ただし、`low` finding は原則として仮説の根拠に使わない（例外時のみ、その旨を `limitations` 同等のフィールドで明示）

### `triangulation_rate` の計算

- 「2つ以上の独立ソースで裏付けがある finding の数 / 全 finding 数」
- 独立ソースの判定: `source_type` が異なる、または同じ `source_type` でも異なる出典元（例: `press` でも PR TIMESと自社HPは独立）
- 成功基準: **0.6以上**（要件書 §10.1）

---

## 3. Master Output スキーマ（`master_output.json`）

MVPでは `pptx_slot` 配下は全て空で構わない。Phase 3でPPTX連携時に埋める予約スキーマ。

```json
{
  "target_company": "<対象会社名>",
  "synthesized_at": "<ISO 8601>",
  "phase": "mvp | phase2 | phase3",

  "pptx_slot": {
    "executive_summary": {
      "_schema_ref": "executive-summary-pptx",
      "main_message": "",
      "chart_title": "",
      "findings": [],
      "source": ""
    },
    "company_overview": {
      "_schema_ref": "company-overview-pptx-v2",
      "title": "",
      "main_message": "",
      "source": "",
      "items": [],
      "photos": {}
    },
    "swot": {
      "_schema_ref": "swot-pptx",
      "main_message": "",
      "chart_title": "",
      "swot": {
        "strengths": {"items": []},
        "weaknesses": {"items": []},
        "opportunities": {"items": []},
        "threats": {"items": []}
      }
    },
    "business_model": {
      "_schema_ref": "business-model-pptx",
      "main_message": "",
      "chart_title": "",
      "company": {},
      "suppliers": [],
      "customers": [],
      "implications": []
    },
    "data_availability": {
      "_schema_ref": "data-availability-pptx",
      "main_message": "",
      "chart_title": "",
      "categories": [],
      "constraints": []
    },
    "issue_risk_list": {
      "_schema_ref": "issue-risk-list-pptx",
      "main_message": "",
      "chart_title": "",
      "items": []
    },
    "table_of_contents": {
      "_schema_ref": "table-of-contents-pptx",
      "main_message": "目次",
      "chart_title": "Table of Contents",
      "sections": []
    },
    "section_dividers": []
  },

  "synthesis_ref": "<synthesis_output.json へのパス>"
}
```

`_schema_ref` は、Phase 3実装時に参照すべきPPTXスキルのディレクトリ名を示す。
各フィールドの具体的な形式は、該当PPTXスキルの `SKILL.md` と `references/sample_data.json` を参照。

---

## 4. バリデーション

出力JSONは `scripts/validate_output.py` でスキーマチェックする（Phase 1時点では
`financial_signals` / `strategic_signals` / `synthesis_output` の3スキーマのみ検証）。

### 必須フィールドチェック

各収集エージェント出力:
- `agent`, `target`, `collected_at`, `findings`, `data_gaps` が存在すること
- `findings[]` の各要素に `metric`, `value`, `source`, `source_type`, `confidence`, `limitations` が存在すること
- `source_type` が許容値のいずれかであること
- `confidence` が `high | medium | low` のいずれかであること

Synthesis出力:
- 全セクションが存在すること
- `strategy_hypotheses.reality_check` が**空配列でない**こと（最低1要素）
  - 齟齬が検出されなかった場合は `{"stated": "-", "revealed": "-", "gap": "明確な齟齬は検出されなかった", "evidence_refs": []}` を入れる
- `verification_issues[]` が**3〜7要素**であること
- `executive_summary.findings[]` が **3〜5要素**であること
