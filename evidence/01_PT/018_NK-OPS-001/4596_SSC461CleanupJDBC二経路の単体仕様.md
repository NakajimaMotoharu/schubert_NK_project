# SSC461 Cleanupの借用JDBC二経路の製造・単体仕様

WBS-F02-a、WBS-P017-07.02、NK-BAT-001／SYS-005、DAT-009/OPS-009、UI251、SS311/332/341、SSC051/057/461、BUG-3233／YKT-2680。CleanupRepositoryのexecuteとreadLogProgress、CleanupStepRepositoryのexecuteのSQL例外から、既Bootstrap JdbcFailureGraphに接続する。SQL、入力、業務上のlimit、固定結果・障害診断、借用Connection、資源の解放順と既例外優先は元契約を維持する。

原703・705仕様のCLNPORT001～009、CLNQUERY001～009を変更せず使用し、固定SQL・列値・JDBC bind・件数制約・null・異常・元本体/close優先とborrowed owner後条件を入力側で独立に照合する。テスト接続は既memory Proxy。実DBや実削除は起動しない。実運用競合のDB後条件は元WBS別受入を維持する。

Java25、厳格NullAway、Checkstyle、SpotBugs Max/Low、全policy PMD、独立JUnit XML、単exec・物理CRC、生成switchを含むunfiltered 5counter、ABI差分。生成switchの未到達は機械生成理由と実測を記録し、実測へ加算しない。既生測定と結合しない。全F02、P017-07、451を未受入で管理する。
