# 220 NK-OPS-001 Morning backup request root公開・限定実行結果

2026-09-28 JST、branch `dev-foundation`、source/test/spec commit `bca771325`。Test IDと独立期待は219。Linux host UID1000、JDK25.0.4、Maven3.9.12、Node24.19.0、JaCoCo0.8.15、SpotBugs4.10.4.0。

`MorningBackupRequestPublicationTest`6＋既存`BackupWorkerRequestFilesTest`8＝14PT、F/E/S0、Batch静的0。手書きevent列によりroot再確認→owner取得→new-only公開→再確認→close→再確認、拒否時の公開0/close試行・null/割込を確認。既存File PTで旧requestの上書き拒否/0600/readbackを併走。開発中SpotBugs2 findingは固定path抑制注釈のlambda付与位置誤りでhelperへ是正、是正後の選択試験だけを合格算入。実VMで固定directoryは未作成、既存Unitはinactive/PID0で不変更。

root/security境界変更として456へ事前triggerを記録し、同source Production6 `clean test`＋JaCoCo/SpotBugsを実行。Protocol80/17suite、Storage149/21、Bootstrap175/22、API742/123、Web555/85、Batch713/86、合計**2,414PT/354suite**、F/E/S0、全6 SpotBugs BugInstance0、Maven exit0。原始log Git外`/tmp/pgpt-pg349-six-final.log` SHA-256 `fe3e67b33062422052c33c9b617f191e338219518979c50777541a93fce04593`。sanitized JUnit354＋coverage2＋static6＝362fileは`evidence/provisional/PG349-backup-stage/`、manifest SHA-256 `9f071677aa04e8e636c85e1d7d25c0b03f07a6f6b59d65c5e2dda7dd96f600d3`。collector初回2試行はbytecodeのないinterfaceとBRANCHなし匿名classを誤処理し未認定、失敗出力をGit外へ退避。修正後collectorで全hash一致・秘密pattern0。JUnit properties/stdout/stderr/失敗payloadは格納しない。

4指標coverage missed（branch/line/method/class）はProtocol/Storage0、Bootstrap`37/11/4/0`、API`1/19/3/0`、Web`1/19/3/0`、Batch`15/235/92/12`。`MorningBackupRequestPublication` native factory/匿名ownerを含め未被覆で、class単位100%未達。実root directory・VMの発行/retire、backup Unit/manifest/DB成功、外部Morning main/permitは未受入。正式source`858713c0bf310ae8bf62078b0a1cedbce4e968db`/run`PT-WEB-20260925-24`/1964PT/53scope、加重中心48.3%を据置。関連BUG-315/YKT-248、YKT-250、SSC-055/089/092/094/104/105継続。
