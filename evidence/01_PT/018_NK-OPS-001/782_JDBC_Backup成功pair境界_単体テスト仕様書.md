# PG2480 JDBC Backup成功pair境界

NK-OPS-001／MorningDatabaseSession.Session.successfulBackup/successfulHandle、SS343/353/354、SSC129/133/134。WBS-P017-10主担当、N05参照費0。群V3_CURRENT_JDBC_BACKUP_PAIR_BOUNDARIES、着手予算1/3/7週次共有pp、events0642を保持。Production cdbc・PG2404全Main1643を再compileせず、当PG2474九nativeと資格済みPG2478v4 selectedだけをbyte/hash照合して測定する。全体再回帰/正式更新は別条件。

PT-MDB2480-001／mdb2480001：実隔離PostgreSQLへ手書き二SUCCESS行（DB1/1/26byte・CONFIG2/2/67byte、同run/attempt1/開始・終了+3秒）をinsertする。JDBCの読取境界だけで日付/開始逆転/未来終了/非micro精度/target/success/failure/byte/error二字段/null ID・step・終了を一つずつ変異。期待=秘匿IOException、実Connection閉鎖・owner/advisory0、別接続の全二行・全count/時刻/状態/errorは元の独立SQL fixtureと一致。正規projectionはliteral BackupBeginsと一致する。

PT-MDB2480-002／mdb2480002：同独立二行に対し二件目欠落・三件目追加・step/attempt/開始/終了のpair不一致・SQL例外を注入。期待=再利用資格を拒否、実SQL全値不変更・資源0。最初のrow欠落はOptional.emptyで成功資格なし。正常再読は二固定handleと一致する。期待値をproduction methodで生成せず、初期SQLと標準時刻算術から作成する。

null/境界/異常/driver例外/所有終了と再読を含む。外部業務のBackup・Root・ADMIN・start/stop/reload・VM DBへの作用0。実DB driverと独立SQLを用い、reflectionでProduction内部状態を無理に書き換えない。新test fixtureの初回不備は失敗のまま保存し、既実装の仕様違反なら修正前にBUG/YKTを起票する。

実command=clean固定後、固定PYTHONPATHで `python3 -B tools/quality/pg2480_backup_pair_selected.py`。新PG2480-selected-v1、JDK25.0.4/実PostgreSQL18、javac Werror、二JUnit XML/FES/aborted/notRun0、全Main CRC、六module coverage/XML/hash、固定fixture/依存前後hashを確認する。実commit/日時/結果/coverage増分/関連BUG/証跡hashは取得後記録、未実行は合格0。
