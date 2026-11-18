# Log・metric・alert・error code設計

## SSC331 primitive local sink/terminal通知のfatal保持（2026-10-22）

WebRequestLogProducer.localは普通のlogger Runtime/disabled loggerで既同Web ownerのfixed terminal signalを一回、DB/JMS/識別子新規発行0とする。Runtime内包のErrorを正常な観測/falseや新catalogへ捨てず、通知後に既pure Web graph分類で同一Errorを伝播する。直接logger Errorは従来の即伝播（通知0）を維持する。

terminal callback Runtimeはcallback graph→logger graphの順に分類し、両非fatalだけ従来固定`request audit terminal signal failed`のIllegalStateExceptionを返す（provider cause/suppressedを持たせない）。直接callback Errorは従来の優先/通知1。cause/suppressed/JMS linked/SQL nextと非fatal cycle/aliasを扱い、元文面・Throwableをlocal/alertへ出さない。通常のmetadata/REQUEST code・HTTP応答/transport/wire/DB/owner/再送は変更しない。詳細312 SSC331、独立観点354、BUG1601/YKT1354。

## 1. 目的・追跡

WebからAPI/DB/MQ/file/batchまでを追跡するstructured log、監査event/action、機密除外、error code、
metric名・label、warning/critical条件、DEBUG/STANDARD監視mode、保持を定める。

- 上位設計: UI 225、231、235、241～243、252～253
- 関連RD: FUN-008、MON-001～MON-013、PER-007～PER-008、AVL-009～AVL-010、OPS-005
- 関連SS: [312_処理sequence・method・例外・transaction設計](../310_アプリケーション/312_処理sequence・method・例外・transaction設計.md)、
  [321_Artemis物理構成・JMS設定設計](../320_メッセージング/321_Artemis物理構成・JMS設定設計.md)、
  [341_朝batch・backup・削除・再実行設計](../340_batch・基盤/341_朝batch・backup・削除・再実行設計.md)
- 関連QA/RDF/UIC: QA-011、QA-021、QA-027、QA-042、RDFなし、UIC-002

## 2. Log channel・正本

| Category | Producer | Local | DB/Queue | 正本・失敗時 |
|---|---|---|---|---|
| `REQUEST` | Web HTTP filter | JSON 1 event/lineまたはjournald | `web_log_outbox`→`WLGEVT01`→`app_logs` | Localを原始証跡、DBをLog画面正本。投影失敗でHTTP結果を変更しない |
| `ACTION` | Web/API | JSON/journal | Critical eventはAPI transaction内`app_logs` | DB監査が正本、失敗は業務transaction rollback |
| `SECURITY` | Web/API | JSON/journal | API DB audit | Login/認可/管理/削除はDB正本 |
| `MQ` | Web/API/Artemis | JSON/journal | 重大eventはDB | Message/correlation/transportで追跡、bodyなし |
| `SYSTEM` | 全component | journald | 必要な重大eventはDB | Process/config/resource/health |
| `BATCH` | Morning/batch | JSON/journal | `batch_runs`＋`app_logs` | `batch_runs`がstep結果正本 |

REQUESTの形成はresponse status/elapsed確定後に行い、local JSON出力とtechnical outbox INSERTへ同じ
`eventMessageId`を使う。APIは`app_logs.source_message_id` UKで重複を捨てる。LocalとDBの差はmessage IDで照合可能にする。

## 3. JSON event schema

### 3.1 共通field

| Field | 型/上限 | 必須 | 規則 |
|---|---|---:|---|
| `timestamp` | UTC ISO-8601 millis | yes | Event確定時、DBはtimestamptz |
| `level` | TRACE/DEBUG/INFO/WARN/ERROR | yes | FATALはERROR＋`processExit=true` |
| `service` | WEB/API/BATCH/BROKER/DB/CADDY | yes | 低cardinality enum |
| `appVersion`,`configVersion` | 64 byte | yes | Release manifestと一致 |
| `category` | REQUEST/ACTION/SECURITY/MQ/SYSTEM/BATCH | yes | UI 252 |
| `action` | 64 ASCII | yes | §4 catalogのみ |
| `outcome` | SUCCESS/FAILURE/DENIED/RETRY/SKIPPED/UNKNOWN | yes | Errorでも判定不能を成功にしない |
| `requestId` | UUID | conditional | HTTP request単位 |
| `messageId`,`correlationId` | UUID | conditional | Wire業務ID |
| `jmsMessageId` | 128 byte | optional | Transport ID、metric label禁止 |
| `receiptId` | 26 ASCII | optional | 質問受付、権限制限logだけ |
| `actorUsername` | 64 UTF-8 byte | optional | NFC、control除外、Login失敗は最小限 |
| `actorRole` | USER/ADMIN | optional | API contextから決定 |
| `remoteAddress` | canonical IP | optional | Caddy信頼済み値、metric label禁止 |
| `resultCode` | 4 ASCII | optional | 電文responseだけ |
| `errorCode` | 64 ASCII | optional | §5 internal catalog |
| `elapsedMs` | 0..N12 | optional | Monotonic clockで計測 |
| `deliveryCount` | 1..4 | optional | JMSXDeliveryCount |
| `details` | object, serialized 1,024 UTF-8 byte以内 | optional | Key allowlist、nest 2層まで。WLGEVT01/LGSRSP01と同上限 |

