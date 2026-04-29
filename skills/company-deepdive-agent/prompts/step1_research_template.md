# Step 1 Web 検索クエリテンプレート — company-deepdive-agent

`company-deepdive-agent` の Step 1 で会社レベル 5 論点それぞれについて WebSearch を実行する際の
クエリテンプレート。プレースホルダ `{company_name}` / `{industry}` / `{competitors[*]}` を
Step 0 で受領した値で展開する。

各論点 **5-8 件** のクエリを実行し、結果を踏まえて Step 5 の `data_NN_*.json` を組み立てる。

---

## プレースホルダ

| 変数 | 例（二幸産業） |
|---|---|
| `{company_name}` | `二幸産業` または `二幸産業株式会社` |
| `{industry}` | `ビルメンテナンス業` |
| `{competitors[*]}` | `イオンディライト` / `東急不動産HD` / `東洋テック` / `大成` / `日本ハウズイング`（Step 0 で確定） |

---

## 論点 1: 会社の概要は？（customer-profile-pptx OR company-overview-pptx-v2）

**目的**: 商号・本社・設立・資本金・代表者・事業内容・主要販売先・仕入先・売上高・従業員数を把握。

### クエリ例

1. `{company_name} 公式 会社概要`
2. `{company_name} 設立 資本金 代表者 本社`
3. `{company_name} 有価証券報告書 会社の概要`（上場の場合）
4. `{company_name} 統合報告書 会社情報`
5. `{company_name} 従業員数 拠点数`
6. `{company_name} 親会社 グループ会社`
7. `{company_name} 沿革 歴史`（簡易版、論点 2 と一部被る）

### 取得したい情報

- 商号・本社所在地・設立年・資本金・代表者
- 事業内容（1-2 行）
- 従業員数・拠点数
- 親会社・グループ会社（あれば）
- 上場区分（東証プライム / スタンダード / 非上場）
- 業種・主要事業

### 非上場時の代替ソース

`FUMA`（fumadata.com）、`Baseconnect`（baseconnect.in）、`gBizINFO`（info.gbiz.go.jp）、`NIKKEI COMPASS`（nikkei.com/compass）、`官報決算公告`、企業の公式 HP「会社案内」PDF。
帝国データバンク・東京商工リサーチは無料で取れる範囲は限定的。

---

## 論点 2: 会社の沿革は？（company-history-pptx）

**目的**: 設立から現在までの主要マイルストーン（10-15 件、年月＋出来事）を整理。

### クエリ例

1. `{company_name} 沿革 創業 設立`
2. `{company_name} 公式 history`
3. `{company_name} 統合報告書 沿革`
4. `{company_name} 上場 東証`
5. `{company_name} M&A 買収 子会社化`
6. `{company_name} 拠点 海外進出 本社移転`
7. `{company_name} Wikipedia`（一次ソース確認必須、二次的に使う）

### 取得したい情報

- 創業年・設立年（法人化）
- 主要な節目: 増資、上場、M&A、拠点開設、社名変更、経営陣交代
- 認証・受賞（環境・SDGs 等のサステナビリティ取り組み）
- 創業者・歴代経営者の経歴

### 注意

- Wikipedia の沿革は**他の一次ソース（公式 HP・有報）と必ず突き合わせる**
- 検索結果に矛盾がある場合、有報 > 統合報告書 > 公式 HP > Wikipedia の優先順位

---

## 論点 3: 事業ポートフォリオは？（business-portfolio-pptx）

**目的**: 事業セグメントごとの売上構成・成長率・利益率を 3-5 年分把握。

### クエリ例

1. `{company_name} セグメント情報 売上構成`
2. `{company_name} 決算短信 セグメント別`
3. `{company_name} 事業セグメント 売上比率`
4. `{company_name} 事業ポートフォリオ`
5. `{company_name} 主要事業 強み`
6. `{company_name} 中期経営計画 セグメント`
7. `{company_name} 公式 事業内容 一覧`

### 取得したい情報

- 報告セグメント（有報の場合）または事業区分（HP の事業ページ）
- 各セグメントの売上高（直近 3-5 年）
- セグメント別売上構成比
- セグメント別営業利益率
- セグメント別 CAGR

### 非上場時の代替

セグメント別売上が取れないため、HP の事業区分を**事業数のみ列挙**し、各事業の概要・主要拠点・主要サービスを定性的にまとめる。「セグメント別売上構成は ✗未取得」と data-availability に明示。

