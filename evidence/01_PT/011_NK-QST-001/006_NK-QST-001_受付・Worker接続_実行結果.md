# NK-QST-001 受付・Worker接続 実行結果（暫定）

PG420選択v11（08:19:50 JST、exit0）：60PT/FES0/static4zero、log SHA2517b13442974d5a8efa4aad8fcfe49e8cfa74f15fc260a85bef4a2692ace933。errorStageを一回returnに整理後、Workerと全内部classのline/method/class/branch missed各0。受付ASUB7/Worker13/Owned4/STUB5/入力8＋依存23を再実行。複数経路の正常/異常/null/再送/監査/SQL後条件は変更せず、close完了前の返却なし。これは選択・累積coverageでありfresh同Source全6/正式/nativeの代用ではない。次はPG420-full-question-workerのSource固定全6。

PG420選択v9（08:09:51、exit0）：60PT（7/9/7/API37）/FES0/static4zero。AWORK001～013・ASUB7/OUTBOX4/STUB5/入力8、監査のreceipt/job/question/state=ERROR/errorCode分離と秘密0を独立SQLで再試験。log SHA66239c552361e31a125a8014693c07269ddcf581f989b96eac265d15675a51ca。Worker残2B/0L/0M/0C。v10（08:13:08、exit0）はAWORK012＋依存3suiteの24PT/static4zero、SQL driver null statement/resultでACK0/原本不変を確認、log SHA640144a29168566b31c527fbefa0a071814d9a0408433628b1810562523bcbee。残2BはerrorStageの複数returnに重複生成された正常TWR closeのnull guard。null資源は成功return前に拒否されるため、戻り値を確定して全資源close後に一回returnする通常の所有構造へ整理し、全独立試験をv11で再実行する。除外・人工private呼出し・期待値変更は行わない。

v7はAPI37中1F（BUG454、存在しないSENDINGのfixture/allowlist、log SHA8c3b51ab4e2cc60bb26933c56207d3421521525526b81e523c4bbc0a09b96979）。v8はAPI37中1F（BUG456、Outboxの列名取り違え、log SHA670a70a6c8413a373b6b059d0b62cf29d85625a4e299720ab26ed97efbcf9103）。失敗runのAPI静的/全6は未実行・合格加算0。BUG455/YKT346監査修正とBUG454/YKT345のPENDING lease/ERROR/unknown、BUG456列名の直接再試験はv9成功、同Source全6と後続取消/削除は未完。

PG420選択v6（2026-10-02 07:37:08 JST、exit0）：4module58PT（7/9/7/API35）/FES0/static4zero。Worker AWORK001～011（11PT）・受付ASUB7・Owned OUTBOX4・既存STUB5/QuestionSubmitRequest8を実行。実PG18/Artemisで受付→Provider空回答→COMPLETED/通知/audit→元ACK、取消/同W再送/削除中三点継承、count1～4実再配送→ERROR+D commitと2つのACK障害窓の2物理DLQ/1 logical W・D row1・Provider追加0・元ordinary proof不変を確認。2物理コピーのBroker側欠落propertyは未観測のまま、D側count4/API_WORK/errorを独立assertした。D欠落とdriver proof不整合はfixed Temporary→実listener rollback→同transport count1→2（fatal ACK0）。Provider/SQL/NULL/time/NFC4096byte/原本identityの負試験を含む。`QuestionWorkerService`/内部所有classは選択現在byteで残B/L/M/C19/0/0/0、全branch・全6・第三consumer・ordinary ready・native/実CHRは未認定。base HEAD80f1e20fc＋今回未commit delta、v6log SHA52989b52eb7912c2bd62ea95b725b73c4c2a8f5f8bd657ebbd2722202af58c91、rawはWorkPG379/pg420-question-selected-v6.logのみ。commandは4module test-compile/test-jar/test/spotbugs/check/report、MessageCodecTest/LinuxInodeSecurityTest/ApiNonSecretConfigTestと本5suiteを閉鎖指定、JDK25.0.4/Maven3.9.12/Node24.19.0/offline。同code群のfresh全6を後続で採取する。

