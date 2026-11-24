# Scenario配置record同一性 実行結果

PG44120でPT-MIG-PLACE013と既存12件を同時実行し、13成功、失敗・エラー・skip各0。試験source `161c7f5464ef54c6d32d610777dc0568868d1b07`、製品Core `4d3a0f69c8241f6dd3dbe67e5fdf7b067cd98349`、正規Bootstrap JAR同物理。合成配置と出力で同値は一要素、indexまたはfileが異なる値は別要素になった。

同一execの対象三物理で行79/79、メソッド29/29、クラス3/3、分岐24/24。新規fixtureの書式・Checkstyle・PMDは各0。既存12件の新規Test ID加算0。実asset、DB、現行移行、全451・正式受入は未実行。

[単体仕様](177_Scenario配置record同一性の単体仕様.md) [証跡](evidence/PG44120-current-scenario-placement-raw-complete/manifest.json)
