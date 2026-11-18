# Artemis物理構成・JMS設定設計
## SSC334 ordinary broker/親runtimeのcatalog・factory secondary（2026-10-22）

BUG1604/YKT1357・1606/YKT1359。ApiMessagingRuntimeの最終startup/close wrapper前、API/Web brokerのpassword supplier/createContext/closeのfixed catalog前では、既API Temp/Web Startupのpure finite graph口でcause/suppressed/JMS linked/SQL nextを分類してから通常診断へ縮退する。provider text/causeを新fixed catalogへ持ち込まず、非fatal時の既message/cause/suppressed契約を保つ。borrowed input copyはcreateContext失敗/分類Errorでも既finallyでwipe、copy取得前失敗を取得済と推定せず、context取得失敗からcaller-owned factoryを勝手にcloseしない。

API provider/Web configureOwnedおよびAPI broker partial constructionは、既直接primary/直接closeのcomponent別選択表・raw primary identity・individual reverse secondary順を維持する。raw carrierに元graphを保持できる場合は無用な別型への変換をしない。suppression無効で別secondaryを保持できない場合だけ、必要owned close後のqualified attachment fallbackで元Errorを保持する。複数ownerのpartial/live closeは、取得前にprivate scratchを準備し、既close試行順・成功phase/再closeなしを保持、既onUnconfirmed通知が正常returnした後にだけ未保持graphを分類する。最初の直接Errorの既優先を保ち、scratchは終了finallyでclearする。callbackの非帰還UNKNOWNをcatchして次工程へ進む変更はしない。

親group closeは実childの非Error cause carrier/直接Error契約を確認し、全必要group close後の最終wrapper前で分類する。startupの通知/cleanupで連結できないsecondaryも同じ終端後に分類する。private field/listを反射で差し替えた人工入力を要求しない。全graphはprivate一時scope/既障害引渡しだけ、公開log/JSON/新catalogへ追加保存しない。role/credential源/connector/12設定/window/backoff・normal ACK/commit/業務/wire/SQL/Unit/親期限は不変更、実Root/VM/cohort/鍵/permit/nativeの保留解除ではない。

## SSC333 ordinary consumer startup/closeのsecondary保持（2026-10-22）

BUG1604/YKT1357。API Sync/WebLog/Questionのstartup通知・cleanupとSync複数context close、Web Reply startupは、suppression無効でもnotification/closing graphのErrorを捨てない。addSuppressedの成否だけを保持の実証とせず、未連結secondaryを一時scopeへ保持する。必要owned closeを完了してから既module-local pure graph口で分類、直接primary/通知選択済Error・直接close Errorの既component優先を先に保ち、非fatal時は従来catalog/cause/suppressed順へ帰還する。同一Throwableの自己抑制はしない。

Sync multi-closeは各失敗graphのErrorを遅延捕捉し、残contextのcloseを継続する。最初の直接Errorを含む既選択表と、成功済contextのphaseは保持し、再確認close時に成功phaseを再closeしない。分類を早期throwする共通attachmentへ盲目的に置換しない。全close試行後のonUnconfirmed引渡し・既非帰還UNKNOWNと所有を維持し、そのcallbackが正常returnした場合だけ後段のfatal選択・throwへ進む。UNKNOWNを回避して次工程へ移す変更はしない。

raw provider graphはprivate一時scope/既所有者の障害引渡しに限り、catalog/log/公開JSONへ追加保存しない。登録配送SSC332の確認済rollback/API通知後return/Web同一Error再throw、正常業務/role/SQL/ACK/commit/再送backoff/上限・Unit/親期限は不変更。実VM/current/Root/cohort/鍵/intent/permit/nativeの保留を、このordinary内部契約から解除しない。


## SSC332 ordinary consumerのfatal graphとWeb返信rollback実証（2026-10-22）

BUG1602/YKT1355・1354。普通retryへ委ねる前にcause/suppressed/JMS linked/SQL nextをidentity visitedで有限分類し、到達可能Errorをretry可能としない。API Sync/WebLog/Questionは元direct Errorと同じhalted/terminal・既owner fatal通知を行い、通知が正常returnした場合は元API契約どおりErrorを再throwしない。graph分類口はpure・非I/Oとし通知/再送を代行しない。

