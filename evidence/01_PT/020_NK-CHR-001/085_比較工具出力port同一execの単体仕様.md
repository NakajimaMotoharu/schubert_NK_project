# 比較工具の出力port分岐を確認する単体仕様

NK-CHR-001／WBS-P020-01.03/2／SS354・355。対象は `GateCli.writeJson(Path,Object,JsonOutput)`。

- PT-CHR-OUTPUT-NULL-001 は出力先nullの `IllegalArgumentException` と固定診断 `output is required`、注入port未呼出を確認。
- [親のないPathの独立仕様](083_比較ゲート出力先の親なし境界単体仕様.md)の1件と、元PG44084に接続した四つの合成portケースを、対象overloadの未確認分岐を埋めるため、同じsource・同じexecに限定して選択。
- 固定順序、主例外の型と同一性、cleanup・取得状態の保持を独立期待値で検査する。以前の単独成功分は追加Test IDや新規成果として再計上しない。
- 合成portを使用。JVMの所有一時領域以外への入出力、CLI dispatch、実Current/NK、baseline、製品PTは対象外。工具クラス全体と対象メソッドの四指標を分けて記録する。