PG420探索履歴（不合格・未実行は加算0）：v1はprotocol該当test0で開始拒否（log76e443c7c623135b1814237e7e6ad115bf34cd3f85ebbce00036a85a7d847995）、既存3依存suiteを明示したv2は52PT/FES0/static4zero/e710fba97b213a3e03243dd997e9293b8e1b9aeb6cbe8a3806dd58ec57a13305。v3は実Broker2窓含む54PT/FES0/static4zero/59bc7464df7a1a634e9c3fbdf3e1bf9a3468895f23edef1d270b01fa64b8babf、v4はD欠落/driver proof/Provider境界追加56PT/FES0/static4zero/2171fee39047eb77705a21dbd7d669a81edd5cfca401565eebc5c963c9d6c927。v5は新fixtureのHeader getter不存在compile拒否BUG452（log24cafd45313a681c7ec9a7d24258c8c250b04e5c57330a6f392dd551cd6987f2）、v6へ訂正し本結果。BUG447～452は修正前登録・直接試験、YKT344の送信proof/内部clock分類、SSC156のhard接続断・後続lifetime/nativeは別未完。Rollbackのみのhost component観測をLinux IT/ST完了としない。

PG419全6-v2（2026-10-02 01:28:49 JST、exit0）：Source1d3f06e1e83a04d9ed9e0300dd69f9b1351c0b81、全2790PT/FES0/static6zero（80/154/210/798/560/988）。commandはNode24.19.0/JDK25.0.4 PATH・Maven3.9.12 offline、全6 clean/test-compile/test-jar/test/SpotBugs/JaCoCo/JAR/dependency3.9.0 runtime inventory、詳細は018 provisional/PG419-full-question-acceptance/manifest.json（SHA b08a4b54d940d50141b4c7ffebc55a3cc2cd65f00ae8f3603fc070949de303e7）。JUnit stdout/stderr/propertiesを除去、raw logはWorkだけ、同Source host exec/classesもWorkpg419-*へ凍結。ASUB001～007/OUTBOX001～004および既存Inspector scope/JVM flagsの再試験を含む。全host残B/L/M/C1140/3296/551/39、QuestionSubmissionService33/5/0/0、OwnedOutboxDispatcher0/0/0/0。BUG437～446は直接選択＋全回帰で閉鎖、YKT341/342の後続Worker/lifetimeは未完。SS補足SSC156とAWORK006は実装前、Worker/実31起動/3consumer/native/実CHR/全coverage正式認定には加算しない。

PG419選択v9（01:04:12）42PT（7/9/7/API19）F/E/S0/static4zero/exit0。BUG446/YKT343のInspector全8＋ASUB7/OUTBOX4を同reactorで直接再試験。POMは42.7.13 compile明示、Deployment XPath/固定JVM flags/禁則/versionを全件保持。次Source固定の全6再回帰が必要、選択成功を全正式gateに置換しない。

PG419全6 Source31bf758db初回は00:59:01 exit1、Protocol80/Storage154/Bootstrap210成功、API798中旧Inspector scope XPath1F（BUG446/YKT343先行登録）。API静的/Web/Batchは未実行、full合格加算0。Work pg419-six.log SHA256 **fa51c6f7bda70c9d022d6051c83ea54233158675ceecdf84fb393cb400900930**。PG-D-328の明示compile scope/version/runtime unchangedを独立deployment oracleへ追跡し、選択再試験→新Source全6へ進む。

PG419 v8（00:47:22）：34PT（7/9/7/API11）F/E/S0/static4zero/exit0、log SHA256 **35b83b41c9f19e6b17216104884ef606cd8aae7e120881f8a33e1acc780d4dea**。同変更mainの選択exec累積でSubmission残B/L/M/C33/5/0/0、Owned0/0/0/0。Owned全20 branch/57 line/7 methodはinflight close割込と終了前依存保全を含む。ASUB007 public ctor/Random UUIDv4/late9000/config null、ASUB005 PROCESSING/ERROR/response layout/versionを追加。fresh同source全scope/VM/formalではない。実装file SHA256：Submission **0ed3a8a5202ffa172ac1e5d8937627d277b3d6ea3d0fa37319325eeade69869b**、Owned **95d8d7182e062445c2b9dc0b24af4fe25167d7b424670307da2379bb3b845159**。BUG437～445の直接再試験は成功したが横断full/Worker/既存main負系/YKT341342全閉鎖は保留。

PG419 v7追記（00:42:29）：33PT（7/9/7/API10）F/E/S0/static4zero/exit0、log SHA256 **b2b22c6db037ae68ed9fc2d365eb85ad45c055a8f7d673740a6c44b3e53c3181**。OUTBOX001～004は実専用threadの一時SQL/Runtime再試行、inflight join/二重close/close後wake拒否、Error健康失敗＋固定stderr、割込/自己join拒否を確認。B/L/M/C residualはSubmission35/8/1/0、Owned1/2/0/0。close callerのinflight interruptとpublic ctor/初期化null、Inbox PROCESSING/ERROR/layout/versionの追加probeをv8へ進め、未実行の上積みは合格0。

