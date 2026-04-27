# {TARGET_COMPANY} 戦略調査レポート

- 作成日: {SYNTHESIZED_AT}
- 業界: {INDUSTRY}
- 調査目的: {RESEARCH_PURPOSE}
- 調査深度: {DEPTH_MODE}
- 本レポートはスモールキャップ戦略調査スキル v1.0 (MVP) により生成された

---

## Executive Summary

**{EXECUTIVE_SUMMARY_MAIN_MESSAGE}**

{EXECUTIVE_SUMMARY_FINDINGS_BULLETS}

---

## 1. 会社概要（確定情報のみ）

対象会社名: {TARGET_COMPANY}

確定している基本情報:
{COMPANY_OVERVIEW_ITEMS}

> 注: 本セクションは `confidence: high` の finding のみから構成される。
> 推定・仮説は全て「3. 戦略仮説」に分離して記述する。

---

## 2. 情報源サマリー

調査対象エージェント:
{AGENTS_INVOKED_LIST}

収集された findings の信頼度分布:
- `high`: {CONFIDENCE_HIGH_COUNT} 件
- `medium`: {CONFIDENCE_MEDIUM_COUNT} 件
- `low`: {CONFIDENCE_LOW_COUNT} 件
- 合計: {TOTAL_FINDINGS_COUNT} 件
- triangulation率（2ソース以上で裏付けがあった finding の比率）: {TRIANGULATION_RATE}

---

## 3. 戦略仮説

### 3.1 Where to play（事業領域・顧客・地域の選択）

**仮説** (`confidence: {WTP_CONFIDENCE}`):
{WHERE_TO_PLAY_HYPOTHESIS}

根拠となる finding:
{WHERE_TO_PLAY_EVIDENCE}

### 3.2 How to win（差別化軸・戦い方）

**仮説** (`confidence: {HTW_CONFIDENCE}`):
{HOW_TO_WIN_HYPOTHESIS}

根拠となる finding:
{HOW_TO_WIN_EVIDENCE}

### 3.3 Capability & Resource Allocation（資源配分の重心）

**仮説** (`confidence: {CAP_CONFIDENCE}`):
{CAPABILITY_RESOURCE_HYPOTHESIS}

根拠となる finding:
{CAPABILITY_RESOURCE_EVIDENCE}

### 3.4 Aspiration & Trajectory（経営意図と時間軸）

**仮説** (`confidence: {ASP_CONFIDENCE}`):
{ASPIRATION_TRAJECTORY_HYPOTHESIS}

根拠となる finding:
{ASPIRATION_TRAJECTORY_EVIDENCE}

### 3.5 Reality Check（発言と行動の齟齬）

{REALITY_CHECK_ITEMS}

---

## 4. Data Availability Matrix

| カテゴリ | 項目 | ステータス | ソース／制約 |
|--------|------|----------|------------|
{DATA_AVAILABILITY_TABLE_ROWS}

**取得済（✓）**: {COMPLETE_COUNT} 件 / **一部取得（△）**: {PARTIAL_COUNT} 件 / **未取得（✗）**: {MISSING_COUNT} 件

---

## 5. 今後検証すべき論点

公開情報では確定できなかった点、仮説にとどまる点について、
業界インタビュー・マネジメントインタビュー等で確認すべき論点を優先度順に示す。

| ID | カテゴリ | 論点 | 現時点での仮説 | 確認方法 | 優先度 |
|----|--------|-----|--------------|---------|------|
{VERIFICATION_ISSUES_TABLE_ROWS}

---

## 6. 結論と留意事項

本レポートは**公開情報およびユーザー提供資料のみ**に基づく調査結果である。以下を明記する:

- 本レポートの戦略仮説は、**{INDUSTRY} 業界の典型的な構造を対象会社が採っている**という前提に立っており、実際のオペレーション・KPI・内部戦略は業界インタビュー／マネジメントインタビューで検証が必要
- `confidence: low` の finding は参考情報として位置づけ、意思決定の根拠には用いないこと
- Reality Check で指摘した齟齬は、発言と行動の間の時差・戦略優先度の違いを示すに過ぎず、即座に「方針がブレている」と断じるものではない
- M&A・投資意思決定にあたっては、本レポートの「5. 今後検証すべき論点」を設問設計のベースに、追加の一次情報収集を行うこと

---

## Appendix A. 情報ソース一覧

調査で実際に参照した主要ソース（抜粋）:

{SOURCES_APPENDIX}

---

## Appendix B. Finding Index（全件）

全 findings の一覧（ID、エージェント、metric、出典、信頼度）:

{ALL_FINDINGS_INDEX}

---

*本レポートは `smallcap-strategy-research` スキルにより自動生成されました。*
*Synthesis JSON: `{SYNTHESIS_OUTPUT_PATH}`*
*Master Output (Phase 3 PPTX用予約): `{MASTER_OUTPUT_PATH}`*
