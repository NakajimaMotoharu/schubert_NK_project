# 218 NK-OPS-001 Morning backup request公開順・限定実行結果

2026-09-28 JST、branch `dev-foundation`、source/test/spec commit `775421d8e`。Test IDと独立期待は217。Linux host UID1000、JDK25.0.4、Maven3.9.12、Node24.19.0、JaCoCo0.8.15、SpotBugs4.10.4.0。

選択`MorningBackupPreparationTest` 6PT、F/E/S0・Batch静的0・新classのbranch/line/method/class missed0。固定run/cutoff・手書き2step handleとevent列により、両DB begin commit→同run request新規公開→後続、resume元identity、commit不明/不正handle/公開失敗時の非成功、null/時計境界を確認。開発中の最初の`spotless:check`失敗は新2fileの整形不足で、整形後に成功した選択試験だけを合格算入する。

Batch限定triggerを456に事前記録し、同sourceで`clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`を実行。**703PT/84suite** F/E/S0、SpotBugs BugInstance0、Maven exit0。原始logはGit外`/tmp/pgpt-pg347-batch.log`、SHA-256 `2382fc53d13af0c84d29b62d6fac3c4a463d800dab547d7f8a2d751fa2df0f23`。sanitized JUnit84＋coverage2＋static1＝87fileを`evidence/provisional/PG347-backup-request/`へ保存、manifest SHA-256 `061ceaee023296db8db1aabebfb91901350c30c5018f0497807ebdce130cd83e`。全manifest path/hash一致、秘密pattern0。JUnit properties/stdout/stderr/失敗payloadは保存しない。

Batch全体4指標coverage missed（branch/line/method/class）は`13/202/82/10`で100%未達。新`MorningBackupPreparation`のみ`0/0/0/0`。今回はBatch内部追加でありProduction6・全scope正式認定を実施していない。全体正式source`858713c0bf310ae8bf62078b0a1cedbce4e968db`/run`PT-WEB-20260925-24`/1964PT/53scope、加重中心48.3%は不変。

新規BUGなし。関連BUG-315/YKT-248のhandleなしUNKNOWNとhard timeout後保全、YKT-250の原本complete/GC、SSC-055/092/094/104/105は継続。新classは内部順序境界であり、native親caller、固定request directoryの実開閉、backup Unit起動/全終端、実dump/manifest/DB成功、Cleanup/permit、外部Web/API、実NK CHR-A01/L01を実装・受入済みとはしない。PG/PT・IT/ST完了を宣言しない。
