# skills_factory プロジェクト規約

## セッション開始時の必須手順

1. **`ISSUES.md` を読み込む** — 判断保留事項・将来検討事項が登録されている。新規作業着手前に未解決イシューを確認すること。
2. 直近の plan ファイル（`/Users/nakamaru/.claude/plans/` 配下）を確認し、進行中の v0.x 開発計画があるか把握する。

## プロジェクト構造（最低限）

- `skills/<skill-name>/` — 各スキルのソース（SKILL.md, scripts/, references/, templates/ 等）
- `skills/_common/` — 複数 orchestrator で再利用する共通プロンプト・規約（v0.2 Phase D1 で新設）
- `tools/build_skill.py` — `{{VAR}}` 置換と `@if/@endif` 分岐を解決して `~/.claude/skills/` にインストールするビルドツール
- `work/`, `outputs/` — 各スキル実行時の作業領域・成果物
- `ISSUES.md` — プロジェクト懸案管理（D2 保留など）

## 共通スキル（skills/_common/）の運用ルール

`skills/_common/` 配下のファイルを変更した場合、被参照 SKILL.md（`grep -r "source: skills/_common/" skills/*/SKILL.md` で検出）を**手動でコピペし直す**こと。`build_skill.py` には現時点で `@import` 機構が未実装（ISSUE-001 で v0.3 検討中）。

## スキル編集はソース側で行う

`skills/<name>/` を編集して `python tools/build_skill.py install <name>` で `~/.claude/skills/` に反映する。`~/.claude/skills/` 配下を直接編集しない（次の install で上書きされる）。