Web Replyのpublic onMessageは元例外identity/checked署名とnull/session preflightを保持する。登録consumerの内部同期portは、同配送・同contextのrollback直前attemptedと正常帰還後confirmedを分離し、両state/portはcontext取得前に確保、各配送前resetする。未確認の非Errorは普通retryにせずhalted/terminal・既fatal通知へ。preflightやrollback例外を確認済としない。直接/内包Error時の既best-effort rollbackは未試行だけ一回、既rollbackが失敗した場合に再発行しない。

Webで選択したErrorはowner通知を一回試みた後も同一objectで伝播し、通知Runtime/Errorが当Errorを覆わない。非Error typed fatalの従来通知・CommittedFatalの区別を保持する。普通retryはconfirmedかつ非fatal graphだけ、brokerの既delivery-count/backoff/上限に委ねる。ACK/commit/close/追加業務再送/Root等をこの是正から追加しない。startup/close・native UNKNOWN所有契約、業務/role/wire/DB・DIFは不変更。

## SSC319 ordinary配送の確認済rollback（2026-10-21、内部補足）

試行資格も区別する：内部portはrollback呼出直前のattempted通知と、正常帰還後だけのconfirmed通知を分ける。consumerは両stateを同配送でresetする。direct Errorに対する既best-effort rollbackは未試行時だけ一回、既rollbackがErrorで不確定なら再発行せずfatal/UNKNOWN側を維持する。public listenerの元Error identity/checked契約は不変更で、Errorを別型へ包んで回避しない。通知portは同期のprimitive state更新だけ、取得前に準備しI/O/ACK/追加業務を持たない。

SYNC/ASYNC_WORK/WEB_LOGのordinary retryは、その配送・同じcontextのrollbackが正常帰還したことを必要とする。listenerは既null/session preflight・処理順/元例外identity/公開checked契約を保ち、内部同期通知portはrollback正常帰還後だけ呼ぶ。preflight失敗、rollback失敗、確認port失敗等をcatch型だけから確認済へ読み替えない。public互換entryは新通知を要求しないが、登録済consumerは当内部portを明示使用する。

consumer側の確認stateは所有準備時に確保し、各配送直前にreset、正常rollback後の同期通知だけで更新する。Sync四contextは別state、単一sessionの直列callback内の値を他sessionへ共有しない。普通retry catchで未確認ならhalted/terminal・既fatal通知へ分離し、ACK/commit・追加rollback・新業務再送・close/Root操作をそのcatchから発行しない。確認済だけ既broker delivery-count/最大回数/backoffへ委ねる。CommittedFatal/FailedIsolation/UnconfirmedRollback/directErrorの既typed境界、fatal notificationとUNKNOWN解放保持は維持する。

BUG1565/YKT1322。外部入力/role/admission/画面/電文/SQL/再送上限/親30分・Unit期限は不変更。自己所有finite proxyでnull/preflight/rollback/配送reset/context分離/停止・旧public例外互換を検証する。現providerでの障害発生実測や実Root/nativeの所有・後条件をこの局所仕様から認定しない。

## SSC316 native専用の返却前/close UNKNOWN保持（2026-10-21、S3b）

既component entryは元cleanup例外順位と明示保持handle再確認を維持する。ordinary native entryは明示したRetainingUnknown経路だけを固定trueで選び、三consumerのpartial startup/returned close、API/Web provider設定失敗cleanup、API broker partial/live closeまで同状態を伝播する。provider closeが未確認ならそのcatch frameで既ServiceProcessResourcesの固定UNKNOWN保持へ入り、以後のclose再発行/正常return/外側ownerのcleanupをしない。native保持は外部環境/入力のpermissionやadmission bypassではなく、既admitted graphの解放失敗時だけの処理である。

API親groupは最初の取得前ownerと成功phaseを維持し、未返却childのclose UNKNOWNも内側で保持する。新consumer停止後処理をしない既halted/guardとS2成功phaseを維持する。normal componentの既Runtime/Error/secondary順位は変更しない。Webの返却済みNativeRuntimeは既phase/Execution保持を維持し、返却前factoryだけ明示native経路を接続する。固定設定/全window/role/credential/ACKrollback/再送/期限は不変更。BUG1547/1548/1553/1556/YKT1307、SS342343354。

## SSC315 API factory取得・設定・親owner準備（2026-10-21、S3a）

