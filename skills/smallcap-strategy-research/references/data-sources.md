# データソース一覧（共通リファレンス）

本スキルの全エージェントが参照するデータソースの共通カタログ。
各エージェントが自分の責務に合ったソースを選択する際の参照資料。

---

## A. 公的・無料DB（最優先）

### A-1. 登記・法人基本情報

| データソース | URL | 何が取れるか | 信頼度 | エージェント |
|----|----|------------|------|------------|
| 法人番号公表サイト | https://www.houjin-bangou.nta.go.jp/ | 法人番号、商号、本店所在地、変更履歴 | high | Corporate Registry (Phase 2) |
| EDINET | https://disclosure.edinet-fsa.go.jp/ | 有報、社債発行届出、大量保有報告書 | high | Financial Signals |
| 建設業者・宅建業者等企業情報検索システム | 国土交通省 | 建設業許可、有効期限、経営事項審査結果 | high | Corporate Registry (Phase 2) |

### A-2. 財務・決算

| データソース | URL | 何が取れるか | 信頼度 | エージェント |
|----|----|------------|------|------------|
| 官報決算公告 | 官報検索サイト（公開範囲） | BS/PL主要項目、資本金、純利益 | high | Financial Signals |
| 国税庁法人税情報公表サイト | https://houjin.nta.go.jp/ | 法人税の高額納税企業（対象が該当すれば） | high | Financial Signals |

### A-3. 補助金採択

| データソース | URL | 何が取れるか | 信頼度 | エージェント |
|----|----|------------|------|------------|
| jGrants | https://www.jgrants-portal.go.jp/ | 経産省系補助金の採択事業者・事業計画概要 | high | Strategic Signals |
| ものづくり補助金成果事例DB | https://portal.monodukuri-hojo.jp/ | 採択案件の事業内容・成果 | high | Strategic Signals |
| 事業再構築補助金 採択事業者一覧 | 中小機構 | 採択事業者、事業計画概要 | high | Strategic Signals |
| NEDO採択事業者一覧 | https://www.nedo.go.jp/ | R&D系国庫事業の採択事業者 | high | Strategic Signals |

### A-4. 知財

| データソース | URL | 何が取れるか | 信頼度 | エージェント |
|----|----|------------|------|------------|
| J-PlatPat | https://www.j-platpat.inpit.go.jp/ | 特許・実用新案・意匠・商標の出願・登録情報 | high | Strategic Signals |

### A-5. 業界団体・統計

| データソース | 何が取れるか | 信頼度 | エージェント |
|----|------------|------|------------|
| 業界団体の会員名簿（例: 日本機械工業連合会、化学工業協会、フードサービス協会） | 業界内の企業一覧、役員構成、統計資料 | medium | Industry Context (Phase 2) |
| 経済産業省 / 中小企業庁の業界統計 | 業界規模、企業数、集中度 | high | Industry Context (Phase 2) |
| 地方経済産業局の地域経済動向 | 地域内の企業動向、ランキング | medium | Industry Context (Phase 2) |

---

## B. プレス・メディア

| データソース | URL | 何が取れるか | 信頼度 | エージェント |
|----|----|------------|------|------------|
| PR TIMES | https://prtimes.jp/ | プレスリリース全文 | medium | Strategic Signals |
| @Press | https://www.atpress.ne.jp/ | プレスリリース全文 | medium | Strategic Signals |
| 共同通信PRワイヤー | https://kyodonewsprwire.jp/ | プレスリリース全文 | medium | Strategic Signals |
| 日経ビジネス・日経産業新聞 | https://www.nikkei.com/ | 業績報道、トップインタビュー | medium | Financial / Strategic |
| 日刊工業新聞 | https://www.nikkan.co.jp/ | 製造業向け詳細報道 | medium | Financial / Strategic / Industry |
| 地方紙（例: 中日新聞、北海道新聞、西日本新聞） | 各紙HP | 地元企業の詳細報道、工場訪問記事 | medium | Industry Context (Phase 2) |

---

## C. 求人・組織情報

