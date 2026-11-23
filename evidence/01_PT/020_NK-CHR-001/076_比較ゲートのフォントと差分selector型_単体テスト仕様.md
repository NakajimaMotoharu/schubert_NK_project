# 比較ゲートのフォントと差分セレクターの型

NK-CHR-001、WBS-P020-01.03/2、SS355 CHR-G01、PT-CHR-DEF-017、YKT-2909。対象は定義の `fonts` と `DIF-002.selectors`。試験では公開定義6点の複製をメモリ上で操作する。

| Test ID | 操作 | 独立期待値 |
|---|---|---|
| PT-CHR-DEF-017 | フォント名配列を数値7、JSON null、空白のうち一要素の配列に置換する。差分セレクター配列は数値7、JSON null、boolean falseのうち一要素で置換する。 | フォント側は `BROWSER_FONTS`、差分側は `DIF_SELECTOR_EMPTY:DIF-002`。旧承認定義では診断なし。承認された文字列セレクター、文字の禁止条件、差分の適用範囲・件数は維持する。 |

旧PT-CHR-DEF-001～016と同じJDK25／JUnit／Jacksonで、配列型と値の検査だけを実施する。実Browser、実NK／Current、FileStore、VM、サービスやネットワークは使用しない。
