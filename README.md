# skills_factory

Web や手元資料を入力にして、Claude のスキルを使って調査・パワーポイント生成までを一気通貫で回す「工場」。

この工場の役割は 2 つ：

1. **スキルを開発・配布する** — 正本 (`skills/<name>/`) を 1 つ書けば、Claude Code と Claude.ai の両方に配布できる。
2. **実作業のワークスペースを提供する** — 入力資料・中間生成物・出力成果物を工場内の `inputs/` `work/` `outputs/` に集約する。

`skills/<name>/` に `{{VAR}}` 入りの canonical source を置き、`tools/build_skill.py` で環境ごとに差し替えて配布する。

## ディレクトリ構造

```
skills_factory/
├── inputs/               # 作業入力（docx / IM / Webスクレイプ結果 / 画像など）— gitignore
├── outputs/              # 生成された pptx などの成果物 — gitignore
├── work/                 # スキル実行中の中間ファイル（<skill_name>/ 配下）— gitignore
├── profiles/             # 環境プロファイル（変数値の定義）
│   ├── claude_code.json
│   └── claude_ai.json
├── skills/               # 正本（{{VAR}} 入り）
│   └── <skill_name>/SKILL.md, scripts/, assets/, ...
├── tools/
│   └── build_skill.py    # ビルド CLI
└── dist/                 # Claude.ai 向け zip 出力（.gitignore）
```

`inputs/` `outputs/` `work/` は `.gitkeep` のみ追跡し、中身は Git 管理しない。

## コマンド

```bash
# スキル一覧
python3 tools/build_skill.py list

# 未解決変数チェック（--profile 省略で両プロファイル）
python3 tools/build_skill.py check <skill> [--profile claude_code|claude_ai] [--strict]

# 任意ディレクトリへビルド
python3 tools/build_skill.py build <skill> --profile <p> --out <dir> [--strict]

# Claude Code にインストール (~/.claude/skills/<skill>/)
python3 tools/build_skill.py install <skill> [--strict]

# Claude.ai アップロード用 zip を生成 (dist/<skill>.zip)
python3 tools/build_skill.py package <skill> [--strict]

# 全スキルを Claude Code にインストール
python3 tools/build_skill.py install-all

# 全スキルを Claude.ai 用 zip にパッケージ (dist/*.zip)
python3 tools/build_skill.py package-all [--strict]
```

`--strict` は未解決 `{{VAR}}` をエラーにする。CI やリリース前チェックで使う。

## 変数とプロファイル

| 変数 | claude_code | claude_ai |
|---|---|---|
| `{{FACTORY_ROOT}}` | `/Users/nakamaru/Developer/projects/skills_factory` | （未定義・未使用） |
| `{{INPUT_DIR}}` | `{{FACTORY_ROOT}}/inputs` | `/mnt/user-data/uploads` |
| `{{WORK_DIR}}` | `{{FACTORY_ROOT}}/work/{{SKILL_NAME}}` | `/home/claude` |
| `{{OUTPUT_DIR}}` | `{{FACTORY_ROOT}}/outputs` | `/mnt/user-data/outputs` |
| `{{SKILL_DIR}}` | `~/.claude/skills/{{SKILL_NAME}}` | `.` |
| `{{PIP_FLAGS}}` | （空） | `--break-system-packages` |
| `{{PYTHON_BIN}}` | `python3` | `python3` |
| `{{OPEN_CMD}}` | `open` | （空） |
| `{{SKILL_NAME}}` | スキルのディレクトリ名（自動注入） | 同左 |

プロファイルに変数を足したい場合は両 JSON を編集する。プロファイルの値自身も `{{VAR}}` 参照可能（例: `INPUT_DIR` が `FACTORY_ROOT` を参照、`WORK_DIR` が `SKILL_NAME` を参照）。

## セクションマーカー

片方の環境でだけ出したいブロックは `@if` で囲う。閉じ忘れはビルド時にエラー。

Markdown:
```markdown
<!-- @if:claude_ai -->
python -m markitdown {{OUTPUT_DIR}}/foo.pptx
<!-- @endif -->
```

Python / シェル:
```python
# @if:claude_ai
import markitdown
# @endif
```

ネスト不可。1 つのマーカー内に `@if` は 1 つだけ書く。

## 対象ファイル

テキスト処理される拡張子: `.md .py .mjs .js .sh .json .txt .yaml .yml`

`.pptx .png .jpg` など上記以外のバイナリは `shutil.copy2` で素通しコピー。

## 開発ワークフロー

1. `skills/<name>/` を編集（`{{INPUT_DIR}}` `{{OUTPUT_DIR}}` `{{WORK_DIR}}` を使って入出力を工場内で扱う）
2. `python3 tools/build_skill.py check <name> --strict` で未解決変数なしを確認
3. `python3 tools/build_skill.py install <name>` で Claude Code に反映 → `inputs/` に資料を置いてその場で試す
4. 成果物は `outputs/` に出る
5. 問題なければ `package <name>` で zip 生成 → Claude.ai のスキル管理画面にアップロード

`~/.claude/skills/<name>/` は常にビルド成果物として扱う（手編集しない）。編集は必ず `skills/<name>/` 側で行い、`install` で反映させる。

## 新しいスキルの追加

1. `skills/<new_name>/SKILL.md` を作る（`{{VAR}}` と `@if` 使用可）
2. `scripts/`, `assets/`, `templates/`, `references/`, `examples/` など必要なサブディレクトリを配置
3. 入力は `{{INPUT_DIR}}`、出力は `{{OUTPUT_DIR}}`、中間は `{{WORK_DIR}}` を参照するように書く
4. `check <new_name> --strict` が通ることを確認
5. `install <new_name>` / `package <new_name>` で配布

## Claude.ai への配布ワークフロー

全スキルのzipをGitHub Releaseにまとめて置き、必要なものを手動アップロードする運用。

1. スキルを `skills/<name>/` で編集 → `check --strict` と `install` で動作確認
2. リリース用タグを push：
   ```bash
   git tag v0.1.0 && git push origin v0.1.0
   ```
3. `.github/workflows/release.yml` が発火して `package-all` を実行、全zipを Release `v0.1.0` に添付する
4. GitHubのReleases画面から必要なスキルzipをダウンロード → claude.ai のスキル管理画面にアップロード

任意のタイミングでビルドしたい場合は、Actions タブから `Release skill zips` ワークフローを手動実行（`workflow_dispatch`）する。`tag` を空にすると `snapshot-<短SHA>` 名でReleaseが作られる。

## ドキュメント

工場で積み上げたノウハウ・トラブルシューティング・設計判断は `docs/` 配下に記録する。新しい知見を得たら該当ファイルに追記するか、必要なら新規ファイルを足す。

| ファイル | 内容 |
|---|---|
| [`docs/troubleshooting-pptx-repair.md`](docs/troubleshooting-pptx-repair.md) | PPTX「修復が必要」エラーの原因・診断手順・恒久対策（テンプレ rels クリーンアップ + LibreOffice ラウンドトリップ統合）。新スキル追加時のチェックリスト付き。 |

## 現状の移行状況

| スキル | 出身 | 取り込み | 備考 |
|---|---|---|---|
| `company-overview-pptx-v2` | Claude.ai | ✓ | 完全変数化済み |
| `html2pptx` | Claude Code | ✓ | 完全変数化済み |
| `scq`, `issue-tree`, `design-doc`, `sketch2slides` | Claude Code | 未 | 環境依存がほぼないため後続で取り込み予定 |
