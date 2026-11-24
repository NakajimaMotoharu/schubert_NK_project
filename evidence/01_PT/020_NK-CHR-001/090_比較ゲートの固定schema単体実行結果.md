# 比較ゲートの固定schema単体試験結果

PT-CHR-DEF-SCHEMA001、BUG-3805。対象 `7ce7cd397a1a74d765c43d1038ba04dca2f69abf`、製品Core `03dfb35a6a68f4ee32e9303b4fa0df3d262156fa`、PG44602。修正前は新試験1件が失敗し、独立7条件の診断が欠落。修正後は既存を含む25件、失敗・エラー・skip各0。初回結果処理は件数の下限を誤って26と設定して終了1。元JUnitは終了0で、試験注釈22＋3と元XMLの名前を照合して25件を確定した。再実行なし。

Checkstyleは対象二Javaで0件。単一execの該当メソッドは行18/18、メソッド1/1、条件分岐0（該当なし）。無除外の全classは行253/544、メソッド22/63、class1/1、branch138/303。実Current/NKのgate、実ブラウザ、全451の認定は保留。 [実行証跡](evidence/PG44602-schema-const-and-container-types/manifest.json)