API providerもSSC311 Webと同様に、profile/endpoint/固定connector・supplier等の準備をfactory取得前に行う。取得後は追加の未保護allocationを挟まず12設定をtryで保護、成功時だけlive factoryを返す。設定Runtime/Errorでは一度closeし元primaryを同一保持、close Error対非Error primaryだけfatal優先、別secondaryはsuppressed、同一Throwableは自己抑制しない。取得自体の例外/nullは未取得資源を推定closeしない。既全設定/三window・credential-free/loopback値を変更しない。

ApiBrokerContextsはowner/lock/password supplier・三owner backing容量/成功phaseを最初のprovider取得より前に準備する。SYNC→WEB_LOG→ASYNCの各正常返却を既容量へ格納し、最後の取得後はfinal field格納だけでownerを完成する。途中失敗は既取得だけ逆順でcloseし、既PG-D379の元primary同一性と個別secondary列挙を維持する。借用注入constructorの所有/credential copyは不変更、live closeはSSC314の確認済みphaseに従う。native返却前UNKNOWN時の外側保持は別S3b gate未完であり、本component契約だけから実native完了を認めない。BUG1553/YKT1307、SS342354、RD/UI/業務不変更。

## SSC314 API JMSの停止通知と確認済みclose（2026-10-21、内部詳細/S2）

SyncRequestConsumers/WebLogConsumers/QuestionWorkConsumers、ApiMessagingRuntime、ApiBrokerContextsはclose要求と全子資源のclose完了を別状態にする。停止通知後はreadyをDOWN、新callback/新contextを非受理とし、既callbackのACK/rollback規約を変えない。各ownerのprivate final lockでcloseを直列化する。Syncの四context・親最大三group・broker最大三factoryは取得前に成功phase領域を準備し、子close正常帰還後だけその子を確認済みとする。再closeは確認済み子を再発行せず、未確認子だけ既定順序で確認する。全子の成功後だけclosed、未確認Runtime/Errorを後続no-op成功へ変換しない。

Syncのcontext順序、親/brokerの逆順、全子への停止試行、既Error優先/同一Throwable/self-suppression回避・固定秘匿例外を維持する。provider closeそのものの時間上限を新設したり親30分/Unit期限を延長しない。このcomponent保持handleでの明示再確認は、native UNKNOWNの自動retry・VM/Root/Unit再操作の許可ではない。部分factory失敗時のowner/外側借用依存の保持はS3で別確認し、S2局所結果をnative全体へ拡大しない。BUG1548/YKT1307/PG-D463、SS342/354、RD/UI/業務仕様不変更。

SSC311（2026-10-20、BUG1537/YKT1297、Web factory取得・設定の所有）：§6のendpoint/全12設定/role/credential/consumer値は不変更。WebBrokerContexts public createはcredential非null確認、password supplier・owner/lock等全state準備をfactory取得より前に完了し、private ctor最後に固定endpoint factory取得/設定を行う。取得/設定成功後は同factoryをfinal factory/ownerへ格納するだけで完成ownerを返し、取得後のcallback/owner/state allocation gapを作らない。open時のpassword copy消去と既live close retry/固定例外・停止規約は維持する。

設定用の内部acquire portは取得前にnonnull検証し、helper内一回取得/nonnull確認直後から既12settingを保護する。全設定成功時だけlive factoryを返し、Runtime/NPE/Error失敗時は当factory.closeを一度試みる。通常は同一primaryを保持しclose失敗を一回suppressedへ追加、同一Throwableは自身へ追加しない。closeがErrorかつprimary非Errorの時だけ同close Errorを優先してprimaryをsuppressedへ保持する。factoryにはまだuser/passwordを設定せず接続/consumerを開始しない。例外/cause/suppressedのprovider診断をログへ出さず、close UNKNOWNを成功へ変更・自動再試行しない。

既三引数注入constructorはcallerが正常完成まで提供factory/ownerを保護する借用入口として区別する。Productionのcreateは取得済み資源をそのctorへ渡して組み立てず、上記factory-last経路を使う。RD/UI/外部業務/wire/認証権限/設定値/既正常結果は不変更。SS343/354・MQFACT311001..003・PG判断/独立PT/実bytecode/同source品質へ追跡し、設計反映自体をPG/PT/native/正式完了にしない。

