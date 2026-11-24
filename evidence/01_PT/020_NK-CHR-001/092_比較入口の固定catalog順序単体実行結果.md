# 比較入口の固定catalog順序単体実行結果

PG44628、PT-CHR-CATALOG-ORDER001、BUG-3806、YKT-2964。工具source `d1a4cd60b5ff429f7cb83922d45ab5a1b0f18f52`、製品Core `03dfb35a6a68f4ee32e9303b4fa0df3d262156fa`。初回準備は既存の合成fixture提供二型が不足しcompileで終了1、試験未実行。必要二型を限定で含めた修正前実行で、入替後が成功扱いとなることを確認し、独立期待に対して1件失敗した。

修正後の通常比較、順序違反、重複、未承認ID、G01の定義条件など7件は失敗・エラー・skip各0。Checkstyleは対象3ソースで0。正規包装の物理17を照合し、変更された4物理は試験で使った当classと同じSHA-256。Current原定義とbaselineは保持した。未測定の実CHR、権限および全451は保留。 [実行証跡](evidence/PG44628-fixed-catalog-order-two-entrances/manifest.json)
