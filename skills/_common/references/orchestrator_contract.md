# Orchestrator Contract — オーケストレーター間の共通契約

> **このファイルは `skills/_common/references/orchestrator_contract.md` です。**
> オーケストレータースキル（market-overview-agent / strategy-report-agent / smallcap-strategy-research 等）の SKILL.md からは、`<!-- source: skills/_common/references/orchestrator_contract.md (manual sync until D2) -->` コメント付きで**手動コピペ**してください。
> このファイルを変更したら `grep -rn "source: skills/_common/references/orchestrator_contract.md" skills/*/SKILL.md` で被参照スキルを全て検出し、コピペし直すこと（ISSUE-001 D2 で自動化検討中）。

オーケストレーターと下流ツール（`merge-pptxv2` / `visual-quality-reviewer`）の間で
受け渡す中間ファイルの正規スキーマを定義する。本ファイルが不変点であり、
個別スキルは本ファイルに準拠した構造で出力すること。

---

## 1. `merge_order.json` — オーケストレーター → merge-pptxv2 / visual-quality-reviewer

### 配置

`{{WORK_DIR}}/<run_id>/merge_order.json`

### スキーマ

```json
{
  "entries": [
    {
      "slide_number": 1,
      "file_name": "slide_01_exec_summary.pptx",
      "skill_name": "executive-summary-pptx",
      "data_file": "data_01_exec_summary.json",
      "category": "header"
    }
  ]
}
```

### フィールド定義

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `slide_number` | int | ✓ | 通し番号（1始まり）。`merge_warnings.json.slide_index` に転写される |
| `file_name` | str | ✓ | 個別 PPTX のファイル名（`{{WORK_DIR}}/<run_id>/` 配下） |
| `skill_name` | str | ✓ | 生成元スキル名。`visual-quality-reviewer` の自動修正ループが該当スキルの `fill_*.py` を再実行するために使う |
| `data_file` | str | ✓ | 入力 JSON のファイル名。自動修正ループで `regeneration_hint` に従って書き換える対象 |
| `category` | str | ✓ | デッキ内での役割。下記 4 値のいずれか |

### `category` の値域

| 値 | 用途 |
|---|---|
| `header` | エグゼクティブサマリー・目次など、セクション開始前の冒頭スライド |
| `content` | 通常のコンテンツスライド（チャート・テーブル・分析） |
| `section_divider` | 中扉（セクション区切り） |
| `footer` | データアベイラビリティ・付録など、末尾スライド |

正規ソース: `skills/market-overview-agent/references/deck_skeleton_standard.json`

### 検証ルール（merge-pptxv2 が assert）

- `category=section_divider` の **直後** のエントリは `category=content` でなければならない
  （中扉の連続、中扉直後の `header` / `footer`、中扉が末尾エントリは違反）
- 違反は `merge_warnings.json` に記録され、マージは継続する（`ValueError` を投げない）

---

## 2. `merge_warnings.json` — merge-pptxv2 → 下流（visual-quality-reviewer / ユーザー）

### 配置

出力 PPTX と同じディレクトリ（`{{OUTPUT_DIR}}/merge_warnings.json` または `{{WORK_DIR}}/<run_id>/merge_warnings.json`、merge-pptxv2 の第 1 引数で決まる）

### スキーマ

```json
[
  {
    "slide_index": 5,
    "type": "section_divider_position",
    "message": "slide 5 (section_divider) is followed by slide 6 (category='section_divider'); expected category='content'."
  }
]
```

### フィールド定義

| フィールド | 型 | 説明 |
|---|---|---|
| `slide_index` | int | 違反した `section_divider` の `slide_number`（merge_order.json から転写）。**§4.4 brand_fallback では `-1`** を入れる（特定スライドに紐付かない全体警告の意） |
| `type` | str | 警告種別。`section_divider_position`(merge-pptxv2 が出力) / `brand_fallback`(orchestrator が出力、§4.4 参照)。将来追加される可能性あり |
| `message` | str | 人間可読な違反内容 |

### 重要な前提

- **常時書き出される**: `--merge-order` 指定時は違反 0 件でも `[]` で出力される
- 下流（visual-quality-reviewer 等）は本ファイルの**存在**を前提に分岐できる
- マージ自体は警告があっても継続する。警告を無視するか、JSON を修正して再生成するかはオーケストレーターの判断

---

## 3. `regeneration_hint` — visual-quality-reviewer → 自動修正ループ

### 配置

`visual_review_report.json.issues[i].regeneration_hint`（visual-quality-reviewer の出力内）

### スキーマ（参考）

