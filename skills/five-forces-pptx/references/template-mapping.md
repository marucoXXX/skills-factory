# Five Forces テンプレート Shape マッピング

テンプレート: `assets/five-forces-template.pptx`（スライド1枚構成）

## Shape一覧

| Shape名 | Shape ID | 種別 | マッピング先 | 備考 |
|---------|----------|------|------------|------|
| `Title 1` | 2 | PLACEHOLDER (title) | Main Message | スライドタイトル |
| `Text Placeholder 2` | 3 | PLACEHOLDER (body) | Chart Title | サブタイトル |
| `Rectangle 5` | 6 | SHAPE (rect) | 業界内の競争 | 中央ボックス。1段落目がラベル（太字14pt）、2段落目以降がbullet（11pt） |
| `Rectangle 15` | 16 | SHAPE (rect) | 売り手の交渉力 | 左ボックス。同上構造 |
| `Rectangle 17` | 18 | SHAPE (rect) | 買い手の交渉力 | 右ボックス。同上構造 |
| `Rectangle 18` | 19 | SHAPE (rect) | 新規参入の脅威 | 上ボックス。同上構造 |
| `Rectangle 20` | 21 | SHAPE (rect) | 代替品の脅威 | 下ボックス。同上構造 |
| `TextBox 30` | 31 | TEXT_BOX | 意味合い | 右側の大きなテキストボックス。`wrap="square"`で折り返し対応。1段落目がラベル「意味合い」（太字20pt）、2段落目以降がbullet（16pt） |

## ボックス内のXML構造

各Rectangleの共通パターン：

```xml
<!-- 1段落目: ラベル（太字） -->
<a:p>
  <a:r>
    <a:rPr kumimoji="1" lang="en-JP" sz="1400" b="1" dirty="0" err="1">
      <a:solidFill><a:schemeClr val="tx1"/></a:solidFill>
    </a:rPr>
    <a:t>業界内の競争</a:t>
  </a:r>
</a:p>
<!-- 2段落目以降: bullet項目 -->
<a:p>
  <a:pPr marL="285750" indent="-285750">
    <a:buFont typeface="Arial" .../>
    <a:buChar char="•"/>
  </a:pPr>
  <a:r>
    <a:rPr lang="en-JP" sz="1100" dirty="0" err="1">
      <a:solidFill><a:schemeClr val="tx1"/></a:solidFill>
    </a:rPr>
    <a:t>Competitor1</a:t>
  </a:r>
</a:p>
```

ラベル（1段落目）は変更しない。2段落目以降のbullet項目のテキストのみ差し替える。

## 意味合いボックスのXML構造

意味合いのTextBoxは `wrap="square"` が設定されており、テキストが自動的にボックス幅で折り返される。

```xml
<a:bodyPr wrap="square" lIns="72000" tIns="72000" rIns="72000" bIns="72000" rtlCol="0">
  <a:noAutofit/>
</a:bodyPr>
```

```xml
<!-- 1段落目: 見出し「意味合い」（太字20pt） — 変更しない -->
<a:p>
  <a:pPr algn="l" defTabSz="288000">
    <a:spcAft><a:spcPts val="600"/></a:spcAft>
  </a:pPr>
  <a:r>
    <a:rPr kumimoji="1" lang="en-JP" sz="2000" b="1">
      <a:latin typeface="+mn-ea"/>
    </a:rPr>
    <a:t>意味合い</a:t>
  </a:r>
</a:p>
<!-- 2段落目以降: bullet項目（16pt） -->
<a:p>
  <a:pPr marL="285750" indent="-285750" algn="l" defTabSz="288000">
    <a:spcAft><a:spcPts val="600"/></a:spcAft>
    <a:buFont typeface="Arial" .../>
    <a:buChar char="•"/>
  </a:pPr>
  <a:r>
    <a:rPr lang="en-JP" sz="1600">
      <a:latin typeface="+mn-ea"/>
    </a:rPr>
    <a:t>Implication1</a:t>
  </a:r>
</a:p>
```

## プレースホルダーテキスト

| セクション | プレースホルダー |
|-----------|---------------|
| Main Message | `Main Message` |
| Chart Title | `Chart Title` |
| 業界内の競争 | `Competitor1`, `Competitor2` |
| 新規参入の脅威 | `NewEntrant1`, `NewEntrant2` |
| 代替品の脅威 | `Substitute1`, `Substitute2` |
| 売り手の交渉力 | `Supplier1`, `Supplier2`, `Supplier3` |
| 買い手の交渉力 | `Buyer1`, `Buyer2`, `Buyer3` |
| 意味合い | `Implication1`, `Implication2`, `Implication3` |

## 注意事項

- ラベル（各ボックスの1段落目）は書き換えない
- bullet項目数がテンプレートと異なる場合は、スクリプトが段落の追加・削除を行う
- 各ポイントは30文字以内を推奨（Forceボックスが小さいためオーバーフローに注意）
- 意味合いボックスは折り返し対応のため、60文字程度まで許容される
