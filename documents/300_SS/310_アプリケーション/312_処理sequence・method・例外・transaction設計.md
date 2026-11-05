# 処理sequence・method・例外・transaction設計

## SSC331 ordinary local audit callback graph（2026-10-22）

§11のprimitive local logger Runtime故障は通常記録成功へ戻さず、既固定onTerminalを一回試みる。Runtime内のcause/suppressed/JMS linked/SQL nextに到達可能なErrorは、通知を試み終えた後に既WebStartupExceptionのpure finite graph portで同一objectを伝播し、falseへ縮退しない。直接logger Errorの既即伝播/通知0は変更しない。

onTerminalがRuntimeを投げた場合はそのcallback graphを先に分類し、非fatalなら保持したlogger Runtime graphも分類する。いずれかのErrorを元objectで伝播し、両方非fatalの場合だけ従来固定IllegalStateException（cause/suppressedなし）とする。直接callback Errorの既優先/通知一回は維持する。同一/alias/cycleを有限に扱い、provider graphをcatalog/local JSON/alertへ保存しない。owner通知前にlogger graphをthrowして必要通知を省略せず、通知やloggerを再試行しない。

通常metadata/PENDING/FAILEDのJSON code、owner/DB/JMS/identifier発行回数、HTTP status/body/header、wire/再送/認可・DIFは不変更。SQL projectionのSSC329と独立にこのlocal境界を確認する。BUG1601/YKT1354、351/354、実VM/Root/cohort/permit操作の承認追加なし。

## SSC330 ordinary readiness graph・pure secondary保持（2026-10-22）

ordinary API/Webのreadinessは、Connection/JMSContextのowned closeを一回試みた後で通常startup catalogを返す前に、cause/suppressed/JMS linked/SQL nextのfinite graphをidentity visitedで分類する。到達可能なErrorは元object、非fatal循環は有限帰還し、provider graphを新catalogに保持しない。既manual cleanupの直接primary Error/直接close Errorの選択を先に維持し、捨てていた非fatal型secondaryも同scopeのprimary graphへ一時連結する。wrapped Errorをその型だけでnonfatalと断定しない。

共通pure分類/secondary attachmentはAPI内のTemporaryInfrastructureException、Web内のWebStartupExceptionへ置く。Auth既suppressed優先/Session既JDBC専用portを無関係に変更せず、bootstrap/protocolへのJMS依存追加やWeb→API依存を行わない。attachmentはprimary/secondaryのnull契約を検査し同一objectならself-suppressionを行わず、別objectだけaddSuppressedする。suppression無効で連結できない場合はprimary graph、次にsecondary graphを分類してErrorを失わない。途中でfatalが伝播してもcallerのfinally/TWRで残るowned closeを完了させる。既SS329 API ownerへの再利用は各呼出/同source品質へ追跡し、close成功/rollback成功を捏造しない。BUG1593/YKT1346、既SQL部分は1592/1345と同一siteで二重費/二重受入なし。

## SSC329 ordinary JDBC fatal保持・owned transaction（2026-10-21）

SQLException/RuntimeExceptionを固定catalogや業務SQLstateへ変換する前に、捕捉したfinite exception graphのcause/suppressed/SQLException.nextへ到達可能なErrorを元objectで伝播する。非fatal graphはidentity visitedで有限帰還し、provider text/cause/suppressedを新catalogへ保持しない。ordinary APIの共有分類はapi.error.TemporaryInfrastructureExceptionのpure static portへ置き、API内で再利用する（新module/GAV/権限依存なし）。既Authのsuppressed優先とWeb/sessionのcause優先はSSC328を維持する。Web内部の同分類は既SessionStoreException portを使い、production Web→API依存を追加しない。

