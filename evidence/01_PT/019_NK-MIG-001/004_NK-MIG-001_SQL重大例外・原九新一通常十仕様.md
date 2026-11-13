# NK-MIG-001 SQL重大例外・原九新一通常十仕様

Program NK-MIG-001、SchemaHistoryAdmission/RowとJdbcAdmissionFailures、関連Source/DBAdmissionはP01805。BUG2806/2807/YKT2359/2387、SS3313.3/343SSC082084095/354451、SCHEMA001..010。四MainのknownSQLfatal処理を是正したが、通常PT閉包はSchema/helper/StorageのMain3/physical5であり、関連2Mainの動的受入は増やさない。

原whole9の固定六列・SCHEMA/V001/checksum-170000001・全column/null/余剰/最大1000行、固定query/timeout5、rows-statement-close各1/借用Connection0、IRQ、64通常type優先matrixを維持。並行8worker/barrier5s/future5sは不変更、finally shutdownNow/awaitTermination10s assertionだけ追加する。

新SCHEMA010はprepare/settimeout/execute/next/rowclose/statementcloseの6位置×cause/suppressed/cycle/SQLnext4graphの24条件。元Error identity、cause/supp無し、位置別固定closecount（prepare0,0,0・timeout/execute0,1,0・残り1,1,0）を確認。SQL primary内fatalと普通rowcloseRuntime、普通SQL primaryとrowcloseSQL内fatal＋statementRuntimeの追加2条件で、正規所有のcloseを全て試行し、元Errorと固定安全diagnosticだけを維持する。未知のnonSQL primaryと原64matrixは不変更。expectedは設計/独立literal、Production helperで生成しない。Row構造は入力fixtureの型表現であり運用DBの実測/実signedrelease値と混同しない。

JDK/JSpecify/JUnitだけ、Connection/Statement/ResultSetは全メモリProxyでRoot/DB/Flyway/DDL/migration/credential/native/actual4なし。MainはRoot Java25/NullAwayでfresh compile、physical全5をcoverage/CRC/SB対象とし、targetはSchema+RowとJdbcHelperの全source2。Storage/Reasonの未網羅は独自除外せず残す。Source全4はGJF/CS0だが、関連2Main全static/PTは未。source固定後preflight→whole10を一度実行→独立post、command/OS/JDK/source/run/終了code/XML/input/hash/counterはmanifest chainへ。正式451/190と実DB後条件は未受入。
