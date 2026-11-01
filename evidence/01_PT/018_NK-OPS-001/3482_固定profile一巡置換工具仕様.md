# 固定profile一巡置換工具 仕様

PG-D1130/F03・BUG2220/2226再発防止の内部工具補足、既helper literal_template_replace_v1.mjsは変更しない。Production6b53/HEAD77d06c1ca353d5604cdd49d28d5c9ef4b48307b8不変更、新PG18288事前0.25/0.75/2共有pp cap10。新製品機能ではない。

新literal_profile_replace_v2.mjsは文字列と明示triple[needle,replacement,元一巡最長一致の正確出現数]だけを受け、最長original needleを一巡で置換。重なった短keyの部分一致を二重に数えない。replacementを次keyへ再置換しない、JS replacement-stringのドル記号補間を使わずcallbackのliteralを保持する。空/不正型/重複key/未出現/出現数違い/非整数/過大count/不正Unicodeを拒否し、裸の数値及び中途hash fragmentを禁止する。40/64文字の完全commit/digestは許容する。境界上限512entries、出力はtextと実countsのimmutable snapshot。code eval/動的import生成/ファイルwrite/実行・Product fixture・VM/DB/ネット操作は一切持たない。

成功literalはA→B,B→Cの原位置同時置換、最長overlap、ドル/改行/Unicode/削除/正規表現記号/完全hash・commit/出現数複数。期待は手書きfixed stringsで作り、独立readerはregexを使わない位置scan/最長一致を別計算して全結果を確認する。拒否は型/null/空/重複/回数0・負・不整合・NaN/数値key/hash断片/不正Unicode/over512等。これを製品TestID/PASS/coverageへ加算しない。

固定Node24.19.0と元runtime SHA、checked Python entry/工具自身hashを実前後束縛、Node tool selftestだけを一回実行し同入力で独立postを確認。3483と公開PG18288 manifestへcommand/exit/time/version/元source/新helper/test/hash/positive-negative数と限界を保存。既成功Test/reader/旧v1 selftestを確認再演せず、将来は新しい未実行draftの機械生成に限り使用、実行済みSource/Test/helperの上書き用途は禁止。Java/Python意味解析や品質合格を保証せず、生成後の独立byte/metadata/compile/451条件を残す。新WBS受入/正式/工数率0、全HOLD維持。
