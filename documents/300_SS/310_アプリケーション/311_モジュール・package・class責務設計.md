# モジュール・package・class責務設計

SSC-049/PG-D-151: batch.platform.InspectorStaticEnvironmentはSS343 §6.8の静的2行fileをMap化前に検証する非秘密byte境界。DB connectorや秘密鍵をbatchへ持込まず、子API launcherの値検証と両側で同じSSを満たす。file属性/読取/公開の責務はbatch.file、子起動と同run確認は親platformへ分離する。NK-OPS-001、OPS-009/UI251、PT-OPS-CFG-001～006。

SSC-049/PG-D-150（先行0797b369）: batch.cleanup.InspectorLockHandoffはSS341 §7.3の親Connectionのadvisory解放・同期callback・finally再取得だけを担う。借用transaction/connectionのcommit/rollback/close、実process/OS lock/backup/run原本には責務を広げない。NK-BAT-001、OPS-009、UI251、PT-BAT-030～037。JDBC scalar/資源終了の固定診断と未知programming failureの非成功を検証する。

SSC-049/PG-D-149（2026-09-09、先行17b06c0c）: batch.platform.InspectorRunEnvironmentはSS343 §6.8のrun専用EnvironmentFileのcanonical ASCII生成・期待runとの全byte照合だけを担う。BatchRunの検証契約を再利用し、時刻取得・file IO・root/lock/backup/起動・永続原本の確定を行わない。NK-OPS-001、OPS-009、UI251、PT-OPS-ENV-001～004へ追跡する。

SSC-049/PG-D-148: batch.platform.ApplicationStopGateはAPI/Webの固定2unitをread-only照会し、UnitStateParserの厳密な7property契約で停止を確認する。SystemctlStateSourceだけが固定systemctl show・制限環境・5秒/1024byte境界を所有する。停止/起動や任意unit/commandの実行入口を追加しない。親OS lock/再起動禁止/実backup/DB引渡しは別責務で、観測結果を永続的な停止leaseとして扱わない。

SSC-049/PG-D-147: batch.file.MaintenanceFileLockはroot controller内部だけの固定runtime admission adapterとする。storageの保持directory/inode/実Linux flockを借用し、固定/run配下の所有・型・mode・ACL・local tmpfs・identityを確認した保守callbackをOS lock下で実行する。公開factoryにpath/UID/commandを渡す入口を作らない。batch→storage依存を追加しAPI/Webへの逆依存は禁止。停止/backup/DB排他引渡しを低位lock取得結果だけで代替しない。

SSC-028: Shared storageの既存保持directory/inodeへ、Asset adapter向け既存child/entryのread-only能力と正サイズfile属性照合を追加する。Transfer専用UUID/date/48MB入口は維持し、API/Webのnative実装複製やProtocolからfile I/Oを行わない。詳細はSS333 §7.2、PG-D-073/PT-MED-018～020。

## 1. 目的・追跡

SSC-027具体化: `.api.application.scenario.ScenarioApplicationService`がSyncRequestProcessorとして内部段階処理を所有する。process/decode/guard→inspect（非更新認証/Inbox/query）→prepare（DB外file）→complete（再認証/通常Inbox/必要時descriptor暗号置換）→commit/close後replyの順。Private sealed Work/Preparedで新規query・確定error・既存snapshotを区別し、repository/storage実装を同classへ複製しない。JMS send/ACKは既存SyncRequestListener、root/鍵closeは起動所有者。single-instance/full root/readinessを実装するまで本番dispatcherへ登録しない。PT-SCN-009-T01～T07。

Web Java、API Java、batch、固定長共通部品のMaven module、package、主要class、責務および依存禁止を定める。

- 関連UI: 211～213、221～237、241～243、251～253、261 SS-001/007～013
- 関連RD: SYS-002、SYS-005～011、MQ-001～045、DAT-001～011、OPS-001～005
- 関連QA/RDF/UIC: QA-001～040、RDFなし、UICなし

## 2. Maven module

