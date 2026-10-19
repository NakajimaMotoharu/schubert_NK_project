# F03 例外・JDBC cleanup current型検査

NK-OPS-001/411/451/SS332・SSC063/199、主担当WBS-F03。群V4_F03_TYPED_FAILURE_CONTEXTの開始見積.25/.75/2pp固定。Source0ea400109の全849Main・全1664実class/選択73を固定し、既all849解析mirrorは全file hash一致時だけ読取利用する。旧sourceの試験成功やnativeへ加算しない。

`pg5592_current_failure_facts.py`はJDK25公開compiler APIで全catchのparameter型/同symbol再throw/別throw/return/代入/break/continueと、指定されたJDBC close/primary保存/secondary判定の正確な型構造を採取する。SourceCatchContextInventory/SourceJdbcClosePrecedenceInventoryの独立手書きfixtureを併用する。単なる最後の同parameter再throwを適用性合格へ変換しない。未知cleanupやcatchの握り潰しは未判定のまま。

解析classpathは現選択の実class、署名PG5430 BOM内の第三者JAR、実POMのprovided注釈4.10.4と宣言transitive JSR3053.0.2だけ。全hashを前後一致、compile `--release25 -Xlint:all -Werror`、Mainの初期化/私有method呼出し/実DB・VM操作なし。raw compiler errorはprivateへ保存し失敗時に結果を上書きしない。

実行: 既PYTHONPATHで`python3 -B -m unittest tools/quality/source_catch_context_inventory_test.py tools/quality/source_jdbc_close_precedence_inventory_test.py`、その後`python3 -B tools/quality/pg5592_current_failure_facts.py`。fixture再実行は新runnerが使う二つのgrammar/schemaの接続確認であり既全回帰/Production PT再演ではない。出力new-only `work/pgpt-runs/PG379/pg5592-current-failure-facts-v1/manifest.safe.json`。後続はcurrent診断の全指摘をactual coordinateへjoinし、承認済契約と当whole独立test XMLのある個別項目のみ判断する。F03/正式/coverage/工数率未受入を維持。
