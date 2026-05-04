# Brand Migration Guide — 残り PPTX スキルの brand-aware 化手順

V1（2026-05、format_add ブランチ、commit 4d752b1〜128fa15）で
**Pilot 3 スキル**（customer-profile-pptx / company-history-pptx / market-environment-pptx）
を brand-aware 化し、`stellar_aiz` / `roleup` の出力切替機構を確立した。
本ガイドは V2 以降で残り 25 fill scripts に展開する際の手順を残す。

---

## 1. アーキテクチャ概要

```
scope.json (brand: "roleup")
    ↓ orchestrator が読む
fill_*.py --brand roleup
    ↓
brand_resolver.resolve_brand("roleup", SKILL_DIR)
    ├─ skills/_common/brands/roleup/theme.json     (色・フォント・チャートパレット)
    └─ skills/<skill>/assets/roleup/layout.json    (skill 固有座標)
    → BrandTheme dataclass
    ↓
fill_*.py が theme.color() / theme.font_ea / theme.layout() / theme.pt() / theme.hex() で resolve
+ template_path = SKILL_DIR/assets/<brand>/<skill>-template.pptx
  （curated brand template が無ければ stella にフォールバック）
```

### 設計思想
- **theme（色・フォント・サイズ）は brand 共通** → `_common/brands/<id>/theme.json`
- **template と layout（座標）は skill 固有** → `<skill>/assets/<brand>/`
- **fill_*.py は scope.json を読まない**（CLI `--brand` で伝播）→ 単体起動互換維持

---

## 2. スキル分類（改修コスト）

V1 Pilot 3 の経験から、PPTX スキルは以下 3 パターンに分かれる：

### Pattern A: hardcode 駆動（重）
fill_*.py 内で `RGBColor(...)`, `FONT_NAME = "Meiryo UI"`, `Pt(14)`, `Inches(...)`,
inline `<a:srgbClr val="4E79A7">` が多数定義され、スクリプト側で色・フォント・座標を完全制御。

**例**: `customer-profile-pptx`, `market-environment-pptx`
**改修コスト**: 中 〜 大（90分 〜 3時間 / スキル）
**手順**: 全 hardcode 定数を module 変数化 → `_apply_theme(theme)` で再代入。
inline OOXML hex 文字列 (`'val': '4E79A7'`) は別途 `ACCENT_*_HEX` 等の module 変数を導入して置換。

### Pattern B: テンプレ rPr/tcPr 駆動（軽）
`copy.deepcopy(old_table.cell(0,0)._tc.find(qn("a:tcPr")))` のように、
テンプレ pptx の rPr/tcPr 要素をコピーして使う設計。スクリプト側の色・フォント定数は最小（または無し）。

**例**: `company-history-pptx`
**改修コスト**: 小（30 分 / スキル）
**手順**: `--brand` 引数追加と `--template` の任意化（テンプレ解決を brand 経由）のみ。
slide_height などレイアウト計算で brand 依存が生じる箇所は `prs.slide_height` から動的取得に変更。

### Pattern C: HTML→Playwright スクリーンショット駆動（変則）
`html2pptx` / `gantt-chart-pptx` / `current-period-forecast-pptx` 等。
HTML を Playwright でレンダリングして PNG 化し、PPTX に画像挿入する方式。
HTML 側に CSS で色・フォントが定義される。

**例**: `gantt-chart-pptx`, `customer-sales-detail-pptx`
**改修コスト**: 中（HTML テンプレートの brand-aware 化が必要、60-90 分 / スキル）
**手順**: HTML テンプレートを Jinja 化し、CSS 変数を theme.json から注入。

---

## 3. Pilot 3 改修パターン（テンプレート）

### Step 1: bootstrap import を追加

```python
import argparse, os, sys
# ...other imports...

# ── brand_resolver bootstrap (skills/_common/lib/brand_resolver.py) ──
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_DIR, "..", "_common", "lib"))
from brand_resolver import resolve_brand, add_brand_arg  # noqa: E402
```

### Step 2: module-level 定数を「stella 既定値 + 後で _apply_theme で再代入」に

```python
# Default = stella; reassigned in main() via _apply_theme(theme)
COLOR_TEXT = RGBColor(0x33, 0x33, 0x33)
FONT_NAME_JP = "Meiryo UI"
PANEL_Y = Inches(1.50)
# ...
TEXT_HEX = "333333"
ACCENT_REVENUE_BAR_HEX = "4E79A7"


def _apply_theme(theme):
    global COLOR_TEXT, FONT_NAME_JP, PANEL_Y
    global TEXT_HEX, ACCENT_REVENUE_BAR_HEX
    COLOR_TEXT = theme.color("text")
    FONT_NAME_JP = theme.font_ea
    PANEL_Y = theme.layout("panel_y_in")
    TEXT_HEX = theme.hex_no_hash("text")
    ACCENT_REVENUE_BAR_HEX = theme.hex_no_hash("accent_revenue_bar")
    # ...
```

### Step 3: main() で brand 引数を追加し、theme を resolve

```python
def main():
    parser = argparse.ArgumentParser(...)
    parser.add_argument("--data", required=True)
    parser.add_argument("--template", required=False, default=None)  # 任意化
    parser.add_argument("--output", required=True)
    add_brand_arg(parser)
    args = parser.parse_args()

    theme = resolve_brand(args.brand, SKILL_DIR)
    _apply_theme(theme)
    template_path = args.template or theme.template_path(SKILL_DIR, "<skill-name>")
    print(f"  ✓ Brand: {theme.id} ({theme.label})")

    prs = Presentation(template_path)
    # ...
```