StringはNFC、CR/LF/TAB/Unicode line separatorをASCII spaceへ変換、上限でcode-point境界truncateし
`truncated=true`をdetailsへ設定。JSON encoderを使い、message patternへ利用者入力を連結しない。

### 3.2 HTTP field

`httpMethod` 8 ASCII、`path` 256 UTF-8 byte、`status` 100..599、`responseBytes` N12、`userAgentFamily` 32 byte。
`path`はquery/fragmentを除いたroute templateまたは正規pathで、任意query値を保存しない。
Cookie/Authorization/CSRF/Referer全文/request・response bodyをdetailsへ入れない。

### 3.3 REQUEST正規化と限定ACTION投影（SSC-008/336）

WLGEVT01はUI235 §12.2の閉じた組合せだけを受理する。REQUESTのWeb producerはAction=`HTTP_REQUEST_COMPLETED`を設定し、REQUESTに限りAction省略時もAPIが同値を補う（SSC-008）。QA-054承認によりACTION/`MENU_VIEWED`を限定追加する。ACTIONのAction省略、未知category/action、交差組合せ、Webからの`LOG_SEARCHED`はDB接続前に恒久不正として拒否し、REQUESTへ読み替えない。Log typeの必須二値化以外の物理layout/必須項目は不変更。以下Details・表示metadata・UK/ACK規則は両組合せに共通する。

Detailsのwire入力は省略またはstrict JSON objectとし、次のkeyだけを許可する。重複key、未知key、null、末尾別document、コメント、型不一致を恒久不正としてDB接続前に拒否する。空objectは有効。Wire最大1,024 byteとDB JSONB表示最大1,024 byteの両方を維持する。

| Key | 型・値 | 根拠 |
|---|---|---|
| responseBytes | 整数0～999999999999（指数・小数・符号なし） | §3.2 HTTP byte数 |
| userAgentFamily | 1～32 ASCIIの英数/space/`.`/`_`/`-`によるfamily名 | §3.2。Producerは解析済みfamilyを生成しraw User-Agentを複製しない |
| truncated | boolean | §3.1の安全な上限処理の有無 |
| projectionStatus | `PENDING`または`FAILED` | 312 §11のlocal/outbox投影状態。MQ送信の確定を意味しない |

API保存時はwire Roleがある場合だけdetailsに`actorRole=USER/ADMIN`を追加する。このkeyをwire Detailsから受け付けず、独立Role fieldを正とする。Usernameは`actor_username`、HTTP request IDは`request_id`、event Message IDは`message_id/source_message_id`、Correlation IDは`correlation_id`へ保存する。表示metadataから業務user IDを逆引きせず、`actor_user_id`はNULLとする。Webによるmetadataを認証・認可の根拠にしない。

DB INSERTとsource UKの重複判定を同じ短transactionで確定し、その後にJMS ACKをcommitする。DB失敗時はJMS rollback、DB確定後ACK前の停止は再配送でINSERT 0/既存行不変を確認してACKする。Broker duplicate cacheのhit/missにかかわらずDB UKを最終正本とする。

### 3.4 REQUEST終端hook・投影故障（SSC-172）

SSC-173: `responseBytes`はWeb originのcharset後successful content write byte。HTTP header/transfer chunk framingを除き、導入Tomcat11.0.25のterminal callbackからCoyote Response.getContentWritten（ByteBuffer消費byte）を読取る。transport込みResponse.getBytesWritten、Servlet char数、Caddy後段変換を混同しない。強制flushなし・HTTP不変更、切断時の既知write観測はclient受信ACKの保証ではない。独立UTF8/固定body/HEAD0とchunked実HTTPを比較する。

