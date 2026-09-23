# Log検索HTTP実行結果

2026-09-23 JST。Program NK-WEB-002 / PG218 / PT-SCR-093～103。ここに記すのは正式run前の選択試験であり、PT-SCR-104（実NK CHR-L01）は未実行、Log一画面全体は未受入。正式runのsource commit・全module coverage・静的解析・全scopeは後続manifestでのみ認定する。

対象は `dev-foundation` の `0080c879` に上記Log controller/config/testを加えた未commit作業tree。Linux、JDK25.0.4、Maven3.9.12、公開synthetic fixture、隔離したPostgreSQL/loopback HTTPを使用。command:

```text
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am -Dtest=FieldCodecTest,ResourceScopeTest,LogControllerTest test
```

2026-09-23 20:19:46 JST、exit0。Protocol5・Storage8・Log controller11、計24件、failure/error/skipped各0。Logの独立期待値は仕様023のUI232/235手組byte・HTTP status/DOM値。実際値は各JUnit assertionとSurefire XMLで照合。raw logはGit非格納の `/tmp/pgpt-pmo-20260923-log-http-selected-2.log`、SHA-256 `a959c5b0ab5082d03fb1b1cf4bd05f3d84621a5af8c6158d06a7fb2a644c086d`。初回選択試験はPT fixtureの重複query生成の引数不足で1 errorとなり、fixtureのみ訂正して再実行した。障害表のProduction仕様違反ではない。Java4 coverage/NullAway/SpotBugs/全回帰・実NK CHRは本選択試験で未認定。関連新BUGなし、SSC-073既存Log入力境界を維持。credential、session ID、token、raw電文は保存しない。

20:30:24終了の初回全run `PT-WEB-20260923-01`/source `69479c71` はexit1。Web全472PTはfailed/error/skipped0だったが、`LogController`の3行が未実行となりJacoco line gateで失敗、Batch未実行。raw log SHA-256 `7e3f433c1dd7cf8d71c466168e46bb8042709ecb8b7605230167cc2ae34a1dd7`。失敗runを合格に算入しない。UI232のbyte-validだが要求pageと異なる応答という独立view-binding反例をPT-SCR-097へ加え、20:31:54終了の選択24件はexit0、raw log SHA-256 `370742a58451eda2f74282dd82f32a865162d7f2c60ed2b47aaa502014f99700`。局所Jacoco再生成でWeb classのmissed0、Spotless check exit0。ただし正式な全reactor/Java4coverage/静的解析/全scope/実NK CHRは新sourceの次runまで未認定。

正式再試験 `PT-WEB-20260923-02`、source `7b09c09007bbf2d651fdaa65b0d60c7fa964c9c4`、`dev-foundation`、2026-09-23 20:33:53～20:46:37 JST、exit0。Linux/JDK25.0.4/Maven3.9.12/Node24.19.0。commandは`tools/quality/030_run_pgpt_verify.sh PT-WEB-20260923-02`（内部で同一toolchainのoffline `clean verify`）。全1731件=CHR41/Protocol80/Storage82/API689/Web472/Batch367、failed/error/skipped0、全Java coverage gateとProduction静的解析が通過。対象Log controller11＋Browser JUnit1はWeb472の内数であり重複加算しない。JS line/function/branch100%はLog JUnit1のNode subcase8で検査。raw logはGit非格納 `/tmp/PT-WEB-20260923-02.log`、SHA-256 `60d9162ed131587fc859904e67df278b4054cc9668475674f83dc8aa3c7a1058`。正式41scope/manifest/hash/canaryと実NK CHR-L01は、この時点では別確認待ち。全画面・PGPT・IT/ST完了を意味しない。

同一sourceの018 collectorによる全41scope・全file SHA-256検証はPASS、保存manifestの`--validate-only`もPASS。019負canaryは81件PASS。root manifest SHA-256 `b8d0a6b2ba00379c8d09147c6ad6d2fed0ec416f6df9255da7ad9112ab71ef58`。6 Java moduleのline/method/class/branch missedは全0、Production5のSpotBugs違反0。LogControllerは45line/3method/1class/10branchのmissed0、Log JS8 subcase/line・function・branch各100%。016証跡はPT-SCR001～103の103 JUnitを収録し、104の実NK CHR-L01は未実行として含めない。raw session/cookie/token/DB dumpは格納しない。