SSC151153155（PG/PT、2026-10-01）：既存物理SYNC_REQUEST/SYNC_REPLY_WEBはregistry-valid QSBREQ01 Q/A、QSBRSP01 S/Aも運ぶ（応答kindはUI232のSでありRではない）。他通常S/内部IとProtocolValidatorのexact profile/transport/route一致は維持、他layoutの偽Aや内部eventを許さない。全4API/Web送受信境界を同契約でPTする。内部QWKはguard済みactual delivery metadataをbusiness portへ渡す。業務最終QWK DLQだけは新Outbox dispatch UUID Dを_AMQ_DUPL_IDへ使い、body/header/NKMessageIDは元Wを保持する。元transport ID/count/error/detectedAtは不変列、元async address/queue/API_WORKは固定で§11 bounded propertyを構成する。通常workのduplicate ID＝Wは不変更。DB最終ERRORだけでは元ACKせず、対応DのSENTまで確認する。consumer/元body/秘密redaction/role/TTL/local transactionは緩めない。

SSC146（BUG411/YKT328、PG/PT隔離認証fixture）：app login usernameはAPI=`nk_api`、Web=`nk_web`とし、それぞれ同名ACL roleへ一対一で対応付ける。roleは認可、username/passwordは認証の別概念であり、role名だけが正しくても別userのcredentialでは接続を許可しない。固定mq-api/mq-webを通常LoadCredentialで受領し、管理login/roleをappへ転用しない。既存Ops login schubert_ops→nk_ops、保守login schubert_maintenance→nk_mq_maintenanceは維持。ユーザ名aliasやpassword fallbackをProductionへ追加しない。fixtureの旧private設定を保存して限定配置/readback/実認証/誤user・誤credential・cross-role負系をPT297298に記録する。UI231のACL表・6Address/Queue・電文互換・秘密保管契約は不変更。

## 1. 目的・追跡・状態

Apache ActiveMQ ArtemisのBroker物理設定、Address/Queue、security、journal/paging、JMS transaction、consumer、DLQ/Expiry、再配送を定める。

- 状態: `確定`。再配送はQA-041/UIC-001、Address容量・paging/full policyはQA-042/UIC-002承認済み
- 関連UI: 212～213、231、233、251～253
- 関連RD: MQ-001～013、MQ-040～045、PER-005、PER-010、MON-005、T-001、T-003～004
- 関連QA/RDF/UIC: QA-017、021、027、036、QA-041～QA-042、RDFなし、UIC-001～UIC-002

## 2. Instance・process

| 項目 | 設計値 |
|---|---|
| Instance | `/var/lib/schubert-nk/artemis`、単一primary、HA/replicaなし |
| Broker name | `schubert-nk-broker` |
| Java | Java 25、Artemis配布版同梱launcher、専用OS user `schubert-artemis` |
| Bind | Core/JMS `tcp://127.0.0.1:61616?protocols=CORE`、console `127.0.0.1:8161` |
| Persistence | 有効、File Journal、`journal-type=NIO` |
| Data root | bindings/journal/paging/large-messagesをArtemis root配下で分離 |
| Public | 61616/8161/JMXをglobal/LANへ公開しない |
| Clock/timezone | OS NTP同期、JVM timezone Asia/Tokyo。Message expiryはepoch ms |

`journal-type=NIO`はnative `libaio`依存を避け、最大10利用者の成立性と復旧可搬性を優先するSS判断である。ITでNIOのp95・journal
fsync・broker restartを実測し、上位性能未達の場合だけASYNCIOを変更管理する。

## 3. `broker.xml` global設定

| 設定 | 初期値 | 理由・検証 |
|---|---:|---|
| `persistence-enabled` | true | Durable request/work/log/DLQ/Expiry |
| `journal-type` | NIO | 単一SSD、native依存削減 |
| `journal-file-size` | 10MiB | 小規模queueとcompaction単位 |
| `journal-min-files` | 4 | 起動時最低pool |
| `journal-pool-files` | 20 | 200MiB事前pool、実測後上限内調整 |
| `journal-compact-min-files` | 10 | 小file増加抑止 |
| `journal-compact-percentage` | 30 | reclaim閾値 |
| `global-max-size` | 512MiB | JVM heap 1GiB内でAddress memory high-water合計448MiBを包含 |
| `global-max-messages` | 50,000 | UI全Queue件数上限41,000件に運用余裕 |
| `max-disk-usage` | 90 | 90%でproducer block/readiness false |
| `disk-scan-period` | 5,000ms | Disk枯渇検知 |
| `id-cache-size` | 20,000 | Outbox duplicate IDを保持。Async/Web log各上限以上 |
| `persist-id-cache` | true | Broker再起動跨ぎduplicate detection |
| `graceful-shutdown-enabled` | true | 計画停止でConsumer切断待ち |
| `graceful-shutdown-timeout` | 60,000ms | API stop上限と一致 |
| Auto create/delete | 全てfalse | 未定義Address/Queueを起動失敗にする |

