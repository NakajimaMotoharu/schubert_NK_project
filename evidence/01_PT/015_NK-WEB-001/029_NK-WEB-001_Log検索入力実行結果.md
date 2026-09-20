# Log検索入力実行結果

PG214/SSC073/仕様028/WEB278～285。選択成功・正式未認定。新3class17method109line54branch全missed0。正常/byte境界/Unicode/未知・重複field/page/enum/厳密JST日時/31日境界/null/不変性/64並行を独立期待で照合。

初回 /tmp/pgpt-pg214-selected.log は09:46:33 JST/41.826秒/exit0だがline163の末尾surrogate判定1branch未網羅のため非認定。SHA256=f049343fb8c4cf3586625bb3b1341714c83f1c88e21d3ab6ccda8d43fa0745ec。BUG225/YKT181を7873af91へ修正前起票。空白で囲むfixtureが末尾条件を消していたため全8fieldへ末尾high surrogateを直接渡すnegativeを追加、拒否code/値破棄をassert。Production/期待値/除外不変更。Scenario WEB216はq/game/pageへ同末尾値を直接投入済みで非該当、既存回帰も実行。

選択再試験は2026-09-20 09:53:24 JST/34.393秒/exit0、Web16（新8＋Scenario8）と依存PT成功、failed/error/skipped0。NullAway/Spotless/SpotBugs未解決0。raw /tmp/pgpt-pg214-green.log SHA256=3a29c2e959fe31b2e59ff9709b591ba9bd4c53b98378b2c236d032cf9e58bca0。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,LogSearchFormTest,ScenarioSearchFormTest
```

source7873af91＋PG214作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12。015collectorへ8ID/2source/028029、019独立inventory追加で78負canary成功（017と正式79予定）。正式manifestへ環境/対象commit/日時/command/exit/input/expected/actual/coverage/BUG/SSC/path/hashを保存予定。Controller/template/HTTP/実NKgate・PGPT/IT/ST未完了。
