# NK-DAT-001 更新対象暗号binding 単体テスト仕様書

NK-DAT-001/NK-MSG-002、ResultBoundResponseSnapshotCodec constructor/encrypt/decrypt/toStringとprivate metadata/layoutLength。RD DAT-009/MQ-008/OPS-009、UI232/236/241、SS324 §6・331 §7.1・352 §11.2.1、SSC-052/049、QA-046、PG-D-140、BUG-014/YKT-012。

## 1. 独立fixture・oracle

鍵はruntime32byte CSPRNG、独立JCE/Deflaterの既存test fixtureを利用する。NKENC1外側と8個length-prefixed AAD部分はtest-only DataOutputStreamで組立/読取し、production codecのAAD/metadata methodでexpectedを作らない。
内側はliteral ASCII NKREF1（0..5）、kind（6）、N12正int64（7..14）、UUIDの2long（15..30）、wire長int32（31..34）、opaque wire bytes（35以降）。QSB/QUESTION/320、NTC/JOB/288、QDL/QUESTION/280。wireはwrapper境界のopaque byte fixtureであり、固定長semantic合格や実DB照合を証明するものではない。実固定長snapshot/参照/UK接続は後続PTで別途必要。
入力wire/返却wireはcaller所有、作業prefixと復号包絡はprivate finallyで消去。入力不変・返却copy独立を実試験し、private working bufferの消去は全終了経路のsource reviewでも照合する。JVM/JCA内部copyの物理消去保証へ拡張しない。

## 2. Test ID

| ID | Test method | 入力/操作とliteral期待 |
|---|---|---|
| PT-DB-INBOX-169 | independentWriteAndReadAllRoutes | 3route×ID1/N12max×UUID zero/allbit。Production encryptを独立JCEで復号して全byte一致、独立JCEで作ったprefixをProduction decryptして入力wire一致 |
| PT-DB-INBOX-170 | nullIdentityAndReferenceContracts | constructor/両method各null、anonymous/owner不在、version002、他layout、NONE/AUTH_SESSION/USER/SCENARIO_FILE/誤QUESTION・JOB参照を拒否。入力正系の借用codecは閉じない |
| PT-DB-INBOX-171 | everyMetadataByteIsAuthenticated | 35位置を各1byte変更して再暗号化、全て拒否。wrong kind/id/tokenMSB・LSB/length、全metadata一致だけwireを返す。期待metadataを暗号内から逆採用しない |
| PT-DB-INBOX-172 | exactLengthAndLegacyRejection | encode/decodeの各実長前/一致/後、prefix未満0/1/34、raw旧fixedbody、prefixだけ、末尾追加/切詰め、encoded length0/-1/最大を拒否。expected320/288/280の固定値 |
| PT-DB-INBOX-173 | keysAadAndCipherDamage | current/previous/unknown version、別key、Message/owner/layout入替、tag/nonce/byte改変・外側不正。鍵rotationは旧世代を明示し、unknownを推測しない |
| PT-DB-INBOX-174 | borrowedOwnershipAndRedaction | 入力不変、返却array書換え後の再decrypt不変、success/failureで借用codecは使用可能、外からclose後は失敗、no raw値toString。private作業buffer全finallyのsource reviewも記録 |
| PT-DB-INBOX-175 | concurrentBindingsNeverCross | 100並行、異Message/owner/ID/token/wireで各結果完全一致、他bindingへの復号不可、鍵寿命固定 |
| PT-DB-INBOX-176 | equalBusinessTimesDoNotAuthorizeAnotherTarget | 同一opaque wire（同確定日時想定）に異ID/tokenを渡すと拒否。旧NKENC1 raw形式は従来codecで読取不変だがbound APIでは拒否。別layout/type・snapshot移植/再包装なし |

## 3. 実行・coverage・証跡

421固定Java25.0.4+7/Maven3.9.12/JUnit5.13.4、API module -am選択testを探索だけに用い、正式clean全module verifyでNullAway/Enforcer/Spotless/SpotBugs、class/method/line/branch100%、failed/error/flaky/skipped/not-run0。8新PTと全既存暗号/Inbox/DB回帰を確認する。
044とevidence/result-binding/manifest.jsonに日時/OS/JDK/version/branch/source/command/exit/各Test ID/coverage/hash/関連SSC/BUGを記録。018全29scopeの同時点性/全hash/参照、017/019負canaryを必須とする。実鍵・nonce/cipher・token・raw wireはGitへ保存しない。Class成功は3更新Program/DB参照/oneshot/工程全体完了ではない。
