# PG2490 JDBC skip原本・pair実行順

NK-OPS-001／MorningDatabaseSession.Session.observeBackup/observeBackupPair・lambda、SS343/353/354、SSC133/134。WBS-P017-01、N05参照費0、0642/0644群予算1/3/7ppのsubset、追加配賦0。

PT-MDB2490-001／mdb2490001：独立SQLでoriginalのCONFIG idをDB idより小さく置き、両SUCCESSの固定count/byte/時刻を用意。正規beginResume/completeReused後、四case=VALID／manifest欠落／recipient fingerprintだけ不一致／original読取row欠落を検査する。正常はcurrent二SKIPPEDとprior二SUCCESSを必ずDB→CONFIG順へ対応し、原id/attempt/count/byte/時刻はliteral oracle、current idは別admin SQLから導く。異常はIOException、四実SQL行・原本の全値は不変更、Connection閉鎖・owner/advisory0。期待値をproductionの戻り値から生成しない。

PT-MDB2490-002／mdb2490002：正規FAILED二行をcommitし、JDBC terminal読取の一件目欠落／二件目欠落／三件目余剰を別caseで注入。期待=exact cardinalityを満たさないため拒否、別接続SQLでは正規二行・全元値、資源0。reflectionでtrusted内部stateを作らず、実DDL/driver/commit/rollback/closeを使う。

実command=`python3 -B tools/quality/pg2490_backup_original_selected.py`（固定PYTHONPATH）。fresh PG2490-selected-v1、JDK25.0.4/実PG18・Werror・二JUnit XML/FES/aborted/notRun0・全1643Main CRC・PG2404 immutable fixture/依存・PG2474 latest九native・PG2478v4 qualified選択execを検査する。旧source/native輸入0、VM/業務/原本/Backup/start/stop/reload操作0。実source/time/exit/coverage/証跡hashは取得後追記、全体正式認定と区別する。

## 実結果

v1 actual1：新oracleのSQLExceptionがcallback IOException契約へ伝播されておらずjavacで拒否、試験未実行。初期v2の純工具試験は前結果のCRCを存在しないtop-level keyで読んで失敗、実発行前に全六moduleの型付きCRCへ是正し、wrong source/false/null/欠落/非0/hash差の十negativeを追加。新fixture製造失敗は保存しProduction障害と読み替えない。

v2/session55701 actual0、testSource3456059b2210e5e9acc964f72ec22f4988963295、22:52:39.503734Z～22:52:53.057925Z。二PT・七case/FES/aborted/notRun0・warnings0・Main CRC不一致0、実SQL原四行/二行・owner/advisory0。manifest6076964ff66d5e5adcd848f2de3f838b8abb7085fa1c8cb528a5b271a471bce3、payload012d17daccf7530f84de04eb1aff446f41ca877f62fd3d5ec98e87d4bd4952f1。PG2486v2の実selected execも全同Main Jar/Source・filehash資格後に合わせ、技術残L805/M157/C9/B576、直前から1line/1method/6branch追加。

SessionはL603/628・M40/41・C1/1・B308/387、未閉鎖。最新証跡=`evidence/current-jdbc-backup-boundaries/manifest-2490-v2.json`。VM/業務/原本/Backup/current不変更、全体全回帰と正式1964/53へ単純加点0。新四Broker＋新八JDBCの12methodを一つの必要な全回帰へまとめる。旧sourceのnative輸入0。