| Module/artifact | 実行形態 | 責務 | 依存可能 | 依存禁止 |
|---|---|---|---|---|
| `schubert-nk-protocol` | Library jar | 256 byte header、64 layout record、codec、NFC/byte検査、共通result/error、descriptor model | Java標準API、test時だけJUnit | Spring MVC、JMS、JDBC、DB entity、HTTP model |
| `schubert-nk-storage`（SSC-021） | Library jar | Linux保持directory/inode、NOFOLLOW・非上書き公開、OS属性/root配置の低位契約 | Java25標準NIO/FFM、null annotation、testだけJUnit | Protocol業務model、Spring/JMS/JDBC、HTTP/DB model、認証・Inbox・quota業務 |
| `schubert-nk-web` | Executable jar | MVC/Thymeleaf、HTTP validation、Spring Security、暗号化HTTP session、JMS request/reply、file配信、Web log outbox | protocol/storage、Spring Web/Security/JMS/JDBC | 業務schema repository、業務状態更新、API module |
| `schubert-nk-api` | Executable jar | 固定長request Consumer、認証・認可、application service、PostgreSQL業務schema、outbox/inbox、async worker | protocol/storage、Spring JMS/JDBC/Security crypto | MVC/Thymeleaf、Browser response、Web technical table更新 |
| `schubert-nk-batch` | Executable jar/oneshot | Backup検証、business/technical cleanup、transfer cleanup、Expiry保守、run記録 | Spring JDBC、PostgreSQL/Artemis管理client | HTTP公開、業務Consumer、任意table/Queue操作 |
| Root project | Aggregator | Maven Wrapper、Java 25 toolchain、dependency/version、品質plugin | 上記module | Production sourceの直置き |

Group IDは`dev.codex.schubert`、Java package rootは`dev.codex.schubert.nk`とする。Java module systemの`module-info.java`は
Spring reflectionとの運用複雑性を避け初期releaseでは使用しない。Mavenのmodule依存とArchUnitで境界を検査する。

## 3. 共通依存規則

```text
schubert-nk-web   ─┐
                   ├──> schubert-nk-protocol
schubert-nk-api   ─┘

schubert-nk-batch      （protocolへ依存しない。Expiry message本文をdecodeするDLQ整合toolだけは
                         protocolを明示dependencyとして利用可）
```

- WebとAPIは互いにcompile/runtime依存しない。
- SSC-021: Web/API/batchのfile adapterだけがstorage libraryへ依存可能。Controller、application/domain、Protocolからstorageへの依存を禁止する。API/Web間のclass複製やProtocolへfilesystem実装を移す方法は採らない。既存API `.api.storage`から純粋な低位7classを`.storage`へ移し、業務writer/record codec接続/quota/readiness wiringはAPIへ残す。Native SPIのFD整数を公開service/HTTP/DB/電文/ログへ渡さない。
- Protocolは外部frameworkから独立させ、同一jar hashをWeb/APIで使用する。
- HTTP form/view model、DB row/entity、固定長layout recordは別classとし、mapperで変換する。
- `controller -> web application facade -> messaging adapter -> protocol`の向きだけを許可する。
- APIは`messaging adapter -> application service -> domain/persistence/file adapter`の向きとし、repositoryから上位層を呼ばない。
- Batchはallowlist済みrepository/functionとOS command adapterだけを使用し、API serviceを流用して公開処理を起動しない。

SSC-021の依存補足: Web/APIはprotocolとstorageをそれぞれ参照し、両libraryは互いにも依存しない。Batchは承認済み保守file操作に限りstorageを使用できる。Executable process数、HTTP/JMS経路、業務DB権限は変更しない。

Storage package `.storage`はDirectoryCalls/LinuxDirectoryCalls、OwnedTransferDirectory、StorageIoException、StorageIdentity、StorageAttributeGuard、StorageRootLayoutを持つ。Class/operationはfile adapterから使える公開契約へ限定して可視化し、native symbol binding・entry FD実装・状態lockをprivateに保つ。必要なnative accessは利用processへ明示設定し、起動時にfail closedで検証する。

## 4. `schubert-nk-protocol`

SSC-049/PG-D-133: storageへ低位InodeSecurityCalls/LinuxInodeSecurityを追加し、保持inode callback内のaccess ACL/readonly filesystem flag/effective UIDだけを公開する。業務認証やkey内容を扱わず、APIのcredential file adapterがSS343 §6.2のpolicyと組み合わせる。任意path・symbol・attribute名を受けず、native実装をAPIへ複製しない。検査processも明示native-accessを必須とする。PT-DB-INBOX-121～128。

SSC-049/PG-D-146: storageのLinuxFileLockは保持済みregular inodeへの低位scoped flockだけを担当し、batch file adapterから利用する。呼出しは保持callback中の固定/proc/self/fd能力と閉じた業務callbackに限定。任意pathや生FDをserviceへ公開せず、OS user/ACL/root/実backup/DB transactionはbatch側の別責務。FFM bindingはshared storageへ集約、FileChannel.lock/fcntlをflockの代用にしない。PT-OPS-FLOCK-001～008。

