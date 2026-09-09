# NK-OPS-001 Linux flock 実行結果

003/PT-OPS-FLOCK-001～008、SSC-049/PG-D-146。2026-09-09 19:37:04 JSTのStorage選択試験8件成功、19:43:39のStorage compile/SpotBugs成功・指摘0。探索logは`/tmp/pgpt-flock-explore-1.log`、`/tmp/pgpt-flock-spotbugs-1.log`（作業領域のみ、正式証跡ではない）。019 collector異常系14件成功。正式41の全体clean verifyと同一sourceの証跡収集はこれから実施し、正式40以前へ遡って算入しない。root lockfile配布/親OS停止/実backup/DB引渡しは別未完了。

再現command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-storage -Dtest=LinuxFileLockTest test`。正式runは全module `clean verify`。022のOPS scopeへ8件を追加し、API deployment8件とstorage排他8件を異なるTest IDで一意対応する。006のScenario選択から排他classを除き、全reactorのstorage合計・coverageには含める（019独立所属canary付き）。Native故障portのliteral errno/flagsと実OS競合結果をoracleとし、Production値からexpectedを生成しない。