---

## 論点 4: 会社としての収益性は？（revenue-analysis-pptx + financial-benchmark-pptx の 2 枚）

**目的**: (a) 全社の売上・EBITDA 推移、(b) 業界内競合との財務比較。

### 4-a. 売上・EBITDA 推移（revenue-analysis-pptx）

#### クエリ例

1. `{company_name} 売上高 推移 5 年`
2. `{company_name} EBITDA 営業利益 推移`
3. `{company_name} 決算 業績 過去`
4. `{company_name} 中期計画 業績見込み`
5. `{company_name} 通期見通し`
6. `{company_name} 年商 売上規模`

#### 取得したい情報

- 売上高（直近 5-7 年 + 当期見込み）
- EBITDA / 営業利益（同上）
- 売上 CAGR
- 通期見通し・中計目標

### 4-b. 業界内財務ベンチマーク（financial-benchmark-pptx）

#### クエリ例（{competitors[*]} を 1 社ずつ展開）

1. `{competitors[i]} 売上 営業利益率 推移`（i=0..N-1、社数分）
2. `{competitors[i]} ROE 自己資本比率 直近`
3. `{competitors[i]} EBITDA マージン`
4. `{industry} 業界 ランキング 売上`
5. `{industry} 業界 利益率 平均`

#### 取得したい情報

- 競合 5 社程度の売上・営業利益率・EBITDA・ROE・自己資本比率（直近 3 年）
- 対象会社が業界内でどのポジションか
- 業界平均値（業界統計）

---

## 論点 5: 株主・役員は？（shareholder-structure-pptx）

**目的**: 主要株主（議決権比率上位 10 社）と役員構成（取締役 / 監査役）を整理。

### 上場の場合のクエリ例

1. `{company_name} 主要株主 議決権比率`
2. `{company_name} 大株主 上位 10`
3. `{company_name} 取締役 役員報酬`
4. `{company_name} 役員構成 監査役`
5. `{company_name} 株主構成 安定株主`
6. `{company_name} EDGAR 有報 株主の状況`

### 非上場の場合のクエリ例

1. `{company_name} 役員一覧 取締役`
2. `{company_name} 経営陣 社長 副社長`
3. `{company_name} 親会社 持株会社`
4. `{company_name} 創業家 オーナー`
5. `{company_name} 統合報告書 役員紹介`

### 取得したい情報

- 主要株主名・議決権比率（上場のみ）
- 取締役の氏名・役職
- 監査役の氏名・役職
- 役員の在任期間・経歴（取れる範囲）
- 役員報酬（上場のみ、有報 開示）

### 非上場時の制約

- 株主構成・議決権比率は通常 **✗未取得**（公開義務なし）
- 役員構成は HP・統合報告書から取得可能
- 役員報酬は通常 ✗

---

## クエリ実行のガイドライン

- 各クエリ間で重複検索を避ける（既出の URL は再 fetch しない）
- 1 論点あたり **5-8 件**（多すぎても情報過多、少なすぎると裏取り不足）
- 取得した数値は **出典 + 取得日** をメモする（fact-check-reviewer の入力データになる）
- 公式ソース優先順位: **有報 > 統合報告書 > 公式 HP > 業界団体 > 業界紙 > 調査会社レポート > Wikipedia（一次ソース確認必須）**
- 非上場時は **公式 HP の会社案内 PDF が最高精度**、次いで NIKKEI COMPASS / FUMA / Baseconnect で売上規模を補強

---

## 出力形式

各論点について Web 検索が完了したら、以下の構造で内部メモを作成（Step 5 の `data_NN_*.json` 組み立てに使う）:

```markdown
## 論点 1: 会社の概要

### 取得済情報
- 商号: ○○株式会社
- 本社所在地: 東京都○○区...
- 設立: 19XX 年X月
- 資本金: X,XXX 万円
- 代表者: ○○ ○○
- 従業員数: X,XXX 名
- 主要事業: A 事業 / B 事業 / C 事業
- 上場: 東証プライム（コード XXXX） or 非上場

### 出典
- 公式 HP「会社概要」（取得日: 2026-04-29）
- 有価証券報告書 第 XX 期（上場時）

### 未取得・data_gap
- なし or 具体的に未取得項目を列挙
```

5 論点分を集約し、Step 2（data-availability）と Step 5（PPTX 生成）に渡す。
