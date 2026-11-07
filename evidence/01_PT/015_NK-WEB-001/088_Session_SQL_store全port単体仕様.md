# Session SQL store全port単体仕様

NK-WEB-001/NK-AUT-001、WBS-P015-01、FUN001/AUT001..004/UI226242/SS312314§7.2.3・331§9.1・332・352、PG-D096/SSC040041056328。対象whole JdbcWebSessionStoreとprivate InvalidStoredRow。Main7aedを変えず、借用JDBC interfaceのSQL・bind・typed getter・資源解放・例外catalogだけを独立に検証する。

PT_DEFAULT。全239行を確認し、必須calleeは公開format-only SessionPayloadIdentity/EncryptedSessionPayload/WebSessionRowとmodule-local SessionStoreException/InvalidSessionRowExceptionだけ。3423で明示されたlocal fatal helperは保留Graph9の四型へ委譲しない。実Source/driver/DB/crypto/session identifier/認証/権限/Root/VM/native/network/fileを使わず、JDK Connection/PreparedStatement/ResultSetの明示proxyが固定入力を返す。Ciphertextは公開零64byteのopaque format fixture、hashは公開固定文字列、UUIDは固定数値/time固定。暗号処理・本物のsession発行ではない。

既JdbcWebSessionStoreTestの実PostgreSQL BeforeAll/実SQL制約/role/lock/fixation試験を抽出・改作・再演しない。本Testは独立したpublic SQL界面の別Program仕様で、元の実DB PTはNOT_RUN/HOLDのまま。新しいproxyはSQLを解釈/実行するDB emulatorではなく、手書command/parameter/callback/close観測portであり、実DB後条件の受入にしない。

|Test ID|目的・入力/操作と独立期待|
|---|---|
|PT-WEB-JDBCSTOREPORT001|全5APIのnull/不正hash/version/replace異identity・非連番→事前拒否、JDBC callback0|
|PT-WEB-JDBCSTOREPORT002|find absent→Optional.empty、明示九column＋hash=? for update、一bind、result→statement close、borrowed connection変更0|
|PT-WEB-JDBCSTOREPORT003|一row→手書九値/typed UUID・OffsetDateTime・Integer・Long getter、UTC Instant復元とopaque bytes copy、二next、資源close後だけ返却|
|PT-WEB-JDBCSTOREPORT004|重複row→InvalidSessionRowException、両資源close完了後の固定分類、未送信変更0|
|PT-WEB-JDBCSTOREPORT005|九column各null、hash/key/cipher/time/idle/version値不正→clean close後InvalidSessionRow、getter SQLException/型不正はinfrastructureへ区別|
|PT-WEB-JDBCSTOREPORT006|malformed row＋result/statement close failure→通常SessionStoreException、invalid-row削除の資格を与えない|
|PT-WEB-JDBCSTOREPORT007|malformed/SQL row-read＋fatal close/cause→元Error identity、両owned closeを保つ。local有限acyclic graphのみ|
|PT-WEB-JDBCSTOREPORT008|insert九placeholder/九bind型位置・UTC、version0のみ、update count1成功/0・2・負失敗、UPSERT0|
|PT-WEB-JDBCSTOREPORT009|replaceはcipher/version更新＋元identity三値/version CASの十bind、0false/1true/その他失敗、再INSERT0|
|PT-WEB-JDBCSTOREPORT010|deleteはidentity三値/version、deleteByHashはhashだけ、0false/1true/その他失敗、borrowed TX操作0|
|PT-WEB-JDBCSTOREPORT011|autocommit/read-only/nullable statement・result→固定失敗、短絡・作成済owned資源だけclose、connection ownership変更0|
|PT-WEB-JDBCSTOREPORT012|各実JDBC stageのSQLExceptionを個別注入→value-free固定catalog、未作成資源をcloseせず作成済close、原因/suppressed診断を保持しない|
|PT-WEB-JDBCSTOREPORT013|primary/cleanupの同時失敗・direct/cause Error優先を元objectで確認、return成功/invalid削除分類0|
|PT-WEB-JDBCSTOREPORT014|µs適合だがOffsetDateTime範囲外Instantはinsert/replace/delete中に固定障害、statement close、borrowed TX不変|
|PT-WEB-JDBCSTOREPORT015|同stateless storeへ独立二connectionで並行callback、bind/row/資源stateを交換しない。実row lock/DB transaction並行を認定しない|

期待値はSS331の九column・DDL型/不変条件、SS314のversion0/CAS/borrowed TXとinvalid-row分類、SS332のJDBC4.2 UTC、SS314328のmodule-local fatal identityから手書する。Production SQL/DTOからexpected列/SQLを生成しない。Connection commit/rollback/close/setAutoCommit/setReadOnly/isolation変更はproxyで常に禁止。期待するSQLは技術schemaだけでliteral固定、parametersは別typed値。入力・実際は公開fixtureで、raw session/Cookie/token/認証context/keyなし。

null/欠落/空/未知型/境界/各SQLとowned close例外/二row/再送CAS0/独立並行を全15methodで確認する。unknown provider runtimeを成功へしない。Main全physical/全Code L/M/C/B未達0が必要で、標準compiler filterだけ、support DTO/helperをwhole sourceへ加算しない。SDK/JDBC interface以外のdriver・providerはclasspath/runtimeから除外、Main既normal22084/六静的22086は同byteで再利用、新Testだけlint/Werror/PMD/CS/GJFを実施。source固定push後一Unit、実exit/XML/F-E-S-abort0/一exec-session/CRC/probe/全実method/initを独立postで照合する。旧exec/旧sourceを合算しない。

元/v3/v4/v5・正式1964-53・工数null・QA051final・全HOLD不変。群開始2/5/9pp cap10、開始unique415/whole93。実DB後条件・constraint・grant・race/real crypto・実session/filter/runtime/CHR/451/親leafは別未受入。新規unit自身が不成立なら欠測/失敗のまま保持する。
