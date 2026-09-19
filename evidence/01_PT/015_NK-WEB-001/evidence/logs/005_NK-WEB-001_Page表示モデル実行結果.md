# NK-WEB-001 Page表示モデル実行結果

正式認定: PT-WEB-20260920-10/source34a8f9a903f309e2efe68767bc2c24d4d44520e8、04:31:01～04:42:43 JST/Maven11:41/exit0。全1516PT（Web257、うち本Program181）成功、failed/error/skipped0、6Java4coverage100%/Production5静的解析未解決0。40scope/57負canary成功。本対象8PT・1class13method33line28branch全missed0を限定認定。Production画面/HTTP/実NKgate/PGPT/IT/ST完了ではない。raw log SHA256=763ce326ea9ea6a32c0b734e142d5f856cc7d9e786a5c4d5423c82e66968f058。正式command/tool/source/hashはmanifestへ固定。以下は選択試験履歴。

PG192/PT-WEB-174～181、仕様004。2026-09-20 04:29:51 JST終了、選択試験8件成功、Maven33.212秒/exit0。1class/13method/33line/28branch全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。正式全回帰前のため全体件数・部分成果数への加算は保留する。

command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,ScenarioWireClientTest,PageViewModelTest`。source83227e53＋PG192変更/dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15、tool追加なし。

raw log `/tmp/pgpt-pg192-green.log` SHA256=01aa702c95670b842e7717e999b4884f952af8c3aa36c9d01526e72d56f4cd8a。入力・期待値は004とtestの独立literal。正常/境界/異常/null/100並行/JavaBean/合成Thymeleaf DOMを成功。業務URL・Production画面・HTTPへの結線は未検証。失敗/skipなし、新障害なし、SS範囲内の内部型付けでSSC不要。正式実行時のtarget commit/環境/command/時刻/exit/全coverage/証跡hashはmanifestへ記録する。

collector015が174～181のmethodを厳密対応させ004/005/source hashを収集。019独立canaryは欠落・未知method・余分IDを拒否する。未実装範囲のcoverage分母外を工程完成とみなさない。
