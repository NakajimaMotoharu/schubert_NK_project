# Scenario検索入力実行結果

PG199/SSC072/PT-WEB214～221、仕様012。選択8PT成功、正式全reactor未実行。正式1572PT/81部分成果へ未加算。HTTP/template/MQ接続・実NKgate/PGPT/IT/ST完成ではない。

選択 `/tmp/pgpt-pg199-green.log`、2026-09-20 06:30:24 JST終了、34.336秒、exit0。SHA256 `454e6a97f93091a2a7ebe27560219edd3fc065fa4d6d05dbb7af9c7ca96ecc01`。新8＋検索結果8＋依存選択成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。新3class/19method/90line/42branch全missed0。2enumのbranch0/0は除外なし。新規障害なし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,ScenarioSearchFormTest,ScenarioSearchResultsViewModelTest
```

source391ba33a＋PG199作業tree/dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15。新toolなし。入力/独立期待は012のpublic synthetic fixture、実際値はtyped request全field/closed issue集合/例外/並行結果をassert。NFC後q/chapter256・speaker128 byte、control4種/不正surrogate、game/type/voice両値、7field allowlist/duplicate、負int/zero→1/999999/overflow/ASCII grammar、null/snapshot/redaction/64並行を確認。collector015で8Test ID/2source hash/012・013、019独立inventoryで欠落/余分/未知method拒否。正式command/commit/時刻/exit/環境/coverage/hashは次回manifestへ固定する。
