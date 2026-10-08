# PG588 実隔離DBのtyped30拒否readback

NK-BAT-001/MorningDatabaseSession.Session.observeCleanupRejected、P017-01.03/初期0.66・1.66・3.66pp（event0086/実装前固定）、RD OPS009/DAT009/UI251/SS341343/SSC199200。host専用PG18/Flyway28・package-local Gate/Connect/Schema port、実VM/Root許可/通常親成功として認定0。SQL fixtureは独立literal、typedreceiptは既bus/kernel literal gate fixtureで、native authorityではない。

PT-OPS-MDB588001: 正規Backup2FAILED/soleCleanup handoff後、typed30だけで七空slotをreadonly二読。Backup全column SQL before=after、fakeFAILED/SKIP作成0、parent advisory保持/observer取得不可、rollback/autocommit復帰・最終Connection closed/observer取得可能。前Backup未完/hand-off未実行/wrong target/0receipt/owner期限/null/callback後のAccess再使用は拒否。002: child独立SQL fixtureはNotification RUNNING（ended/result無し）とQuestion FAILED/COMMAND_FAILURE/target1failure1だけ、返却七slotの最初二つをliteral fullrecordに照合し後五はempty、旧Backup/partial全column不変。これは部分記録の捕捉、業務成功ではない。003: 既transaction/ReadOnly状態は操作前拒否して元flagを保持、fixtureが明示rollback/復帰・最後close、null引数はfail-fast。

MACCESS9＋MDB既20/新3=選択32PTを予定、全未実施加算0/対象外not-run加算0。コマンド bash tools/quality/vm/050_s1/pg588_session_readback_v1.sh <固定HEAD>、既同source導入jar/current/PG585の1600mainclassbyte事前照合、旧selectedexecを認証してprivateへ移動/append無し、閉鎖PG588profileから新privatePG379/pg588-session-readback-v1だけ生成。 sourcefilehash/両newXML/exit/日時/静的/counterとBUG/SSC関連は実後追記、秘密/Gitdump0。既PG587 profileは旧output再実行拒否のまま、prototypeの任意Root/dir受付を追加しない。
