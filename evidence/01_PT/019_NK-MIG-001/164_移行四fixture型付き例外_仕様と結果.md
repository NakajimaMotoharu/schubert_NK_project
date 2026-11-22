# 移行四fixtureの型付き例外と通常試験

対象はNK-MIG-001、WBS-F03/2-2-bとP019-03、UI242/254、SS343/354およびSSC366。確認するTest IDとSQL、資源の所有・一回解放、元例外と抑制例外の期待値は162・163を継承する。原112件と追加2件をすべて実行した。PG42852の事前コンパイルとGit差分で、36箇所の試験宣言および4箇所のhelper宣言を具体的なSQLException、待機例外等へ変更したことを確認。期待値・入力・製品Javaの変更はない。

PG42854、2026-11-23 JST、source 500f2751e92c920fe889866e005124643ae9bcb9、製品Core e8368d22c4da2ec841f008df793594d3be9066af。JDK25、JUnit ConsoleとJaCoCo 0.8.15で通常114件成功、失敗・エラー・skip各0。scopeの行370、method117、class5、branch176は全missed0。5 CodeのCRCと389/389 probeの一致、7 abstract物理の自然NoCode、Checkstyle0を確認した。単一execの結果。試験はJDK JDBC interface合成proxyを用いる。

SpotBugs生3は元例外を故障点ごとに注入する三つのhelperのThrowable宣言。実行時例外・Error・SQLExceptionの同一性を検証する既存仕様のため、これらの指摘を記録した。PMD生38件の内訳は、借用接続3と有限のworker pool4のCloseResource、有限workerの起動・終了のDoNotUseThreads16、作業先ごとに独立したHashMap2、JDK interfaceをロードする既存proxy11、自己抑制の参照同一性2。接続の解放を呼出先の責務に付け替えず、各workerに独自fixtureを渡す。個別指摘の生結果はmanifestに保持した。

BUG-3631の包括checked宣言とYKT-2854の局所確認を完了。列・制約の兄弟scopeは160／161にある。六製品全体の451、正式受入、実DBは個別に証拠が必要。独立検証の結果、CRC、原XMLと公開XMLのhashは[PG42854 manifest](evidence/PG42854-four-migration-final-typed-v1/manifest.json)。
