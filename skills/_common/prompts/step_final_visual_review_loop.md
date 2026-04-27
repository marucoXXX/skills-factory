# Step 最終: ビジュアル品質レビュー＋自動修正ループ（共通パターン）

> **このファイルは `skills/_common/prompts/step_final_visual_review_loop.md` です。**
> オーケストレータースキル（market-overview-agent / strategy-report-agent / smallcap-strategy-research 等）の SKILL.md のマージ後フェーズから、`<!-- source: skills/_common/prompts/step_final_visual_review_loop.md (manual sync until D2) -->` コメント付きで**手動コピペ**してください。
> このファイルを変更したら `grep -rn "source: skills/_common/prompts/step_final_visual_review_loop.md" skills/*/SKILL.md` で被参照スキルを全て検出し、コピペし直すこと（ISSUE-001 D2 で自動化検討中）。

`merge-pptxv2` 完了後、`visual-quality-reviewer` を呼び出してデッキ全体をページ画像化 → 目視レビューする。
文字溢れ・要素重なり・配色崩れ等の `severity=high` issue が残ると最終納品の品質に直結するため、
最大 2 ラウンドの自動修正ループで `severity=high` を 0 件まで下げる。

## 起動

入力:
- `merged_pptx`: `{{OUTPUT_DIR}}/<DeckName>_<topic>_<date>.pptx`
- `merge_order`: `{{WORK_DIR}}/<run_id>/merge_order.json`（`category` フィールド必須、`orchestrator_contract.md` 参照）
- `data_dir`: `{{WORK_DIR}}/<run_id>/`

出力: `{{FACTORY_ROOT}}/work/visual-quality-reviewer/visual_review_report.json`

## レビュー結果の分岐

| `overall_verdict` | 処理 |
|---|---|
| `pass` | 終了。完成デッキをユーザーに提示 |
| `needs_fixes` かつ `severity=high` ≥ 1 件 | **自動修正ループへ**（下記） |
| `needs_fixes` かつ `severity=high` = 0 件 | ユーザーに差分レポートを提示し、手動修正 or 許容を選ばせる |
| `reject` | LibreOffice レンダリング失敗を疑いユーザーに報告して停止 |

## 自動修正ループ（最大 2 ラウンド）

`severity=high` の各 issue について:

1. `issues[i].skill_name` と `issues[i].data_file` から、該当スライド生成に使った JSON を特定
2. `issues[i].regeneration_hint` に従って `data_NN_*.json` を修正
   （例: bullets を短縮、項目数を減らす、main_message を 65 字以内に書き直す）
3. 該当スキル（例: `pest-analysis-pptx`）の `fill_*.py` を**同じ `slide_NN_*.pptx` ファイル名で再実行** → 既存スライドを上書き
4. 全修正完了後、`merge-pptxv2 --merge-order` を再実行して最新デッキを再生成
5. 再度 `visual-quality-reviewer` を起動

**2 ラウンド終了時点で `severity=high` が残存する場合**:
- ユーザーに残存 issue を提示し、手動修正か許容の判断を仰ぐ
- 無限ループには絶対に入らない（カウンタを必ず持つ）

## ユーザーへの最終出力

- `overall_verdict=pass` 時: 「ビジュアル品質レビュー: 問題なし」のみ
- 自動修正で pass に到達した時: 「自動修正 N 件を適用しました（詳細: `visual_review_report.json`）」
- 手動対応が必要な時: レポートと共に次アクションを明示

## アンチパターン

- ❌ 自動修正ループのカウンタを持たない（無限ループ → コスト爆発）
- ❌ `severity=high` を残したまま納品する（ユーザーは PPT を開いて初めて気付く）
- ❌ `regeneration_hint` を無視して別の修正を入れる（次ラウンドで同じ issue が再発）
- ❌ visual review を skip して納品（merge_warnings.json も併せて確認漏れの主因）
