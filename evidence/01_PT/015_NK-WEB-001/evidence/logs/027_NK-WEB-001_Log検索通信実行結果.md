# Log検索通信実行結果

正式認定: PT-WEB-20260920-26/source7df9eb2efbe929bf1fb498cf911f35d571285c5f、09:54:21～10:07:03 JST/12:41/exit0。全1703PT/Web444、failed/error/skipped0、6Java4coverage100%/Production5静的解析未解決0、JS3coverage100%、41scope/79負canary成功。PG212～214の24PTを限定認定。BUG224/225・YKT180/181は全view/form含む正式再試験で完了、SSC073は入力境界だけ完了。raw SHA256=17a28095849c08e51bd37c4050f32ec6f164a44903bd17638bac1fdb79c97715。evidence/manifest.jsonとsanitized suite/coverage/spec copyが対象commit/環境/独立expected/actual/hashを一意に追跡する。以下の未認定表現は選択試験時点の履歴。Log template/HTTP/NKgate・PGPT/IT/ST未完了。

PG213/仕様026/WEB270～277。選択成功・正式未認定。新1class2method5line全missed0、条件分岐0で除外なし。全type/level・656/48/2088独立byte、0/1/100/31日、page/date不正、全error/0103、malformed/null/transport/未知例外同一性/64相関・所有消去は全assert成功。初回runでも新通信8PTは成功したが同runにBUG224があり全体合格には算入しない。BUG224再試験に同時参加。

選択再試験は2026-09-20 09:44:59 JST/35.804秒/exit0。Web48（Log表示8/Log通信8/Page8/Music8/Animation8/Scenario8）＋依存PT成功、failed/error/skipped0。NullAway/Spotless/SpotBugs未解決0。raw /tmp/pgpt-pg212213-green.log SHA256=78fe27ba85971af4c0fefd1e45dc0866b411afd5a2b0f024f3f4ea50c42d8ec1。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,LogSearchResultsViewModelTest,LogSearchWireClientTest,PageViewModelTest,MusicWireClientTest,AnimationWireClientTest,ScenarioWireClientTest
```

sourcec784bf10＋PG212/213作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12。015collectorに各8ID/計4source/024～027、019独立inventory追加で77負canary成功、017と正式78予定。正式manifestへ環境/対象commit/日時/command/exit/input/expected/actual/coverage/関連BUG/SSC/path/hashを保存予定。form/template/HTTP/実broker/実NKgate・PGPT/IT/ST未完了。
