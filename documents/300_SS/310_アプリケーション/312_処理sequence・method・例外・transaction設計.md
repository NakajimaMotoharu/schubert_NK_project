# 処理sequence・method・例外・transaction設計

## 1. 目的・追跡

主要処理の呼出順、method契約、引数・戻り値、例外、PostgreSQL/JMS transaction境界とcrash pointを定める。

- 関連UI: 212～213、223～237、241～242、251～252
- 関連RD: FUN-001～013、FUN-101～108、AUT-001～004、ASY-001～009、QST-001～105、MQ-001～045
- 関連QA/RDF/UIC: QA-002、009、027、030、034～040、RDFなし、UICなし

## 2. 共通method規約

- 公開application serviceの日時引数・戻り値は`Instant`、wire変換だけ`JstWireTimestamp`を使用する。
- DB内部IDは`long`、N12上限検査済みの非負値。公開受付IDは`ReceiptId`、UUIDは`UUID`で表す。
- OptionalなDB値は`Optional<T>`またはnullable row fieldのどちらかをrepository単位で統一し、wireの全spaceをdomainへ持ち込まない。
- Pageは`PageRequest(page,size)`と`PageResult<T>`を使用し、1未満/最終超過の補正はapplication serviceで行う。
- Application serviceのcommand/query objectはimmutable `record`。Password、context raw、本文を含むrecordは`toString`をoverrideしてredactする。
- Transaction retryをannotationで無条件化しない。Message再配送/inbox、optimistic lock、明示的な一時例外分類で制御する。

## 3. 同期Request/Reply

### 3.1 Sequence

```text
Controller
  -> FormValidator
  -> WebMapper.toRequest()
  -> JmsRequestReplyClient.exchange(request, 2s)
       -> encode / persistent send / correlation register
       -> wait reply
  -> API SyncRequestListener
       -> InboundMessageGuard（property/header/length/layout）
       -> Login: 匿名Inbox、Logout: 失効専用lookup（§4.2）、その他: AuthenticationContextVerifier
       -> InboxCoordinator.execute()
            -> LayoutHandler.handle()
                 -> @Transactional ApplicationService
            -> request_inbox COMPLETED
       -> ReplySender.send()
       -> JMS session commit（request ACKを含む）
  <- Web decode / correlation検証
  -> WebMapper.toViewModel()
  -> Template
```

### 3.2 Web method

| Method | 引数 | 戻り値 | 主な例外・処理 |
|---|---|---|---|
| `JmsRequestReplyClient.exchange` | `WireRequest<Q>`, `Duration timeout` | `WireResponse<S>` | Encode失敗はHTTP 400相当、send/timeoutは`WebTemporaryFailureException`、protocol不正replyはDLQ後fatal |
| `ReplyCorrelationRegistry.register` | correlation ID、deadline | `PendingReply` | 重複IDは起動不変条件違反 |
| `ReplyCorrelationRegistry.complete` | received response | `boolean` | 待機中ならtrue、timeout済みならfalseでExpiry/破棄log |
| `WireMessageFactory.newRequest` | layout、context、payload | `WireRequest<Q>` | Message ID UUID、root correlation=自身 |

Webはtimeout時に自動再送しない。参照GETは利用者の再操作で新Message ID、更新POSTは同じoperation tokenを使用する。

### 3.3 API method・transaction

| Method | Transaction | 契約 |
|---|---|---|
| `SyncRequestListener.onMessage` | JMS local transaction | DB処理、reply送信後にJMS commit。例外時rollbackまたはDLQ transaction |
| `InboundMessageGuard.validate` | なし、業務前 | 232 §8順。恒久不正は`PermanentProtocolException` |
| `InboxCoordinator.execute` | PostgreSQL transaction内 | Message IDをINSERT。重複は処理状態/保存結果を判定。新規だけhandler実行 |
| `LayoutHandler.handle` | 呼出元transactionへ参加 | 業務結果を返す。JMS APIを呼ばない |
| `ReplayResponseFactory.rebuild` | read-only transaction | result_refまたは暗号化responseから同じ業務結果を再構成 |

