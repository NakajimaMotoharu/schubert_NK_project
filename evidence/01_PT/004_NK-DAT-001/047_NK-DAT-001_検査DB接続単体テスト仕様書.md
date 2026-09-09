# NK-DAT-001 検査DB credential・接続 単体テスト仕様書

Program NK-DAT-001/NK-MSG-002、RD DAT-009/OPS-009/SEC/FIL-006、UI212/241/251、SS343 §6.6/342 §6.2～6.3/352 §11.1、QA-046/UIC-006/SSC-049/PG-D-142。対象InspectorDbCredential、InspectorCredentialLoader.loadDatabasePasswordと共通private IO、InspectorCredentialAccessのpassword file契約、InspectorDatabaseConnections。既存AESの031/035とSQL/owned cleanupは回帰対象。main/実systemd配布/親OS/backup実体は別gate。

## 1. Fixture・oracle・null契約

UTF-8 byteは手入力位置/独立JDK標準符号化、期待char列とzero化はliteral/元入力copyから照合。秘密はruntime CSPRNGまたは公開canary、Git/log/DB dumpへ格納しない。保持inode/実temporary file・channelと明示synthetic ACL/属性fault portを組合せる。systemd root credentialの実配布をmockで済ませたとは扱わない。

接続は固定Propertyの独立集合、role/session_user/current_database/readOnly/recoveryのSQL後条件と、隔離PG18.6のSCRAM password正誤で確認する。SQL/JDBC faultはpackage portへ限定注入し、任意Production SQL/role/propertyを公開しない。Null引数はconstructor/factoryの契約違反として拒否、DB値null/未知は非成功、NPE catchなし。

## 2. Test ID

| ID | class / method | 入力・操作・独立期待値 |
|---|---|---|
| PT-DB-INBOX-193 | InspectorDbCredentialTest.validUtf8AndNewlines | ASCII/多byte/補助文字、改行なし/LF/CRLF、space維持、byte入力消去、独立char一致 |
| PT-DB-INBOX-194 | 同.invalidEncodingAndBounds | null/0/65537byte、空改行/BOM/埋込NUL/CR/LF、不正UTF8/overlong/途中切断/surrogateを拒否、失敗も入力zero |
| PT-DB-INBOX-195 | 同.ownedCopiesAndClose | 返却copy変更非伝播、二重close、close後拒否、redaction/例外causeなし |
| PT-DB-INBOX-196 | 同.concurrentOwnership | 100並行copy、close競合の成功copyは独立/close後は拒否、値流出なし |
| PT-DB-INBOX-197 | InspectorDatabaseCredentialLoaderTest.validBoundedFile | 固定名、1/54/69/65536byte、channel/entry/rootの全close後だけmaterial返却、buffer消去 |
| PT-DB-INBOX-198 | 同.missingAndInvalidContent | 必須不存在、途中消失、不正UTF8/BOM/改行、サイズ不正を固定例外、AES previousだけ任意 |
| PT-DB-INBOX-199 | 同.permissionsAndMetadata | file/dir type・owner・mode・link・ACL/RO・前後変化・NULL属性を拒否、読取前gate維持 |
| PT-DB-INBOX-200 | 同.ioFailuresAndCleanup | open/read/0read/過長/size変化/channel/entry/root再検証/close各故障で成功なし、buffer消去 |
| PT-DB-INBOX-201 | 同.concurrentFilesAndAesRegression | 100独立読取、4 AES名/54～69制約を維持、任意名APIなし |
| PT-DB-INBOX-202 | InspectorDatabaseConnectionsTest.fixedConnectionProperties | canonical loopback URLだけ、固定4property、独立password copy、Propertiesは成功/失敗後clear |
| PT-DB-INBOX-203 | 同.urlAndNullContracts | null/credential終了、port0/65536、host/URL parameter/fragment/userinfo/DB識別子不正を接続前拒否 |
| PT-DB-INBOX-204 | 同.connectionAdmission | autoCommit/readOnly/current_user/session_user/database/recovery/row欠落重複/nullの全拒否、返却connection所有境界 |
| PT-DB-INBOX-205 | 同.sqlFailuresRemainRedacted | connect/属性/prepare/execute/next/get/statement/result/connection close各故障の固定SQLException、cause/suppressed/secretなし |
| PT-DB-INBOX-206 | 同.closeAndConcurrentOpen | close冪等、closed後open拒否、open中close排他、100並行fresh接続、既返却をcloseしない |
| PT-DB-INBOX-207 | 同.realScramRoleAndPassword | 隔離PGの専用role正password接続・独立SQL権限/後条件、誤password拒否。trust接続をSCRAM合格へ代用しない |
| PT-DB-INBOX-208 | 同.ownedInspectionConnection | 実providerから既存owned cleanupへ接続し同run/backup/commit/rollbackを維持、他role誤接続不成功 |

## 3. 実行・証跡・完了条件

JDK25.0.4+7/Maven3.9.12/PG18.6/JDBC42.7.13、421の再現環境。選択testは探索、正式clean verifyで全Java moduleのline/method/class/branch100%、NullAway/Spotless/SpotBugs成功、failed/error/skipped/flaky/not-run0を要求。collectorに新scopeを明示追加、009共有packageの所属と019未知/欠落/重複method負canaryも試験する。

048とevidence/inspector-database/manifest.jsonへ全16 Test IDの入力分類/期待・実際、実行日時・OS/tool・branch/source・command/exit・coverage/BUG/SSC/hashを保存する。runtime secret/接続password/credential本文/DB dumpは保存しない。既存30scopeと同run/source/hashを018で照合するまで正式合格に算入しない。
