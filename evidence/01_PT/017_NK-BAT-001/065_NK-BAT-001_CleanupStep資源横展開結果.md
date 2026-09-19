# NK-BAT-001 CleanupStepRepository資源横展開結果

選択再試験成功: `/tmp/pgpt-pg181-green2.log`、2026-09-20 01:14:22 JST/34.326秒/exit0。Storage8＋Repository8＋Service8＝24 PT、BAT168内68複合と元2反例、failed/error/skipped0。CleanupStepRepository1class/5method/68line/28branch全missed0、NullAway/Enforcer/Spotless/SpotBugs成功。borrowed接続不変/全取得済close/未取得0/live0、admin独立質問count・caller rollback後step countsを確認。BUG207/YKT163の新2読取位置を修正、既存後条件はadminで非該当、16関連PT回帰成功。全reactor前のため障害/横展開完了は保留。SHA256=`1f8fc8551c3a2d6330803fb14e1ddf3fe928ba72f1aed2f50bc222fb7c63a452`。

PG181/SSC063/BUG195・206・207/YKT154・162・163、064・BAT168。正式認定前、新JUnit/部品加算0。

反例: `/tmp/pgpt-pg181-red2.log`、2026-09-20 01:11:17 JST/10.670秒/exit1。Storage8成功、BAT168 1FAIL（assertAll内2反例）。cleanup getterのprovider IAEと同一IllegalState body/closeが共にBatchRepositoryExceptionへ置換された。Productionは未修正のd81f06f1、fixture/testのみ追加。SHA256=`5be800bd4c4d1ca4bc20d731483251ed92f2c2cbe01a662138a2b82ce57c1a0b`。

初回修正: `/tmp/pgpt-pg181-green.log`、01:12:54 JST/29.909秒/exit1。関連24 PT中1error。新68複合の前提oracleが最小権限batchでquestionsを直接SELECTし42501となった（BUG207/YKT163）。検証用adminへ読取だけを移し、本番grant・正常期待を変更しない。SHA256=`51ddac20a5fafaedf4ecc5452ef962d7b367bb6d1ed31627025d0922e93dccb3`。これは68複合合格ではない。

初回準備: `/tmp/pgpt-pg181-red.log`、01:10:28 JST/3.125秒/exit1はformat check停止で対象PT未実行。formatter適用後に上記red2を実行した。SHA256=`399330aef175b10a554b7aa71fb4344429632aa6f3dd93a5c42d99dd391e825e`。

実行環境: Ubuntu26.04.1 amd64、JDK25.0.4/Maven3.9.12、PG18.6/JDBC42.7.13、dev-foundation。公開合成fixtureのみ。commandは `JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 ./mvnw -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository --no-transfer-progress -pl src/schubert-nk-batch -am -Dtest=ResourceScopeTest,CleanupStepRepositoryTest,StepCleanupServiceTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。反例はtest goalのみ、CleanupStepRepositoryTest#interruptRuntimeAndResourceOwnershipへ限定（StepCleanupServiceTestなし）。

再試験とcoverage/staticは確認後追記する。正式full-reactor/source固定・38scope/46負canary未実施、BUG195/206/SSC063の残Repositoryは未完了。
