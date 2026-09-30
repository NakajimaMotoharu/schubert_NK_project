# PG381 接続変更群の選択試験結果（暫定・工程未完了）

固定source `a3eb64c71ca6a09ecc7c414e14be15aa66a65c8d` の全6 runは09:59:40 JST/12:52min/exit1、2536PT中BUG336の1 failure、E/S0、Batch static/coverage/package未実行。他5module static0。失敗証跡 `evidence/provisional/PG381-failed-regression/manifest.json`、sanitized JUnit全6を保全した。成功へ算入しない。SSC111独立literalへ修正後、Cleanup/Expiry Unit4PT/static0/Build成功は10:02:01 JST/20.621sec、pg382-unit-oracle.log。nativeVM/正式coverageは別gate。

2026-09-30 09:44:41 JST、Linux UID1000/JDK25.0.4/Maven3.9.12、dev-foundation。対象は272/274、SSC108～112。同じsource変更群のBootstrap16＋Batch136、合計152PT、F/E/S0、SpotBugs両module0、終了code0。ログはGit外 `/home/mini/codex/project1/work/pgpt-runs/PG379/pg381-resume-wiring-1.log`。固定source後の全6 regression/evidence manifestでcommit/hashとcoverageを確定する。選択coverageを正式100%へ算入しない。

command: fixed JAVA_HOME/Node PATH/m2; `./mvnw -o -pl src/schubert-nk-bootstrap,src/schubert-nk-batch spotless:apply clean test spotbugs:check jacoco:report -Dtest=<ログ記録の17 class>`。NullAway compile成功、class mismatch warningなし。

先行失敗は保存：expiry-wiring-4（97中1 error、BUG334 fixture残存child）、-5（97中1 error、BUG335旧256byte上限）、-6（97成功/static0）。readback初回BUG329、native-artifact-2 BUG331、-3 BUG332、expiry-wiring-2 BUG333も別ログ保持。BUG330の全native入力close/再承認順は実VM未実行で対応中。YKTは全対象/独立試験・native証拠が揃うまで未完了。実外部Morning/Backup、失敗継続、全8Unit、Expiry purge、issuer/APIWeb/CHRは未受入。