owned transactionはhandler/commitのSQL・Runtime・Error失敗時にrollbackを一回試み、owned connection closeも一回完了させてから結果を返すか失敗を伝播する。rollbackのSQL/Runtime/Errorは元primaryへ同一object以外だけ一時attachし、直接primary Errorのidentity/優先を維持する。TWRが同一Throwableのself-suppressionを別例外へ包んだ場合も、そのcause内Errorを通常catalogへ縮退させない。commit後close失敗はcommitを取り消せたことにせず、応答/ACKの成功を返さない。borrowed repositoryはConnectionのcommit/rollback/closeを新しく所有せず、既Statement/ResultSet closeの後に変換前fatal分類を行う。既通常catalog/SQL/更新数/DB role/再送・DIFは不変更。BUG1592/YKT1345、実原本DB/Root/VM/cohort/keysへの操作権限を追加しない。

SSC156（2026-10-02、Worker実装前）：retry_countはmin(actual count-1,3)、実delivery metadataは非cap。AnswerResult.answeredAtの有限UTCµsをstarted/received以上で検査し、answer/job/notificationの同完了stampへ使用、wireだけms。通常最終ERRORは既存DのSENT後だけ元ACK。ERROR+D commit～元ACKにhard crash/session rollbackが起きると、固定Broker max4が元WをDLQ移動し、startup dispatcherのD送信と2物理コピーになり得る。双方を同Wの論理隔離として保全し、353 §7.2で個別照合/承認整理する。ERROR時のprovider再実行、新D生成、ordinary W proof変更は禁止。停止要求でD未確認の待機を解く場合は正常復帰せずrollbackする。shared stop→consumer drain/close→Outbox join→DB/factory/key/root closeの所有順を守り、待機中DB/JMSを保持しない。

PG/PT内部接続補足（SSC153154155、2026-10-01、実装前）：普通APIは31 requestとQWK/WebLog、全3consumer、専用Outbox lifecycleを実接続するまでready/A releaseを許さない。共通event portはguard検証済みactual delivery count・bounded transport ID・UTC受信時刻をQuestionへ渡す。Questionのcount-less呼出しをdelivery1と推測しない。

QSBの元request ID M0はInbox source/async_job message_id/correlationであり、内部QWKの新UUID Wとは別。受付transactionはquestion/job/notification(type ACCEPTED/state RECEIVED)/PENDING work/QUESTION-bound NKREF1 success snapshotを一度だけcommitする。再送snapshot AADはM0、返信は新UUID/今request correlation、payload/受付時刻は保存値。応答成功は当該workの真正SENT確認後だけ。単調budgetはheader.sentAt+2秒と受信clock+2秒の早い期限の残量を受信時に固定し、既に遅い要求は受付前9000。commit後timeoutもfresh9000で既存COMPLETED/保存期間を変更しない。専用dispatcherへwakeし、DB connection/lockなしで残時間内に対象SENTを短い再観測する。共通processorをrequest thread内のJMS sendへ変えない。

7日mutation Inbox保持後、retained question owner/tokenは永久重複防止を維持する。decoded canonical本文が異なる場合0105、同じでも元認証snapshotとSENT根拠がない場合9000とし、新question/job/work、Inbox alias、推測完了時刻を作らない。通常8時間tokenの再送契約は変更しない。Workerはanswer作成transaction内でquestion rowをlockし削除flag/時刻/actor三点をanswerへ継承する。

最終一時失敗4回以降の業務DLQはdispatch UUID Dを新Outbox rowへ保存し、元QWK W/body/correlationを保持する。固定SS321 metadataをimmutable専用列へ保存、DB ERROR＋DLQ row commit→DのSENT→元ACK。ERROR再配送でDLQ PENDINGならACKせず確認を継続する。既存work SENT rowの書換え、duplicate W INSERT、未送信を成功化する代用を禁止する。STUB業務ERRORとprotocol fatalの既存別経路は維持する。UI213のFIFOは内部Queueの到着順であり、資料にない全利用者の受付timestamp順保証は追加しない。

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

`ContextRevocationRetrier.retryDue(Instant now, int limit)`はdue rowを`FOR UPDATE SKIP LOCKED`で最大100件claimし、唯一lease UUID/期限を確定して短DB transactionを閉じてからJMSへ送信する。更新/削除は自分の現在leaseをCASし、検証済0000/0200だけを自動削除根拠とする。expires_at=NULL/推測期限/一般0102/不明/復号不能は保持・警告。初期5秒/30秒/5分後は15分、attempt_count=100飽和後も継続し、IT/ST性能問題時に間隔を見直す（QA050、SS314 §10）。JMS待機中にDB接続/lockを保持しない。

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