## PG419 受付＋専用Outbox（2026-10-02）

dev-foundation、base531409a28後の未commit同WIP。Java25.0.4/Maven3.9.12/offlineM2、既存isolated PostgreSQL18/Artemis2.56.0 fixture、OS Linux。Productionはsrcのみ、Current baseline不変更、VM signedPG408/source32c/23SQLへ未配備。

`JAVA_HOME=work/toolchain/jdk-25.0.4 PATH=work/toolchain/node-v24.19.0/bin:... ./mvnw -B -o -Dmaven.repo.local=work/toolchain/m2/repository -pl src/schubert-nk-protocol,src/schubert-nk-storage,src/schubert-nk-bootstrap,src/schubert-nk-api spotless:apply test-compile jar:test-jar test -Dtest=MessageCodecTest,LinuxInodeSecurityTest,ApiNonSecretConfigTest,QuestionSubmissionServiceTest spotbugs:check jacoco:report`

v6 00:36:45 exit0、29PT=7/9/7/API6、F/E/S0/static4zero。Work log `PG379/pg419-question-selected-v6.log` SHA256 **e0026111d0829bb585a511c215a624b17f2480eb26ce230613a508f4ae28ed3a**。本runは変更fileを保持した選択探索、正式同source全runではない。

| Test | 実際値・独立根拠 |
|---|---|
| ASUB001 | QSB4400 literal→受付atomicDB→別実threadのJMS persistent→QWK320 literal一致→元SENT→QSBRSP0000。M0/新W分離、type ACCEPTED/state RECEIVED、µs DB/17digit JST ms、同/新Message再送0200、保存cipher/completion/expiry不変更、1question/job/work/Inbox、別送信なし。 |
| ASUB002 | pre-admission期限過ぎは9000/DB0、commit後budget切れは9000/COMPLETED・PENDING保持、後送信確認の再送0200。request threadにはwait/JMS中DB connection0。SQL-only SENT fixtureはproof試験でありMQ受入ではない。 |
| ASUB003 | current auth0102、token本文違い0105、同Message違い恒久拒否と監査、Inbox purge後同本文9000/異本文0105・alias/新q/work0。rollback不確定/監査SQL故障は固定一時型。 |
| ASUB004 | open/null/autocommit/readonly/全atomicINSERT/Inbox完了/commit故障で全5表0、close不確定はcommit済受付1だが成功返却なし、rollback故障もlease0/provider text非露出。 |
| ASUB005 | encrypted snapshot破損、work欠落/内容/W/日時/lease/SENT時刻/job owner/correlation/receipt改変は再送成功せず新受付0。 |
| ASUB006 | receipt名UKだけsavepoint再試行、sequenceが1件目1→失敗2→新成功3で独立期待、3collision exhaustion rollback、同寸法reserved不正の実service拒否。 |

API2新主classの残B/L/M/C：QuestionSubmissionService **35/8/1/0**、OwnedOutboxDispatcher **10/20/1/0**（v6、既存coverageを100%と主張しない）。後者のError redaction修正・専用寿命PTはv7で継続中。Worker/質問read/cancel/delete/全31/3consumer/ordinary ready/CHRは未実装又は未接続。

失敗は加算0：compile初回format未適用、v2 compile API単独旧snapshot（BUG437）、selected初回JDBC/JMS同名import（BUG438）、v2 3F3E/µs投影＋error golden（BUG439440）、v3 1F/fixtureがWireMessage constructorで先行拒否（BUG441）、v4 serial compile警告（BUG443）、v5全6PT成功後静的NPE1（BUG444）。retained cleanup/auditはsource review BUG442、子thread default fatal textはBUG445、修正前台帳登録済。

v2失敗log SHA256 **7bb72c06d1bcbd5809b98f37c565e0e89800f88c830a07f8e36565a7b5a749ec**、v3 **74c3bd871a3caf0fef9ea4a628a9575fc515cbec3bc03c95081ddc0c5e220158**。raw SQL/wire/assertion failure/providerログはWorkに留め、Gitへ保存しない。YKT341 µs/Worker投影とYKT342既存main handler回帰は未完範囲を保持。