```json
{
  "slide_number": 4,
  "skill_name": "market-environment-pptx",
  "data_file": "data_04_market_environment.json",
  "severity": "high",
  "category": "text_overflow",
  "issue_summary": "main_message が 80 字で 65 字制限を超過、テンプレ枠から溢れている",
  "regeneration_hint": {
    "field": "main_message",
    "action": "shorten_to",
    "max_chars": 65,
    "guidance": "主語を1つに絞る、修飾語を削除（『主要な』『重要な』等）、数値は1つだけ残す"
  }
}
```

### 自動修正ループでの使い方

1. `slide_number` から `merge_order.json.entries[].slide_number` を引いて該当エントリを特定
2. `data_file` を `{{WORK_DIR}}/<run_id>/<data_file>` から読み込み
3. `regeneration_hint.field` を `regeneration_hint.action` に従って書き換える
4. `skill_name` の `fill_*.py` を**同じ `file_name` 出力で**再実行
5. 全修正完了後、`merge-pptxv2 --merge-order` を再実行
6. `visual-quality-reviewer` を再起動して `severity=high` が 0 になるまで（最大 2 ラウンド）繰り返す

詳細は `skills/_common/prompts/step_final_visual_review_loop.md` を参照。

---

## 4. scope.json — オーケストレーター内部で完結する真実源

### 配置

`{{WORK_DIR}}/<run_id>/scope.json`

### 役割

`scope.json` は Step 0 で確定した調査スコープ（地理・セグメント・年数・上限値・事業モデル境界等）を後続 Step に伝達するためのオーケストレーター内部のファイル。スキーマと共通フィールドは `skills/_common/prompts/step0_scope_clarification.md` を正本とする。

### 重要な責務分担: scope.json は **オーケストレーターのみ** が読む

| 読む | 読まない |
|---|---|
| オーケストレーター本体（Step 1 Web 検索クエリ・Step 5 スライド生成判断・Step 9 FactCheck_Report.md 注記） | 各 fill_*.py（market-environment / market-share / competitor-summary / market-kbf / positioning-map 等すべて） |

理由:
- `fill_*.py` を **単体起動**（オーケストレーター経由でなく開発者がデバッグで叩く）で動くようにする後方互換維持のため
- 個別 PPTX スキルは「JSON で渡された情報を忠実にスライド化する」責務のみを持ち、母集団の絞り込み判断はオーケストレーターの責務とする

### 具体的な責務（特に `included_business_models` / `excluded_segments`）

- `data_06_market_share.json` の母集団 = `included_business_models` の範囲内のプレイヤーに絞り込む（オーケストレーターが Step 1 Web 検索段階で実施）
- `data_08_competitor_summary.json` の比較対象 = 同上
- `data_10_market_kbf.json` の player_examples = 同上
- `data_12_data_availability.json` または最終 FactCheck_Report.md の冒頭注記 = `excluded_segments` が空配列でない場合に「本レポートでは <excluded_segments> を対象外として除外している」を明記
- 各 fill_*.py の入力 JSON にはすでに絞り込み済みのデータを渡す（fill_*.py は渡された JSON を信じてスライド化する）

### 後方互換

- `included_business_models = []`（空配列）は「全モデル統合扱い」を意味し、v0.2 までと同じ挙動（境界なし全プレイヤー対象）
- 既存の scope.json（`included_business_models` フィールドがない）は `[]` 同等として扱う

### `brand` フィールド（V1 brand-aware 拡張、Phase 0 で N 社 agnostic 化）

scope.json に以下のフィールドを追加（**いずれも任意**、未指定時は後方互換挙動）：

| キー | 型 | 値域 | デフォルト | 役割 |
|---|---|---|---|---|
| `brand` | string | `_common/brands/<id>/theme.json` が存在する任意の id（D1 命名規則 `^[a-z][a-z0-9_]{1,23}$` に準拠） | `"stellar_aiz"`（未指定時） | クライアント別 PPTX フォーマット切替 |
| `brand_label` | string | 自由文字列 | （未指定可） | UI / 納品物メタデータ用の表示名 |

**N 社 agnostic 設計**: 値域は静的列挙ではなく、`skills/_common/lib/brand_resolver.py` の `_discover_brands()` が返す結果を真実源とする。新ブランド追加（C 社・D 社…）は `_common/brands/<新 id>/theme.json` を配置するだけで、本ドキュメント・各 agent SKILL.md の改修は不要。

#### 4.1 責務分担（既存原則の例外）

「scope.json は orchestrator のみ読む」原則は維持しつつ、`brand` は **CLI 引数 `--brand` で fill_*.py に伝播**することを明示する。fill_*.py は scope.json を直接 open しない（既存の単体起動互換も維持）：