SSC-031（管理更新の認証前lock prelude）: UCR/UST/URL/UPW/ULKは通常verifyを最初に呼ばない。context hashの候補user IDを非lockingでlookupし、減員し得るUST無効化/URL USER化だけadvisory 71419601を取得する。その後、候補actor、target（作成はなし）、減員時の全active ADMINを一つのSELECTでUser ID昇順FOR UPDATEする。当該context sessionをlockし、ownerが候補と同じことを確認してから通常verify（有効性/最新role/idle更新）とADMIN認可を実施し、続いてInbox/業務commandへ入る。候補lookupだけを認証許可にしない。Owner変化/不整合はrollbackする。すべて同じcaller write transactionであり、取得済みactor/targetをcommandが再lockしても順序を逆転しない。UCRは既存actorを先にlockし新UserをINSERTする。非管理・参照requestの既存verify順は変更しない。

### 6.1 Method

SSC-034（拒否監査のidentity境界）: `AdminCommandAuthenticator.verifyIdentity`はSSC-031の候補lookup/必要advisory/User昇順/session再照合/通常verifyを同じcaller write transaction内で完了し、最新DB identityを返す。候補IDのまま返さず、USERをADMIN許可にしない。旧verifyはこのidentity取得後に既存ADMIN認可を行う互換wrapperとする。

`UserMutationApplicationService`はidentity取得後にADMINを判定し、USERなら351のAUTHORIZATION_DENIED/SECURITY（actor/role/layout/最小target/result0103）を同transactionへ記録してcommitし、Inbox/業務へ入らない。認証失効0102はactorを推測せず欠落として最小拒否監査し、Inbox/業務へ入らない。拒否監査INSERT/close/commit不成立を拒否完了にせず9000型で再試行対象とする。

ADMINは7日保持のowner/token/HMAC Inboxから新規だけUserCommandServiceへ入り、User/全session失効/critical audit/暗号結果を一括commitする。保存replayはPG-D-086のref/version/暗号検証を同transactionで完了し、INBOX_REPLAYED監査を追加する。Token payload不一致は既存結果を返さず0105/SECURITY WARNを記録し新Inboxを作らない。同Message異identityはPROTOCOL_REJECTED監査を確定してから恒久protocol拒否を通知する。DB/監査異常は全rollback、一度commit済みの結果はJMS reply/send/ACK失敗後も再更新しない。

ResponseはDB commitとConnection closeが正常完了した後だけ新ID/correlation/context/時刻で構築する。User更新/確定業務error以外の0102/0103/異token0105はresponse snapshotへ保存せず、再受信時に最新認証/HMACを再評価する。外側JMS listenerがreply送信とACKを所有し、このserviceはJMSをcommitしない。HTTP・全layout登録/起動・IT/STは別gate。

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

SSC-173: 送信body byteはWeb originのcharset変換後に成功したcontent writeを終端で観測し、HTTP headers/transfer chunk framingは除外する。実Tomcat11.0.25は`response.getCoyoteResponse().getContentWritten()`（Coyote doWriteのByteBuffer消費byte）を使い、transport framing込み`getBytesWritten(false)`やServlet char混在counterを使わない。読取によるforce flush/応答変更なし。切断時も既知のsuccessful origin writeを記録するだけでclient受信ACKを保証せず、Caddy後段変換もorigin値へ混入しない。