`broker.xml`は設定雛形をGit管理し、credential/data path実値を分離する。起動前にXML schema validationとArtemis `check node`相当、起動後に
management APIで実効値を取得してmanifestへ保存する。

## 4. Address・Queue定義

全AddressはANYCAST、durable Queueを明示作成し、Address名とQueue名を混同しない。

| Address | Queue | Durable | Producer | Consumer | Body/TTL |
|---|---|:---:|---|---|---|
| `nk.sync.request` | `nk.sync.request.q` | ○ | `nk_web` | `nk_api` | 最大1,000,000 byte、TTL 5秒 |
| `nk.sync.reply.web` | `nk.sync.reply.web.q` | ○ | `nk_api` | `nk_web` | 最大1,000,000 byte、TTL 10秒 |
| `nk.async.work` | `nk.async.work.q` | ○ | `nk_api` dispatcher | `nk_api` worker | 最大1,000 byte、TTLなし |
| `nk.web.log` | `nk.web.log.q` | ○ | `nk_web` dispatcher | `nk_api` ingestor | 最大10,000 byte、TTLなし |
| `nk.dead.letter` | `nk.dead.letter.q` | ○ | Broker/fatal handler | Ops browse/replay tool | 元messageの定義上限、TTLなし |
| `nk.expiry` | `nk.expiry.q` | ○ | Broker | Ops/maintenance | 元messageの定義上限、TTLなし |

Requestの`JMSReplyTo`は事前定義`nk.sync.reply.web`だけを許可する。APIはtemporary/dynamic destinationを拒否する。将来Web複数instance時は
`nk.sync.reply.<instance-id>`を構築変更として追加し、body layoutは変更しない。

## 5. Address settings

### 5.1 共通

各業務Addressに次を明示する。

- `dead-letter-address=nk.dead.letter`
- `expiry-address=nk.expiry`
- `auto-create-dead-letter-resources=false`、`auto-create-expiry-resources=false`
- `auto-create-addresses/queues=false`、`auto-delete-addresses/queues=false`
- `address-full-policy=PAGE`、`page-full-policy=FAIL`（QA-042/UIC-002承認済み）
- `disk-full-policy=BLOCK`、`page-size-bytes=8MiB`
- `redelivery-collision-avoidance-factor=0.0`
- `enable-metrics=true`、`enable-ingress-timestamp=true`

### 5.2 容量

| Match | 合計保存上限 | 合計件数上限 | Full policy | Warning/Critical |
|---|---:|---:|---:|---|
| `nk.sync.request` | 256MiB | 500 | PAGE→上限FAIL | 250/450件、70/90% |
| `nk.sync.reply.web` | 256MiB | 500 | PAGE→上限FAIL | 250/450件、70/90% |
| `nk.async.work` | 1GiB | 10,000 | PAGE→上限FAIL | 5,000/9,000件、70/90% |
| `nk.web.log` | 256MiB | 10,000 | PAGE→上限FAIL | 5,000/9,000件、70/90% |
| `nk.dead.letter` | 2GiB | 10,000 | PAGE→上限FAIL | 1件/増加継続 |
| `nk.expiry` | 1GiB | 10,000 | PAGE→上限FAIL | 1,000/5,000件、70/90% |

本表はUI 231の用途別合計保存上限であり、memory high-waterとdisk paging上限の合計で実現する。Byte値を
`max-size-bytes`へ直接転記しない。6 Address合計は4.75GiBで、Broker journal/pagingのdisk budget 10GiB内に置く。

### 5.3 QA-042/UIC-002承認値

