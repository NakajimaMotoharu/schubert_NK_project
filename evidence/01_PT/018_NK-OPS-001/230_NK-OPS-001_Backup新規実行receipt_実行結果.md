# 230 NK-OPS-001 Backup新規実行receipt PT結果（PG353）

状態: `BackupUnitReceiptGate`限定PT完了。実worker起動/親M+A/backup現物・正式R2/R3は未認定。

2026-09-28 JST、branch`dev-foundation`、source/test/spec commit`3578716cba2af02543c212f7174d3d2bc01e91ed`。関連正本とBGATE001～008の独立期待値は[229](229_NK-OPS-001_Backup新規実行receipt_単体テスト仕様書.md)を参照。実`systemctl start`、VM Unit変更、credential/request/原本変更は0回。

限定command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -q -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.repository=/home/mini/codex/project1/work/pgpt-foundation -pl src/schubert-nk-batch -Dtest=BackupUnitReceiptGateTest spotless:apply test spotbugs:check jacoco:report`。Host Linux 7.0.0-34-generic/JDK25.0.4/Maven3.9.12、exit0、8PT/1suite F/E/S0、SpotBugs0。初回GREEN前のfixtureに`List.of(...,null)`を使用したためBGATE006がfixture内NPE/1error。修正後の上記runのみPASSとし、Production挙動のNPE成功には算入しない。

新outer `BackupUnitReceiptGate`のJaCoCo B/L/M/C missed0/0/0/0、nested `Baseline`のL/M/C missed0/0/0。interfaceはcounterなし。Batch全体のB/L/M/C missed15/235/92/12で100%不可。JaCoCo XML SHA-256 `265cbf923b60825a168074d5c1cf2e2ea7ede83581849facf2d826da723969db`。raw JUnit XMLはGitへ含めずSHA-256 `704d722ac818a76e5c9f2f0d630590812fea4209bd1a04ea2ea7f46d53969453`、sanitized結果は`evidence/provisional/PG353-backup-receipt/output/selected-summary.md`へ保存。

前後Unit状態・kernel全process・再読の同一性は限定fixtureで確認したが、親M/A内の実poll/30分budget/出力archive/明示stop/retireは未結線。BUG-315/YKT-248/SSC-105のhandleなしUNKNOWN・hard-timeoutも未閉鎖。限定class変更なので451の全6正式run triggerではなく、R/D固定IDと正式source/run・中心48.3%は据置。sanitized manifest SHA-256 `38e25e9774d1342c12700d2cc7ef807d76918740c4fc3e10f7ee9b0b7ad7d301`、file hash照合済み、秘密pattern0。
