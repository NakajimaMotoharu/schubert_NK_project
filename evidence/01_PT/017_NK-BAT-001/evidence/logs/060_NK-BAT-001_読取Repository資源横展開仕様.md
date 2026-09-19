# NK-BAT-001 読取Repository資源横展開仕様

PG179/SSC063/BUG195・206/YKT154・162、2026-09-20。仕様先行。RD DAT009/OPS009、UI251、SS331§3.12～13/332/343。RunReferenceRepository.readとInspectionSummaryRepository.read、共通JdbcResourceFailuresの全methodを既存BAT087/121へ追跡。元の8件ずつ、計16PTと正常/NULL/歴史UTC/DBlock/borrowed connection/並行の独立oracleを維持する。

## 独立matrix

- 各readerのrow.next→row.close、statement.executeQuery→statement.close、計4境界。実PG18/JDBC proxyでclose後に故障を注入し、実resource live数と公開close回数を検証する。
- 0=SQLException、1=IllegalArgumentException、2=IllegalStateException、3=NPE、4=AssertionErrorの5×5異なる組合せ、同じ未知4組、body成功/closeのみ5組、各34・全136組。providerのIAEは未知、model不正値のIAEはProductionの狭い境界でSQL不正に変換する。最初にprovider IAE単独と同一unknown複合の反例を実行する。
- 独立期待表: primary未知なら元identityを保持し固定BatchRepositoryException secondary1件だけ。primarySQL＋secondary未知ならsecondary identity。SQL同士/SQL単独は固定message/causeなし/suppressed0。成功bodyの未知closeはその同一物。未取得rowはclose0、取得済row/statementは各1、live0、connection非close/commit/rollback/config変更0。
- null/欠落/重複/不整合boolean・負countsの元期待は不変。未知IAEを不正データ成功や空Optionalへ変換しない。Thread割込を保持し、各callerの元transaction契約を守る。

Test IDはBAT087 RunReferenceRepositoryTest.interruptionAndRuntime、BAT121 InspectionSummaryRepositoryTest.interruptAndRuntime。Productionのprivate methodをreflectionで呼ばず公開read/JDBCだけを使う。期待値を同じProduction methodから作らない。再現/実結果・対象commit・日時・OS/tool・実行command・coverage/hashは061と正式manifestへ保存する。

## 実行・完了条件

既定JDK25.0.4/Maven3.9.12/M2で `./mvnw -o --no-transfer-progress -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -pl src/schubert-nk-batch -am -Dtest=ResourceScopeTest,RunReferenceRepositoryTest,InspectionSummaryRepositoryTest,LogCleanupServiceTest test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。変更class全line/method/class/branch100%、static成功、failed/error/skipped0、その後単一clean verifyと46負canary/38scope同source整合。

新JUnit/部分成果の増算なし。PG178の225複合も回帰する。BUG205で確認したdirect finally closeを使い、解析抑止/coverage除外を加えない。BUG195/YKT154/SSC063、YKT162全体は他Repository分類・修正・再試験が残り継続する。PGPT/IT/ST完了ではない。
