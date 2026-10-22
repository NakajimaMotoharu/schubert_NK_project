# 1526 リカバリJMS三領域・F02個別PG品質matrix

2026-10-23、群1771。source e7d64fda2453e906ee6ccc5fe718e5c29841e4aa／元PG6930-six-v1。新規対象P005-02/03/04/F02だけ、既v5参考2.67/4.50/9.77pp、共有20pp目標/30pp上限を維持する。必要4再認証とcatalog新1は488で当source成立済み。残る歴史13を一括再認証しない。本文は個別PG/独立期待値/適用性の事前matrixであり、未達条件は成功にしない。

## 実施範囲と原証跡の再利用

P005-02の19file、03の22file、04の3fileを全件点検、44fileは481のlogical ownedArtifactsとexact一致させる。加えて485に既登録の03支援二Main（FailedJmsIsolationException/UnconfirmedJmsRollbackException、implementationSupportOnly・追加予算0）も全hash/counter/原Testを照合し、物理scopeは計46とする。新logical leaf/予算は増やさず支援も除外しない。04のshared ApiBrokerContextsは03の所有・受入・hash/四counterへ参照し追加費0。F02は専有Production Java0だが、全7POM、Wrapper、全6moduleの実build入力/出力/toolchain/境界という非Java契約があり、0/0を100にしない。

通常PTが既定。当scopeの原4222/660・全Main851/物理1669/全source Test/fixtureを同byte/sourceで照合し、既SUCCESSの確認再演0。Main/Test/POM/既gateは不変更。個別scopeの実counter全miss0、当原suiteのF/E/S/flaky/not-run0、format/NullAway/lint/SpotBugs/分類済み静的根拠を使用し、Root11はF03未受入のまま。必要な新PT/是正が生じた場合には新sourceで451所定の検証を実施し旧成功を転用しない。

## P005-02：全19file・MQ-021～036

| 対象group | 独立oracle/Test・入力/戻り/状態/例外/後条件 |
|---|---|
| JmsRequestReplyClient / ReplyCorrelationRegistry / PendingReply | PT-JMS-008/ReplyCorrelationRegistryTest/JmsRequestReplyClientTest。固定UUID・Clock・1ns/2s/超過、容量1/12/20/21、先登録・send一回、duplicate/full、complete/expire/cancel競合、deadline同時刻late、defensive byte、send checked/unchecked・interrupt回復・semaphore/registry解放。expectedをproductionから生成しない |
| JmsReplyDecoder / ValidatedReply | PT-JMS-005/006/008。独立256byte/header＋DATA、Bytes/persistent/TTL/ID/property/routeの各不一致、負/百万超/コピー長変化、null/空/未知/temporary/FQQN不正を型付き拒否。reply bodyはclone/非公開診断、success前に全metadata/固定長を照合 |
| ArtemisRequestSender / JmsRequestSender / JmsContextFactory | PT-JMS-005/ArtemisRequestSenderTest。caller factoryから専用transacted context、固定request FQQN/ReplyTo/TTL5000/persistent、Q/Sと承認QSB Q/A、send→commit一回。失敗時rollback/closeのprimary identity/secondary graph/Error優先、未取得close無し。二interfaceに架空counterを付けない |
| ArtemisReplyConsumer / ArtemisReplyConsumers / ArtemisReplyDlqSender / CommittedFatalReplyException | PT-JMS-006/009/014、ReplyIsolationPrimary/ReplyFatalIsolation/ReplyRollbackSignal/ReplyRollbackUnconfirmed/ReplyCommittedTerminalAdmission/ReplyConsumerGraph332/ReplyCleanup333/BrokerGraph334各Test。順序はdecode→correlation→commit、lateもACK。恒久不正は元body不読/不変・bounded metadata→同transaction DLQ＋ACK→terminal。未確認rollback/graph内Errorをordinary retryとしない、Web Errorは通知後も同identity再throw。開始前state準備、停止後新配送/新start拒否、close失敗をclosed成功へ正常化しない |
| WebBrokerContexts | PT-JMS-WEB-001～003/WebBrokerContexts/WebBrokerFactoryOwnership/WebFactoryNativeRetention/BrokerGraph334。固定nk_web/loopback CORE/12設定、profile1MiB、password copy長1～65536と全finally消去、stopping拒否、借用factory/owner区別。取得前state完成・設定失敗一close・direct/内包Error優先・同一Throwable抑制回避。native名のfixture結果を実VM/実鍵/UNKNOWN解放済みへ広げない |
| ProtectedReadWireClient / MediaDescriptorWireClient / ProtectedReadWireException | PT-WEB-166～173/238～245/S3WIRE001～008、WebBusinessWireClientsTest/ScenarioWireClientTest/AnimationWireClientTest/MusicWireClientTest。trusted allowlist/UUID/context/固定layout・長さ、optional error/response型、constant-time context一致、request/response temporary byte消去、invalid input/response/unavailableの固定区別。HTTPからcapability選択/業務DB直結/自動再送無し、実file配信は別owner |
| MqLoginClient | PT-WEB-054～059/MqLoginClientTest。LGNREQ640/LGNRSP688、Username NFC/trim/role/context/0106 retry/error filler/0200 snapshot、unknown code/ID不一致、literal IP・scoped IPv6拒否。password/request/response copyを全経路消去、session grantは外側。API auth/roleはAuthenticationContextVerifier/AuthorizationService原Testへ費0参照 |
| package-info | @NullMarked宣言。全実compile/NullAwayを要求、実行method無し |

