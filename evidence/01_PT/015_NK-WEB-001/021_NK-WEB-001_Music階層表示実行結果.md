# Music階層表示実行結果

正式24/source5f2abbf26f67c19a4d60a0778057360313366759、2026-09-20 09:06:27～09:19:08 JST/Maven12:39/exit0で認定。全1659PT/Web400、failed/error/skipped0、6Java全line/method/class/branch100%・Production5静的解析未解決0、JS3coverage100%、41scope/74負canary成功。raw log SHA256=efe1bf7eb10e042397b389c60147c87c3b9cd81fea2a8579beedec0dea963abc。新BUG/SSCなし。環境/command/対象commit/coverage/hashはmanifestへ保存。PG208の8PTを限定認定。4class25method76line28branch全missed0。PGPT/IT/ST未完了。以下は選択試験履歴。

PG208/PT-WEB246～253、仕様020。選択試験合格・正式全体回帰は未実行。全体合格件数へはまだ加算しない。

2026-09-20 09:03:59 JST終了、40.835秒、exit0。新8PT/依存PTすべて成功、failed/error/skipped0。MusicCategoryViewModel/MusicSectionViewModelとnested Cardの4class25method76line28branchは全missed0、除外なし。NullAway/Spotless/SpotBugs未解決0。独立期待値は020のliteral件数・URL・順序・閉じたproperty集合で、正常/境界/不正/null/不変性/64並行を確認。新規BUG/SSCなし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.node=/home/mini/codex/project1/work/toolchain/node-v24.19.0/bin/node --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,MusicHierarchyViewModelTest
```

source eef1da18＋PG208作業tree/dev-foundation、Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12。raw log `/tmp/pgpt-pg208-green.log` SHA256=5a6427e29de67ae9351477d3e082828c9de9b0372b917769310a2e8ed8edcaf0。015collectorに8ID/3source/020021、019の独立inventory負canary追加、72件合格（017の1件と合わせ正式時73）。正式manifestへ対象commit/環境/実行日時/command/coverage/hashを保存予定。HTTP/音楽配信/実NKgate・PGPT/IT/ST未完了。
## PG43368 現候補の音楽階層の選択試験

UI235 §§7–8、SCR011／012、PT-WEB-246～253。現在のfixtureとProtocol正規JAR、現SDKで8/8成功。対象はMusicCategoryViewModelとMusicSectionViewModelおよび各Cardの4物理。単一execを独立CRCと照合し、行76/76、method 25/25、class 4/4、branch 28/28。初回は局所コンパイルの引数にSpring Webが欠け、PTは未起動。再試験は固定済み依存を明示した。旧別実行の結果は合算しない。実ブラウザ・HTTP・配信、正式Web JARと全451は別の受入条件。[PG43368](../018_NK-OPS-001/evidence/PG43368-current-music-hierarchy-eight-v2/manifest.json)
