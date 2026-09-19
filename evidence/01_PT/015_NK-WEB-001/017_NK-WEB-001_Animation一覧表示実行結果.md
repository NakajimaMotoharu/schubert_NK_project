# Animationメニュー・一覧表示実行結果

PG204/PT-WEB230～237、仕様016。選択8PT初回成功、正式reactor未実行。正式1609PT/86部分成果へ未加算。表示modelだけでtemplate/HTTP/MQ/動画stream/実NKgate・PGPT/IT/ST完成ではない。PG205 templateと合わせて正式21へ進める。

`/tmp/pgpt-pg204-green.log`、2026-09-20 08:01:36 JST終了、35.968秒、exit0、SHA256 `b0c7fa2dddbb28d604ae0d0bb9298eb94eb51620fe57970aff3df55e74a8ba45`。新8PTと依存選択成功、failed/error/skipped0、NullAway/Spotless/SpotBugs未解決0。新4classのline/method/class/branch全missed0、除外なし。新規障害なし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,AnimationViewModelTest
```

source803e02ef＋PG204作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12、tool変更なし。入力/独立期待は016のmenu15/4/1/20、3main/2sub（sub先行も含む）、OVA0/4/50/51、各不整合/null・不変所有・閉bean・固定percent URL・HTML逃避・64並行。実際は全assert成功。015 collectorへ230～237/source3hash/016017を追加、019独立inventory含む68canary成功。017の1と計69は次正式gateで確認する。正式command/対象commit/時刻/環境/exit/coverage/source・証跡hashはmanifestへ記録する。