### Step 4: アセット移動と layout.json 作成

```bash
mkdir -p skills/<skill>-pptx/assets/{stellar_aiz,roleup}
git mv skills/<skill>-pptx/assets/<skill>-template.pptx \
       skills/<skill>-pptx/assets/stellar_aiz/
```

`assets/stellar_aiz/layout.json`: 現状の hardcode 座標を JSON 化（regression-zero）
`assets/roleup/layout.json`: V1 placeholder（stella と同値、curated roleup テンプレ未配置時はフォールバック）

### Step 5: SKILL.md 更新
- `--brand` 引数を実行例に追記
- アセット表に `assets/<brand>/` 配置を反映
- オーケストレーター連携節に「parent は scope.json `brand` を `--brand` で渡す」追記

---

## 4. theme.json と chart 色の二重源ルール

ロールアップテンプレ pptx の `theme1.xml` の accent と、fill_*.py の inline `<a:srgbClr>` で
**色源が 2 箇所**ある。設計上の割り切り：

- **テンプレ accent**: スライドマスター・レイアウトの装飾要素（タイトルバー等）専用
- **fill_*.py の `<a:srgbClr>`**: チャート系列色 / カスタム強調色（theme.json から resolve）

両者が乖離していても運用上問題ない設計。fill 側が優先される箇所は theme.json 単一情報源で OK。

---

## 5. ISSUE-001（@import 機構）との関係

stella 内 5 スキルの `chart_palette.md` 手動同期は ISSUE-001 で v0.3 検討中。
brand-aware 化はこれを以下のように再構築：

| | brand-aware 前 | brand-aware 後 |
|---|---|---|
| stella の chart_palette 同期源 | `_common/styles/chart_palette.md` (手動 5 同期) | 〃（既存維持、stella のみ） |
| roleup の chart_palette 同期源 | — | `_common/brands/roleup/theme.json` (1 ファイル、自動 resolve) |
| 同期負荷 | 5 ファイル × 編集ごと | 0（roleup は theme.json 単一） |

**roleup 以降の新ブランドは theme.json 単一源**。stella の手動同期負荷は新ブランドに伝播しない。
将来 ISSUE-001 D2（@import 機構）が稼働したら、stella の chart_palette.md も
`@import "skills/_common/brands/stellar_aiz/theme.json#chart_palette"` 化して 1 本化可能。

---

## 6. Yu Gothic UI on macOS セットアップ

Roleup 仕様の `Yu Gothic UI` は macOS 標準搭載されない。3 段階の対策：

### (A) Microsoft Office for Mac インストール（正攻法）
Microsoft 365 サブスクライバーなら Office for Mac インストール時に Yu Gothic UI 同梱。

### (B) fontconfig エイリアス（代替）
`~/.config/fontconfig/fonts.conf` に以下を配置：

```xml
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <alias>
    <family>Yu Gothic UI</family>
    <prefer>
      <family>Hiragino Sans</family>
      <family>YuGothic</family>
    </prefer>
  </alias>
</fontconfig>
```

確認: `fc-match "Yu Gothic UI"` → `Hiragino Sans` を返せば成功。
**LibreOffice / Playwright（visual-quality-reviewer の PNG 化）に対しては有効**。
PowerPoint Mac / Keynote は fontconfig を読まない。

### (C) Windows 環境で最終チェック
Roleup 納品前の最終視覚レビューは Windows / Office for Mac で行う。

**Deliverable PPTX の中身は `Yu Gothic UI` 指定のまま固定**（Roleup 社内 Windows 環境で正しく表示）。
macOS 視覚レビューは fallback フォントでの近似であり、最終確認は別途実施。

---

## 7. 残り 25 スキル展開チェックリスト（V2 以降）

各スキルの brand-aware 化時に確認：

- [ ] スキル分類（Pattern A / B / C）を判定
- [ ] fill_*.py に bootstrap import 追加
- [ ] hardcode 定数を module 変数化、`_apply_theme(theme)` 関数追加（Pattern A の場合）
- [ ] inline OOXML hex 文字列を `*_HEX` 変数経由に置換
- [ ] `--brand` 引数追加、`--template` を任意化
- [ ] テンプレを `assets/stellar_aiz/` へ git mv
- [ ] `assets/{stellar_aiz,roleup}/layout.json` 作成
- [ ] regression-zero 確認: `--brand` 未指定 / `stellar_aiz` 明示の出力が現状と diff 無し（random axId 等は許容）
- [ ] `--brand roleup` で例外なく完走（fill 生成箇所が roleup 色 / Yu Gothic UI に切替わる）
- [ ] SKILL.md に `--brand` を文書化、アセット表更新

### V2 で curated roleup template を入れる際の追加作業
- [ ] PowerPoint で A4 横（11.69×8.27）の Roleup テンプレを作成、shape 名を stella と合わせる
- [ ] `assets/roleup/<skill>-template.pptx` に配置
- [ ] `assets/roleup/layout.json` を A4 横向け座標に更新
- [ ] 視覚レビュー（visual-quality-reviewer + Office for Mac / Windows VM）

---

## 8. 参考コミット

- Phase A 基盤（commit `4d752b1`）: theme.json + brand_resolver.py + build_skill.py 同期機能
- Phase B-1（commit `b767ee3`）: customer-profile-pptx (Pattern A 代表)
- Phase B-2（commit `c199f03`）: company-history-pptx (Pattern B 代表)
- Phase B-3（commit `128fa15`）: market-environment-pptx (Pattern A + chart_palette)

これらの diff を read-only に参照すれば、改修パターンが具体例と共に把握できる。
