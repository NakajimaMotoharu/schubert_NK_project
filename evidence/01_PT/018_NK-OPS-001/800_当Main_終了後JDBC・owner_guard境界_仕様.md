# PG2570 終了後JDBC/owner再認証

## v2実結果

actual0/testSourcec3daf71bd1815bd13803e77d6b9111ecec84b0f2/payloadac2b20f3/servera60e5716・限定1PT/12case/FES-aborted-notrun0・javac warnings0/全Main CRC0/VM操作0。SQL pair不変・Connection/client/advisory0、3line/3branch追加、当sameSource合成残L799/M156/C9/B561。公開final-guard-manifest-v2.json。旧v1新oracle失敗は保持し合格0、必要統合回帰・正式/leaf依存は未完。

## 初回新oracle構築失敗

v1/testSource8a46a6569 actual1、payloada87320ad、JUnit失敗IOException/execute497を保持。新oracleが拒否後に同callbackでsnapshot再取得まで要求したが、owner例外後の未完transactionはouter closeで回収する契約であり再授権を仮定しない。正常snapshotを注入前に独立値確認し、拒否後はliteral SQL不変とouter close/client/advisory0だけを確認するv2へ是正。Production/業務期待値の変更0、旧v1を合格0、v2未実行。

NK-OPS-001/MorningDatabaseSession.Session.failedBackupSnapshot/observeBackup/recheckConsistent、SS341/343/353/354、WBS-P017-01.03・0670群subset/追加予算0。既2568同Main入力・独立実結果digestから資格されたselected execだけを参照し、当fullPG2510/最新9native/hashと六Jar全等価を要求する。

PT-MDB2570-001：実隔離PostgreSQLに12独立業務日/runを作り、実FAILED/COMMAND_FAILURE pairを完成。各guardにautocommit=false、readOnly=true、isolation=SERIALIZABLE（snapshotのみ）、SQLException、owner IOException（owner契約有り二操作のみ）を注入。全12caseでIOExceptionと注入実行を確認。armed解除後は実snapshotのid/run/start/endとliteral SQL pair全値、Connection閉鎖・全client/advisory0を確認。異常を成功読替え0、production expected生成0、DB書換えで期待を合わせない。

command：固定PYTHONPATHで pg2570_failed_guard_selected_test.py→clean固定→pg2570_failed_guard_selected.py。独立工具二fixture/static/全namespace compile、限定JUnit一PT/12case、FES/aborted/notrun0、javac -Xlint:all -Werror、Main/fixture/native/依存hash不変/CRC0必須。actual PT未実行、結果は取得後別記。旧2568初回compile失敗は合格0、全3650へ新method件数合算0・必要群統合回帰未完。元残L802/M156/C9/B564、正式1964/53/leafdelta0、N/T・個別費null。
