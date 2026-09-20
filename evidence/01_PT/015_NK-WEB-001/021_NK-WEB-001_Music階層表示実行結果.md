# Music階層表示実行結果

PG208/PT-WEB246～253、仕様020。選択試験合格・正式全体回帰は未実行。全体合格件数へはまだ加算しない。

2026-09-20 09:03:59 JST終了、40.835秒、exit0。新8PT/依存PTすべて成功、failed/error/skipped0。MusicCategoryViewModel/MusicSectionViewModelとnested Cardの4class25method76line28branchは全missed0、除外なし。NullAway/Spotless/SpotBugs未解決0。独立期待値は020のliteral件数・URL・順序・閉じたproperty集合で、正常/境界/不正/null/不変性/64並行を確認。新規BUG/SSCなし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,MusicHierarchyViewModelTest
```

source eef1da18＋PG208作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12。raw log `/tmp/pgpt-pg208-green.log` SHA256=5a6427e29de67ae9351477d3e082828c9de9b0372b917769310a2e8ed8edcaf0。015collectorに8ID/3source/020021、019の独立inventory負canary追加、72件合格（017の1件と合わせ正式時73）。正式manifestへ対象commit/環境/実行日時/command/coverage/hashを保存予定。HTTP/音楽配信/実NKgate・PGPT/IT/ST未完了。
