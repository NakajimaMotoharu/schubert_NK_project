# Scenario検索画面状態実行結果

PG200/PT-WEB222～229、仕様014。選択8PT成功、正式全reactor未実行。正式1580PT/82部分成果へ未加算。検索template/controller/実NKgate・PGPT/IT/ST完成ではない。

選択 `/tmp/pgpt-pg200-green.log`、2026-09-20 06:46:31 JST終了、32.791秒、exit0。SHA256 `4a177fd3d4e4f188b2333299f5df91462e35ba5ff386211651cf4426e6964e51`。新8＋検索入力8/結果8＋依存選択成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。新3class/33method/86line/16branch全missed0。Filtersのbranch0/0は除外なし。新規障害なし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,ScenarioSearchViewModelTest,ScenarioSearchFormTest,ScenarioSearchResultsViewModelTest
```

source5d8472f7＋PG200作業tree/dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15。新toolなし。入力/独立期待は014/public synthetic fixture、実際値は表示scalar/候補順/URL literal/例外/合成DOM/並行assertで確認。固定6条件URLとUTF8 percent vector、page補正と要求応答binding、candidate10/500上限、全field/error、null/不変/閉bean/redaction、64並行を検証。collector015で8Test ID/2source hash/014・015、019独立inventoryで欠落/余分/未知method拒否。正式command/commit/時刻/exit/環境/coverage/hashは次回manifestへ固定する。