| Match | Memory high-water (`max-size-bytes` / `max-size-messages`) | Paging store上限 (`page-limit-bytes` / `page-limit-messages`) | 合計上限 |
|---|---:|---:|---:|
| `nk.sync.request` | 32MiB / 50 | 224MiB / 450 | 256MiB / 500 |
| `nk.sync.reply.web` | 32MiB / 50 | 224MiB / 450 | 256MiB / 500 |
| `nk.async.work` | 128MiB / 1,000 | 896MiB / 9,000 | 1GiB / 10,000 |
| `nk.web.log` | 64MiB / 1,000 | 192MiB / 9,000 | 256MiB / 10,000 |
| `nk.dead.letter` | 128MiB / 1,000 | 1,920MiB / 9,000 | 2GiB / 10,000 |
| `nk.expiry` | 64MiB / 1,000 | 960MiB / 9,000 | 1GiB / 10,000 |

承認値は`global-max-size=512MiB`、Address byte high-water合計448MiB、`page-size-bytes=8MiB`、
`address-full-policy=PAGE`、`page-full-policy=FAIL`、`disk-full-policy=BLOCK`とする。High-water到達後は永続pageへ退避し、
byteまたは件数page limitでproducerに明示例外を返し、沈黙破棄しない。Web/APIは新規受付を`9001`へ変換し、
Outboxは残してretryする。Filesystem 90%ではAddress個別上限と別に新規producerをBLOCKし、readiness falseとする。

`page-limit-*`はpaging開始後の受入上限であるため、表ではUI上限からmemory high-waterを控除した。Byte値は8MiBのpage単位で
割り切れる値とし、memory＋pageの設計合計をUI 231/253の上限以内に置く。Page読込によるheap再膨張を防ぐため、
`max-read-page-bytes=16MiB`、`max-read-page-messages=100`を各Addressへ明示し、両条件の先着で制限する。
Journal/page metadata、配送中message、consumer buffer等のoverheadはこの業務message容量に含めず、10GiBのBroker disk budgetと
1GiB heap内でIT実測する。

`DROP`はAddress/page/diskのいずれにも使用せず、DLQ/Expiryの自動削除も行わない。
本設定は`page-limit-*`を備えるArtemis 2.28.0以上、かつAddress別`disk-full-policy`を備える2.50.0以上を前提とする。
導入時の最新安定版でXML schema/config validationを行い、2.50.0未満では実装開始しない。

### 5.4 再配送（QA-041/UIC-001反映済み）

| 設定 | 値 | 実効動作 |
|---|---:|---|
| `max-delivery-attempts` | 4 | 初回＋再配送3回。4回目の失敗後にDLQへroute |
| `redelivery-delay` | 1,000ms | 第1再配送は1秒後 |
| `redelivery-delay-multiplier` | 5.0 | 次回delayを前回の5倍にする |
| `max-redelivery-delay` | 30,000ms | delay上限。3回の範囲ではcapへ到達しない |
| 実効delay | 1秒、5秒、25秒 | QA-041承認済みの一意なrelease/test oracle |

UI 231 §8はQA-041/UIC-001に基づき同値へ修正済みである。Application outboxの再送scheduleとは別のBroker再配送値であり、
`broker.xml`、設定test、IT時系列、監視/runbookの全てで1/5/25秒を使用する。

## 6. JMS connection factory

| Client | Connection | Session/consumer | 初期値 |
|---|---|---|---|
| Web request producer | `nk_web`専用pool | transacted producer session | call timeout 2秒、block-on-durable-send=true |
| Web reply consumer | 同connection、専用session | transacted consumer、1 | consumer window 1MiB、selector/registry相関 |
| Web log dispatcher | 別session | transacted producer | reconnect/retry、HTTP threadと分離 |
| API sync | `nk_api` connection | transacted listener、concurrency 4 | max 8、consumer window 1MiB |
| API async | 別session | transacted listener、concurrency 1 | consumer window 0、priorityなし |
| API Web log | 別session | transacted listener、concurrency 1 | consumer window 64KiB |
| API outbox/reply | listener sessionまたは専用dispatcher | transacted producer | Persistent、send commit確認 |

共通初期値はconnect timeout 3秒、initial connect attempts 3、reconnect attempts unlimited（process稼働中）、retry interval 1秒、
retry multiplier 2、max retry 30秒、client failure check 10秒、connection TTL 30秒とする。API/Web readinessは必要connection/consumerが
確立するまでfalse。計画停止はlistener stop後にsession commit/rollbackを完了する。