### 4.1 Package

| Package | 主要class | 責務 |
|---|---|---|
| `.protocol.header` | `CommonHeader`, `MessageKind`, `InteractionKind`, `ResultCode` | 共通headerの型安全な表現 |
| `.protocol.layout` | `LayoutId`, `LayoutDefinition`, `LayoutRegistry`, `LayoutPayload` | Layout ID/version、data/record長、最大件数、Q/S/E制約 |
| `.protocol.layout.auth` | `LoginRequest/Response`, `LogoutRequest/Response` | IF-001/002のlayout record |
| `.protocol.layout.scenario` | `Game*`, `Speaker*`, `Scenario*`, `Route*`, `ScenarioFile*` | IF-003～008 |
| `.protocol.layout.media` | `Audio*`, `Animation*`, `Music*`, `MediaDescriptor` | IF-009～016 |
| `.protocol.layout.log` | `LogSearch*`, `WebLogEvent` | IF-017、IF-I02 |
| `.protocol.layout.admin` | `User*` | IF-018～024 |
| `.protocol.layout.question` | `Question*`, `Notification*`, `QuestionWork` | IF-025～031、IF-I01 |
| `.protocol.codec` | `FixedWidthEncoder`, `FixedWidthDecoder`, `HeaderCodec`, `PayloadCodec`, `FieldCodec` | byte列との相互変換 |
| `.protocol.validation` | `ProtocolValidator`, `FieldValidator`, `Utf8Validator`, `LayoutValidationException` | 構造・型・必須・許容値の受信前検査 |
| `.protocol.file` | `LargeResultDescriptor`, `LargeResultRecordCodec`, `MediaDescriptorValidator` | Transfer/media descriptorの構造検査 |
| `.protocol.time` | `JstWireTimestamp` | 17桁JST日時のparse/format |

`LayoutPayload`はsealed interfaceとし、各data/recordをJava `record`で定義する。Record constructorはnull、range、enumを検査するが、
encode後byte長は`FieldCodec`を正とする。`LayoutRegistry`は64 layoutを起動時に登録し、ID重複、長さ式、最大body 1,000,000 byteを
検査する。

### 4.2 Codec class

| Class.method | 引数 | 戻り値 | 例外 |
|---|---|---|---|
| `FixedWidthEncoder.encode` | `WireMessage<? extends LayoutPayload>` | `byte[]` | `MessageEncodingException` |
| `FixedWidthDecoder.decode` | `byte[]`, `TransportMetadata`, `ExpectedRoute` | `WireMessage<?>` | `PermanentProtocolException` |
| `HeaderCodec.peek` | 256 byte以上のbody | `CommonHeader` | `PermanentProtocolException` |
| `FieldCodec.encodeText` | value、field definition | 規定長`byte[]` | `FieldEncodingException` |
| `FieldCodec.decodeText` | field slice、definition | `String`/empty | `PermanentProtocolException` |
| `ProtocolValidator.validateTransport` | decoded message、JMS property snapshot | `void` | `PermanentProtocolException` |

JMS classはprotocol moduleへ渡さず、Web/API adapterが必要propertyを`TransportMetadata`へ写して検証する。

## 5. `schubert-nk-web`

### 5.1 Package

