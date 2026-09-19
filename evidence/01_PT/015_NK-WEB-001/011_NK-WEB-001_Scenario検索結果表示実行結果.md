# Scenario検索結果表示実行結果

PG198/PT-WEB-206～213、仕様010。選択8PT成功、正式全reactorは未実行。正式1564PT/80部分成果へ未加算。検索form/controller/template/実NKgate・PGPT/IT/ST完成ではない。

選択 `/tmp/pgpt-pg198-green.log`、2026-09-20 06:11:04 JST終了、32.047秒、exit0。SHA256 `fee315c539ee6ae837b56a465b36fbccb83b43892012e643d4b3c9c03a4c227e`。新8PTとPage/本文モデル/依存選択が成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。新3class/26method/57line/12branch全missed0。Audioはbranch0/0で除外なし。新規障害なし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,ScenarioSearchResultsViewModelTest,PageViewModelTest,ScenarioDetailViewModelTest
```

source bec65458＋PG198作業tree/dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15。新toolなし。

入力と独立期待は010/public synthetic fixture。実際値はgetter、合成DOM、例外、並行結果のassertで検証。両game/role、literal表示ラベル、API順序、固定numeric URL、page0/100/最終/最大、件数不一致、audio全8組、null/immutable/closed bean/redaction、64並行投影を確認。collector015で8Test ID・source2hash・010/011を収集し、019で欠落/余分/未知methodを拒否。正式実行commit/時刻/終了code/環境/coverage/evidence hashは次回manifestで固定する。
