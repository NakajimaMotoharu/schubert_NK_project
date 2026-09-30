# PG381 接続変更群の選択試験結果（暫定・工程未完了）

2026-09-30 09:44:41 JST、Linux UID1000/JDK25.0.4/Maven3.9.12、dev-foundation。対象は272/274、SSC108～112。同じsource変更群のBootstrap16＋Batch136、合計152PT、F/E/S0、SpotBugs両module0、終了code0。ログはGit外 `/home/mini/codex/project1/work/pgpt-runs/PG379/pg381-resume-wiring-1.log`。固定source後の全6 regression/evidence manifestでcommit/hashとcoverageを確定する。選択coverageを正式100%へ算入しない。

command: fixed JAVA_HOME/Node PATH/m2; `./mvnw -o -pl src/schubert-nk-bootstrap,src/schubert-nk-batch spotless:apply clean test spotbugs:check jacoco:report -Dtest=<ログ記録の17 class>`。NullAway compile成功、class mismatch warningなし。

先行失敗は保存：expiry-wiring-4（97中1 error、BUG334 fixture残存child）、-5（97中1 error、BUG335旧256byte上限）、-6（97成功/static0）。readback初回BUG329、native-artifact-2 BUG331、-3 BUG332、expiry-wiring-2 BUG333も別ログ保持。BUG330の全native入力close/再承認順は実VM未実行で対応中。YKTは全対象/独立試験・native証拠が揃うまで未完了。実外部Morning/Backup、失敗継続、全8Unit、Expiry purge、issuer/APIWeb/CHRは未受入。