JMS sessionは`SESSION_TRANSACTED`とし、`Message.acknowledge()`は呼ばない。`session.commit()`が受信ACKとreply sendを同時確定する。
UIの「manual ACK」は、framework自動ACKではなくlistenerがJMS commit時点を制御する意味として実装する。

`LGNREQ01`は認証contextを持たないため、恒久protocol検証後に匿名InboxをMessage IDで先に開始する。
Username・client address・NFC後passwordのexternal-key HMACを照合し、Inbox、失敗counter、auth session、暗号化response
snapshotを同一PostgreSQL transactionで確定する。これによりDB commit後のJMS再配送で失敗counterやsessionを二重更新しない。

#### 3.3.1 Scenario認証事前確認（SSC-023）

`AuthenticationContextVerifier.inspectReadOnly(connection, context, now)`は、caller所有の明示read-only transactionでDBのsession/Userを1つのJOIN SELECTにより参照する。未知context、revoked、expires_at <= now、非ACTIVEを0102、必須列NULL/未知role/JDBC故障を9000型として拒否する。通常`verify`と同じrow判定を使うが、FOR UPDATE、idle延長、commit/rollback/connection closeは行わない。autoCommitまたはreadOnly=falseを拒否する。

このactorは参照snapshot取得前の事前確認だけであり、通常requestの最終認証や永続的な権限証明の代替ではない。333のfile I/O前にsnapshot transactionをcommitし、I/O後の最終短write transactionでは新しいstage時刻で通常`verify`を実行し、現在のowner/roleを再検証してからInbox/responseを確定する。途中の失効/期限切れ/無効化を事前actorで迂回しない。File I/O中のrow lock/DB transaction保持は禁止する。最終Inbox・再送・file再生成を含むservice接続は独立したPT gateとする。

### 3.4 Crash matrix

| Crash point | DB | Reply/JMS ACK | Recovery |
|---|---|---|---|
| Body検証前/中 | 未更新 | 未確定 | 恒久不正は同一JMS transactionでDLQ後exit。一時I/Oならrollback |
| Inbox INSERT前 | 未更新 | 未確定 | Request再配送、通常新規処理 |
| 業務rollback後 | 未更新 | 未確定 | 一時障害は再配送。業務errorはerror responseを確定 |
| DB commit後、reply送信前 | 確定 | 未確定 | 再配送時にinboxから保存済み結果をreply |
| Reply send後、JMS commit前 | 確定 | 未確定 | JMS rollbackでsendも取消。再配送してreply再送 |
| JMS commit後 | 確定 | Reply/ACK確定 | 完了。Web timeoutなら遅延replyを画面へ使わない |

## 4. Login・Logout

### 4.1 Login

| Method | 引数 | 戻り値 | Transaction/例外 |
|---|---|---|---|
| `AuthenticationService.authenticate` | normalized username、`char[]` password、`InetAddress`、Message ID | `LoginResult` | User/IP試行rowとaccount/sessionを1 transactionでlock。認証失敗もcounter commit |
| `LoginAttemptRepository.lockForAttempt` | username key、IP | `AttemptState` | `SELECT ... FOR UPDATE`。不存在usernameはIP rowのみ更新 |
| `AuthSessionService.issue` | user、client、Message ID | raw contextを含む`IssuedContext` | rawのhash＋AES-GCM暗号文を保存、3件目は最古revoke |
| `MqAuthenticationProvider.authenticate` | Spring authentication token | authenticated principal | `0101`は同一message、`0106`はRetry-After、`9000`は503 |

