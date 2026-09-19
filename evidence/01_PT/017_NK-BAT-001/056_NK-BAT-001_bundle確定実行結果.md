# NK-BAT-001 bundle確定実行結果

SSC066/PG177、055/BAT258～273、正式認定前。

- `/tmp/pgpt-pg177-green.log`: 2026-09-19 23:41:32 JST/exit1。BUG203 compile不成立、Storage16のみ成功、Batchはnot-run。
- `/tmp/pgpt-pg177-green2.log`: 23:42:52/29.074秒/exit0、選択80成功・全変更class coverage100%だったが、後続reviewでBUG204を検出し完了認定しなかった。
- `/tmp/pgpt-bug204-red.log`: 23:47:53/exit1、Storage8成功・BAT268の実同byte clone反例1件失敗。期待StorageIoExceptionに対し何もthrowされないことを確認。
- `/tmp/pgpt-pg177-green3.log`: 23:51:19/31.261秒/exit0、選択104（Storage16/Batch88）成功、failed/error/skipped0。元inode proof修正とYKT160対象全再試験、NullAway/Enforcer/Spotless/SpotBugs成功。

新BundlePublisher＋NioIoは2class/14method/60line/14branch、BundleSnapshotは1class/2method/12line/14branchのmissed0。変更Verifier本体1/23/215/124、Reader本体1/17/143/104もmissed0。private/package内部をreflectionせず公開SPIと実FD・synthetic UIDで試験した。全体coverageは次clean verifyへ。

独立goldenとtraceはmanifest964byte/hash、force4/publish1/sync2、IO301/clock514（全phase共通tick）で一致。057の全対象を再試験済みだが、同run/source/38scope認定前のためBUG199～204/YKT158～160/SSC064～066を完了にしない。全PGPT、DB成功、実dump/tar/age/restore、7世代、親処理、IT/STは未完了。
