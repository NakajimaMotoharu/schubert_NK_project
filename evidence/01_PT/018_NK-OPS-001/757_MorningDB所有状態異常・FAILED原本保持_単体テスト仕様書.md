# PT-MDB2292-001/002（新追加、実未試験）

NK-BAT-001/NK-OPS-001、MorningDatabaseSession.Session completionGuard/requireAbandonedRequest/retainedBackupSuccessful、RD OPS009/BAK、UI253、SS341343/SSC116/QA047/451。Main3b7f/PG2126/BOM62213f/全1643と既全2228-2236/当native2284へ固定する。新試験sourceは保存commitで確定、全3633旧成功を新試験の合格にしない。

Fixtureは専用LAN内の新private tmp・PostgreSQL18动态loopback port/当Flyway28history29・roleを使用し、VMや業務DBへ接続しない。既BatchDatabaseFixture/全test-class hashを前後照合する。JDBC portの対象呼出し間だけ一つの観測値を変え、finallyで戻す（実DBのautocommit/readOnly/isolation/lockを解除・偽装運用しない）。Productionは拒否すべき異常として観測する。失敗期待はIOException、NPEを正常化しない。

| Test ID | 入力・操作 | 独立期待値/算出根拠 |
| --- | --- | --- |
| PT-MDB2292-001 | 同runにBACKUP_DB/CONFIGをbegin、auto=false/readOnly=true/isolation=SERIALIZABLE/held=falseをそれぞれ一つ観測してrequireAbandonedRequest | SSの完了guardでIO拒否・業務変更0。別admin SQLで当runの正確に二step/attempt1/RUNNING/started固定値/ended NULL/全countとbytes0を前後確認。呼出元正常close後、実Connection.isClosed=true/client/advisory0。 |
| PT-MDB2292-002 | 二stepを既契約のCOMMAND_FAILUREへ完了、auto=false/readOnly=true/held=falseをそれぞれ観測してretainedBackupSuccessful | IO拒否、正常状態へ戻してもFAILED二行はeligible=false。SQLは正確に二step/attempt1/FAILED/started・ended固定値/target1-success0-failure1/bytes0。新SUCCESS/第三行を生成しない。Connection close/client/advisory0。 |

期待値はSS/DDLからのliteral SQL列・時刻・status・countで、production methodから生成しない。runUUIDは試験専用公開vector、VM実run/session/credentialではない。変化は各case独立、unknown/row不足/余剰/状態遷移/接続未返却を合格にしない。

準備済みhostwhole1tool fixture/static0・Java format。実commandは固定PYTHONPATHで`python3 -B tools/quality/pg2292_morning_guard_selected.py`、新onlyselected slotにJDK25.0.4/XlintWerror・JUnit exact二test/XML/FES-aborted-notRun0を照合する。全MainJARは最新3633のSHA/CRC、追加testのみcompile、既全fixture不変、旧0fdnative0。六host＋同2284九latest＋新selectedの全counter/XMLを技術測定するが、全scope正式及び新tests sourceのfresh全体回帰は別必須。

Coverage・実結果・実manifest/hash・BUG番号は実行後追記。現状=未実行、PASS/100%/工程完了への加算0。既BUG1224等の正常回収/当ownedstopは再発行しない。
