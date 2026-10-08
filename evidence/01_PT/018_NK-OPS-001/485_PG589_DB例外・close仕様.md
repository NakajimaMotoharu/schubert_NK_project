# PG589 DB例外・close後条件

NK-BAT-001/MorningDatabaseSession.execute/Session.observeCleanupRejected、P017-01.03の既群0.66/1.66/3.66pp内、RD OPS009/DAT009/UI251/SS341343/SSC199200。別native経路/正式受入ではない。対象34PT予定=Access9/MDB既23＋新2、合格はactual実後だけ。

PT-OPS-MDB589001: 同じhost隔離PG18 actualUrlで正規Backup FAILED二行→soleCleanup30→readback。接続のgetAutoCommit/isReadOnly/setAutoCommit(false)/prepareStatement/rollback/setAutoCommit(true)の六JDBC failureとowner bindの期限拒否一つを自然な操作経路に注入。実Driverへ全その他操作を委譲し、例外は独立literal PRIVATE_SQL_FAULTで期待値生成にProductionを用いない。七fixtureは独立JST日付09-10～16・run別（PG588の10-06～08と非衝突）、各実SQL全column before=after、全connection閉鎖/advisory取得可能、外部message固定root batch database unavailable/cause・suppressed空が期待。人工到達/reflectionによるprivate呼出し・除外0。

PT-OPS-MDB589002: 実ConnectionをcloseしてからSQL/Runtime/Errorを返すdriver adapter、callback正常/IO拒否の六組。close一回・実connection closed・observer同DBadvisory取得可能。SQLはsanitized IOException固定message/cause-suppressed空、未知Runtime/Errorは同identity再throw。close結果を正常認定しない。

実行 `bash tools/quality/vm/050_s1/pg589_session_sql_close_v1.sh <固定HEAD>`、same PG585/current/m2全main1600byte/前PG588 execSHAを事前認証、新onlyprivatePG589/exec分離/append0、source/終了値/newXML/static/counter/hashは実後追記。実source別全回帰・全global100/正式は未達のまま。JDK25.0.4/Maven3.9.12/Flyway28/PG18/Spotless-Spotbugs-NullAway/JaCoCo0.8.15、秘密dump出力0。