## 7. JMS transaction・ACK

- API/Web Consumerは`SESSION_TRANSACTED`。成功時`session.commit()`、一時失敗時`session.rollback()`とする。
- `Message.acknowledge()`を呼ばず、JMS commitが受信ACKと同session上sendを確定する。
- Sync APIはDB commit後、reply sendとrequest ACKを同じJMS transactionでcommitする。XAは使用しない。
- Permanent protocol errorはDLQ sendと元message ACKを同一JMS transactionでcommitし、その後processを非zero終了する。
- Async最終失敗はDB outboxでDLQ sendを確認後に元messageをcommit/ACKする。DB不能時のbroker自動DLQは353で整合する。
- Web reply protocol errorもDLQ send＋reply ACK後、Web processを非zero終了する。

## 8. Property・body guard

送信adapterは次を設定し、受信時に232のheaderと完全一致を検査する。

| Property | 設計 |
|---|---|
| `JMSDeliveryMode` | PERSISTENT |
| `JMSCorrelationID` | wire Correlation ID |
| `JMSReplyTo` | Requestだけ、allowlist Address |
| `JMSExpiration` | Request 5秒、reply 10秒、internal 0 |
| `NKMessageID` | wire Message ID |
| `NKLayoutID` | wire layout ID |
| `NKProtocolVersion` | `001` |
| `_AMQ_DUPL_ID` | Outbox/work/log eventでは業務Message ID ASCII byte。Request/replyも設定可 |

`JMSMessageID`はprovider transport IDとしてlogだけに使用する。Bodyは`BytesMessage`、`getBodyLength`を1,000,000 byte上限より前に検査し、
exact lengthの`byte[]`へ一度だけ読み込む。ObjectMessage/TextMessage/MapMessageは恒久protocol error。

## 9. Correlation registry

Webはrequest送信前にcorrelation IDを`ConcurrentHashMap<UUID, PendingReply>`へ登録し、send失敗/timeout/completeで必ずremoveする。
Reply Consumerは次を順に行う。

1. Body/propertyを恒久protocol検査する。
2. Correlation IDでpending entryをatomic removeする。
3. 存在しdeadline内なら待機threadへ1回だけcompleteする。
4. 不存在/期限後なら画面へ渡さずlate response metricを増やしてJMS ACKする。Broker expiry済みmessageはExpiry Queueへrouteされる。

Registry上限はWeb同期待機20、初期semaphore 12。上限時はMQ送信前に503/429相当を返す。

## 10. Security settings

| Address | `nk_web` | `nk_api` | `nk_mq_maintenance` | `nk_ops` |
|---|---|---|---|---|
| Sync request | send | consume | なし | browseのみ |
| Sync reply | consume | send | なし | browseのみ |
| Async work | なし | send/consume | なし | browse、承認済み再投入 |
| Web log | send | consume | なし | browse |
| DLQ | fatal sendのみ | fatal sendのみ | なし | browse/manage、個別replay/purge |
| Expiry | なし | なし | browse＋7日超selector purgeだけ | browse/manage |

Application roleはAddress/Queue create/delete、management、browse、arbitrary sendを禁止する。Management console/Jolokiaはloopback＋
OS tunnel、strong credential、ADMIN app accountと別管理accountとする。Credentialをapplication log/command lineへ出さない。

SSC-075: Ops専用Core management照会はArtemis `ClientRequestor`が`activemq.management.<UUID>`の一時・非durable reply Address/Queueを明示作成し、完了時に削除する。`nk_ops`に`activemq.management.#`内の`createAddress`/`deleteAddress`/`createNonDurableQueue`/`deleteNonDurableQueue`を許す。業務6 Address、`nk_web`/`nk_api`には付与しない。`nk_mq_maintenance`の例外はSSC-076に限定する。恒久Queue作成/削除と管理namespace外のAddress作成/削除は許さず、global auto-create=falseを維持する。管理応答待ちは各request 2秒上限、null/失敗/cleanup不完了は固定redacted失敗でAPI起動へ進めない。実認証BrokerでOps正系とapp role拒否、2秒境界/一時Address/Queue cleanupをPTする。これは管理値照会の限定契約であり、§13全項目のreadiness完了を意味しない。

