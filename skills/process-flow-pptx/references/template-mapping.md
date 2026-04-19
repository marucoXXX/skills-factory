# テンプレートShape名マッピング表

ProcessFlow9.pptx を実際に検査して確認済み（2026-03）。

## スライド構成

1枚スライド構成。左側にプロセスフロー図（矢印付き、最大3列×3行）、右側にプロセス特徴を配置。
ステップ数が9未満の場合、スクリプトが不要なボックスとコネクタを自動削除する。

## 共通Shape（常に存在）

| セクション | Shape名 | Shape Type | 内容 |
|---|---|---|---|
| Main Message | `Title 1` | PLACEHOLDER | スライドタイトル |
| Chart Title | `Text Placeholder 2` | PLACEHOLDER | サブタイトル |
| セクションラベル（左） | `TextBox 52` | TEXT_BOX | 「プロセスの全体像」固定テキスト（編集不要） |
| セクションラベル（右） | `TextBox 53` | TEXT_BOX | 「プロセスの特徴」固定テキスト（編集不要） |
| 区切り線 | `Straight Connector 55` | LINE | 水平区切り線（編集不要） |
| プロセス特徴 | `TextBox 6` | TEXT_BOX | 9段落（3特徴×3行） |

## プロセスステップ（9個）

| ステップ | Shape名 | 位置（行-列） | top位置 |
|---|---|---|---|
| Process1 | `Rectangle 4` | Row1-Col1 | 1883664 |
| Process2 | `Rectangle 3` | Row1-Col2 | 1883664 |
| Process3 | `Rectangle 13` | Row1-Col3 | 1883664 |
| Process4 | `Rectangle 24` | Row2-Col1 | 3367667 |
| Process5 | `Rectangle 25` | Row2-Col2 | 3367667 |
| Process6 | `Rectangle 26` | Row2-Col3 | 3367667 |
| Process7 | `Rectangle 40` | Row3-Col1 | 4851670 |
| Process8 | `Rectangle 41` | Row3-Col2 | 4851670 |
| Process9 | `Rectangle 42` | Row3-Col3 | 4851670 |

## コネクタ（矢印）

| 接続 | Shape名 | top位置 | 備考 |
|---|---|---|---|
| Step1 → Step2 | `Straight Arrow Connector 9` | 2397137 | Row1水平 |
| Step2 → Step3 | `Straight Arrow Connector 14` | 2397137 | Row1水平 |
| Row1 → Row2（U字折り返し） | `Straight Arrow Connector 27` | **1247755** | 同名Shape 2つのうち上側 |
| Step4 → Step5 | `Straight Arrow Connector 30` | 3881140 | Row2水平 |
| Step5 → Step6 | `Straight Arrow Connector 33` | 3881140 | Row2水平 |
| Row2 → Row3（U字折り返し） | `Straight Arrow Connector 27` | **2731758** | 同名Shape 2つのうち下側 |
| Step7 → Step8 | `Straight Arrow Connector 46` | 5365143 | Row3水平 |
| Step8 → Step9 | `Straight Arrow Connector 49` | 5365143 | Row3水平 |

**注意**: `Straight Arrow Connector 27` が2つ存在する。top位置で区別する。

## 自動削除ロジック

ステップ数Nに応じて、以下のShapeを削除する（Step9から逆順に処理）:

| 不要ステップ | 削除するShape |
|---|---|
| Step 9が不要 (N<9) | `Rectangle 42`, `Connector 49` |
| Step 8が不要 (N<8) | `Rectangle 41`, `Connector 46` |
| Step 7が不要 (N<7) | `Rectangle 40`, `Connector 27 (top=2731758)` ← Row2→3のU字 |
| Step 6が不要 (N<6) | `Rectangle 26`, `Connector 33` |
| Step 5が不要 (N<5) | `Rectangle 25`, `Connector 30` |
| Step 4が不要 (N<4) | `Rectangle 24`, `Connector 27 (top=1247755)` ← Row1→2のU字 |

## プロセス特徴TextBox（`TextBox 6`）の段落構成

| 段落 | 内容 | フォント |
|---|---|---|
| para[0] | Feature1 ラベル | bold, +mn-ea |
| para[1] | Feature1 Comment1 | size=177800 (14pt), +mn-ea |
| para[2] | Feature1 Comment2 | size=177800 (14pt), +mn-ea |
| para[3] | Feature2 ラベル | bold, +mn-ea |
| para[4] | Feature2 Comment1 | size=177800 (14pt), +mn-ea |
| para[5] | Feature2 Comment2 | size=177800 (14pt), +mn-ea |
| para[6] | Feature3 ラベル | bold, +mn-ea |
| para[7] | Feature3 Comment1 | size=177800 (14pt), +mn-ea |
| para[8] | Feature3 Comment2 | size=177800 (14pt), +mn-ea |

スタイルはテンプレートの既存runから継承されるため、スクリプトでは run.text だけを上書きする。
