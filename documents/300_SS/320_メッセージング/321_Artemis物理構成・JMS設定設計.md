# Artemis物理構成・JMS設定設計

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