| Package | 主要class | 責務 |
|---|---|---|
| `.web.bootstrap` | `WebApplication`, `StartupInvariantValidator` | 起動、layout/root/Queue/session設定検査 |
| `.web.config` | `WebMvcConfig`, `SecurityConfig`, `JmsClientConfig`, `WebProperties` | Framework wiringと外部設定束縛 |
| `.web.controller` | `LoginController`, `MenuController`, `ScenarioController`, `MediaController`, `AnimationController`, `MusicController`, `LogController`, `UserAdminController`, `QuestionController`, `NotificationController`, `ErrorController` | HTTP endpoint、form binding、view選択 |
| `.web.form` | 画面別`*Form`、`*SearchForm` | HTTP入力とfield error。MQ recordを保持しない |
| `.web.view` | 画面別`*ViewModel`、`PageViewModel`, `FlashMessage` | Template表示専用model |
| `.web.mapper` | `ScenarioWebMapper`, `AdminWebMapper`, `QuestionWebMapper` | Form/viewとprotocol recordの変換 |
| `.web.messaging` | `JmsRequestReplyClient`, `ReplyCorrelationRegistry`, `WireMessageFactory`, `ResponseMapper` | Persistent送信、2秒待機、相関、response検証 |
| `.web.security` | `MqAuthenticationProvider`, `AuthenticationContext`, `ApiAuthorizationFailureHandler`, `TrustedClientAddressResolver` | Login MQ認証、context保持、Web側role/owner gate |
| `.web.session` | `EncryptedWebSessionRepository`, `SessionAttributeCodec`, `PendingRevocationRepository`, `ContextRevocationRetrier` | Technical schemaだけを使う暗号化session/Logout再試行 |
| `.web.operation` | `OperationTokenService`, `OperationTokenStore` | UUID発行、用途別最大10件、PRG/timeout時のtoken保持 |
| `.web.media` | `DescriptorFileResolver`, `MediaRangeService`, `LargeResultReader`, `ContentDispositionFactory` | Root/path/hash/Range/file配信 |
| `.web.logging` | `HttpRequestLoggingFilter`, `WebLogOutboxRepository`, `WebLogDispatcher`, `RedactionPolicy` | Local JSON＋WLGEVT01 outbox |
| `.web.error` | `GlobalWebExceptionHandler`, `ProblemViewFactory` | 400/401/403/404/409/416/503の共通表示 |

### 5.2 Controller依存禁止

ControllerはJDBC、JMS template、filesystem APIを直接呼ばない。Controllerからは画面単位facadeを呼び、facadeがmapperと
`JmsRequestReplyClient`を組み合わせる。Media endpointもdescriptor取得をAPIへ要求後、`MediaRangeService`へ委譲する。

## 6. `schubert-nk-api`

### 6.1 Package

| Package | 主要class | 責務 |
|---|---|---|
| `.api.bootstrap` | `ApiApplication`, `StartupInvariantValidator` | 起動、migration/version/root/codec整合検査 |
| `.api.config` | `ApiJmsConfig`, `DataSourceConfig`, `SecurityCryptoConfig`, `ApiProperties` | Consumer、pool、credential、設定 |
| `.api.messaging.inbound` | `SyncRequestListener`, `QuestionWorkListener`, `WebLogListener`, `InboundMessageGuard` | Queue受信、property/body検査、delivery count分類 |
| `.api.messaging.outbound` | `ReplySender`, `DlqSender`, `OutboxDispatcher`, `JmsMessageFactory` | Reply/internal work/DLQ送信 |
| `.api.dispatch` | `RequestDispatcher`, `LayoutHandlerRegistry`, `LayoutHandler<Q,S>` | Request layoutからhandlerへ型安全にdispatch |
| `.api.security` | `AuthenticationService`, `AuthenticationContextVerifier`, `AuthorizationService`, `LoginAttemptRepository` | Password、session、role/owner、lock |
| `.api.application.scenario` | `ScenarioQueryService`, `MediaQueryService` | 現行検索・階層・descriptor query |
| `.api.application.admin` | `UserQueryService`, `UserCommandService` | User管理と自己保護 |
| `.api.application.question` | `QuestionCommandService`, `NotificationQueryService`, `QuestionQueryService`, `QuestionWorkerService`, `AnswerProvider` | 質問、通知、取消、回答、STUB |
| `.api.application.log` | `LogQueryService`, `WebLogIngestService`, `AuditLogService` | Log検索、WLGEVT01投影、critical audit |
| `.api.idempotency` | `InboxCoordinator`, `OperationFingerprintService`, `ReplayResponseFactory` | Message/token重複、HMAC、結果再構成 |
| `.api.domain` | `AsyncJobState`, `Role`, `AccountStatus`, `NotificationType`, domain result | 業務状態・遷移。Framework annotationを含めない |
| `.api.persistence` | 画面/aggregate別`*Repository`、`*RowMapper` | Parameterized SQL、row mapping、lock |
| `.api.file` | `AssetResolver`, `MediaDescriptorFactory`, `LargeResultWriter`, `FileIntegrityVerifier` | Logical IDから許可root内fileを解決 |
| `.api.storage` | `LinuxDirectoryCalls`, `OwnedTransferDirectory`, `StorageAttributeGuard`, `TransferCapacity` | SSC-019のAPI内部filesystem capability/属性/予約会計。`.api.file`の下位技術部品で、Controller/DB/JMS/HTTPへ依存しない |
| `.api.error` | `ApiExceptionMapper`, `RetryClassifier`, `FatalProtocolHandler` | Result code、一時/恒久分類、DLQ後exit |

