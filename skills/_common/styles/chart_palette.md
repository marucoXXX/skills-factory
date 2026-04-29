# Market Overview Report 共通配色仕様

このファイルは正本仕様。各 `fill_*.py` スクリプトの色定数（`CHART_PALETTE` / `OTHER_COLOR` / `TARGET_COLOR` / `LABEL_BAR_COLOR` / `LABEL_BG_COLOR`）を本ファイルと同期させること。
`build_skill.py` に `@import` 機構が無いため手動同期（ISSUE-001 で v0.3 検討中）。

---

## 1. データチャート用パレット（CHART_PALETTE）

P4 棒（market-environment）、P6 ドーナツ（market-share）、P7 バブル（positioning-map）など「系列を識別するための色」に使う。

| Idx | Hex | 用途 |
|---|---|---|
| 0 | `#4E79A7` | 青（単一系列のデフォルト、複数系列の1番目） |
| 1 | `#F28E2B` | オレンジ |
| 2 | `#59A14F` | 緑 |
| 3 | `#76B7B2` | ティール |
| 4 | `#EDC948` | 黄 |
| 5 | `#B07AA1` | 紫 |
| 6 | `#FF9DA7` | ピンク |
| 7 | `#9C755F` | 茶 |

**TARGET_COLOR (`#E15759` 赤) と OTHER_COLOR (`#BAB0AC` 灰) は palette 外で固定** し、それぞれ「対象会社」「その他系」エントリに強制適用する。意味付き色を palette から除外することで、palette 引きの結果と意味付け色の衝突（例: 配列 index = 3 で赤を引いて target と被る）を防ぐ。

### 適用ルール

1. JSON の `color` フィールドは **読まない**（後方互換のため受け取りはする、無視する）
2. **単一系列** → `CHART_PALETTE[0] = #4E79A7` を使う
3. **複数系列** → 「その他」「target」を **スキップせず**、`players` 配列の index で `CHART_PALETTE[i % len(CHART_PALETTE)]` を引く（P6/P7 で同じ社が同じ色になるよう統一）
4. 例外: 「その他」系エントリ（前方一致: `name.startswith("その他") or "Others" or "other"`）は **OTHER_COLOR=`#BAB0AC`** に強制上書き
5. 例外: positioning-map の `target_company` と完全一致するエントリは **TARGET_COLOR=`#E15759`** に強制上書き（赤強調）
6. **`NON_TARGET_PALETTE` は廃止**: 旧実装で「target を除外した独自 palette を非ターゲットだけで連番引き」していたが、target を palette から除外すれば配列 index 直引きで衝突せず、P6/P7 のロジックを揃えられるため不要

### 標準ヘルパー関数

各スキルの `fill_*.py` に同名で実装する:

```python
def _palette_color(index: int, total: int) -> str:
    """系列インデックスからチャート色を決定。JSON の color は無視。"""
    if total <= 1:
        return CHART_PALETTE[0]
    return CHART_PALETTE[index % len(CHART_PALETTE)]


def _is_other_player(name: str) -> bool:
    """「その他」系エントリの前方一致判定（"その他工房系・中小メーカー" などにも対応）。"""
    if not name:
        return False
    return (
        name.startswith("その他")
        or name.startswith("Others")
        or name.lower().startswith("other")
    )
```

---

## 2. 意味ラベル用カラー（モノトーン青）

P1 のカテゴリラベル、P11 の PEST 象限ヘッダーなど「分類を視覚化するための色」は、
**カラフルにせず単色青で統一**する。

| 用途 | Hex |
|---|---|
| ラベルバー / ヘッダー本体（LABEL_BAR_COLOR） | **`#4E79A7`** （CHART_PALETTE[0] と同じ青） |
| 象限の塗り背景・淡色（LABEL_BG_COLOR） | `#E8EEF5` （青の極淡トーン） |
| ヘッダー上の文字色 | `#FFFFFF` |

### 適用ルール

1. **executive-summary-pptx (P1)** の `CATEGORY_COLORS` dict は使わず、すべての findings の category バー（▍）を `#4E79A7` で塗る
2. **pest-analysis-pptx (P11)** の `header_color` は P/E/S/T 共通で `#4E79A7`、`body_color` は共通で `#E8EEF5`
3. **impact 指標**（▲ 追い風 / ▼ 逆風 / ▬ 中立）の緑/赤/灰は **意味的記号**なので維持
4. **テキスト色 / ソース文字色**（`COLOR_TEXT` / `COLOR_SOURCE`）は維持

---

## 3. 同期対象スクリプト

以下 5 ファイルすべてに **同一順序・同一 hex 値** で定数を埋める:

- `skills/market-environment-pptx/scripts/fill_market_environment.py`
- `skills/market-share-pptx/scripts/fill_market_share.py`
- `skills/positioning-map-pptx/scripts/fill_positioning_map.py`
- `skills/executive-summary-pptx/scripts/fill_executive_summary.py`
- `skills/pest-analysis-pptx/scripts/fill_pest_analysis.py`

### 共通定数ブロック（5 ファイルすべての色定義直下に貼り付け）

```python
# ─── 共通配色（正本: skills/_common/styles/chart_palette.md） ───
# 編集時は _common/styles/chart_palette.md と他 4 スキルの fill_*.py も同期更新
# CHART_PALETTE には TARGET_COLOR(赤) と OTHER_COLOR(灰) を含めない（palette 外で固定）
CHART_PALETTE = [
    "#4E79A7", "#F28E2B", "#59A14F", "#76B7B2",
    "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F",
]
OTHER_COLOR = "#BAB0AC"
TARGET_COLOR = "#E15759"
LABEL_BAR_COLOR = "#4E79A7"
LABEL_BG_COLOR = "#E8EEF5"


def _palette_color(index: int, total: int) -> str:
    if total <= 1:
        return CHART_PALETTE[0]
    return CHART_PALETTE[index % len(CHART_PALETTE)]


def _is_other_player(name: str) -> bool:
    if not name:
        return False
    return (
        name.startswith("その他")
        or name.startswith("Others")
        or name.lower().startswith("other")
    )
```

---

## 4. 維持する例外

| 用途 | Hex | 維持理由 |
|---|---|---|
| その他（OTHER_COLOR） | `#BAB0AC` 灰 | 「主要プレイヤー以外」を視覚的に他と分けるため |
| 対象会社（TARGET_COLOR） | `#E15759` 赤 | レポートの主役を強調するため |
| ▲ 追い風 | `#1B7A3B` 濃緑 | PEST の影響度の意味記号 |
| ▼ 逆風 | `#C03A3A` 濃赤 | PEST の影響度の意味記号 |
| ▬ 中立 | `#666666` 灰 | PEST の影響度の意味記号 |
| テキスト | `#333333` 濃グレー | 既存仕様 |
| 出典 | `#666666` グレー | 既存仕様 |

---

## 5. 改訂履歴

- 2026-04-29: 初版作成。p1-golden-frog.md プラン承認に基づき 5 スキルへ展開
- 2026-04-29: P6/P7 色不整合バグ修正（snug-dancing-alpaca.md）。CHART_PALETTE を 10→8 色に削減（赤・灰を palette 外へ）、`_is_other_player()` で「その他」判定を前方一致化、配列 index 直引きに統一、`NON_TARGET_PALETTE` 廃止
