# Scenario本文表示モデル実行結果

正式認定: PT-WEB-20260920-14/source414d79c5d21ef00e4ada50aad85b9cd433bccfd8、05:55:40～06:07:26 JST/Maven11:44/exit0。全1564PT（Web305、本Program205）・6Java4coverage100%・Production5静的解析未解決0、41scope/62負canary成功。新12PT・4class36method99line30branch全missed0を認定。raw log SHA256=4e695d4c3a998cf6808fd8446d50831a7d7b655da1153d3db7ae64f174553c50。正式13は非合格のまま別履歴。command/環境/対象commit/source・evidence hashはmanifest。本文controller/file port/readiness/実NKgateは未完了。以下は選択・失敗履歴。

正式13は既存InspectorDeploymentTestのxtrace混線（BUG217/YKT173）でexit1となり、Web/Batch未実行。PG195は未認定のまま。詳細は018035、修正後の別clean verifyで全体を再試験する。正式13の失敗をretry成功へ書換えない。

PG195/PT-WEB-194～205、仕様008。選択12PT成功、正式全reactorは未実行。現在の正式1544PT/78部分成果へ加算しない。画面・large reader本番接続・実NK互換性gate・PGPT/IT/ST完成ではない。

選択 `/tmp/pgpt-pg195-green.log`、2026-09-20 05:39:44 JST終了、38.413秒、exit0。SHA256 `62efc72b638dcf0622c3e777672babf34f2426b44cea835713118b895ba5e4c1`。新12PTと階層HTTP16PT・依存選択が成功、failed/error/skipped0、NullAway/Enforcer/Spotless/SpotBugs未解決0。新4class/36method/99line/30branch全missed0。Navigation/Audioのbranch0/0は条件なしで、coverage除外ではない。新規障害なし。

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-web -am spotless:apply test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check -Dtest=FieldCodecTest,ResourceScopeTest,ScenarioDetailViewModelTest,ScenarioControllerTest
```

source74c282c1＋PG195作業tree/dev-foundation。Ubuntu26.04.1/Linux7.0.0-31/amd64/JDK25.0.4/Maven3.9.12/JUnit5.13.4/JaCoCo0.8.15。新tool導入なし。

入力・独立期待は008とpublic synthetic fixture。実際値はgetter/合成DOM/例外/並行結果をassertし、正常同entryの全audioと本文1回、同entry metadata不一致拒否、inline0/200・file1/10000・超過/不一致、null、前後pair、固定URL、immutable/閉getter/toStringを確認。Large-result descriptorを保持せず、検証済recordsの投影に限定する。collector015が12Test ID/2source hash/008・009と全coverageを収集、019独立inventoryは欠落/余分/未知methodを拒否。正式command/環境/commit/時刻/exit/coverage/hashは次回manifestへ固定する。

## PG43382 現候補の本文表示

PT-WEB-194～205の単一実行で12件成功。失敗、エラー、skippedは各0。本文とAudio/Entry/Navigationの生四指標は L100/M36/C4/B30で各100%。実ファイル・API・HTTP・実Browser・全451は別条件。公開manifest evidence/01_PT/018_NK-OPS-001/evidence/PG43382-scenario-detail-current-twelve-v1/manifest.json（SHA256 22c08f76dca5a8a12e9f8f33fdfcc47273ccbd8a5fbf04c4d25583cf4465720e）。
