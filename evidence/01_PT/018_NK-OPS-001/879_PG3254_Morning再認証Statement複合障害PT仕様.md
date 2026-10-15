# PG3254 Morning再認証Statement複合障害PT仕様

NK-BAT-001/NK-OPS-001、MorningDatabaseSession.Session.recheckConsistent/execution resource owner、RD DAT009/OPS009、UI251/253、SS332先頭SSC063/199・343・451。WBS-P017-01.03、PT-MDB-3254-001。0828開始見積.5/1.5/4週次共有pp。Main a9/全3697/native28/現607L115M0C472Bを保持しTestだけ追加、VM/原DBBackup/新Root/配備/署名0。BUG1251/YKT1017は既完了07:02、五nullmodeを再実行する作業ではない。

## 固定oracle

Statement.execute後primary、close secondaryをNONE/SQL/IAE/STATE/ERRORとする。NONE/NONEを除く24tuple＋同一Throwableを両箇所へ出すSQL/STATE/ERROR三tuple=27。expectedはSS332の固定表で、JdbcResourceFailuresやProduction methodから生成しない。

- primaryなし：closeが主。SQLは公開IOException/固定非秘密文言/cause-suppressed0、未知IAE/STATE/Errorは同一Throwable。
- primary SQL＋close SQL/なし：既知SQL拒否、公開IOException/固定値/cause-suppressed0。
- primary SQL＋close未知：未知closeの同一性を優先。
- primary未知＋closeなし：同一primary/suppressed0。
- primary未知＋closeあり：同一primary＋固定BatchRepositoryException一つ/cause-suppressed0、raw secondaryやself-suppressionを出さない。同じThrowable両回でも同じ規則。

未知例外は非正常としてescapeし、成功や既知DB errorへ変換しない。fixture SQL/Runtime/Error markerは公開試験専用文字列であり実credentialを使わない。

## 実DB・資源・後条件

既BatchDatabaseFixtureの隔離PostgreSQL18で日/runをtuple別に固定。beginBackup→既定FAILED pairを確定し、faultをarmする前に独立SQLで元行を確認。Connectionの対象createStatementだけ実driver Statementを包み、実`SET TRANSACTION READ ONLY`後にprimaryを注入する。Test自身の別Statementでtransaction_read_only=onを確認し、実Statement.close正常終了/物理isClosedを確認した後だけclose faultを注入する。SQL後の未知応答という不確実性でも原行を変更しないことを検査する。

実行一回/close一回、READ ONLY実確認一回、接続close、borrowed Session使用拒否、元二FAILED rowの全既定値/時刻/件数不変、client/advisory0を独立SQLで確認。FixtureはProduction query/期待値生成を呼ばず、observer SQL＋固定Instant/count/statusで判定する。statement null/未取得資源closeを作る試験ではない。原本/MASTER/実VM DBには接続しない。

## 実行と受入

一新@Test methodとTest-only helper、全MorningDatabaseSessionTest（旧61＋新一=62想定）を最新3697の同Main六jar/同依存へ別compileして実行。formatter1.36.1、javac25 -Xlint:all/-Werror、独立XML/FES-flaky-aborted-notrun0、hash/counter/SQL資源後条件を保存する。限定counterと旧native合成値を直接比較せず、必要一新whole3698/542/1643/static六→同28streambyte/CRC資格後に更新する。新Main不具合なら修正前915/916/必要設計分類へ起票。正式1964/53/effortnull/QA051final保留は不変、失敗/未実行/別sourceを加算0。

## PT-MDB-3256-001 同Session完了guardの必要依存（開始群0828内）

補足=同じSQLException固定化を持つcompleteBackupのcompletionGuardも、getAutoCommit/getTransactionIsolation二provider失敗を検査する。beginBackupの元二RUNNING行を確定後、正確に当getterへSQLExceptionを一回注入し、BackupBundleCompletionに到達する前に公開IOException/固定文言/cause-suppressed0で止まる。fixtureのempty backup rootは本物のOwnedTransferDirectory/実inode security/実非root UID-GIDから作るが、検証済みbackupやRoot権限とはしない。fault到達一回、空root不変、接続/OS directory ownerのclose、原RUNNING二行/時刻/count不変、client-advisory0を確認する。SS332/341のDB guard先行と未確認backup非成功が独立期待値。Main/仕様/VM変更0。

3254は09012b15d/exec26861 actual0/全62/FES-aborted-notrun0、27tuple/実RO/実close/元二FAILED・closed session・client/advisory後条件成功。manifestd3637210/XMLbda97f4a、再試行0。ただし3256追加後は新sourceで全63を再検査し、旧62成功を新sourceの代用にしない。新Test群は二method/同一file、必要一wholeは**3699**/542/1643/static六を期待し、先の3698は一method時点の計画履歴として保持。予算/主担当は0828内で、共通費の重複計上0。元BUG1251のnull再試験ではなく、異なるSQL guard/資源post条件の接続確認である。
