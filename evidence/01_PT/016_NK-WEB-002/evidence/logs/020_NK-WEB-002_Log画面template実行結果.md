# Log画面template実行結果

正式認定: PT-WEB-20260920-27/source3b980d71f5573342b7c787ad6eed53db6d8c2940、10:14:36～10:27:24 JST/12:47/exit0。全1719PT/Web460、failed/error/skipped0、6Java4coverage100%/Production5静的解析未解決0、JS3coverage100%、41scope/81負canary成功。PG215/216計16PTを認定しBUG226/YKT182は全template/閉resolver再試験で完了。raw SHA256=03b144af204d27da27c388a4abfe933407787d29920e4d162510825b08edc4e6。evidence/manifest.jsonとsanitized suite/coverage/spec copyへ対象commit/環境/command/独立expected/actual/hashを固定。以下の未認定表現は選択試験時点の履歴。Browser入力検査/Log HTTP/実NKgate・PGPT/IT/ST未完了。

PG216/仕様019/SCR084～091。選択成功・正式未認定。実resolverによるLogs・共通nav/CSRF、7条件/option順、15field/optional、0/100/101/201/過大page、上下URI/空表示、escape/全error、CSS実配信・許可view境界、64並行を独立DOMで照合。template条件分岐をassertし、Java coverageと混同しない。

初回 /tmp/pgpt-pg216-selected.log は2026-09-20 10:11:48 JST/27.706秒/exit1、Web24中6failure/1error。閉resolverのlogs登録漏れ、SHA256=8badb77e195f37d60b1eaf014adc31fef4b0a6961ca16e8eb42f1f3b4b086f26。BUG226/YKT182をce5c486cへ修正前起票しlogsだけ明示追加。既存resolverは1箇所、既存画面は各template試験で解決確認済み。SCR090へ未知/fragment/相対/redirect/forward拒否の予防test追加。任意templateの許可やexpected緩和なし。

再試験は10:13:52 JST/43.416秒/exit0、Web24（新Log template8/Log状態8/Scenario template8）＋依存成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。raw /tmp/pgpt-pg216-green.log SHA256=45ccf16350d0792d82239cf11713107811895ebda761a69c8668444bdd117080。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,LogSearchTemplateTest,LogSearchViewModelTest,ScenarioSearchTemplateTest
```

sourcece5c486c＋PG216作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12。029へ8ID/4source/019020、CSS/WebMvcConfigurationは既存source inventoryに含む。019負canary80件成功（017と正式81予定）。正式manifestへ環境/対象commit/日時/command/exit/input/expected/actual/coverage/BUG/path/hashを保存予定。Browser byte事前検証/HTTP/実Browser/実NKgate・PGPT/IT/ST未完了。
