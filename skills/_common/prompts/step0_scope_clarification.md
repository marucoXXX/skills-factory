# Step 0: スコープ確認（共通パターン）

> **このファイルは `skills/_common/prompts/step0_scope_clarification.md` です。**
> オーケストレータースキル（market-overview-agent / strategy-report-agent / smallcap-strategy-research 等）の SKILL.md の Step 0 から、`<!-- source: skills/_common/prompts/step0_scope_clarification.md (manual sync until D2) -->` コメント付きで**手動コピペ**してください。
> このファイルを変更したら `grep -rn "source: skills/_common/prompts/step0_scope_clarification.md" skills/*/SKILL.md` で被参照スキルを全て検出し、コピペし直すこと（ISSUE-001 D2 で自動化検討中）。

調査開始前にユーザーから調査スコープを確定し、`scope.json` として作業ディレクトリに保存する。
スコープを文書化する目的は (1) 後続 Step（Web 検索・データ生成・fill_*.py）で参照する単一の真実源、
(2) 中断・再開時のコンテキスト復元、(3) 最終納品物のメタデータ。

## 共通原則

1. **AskUserQuestion で確定**: スコープに関する質問は対話のテキスト出力ではなく `AskUserQuestion` ツールで聞く。単一選択は `single_select`、複数選択は `multi_select`。
2. **`scope.json` に保存**: 確定したスコープは作業ディレクトリ（`{{WORK_DIR}}/<run_id>/`）の `scope.json` に書き出し、後続 Step は必ずこのファイルを参照する。
3. **`run_id` と `started_at` を必ず含める**: `run_id` は YYYY-MM-DD_<topic> 形式（例: `2026-04-27_taxi_industry`）、`started_at` は ISO 8601 with timezone。
4. **`limits` 範囲外の値は再確認**: 各スキルの `references/deck_skeleton_standard.json` 等で定義された `limits.<param>.{min, max}` の範囲外を選ばれたら、AskUserQuestion で再確認する。デフォルト値（`limits.<param>.default`）はユーザーが明示しない場合に採用する。
5. **`max_competitors` / `kbf_count` 等の共有制約は scope.json で一元管理**: 複数スライド間で一貫させたいパラメータ（例: market-share / positioning-map / competitor-summary / market-kbf で同じ競合数を使う）は scope.json で確定し、各 fill_*.py が読み込む。
6. **事業モデル境界を必ず確認**: 同一業界内に異なる収益構造の事業モデルが併存する場合、シェア表・競合比較で異種を混在させると読み手を誤解させる。Step 0.5（後述）で必ず境界を確認する。

## scope.json の最小スキーマ

```json
{
  "topic_name": "国内タクシー市場",
  "run_id": "2026-04-27_taxi_industry",
  "started_at": "2026-04-27T10:00:00+09:00",
  "included_business_models": ["タクシー事業者"],
  "excluded_segments": ["配車アプリ事業者"]
}
```

各オーケストレーターは上記に独自フィールドを追加する。例:
- market-overview-agent: `geography`, `segment`, `analysis_years`, `max_competitors`, `kbf_count`
- strategy-report-agent: `report_type`, `deck_depth`, `data_availability_position`
- smallcap-strategy-research: `target_company`, `depth`, `agents`

### `included_business_models[]` / `excluded_segments[]` の意味

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `included_business_models` | string[] | ✓ | 調査対象に含める事業モデルのラベル。シェア表・競合比較・市場規模算出の対象母集団を定義する。空配列 `[]` は「全モデル統合扱い」（v0.2 までと同じ後方互換挙動） |
| `excluded_segments` | string[] | ✓ | 同一業界内で意図的に除外したセグメント。読み手への透明性のため `data-availability` スライドや FactCheck_Report.md の冒頭注記で明示する。空配列 `[]` 可 |

