# Log検索結果表示実行結果

正式認定: PT-WEB-20260920-26/source7df9eb2efbe929bf1fb498cf911f35d571285c5f、09:54:21～10:07:03 JST/12:41/exit0。全1703PT/Web444、failed/error/skipped0、6Java4coverage100%/Production5静的解析未解決0、JS3coverage100%、41scope/79負canary成功。PG212～214の24PTを限定認定。BUG224/225・YKT180/181は全view/form含む正式再試験で完了、SSC073は入力境界だけ完了。raw SHA256=17a28095849c08e51bd37c4050f32ec6f164a44903bd17638bac1fdb79c97715。evidence/manifest.jsonとsanitized suite/coverage/spec copyが対象commit/環境/独立expected/actual/hashを一意に追跡する。以下の未認定表現は選択試験時点の履歴。Log template/HTTP/NKgate・PGPT/IT/ST未完了。

PG212/仕様024/WEB262～269。選択成功・正式未認定。新2class25method61line18branch全missed0。全field/UTC日時literal/1024 optional組合せ/page・順序・ID/null・ADMIN・不変性・closed bean・合成HTML・64並行は全assert成功。

初回 /tmp/pgpt-pg212213-selected.log は09:43:18/32.435秒/exit1、Web48中1error（WEB268のplain TemplateEngineでOGNLなし）、SHA256=79e2d30654b2ec174febc0e91175858d2058122722506265f92cdd948f95efac。BUG224/YKT180をc784bf10へ修正前起票。全Web view engine検索では新1箇所だけplain、既存7合成HTMLはSpring・その他実resolver。SpringTemplateEngineへ修正しOGNL追加/期待緩和なし。既存全view/実resolverを正式回帰するまで台帳未完了。

選択再試験は2026-09-20 09:44:59 JST/35.804秒/exit0。Web48（Log表示8/Log通信8/Page8/Music8/Animation8/Scenario8）＋依存PT成功、failed/error/skipped0。NullAway/Spotless/SpotBugs未解決0。raw /tmp/pgpt-pg212213-green.log SHA256=78fe27ba85971af4c0fefd1e45dc0866b411afd5a2b0f024f3f4ea50c42d8ec1。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,LogSearchResultsViewModelTest,LogSearchWireClientTest,PageViewModelTest,MusicWireClientTest,AnimationWireClientTest,ScenarioWireClientTest
```

sourcec784bf10＋PG212/213作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12。015collectorに各8ID/計4source/024～027、019独立inventory追加で77負canary成功、017と正式78予定。正式manifestへ環境/対象commit/日時/command/exit/input/expected/actual/coverage/関連BUG/SSC/path/hashを保存予定。form/template/HTTP/実broker/実NKgate・PGPT/IT/ST未完了。

## 2026-11-22 現候補の局所再試験

PG42362／試験source c9b95413be15f435a4fbf50c70947d94df8655cb、Java Core 1e4e9e64830b552727043f3cb8b9435b28cba472。独立期待値のPT-WEB-262～269は8成功、失敗・エラー・skipped各0。投影本体とRowは行61、メソッド25、クラス2、分岐18が各100%。従属Page/TopBarも報告した範囲の未測定を保持。SpotBugsは指摘・欠落class・解析error各0、Checkstyleとformatはexit0。PMDの有限worker5指摘は保持し、全451の判定は保留。証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG42362-f03-log-result-fixture-current-v1/manifest.json SHA256 5f707ea329998b1e1b232c66d7802ce7201be1ad76f6a4e1267f93153971cc51。BUG-3578／YKT-2813。実HTTP・業務接続・全体認定は未実行。
