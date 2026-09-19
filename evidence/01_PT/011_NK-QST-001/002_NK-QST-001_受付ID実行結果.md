# NK-QST-001 受付ID実行結果

PG188/RID001～008、選択8PT成功・正式全reactor前。低位ID部品だけ、質問受付/再送/worker完成ではない。

2026-09-20 03:10:49 JST終了、39.339秒/exit0、QuestionReceiptIdTest8＋PostgresDeploymentTest8と依存FieldCodecTest/ResourceScopeTest成功、failed/error/skipped0。新2class/6method/20line/8branch全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。古いexecを含む選択実行なのでAPI全coverage表示は正式認定へ流用しない。raw log `/tmp/pgpt-pg188-green.log` SHA256=`b4b95bbae29d563faaeaf7a02b0376244f1a61f47f80b960a663e4f666b8c0cf`。

command: `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-api -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,PostgresDeploymentTest,QuestionReceiptIdTest`。source4cf82f62＋当変更/dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15。tool新規導入なし。

全32許容文字、各26位置の全ASCII禁則とUnicode境界、固定正逆vector、全26provider例外位置、index4境界、null、SecureRandom factory、private lock64並行の独立16literal各4件・1664draws、等値/hash/toString REDACTEDを成功。生成値の確率的一意性を試験合格条件にせず、DB UK/再送は別責務。新障害なし。source/spec/入力期待実際と公開trace・coverage/hashは正式後evidence/manifest.jsonへ収集する。新8PT/1部分成果未加算。