具体producerと所有は312 §11。導入Tomcat11.0.25のAccessLog terminal callbackを使用し、通常・ERROR・ASYNC終端の最終status/elapsed/body byteを一度確定する。callback timeの単位はnanoseconds、local N12とWLGEVT01 X9の各上限を区別し、上限処理が必要なfieldはtruncated=trueで明示する。未知/負の観測を無根拠な成功へ補正しない。

server UUIDはpretrust identity、client addressはCaddy検証済値であり混同しない。actorは検証済username/roleだけ、pathはregistered routeの閉allowlist（unknownは固定/**）、raw URI/query/header/body/cookie/context/token/passwordは除外する。既存fixed business wireの最初のMessage IDだけをrequest lifetimeへ関連付け、対応MQなしはCorrelation ID=event自身とする。初回local PENDINGと故障時FAILED補足は同event IDで結合し、DB source UKの別eventを生成しない。

projection/local/metadata故障の固定internal codeは`WEB_REQUEST_LOG_PROJECTION_FAILED`、`WEB_REQUEST_LOG_LOCAL_FAILURE`、`WEB_REQUEST_LOG_METADATA_INVALID`（64 ASCII以内）。既存SYSTEM action INTEGRITY_FAILED/UNKNOWNまたは失敗alertへ使用し、新しいactionや業務resultを追加しない。null/malformed・未検証transportでwire必須のverified IP/statusを捏造せず、local安全故障を記録する。local logger失敗もownerへ固定terminal signal、例外原文・NPE正常化・HTTP結果変更0。critical API監査、wire layout/envelope/DDL、再送/保持/認可、Current/DIFは不変更。

## 4. Action catalog

| Action | Category | 発火・必須context |
|---|---|---|
| `HTTP_REQUEST_COMPLETED` | REQUEST | request ID、method/path/status/elapsed |
| `MENU_VIEWED` | ACTION | 認証済み正常メニューGET成功終端時、Web local/outbox/API UK、HTTP request ID、REQUESTと別event |
| `LOG_SEARCHED` | ACTION | ADMINログ検索のAPI初回成功transaction内に一度、snapshot取得後、保存結果再送で追加0、query値なし |
| `LOGIN_SUCCEEDED`,`LOGIN_FAILED`,`LOGIN_LOCKED` | SECURITY | request ID、remote IP、user有無を外部へ出さないreason code |
| `LOGOUT_SUCCEEDED`,`LOGOUT_REVOCATION_QUEUED` | SECURITY | actor、request/message ID、raw contextなし |
| `SESSION_REVOKED`,`SESSION_EXPIRED`,`SESSION_DECRYPT_FAILED` | SECURITY | reason、session ID/hashなし |
| `AUTHORIZATION_DENIED`,`OWNER_SCOPE_DENIED` | SECURITY | actor、route/layout、target type、target ID最小限 |
| `USER_CREATED`,`USER_STATUS_CHANGED`,`USER_ROLE_CHANGED` | ACTION/SECURITY | actor/target username、before/after、tokenなし |
| `USER_PASSWORD_RESET`,`USER_UNLOCKED` | SECURITY | actor/target、password/hashなし |
| `SCENARIO_SEARCHED`,`SCENARIO_VIEWED` | ACTION | 条件は種別/件数だけ、keyword/bodyなし |
| `MEDIA_STREAMED`,`MEDIA_DOWNLOADED`,`MEDIA_RANGE_REJECTED` | ACTION | media type、logical ID、status/bytes、pathなし |
| `QUESTION_SUBMITTED`,`QUESTION_CANCELLED`,`QUESTION_DELETE_MARKED` | ACTION | receipt/job/question ID、actor、state、本文なし |
| `QUESTION_PROCESSING_STARTED`,`QUESTION_COMPLETED`,`QUESTION_FAILED` | ACTION | receipt/job/message ID、state/error code、回答なし |
| `MESSAGE_SENT`,`MESSAGE_RECEIVED`,`MESSAGE_ACKED`,`MESSAGE_REDELIVERED` | MQ | address/layout/IDs/count/bytes |
| `MESSAGE_EXPIRED`,`MESSAGE_DLQ_ROUTED`,`MESSAGE_REPLAYED` | MQ | original address/queue、IDs、approval reference |
| `PROTOCOL_REJECTED`,`CORRELATION_REJECTED` | MQ/SYSTEM | layout/version/length step、body dumpなし |
| `OUTBOX_CLAIMED`,`OUTBOX_SENT`,`OUTBOX_RETRY`,`INBOX_REPLAYED` | MQ | type/count/age/attempt、token/HMACなし |
| `SERVICE_STARTED`,`SERVICE_READY`,`SERVICE_STOPPED`,`SERVICE_EXITED` | SYSTEM | version、exit code、duration/reason |
| `CONFIG_DRIFT_DETECTED`,`RESOURCE_LIMIT_REACHED`,`INTEGRITY_FAILED` | SYSTEM | config area/resource/error code、secret/pathなし |
| `BATCH_STEP_STARTED`,`BATCH_STEP_COMPLETED`,`BACKUP_VALIDATED` | BATCH | run/step/attempt/count/byte/status |
| `CLEANUP_SKIPPED`,`CLEANUP_COMPLETED`,`RESTORE_VERIFIED` | BATCH | gate/reason/count/duration |

Action名追加は351とLog画面filter/testを同時更新する。フリーテキストactionを許さない。

### 4.1 Currentとのaction対応・独立期待値（QA-051/SSC-184、2026-11-02承認）

CHR-L01ではUI264 §5.1のDIF-010を適用し、NKのactionを本節catalogへ統一する。空REQUEST→`HTTP_REQUEST_COMPLETED`、`login_success`→`LOGIN_SUCCEEDED`、scenario検索の`search`→`SCENARIO_SEARCHED`は、それぞれ同じ実操作・categoryの相関根拠が成立する行だけを対応付ける。Currentの値を汎用uppercase化して対応を推測しない。

操作ごとに、本設計及び既承認UIからcategory/action/記録先/必要件数/REQUESTのHTTP項目を独立した期待表へ固定する。`menu`/`log_search`相当の記録とcallerを対応表へ含め、未対応・不足は未完のまま残す。実測値を期待件数として採用しない。

既存ログとCurrent baselineは不変とし、fixture・before/after・request/event/message相関・整合した観測時点から今回操作を識別する。水位のみの選択、追加技術行の一律除外、秘密を含むraw比較出力は禁止する。local/outbox/DBの冪等性、欠落0・重複0及び画面の件数/順序/明細はSS355 §8.1で独立に検証する。

本承認は比較仕様の確定であり、実装・比較oracle・実NK試験・正式受入は未完。wire/schema、ログ生成・保存・送達責務や未知の業務差分を変更・免除しない。

## 5. Result・internal error catalog

### 5.1 Wire result（上位確定）

| Result | HTTP | 利用者・再試行 | Log level/category |
|---|---:|---|---|
| `0000` | 200/302 | 新規成功 | INFO/ACTION |
| `0100` | 400 | Field error、修正後再送 | INFO/REQUEST |
| `0101` | 401 | 認証失敗、存在有無を区別しない | WARN/SECURITY |
| `0102` | 401 | HTTP session破棄、Loginへ | INFO/SECURITY |
| `0103` | 403 | 認可拒否、自動再試行なし | WARN/SECURITY |
| `0104` | 404 | 非scope/不存在を区別しない | INFO/WARN |
| `0105` | 409 | 最新再表示・新token | INFO、HMAC不一致はWARN/SECURITY |
| `0106` | 429相当 | Lock残時間を案内 | WARN/SECURITY |
| `0107` | 409 | 取消不可・最新状態表示 | INFO/ACTION |
| `0200` | 200/302 | 冪等成功、保存済み結果 | INFO/ACTION |
| `9000` | 503 | 一時障害、再操作案内 | ERROR/SYSTEMまたはMQ |
| `9001` | 503 | 容量/resource上限、新規受付停止 | ERROR/SYSTEM、alert |

SSC-046: 上表は汎用HTTP分類であり、form POST `/login`の0101は現行互換の302 `/login?error`、0106は302 `/login?locked`＋API応答の0..900秒 `Retry-After`を使用する。UI226のquery別表示と313のredirect/再表示を優先し、401/429の直接応答へ置換しない。不存在/不一致/disabledは同じ失敗遷移。API timeout/9000・session保存障害は503で、認証失敗counterをWebで加算せず、LOGIN_FAILEDへ誤分類しない。正常はsafe SavedRequestのGETへ302、なければ`/`。Header/body/sessionへ例外やpasswordを保存しない。根拠はCurrent LoginAuthenticationFailureHandler/SuccessHandlerとCHR-A02のlockedRedirectであり、Current baselineは不変更。

SSC-048: 業務API0102の401はPOST/HEAD/その他・AJAX・media向けとし、通常GETだけ313/UI221に従い302 `/login?session-expired`へ戻す。いずれもlocal HTTP sessionと表示snapshot/CSRFを消去し、既存action SESSION_EXPIRED/reason API_SESSION_INVALIDをINFO/SECURITYで記録する。API context/session ID/hash/元response/秘密値は記録しない。WebResultMapperの全result汎用分類だけでは失効/競合/field再表示等の副作用を完了扱いしない。

Permanent protocol errorは信頼できるresponseを返さずDLQとprocess exitのためwire resultなし。

### 5.2 Internal error群

| Prefix/例 | 分類 | Wire/action |
|---|---|---|
| `AUTH_INVALID`,`AUTH_LOCKED`,`AUTH_SESSION_INVALID` | 認証 | 0101/0106/0102、秘密なし |
| `AUTHZ_ROLE_DENIED`,`AUTHZ_OWNER_DENIED` | 認可 | 0103/0104、SECURITY |
| `VALIDATION_FIELD`,`STATE_CONFLICT`,`CANCEL_NOT_ALLOWED` | 業務 | 0100/0105/0107 |
| `MQ_CONNECT_TIMEOUT`,`MQ_REPLY_TIMEOUT`,`MQ_SEND_BLOCKED` | 一時MQ | 9000/9001、retry/alert |
| `MQ_PROTOCOL_LENGTH`,`MQ_PROTOCOL_UTF8`,`MQ_PROTOCOL_LAYOUT` | 恒久protocol | DLQ＋exit、responseなし |
| `MQ_CORRELATION_MISMATCH`,`MQ_DELIVERY_EXHAUSTED`,`MQ_DLQ_SEND_FAILED` | MQ整合 | DLQ/exit/runbook、critical |
| `DB_CONNECT`,`DB_TIMEOUT`,`DB_DEADLOCK` | 一時DB | 9000またはJMS rollback |
| `DB_SCHEMA_MISMATCH`,`DB_CONSTRAINT_UNEXPECTED`,`DB_GRANT_INVALID` | 起動/整合 | readiness false、critical |
| `FILE_DESCRIPTOR_INVALID`,`FILE_PATH_REJECTED` | 恒久/攻撃 | 404/503、SECURITYは連続時 |
| `FILE_INTEGRITY_MISMATCH`,`FILE_IO`,`FILE_CAPACITY` | File障害 | 503/9000/9001、配信停止 |
| `BACKUP_COMMAND`,`BACKUP_INTEGRITY`,`BACKUP_CAPACITY` | Backup | Business cleanup skip、warning/critical |
| `CLEANUP_SAFETY_GATE`,`CLEANUP_PARTIAL`,`EXPIRY_MAINTENANCE` | Batch | 後続停止またはwarningは341に従う |
| `CONFIG_INVALID`,`CONFIG_DRIFT`,`SECRET_MISSING`,`SECRET_KEY_VERSION` | Config/security | 起動失敗/deny closed |
| `RESOURCE_MEMORY`,`RESOURCE_DISK`,`RESOURCE_QUEUE`,`RESOURCE_THREAD` | 容量 | 9001/new work停止、critical |

Exception class→error code→wire result/HTTPの mappingはexhaustive switchとし、unknownは`SYSTEM_UNEXPECTED`/9000。
DB constraint/SQL/path/exception messageを利用者responseに直接設定しない。

### 5.3 非同期通知用error code

NTDRSP01の16 byte Error codeは内部64 byte codeを直接出さず、次の安定allowlistへmapする。

| Notification code（16 ASCII以内） | 主な内部code群 | 利用者向けmessage |
|---|---|---|
| `PROCESS_FAILED` | `SYSTEM_UNEXPECTED`、分類不能な最終失敗 | 処理に失敗。通知/質問IDと共に管理者へ連絡 |
| `SYSTEM_UNAVAIL` | MQ/DB/file一時障害の再配送上限 | 一時障害で処理できなかったことを案内 |
| `RESOURCE_LIMIT` | Memory/disk/Queue/file容量上限 | 容量制限による失敗と再操作案内 |
| `DATA_INTEGRITY` | File/hash/DB整合性異常 | 対象dataの整合性確認中であることを案内 |
| `PROTOCOL_ERROR` | Fixed message/version/layout恒久error | 処理不能と管理者連絡を案内 |

`notifications.error_code`/NTDRSP01はこの値だけ、`async_jobs.last_error_code`やlog/outbox/batchは
内部64 byte codeを保持する。利用者向けerror messageは512 byte以内の定型文とし、exception文を複製しない。

## 6. Metric catalog

Metricは`nk_`接頭辞、counterは`_total`、byteは`_bytes`、時間は`_seconds`。

| Metric | Type | Label allowlist | 目的 |
|---|---|---|---|
| `nk_http_requests_total` | counter | service,route,method,status_class | HTTP結果、route templateのみ |
| `nk_http_request_duration_seconds` | histogram | service,route | p50/p95/p99、bucket .05/.1/.25/.5/1/1.5/2/2.5/5 |
| `nk_mq_messages_total` | counter | direction,address,layout,outcome | Send/receive/ACK/retry/DLQ |
| `nk_mq_processing_duration_seconds` | histogram | flow,layout,outcome | MQ/API時間budget |
| `nk_mq_queue_messages`,`nk_mq_queue_bytes` | gauge | queue | Artemis滞留 |
| `nk_mq_address_memory_bytes`,`nk_mq_address_paged_bytes` | gauge | address | QA-042/UIC-002承認済みのAddress別memory high-waterとpage limitに照合 |
| `nk_mq_paging_active`,`nk_mq_page_files` | gauge | address | PAGE開始・page growth・page-full予兆 |
| `nk_mq_redeliveries_total` | counter | queue,delivery_count | Redelivery回数。時系列oracleはQA-041/UIC-001承認値の1秒、5秒、25秒 |
| `nk_outbox_rows` | gauge | store,status | API/Web outbox件数 |
| `nk_outbox_oldest_seconds` | gauge | store,status | 滞留時間 |
| `nk_inbox_replays_total` | counter | layout,result | Message/token replay |
| `nk_operation_token_mismatch_total` | counter | operation | HMAC不一致、actor/token labelなし |
| `nk_async_jobs` | gauge | state | RECEIVED～CANCELLED |
| `nk_db_pool_connections` | gauge | service,state | active/idle/pending/max |
| `nk_db_query_duration_seconds` | histogram | query_id,outcome | SQL本文なし |
| `nk_file_transfer_files`,`nk_file_transfer_bytes` | gauge | suffix | transfer容量 |
| `nk_media_streams` | gauge | media_type | 同時stream |
| `nk_media_bytes_total` | counter | media_type,mode,status | Inline/download/Range |
| `nk_integrity_failures_total` | counter | area,step | Hash/path/config異常 |
| `nk_batch_runs_total` | counter | step,status | Morning/backup/cleanup |
| `nk_batch_last_success_timestamp_seconds` | gauge | step | 未実行・連続失敗 |
| `nk_process_restarts_total` | counter | service,reason | Systemd/Java異常 |

JVM/GC/thread、Hikari、process/host/disk、PostgreSQL、Artemisは製品exporter/Micrometer標準metricを使う。
Username、IP、request/message/correlation/token/receipt/media ID、path、exception messageはlabel禁止。

## 7. Alert condition

| Alert | Warning | Critical | 自動制御/一次対応 |
|---|---|---|---|
| Filesystem | >=80% 5min | >=90% 1min | Large-result新規停止、95%は入口停止検討 |
| Transfer | >=3.5GBまたは5,000 | >=4.5GBまたは9,000 | 新規file modeを9001、朝清掃調査 |
| Async Queue | >=5,000または70% | >=9,000または90% | 新規質問受付を9001、既受付は削除しない |
| Web log Queue/outbox | >=5,000または最古5min | >=9,000または最古30min | Local JSON継続、dispatcher/ingestor復旧 |
| DLQ | >=1 | 増加または未調査 | 自動再投入/削除なし、353 |
| Expiry | >=1,000 | >=5,000 | Morning selector purge、criticalはAPI起動停止 |
| DB pool | >=80% 5min | pending/timeout 1件 | Slow query/pool leak調査 |
| JVM heap | >=75% 10min | >=90%またはOOM | OOMはexit/restart、heap dumpなし |
| Sync p95 | >2.0s 5min | >2.5s 5min | Error率と区間別を確認 |
| Backup | 05:00 run後当日SUCCESSなし | 2回連続失敗 | Business cleanup skip、容量/権限/DBを復旧 |
| Restart | 1回 | 10分に5回・rate limit | Unit failed、message/error ID調査 |
| Integrity/config | 1回 | 常にcritical | 配信/readiness停止、自動修復なし |

Alertは同一condition/serviceで1 eventをopenし、継続中はcount/lastSeenを更新。Warningは5分正常、criticalは
10分正常＋原因撤去確認でclose。初期の外部通知先は要件外のため、local status/journal/管理者SSH確認を正とする。

Queueのbyte/percentage alertの分母は321 §5.2の用途別合計保存上限、paging開始は§5.3のmemory high-water、
page-fullはAddress別disk paging上限とする。Page-full時は明示errorを9001へ変換し、filesystem 90%ではproducer BLOCK/readiness false。
件数thresholdとDLQ 1件alertも併用する。

## 8. DEBUG/STANDARD

| 項目 | DEBUG（PG/PT/IT） | STANDARD（ST/本番） |
|---|---|---|
| Actuator detailed metric | enabled、loopback | 非公開の最小healthのみ |
| Prometheus/Grafana/exporter | enabled | service停止・scrape無効 |
| Retention/cap | 15日/5GB | 詳細metric保存なし |
| JVM app log level | 別keyで必要時DEBUG | INFO |
| Redaction | 同一・緩和不可 | 同一 |

`nk.monitoring.mode`とsystemdの監視target状態をstatus checkが照合。Mode切替はapplication rebuildなし、
service daemon-reload/restartが必要な場合は計画停止内に行う。

## 9. Retention・rotation・access

- Journald/file log: 100MB＋14世代を目安、service合計5GB、file 0640、ops read。OS journald合計もUI 253の10GB内。
- `app_logs`: 90日、backup成功後chunk削除。Security holdの明示IDは`app_logs.id`、期限は
  `security_hold_until`とし、`category='SECURITY' and security_hold_until > cleanup cutoff`だけを除外する。
  期限未設定/到達後は通常保持に戻し、保持期限自体はLog画面/ops viewに表示しない。
- `batch_runs`: 400日、RUNNING/FAILED調査中は削除禁止。DEBUG metric: 15日/5GB。
- Log画面はADMINだけ、ops read viewは本文/ciphertext/hash/IP等を除外。OS logはservice group/運用者だけ。

## 10. Test・quality gate

1. 全action/error/metricがcatalog外値を受け付けないこと。JSON schemaとDB column長の照合。
2. Password、hash、raw/hash/ciphertext context、cookie、CSRF、HMAC/AES key、質問/回答、fixed body、absolute pathのcanary検索が0。
3. Web local JSON→outbox→WLGEVT01→DBの停止/再送/重複、source message IDで欠落/重複0。
4. Metric cardinalityの利用者数/要求数比例増加がないこと、label禁止値が0。
5. 全warning/criticalの境界値直前/到達/回復、抑止・起動gate、alert closeを検証。
6. DEBUG→STANDARD切替で詳細service/scrape停止、最小health/systemd/journal/Artemis/DB/disk継続。

## 11. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-042 | Log action/error/metric labelをcatalog allowlistにし、未知値をフリー文字列で出さない | 追跡性、redaction、metric cardinalityを機械検査可能にする | Enum/schema/log contract PT |
| SS-D-043 | PostgreSQL slow SQL本文ではなく`query_id`＋duration metricで性能を追跡 | Bind値の質問/passwordがlogへ漏れるriskを防止 | Repository query ID、PT/IT plan証跡 |
| SS-D-044 | Alertをcondition/service単位のopen eventとし、重複発報ではなくcount/lastSeenを更新 | 外部通知なしの初期構成でも調査可能な証跡を残す | Status/runbook/alert state PT |

## 12. 禁止事項

SSC-454。Webの値型の一般診断では、EncryptedWebLogPayload.toStringは「EncryptedWebLogPayload[keyVersion/ciphertext=<redacted>]」、ValidatedReply.toStringは「ValidatedReply[correlationId/body=<redacted>]」の固定文字列とする。内部idや鍵versionラベルの値を一般診断へ連結しない。§3.1に従う構造化相関IDのフィールド、JMS相関に使うUUID、暗号処理と保存に使う鍵version、値取得methodと型の比較契約に変更はない。実Logのfield allowlist及びmetricsのlabel禁止は従来どおり適用する。

SSC-455。EncryptedAuthContext.toStringは「EncryptedAuthContext[keyVersion/ciphertext=<redacted>]」の固定値とし、鍵versionや暗号文の実値を一般診断へ連結しない。認証・再送の構造化ログやmetricのallowlist、値取得、保存列、暗号key選択の契約を維持する。

SSC-458。CanonicalField.toStringは「CanonicalField[<redacted>]」、CanonicalRequest.toStringは「CanonicalRequest[<redacted>]」の固定値とする。field名・型版、layout ID・版、owner・target・fieldsの実値を一般診断文字列に連結しない。SS324 §3の正規化・暗号入力・固定layout・値アクセサーと、本書§3の項目別に許可した構造化ログを維持する。

SSC-459。PendingReply.toStringは「PendingReply[correlationId/deadline/body=<redacted>]」の固定値とし、実相関ID・締切・応答bodyを一般診断に連結しない。SS321の相関照合・単調な期限判断・一回終端と、本書§3で許可する明示構造化相関項目及び所有copyの契約を維持する。

SSC-460。一般診断のFingerprint／InboxCompletion／InboxExecution／AuthenticatedActorのtoStringは、各型名と「[<redacted>]」を連結した固定値とする。鍵版ラベル、Inbox状態、認証済roleは必要な明示アクセサーと許可された構造化項目から扱う。照合用digest、状態判定、実行結果、認可の契約は従来どおり。

SSC-462。EncryptedResponseSnapshot.toStringは「EncryptedResponseSnapshot[keyVersion/ciphertext=<redacted>]」の固定値を返す。鍵versionラベルと暗号文本体を一般診断へ連結しない。SS324の保存と鍵選択、明示アクセサー、記録を許可された構造化フィールドは既契約に従う。

SSC-463。InboxResultReference.toStringは「InboxResultReference[<redacted>]」の固定値を返す。内部enum種別と識別値を一般診断へ連結しない。必要なtype()・参照値と明示の構造化種別欄はSS324と本書§3の契約に従う。

SSC-464。OutboxEntry.toStringは「OutboxEntry[<redacted>]」、OutboxRequest.toStringは「OutboxRequest[<redacted>]」を返す。実id、宛先、本文を一般診断へ連結しない。本書§3で許可する構造化欄、明示アクセサー、配送・再送の責務は維持する。


- DEBUGだけ機密除外を緩和、request/response/fixed body、exception/SQLの`toString()`を無制限出力。
- Username/IP/message/token/path等の高cardinality/機密値をmetric label化。
- REQUEST投影失敗で利用者の成功responseを503へ変更、またはcritical auditをbest-effort投影だけにすること。
- DLQ/integrity/secret/config drift alertを自動close、調査なしにmessage/file/configを削除/修復。

## 13. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Structured log、action/error/metric catalog、alert、mode、retentionを詳細化。 |
| 2026-08-31 | 横断監査でQA-042/UIC-002のpaging/address memory metricと、容量率alertのpending oracleを追加。 |
| 2026-09-01 | QA-042/UIC-002承認を反映し、Queue容量率、paging開始、page-full、disk-fullのalert分母と動作を確定。 |
| 2026-09-03 | SSC-005を反映し、Security holdのID/期限、対象category、非公開条件を具体化。 |

## QA-050承認反映：Logout継続再試行の観測（2026-10-03）

15分継続再試行の送信件数/秒・残件数・最古滞留時間・claim/lease競合・結果code/復号不能・解消件数・Logout要求から確定失効までの時間を観測する。IT/STでは同期画面p95/MQ待ち、API/DB CPU・lock待ち・接続pool、Inbox件数/容量・WAL、Broker pending/journal/diskを同じ負荷条件で測定する。raw/hash/contextや暗号本文をmetric/logへ含めない。滞留と鍵保持は警告・正規復旧へ引継ぎ、attempt100を解消扱いにしない。間隔の変更判定・再試験はSS354のQA050節に従う。

## QA-054 独立期待表（UIC-011/SSC-336、2026-11-05承認）

| 操作/観測 | 成功ACTION期待値 | REQUEST/保存・再送後条件 |
|---|---|---|
| 認証済みUSER/ADMINの正常メニューGET | MENU_VIEWED/ACTION 1件 | HTTP_REQUEST_COMPLETED/REQUEST 1件、別event ID/同HTTP request ID、各local/outbox/API DBの論理投影1件、各再配送で追加0 |
| ADMINログ検索の初回成功 | LOG_SEARCHED/ACTION 1件、検索snapshot取得後に同成功transactionで保存 | 別REQUEST 1件、commit後DBのACTION 1件と応答snapshotを別照合、必要MQは別期待値 |
| 保存済み検索結果の再送 | LOG_SEARCHED追加0 | 保存結果不変、必要INBOX_REPLAYED等と区別。新HTTP requestのREQUESTを業務成功ACTIONと混同しない |
| 失敗・未認証・role拒否、メニュー以外/HEAD | 当該成功ACTION 0件 | 従来REQUEST・拒否/失敗監査はそれぞれ既存規則どおり |

上記はUI235/252/264・SS312/323/324/355へ横断反映する。API LOG_SEARCHED保存失敗は初回成功transactionをrollbackし、Web投影で代替しない。Current baseline、保持済ログ、画面表示順/件数/明細を変更せず、実測から期待値を作らない。既存app_logs DDLはcategory ACTION/64-byte action/UKを収容しDDL変更不要。承認は実装/実PT/CHR/正式品質の受入を意味しない。