**重要**: 後続 Step（Web 検索・データ生成・スライド生成）で `included_business_models` の境界を尊重する責務はオーケストレーターにある。`fill_*.py` は scope.json を読まない（単体起動互換性維持）。`skills/_common/references/orchestrator_contract.md` 参照。

## Step 0.5: 事前スコーピング Web 検索（必須）

`topic_name` が確定したら、ユーザー固有質問（geography / segment 等）を聞く前に **市場構造ザックリ把握用の Web 検索を 1〜2 件** 走らせる。
目的は「同一業界内に収益構造の異なる事業モデルが併存していないか」を Step 0 確定前に検知すること。

### 検索クエリのテンプレート

| 検索意図 | クエリ例 |
|---|---|
| 業界の構造マップ | `<topic_name> 業界構造 / バリューチェーン / プレイヤー類型` |
| 関連市場との切り分け | `<topic_name> 市場規模 定義 / 統計対象範囲` |

### 異種事業モデル併存の検知パターン

以下のような兆候を Web 検索結果から拾った場合、ユーザーに**境界確認**を入れる:

| 業界例 | 併存しがちな事業モデル |
|---|---|
| タクシー | 事業者（営業収入）/ 配車アプリ（配車手数料） |
| 半導体 | 装置メーカー / IDM / ファブレス / ファウンドリ |
| 教育 | 学校法人 / 学習塾 / EdTech SaaS |
| 飲食 | 個店 / チェーン / プラットフォーム（食べログ等） |
| 物流 | 元請キャリア / 中堅 / ラストワンマイル / 倉庫オペレーター |
| 金融 | 銀行 / 証券 / 資産運用 / FinTech |

### 境界確認の AskUserQuestion パターン

```python
{
    "question": "「<topic_name>」には収益構造の異なる事業モデルが併存しています。どの層を調査対象に含めますか？",
    "options": [
        "A. <事業モデル1>のみ（例: タクシー事業者）",
        "B. <事業モデル2>のみ（例: 配車アプリ事業者）",
        "C. 両方含める（シェア表は別レイヤーで分けて表示）",
        "D. その他（自由記述）"
    ],
    "type": "single_select"
}
```

選択結果に応じて `included_business_models` / `excluded_segments` を埋める。

- A 選択 → `included_business_models=["事業モデル1"]`, `excluded_segments=["事業モデル2"]`
- C 選択 → `included_business_models=["事業モデル1","事業モデル2"]`, `excluded_segments=[]` （ただし読み手向け注記必須）

### Step 0.5 をスキップして良いケース

- `topic_name` が単一事業モデルしか含まないことが自明（例: 「東証プライム上場の地方銀行」「コンビニ大手 5 社」）
- ユーザーが冒頭で `included_business_models` を明示している（例: 「タクシー事業者の市場を調べて」）

スキップした場合も `scope.json` の `included_business_models` は空配列ではなく**判明している値**で埋めること。

## オーケストレーター固有の質問項目

各オーケストレーターは本ファイルを継承した上で、自身の SKILL.md に固有の質問テーブル
（`AskUserQuestion` の questions 配列または対応表）を必ず明示すること。質問の **既定値**
は `references/deck_skeleton_standard.json` の `limits.<param>.default` から採るのが望ましい。

## アンチパターン

- ❌ Step 0 を省略して即 Web 検索に入る（後で「全社シェアを揃える」等の制約が破綻する）
- ❌ scope.json を作らず会話メモリだけで進める（中断時に復元不能）
- ❌ `limits` 範囲外の値を黙って受け付ける（fill_*.py が hard-fail する）
- ❌ run_id を秒単位 timestamp で作る（同日複数実行の名前衝突回避が目的なら、トピック名で区別する方が読みやすい）
- ❌ Step 0.5 を省略し、異なる収益構造の事業モデルをシェア表で混在させる（v0.2 Phase E のタクシー業界 E2E で発生した既知の落とし穴）
- ❌ `included_business_models` を勝手に空配列のまま進める（明示的な「全モデル統合」判断ならコメントで根拠を残す）
