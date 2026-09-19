# NK-WEB-001 Scenario通信実行結果

PG118継続/PG191、仕様は001§14.14・PT-WEB-166～173。選択8PT成功、正式全回帰前。6layout交換部品のみで、controller/画面/実Artemis/本番起動・実NK CHR完了ではない。

2026-09-20 04:09:47 JST終了、31.059秒/exit0。依存FieldCodecTest/ResourceScopeTestとScenarioWireClientTest8件成功。新4class/15method/88line/26branch全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。選択runの旧coverage execを正式全体結果へ流用しない。raw log `/tmp/pgpt-pg191-green.log` SHA256=`53b5761da2a6b7479f457bb8522ddd76b4f9c3bff5b8a0481bcdc3866df7ce9e`。

command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,ScenarioWireClientTest`。source d3ca485c＋原本3file copy/dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15、tool追加なし。

原本dev-webを変更せずcopyし、整形・選択試験後も両側3hash一致を確認:

| file | SHA256 |
|---|---|
| ScenarioWireClient.java | a934460aa70f506aeb1eea85e421e7b772bf4690e9cc87c4149d6d80308956a6 |
| ScenarioWireException.java | 35a99fc0ecbe45cca467835349e03a28495aa558fb3103a26cce74208b7f3321 |
| ScenarioWireClientTest.java | 9fc6b4012cd0e41a158c668c0ffc29c7073cb4376f9435d7b02d5460f700a405 |

UI234の独立offset byte vectorによる要求全byte/正常0・1・最大件数/0000・0200/SCN I・F/error空profile/不正header・data・record/NULL・clock・UUID・transport/容量・timeout・割込/100並行/byte消去を成功。合成sender＋実既存correlation registryであり、実brokerへの接続証跡ではない。SCF要求値やSCN target、file実体の業務結合は後続facade責務としてPG118に維持。新障害は検出なし。

collector015へ166～173の正確なmethod mapping、3source hash、001/003のコピーを追加し、019独立inventoryの欠落/未知method/余分ID拒否を追加した。正式source/時刻/OS・tool/command/exit/input期待/実際/coverage/hashは成功後evidence/manifest.jsonへ固定する。未完了フローは合格へ算入しない。
