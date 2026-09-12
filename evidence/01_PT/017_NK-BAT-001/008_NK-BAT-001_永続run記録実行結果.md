# NK-BAT-001 永続run記録の実行結果

PG-D-156/007/PT-BAT-038～045。実装・探索成功、正式全体試験待ち。正式20260912-06には含めない。source/全体run/関連証跡hashは正式実行後に追記する。原本file store・active lifecycle・親/GCとR001全体は未完了。

2026-09-12 23:45:54 JST、`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am verify` 終了0。Storage58+Batch115＝173 PT、line/method/class/branch100%、NullAway/Enforcer/Spotless/SpotBugs成功。OS既存toolchainは421のまま、新規導入なし。`/tmp/pgpt-run-record-explore2.log` SHA256 d6522a084b99c166f7e2ede0f9827de7844f1a84e9560e1ec9dbaef037754324。4実byte trace出力、017の1＋019の18＝19負canary成功。新規BUGなし。

初回探索23:38:26 JSTも173 PT/全gate成功（raw SHA f3526b90ff7e45f912b5fa403b8ba94f28094a17db55cf0e4fb1bbaaaa6a47c4）。追加した実byte trace・collectorの検証後に再実行した上記探索を正式実行準備の基準とし、未認定のまま全体件数へ足さない。
