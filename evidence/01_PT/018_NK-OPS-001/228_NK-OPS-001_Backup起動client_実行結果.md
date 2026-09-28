# 228 NK-OPS-001 Backup起動client PT結果（PG352）

状態: `BackupUnitStartClient`限定PT完了、実Backup Unit起動/親M+A継続/worker受入は未達。

2026-09-28 JST、branch `dev-foundation`、source/test/spec commit `84763f857977508c9965ece2bb98ed28f1a146c1`。関連SS/目的/独立期待値とPT-OPS-BSTART001～008は[227](227_NK-OPS-001_Backup起動client_単体テスト仕様書.md)を参照。BUG-315/YKT-248/SSC-105のhandleなしUNKNOWN/hard-timeout保全は引き続き未解決。

限定command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -q -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.repository=/home/mini/codex/project1/work/pgpt-foundation -pl src/schubert-nk-batch -Dtest=BackupUnitStartClientTest test spotbugs:check jacoco:report`。Host Linux 7.0.0-34-generic、JDK25.0.4、Maven3.9.12、exit0、8PT/1suite、F/E/S0、SpotBugs0。最初のcompile試行は`NativeStart`を別SAM型に直接渡して型不一致/exit1でPT未実行。method referenceへ修正した後の上記実行だけがPASS。

JaCoCo XMLでは新outer `BackupUnitStartClient` B/L/M/C missed0/0/0/0、`Attempt`も0/0/0/0、`Status`のL/M/Cも0/0/0。3 interfaceには実行counterなし。対象新class以外のBatch全体はB/L/M/C missed15/235/92/12（PG351以前の蓄積execを含む）で、要求100%には未達。JaCoCo XML SHA-256 `e59e8fc4f1020c78aa0a5888ea4184e82be913657ead22173f035477c9241e5e`。JUnit raw XMLはGitへ含めずSHA-256 `bfa4563e33bdfe7cde886f199ea1920689e18e4f941d2b329326bb05a936c8dd`でローカル照合、sanitized結果は`evidence/provisional/PG352-backup-start/output/selected-summary.md`へ保存。

`systemctl start`実発行0回、Unit/worker/DB/原本/credentialは不変更。client exit0をworker成功にしないためR2/R3/D固定closed0、正式source/runと全体中心48.3%は据置。全6回帰は限定class追加のみで発火せず、親機能受入・PR/工程gate前に451規定で実施する。sanitized manifest SHA-256 `21bff9de65617a987c101b2135e2d123cc397b07849e7c80983dafc02a9f7c27`、file hash照合済み。秘密pattern0。
