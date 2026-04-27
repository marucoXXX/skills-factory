#!/usr/bin/env python3
"""Validate agent/synthesis/master output JSONs against the smallcap-strategy-research schema.

Usage:
    python3 validate_output.py <agent|synthesis|master> <json_path>

Exits 0 on valid, 1 on schema error with a summary.

対応スキーマ:
- agent:     financial_signals / strategic_signals / corporate_registry /
             talent_organization / industry_context の出力
- synthesis: synthesis_output.json
- master:    master_output.json の pptx_slot 配下（Phase 3.2b 追加）
             下流PPTXスキルのキー名契約を強制する
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

VALID_AGENTS = {
    "financial_signals",
    "strategic_signals",
    "corporate_registry",
    "talent_organization",
    "industry_context",
}
VALID_SOURCE_TYPES = {
    "registry",
    "gazette",
    "press",
    "grant_db",
    "patent_db",
    "web",
    "sns",
    "upload",
}
VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_STATUS = {"complete", "partial", "missing"}
VALID_PRIORITY = {"high", "medium", "low"}

AGENT_REQUIRED_TOP = ["agent", "target", "collected_at", "findings", "data_gaps"]
AGENT_REQUIRED_FINDING = [
    "metric",
    "value",
    "source",
    "source_type",
    "confidence",
    "limitations",
]
AGENT_REQUIRED_GAP = ["item", "reason"]

SYNTHESIS_REQUIRED_TOP = [
    "target_company",
    "industry",
    "research_purpose",
    "synthesized_at",
    "executive_summary",
    "strategy_hypotheses",
    "data_availability_matrix",
    "verification_issues",
    "triangulation_stats",
    "all_findings_index",
]
SYNTHESIS_HYPOTHESIS_KEYS = [
    "where_to_play",
    "how_to_win",
    "capability_resource",
    "aspiration_trajectory",
]


def err(errors: list[str], msg: str) -> None:
    errors.append(msg)


def validate_agent_output(data: dict) -> list[str]:
    errors: list[str] = []
    for key in AGENT_REQUIRED_TOP:
        if key not in data:
            err(errors, f"missing top-level field: {key}")
    if errors:
        return errors

    if data["agent"] not in VALID_AGENTS:
        err(errors, f"invalid agent: {data['agent']}")
    if not isinstance(data["findings"], list):
        err(errors, "findings must be a list")
    if not isinstance(data["data_gaps"], list):
        err(errors, "data_gaps must be a list")

    for i, f in enumerate(data.get("findings", [])):
        if not isinstance(f, dict):
            err(errors, f"findings[{i}] must be an object")
            continue
        for key in AGENT_REQUIRED_FINDING:
            if key not in f:
                err(errors, f"findings[{i}] missing field: {key}")
        if f.get("source_type") not in VALID_SOURCE_TYPES:
            err(errors, f"findings[{i}].source_type invalid: {f.get('source_type')}")
        if f.get("confidence") not in VALID_CONFIDENCE:
            err(errors, f"findings[{i}].confidence invalid: {f.get('confidence')}")

    for i, g in enumerate(data.get("data_gaps", [])):
        if not isinstance(g, dict):
            err(errors, f"data_gaps[{i}] must be an object")
            continue
        for key in AGENT_REQUIRED_GAP:
            if key not in g:
                err(errors, f"data_gaps[{i}] missing field: {key}")

    return errors


def validate_synthesis_output(data: dict) -> list[str]:
    errors: list[str] = []
    for key in SYNTHESIS_REQUIRED_TOP:
        if key not in data:
            err(errors, f"missing top-level field: {key}")
    if errors:
        return errors

    exec_sum = data["executive_summary"]
    if "main_message" not in exec_sum:
        err(errors, "executive_summary.main_message missing")
    findings = exec_sum.get("findings", [])
    if not isinstance(findings, list) or not (3 <= len(findings) <= 5):
        err(errors, f"executive_summary.findings must have 3-5 items (got {len(findings) if isinstance(findings, list) else 'non-list'})")

    hyp = data["strategy_hypotheses"]
    for key in SYNTHESIS_HYPOTHESIS_KEYS:
        if key not in hyp:
            err(errors, f"strategy_hypotheses.{key} missing")
            continue
        node = hyp[key]
        if not isinstance(node, dict):
            err(errors, f"strategy_hypotheses.{key} must be an object")
            continue
        for k in ("hypothesis", "evidence_refs", "confidence"):
            if k not in node:
                err(errors, f"strategy_hypotheses.{key}.{k} missing")
        if node.get("confidence") not in VALID_CONFIDENCE:
            err(errors, f"strategy_hypotheses.{key}.confidence invalid: {node.get('confidence')}")

    rc = hyp.get("reality_check")
    if not isinstance(rc, list) or len(rc) < 1:
        err(errors, "strategy_hypotheses.reality_check must have >= 1 item (use placeholder if no gap found)")

    vi = data.get("verification_issues", [])
    if not isinstance(vi, list) or not (3 <= len(vi) <= 7):
        err(errors, f"verification_issues must have 3-7 items (got {len(vi) if isinstance(vi, list) else 'non-list'})")
    for i, v in enumerate(vi):
        if not isinstance(v, dict):
            err(errors, f"verification_issues[{i}] must be an object")
            continue
        for k in ("id", "category", "issue", "current_hypothesis", "verification_method", "priority"):
            if k not in v:
                err(errors, f"verification_issues[{i}].{k} missing")
        if v.get("priority") not in VALID_PRIORITY:
            err(errors, f"verification_issues[{i}].priority invalid: {v.get('priority')}")

    dam = data.get("data_availability_matrix", {})
    cats = dam.get("categories", [])
    if not isinstance(cats, list) or len(cats) == 0:
        err(errors, "data_availability_matrix.categories must be non-empty list")
    for ci, cat in enumerate(cats):
        for item in cat.get("items", []):
            if item.get("status") not in VALID_STATUS:
                err(errors, f"data_availability_matrix.categories[{ci}].items[...].status invalid: {item.get('status')}")

    stats = data.get("triangulation_stats", {})
    for k in ("total_findings", "high_confidence", "medium_confidence", "low_confidence", "triangulation_rate"):
        if k not in stats:
            err(errors, f"triangulation_stats.{k} missing")

    return errors


# ── Master Output (pptx_slot) validators ──────────────────────────────

# pptx_slot キー別の必須下流スロット（Phase 3.4-b 時点の15スロット）
# capability_resource_detail / aspiration_trajectory_detail を追加
MASTER_REQUIRED_SLOTS = [
    "table_of_contents",
    "executive_summary",
    "company_overview",
    "company_history",
    "revenue_analysis",
    "shareholder_structure",
    "swot",
    "strategy_summary",
    "where_to_play_detail",
    "how_to_win_detail",
    "capability_resource_detail",
    "aspiration_trajectory_detail",
    "reality_check",
    "data_availability",
    "issue_risk_list",
]

# 下流PPTXスキルがエラー扱いする別名キー（Synthesis LLMが混入させがち）
FORBIDDEN_ALIAS_DATA_AVAILABILITY_CATEGORY = {"category"}
FORBIDDEN_ALIAS_DATA_AVAILABILITY_ITEM = {"item"}


def _warn(warnings: list[str], msg: str) -> None:
    warnings.append(msg)


def validate_master_output(data: dict) -> tuple[list[str], list[str]]:
    """Validate master_output.json. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    for key in ("target_company", "synthesized_at", "pptx_slot"):
        if key not in data:
            err(errors, f"missing top-level field: {key}")
    if errors:
        return errors, warnings

    slots = data["pptx_slot"]
    if not isinstance(slots, dict):
        err(errors, "pptx_slot must be an object")
        return errors, warnings

    for slot_key in MASTER_REQUIRED_SLOTS:
        if slot_key not in slots:
            err(errors, f"pptx_slot.{slot_key} missing")
    if errors:
        return errors, warnings

    # --- table_of_contents ---
    toc = slots["table_of_contents"]
    for key in ("main_message", "chart_title", "sections"):
        if key not in toc:
            err(errors, f"pptx_slot.table_of_contents.{key} missing")
    for i, sec in enumerate(toc.get("sections", [])):
        for key in ("title", "page", "subitems"):
            if key not in sec:
                err(errors, f"pptx_slot.table_of_contents.sections[{i}].{key} missing")

    # --- executive_summary ---
    es = slots["executive_summary"]
    for key in ("main_message", "chart_title", "findings"):
        if key not in es:
            err(errors, f"pptx_slot.executive_summary.{key} missing")
    if isinstance(es.get("main_message"), str) and len(es["main_message"]) > 70:
        _warn(warnings, f"pptx_slot.executive_summary.main_message is {len(es['main_message'])} chars (>70 may truncate)")
    findings = es.get("findings", [])
    if not isinstance(findings, list) or not (3 <= len(findings) <= 5):
        err(errors, f"pptx_slot.executive_summary.findings must have 3-5 items (got {len(findings) if isinstance(findings, list) else 'non-list'})")
    for i, f in enumerate(findings if isinstance(findings, list) else []):
        for key in ("category", "heading", "detail"):
            if key not in f:
                err(errors, f"pptx_slot.executive_summary.findings[{i}].{key} missing")
        if isinstance(f.get("detail"), str) and len(f["detail"]) > 180:
            _warn(warnings, f"pptx_slot.executive_summary.findings[{i}].detail is {len(f['detail'])} chars (>180 may truncate)")

    # --- company_overview ---
    co = slots["company_overview"]
    if co:  # 空オブジェクトの場合は未充填として扱う（エラーではない）
        for key in ("title", "main_message", "source", "items"):
            if key not in co:
                err(errors, f"pptx_slot.company_overview.{key} missing")
        if isinstance(co.get("source"), str) and co["source"].startswith("出典："):
            err(errors, "pptx_slot.company_overview.source must NOT start with '出典：' (auto-prepended by fill script, causes duplicate prefix)")
        if isinstance(co.get("main_message"), str) and len(co["main_message"]) > 65:
            _warn(warnings, f"pptx_slot.company_overview.main_message is {len(co['main_message'])} chars (>65 may truncate)")
        items = co.get("items", [])
        if not isinstance(items, list) or not (1 <= len(items) <= 15):
            err(errors, f"pptx_slot.company_overview.items must have 1-15 items (got {len(items) if isinstance(items, list) else 'non-list'})")
        for i, it in enumerate(items if isinstance(items, list) else []):
            for key in ("label", "value"):
                if key not in it:
                    err(errors, f"pptx_slot.company_overview.items[{i}].{key} missing")
                elif not isinstance(it[key], str):
                    err(errors, f"pptx_slot.company_overview.items[{i}].{key} must be string")

    # --- swot ---
    sw = slots["swot"]
    if sw:
        for key in ("main_message", "chart_title", "swot"):
            if key not in sw:
                err(errors, f"pptx_slot.swot.{key} missing")
        if isinstance(sw.get("main_message"), str):
            if "すべき" in sw["main_message"]:
                err(errors, "pptx_slot.swot.main_message must NOT contain '〜すべき' (v5.0 factual tone rule)")
            if len(sw["main_message"]) > 70:
                _warn(warnings, f"pptx_slot.swot.main_message is {len(sw['main_message'])} chars (>70 may truncate)")
        swot_body = sw.get("swot", {})
        for quadrant in ("strengths", "weaknesses", "opportunities", "threats"):
            if quadrant not in swot_body:
                err(errors, f"pptx_slot.swot.swot.{quadrant} missing")
                continue
            items = swot_body[quadrant].get("items", [])
            if not isinstance(items, list) or not (3 <= len(items) <= 6):
                err(errors, f"pptx_slot.swot.swot.{quadrant}.items must have 3-6 items (got {len(items) if isinstance(items, list) else 'non-list'})")

    # --- shareholder_structure ---
    ss = slots["shareholder_structure"]
    if ss:
        for key in ("main_message", "chart_title", "shareholders", "directors"):
            if key not in ss:
                err(errors, f"pptx_slot.shareholder_structure.{key} missing")
        if isinstance(ss.get("main_message"), str):
            if "すべき" in ss["main_message"]:
                err(errors, "pptx_slot.shareholder_structure.main_message must NOT contain '〜すべき' (v5.0 factual tone rule)")
            if len(ss["main_message"]) > 70:
                _warn(warnings, f"pptx_slot.shareholder_structure.main_message is {len(ss['main_message'])} chars (>70 may truncate)")
        sh = ss.get("shareholders", {})
        sh_rows = sh.get("rows", [])
        if not isinstance(sh_rows, list) or len(sh_rows) == 0:
            err(errors, "pptx_slot.shareholder_structure.shareholders.rows must be non-empty list (use placeholder row with '非開示' if data is undisclosed)")
        for i, r in enumerate(sh_rows if isinstance(sh_rows, list) else []):
            for k in ("number", "name", "position", "relation", "shares", "voting_ratio"):
                if k not in r:
                    err(errors, f"pptx_slot.shareholder_structure.shareholders.rows[{i}].{k} missing")
        dr = ss.get("directors", {})
        dr_rows = dr.get("rows", [])
        if not isinstance(dr_rows, list) or len(dr_rows) == 0:
            err(errors, "pptx_slot.shareholder_structure.directors.rows must be non-empty list")
        for i, r in enumerate(dr_rows if isinstance(dr_rows, list) else []):
            for k in ("number", "name", "position", "relation", "compensation"):
                if k not in r:
                    err(errors, f"pptx_slot.shareholder_structure.directors.rows[{i}].{k} missing")

    # --- revenue_analysis ---
    ra = slots["revenue_analysis"]
    if ra:  # 空オブジェクトは未充填として許容（EBITDA推定不能時はskipする方針）
        for key in ("main_message", "chart_title", "data"):
            if key not in ra:
                err(errors, f"pptx_slot.revenue_analysis.{key} missing")
        if isinstance(ra.get("main_message"), str):
            if "すべき" in ra["main_message"]:
                err(errors, "pptx_slot.revenue_analysis.main_message must NOT contain '〜すべき' (v5.0 factual tone rule)")
            if len(ra["main_message"]) > 70:
                _warn(warnings, f"pptx_slot.revenue_analysis.main_message is {len(ra['main_message'])} chars (>70 may truncate)")
        ra_data = ra.get("data", [])
        if not isinstance(ra_data, list) or not (2 <= len(ra_data) <= 8):
            err(errors, f"pptx_slot.revenue_analysis.data must have 2-8 periods (got {len(ra_data) if isinstance(ra_data, list) else 'non-list'})")
        for i, d in enumerate(ra_data if isinstance(ra_data, list) else []):
            for key in ("year", "revenue", "ebitda"):
                if key not in d:
                    err(errors, f"pptx_slot.revenue_analysis.data[{i}].{key} missing (revenue/ebitda are REQUIRED numbers; if undisclosed, fill with industry-average estimate or set the whole slot to {{}})")
            if "revenue" in d and not isinstance(d["revenue"], (int, float)):
                err(errors, f"pptx_slot.revenue_analysis.data[{i}].revenue must be number (got {type(d['revenue']).__name__})")
            if "ebitda" in d and not isinstance(d["ebitda"], (int, float)):
                err(errors, f"pptx_slot.revenue_analysis.data[{i}].ebitda must be number (got {type(d['ebitda']).__name__})")

    # --- company_history ---
    ch = slots["company_history"]
    if ch:  # 空オブジェクトは未充填として許容
        for key in ("main_message", "chart_title", "history"):
            if key not in ch:
                err(errors, f"pptx_slot.company_history.{key} missing")
        if isinstance(ch.get("main_message"), str):
            if "すべき" in ch["main_message"]:
                err(errors, "pptx_slot.company_history.main_message must NOT contain '〜すべき' (v5.0 factual tone rule)")
            if len(ch["main_message"]) > 70:
                _warn(warnings, f"pptx_slot.company_history.main_message is {len(ch['main_message'])} chars (>70 may truncate)")
        history = ch.get("history", [])
        if not isinstance(history, list) or not (1 <= len(history) <= 15):
            err(errors, f"pptx_slot.company_history.history must have 1-15 items (got {len(history) if isinstance(history, list) else 'non-list'})")
        for i, h in enumerate(history if isinstance(history, list) else []):
            for key in ("year", "events"):
                if key not in h:
                    err(errors, f"pptx_slot.company_history.history[{i}].{key} missing")
            events = h.get("events", [])
            if not isinstance(events, list) or len(events) == 0:
                err(errors, f"pptx_slot.company_history.history[{i}].events must be non-empty list")

    # --- strategy_summary (Phase 3.4-a fix: コンサル品質、implications 中心) ---
    ss = slots["strategy_summary"]
    if ss:
        for key in ("main_message", "chart_title", "dimensions", "implications"):
            if key not in ss:
                err(errors, f"pptx_slot.strategy_summary.{key} missing")
        if isinstance(ss.get("main_message"), str):
            if "すべき" in ss["main_message"]:
                err(errors, "pptx_slot.strategy_summary.main_message must NOT contain '〜すべき' (v5.0 factual tone rule)")
            if len(ss["main_message"]) > 100:
                _warn(warnings, f"pptx_slot.strategy_summary.main_message is {len(ss['main_message'])} chars (>100 may truncate)")
        dims = ss.get("dimensions", [])
        if not isinstance(dims, list) or len(dims) != 4:
            err(errors, f"pptx_slot.strategy_summary.dimensions must have exactly 4 items (got {len(dims) if isinstance(dims, list) else 'non-list'})")
        expected_keys = ["where_to_play", "how_to_win", "capability_resource", "aspiration_trajectory"]
        for i, d in enumerate(dims if isinstance(dims, list) else []):
            for k in ("key", "label", "summary", "confidence"):
                if k not in d:
                    err(errors, f"pptx_slot.strategy_summary.dimensions[{i}].{k} missing")
            if i < len(expected_keys) and d.get("key") != expected_keys[i]:
                err(errors, f"pptx_slot.strategy_summary.dimensions[{i}].key must be '{expected_keys[i]}' (got '{d.get('key')}')")
            if d.get("confidence") not in VALID_CONFIDENCE:
                err(errors, f"pptx_slot.strategy_summary.dimensions[{i}].confidence invalid: {d.get('confidence')}")
        # implications 3 件必須（コンサル品質）
        imps = ss.get("implications", [])
        if not isinstance(imps, list) or len(imps) != 3:
            err(errors, f"pptx_slot.strategy_summary.implications must have exactly 3 items (got {len(imps) if isinstance(imps, list) else 'non-list'})")
        for i, imp in enumerate(imps if isinstance(imps, list) else []):
            for k in ("label", "detail"):
                if k not in imp:
                    err(errors, f"pptx_slot.strategy_summary.implications[{i}].{k} missing")

    # --- 4 次元 detail スロット（コンサル品質） ---
    # Main / Detail / Evidence の各ページが implications 3 個を持ち、main_message・chart_title が独立
    # Phase 3.4-b で capability_resource_detail / aspiration_trajectory_detail を追加
    for dim_key in ("where_to_play_detail", "how_to_win_detail", "capability_resource_detail", "aspiration_trajectory_detail"):
        slot = slots[dim_key]
        if not slot:
            continue
        for k in ("main", "detail", "evidence"):
            if k not in slot:
                err(errors, f"pptx_slot.{dim_key}.{k} missing")

        # 各ページ共通の検証ヘルパー
        # Evidence ページは「メッセージ＋タイトル＋表チャートのみ」構成のため implications は不要
        for page_key in ("main", "detail", "evidence"):
            page = slot.get(page_key, {})
            required_keys = ("main_message", "chart_title")
            if page_key != "evidence":
                required_keys = required_keys + ("implications",)
            for k in required_keys:
                if k not in page:
                    err(errors, f"pptx_slot.{dim_key}.{page_key}.{k} missing")
            mm = page.get("main_message", "")
            if isinstance(mm, str):
                if "すべき" in mm:
                    err(errors, f"pptx_slot.{dim_key}.{page_key}.main_message must NOT contain '〜すべき' (v5.0 rule)")
                if len(mm) > 100:
                    _warn(warnings, f"pptx_slot.{dim_key}.{page_key}.main_message is {len(mm)} chars (>100 may truncate)")
            # Main / Detail ページのみ implications 3 個必須（Evidence は不要）
            if page_key != "evidence":
                imps = page.get("implications", [])
                if not isinstance(imps, list) or len(imps) != 3:
                    err(errors, f"pptx_slot.{dim_key}.{page_key}.implications must have exactly 3 items (got {len(imps) if isinstance(imps, list) else 'non-list'})")
                for i, imp in enumerate(imps if isinstance(imps, list) else []):
                    for k in ("label", "detail"):
                        if k not in imp:
                            err(errors, f"pptx_slot.{dim_key}.{page_key}.implications[{i}].{k} missing")

        # main / detail 用 visual_data 必須
        if "visual_data" not in slot.get("main", {}):
            err(errors, f"pptx_slot.{dim_key}.main.visual_data missing")
        # evidence 用 findings 4 個以上必須
        findings = slot.get("evidence", {}).get("findings", [])
        if not isinstance(findings, list) or len(findings) < 4:
            err(errors, f"pptx_slot.{dim_key}.evidence.findings must have >=4 items (got {len(findings) if isinstance(findings, list) else 'non-list'})")
        for i, f in enumerate(findings if isinstance(findings, list) else []):
            for k in ("id", "agent", "source", "source_type", "confidence", "excerpt"):
                if k not in f:
                    err(errors, f"pptx_slot.{dim_key}.evidence.findings[{i}].{k} missing")
            if f.get("confidence") not in VALID_CONFIDENCE:
                err(errors, f"pptx_slot.{dim_key}.evidence.findings[{i}].confidence invalid: {f.get('confidence')}")

    # --- reality_check ---
    rc = slots["reality_check"]
    if rc:  # 空オブジェクトは未充填として許容
        for key in ("main_message", "chart_title", "columns", "rows"):
            if key not in rc:
                err(errors, f"pptx_slot.reality_check.{key} missing")
        rc_cols = rc.get("columns", [])
        rc_rows = rc.get("rows", [])
        if isinstance(rc_cols, list) and isinstance(rc_rows, list):
            for ri, row in enumerate(rc_rows):
                if not isinstance(row, list):
                    err(errors, f"pptx_slot.reality_check.rows[{ri}] must be a list (2D array)")
                    continue
                if len(row) != len(rc_cols):
                    err(errors, f"pptx_slot.reality_check.rows[{ri}] has {len(row)} cols, expected {len(rc_cols)}")
                for ci, cell in enumerate(row):
                    if not isinstance(cell, str):
                        err(errors, f"pptx_slot.reality_check.rows[{ri}][{ci}] must be string (got {type(cell).__name__})")

    # --- data_availability ---
    da = slots["data_availability"]
    for key in ("main_message", "chart_title", "categories"):
        if key not in da:
            err(errors, f"pptx_slot.data_availability.{key} missing")
    cats = da.get("categories", [])
    if not isinstance(cats, list) or len(cats) == 0:
        err(errors, "pptx_slot.data_availability.categories must be non-empty list")
    for ci, cat in enumerate(cats if isinstance(cats, list) else []):
        # キー名契約: name 必須（category は別名として禁止）
        if "name" not in cat:
            err(errors, f"pptx_slot.data_availability.categories[{ci}].name missing (REQUIRED key, forbidden aliases: {FORBIDDEN_ALIAS_DATA_AVAILABILITY_CATEGORY})")
        for alias in FORBIDDEN_ALIAS_DATA_AVAILABILITY_CATEGORY:
            if alias in cat:
                err(errors, f"pptx_slot.data_availability.categories[{ci}].{alias} is forbidden alias of 'name' — rename to 'name'")
        # items 内部
        cat_items = cat.get("items", [])
        if not isinstance(cat_items, list):
            err(errors, f"pptx_slot.data_availability.categories[{ci}].items must be list")
            continue
        for ii, it in enumerate(cat_items):
            if "label" not in it:
                err(errors, f"pptx_slot.data_availability.categories[{ci}].items[{ii}].label missing (REQUIRED key, forbidden aliases: {FORBIDDEN_ALIAS_DATA_AVAILABILITY_ITEM})")
            for alias in FORBIDDEN_ALIAS_DATA_AVAILABILITY_ITEM:
                if alias in it:
                    err(errors, f"pptx_slot.data_availability.categories[{ci}].items[{ii}].{alias} is forbidden alias of 'label' — rename to 'label'")
            if "status" not in it:
                err(errors, f"pptx_slot.data_availability.categories[{ci}].items[{ii}].status missing")
            elif it["status"] not in VALID_STATUS:
                err(errors, f"pptx_slot.data_availability.categories[{ci}].items[{ii}].status invalid: {it['status']}")

    # --- issue_risk_list ---
    irl = slots["issue_risk_list"]
    for key in ("main_message", "chart_title", "columns", "rows"):
        if key not in irl:
            err(errors, f"pptx_slot.issue_risk_list.{key} missing")
    cols = irl.get("columns", [])
    rows = irl.get("rows", [])
    if isinstance(cols, list) and isinstance(rows, list):
        for ri, row in enumerate(rows):
            if not isinstance(row, list):
                err(errors, f"pptx_slot.issue_risk_list.rows[{ri}] must be a list (2D array)")
                continue
            if len(row) != len(cols):
                err(errors, f"pptx_slot.issue_risk_list.rows[{ri}] has {len(row)} cols, expected {len(cols)}")
            for ci, cell in enumerate(row):
                if not isinstance(cell, str):
                    err(errors, f"pptx_slot.issue_risk_list.rows[{ri}][{ci}] must be string (got {type(cell).__name__})")

    return errors, warnings


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in ("agent", "synthesis", "master"):
        print(f"usage: {argv[0]} <agent|synthesis|master> <json_path>", file=sys.stderr)
        return 2

    kind = argv[1]
    path = Path(argv[2])
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"invalid JSON: {e}", file=sys.stderr)
        return 1

    warnings: list[str] = []
    if kind == "agent":
        errors = validate_agent_output(data)
    elif kind == "synthesis":
        errors = validate_synthesis_output(data)
    else:  # master
        errors, warnings = validate_master_output(data)

    if errors:
        print(f"validation failed: {path}", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        if warnings:
            print(f"warnings:", file=sys.stderr)
            for w in warnings:
                print(f"  ! {w}", file=sys.stderr)
        return 1

    if warnings:
        print(f"ok with warnings: {path}")
        for w in warnings:
            print(f"  ! {w}")
    else:
        print(f"ok: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
