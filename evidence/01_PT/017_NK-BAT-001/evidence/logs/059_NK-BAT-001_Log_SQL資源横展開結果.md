# NK-BAT-001 Log SQL資源横展開結果

正式認定: PT-WEB-20260920-01/source5f813145c442e2b80df28d0ede5d1a9e4b9b55ad/dev-foundation、2026-09-20 00:50:23～01:06:30 JST（Maven終了01:06:29、16:05/exit0）。全1455 PT・failed/error/skipped0、6 Java全4coverage100%、Production5静的解析未解決0、固定path3method限定review・coverage除外なし。38scope/46負canary成功。PG178～180の497複合とCleanup4 NULL、既存SQL/不正投影/所有/rollbackを再確認。Batch95class/578method/3515line/1843branch、全missed0。BUG205/YKT161完了、BUG195/206・YKT154/162・SSC063の残Repositoryは継続。新JUnit/部品加算0、実NK CHR/親全体/PGPT/IT/STは未完了。実行環境・入力期待実際・source/test/hashは017/evidence/manifest.json、raw log SHA256=936f1e675b26c8a023d4a61b08d27b6ad9c836af984fe252d77db777c132999a。以下の未認定表記は探索履歴。

探索log SHA256: red=`386c83937e88134b356b1c5d791846d8adf9ad8fca343cdf7fe5e9a576d6cb23`、green（静的不合格）=`b73819b5217834d2d892a880003e804821fcb23ca0bd334009da3ad2367e4f88`、green2=`d8afd05b80237e66bb51a0bba0465eab514932eed7d20b4c6727ba1f162eea32`。原logは/tmp、正式証跡は対象commit固定後の全reactorから生成する。

PG178/SSC063/BUG195/YKT154、058・BAT026/029。正式認定前。

修正後 `/tmp/pgpt-pg178-green2.log`、00:28:57 JST/33.152秒/exit0。Storage8＋Log12の20 PT（BAT026内225複合）成功、failed/error/skipped0。Log3class/13method/137line/62branchは全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。4 JDBC境界全てdirect finally close、外側leaseの元primary優先、close回数と実lock回収を確認。新JUnit/部品加算0。BUG205/YKT161は正式全reactor/同source証跡待ち、BUG195/YKT154/SSC063は他SQL所有scopeが残るため継続する。

最初の修正 `/tmp/pgpt-pg178-green.log` は00:25:03 JST/34.187秒/exit1。Storage8＋Log12の20PT（225複合含む）は成功し、変更Log3class/16method/113line/50branchはmissed0。しかしSpotBugsがJDBC4scopeの所有解消を追跡できずOBL_UNSATISFIED_OBLIGATION4件となり非合格。BUG205/YKT161へ修正前登録し、直接finally closeへ変更する。PT/coverageだけで合格にしない。

修正前 `/tmp/pgpt-pg178-red.log`、2026-09-20 00:21:25 JST終了、9.914秒/exit1。Storage共通8成功、Log BAT026の1件失敗。lock.nextとlock.resultCloseへ同じ公開合成IllegalStateExceptionを注入し、期待は元identityの伝播、実際はJava TWR self-suppressionによるIllegalArgumentException。未失敗の他PTを含め新正式合格とはしない。反例sourceは127d9446にtestだけ追加した作業状態、Productionは未修正。

再現commandは058の選択commandからtestを `ResourceScopeTest,LogCleanupServiceTest#restorationAndUnlockFailures` へ限定しgoalはtest。JDK25.0.4/Maven3.9.12、dev-foundation、Ubuntu26.04.1/amd64。秘密情報は使用していない。次は5所有scopeの修正と全複合・既存12PT/coverage/staticの再試験。