MQ-021と036は上表Login/context及びAPI verifierへ接続、022はwire/transport ID一致、023はBytesだけ、024～031/033～035は当protocol原FieldCodec/MessageCodec/PayloadCodec/PayloadGoldenVector/JstWireTimestamp等の独立byte/全64layout/287hashを費0で参照する。032は当adapterの恒久拒否・terminal通知/非zero方針とUnit宣言へ対応し、実systemd自動再起動/実起動を本component受入から認定しない。全要件の当owned境界の寄与を照合し、他owner/全native/IT/STの受入を代行しない。

### 送信と2秒待機の判定（PG-D515）

UI212接続表と§2末尾は「同期reply待ち2秒」、SS321§6はproducer call timeout2000ms、§9は受信時deadline照合、SS312§3.2はexchange timeoutと自動再送無しを別責務として定める。旧JmsRequestReplyClientはsend後のfuture待ちをtimeout以内に制限し、registryは受信時に期限内一回complete/期限後lateを判定する。既に期限内にcompleteした応答をcallerの後続時計だけで新たに無効化する条件や「connect/send/close込み全exchange hard2秒」は上位にない。合算2秒へMain/既oracleを変えない。source点検時の合算疑義は追加製造バグと断定せず解消した。正常画面p95/実provider処理時間はIT/STで未実測のまま。

## P005-03：全22file・consumer/transaction/所有

| 全対象group | 独立oracle/Test・後条件 |
|---|---|
| ApiSyncRequestDispatcher / SyncRequestProcessor | DISPATCH026-A～Fの独立31layout→各processor port一意、欠落/未知/不正方向/null/delegate null/例外identity/並行分離。marker processorの単体契約であり実assembly/native readinessではない |
| JmsMessageGuard / GuardedJmsMessage | PT-JMS-005/006/JmsMessageGuardTest・ArtemisTransportContractTest。body型・bytes上限・長さ変化・route/ReplyTo/IDs/version/TTL/deliverycountを先に照合、copy immutable/固定秘匿例外。未検査inputを業務portへ流さない |
| SyncRequestListener / TransactedEventListener / InternalEventProcessor / DeliveryMetadata | PT-JMS-005～009/RB319/SyncRequestListenerTest/InternalEventListenerTest/DeliveryMetadataTest。guard→decode→processor→reply→commit（ACK）。内部eventは固定E/I、DeliveryMetadataは当配送のcount/transport/timeであり推測1を渡さない。正常rollback直後だけconfirmed、attemptedと区別、public互換口と登録consumer口を分ける |
| InboundTransactions / CommittedFatalInboundException / DlqSender / FatalDlqMessageWriter / FatalDlqMetadata / ReplySender | PT-JMS-006/007/009、InboundTransactionsPrimaryContract/OutboundJmsAdapter/FatalDlqMessageWriter/OutboxDlqMetadata。元body保持・固定DLQ/TTL0/非秘密bounded metadata、DLQとACK同commit、隔離失敗でACKしない。元例外/secondary/Error、同一Throwable、未知transport ID上限128を固定negativeで照合。JMSMessageFactory共有は04が所有し費0参照 |
| SyncRequestConsumers / ApiMessagingRuntime | PT-JMS-013/016/CORE001～006、ApiConsumerCloseOwnership/ConsumerRollbackUnconfirmed/ConfirmedRollbackCallback/FatalIsolationConsumers/ConsumerGraph332/ConsumerCleanup333/ParentGraph334/ApiConsumerRemainder/TerminalRemainder/ApiNativeRetention等。四独立contextのrollback state分離、全listener設置後start、停止でreadyDOWN、新配送抑止、成功close phase再発行無し・未確認子のみ再確認、全group逆順close。通知callbackが非帰還ならUNKNOWNを維持、Error graphは必要close試行後分類、原primary/既優先と未連結secondaryを保持 |
| ApiBrokerContexts | PT-JMS-024/ApiBrokerContexts/ApiFactoryOwnership/ApiBrokerFactoryRemainder/BrokerGraph334。三factoryを取得前stateで保護しSYNC→WEB_LOG→ASYNC、partial failureは取得済だけ逆順close、password copyを消去、fixed nk_api/独立3window、live close成功phaseだけ確定。native variantの既finite policy fixtureと実Root/鍵所有を混同しない |
| SqlConnectionProvider / package-info4 | caller-owned借用JDBC境界と@NullMarked宣言。新transaction/close権限を付与しない。実行counter無しはN/A |

