# NK-BAT-001 bundle確定実行結果

正式認定: PT-WEB-20260919-02/source 0ca3aa9588fa480ccf4b3e4ff06561f627365e66/dev-foundation、2026-09-19 23:58:54～09-20 00:14:59 JST、Maven16分04秒/exit0。全1455 PT（80/74/660/241/359/41）・failed/error/skipped0、6 Java全4coverage100%、Production5静的解析未解決0、固定path3method限定review・coverage除外なし。15collector/38scopeと46負canary成功。PG175/176/177の16/8/16 PT・3部品を認定、BUG199～204/YKT158～160/SSC064～066完了。実archive生成/DB成功caller/7世代/親全体/実NK CHR/IT/STは未完了。実行環境・source/test/入力期待実際・hashは017/018各evidence/manifest.json。raw実行log SHA256=b777f9ea117c514d2ae78fcc402aaf9711147655a50df31024e6eeb47c0abf94。以下は探索時点の履歴であり、旧「未認定」は当時の状態。

SSC066/PG177、055/BAT258～273、正式認定前。

- `/tmp/pgpt-pg177-green.log`: 2026-09-19 23:41:32 JST/exit1。BUG203 compile不成立、Storage16のみ成功、Batchはnot-run。
- `/tmp/pgpt-pg177-green2.log`: 23:42:52/29.074秒/exit0、選択80成功・全変更class coverage100%だったが、後続reviewでBUG204を検出し完了認定しなかった。
- `/tmp/pgpt-bug204-red.log`: 23:47:53/exit1、Storage8成功・BAT268の実同byte clone反例1件失敗。期待StorageIoExceptionに対し何もthrowされないことを確認。
- `/tmp/pgpt-pg177-green3.log`: 23:51:19/31.261秒/exit0、選択104（Storage16/Batch88）成功、failed/error/skipped0。元inode proof修正とYKT160対象全再試験、NullAway/Enforcer/Spotless/SpotBugs成功。

新BundlePublisher＋NioIoは2class/14method/60line/14branch、BundleSnapshotは1class/2method/12line/14branchのmissed0。変更Verifier本体1/23/215/124、Reader本体1/17/143/104もmissed0。private/package内部をreflectionせず公開SPIと実FD・synthetic UIDで試験した。全体coverageは次clean verifyへ。

独立goldenとtraceはmanifest964byte/hash、force4/publish1/sync2、IO301/clock514（全phase共通tick）で一致。057の全対象を再試験済みだが、同run/source/38scope認定前のためBUG199～204/YKT158～160/SSC064～066を完了にしない。全PGPT、DB成功、実dump/tar/age/restore、7世代、親処理、IT/STは未完了。
