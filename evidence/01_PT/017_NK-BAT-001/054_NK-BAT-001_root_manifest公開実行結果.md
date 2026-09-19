# NK-BAT-001 root manifest公開実行結果

2026-09-19、SSC064/PG175、053/BAT242～257。正式認定前・未完了。

追加探索 `/tmp/pgpt-pg175-green4.log` は2026-09-19 23:06:03 JST終了、21.569秒、exit0。全選択24 PTと静的解析成功、実part/公開先/子directory差替えと別instanceのcaller共通排他を追加確認した。coverage100%は除外なし。次はcommit固定のPT-WEB-20260919-01で全reactorを認定する。

探索選択run `/tmp/pgpt-pg175-green3.log`、2026-09-19 23:03:08 JST終了、21.016秒、exit0。Storage ResourceScope8＋Batch新16＝24 PT、failed/error/skipped0。JDK25.0.4/Maven3.9.12、source未commitの探索。新class1/method20/line175/branch122は全missed0、Batch/Storage SpotBugs error/warning0、コンパイルNullAway/Enforcer/Spotless成功。追加の実namespace入替え/別instance外部排他は次探索で確認する。

BUG199衝突reason/現物保全の再試験は選択runで成功、BUG200は019の42canary成功で再確認。正式全reactor/source固定・collector・同run/hash検証まで認定を保留する。PG/PT全体、実archive、親制御、世代管理、IT/STを完了としない。