Password `char[]`はencode照合直後にzero fillする。Login Message ID重複時は`auth_sessions.created_message_id`から暗号化raw contextを復号し、
同じ成功結果を返す。認証失敗/lockは`request_inbox`の暗号化response snapshotを返し、counterを再更新しない。
認証失敗responseへpassword/username存在情報を返さない。

### 4.2 Logout

1. WebがIF-002を送信し、APIは`context_hash`で有効sessionをrevokeする。
2. 既にrevoke済みなら`0200`と元の`revoked_at`を返す。
3. API成功/冪等成功後、WebはHTTP session rowとcookieを破棄する。
4. MQ/API障害時もWeb sessionを破棄し、暗号化contextを`pending_context_revocations`へ保存してrecovery taskが再送する。

`ContextRevocationRetrier.retryDue(Instant now, int limit)`はdue rowを`FOR UPDATE SKIP LOCKED`で最大100件取得し、成功またはAPI expiry確認後だけ削除する。

SSC-011: LOGREQ01は通常のactive context verifierを前置しない。失効専用serviceが同じraw hashでUser→sessionの順にlockし、既失効ならaccount状態/期限に関係なく元の失効時刻と0200だけを返す。この経路からactorを業務認可へ渡さず、idle延長もしない。未失効はaccount ACTIVEかつexpires_at>nowだけをLOGOUTへ更新し0000、未知/期限切れ/無効accountは0102、DB障害は9000。初回・冪等成功の監査もcaller transactionに参加する。

## 5. 参照・検索処理

| Service.method | 入力 | 戻り値 | Transaction/例外 |
|---|---|---|---|
| `ScenarioQueryService.search` | `ScenarioSearchQuery` | `PageResult<ScenarioSearchItem>` | `@Transactional(readOnly=true)`、COUNT後page補正、display_order順 |
| `ScenarioQueryService.findScenario` | file ID | `ScenarioDelivery` | read-only。200 record超はLargeResultWriterを呼ぶため短いread snapshot＋file生成へ分離 |
| `ScenarioQueryService.findSpeakers` | optional game | `List<SpeakerItem>` | read-only、出現件数desc/name asc |
| `MediaQueryService.describeAudio/Video/Music` | context、logical ID、disposition | `MediaDescriptor` | read-only、DB metadata＋root/file検証。対象なし404 |
| `LogQueryService.search` | ADMIN context、filters | `PageResult<LogItem>` | read-only、roleをservice先頭で再検証 |

Scenario large-resultはDB cursor/rowをfileへ書く間に長時間transactionを保持しない。必要な表示snapshotをread-only transaction内で
最大10,000件へmaterializeし、commit後にfile生成する。上限超過は`9001`、途中I/O失敗は`.part`を即時best-effort削除し、
削除できない場合だけ朝清掃に残し503とする。

## 6. User管理更新

### 6.1 Method

| Method | Command | 成功結果 | Lock/監査 |
|---|---|---|---|
| `UserCommandService.create` | username、password、role、enabled、token | ID/version | username UK、operation HMAC、ACTION/SECURITY |
| `UserCommandService.changeStatus` | target、enabled、expected version、token | new version | target row＋active ADMIN advisory lock |
| `UserCommandService.changeRole` | target、role、expected version、token | new version | target row＋active ADMIN advisory lock |
| `UserCommandService.resetPassword` | target、password、expected version、token | new version | target row、全auth session revoke |
| `UserCommandService.unlock` | target、expected version、token | new version | target row、counter/window clear。非lockは0200 |

全methodは`@Transactional`、`InboxCoordinator`内で実行し、`app_users.version = expectedVersion`の条件付きUPDATEを使用する。
Critical audit INSERT失敗は全更新をrollbackする。

### 6.2 Active ADMIN保護

ADMIN membershipを減らし得る操作は同じtransactionで固定advisory lockを取得し、active ADMIN行を`FOR UPDATE`後、更新後も1件以上を
確認する。自己無効化・自己role解除はrow更新前に`0105`。Concurrent操作は直列化し、画面button非表示を正本にしない。