### 6.2 Handler規約

`LayoutHandler<Q,S>`は`LayoutId requestLayout()`、`Class<Q> requestType()`、`S handle(RequestContext,Q)`だけを公開する。
Dispatcherは認証・inbox処理後にhandlerを呼ぶ。HandlerはJMS ACK/send、HTTP、templateを扱わない。

`RequestContext`はmessage/correlation/request ID、actor user ID/username/role、受信日時、delivery countを保持するが、raw認証context、
password、全bodyを保持・`toString`出力しない。

## 7. `schubert-nk-batch`

| Package | 主要class | 責務 |
|---|---|---|
| `.batch.bootstrap` | `BatchApplication`, `BatchCommandRouter` | `backup`、`cleanup`、`morning-run`等のcommand選択 |
| `.batch.lock` | `MaintenanceLock`, `BatchRunLeaseRepository` | OS lock＋DB run一意性 |
| `.batch.backup` | `PostgresBackupService`, `ConfigBackupService`, `BackupManifestService`, `BackupVerifier`, `GenerationPruner` | `.part`生成、検証、7世代 |
| `.batch.cleanup` | `BusinessDataCleanupService`, `TechnicalDataCleanupService`, `TransferCleanupService` | Backup gate付きDELETE、root安全検査 |
| `.batch.mq` | `ArtemisReadinessClient`, `ExpiryCleanupService` | 限定credentialによる7日超Expiry削除 |
| `.batch.repository` | `BatchRunRepository`, `CleanupRepository` | Allowlist SQL/function、件数証跡 |
| `.batch.logging` | `BatchEventLogger`, `CommandRedactor` | BATCH JSON/DB log、secret除外 |

`ProcessBuilder`へ渡すcommand/argumentは固定allowlistで組み立て、shell文字列連結を行わない。削除serviceは設定root自体を削除せず、
`SecureDirectoryStream`または同等のsymlink非追従検査を使用する。

## 8. Application共通例外

例外classは各moduleの`.error`へ置き、protocol moduleがWeb/API例外へ依存しない。

| 分類 | 例外 | 処理 |
|---|---|---|
| HTTP validation | `WebValidationException` | 同一画面field error |
| 業務 | `BusinessRuleException(resultCode)` | Transaction rollback要否を個別指定し、固定長error response |
| 認証・認可 | `AuthenticationContextException` / `AccessDeniedException` | `0102`/`0103`、deny closed |
| 対象なし・競合 | `NotFoundException` / `ConflictException` | `0104`/`0105` |
| 一時基盤 | `TemporaryInfrastructureException` | rollback、最大3回再配送 |
| 容量 | `CapacityExceededException` | `9001`、受付/生成停止 |
| 恒久protocol | `PermanentProtocolException` | 業務未実行、DLQ、非zero終了 |
| 起動不変条件 | `StartupInvariantException` | readiness false、process起動失敗 |

## 9. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-001 | Web/API/batch/protocolの4 moduleとする | UI 211/251、RD SYS-011。朝batchをAPI停止中に安全に実行し、protocolをframework非依存にする | PGでMaven reactor/ArchUnit、PTで禁止依存test |
| SS-D-002 | Package rootを`dev.codex.schubert.nk`とする | 現行`dev.codex.schubert`との由来を保ち、NKをnamespace分離 | Artifact/class名、log service名へ反映 |
| SS-D-003 | HTTP model、wire record、DB row/domainを分離する | UI 211 §5、RDの境界分離。秘密値の意図しないserialize/logを防止 | Mapper PTと全layout対応表323を必須化 |

## 10. 実装禁止事項

- Web moduleへの`schubert`業務schema権限または業務repository追加。
- Protocol moduleへのSpring/JMS/JDBC/Java serialization依存。
- Controller/Listener内へのSQL、path連結、業務transaction実装。
- API moduleからBrowserへ直接HTTP待受・HTML応答。
- Batch credentialによる任意SQL、任意Queue purge、DLQ自動削除。
- DTO/entityの`toString`へpassword、context、question/answer本文を含めること。

## 11. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Module、package、主要class、依存規則を初版作成。 |
| 2026-09-01 | SSC-002により`FixedWidthDecoder.decode`を322 §5の完全なtransport/route検査署名へ統一。 |
