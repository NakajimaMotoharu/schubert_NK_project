# PG2590 原本再検査・cached資格拒否

NK-OPS-001/MorningDatabaseSession.Session.completeReusedBackup/retainedBackupSuccessful、SS341/343/353/354、WBS-P017-01.03/0680群subset（追加予算0）、N05/K01参照0。当full3653/1643/current九nativeと資格済2588 execをSource/Jar/hash完全一致で使う。

PT-MDB2590-001：4隔離業務日、COMPLETE/RETENTION×RUNNING/BYTE。実成功原本二row→実resume二SKIPまで生成し、隔離PGPT管理roleで旧原本二rowをRUNNING/ended-null/count-byte0又は実byte+1へ変異。completion直前又はretention前に、二回目の完全原本検査が必ず拒否することをouter executeのIOExceptionで確認。RETENTIONの粗eligibilityだけはcached SUCCESSを注入し、それで完全再検査を省略/削除許可にできないことを検査する。

期待値はliteral SQL全4rowのstatus/start/end/count/byte/error、実Connection/client/advisory0。変異は隔離host fixtureだけ、Production VM/原本Backup実体/Root/restore/prune/ADMINに作用0。変異後DBを成功値へ修復して期待を合わせず、三row省略やプロジェクタ自作値でactualを代用しない。Known repository例外はouter境界で固定IO、NPEや未知例外を正常扱い0。

command：固定PYTHONPATHでpg2590_original_reinspection_selected_test.py→clean固定→pg2590_original_reinspection_selected.py。独立工具二fixture、javac -Xlint:all -Werror・限定1JUnit/4case/FES-aborted-notrun0/全Main CRC0/入力fixture-native-byte不変を要求。元L799/M156/C9/B555、新methodは旧3653へ加算0、必要群統合後/正式1964-53/leaf依存は未完。

v1/session54989 actual1：新test内Operation callbackの隔離管理SQLがchecked SQLExceptionを処理しておらずjavacで拒否、JUnit未実行。private compile logを保持し合格へ加算0。既承認期待値とProductionは変更せず、fixture SQL失敗を固定IOExceptionへ伝搬するcatchを追加。v2は新namespaceで実行しv1を上書きしない。v2実結果は未観測。