| データソース | URL | 何が取れるか | 信頼度 | エージェント |
|----|----|------------|------|------------|
| Indeed | https://jp.indeed.com/ | 求人ポジション、年収レンジ | medium | Talent & Org (Phase 2) |
| リクナビ NEXT | https://next.rikunabi.com/ | 求人、企業情報、求める人物像 | medium | Talent & Org (Phase 2) |
| マイナビ | https://mynavi.jp/ | 求人、会社説明会情報 | medium | Talent & Org (Phase 2) |
| Wantedly | https://www.wantedly.com/ | ミッション・ビジョン系の発信、フォロワー数 | medium | Talent & Org (Phase 2) |
| Green | https://www.green-japan.com/ | IT系求人 | medium | Talent & Org (Phase 2) |
| BizReach | https://www.bizreach.jp/ | ハイクラス求人、ヘッドハンティング案件 | medium | Talent & Org (Phase 2) |
| OpenWork (vorkers) | https://www.openwork.jp/ | 従業員・退職者レビュー、年収情報 | low | Talent & Org (Phase 2) |
| 転職会議 | https://jobtalk.jp/ | 退職者レビュー、面接口コミ | low | Talent & Org (Phase 2) |
| LinkedIn | https://www.linkedin.com/ | 役員・社員の経歴、在籍期間 | medium | Talent & Org (Phase 2) |

---

## D. 経営者・発信情報

| データソース | 何が取れるか | 信頼度 | エージェント |
|----|------------|------|------------|
| X (旧Twitter) | 経営者の発言、重視テーマの頻度変化 | low-medium | Strategic Signals |
| LinkedIn 投稿 | 経営者・役員のビジネス発信 | medium | Strategic Signals |
| note | 経営者・社員の中長文発信（事業の考え、採用方針等） | medium | Strategic Signals |
| 自社ブログ | 経営者メッセージ、製品ブログ、採用ブログ | medium | Strategic Signals |

---

## E. ユーザー提供ファイル（最優先）

`{{INPUT_DIR}}/` にアップロードされたファイルは、Webより優先して参照する。

| ファイル種別 | 最優先エージェント | 取得情報 | 信頼度 |
|------------|------------------|---------|------|
| 登記簿謄本PDF | Corporate Registry (Phase 2) | 資本金推移、役員、事業目的、本支店 | high |
| 官報決算公告PDF | Financial Signals | BS/PL主要項目 | high |
| TDB/TSRレポートPDF | Financial Signals | 売上・利益推移、主要取引先、業況評価 | high |
| IM（Information Memorandum） | Financial / Strategic | 全方位（財務・戦略・組織） | high |
| 中期経営計画書 | Strategic Signals | 戦略発信、中期目標 | high |
| 業界レポート（矢野・富士経済等） | Industry Context (Phase 2) | 業界規模、競合動向 | high |

---

## F. アクセス禁止（有償DBのスクレイピング禁止）

以下へのスクレイピングは **利用規約違反** のため絶対に行わない。
ユーザーがPDF/テキストをアップロードした場合のみ解析する:

- TDB（帝国データバンク）会員エリア
- TSR（東京商工リサーチ）会員エリア
- 商業登記情報サービス（法務省）有料取得分
- 官報検索サービス有料版
- 業界有料DB（矢野経済、富士経済、SPEEDA、スピーダ他）

---

## G. ソース選択のガイドライン

### 優先順位

1. ユーザーアップロード（A〜F のどれに該当しても最優先）
2. 公的・無料DB（A）
3. プレス・メディア（B）
4. 求人・組織情報（C）— Phase 2以降
5. 経営者・発信情報（D）

### 独立ソースの判定（triangulation）

同じ情報が複数ソースで確認できた場合、**`source_type` が異なる** ものを独立ソースとしてカウント。
例:
- ✓ 独立: `gazette`（官報） と `press`（自社プレス） で売上高が一致
- ✗ 独立でない: `press`（PR TIMES） と `web`（自社HP） — どちらも企業発信で独立性が低い

例外: 同じ `source_type` でも **異なる発信主体** であれば独立として扱う（例: `web` の業界紙記事と `web` の商工会議所発表は独立）
