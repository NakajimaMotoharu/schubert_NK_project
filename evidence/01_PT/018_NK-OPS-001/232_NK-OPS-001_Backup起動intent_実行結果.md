# 232 NK-OPS-001 Backup起動intent PT結果（PG355）

状態: 同boot intent file・次回Morning M admission・起動client呼出前保存の限定PT/本番6モジュール回帰は完了。真正root Morning/Backup Unitの外部起動と親hard-timeout後条件、全coverage100%、R2/R3は未認定。

2026-09-28 JST、branch `dev-foundation`、source/test/SS/spec commit `4005d6704fac645267aedcce53c2a413f9eae95a`。関連RD/UI/SS、独立期待・Test ID、fixture/未実測範囲は[231](231_NK-OPS-001_Backup起動intent_単体テスト仕様書.md)を参照。SSC-106を実装前起票、BUG-315/YKT-248/SSC-105は全親の未知状態保全が残るため対応中。

Host Linux 7.0.0-34-generic、JDK25.0.4、Maven3.9.12、JaCoCo0.8.15、SpotBugs4.10.4.0、NullAway0.14.1。まず`-Dtest=BackupStartIntentFilesTest,BackupUnitStartClientTest,MorningControlScopeTest test spotbugs:check jacoco:report`を実行し、29PT/3suite F/E/S0、SpotBugs0。初回静的解析では新classの公開monitor上の`synchronized`3件を検出し、私有lockへ修正して再実行した。初回解析は不合格で合格算入しない。限定JaCoCoは既存execと混在したため全coverageの証拠に用いない。

Security/排他変更のため、456に事前triggerを記録してsource固定のProduction6 clean回帰を実施。commandは `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 PATH=<JDK25/Node24/bin優先> ./mvnw -o -q -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.repository=/home/mini/codex/project1/work/pgpt-foundation -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api,src/schubert-nk-web,src/schubert-nk-batch clean test spotbugs:check jacoco:report`。終了コード0、2,440PT/357suite、failed/error/skipped0、6module SpotBugs0・Java NullAway compile成功。Module別PT/suiteはProtocol80/17、Storage149/21、Bootstrap175/22、API744/123、Web555/85、Batch737/89。

JaCoCo XMLのmissed branch/line/method/classはProtocol0/0/0/0、Storage0/0/0/0、Bootstrap37/11/4/0、API1/19/3/0、Web1/19/3/0、Batch21/259/98/12。新`BackupStartIntentFiles`自体も6/16/4/0でnative fixed-rootなど未実測、`BackupUnitStartClient` outerは0/3/1/0でnative factory未実測。4指標100% gateは不合格のまま。Raw XMLはGitへ入れず、全357 JUnit XMLのpath順SHA256列のSHA256は`ccb2245f4e5135a7f5b1b2e60ebe54f9d98c20869aa3b91dfbb748cea77c8a42`、Batch JaCoCo XML SHA256は`42cc11cfc54a238772bb0445f69b66240342c694e86b1addabcf31350fafce4c`。sanitized結果は `evidence/provisional/PG355-backup-start-intent/output/selected-summary.md` と同directory `manifest.json`。

変更の外部効果はまだ安全拒否側だけ。実systemctl Backup start0回、markerの真正Unit root持続/retire・親UNKNOWN中M/A保持・再boot後確認は未実行。Existing PG323 Morning試験用override/Backup PG309計測用Unitを上書きしない。正式認定source `858713c0bf310ae8bf62078b0a1cedbce4e968db`、正式run `PT-WEB-20260925-24`/1964PT/53scope、全体中心48.3%は変更しない。
