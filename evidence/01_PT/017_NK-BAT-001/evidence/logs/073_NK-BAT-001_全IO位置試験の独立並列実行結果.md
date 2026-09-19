# NK-BAT-001 全IO位置試験の独立並列実行結果

PG185/017072/PT-BAT-110、Production変更なし。正式PT-WEB-20260920-04/source e63b7d045fa7d64aa532fa95494020e3c4492514、02:27:35～02:39:18 JST、clean verify 11:41/exit0、1471PT/6Java全4coverage100%/38scope/48負canary成功で認定。JUnit/部分成果数は増やさない。

正式対象classは177.616秒（16PT成功）、全6768位置を維持。直前正式03の397.9秒から約55%短縮、全reactorは15:26から11:41へ約24%短縮した単回観測であり性能保証ではない。Batch96class/583method/3665line/1899branch全missed0。正式環境・command・source・sanitized証跡はevidence/manifest.json、raw log SHA256=`b01c4c44fdba5a613221f0816c21cae480e562f1d68d1e450298223305029615`。以下は選択実行履歴。

初回 `/tmp/pgpt-pg185-green.log`: 2026-09-20 02:20:00 JST終了、11.875秒/exit1。新しいtest-only DatabaseShard.closeのthrows ExceptionがInterruptedExceptionのtry warningとなり-WerrorでtestCompile失敗。warning抑止をせずIOExceptionへ狭め、停止中割込を非成功・flag保全として修正した。SHA256 `7ccb6cada4e3155c5ddf5fabd1f0bd3215ab7970f27774482bf65e695f3c050d`。未実行Batchを合格に含めない。

再実行 `/tmp/pgpt-pg185-green2.log`: 2026-09-20 02:24:11 JST終了、3:18/exit0。Storage8＋Batch16＝24 PT成功、failed/error/skipped0、NullAway/Enforcer/Spotless/SpotBugs成功。対象class 178.8秒、直前の逐次正式20-03では397.9秒、今回の観測値で約55%短縮（約2.23倍）。異なる実行全体での単回比較であり、恒常性能保証ではない。全6,768位置・独立inventory・注入到達・固定failure・取得済資源0、実行集合完全一致/重複0を維持。追加3cluster/各Connectionと4worker終端後に成功。SHA256 `7e55e3859c71ec201fb9342543a320ff43ee4895d35c00b6b0d45c44c2d1e7d8`。

sourceはd1a7b483＋当test変更のみ、branch dev-foundation、Ubuntu26.04.1/amd64/Linux7.0.0-31/JDK25.0.4/Maven3.9.12/PG18.6/JDBC42.7.13。12CPU・RAM約15GiB、試験中swap使用0。Mavenは1本だけ、JUnitの全体並列化はしていない。各shardの実PGは同じproduction Flyway、native fixtureは各workerで生成し絶対path深度4を維持。実DB/credentialには接続しない。

command: 071のJAVA_HOME/offline/repository引数、選択`ResourceScopeTest,MaintenanceRunRetirementTest`、goal test/JaCoCo report/SpotBugs check。当選択では以前の全execに追記するためJaCoCoの全Batch100%表示を新sourceの全体認定へ流用しない。次のclean verifyと38scope/48canaryで再認定する。全PGPT/IT/ST・新機能完成ではない。