## 7. 質問受付・Outbox

### 7.1 Application method

`QuestionCommandService.submit(AuthenticatedActor actor, SubmitQuestionCommand command, RequestMetadata metadata)`は
`QuestionAcceptedResult`を返す。単一PostgreSQL transactionで次を確定する。

1. Owner＋operation tokenのinbox/fingerprintを検査する。
2. `questions`へ本文・public receipt IDをINSERTする。
3. `async_jobs`へ`RECEIVED`、request Message ID/correlationをINSERTする。
4. `notifications`へ`ACCEPTED/RECEIVED`をINSERTする。
5. `mq_outbox`へ`QWKREQ01` PENDINGをINSERTする。
6. `request_inbox`へresult referenceを設定しCOMPLETEDにする。

Commit後、`OutboxDispatcher.dispatchUntilConfirmed(messageId)`がinternal Queueへのpersistent send確認を行う。UI 213/236に従い、
受付responseは対象outboxがSENTになった後だけ返す。2秒内に確認できなければWebへ`9000`を返すが、DB受付は残る。同じtoken再操作は
dispatcherを再確認し、SENTなら既存受付IDを`0200`で返す。

### 7.2 Outbox dispatcher

| Method | 契約 |
|---|---|
| `OutboxRepository.claimDue(limit, ownerId)` | PENDING/ERROR due rowを`FOR UPDATE SKIP LOCKED`でclaim、lease owner/時刻を記録 |
| `OutboxDispatcher.send` | Destination allowlist、body decode再検証、`_AMQ_DUPL_ID=message_id`でpersistent send |
| `OutboxRepository.markSent` | Send commit確認後SENT。Crashで未更新なら同Message IDを再送 |
| `OutboxRepository.markRetry` | attempt、next_attempt、bounded error code。本文/secretを保存しない |

## 8. Async worker・取消競合

### 8.1 Worker

```text
QWKREQ01 receive
 -> body/DB ID照合
 -> begin DB transaction
    SELECT job FOR UPDATE
    CANCELLED/COMPLETED/ERRORなら冪等ACK対象
    RECEIVEDならPROCESSINGへCAS、processing_message_idを保存
    PROCESSINGかつ同Message IDならcrash recoveryとして再開
 -> commit
 -> AnswerProvider.answer(question)  # 初期STUB、外部通信なし
 -> begin DB transaction
    INSERT answers ON question UK
    job/notification COMPLETED、日時、retry count更新
    audit
 -> commit
 -> JMS commit/ACK
```

`QuestionWorkerService.process(QuestionWork work, DeliveryMetadata delivery)`は`WorkResult`を返す。STUBは空文字と現在時刻だけを返し、
質問本文をlogしない。既存answerが同questionにあれば内容/Provider/日時を照合し、同一なら冪等完了、矛盾なら一時再試行せず整合errorへ送る。

### 8.2 取消

`QuestionCommandService.cancel(actor, notificationId, operationToken)`はownerを先に絞り、次を同一transactionで行う。

```sql
UPDATE async_jobs
SET state='CANCELLED', cancelled_at=:now, state_changed_at=:now, version=version+1
WHERE id=:jobId AND owner_user_id=:actorId AND state='RECEIVED';
```

- 更新1件: notificationもCANCELLEDへ更新し成功。
- 更新0件＋現state CANCELLED: `0200`。
- 更新0件＋PROCESSING/COMPLETED/ERROR: `0107`と最新状態。
- Owner不一致/不存在: `0104`。ADMINも通知取消は本人分だけ。

WorkerのRECEIVED->PROCESSINGも同じjob rowの条件付きUPDATEで競合させ、commit先着だけを有効にする。

## 9. Worker最終失敗・DLQ