終了依存はP002-03/C04。当sourceで488に成立済み。共有参照の手続と全原suite/physical/source/四counter/当static照合後だけ受入候補とする。Root/native UNKNOWNはglobal保留を維持する。

既implementation support二MainのPG：FailedJmsIsolationExceptionは隔離未確定を固定型/固定文言にしてprimary causeと別protocol suppressedを保持、UnconfirmedJmsRollbackExceptionはrollback未帰還を固定型と元primary/rollback identityで保持する。equalsがtrueの別objectを同一扱いせず、nullを即時拒否、自己suppressionせず、primary側suppression無効でも自身のsuppressedへ元secondaryを保持。PT-JMS-ISO009～012/UNC005～008の当原各四methodを全source/物理counterへjoinする。資源/transactionを自ら発行せずErrorやUNKNOWNを成功へ変換しない。

## P005-04：全3file＋shared一参照

- ArtemisConnectionFactoryProvider：固定loopback CORE URL/1..65535/余分query・host・protocol拒否、ConsumerProfile SYNC1048576/ASYNC0/WEB_LOG65536、12設定/credential未保持。ArtemisConnectionFactoryProviderTest/ApiFactoryOwnershipTest/ApiBrokerFactoryRemainderTest/BrokerGraph334のliteral getter/mutated portで初期値・全設定途中Error/Runtime・取得失敗/null・close優先・同objectを照合。
- JmsMessageFactory：OutboundJmsAdapterTest/ArtemisTransportContractTestの独立wireでS/SとQSB S/A、registry/長さ/固定identity/property/Bytes、request/E/不一致拒否。bodyをexpected生成に使わない。
- TransactedJmsContextProvider：借用取得口のみ、interfaceに実測100を補完しない。
- shared ApiBrokerContexts：03の全Main/hash/実counter/受入を参照。所有/costを04へ複製しない。終了依存P002-03/C04に加えshared owner03も同source成立後に照合。

## F02：全toolchain/build/依存境界・SYS寄与

元PG6930のcommandはsrc全6moduleをroot POMから明示選択し、clean/全6事前format/test-compile/test-jar/test/SpotBugs/JaCoCo report/Jarを実行した。root Enforcer(Java25/Maven3.9.12以上4未満/convergence)、lint Werror/NullAway/固定依存は全7POMと原archive/実Main major69へjoinする。これは全体coverage100やroot clean verify正式認定の代わりではない。

SYS-001/002はNK artifact/package名とrelease25、003/004はLinux/Ubuntu Java25.0.4配布・PG18/driver42.7.13固定構成、005はWeb→業務API依存無し/Artemis境界、006/007はWeb/業務/codec分離で既互換/DIFを勝手に変えない構成、008～010はオンプレ/コンテナ非前提/local Storage/libraryと限定依存、012～014は入口Caddyを業務Jarから分離した公開IP/port/TLS交換境界へ対応する。これは当build/architecture寄与のtraceであり、実server OS/公開port/TLS/素材/画面・全SYSのST受入ではない。それらのsource/設定・原Test参照と未完ownerを明示し、F02の専有Java0を全要件の実動成功へ変換しない。

