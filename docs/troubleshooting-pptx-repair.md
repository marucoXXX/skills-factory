# PPTX「修復が必要」エラーの原因と対策

生成した .pptx を PowerPoint で開くと **「ファイルの問題を修復しました」** ダイアログが出る問題の調査記録と、本工場で採用した恒久対策のまとめ。2026-04 の調査（PR #1）をベースに随時追記していく。

---

## 1. 背景：なぜ PPTX は壊れやすいか

PPTX は単一ファイルではなく、`slide.xml` / `slideLayout` / `slideMaster` / `theme` / `[Content_Types].xml` などが `*.rels` で結びついた **Open XML パッケージ**。python-pptx でテンプレを読み書きする過程で、以下のような**静的検査では拾いづらい**歪みが残りやすい：

- `*.rels` が実在しないパートを参照（**dangling rels**）
- `*.rels` に定義された rId が、対応する `.xml` 本体から参照されていない（**orphan rels**）
- `[Content_Types].xml` の `Override` が実ファイルと不整合
- `notesSlides` / `embeddings` が `build_rename_map` の対象漏れで番号衝突（merge 時）

python-pptx のスライドコピー/マージは構造的に弱い（python-pptx GitHub issues 参照）。XML を手で継いで rels を手動更新する方式は、少しでも複雑な要素（chart・埋め込み Excel・OLE）が入ると破損確率が跳ね上がる。

---

## 2. 本工場で確認された具体パターン

| 発見場所 | パターン | 修復トリガー |
|---|---|---|
| 全48テンプレの半数程度の `slide1.xml.rels` | `oleObject4.bin` / `image4.emf` への **orphan rels**（ファイルは存在するが slide が参照していない） | ◎ 高確率で PowerPoint が修復要求 |
| `company-overview-template.pptx` / `market-share-template.pptx` | `slideLayout1/4/5.xml.rels` と `slideMaster1.xml.rels` に存在しない `oleObject` / `image.emf` への参照 | ◎ 確実に修復要求 |
| `merge-pptxv2` 出力 (多数ファイル結合時) | `notesSlides/notesSlide1.xml` への dangling rels が複数 slide で残存 | △ merge 規模依存 |
| PowerPoint 固有の微細な検証差分 | 静的検査では通るが Office の内部バリデータが弾く | △ 個別検証不能 |

---

## 3. 採用した恒久対策（3層）

### 3-1. テンプレの rels クリーンアップ

`tools/fix_template_rels.py` で `skills/*/assets/*.pptx` を一括修復：

```bash
# 検査のみ
python3 tools/validate_pptx.py --template-scan

# 壊れているテンプレだけ自動修復（.bak 作成）
python3 tools/fix_template_rels.py --all

# orphan rels も含めて除去（安全タイプは自動除外: slideLayout/theme/tags/revisionInfo 等）
python3 tools/fix_template_rels.py --all --remove-orphans
```

除去対象から外す rels タイプは `ORPHAN_SAFE_TYPES` 定数に列挙（`slideLayout`, `slideMaster`, `theme`, `tags`, `notesSlide`, `customXml`, `revisionInfo`, `changesInfo`, `slide` など）。

### 3-2. 各スキル生成末尾で LibreOffice ラウンドトリップ

全 `skills/*/scripts/fill_*.py` の末尾に自己完結の `_finalize_pptx(path)` を埋め込み、`prs.save(...)` 直後に呼ぶ。

- 中身: `soffice --headless --convert-to pptx` で OOXML を正規化
- soffice 未インストール / タイムアウト時は **graceful skip**（元ファイル維持）
- `tools/add_finalize_hook.py` で一括注入/取り外し

```bash
# 注入
python3 tools/add_finalize_hook.py

# 取り外し
python3 tools/add_finalize_hook.py --revert

# 一部スキルだけ
python3 tools/add_finalize_hook.py --only customer-profile-pptx,revenue-analysis-pptx
```

**前提**: macOS では `brew install --cask libreoffice` が必要。インストールパスは `/Applications/LibreOffice.app/Contents/MacOS/soffice`。