1. SSC-172: `HttpRequestLoggingValve`を実Tomcatの`AccessLog` terminal hookへ接続し、request開始時にserver UUIDだけのidentityをCaddy検証前に確立する。HTTP header/form/queryからidentityを採用しない。verified Caddy transportと認証済actorの安全なusername/roleだけを別にrequest lifetimeへ投影し、raw context/principal/session/token/passwordは保持しない。
2. UI252 §2/UI235 §12.1/351 §2どおり、通常/HEAD/ERROR/ASYNCの応答終端で最終status/elapsed/送信body byte数を確定し、同event Message IDでまずlocal JSONへPENDING観測を記録する。commit直前やServlet finallyだけで後続ERROR/ASYNC・stream総byteを推測しない。導入Tomcat11.0.25のterminal callbackとnano-time差を使用し、byte読取による強制flush/response変更を行わない。
3. Technical DB transactionで暗号化済みWLGEVT01 payloadを`web_log_outbox`へINSERTする。
4. `WebLogDispatcher`がpersistent sendしSENTへ更新する。
5. `WebLogIngestService.ingest`は`app_logs.source_message_id` UKを用いてINSERTし、重複は更新せずACKする。

Web technical DB障害でoutbox INSERTできない場合も利用者responseを置換せず、local JSONに`projectionStatus=FAILED`を記録してalertする。
Critical auditはAPI transaction内のDB logを正とし、このbest-effort HTTP投影に依存しない。

SSC-172: FAILED補足は最初のlocal PENDING観測と同event IDで結合する投影失敗の記録であり、別の業務HTTP eventや再送UUIDを生成しない。SQL/codec/commit/closeの未知結果も成功へ変更せず、provider文面・Throwable・秘密をlocal/alertへ渡さない。local出力自体の失敗は正常記録として扱わず、固定terminal signalで同Web ownerへ知らせる。投影failureでHTTP status/body/headerを書き換えたり、HTTP threadでJMS再送・業務DB操作を行わない。

処理中の最初の業務MQ Message IDだけを既存fixed wire clientのidentifier supplierからrequest-scoped traceへ結合し、後続probeで上書きしない。MQ呼出なしはUI235の規則どおりCorrelation ID=event Message IDとする。lexical request scopeはnested/ASYNC/並行で混線せず終了時に解除し、background送信・別requestへidentityを継承しない。unknown routeは固定`/**`、ログpathへraw URI/query/fragmentを複写しない。未知transport/null/malformed callbackはsafe local UNKNOWN/固定alertとし、WLGEVT01必須のverified IPや成功statusを捏造しない。NPEをcatchして正常化しない。

既存WebLogPayloadCodec/OutboxRepository/Dispatcher/ReplayWorkerとAPI DB UKを再利用し、鍵/DB/JMSは外側ownerの所有を維持する。HTTP drain→worker join→reply consumer→外側DB/JMS/鍵という停止順、SS342のfull business readinessを省略しない。REQUEST producer単独成功で全Web ready/CHR/native coverage・正式品質を完了にしない。独立JSON/2336-byte golden/AAD/JCE、実HTTP正常・HEAD・ERROR・ASYNC・拒否・切断、SQL/codec/local失敗時のHTTP不変、100並行/再送、静的/全対象4coverage・同Source nativeを検証する。

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

## QA-054 メニュー・ログ検索の成功ACTION（SSC-336、2026-11-05承認）

1. MenuControllerの認証済みUSER/ADMINのメニューGET成功をrequest lifetimeへ明示し、§11の実応答終端で成功を確認した場合だけMENU_VIEWED/ACTIONを一度生成する。HEAD・別画面・認証/権限拒否・失敗を成功閲覧へ補正しない。REQUESTも従来どおり別eventで一度記録し、両者をHTTP request IDで結合する。各event IDをlocal→technical outbox→API UKで保持する。HTTP結果不変更・metadata安全化・worker/外側owner順序は§11のまま。
2. APIの初回成功ログ検索は、結果snapshot取得後、業務成功・Inbox/再送用結果の確定と同じtransactionでLOG_SEARCHED/ACTIONを一度保存する。監査INSERT失敗はそのtransactionをrollbackする。保存済み応答の再送では結果を返し、検索業務/成功ACTIONを再発行しない。失敗・role拒否に成功ACTIONを生成せず既存拒否監査を維持する。INBOX_REPLAYEDとは区別する。
3. 検索応答snapshotと後発監査確定のDB後条件を分け、自己の監査行が検索応答に現れないことを許容する一方、後条件では成功ACTION 1件を要求する。query値・秘密・raw contextを保存しない。実装/単体試験/CHR/正式受入は本設計反映とは別に未完。