既原BatchRuntimeDependencyTest/PT-BAT-283、WebRuntimeDependencyTest等の閉鎖dependency literal/負canary、SS311 SSC084/088/126/142の互換api.* binaryを実bootstrap artifact所属で照合する。package prefixだけをAPI依存と誤認しない。POM compile/runtime/test scope、7POM/Wrapper/hash、固定toolchain版・再現手順を確認する。

### 未実装のArchUnit品質工程（PG-D516、追加発見・同群内）

SS311§2が指定するArchUnitチェックのsource/証跡はtools/quality・全Production POM/testに見当たらない。未実装の品質工程として補完し、F02をそれまで未受入とする。既実装不具合の修正や上位仕様変更ではない。旧v5F02標準0.25ppは比較値を維持し、追加発見/実装/実行費を分離する。同群の累計20/30pp条件は拡大しない。

ArchUnit1.4.2（公式release/Java25を包含するclass-file対応、Maven Centralから固定版）＋既SLF4J2.0.18だけをtool私有classpathに置く。Production POM/既gate/実runtime依存を変更しない。返却済み全6Jar・1669classを固定hashに結び、physical artifact所属でmoduleの有向依存とframework/Controller/JDBC/Repository上位呼出の禁止を静的検査する。全入力classのimport件数・不明/重複・空集合を検査し、安易なexclude/凍結/allowEmptyは禁止。F03 Root11の意味/個別PMD審査を行ったとはしない。

自己所有の小さい手書きJava canaryを別作業領域でjavacし、正規module依存・bootstrap物理所属alias・禁止JDBC/HTTP/MVC・逆向きAPI/Web依存・Controller SQL・repository上位呼出・未所属class参照を検査する。canaryのclass initializerを実行しないことも検査する。対象MainをClass.forName/load/init/entryで実行せず、ArchUnitのbytecode importerだけを使用しclasspathの不足型解決も無効化する。library/helperのsource/hash/command/exit/versionと初回失敗を保存し、代替PT・新Production PASS/coverageへ算入しない。実VM/Root/DB/鍵/permit/native/配備操作は0。

公式参照： https://www.archunit.org/news/release/2026/04/18/release-v1.4.2.html 、 https://www.archunit.org/userguide/html/000_Index.html 、version固定API根拠 https://github.com/TNG/ArchUnit/tree/v1.4.2 。後続成果・取得版/hash・静的違反の分類を別結果へ記録する。

## 出口

PG点検結論：全44 owned source/公開method・取得前準備/close/例外/metadata/copy/認証wire境界を上表へ照合し、既承認仕様に対してProduction変更不要。五empty counterはJmsContextFactory/JmsRequestSender/SyncRequestProcessor/SqlConnectionProvider/TransactedJmsContextProviderという抽象口に限定し、元class hash/Java25 javap flags/Code無しで独立照合、0/0を100へ補完しない。新ArchUnit工程は実行済みで全1669import/5rule0・正負11期待一致、原7f80c3f1。初回PG/通常PTの代替ではなく、既定SSの不足品質工程を埋めた。新source/Main/Test/POM/元4222再演0。残る当原case/全scope/counter/static/全POM/版とsource別strict登録を機械照合するまで受入は更新しない（REVIEW_COMPLETE_PENDING_MACHINE_WITNESS）。

6962初回readはlogical44とcurrent ownerの既支援2を同一setと仮定した新binder不備でactual1/manifest前停止。BUG1638/YKT1391を修正前登録し、logical22を保ちながら正規支援2の名称/hash/Module/class/owner/costOwner/元origin/support flag/追加費0を明示照合する。二支援は追加機能/新費用/新分母でなく既metadata。元scope/予算を変えず、unknown extra/欠落/誤owner/費用追加を負fixtureで拒否する。元4222/ArchUnit原成功は再実行しない。

全個別criteria/当原source/全scope/独立期待値/必要品質/488依存/shared ownerを照合し、成立した行だけsource別registerへ追加する。4項目未達のまま新JDBC/C07群へ拡大しない。formal1964/53・歴史17・工数null・QA051 FINAL_HELD・PTALT0は維持する。実native/CHR/global四counter/451全体/IT/STは別未完。
