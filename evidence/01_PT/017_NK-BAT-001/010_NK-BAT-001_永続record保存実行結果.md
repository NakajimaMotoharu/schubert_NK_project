# NK-BAT-001 永続record保存の実行結果

PG-D-157/009/PT-BAT-046～057。実装/関連探索成功、正式全体認定待ち。正式20260912-07/source e919ac03の1169件には含めない。実行後にsource/run/manifest hashを記録する。固定namespace/state graph/親/GCは未完了。

2026-09-13 00:24:40 JST、dev-foundation未commit source、Ubuntu26.04.1/JDK25.0.4/Maven3.9.12等421の既存環境。command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am verify`、終了0。Storage58+Batch127＝185 PT成功、failed/error/skipped0、両module line/method/class/branch100%、NullAway/Enforcer/Spotless/SpotBugs成功。raw /tmp/pgpt-durable-explore4.log SHA256 147a9e4e426c7eac2be8697e1c48915b905ed89209df1369b676d54092798cc6。実file4traceを出力、017の1＋019の19＝20負canary成功。BUG158/YKT123は正式再試験待ち。

探索1はcoverage4分岐未達で不合格（監査log参照）、探索2で境界修正後成功。探索3は実2instance no-replace競合/実symlink・hardlink/保全追加後00:22:26 JST成功、raw SHA256 98153a212e341b2c64be432d450e74b5324bace46ca91f24a7af862b643d3823。探索4は実file出力追加後の最終関連確認であり、全体正式試験を代替しない。