### 3-3. `merge-pptxv2` 末尾にも同じラウンドトリップ

`skills/merge-pptxv2/scripts/merge_pptx_v2.py` の `merge_presentations()` 末尾で `_finalize_pptx(output)` を呼び、結合結果もそのまま正規化する。`--no-roundtrip` で無効化可能。

---

## 4. 診断ワークフロー（再現手順）

### 4-1. 静的検査 → 故障箇所の特定

```bash
# 単一ファイル
python3 tools/validate_pptx.py <file.pptx> --verbose

# 全テンプレ
python3 tools/validate_pptx.py --template-scan

# 全スキル単体生成 + validate
python3 tools/smoke_test_all.py
# 結果: work/smoke/<skill>.pptx, work/smoke_result.csv, work/smoke_result.json

# 多数ファイル merge の検証
python3 tools/smoke_test_all.py --merge-with v2
```

### 4-2. 実機確認（PowerPoint）

静的検査 OK でも Office が嫌うパターンはあり得る。`work/smoke/<skill>.pptx` を **必ず PowerPoint で開いて修復ダイアログの有無を確認する**。

### 4-3. LibreOffice ラウンドトリップ単独実行

```bash
# ラウンドトリップして別名に出す
python3 tools/pptx_roundtrip.py <file.pptx> --dst <out.pptx>

# soffice で開けるかだけチェック
python3 tools/pptx_roundtrip.py <file.pptx> --verify-only
```

---

## 5. 新しいスキルを足すときのチェックリスト

1. `skills/<name>/assets/*.pptx` を追加した直後に `python3 tools/validate_pptx.py <template>` を通す
2. `dangling rels` / `orphan rels` が出たら `fix_template_rels.py --remove-orphans` で除去
3. `fill_*.py` に `_finalize_pptx` が入っているか確認（`tools/add_finalize_hook.py` が未適用なら実行）
4. `references/sample_data.json` を置く（無い場合は `tools/extract_sample_data.py --all` で SKILL.md から抽出可能）
5. `python3 tools/smoke_test_all.py --only <skill>` で validate 通過確認
6. PowerPoint で生成物を開き修復ダイアログが出ないことを実機確認
7. `install-all` で反映

---

## 6. 既知の限界

- **LibreOffice 経由の副作用**:
  - 日本語フォントのベースラインが 1–2px ずれる既知現象
  - `c:chartSpace` の custom color や `c:extLst` が欠落する報告あり
  - コンサル品質が厳しい場合はチャート付きスライドで個別検証推奨
- **静的検査 (validate_pptx.py) の限界**: PowerPoint 固有の内部バリデーションルールは OOXML 仕様に載っておらず、静的検査で全ては捕捉できない
- **`issue-tree` スキル**: python-pptx を使わない unpack/pack 方式のため roundtrip hook 対象外
- **Windows COM API 経由の統合**: macOS では利用不能のため採用せず

---

## 7. なぜ「中間フォーマット集約」（deck-renderer 新設）にしなかったか

理論的には最も堅牢な解は「各スキルは slide spec だけ返し、最後に単一レンダラで描画」だが、今回は見送った。理由：

- 実装コスト: MVP 3–4 週 / 全量 3–4 ヶ月
- 既存 41 スキルを書き換える必要があり、視覚退行リスクが広範
- テンプレ修復 + ラウンドトリップの 3 層で「修復が必要」は実測で消えた

将来、roundtrip 起因の品質劣化が顕在化した場合や、python-pptx 自体のバグで壊れるパターンが残った場合に再検討する。

---

## 8. 参考資料

- 元調査の PR: [#1 PowerPoint「修復が必要」エラーの根絶](https://github.com/marucoXXX/skills-factory/pull/1)
- ChatGPT による原因分析（PR description に転載）
- python-pptx の slide copy/merge 弱点に関する公式 issue
- 作業計画: `~/.claude/plans/pptx-chatgpt-jaunty-harbor.md`（ローカル）