| 状況 | Transaction/結果 |
|---|---|
| Temporary failure、delivery count 1～3 | DB業務更新rollback、retry_count/error codeだけ独立短transactionで記録可能。JMS rollback |
| Delivery count 4、DB更新可能 | job/notification ERROR＋DLQ用mq_outboxを同一DB transactionでcommit。DLQ send確認後、元JMS message commit/ACK |
| Delivery count 4、DB障害 | JMS rollback。Broker設定上限でDLQ routeされ得る。復旧後353のDLQ整合を必須実行 |
| STUBの予期した業務error | job/notification ERRORをcommitし、JMS ACK。Broker DLQへは送らない |
| 恒久protocol error | 業務DB未更新。JMS local txでDLQ send＋元ACK、commit後process exit |

## 10. 質問・回答検索・削除

| Method | Scope | Transaction |
|---|---|---|
| `QuestionQueryService.search` | USER本人、ADMIN全件 | read-only。`is_deleted=false`共通predicate |
| `QuestionQueryService.detail` | USER owner、ADMIN全件 | read-only。非scopeは404 |
| `QuestionCommandService.logicalDelete` | USER owner、ADMIN全件 | Question/answer flag・日時・actor、audit、inboxを同一transaction |

重複論理削除は同owner scope内なら元`deleted_at`を`0200`で返す。Notificationを更新・削除しない。Notification detailはquestion
削除flagを見て本文/answerをSELECT projectionへ含めず削除済み表示にする。

## 11. Web REQUEST log投影

1. `HttpRequestLoggingFilter`はrequest開始時にrequest IDとnano timeを設定する。
2. Response commit直前にstatus/elapsedを確定し、まずlocal JSONへ1行記録する。
3. Technical DB transactionで暗号化済みWLGEVT01 payloadを`web_log_outbox`へINSERTする。
4. `WebLogDispatcher`がpersistent sendしSENTへ更新する。
5. `WebLogIngestService.ingest`は`app_logs.source_message_id` UKを用いてINSERTし、重複は更新せずACKする。

Web technical DB障害でoutbox INSERTできない場合も利用者responseを置換せず、local JSONに`projectionStatus=FAILED`を記録してalertする。
Critical auditはAPI transaction内のDB logを正とし、このbest-effort HTTP投影に依存しない。

## 12. Error mapping

| Exception/classification | DB | JMS | Fixed result/HTTP |
|---|---|---|---|
| Form/field validation | 未送信 | なし | 400相当、field error |
| `BusinessRuleException` | Commandによりcommit/rollback | Reply後commit | 0100～0107 / 400,401,403,404,409 |
| `CapacityExceededException` | 受付/生成しない | Reply後commit | 9001 / 503 |
| `TemporaryInfrastructureException` | rollback | delivery count内rollback | 最終で9000またはDLQ整合 |
| `PermanentProtocolException` | 業務未実行 | DLQ send＋元ACK commit | Responseなし、process非zero終了 |
| `StartupInvariantException` | なし | Consumer開始しない | Readiness false、unit failed |

Exception messageを利用者へ直接表示しない。Result code、error/action catalogは351を正とする。

## 13. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-004 | JMSはtransacted sessionのcommitでACKを制御する | UI 231のtransacted/manual ACKをJMS仕様上矛盾なく具体化 | ITでreply send/ACK crash pointを注入 |
| SS-D-005 | Async workerのPROCESSING recoveryは同一Message IDを処理所有記録として再開する | UI 213 §9。Business timeout/leaseを追加しない | `processing_message_id`をDDL/worker PTへ追加 |
| SS-D-006 | Web REQUEST投影失敗は利用者処理をrollbackせずlocal JSONを継続する | UI 212/252。Critical auditはAPI transaction内で別保証 | 投影滞留alert、IT再送試験 |

## 14. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | 主要sequence、method契約、transaction/crash matrixを初版作成。 |
| 2026-08-31 | 横断監査でLogin失敗counterを含む匿名Inbox transactionとlarge-result中間file清掃を整合。 |
