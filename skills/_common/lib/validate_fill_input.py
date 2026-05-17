"""validate_fill_input — fill_*.py の入力 JSON スキーマ齟齬を hard-fail で検出する helper。

ISSUE-012 (2026-05-06) で観測された positioning-map-pptx の silent fail
（オーケストレーターが想像で書いた JSON のキー名・値スケールがスキーマと不一致でも
fill スクリプトが成功ログを出して空に近いスライドを出力する事故）を構造的に防ぐため。

設計方針:
    - **必須キー欠落** は ValueError で hard-fail（オーケストレーターが気付ける）
    - **想定外キー** は stderr に WARN（タイポ・古いスキーマ流用を検出）
    - **値の妥当性検査**（数値スケール・文字数等）は呼び出し側の責務（本 helper はキー集合のみ検査）

使い方::

    from validate_fill_input import validate_fill_input

    validate_fill_input(
        data,
        required_top=["main_message", "players", "x_axis", "y_axis"],
        allowed_top=[
            "main_message", "chart_title", "section_title", "target_company",
            "x_axis", "y_axis", "quadrants", "players",
            "implications", "implications_title",
            "source", "source_label", "source_text",
        ],
        nested_required={
            "x_axis": ["label", "low", "high"],
            "y_axis": ["label", "low", "high"],
        },
        per_item_required={"players": ["name", "x", "y"]},
        skill_name="positioning-map-pptx",
    )
"""

from __future__ import annotations

import sys
from typing import Iterable, Optional


def validate_fill_input(
    data: dict,
    *,
    required_top: Iterable[str] = (),
    allowed_top: Optional[Iterable[str]] = None,
    nested_required: Optional[dict] = None,
    per_item_required: Optional[dict] = None,
    skill_name: str = "fill",
) -> None:
    """fill_*.py の入力 JSON スキーマ齟齬を検出する。

    Args:
        data: fill スクリプトに渡された JSON dict
        required_top: トップレベルで必須のキー集合（欠落で hard-fail）
        allowed_top: トップレベルで許容するキー集合（None なら想定外キー検査をスキップ）
        nested_required: ネスト dict（例: x_axis）内で必須のキー集合
        per_item_required: 配列要素（例: players[]）内で必須のキー集合
        skill_name: エラー/警告メッセージで使うスキル名

    Raises:
        ValueError: 必須キー欠落、または値が dict/list でないなど構造不一致
    """
    if not isinstance(data, dict):
        raise ValueError(
            f"[{skill_name}] data は dict である必要があります（受領: {type(data).__name__}）"
        )

    # 1) トップレベル必須キー欠落チェック
    missing_top = [k for k in required_top if k not in data]
    if missing_top:
        raise ValueError(
            f"[{skill_name}] 必須トップレベルキーが欠落: {missing_top}\n"
            f"  受領キー: {sorted(data.keys())}\n"
            f"  → references/sample_data.json を参照してスキーマを確認してください"
        )

    # 2) ネスト dict の必須キー欠落チェック
    nested_required = nested_required or {}
    for parent_key, required_subkeys in nested_required.items():
        if parent_key not in data:
            continue
        sub = data[parent_key]
        if not isinstance(sub, dict):
            raise ValueError(
                f"[{skill_name}] '{parent_key}' は dict である必要があります"
                f"（受領: {type(sub).__name__}）"
            )
        missing_sub = [k for k in required_subkeys if k not in sub]
        if missing_sub:
            raise ValueError(
                f"[{skill_name}] '{parent_key}' 内の必須キーが欠落: {missing_sub}\n"
                f"  受領: {sorted(sub.keys())}\n"
                f"  → references/sample_data.json を参照してください"
            )

    # 3) 配列要素の必須キー欠落チェック
    per_item_required = per_item_required or {}
    for parent_key, required_item_keys in per_item_required.items():
        if parent_key not in data:
            continue
        items = data[parent_key]
        if not isinstance(items, list):
            raise ValueError(
                f"[{skill_name}] '{parent_key}' は list である必要があります"
                f"（受領: {type(items).__name__}）"
            )
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(
                    f"[{skill_name}] '{parent_key}[{i}]' は dict である必要があります"
                    f"（受領: {type(item).__name__}）"
                )
            missing_item = [k for k in required_item_keys if k not in item]
            if missing_item:
                raise ValueError(
                    f"[{skill_name}] '{parent_key}[{i}]' で必須キーが欠落: {missing_item}\n"
                    f"  受領: {sorted(item.keys())}\n"
                    f"  → references/sample_data.json を参照してください"
                )

    # 4) 想定外キー WARN（hard-fail せず stderr に注意喚起）
    if allowed_top is not None:
        allowed_set = set(allowed_top)
        unknown = [k for k in data.keys() if k not in allowed_set]
        if unknown:
            print(
                f"  ⚠ [{skill_name}] 想定外のトップレベルキー (無視されます): {unknown}\n"
                f"     → references/sample_data.json と比較してタイポ/古いスキーマでないか確認してください",
                file=sys.stderr,
            )
