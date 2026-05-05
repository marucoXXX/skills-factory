# Step 0: ブランド確認（共通パターン）

> **このファイルは `skills/_common/prompts/step0_brand_clarification.md` です。**
> オーケストレータースキル（market-overview-agent / company-deepdive-agent / business-deepdive-agent / strategy-report-agent / smallcap-strategy-research / bdd-init / comparison-synthesis-agent 等）の SKILL.md の Step 0 冒頭から、`<!-- source: skills/_common/prompts/step0_brand_clarification.md (manual sync until D2) -->` コメント付きで**手動コピペ**してください。
> このファイルを変更したら `grep -rn "source: skills/_common/prompts/step0_brand_clarification.md" skills/*/SKILL.md` で被参照スキルを全て検出し、コピペし直すこと（ISSUE-001 D2 で自動化検討中）。

スコープ確認に先立ち、本デッキの**出力ブランド**（クライアント別 PPTX フォーマット）を確定し、`scope.json.brand` に保存する。
ブランドは fill スキルの色・フォント・レイアウト・出所必須化等の挙動を切り替える単一の真実源。

---

## 共通原則

- **毎回 `AskUserQuestion` で確定する**。env / config 固定はしない（ユーザー Q1 確定: 2026-05-05）。
- **agnostic 設計**: 選択肢は実行時に `_common/brands/*/theme.json` から動的取得する。新ブランド追加（C 社・D 社…）は `_common/brands/<id>/theme.json` を配置するだけで、本プロンプトの改修は不要。
- **デフォルト値**: `stellar_aiz`（既存運用との後方互換）。
- **brand id の正規化**: スネークケース、半角英小文字 + 数字 + アンダースコア、24 字以内、先頭は英字（`^[a-z][a-z0-9_]{1,23}$`）。

---

## AskUserQuestion テンプレ

```python
import json, os, sys
sys.path.insert(0, os.path.join(SKILL_DIR, "..", "_common", "lib"))
from brand_resolver import _discover_brands, _BRANDS_DIR

discovered = _discover_brands()  # ('roleup', 'stellar_aiz', ...)
options = []
for brand_id in discovered:
    with open(os.path.join(_BRANDS_DIR, brand_id, "theme.json")) as f:
        theme_data = json.load(f)
    options.append({
        "label": theme_data.get("label", brand_id),
        "description": f"id={brand_id}（{theme_data.get('description', '')}）",
    })
# Recommended は既定 brand を先頭にして "(Recommended)" サフィックス付与
# （実装は agent 側 SKILL.md で固有のテンプレに従う）

AskUserQuestion(
    question="このデッキはどのクライアント・ブランドのフォーマットで出力しますか？",
    header="ブランド",
    options=options,  # Other は AskUserQuestion が自動で追加（自由記述で id を入力可能）
    multiSelect=False,
)
```

**選択肢を `_discover_brands()` で動的取得する理由**: 新ブランドを `_common/brands/<id>/theme.json` で追加した瞬間に全 agent の選択肢に自動反映され、prompt や SKILL.md の改修が不要になる（N 社 agnostic 設計）。

**自由記述の扱い**: ユーザーが「Other」で `_discover_brands()` に含まれない brand id を入力した場合は **`AskUserQuestion` を再実行**（その id 用の theme.json が未配置のため fill スキルが起動できない）。`_validate_brand_id` で命名規則違反も同時に弾く。

---

## scope.json への保存

確定した brand を `{{WORK_DIR}}/<run_id>/scope.json` に書き込む（既存 schema に追記）：

```json
{
  "market_name": "...",
  "geography": "...",
  "brand": "roleup",
  "brand_label": "Roleup（A4 横、Yu Gothic UI、褐色アクセント）",
  "...": "..."
}
```

| キー | 型 | 値域 | 必須 | 役割 |
|---|---|---|---|---|
| `brand` | string | `_discover_brands()` の戻り値のいずれか | 任意（未指定時は `stellar_aiz` 扱い） | クライアント別 PPTX フォーマット切替 |
| `brand_label` | string | 自由文字列 | 任意 | UI 表示用（最終納品物のメタデータ・summary 等） |

**保存タイミング**: agent の Step 0 で他のスコープ項目（market_name / target_company / geography 等）を確定する**前または直後**に `brand` を確定し、scope.json を初回書き込み時に同梱する。

