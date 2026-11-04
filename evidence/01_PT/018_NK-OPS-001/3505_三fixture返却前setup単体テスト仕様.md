# NK-OPS-001 三fixture返却前setup単体テスト仕様

Program: NK-OPS-001（試験用資源fixture）、変更担当WBS-P004-05。BUG2245/YKT1991。既存実DB試験の再演や初回Vの差替えではない。設計はorigin/main SS332 SSC320、UI241のtransaction/運用隔離、RD171品質・既存451。原本は633着手前plan/566原三byteへ固定。各sourceには同じPT-FIX-SETUP001～004をfixture class名と組にして一意に使う。

|Fixture|新Test class（同package）|元transaction provider|
|---|---|---|
|batch.repository.BatchDatabaseFixture|BatchDatabaseFixtureTransactionTest|api()|
|api.logging.ApiLogDatabaseFixture（bootstrap test）|ApiLogDatabaseFixtureTransactionTest|api()|
|web.logging.WebLogDatabaseFixture|WebLogDatabaseFixtureTransactionTest|web()|

全class prefixはdev.codex.schubert.nk.。public transactionは同じproviderを一度呼び、package-static beginTransaction(Connection)へ渡す。正常所有移管までのsetupだけが今回の修正scope。constructor/provider/stop/resetは変更しない。

|Test ID/method|入力・操作|独立期待値/根拠|
|---|---|---|
|PT-FIX-SETUP001 normalTransfersOwnership|JDK Connection proxy、setup成功|同一connection返却、setAutoCommit(false)一回、close0、他JDBC0。SSC320正常移管|
|PT-FIX-SETUP002 exactFailureMatrix|setup S(SQL)/R(未知Runtime)/N(NPE)/E(Error)、close -(成功)/S/R/N/E の固定20row|literal winner tableは各setupの先頭四row=P、closeEはsetupS/R/NでC、setupEではP。winner identity不変、異なるloserはsuppressed一回、set→close一回、commit/rollback等0。productionからexpectedを計算しない|
|PT-FIX-SETUP003 identicalThrowableIsNeverSelfSuppressed|各S/R/N/E同一objectをsetup/closeから返す四row|その同一object保持、suppressed0、close一回。self-suppression回避、誤正常化なし|
|PT-FIX-SETUP004 nullFailsBeforeAnyJdbcAccess|null connection|nonnull契約違反を入口でreject、JDBC0。NPEを正常業務としてcatchしない|

各fixture26 literal vector、JUnit四method、全体12method/3suite。fixture classのstatic初期化/constructorによるDB生成は試験対象にしない。全実行はfresh own host JVM/slot、明示method selectorのみ。全schemaやconstructorを検証済みとしない。

PG前に633へ見積0.5/1.5/4pp、通常一群cap10、scope/command/依存/後条件を凍結。S7/10とV同一初回HOLDは別費用原簿。最終PT_DEFAULTは生成bytecodeでhelperのJDK-only呼出、Fixture <clinit>不存在、Testのconstructor呼出不存在、Main/held class不在を確認してから確定する。静的compile自体は-proc:none、明示六sourceのみ。

実行command/version/source SHA、XML、JaCoCo session/CRC・raw全fixtureとhelper四counter、静的check、真正exit、公開hashは3506結果とmanifestへ保存する。失敗/skip/aborted/not-runを合格へ含めない。Coverage除外0、whole fixture四100は今回要求達成を主張せず、未実行DB constructor/providerと全451を残す。旧sourceのPT/coverageへ合算しない。BUG/YKTは全適用先と実provider/影響品質まで揃うまで部分修正状態を維持する。
