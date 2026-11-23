# 比較工具のJSON Pointer構文

NK-CHR-001、WBS-P020-01.02/2、SS355 §8、BUG-3713／YKT-2913。対象は `ArtifactComparator.validPointer` と比較前の診断・選別への接続。Reference tokenのescapeは `~0` と `~1` のみ。 [RFC 6901 §3](https://www.rfc-editor.org/rfc/rfc6901.html#section-3)

| Test ID | 入力 | 独立期待値 |
| --- | --- | --- |
| PT-CHR-POINTER-001 | 通常token、`~0`、`~1`、連続escape、Unicode、途中の空token | 全6入力でtrue |
| PT-CHR-POINTER-002 | 末尾片割れ、2または英字、tilde連続、区切り直前の片割れ | 全5入力でfalse |
| PT-CHR-POINTER-003 | null、空列、root、無接頭辞、末尾区切り、wildcard、`..` | 全7入力でfalse。既存の対象規則を保持 |

期待値は文字列の構文とSS355の対象範囲から定める。Actual Current/NK、baseline、DIF承認一覧、実ファイルやネットワークにアクセスしない試験。PG43546で投入source、実行結果、対象分岐、範囲外を保存する。