---

## fill スキル起動時の brand 伝播（orchestrator の責務）

scope.json の `brand` を CLI 引数 `--brand <id>` として全 fill スキルに伝播する。fill スキルは scope.json を直接 open しない（単体起動互換のため、`orchestrator_contract.md §4` 参照）。

```bash
# orchestrator 内部:
brand=$(jq -r '.brand // "stellar_aiz"' "$WORK_DIR/$RUN_ID/scope.json")
python "$SKILL_DIR/scripts/fill_*.py" --brand "$brand" --data "..." --output "..."
```

---

## 未対応 fill スキル検出と warning + stella fallback（D4）

scope.json の brand が `stellar_aiz` 以外のとき、各 fill スキルが**当該 brand に対応宣言しているか**を `is_brand_supported_by_skill()` で事前検出し、未対応なら warning ログを残して stella で起動する（ユーザー Q3 確定: 2026-05-05）。

### 対応宣言の場所

各 fill スキルの SKILL.md frontmatter に `supported_brands: [stellar_aiz, roleup, ...]` を追記。**未指定の SKILL.md は `[stellar_aiz]` 扱い**（Phase 1 までの後方互換）。

```yaml
---
name: example-pptx
description: ...
supported_brands: [stellar_aiz, roleup]
---
```

### orchestrator の事前検出フロー

```python
import os, sys
sys.path.insert(0, os.path.join(REPO_ROOT, "skills/_common/lib"))
from brand_resolver import is_brand_supported_by_skill

scope_brand = "roleup"  # scope.json から読み込み済み
fill_brand = scope_brand
if not is_brand_supported_by_skill(skill_dir, scope_brand):
    # 警告ログ + merge_warnings.json への追記
    msg = (f"skill {os.path.basename(skill_dir)!r} does not support brand "
           f"{scope_brand!r}; falling back to 'stellar_aiz'")
    # merge_warnings.json への追記スキーマは orchestrator_contract.md §2 参照:
    #   {"slide_index": -1, "type": "brand_fallback", "message": <msg>}
    # （slide_index = -1 は「全体に対する警告」を意味する）
    fill_brand = "stellar_aiz"

# fill 起動（fill スキル本体は --brand stellar_aiz を受け取って従来通り動く）
subprocess.run([
    "python", os.path.join(skill_dir, "scripts", "fill_xxx.py"),
    "--brand", fill_brand, "--data", ..., "--output", ...,
])
```

### warning が記録されたときのユーザー伝達

- 全 fill 完了 → merge → visual review の流れで、**最後の Step**（または Step 8 等の納品確認 Step）でユーザーに warning 件数と内訳を提示する：
  > 「本デッキは brand=`roleup` で出力しましたが、{N} 件のスキルが当該 brand に未対応のため `stellar_aiz` で生成されています。一覧: ...」
- ユーザーは「このまま納品」「該当スキルを brand-aware 化してから再生成」のいずれかを選択できる。

---

## アンチパターン

- ❌ env や `.claude/settings.json` で brand を固定し、AskUserQuestion をスキップする（ユーザー Q1 違反、複数クライアント運用で誤出力の温床）
- ❌ ハードコードされた brand リストで AskUserQuestion を組む（agnostic 設計違反、新ブランド追加時に全 agent 改修が必要になる）
- ❌ unsupported brand 検出時に hard-fail する（ユーザー Q3 違反、デッキ全体が止まる）
- ❌ unsupported brand 検出時に**警告なく** stella で出力する（silent fallback、ユーザーが品質劣化に気付けない）
- ❌ scope.json の `brand` を fill スキル本体（fill_*.py）から open する（orchestrator_contract.md §4 違反、単体起動互換が壊れる）

---

## 関連ドキュメント

- `skills/_common/lib/brand_resolver.py` — `_discover_brands` / `_validate_brand_id` / `is_brand_supported_by_skill` / `resolve_brand_with_fallback` の API
- `skills/_common/references/orchestrator_contract.md` §4 — scope.json と brand 伝播の責務分担
- `skills/_common/references/brand_migration_guide.md` — Pattern A/B/C による brand-aware 化手順（fill スキル開発者向け）
- `skills/_common/prompts/step0_scope_clarification.md` — Step 0 の他のスコープ項目
