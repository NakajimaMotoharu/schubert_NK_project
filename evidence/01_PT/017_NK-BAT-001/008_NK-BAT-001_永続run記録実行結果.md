# NK-BAT-001 永続run記録の実行結果

PG-D-156/007/PT-BAT-038～045: 正式PT-WEB-20260912-07/source e919ac03a008355dbc6afa51c8c94c51845a01b2、dev-foundation、2026-09-12 23:51:38～23:59:15 JST、終了0で8件を認定。全1169 PT、failed/error/skipped0、6 Java moduleのline/method/class/branch100%、5 Production静的解析未解決0（固定path2 method限定reviewは維持）。12collector/35scope/19負canary成功。実行commandは `sh /home/mini/codex/project1/work/pgpt_foundation_verify.sh PT-WEB-20260912-07`、環境は421。evidence/manifest.jsonのhash de2e8de88dc55228d73b0a86303234a600a5e8fee16f9735936e7ecaa32a6324、4独立literal inputと4実output・XML・coverageをmanifestで追跡。関連SSC055、BUGなし。原本file store・active lifecycle・親/GCとR001全体は未完了、実NK CHR/IT/STを認定しない。

2026-09-12 23:45:54 JST、`JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am verify` 終了0。Storage58+Batch115＝173 PT、line/method/class/branch100%、NullAway/Enforcer/Spotless/SpotBugs成功。OS既存toolchainは421のまま、新規導入なし。`/tmp/pgpt-run-record-explore2.log` SHA256 d6522a084b99c166f7e2ede0f9827de7844f1a84e9560e1ec9dbaef037754324。4実byte trace出力、017の1＋019の18＝19負canary成功。新規BUGなし。

初回探索23:38:26 JSTも173 PT/全gate成功（raw SHA f3526b90ff7e45f912b5fa403b8ba94f28094a17db55cf0e4fb1bbaaaa6a47c4）。追加した実byte trace・collectorの検証後に再実行した上記探索を正式実行準備の基準とし、未認定のまま全体件数へ足さない。
