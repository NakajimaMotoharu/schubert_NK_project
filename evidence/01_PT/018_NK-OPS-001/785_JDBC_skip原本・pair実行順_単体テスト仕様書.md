# PG2490 JDBC skip原本・pair実行順

NK-OPS-001／MorningDatabaseSession.Session.observeBackup/observeBackupPair・lambda、SS343/353/354、SSC133/134。WBS-P017-01、N05参照費0、0642/0644群予算1/3/7ppのsubset、追加配賦0。

PT-MDB2490-001／mdb2490001：独立SQLでoriginalのCONFIG idをDB idより小さく置き、両SUCCESSの固定count/byte/時刻を用意。正規beginResume/completeReused後、四case=VALID／manifest欠落／recipient fingerprintだけ不一致／original読取row欠落を検査する。正常はcurrent二SKIPPEDとprior二SUCCESSを必ずDB→CONFIG順へ対応し、原id/attempt/count/byte/時刻はliteral oracle、current idは別admin SQLから導く。異常はIOException、四実SQL行・原本の全値は不変更、Connection閉鎖・owner/advisory0。期待値をproductionの戻り値から生成しない。

PT-MDB2490-002／mdb2490002：正規FAILED二行をcommitし、JDBC terminal読取の一件目欠落／二件目欠落／三件目余剰を別caseで注入。期待=exact cardinalityを満たさないため拒否、別接続SQLでは正規二行・全元値、資源0。reflectionでtrusted内部stateを作らず、実DDL/driver/commit/rollback/closeを使う。

実command=`python3 -B tools/quality/pg2490_backup_original_selected.py`（固定PYTHONPATH）。fresh PG2490-selected-v1、JDK25.0.4/実PG18・Werror・二JUnit XML/FES/aborted/notRun0・全1643Main CRC・PG2404 immutable fixture/依存・PG2474 latest九native・PG2478v4 qualified選択execを検査する。旧source/native輸入0、VM/業務/原本/Backup/start/stop/reload操作0。実source/time/exit/coverage/証跡hashは取得後追記、全体正式認定と区別する。