```bash
# orchestrator 内部で:
brand=$(jq -r '.brand // "stellar_aiz"' $WORK_DIR/$RUN_ID/scope.json)
python fill_*.py --brand $brand --data ... --output ...
```

#### 4.2 Step 0 での brand 確定 UX

agent 系 SKILL.md は Step 0 冒頭で `AskUserQuestion` により brand を都度確定する（env / config 固定はしない）。共通プロンプトは `skills/_common/prompts/step0_brand_clarification.md` を正本とし、各 agent は手動コピペで参照する（manual sync until D2）。

#### 4.3 fill スキルの brand 対応宣言（SKILL.md frontmatter）

各 fill スキルの SKILL.md frontmatter に `supported_brands` フィールドを追加することで、当該スキルが対応している brand を宣言する：

```yaml
---
name: example-pptx
description: ...
supported_brands: [stellar_aiz, roleup]
---
```

| 形式 | 解釈 |
|---|---|
| `supported_brands: [a, b]`（インライン list） | 明示的に対応 brand を列挙 |
| フィールド未指定 | `[stellar_aiz]` 扱い（後方互換、Phase 1 までの暫定） |
| ブロック list 形式 (`- a` / `- b`) | **未対応**(`brand_resolver._read_supported_brands` の制限、Phase 0 簡素化) |

orchestrator は fill 起動前に `is_brand_supported_by_skill(skill_dir, brand)` で対応有無を事前検出する。

#### 4.4 未対応 fill への warning + stella fallback

scope.json の brand が `stellar_aiz` 以外で、当該 fill が未対応の場合、orchestrator は以下を実施する（ユーザー Q3 確定: 2026-05-05）：

1. `warnings.warn(...)` で RuntimeWarning を発出（agent 内部ログに記録）
2. `merge_warnings.json` に `type: "brand_fallback"` のエントリを追記（**§2 のスキーマ拡張**）：
   ```json
   {
     "slide_index": -1,
     "type": "brand_fallback",
     "message": "skill 'example-pptx' does not support brand 'roleup'; falling back to 'stellar_aiz'"
   }
   ```
   `slide_index = -1` は「全体に対する警告（特定スライドに紐付かない）」を意味する。
3. fill には `--brand stellar_aiz` を渡す（fill 本体は brand-agnostic のまま動作）
4. 全 fill 完了後、warning 件数を集計してユーザーに納品確認 Step で提示

orchestrator が既に `--brand` を渡せる pilot 3（V1 brand-aware 化済）で対応 brand なら fallback は不要。

#### 4.5 V1 brand-aware 化済の fill スクリプト

- `fill_customer_profile.py`（commit `b767ee3`）
- `fill_company_history.py`（commit `c199f03`）
- `fill_market_environment.py`（commit `128fa15`）

残り 25 fill スクリプトは ISSUE-010 Phase 2 で順次対応（BDD 系から優先）。Phase 1 では全 fill SKILL.md に `supported_brands: [stellar_aiz]` を一括追加して fallback 検出を機能させる。

#### 4.6 詳細

- API: `skills/_common/lib/brand_resolver.py`（`_discover_brands` / `_validate_brand_id` / `is_brand_supported_by_skill` / `resolve_brand_with_fallback`）
- 移行手順: `skills/_common/references/brand_migration_guide.md`
- Step 0 共通プロンプト: `skills/_common/prompts/step0_brand_clarification.md`

---

## 5. オーケストレーター実装時のチェックリスト

新規オーケストレーターを書く際 / 既存オーケストレーターを改修する際は、以下を満たすこと:

- [ ] `merge_order.json` を `{{WORK_DIR}}/<run_id>/` に書き出している
- [ ] `merge_order.json` の各 entry に `slide_number` / `file_name` / `skill_name` / `data_file` / `category` が揃っている
- [ ] `category` は `header` / `content` / `section_divider` / `footer` のいずれか
- [ ] `merge-pptxv2` を `--merge-order` 付きで起動している
- [ ] マージ後 `merge_warnings.json` を確認している（`section_divider_position` 違反 0 件）
- [ ] `visual-quality-reviewer` に `merge_order` パスを渡している
- [ ] 自動修正ループのカウンタを持っている（無限ループ防止、最大 2 ラウンド）
- [ ] `scope.json` を `{{WORK_DIR}}/<run_id>/` に書き出している（市場系オーケストレーター必須、smallcap 等は適用外）
- [ ] Step 0.5 で異種事業モデル併存を検知し `included_business_models` / `excluded_segments` を確定している
- [ ] Step 1 Web 検索クエリ・data_06/08/10 の母集団絞り込みを `included_business_models` の範囲で実施している
- [ ] `excluded_segments` が空配列でない場合、data_12 または FactCheck_Report.md 冒頭で除外を明記している
