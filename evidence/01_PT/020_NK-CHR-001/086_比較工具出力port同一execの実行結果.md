# 比較工具の出力port分岐 実行結果

PG44112、現試験source `34b7fce211e0a3ba9a61626225d757e6a863dc51`。選択6件すべて成功、失敗・エラー・skip各0。新規PT-CHR-OUTPUT-NULL-001と既存の親なし1件・合成port4件を単一execに収めた。既存5件の新規加算0。

対象の三引数overloadは生行18/18、分岐6/6、メソッド1/1。二引数overload、工具全体の未到達をこの結果へ含めない。書式とCheckstyleは新規一ファイル指摘0。実比較、実書込、製品PT、正式受入0。

元PG44108は補助型不足でコンパイル終了1。PG44110は候補JARの対象member不在で検査起動前に終了。PG44112は外側の補助型をコンパイラにだけ置き、同じ正規工具入力で再試験した。

[単体仕様](085_比較工具出力port同一execの単体仕様.md) [証跡](evidence/PG44112-current-gate-output-single-exec/manifest.json)
