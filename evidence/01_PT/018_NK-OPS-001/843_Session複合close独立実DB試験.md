# Session複合close独立実DB試験

2026-10-15JST。Program NK-BAT-001/MorningDatabaseSession.query/Session.successfulBackup/execute、PT-MDB-2804-001、RD DAT009/OPS009・UI251・SS331/341/343/355、BUG1251/YKT1017の追加複合close確認。WBS-P017-01は共通主担当、消費側参照費0。

## 入力・独立期待値

既実DB fixtureへ固定run/日時/二つのSUCCESS Backup行をSQLでseed。正規実JDBCのtyped failure_countだけ未信頼1へprojectionしchecked IOExceptionを誘発、closeでROWS/STATEMENT/BOTH各SQLExceptionを追加。期待はfixed IOException/原因null、内部primaryのsuppressedは1/1/2のredacted BatchRepositoryException、provider私有message/cause漏洩0。外facade fixed IOExceptionはsuppressed0。実SQL原行全列保持、row/statement各close一回、connection閉鎖・client/advisory0を別SQL/状態で確認。expectedをProduction計算から生成0。

試験method `mdb2804001CheckedCallbackAndCompoundJdbcClosePreserveRowsAndRedactSecondary` は既60methodsと一緒に全61実行。原私有draft2804を保持し、Testだけsrcへ追加、Main/JAR/guest変更0。Test source c04764ddb、tool修正ae9ba5b72。

## 実行・再試験

command `python3 -B tools/quality/pg2912_jdbc_compound_close_selected.py`、PYTHONPATH838同値、aru隔離host DB/Java25.0.4。v1/session48381 actual1は工具入力count0/XML61でcardinality拒否（ケースfailure0でも合格加算0）、BUG1257/YKT1023を修正前起票。named TESTへ是正しwrong ordinal counterexample含む純二試験PASS。既v1slot/log/XML/inputを保全、new-onlyv2/session84204 actual0/61PT/F-E-S-aborted-notRun0/Xlint-Werror0/原fixture・旧XML不変、Main再compile0。

私有WorkPG379 `pg2912-jdbc-compound-close-selected-v2/manifest.safe.json`、payload2b0e44db07e6168b81b3b0f1af99c5b15a97db427524b2ac88bf7ba33f5ee0a9、LANmanifest2cb725c296d2f99b7f3029af6613f06a159e4837b3469376c865fa5cf615c143、XMLaffbad7fe0c5d4775741a6eb039ad677e3b4f5807fce624100ad590a7e99c857。実環境/時刻/command/input/output/hashは各manifest、raw DB/秘密情報Git0。

当追加Test群のfresh全体回帰・coverageは未実行でclaimfalse。旧3680/542成功は当時snapshotとして保全、新Test sourceへ流用しない。新Main差0なので配備/署名/Root/native再採取不要、必要群全回帰で全1643同byteを改めて資格して当nativeを正当にjoinする。正式1964/53/leaf受入0・工数null、BUG1251/YKT1017全体閉鎖は後続品質条件を満たすまで保留。