SSC-076: Expiry保守専用`nk_mq_maintenance`だけは上記Ops管理照会の例外として、`activemq.management.#`内の一時・非durable reply Address/Queueの作成/削除・送受信を許し、管理電文RBACを有効にする。`mops.#`の全管理操作は`nk_ops`に限定し、保守roleには`nk.expiry.q`の`countMessages`、属性の実RBAC名`getMessageCount`/`getPersistentSize`読取、`removeMessages`だけを個別許可する。業務Addressの作成/削除・他Queue/DLQの管理・アプリroleの管理は禁止し、空/null selectorを全件削除として渡さない。`nk_ops`の既存管理照会はRBACを有効化しても維持する。実Brokerで保守role正系、他Queue/アプリ拒否、一時reply cleanupを確認するまで本修正を完了扱いにしない。

## 11. DLQ metadata

Fatal handlerはbodyを改変せず、次のbounded propertyを付加する。

`_AMQ_ORIG_ADDRESS`、`_AMQ_ORIG_QUEUE`（broker標準が設定）、`NKOriginalTransportID`、`NKMessageID`、`NKCorrelationID`、
`NKLayoutID`、`NKDeliveryCount`、`NKErrorCode`、`NKDetectedBy`、`NKDetectedAt`。

Password/質問本文/body hashを追加propertyへ複製しない。DLQは1件からalertし、自動再投入・自動削除しない。

## 12. Expiry保守

- Expiry Queueは7日保持し、Artemis readiness後/API起動前にmanagement APIでexpiry timestamp cutoffを指定して削除する。
- 実行前後count、対象/削除/失敗、推定byte、cutoffを`batch_runs`へ保存する。
- OSからjournal/page fileを削除しない。DLQを同じselector/purge対象にしない。
- 5,000件以上またはbroker health不良でAPI以降を起動しない。未満の保守失敗は警告継続可。

## 13. Readiness・監視

Readinessはbroker processだけでなく、journal load error 0、全6 Address/Queue存在、durable/routing一致、acceptor loopback、disk<90%、
DLQ/Expiry/Queue閾値、expected security role存在を確認する。MetricはQueue message/delivering/scheduled/acknowledged/expired/killed、
consumer count、address bytes、paging、journal sync、connection countを取得する。

## 14. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-013 | File JournalはNIOを初期値とする | UI 231/T-004内で方式はFile Journalまで固定。小規模単一serverでnative依存を減らす | ITでNIO性能・再起動・破損検知、未達時変更管理 |
| SS-D-014 | Auto create/deleteを全て無効化する | Queue typoを新規queueとして黙認せず起動時検出 | Config test/readinessで名称全件照合 |
| SS-D-015 | JMS manual ACKをtransacted session commitで実現する | JMS transaction時の正規ACK境界、UI 231/212のcrash recovery | PT/ITでcommit前後crash試験 |

## 15. 公式仕様参照

- [Artemis Address Settings](https://artemis.apache.org/components/artemis/documentation/latest/address-settings.html)
- [Artemis Paging](https://artemis.apache.org/components/artemis/documentation/latest/paging)
- [Artemis Flow Control](https://artemis.apache.org/components/artemis/documentation/latest/flow-control.html)
- [Artemis User Manual](https://artemis.apache.org/components/artemis/documentation/latest/book.pdf)

## 16. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Broker/Address/Queue/JMS/security/journal設計を作成。再配送第3間隔はUIC-001/QA-041回答待ち。 |
| 2026-08-31 | 横断監査でUI容量を`max-size-*`とみなすBLOCK設計のJVM不整合をUIC-002/QA-042へ起票し、PAGE・memory high-water・page limit案を提示。 |
| 2026-09-01 | QA-041/UIC-001承認を反映し、再配送設定と実効test oracleを1秒、5秒、25秒へ確定。 |
| 2026-09-01 | QA-042/UIC-002承認を反映し、用途別合計保存上限を維持したmemory high-water・disk paging・page/disk full設定を確定。 |

## SSC-467 受信封筒の通常診断

`GuardedJmsMessage.toString()` は `GuardedJmsMessage[<redacted>]` に固定する。配送上の値、内部ID、アドレス、metadata/bodyを通常診断へ連結しない。明示 `metadata()` と `body()`、配列の所有とコピー、配送・電文・既構造化監査の規則を維持する。SS351、PT-P01810-CATALOG-019。
