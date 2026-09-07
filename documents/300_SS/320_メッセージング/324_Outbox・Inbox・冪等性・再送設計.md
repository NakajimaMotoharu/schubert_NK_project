# Outbox・Inbox・冪等性・再送設計

## 1. 目的・追跡

Message ID、operation token、HMAC fingerprint、request inbox、API/Web outbox、response replay、Artemis duplicate detection、再送と保持を定める。

- 関連UI: 212～213、222、225、231～236、241～242、251～253
- 関連RD: MQ-006～010、MQ-040～045、FUN-103～105、ASY-001～006、DAT-005～010
- 関連QA/RDF/UIC: QA-009、027、030、033～040、RDFなし、UICなし

## 2. 冪等性keyの役割

| Key | Scope | 再利用 | 正本 |
|---|---|---|---|
| JMS provider Message ID | Transport delivery | Broker再配送で同一 | Artemis/logのみ |
| 業務Message ID | 1 wire message | Transport再配送は同一、利用者再操作は新規可 | `request_inbox.message_id`、event/work UK |
| Correlation ID | Request/response/後続event関係 | Response/workで元requestを参照 | Header/JMS/log |
| Operation token | 1 Browser論理更新 | Timeout再操作だけ同一 | Owner scope unique index＋業務UK |
| Request/payload fingerprint | 全RequestのMessage ID、更新tokenの対象/layout/payload拘束 | Key rotation version付き | HMAC-SHA-256 |
| Business UK | Question token、answer question、event source ID等 | 永続 | 業務table/DB constraint |

Message IDだけでは同ID・異bodyやBrowser timeout後の新Message IDを安全に判別できない。全RequestにHMAC fingerprintを付け、
更新layoutはoperation tokenも併用する。Artemis duplicate detectionは補助であり、DB一意制約を省略しない。

## 3. Canonical fingerprint

### 3.1 Binary format `NKOP1`

HMAC入力は文字列連結を使わず、次の順で構築する。整数lengthはunsigned 32 bit big-endian、文字列はNFC後UTF-8、nullはlength
`0xFFFFFFFF`、emptyはlength 0として区別する。

```text
ASCII "SCHUBERT-NK-OP1"                            # magic/version
LP(owner scope: user ID decimal or "ANONYMOUS")
LP(request layout ID: exactly 8 ASCII)
LP(request layout version: exactly 3 ASCII)
LP(target canonical string)
U32(field count)
repeat in layout-defined order:
  LP(field name ASCII)
  LP(field type/version ASCII)
  LP(canonical field bytes)
```

Operation token、header ID/time/context、reserved、CSRF、paddingはpayloadへ含めない。全Requestはdecode後のlayout定義順に全有効fieldをcanonical化する。
323 §9の更新/Login layoutは記載のtarget/payloadを正とし、その他は`REQUEST:<layout-id>`をtargetとする。
Password・質問本文もHMAC入力には含めるが、平文/単純SHA-256/canonical bytesをDB/logへ保存せず、計算後bufferをzero fillする。

### 3.2 HMAC

- AlgorithmはHMAC-SHA-256、256 bit以上のrandom key、hex lowercase 64文字保存。
- Credential名とkey versionは352を正とし、DBには`fingerprint_key_version`だけを保存する。
- 比較はconstant-time。Current keyでwriteし、保持中inboxを読むprevious keyを保持する。
- Key/version不明は保存済み成功を推測せずdeny closed・運用errorとする。

## 4. `request_inbox` state

```text
          +--------------------+
new ----> PROCESSING ----------+----> COMPLETED
             |                 +----> ERROR（確定業務error responseあり）
             +-- crash/rollback -> rowもrollback、再配送でnew
```

`PROCESSING`を長期保持したままにしない。Application transaction内でINSERTからCOMPLETED/ERRORまで確定するため、transaction rollback時は
新規rowも消える。既存PROCESSINGが観測されるのは並行Browser再操作だけであり、待機せず`9000`を返して同token再操作を案内する。

## 5. Inbox取得algorithm

`InboxCoordinator.begin(RequestIdentity identity, Fingerprint fp)`は認証後、業務処理と同じDB transactionで次を行う。
`LGNREQ01`だけは認証contextがないため、protocol検証後・password照合前に`AnonymousInboxCoordinator`で同じalgorithmを開始する。

1. Message IDでrowを検索し`FOR UPDATE`する。
2. 存在する場合、layout/correlation/owner/fingerprintを比較する。不一致はMessage ID再利用の恒久整合errorとして処理し、保存結果を返さない。
3. Operation tokenがある場合、`(owner_user_id,operation_token)`を`FOR UPDATE`で検索する。
4. Token rowがありHMAC一致＋COMPLETED/ERRORなら保存済み結果を返す。一致＋PROCESSINGなら`9000`。不一致なら`0105`。
5. 該当なしならPROCESSING rowをINSERTする。並行unique違反は1回だけ既存row再読へ戻る。
6. Handler結果とcritical auditを確定し、result reference/response snapshot、response layout、completed_at/expires_at、stateを更新する。

Login前はowner NULLであり、Message IDだけを一意keyとする。同一Message IDでは323 §9の匿名HMACも一致必須とする。
Login成功replayは`auth_sessions.created_message_id`、認証失敗は暗号化済みerror response snapshotを使用する。
Inbox・User/IP counter・auth session・snapshotは同一transactionでcommitする。Owner NULL＋operation tokenのpartial uniqueは作らない。

## 6. Response保存・再構成

| 処理 | 保存方式 | Replay |
|---|---|---|
| Login成功 | `result_ref=AUTH_SESSION`＋`result_ref_uuid=auth_sessions.id` | auth session ciphertextを復号し同context/expiryを返す |
| Login失敗/lock | 暗号化response snapshot | 同result/retry情報を返す |
| 参照/list/detail | 暗号化・圧縮済みfixed response body | Header Message/Correlation/sentAtを新response用に再構築しpayloadをdecode/encode |
| User更新 | `result_ref=USER`＋version/result | 現在値が進んでいても当該操作の保存versionを0200で返す |
| Question受付 | `result_ref=QUESTION` | receipt/question/submittedを業務rowから0200で返す。Outbox SENTも再確認 |
| Cancel/delete | `result_ref=JOB/QUESTION`＋確定日時 | 同じstate/deleted_atを0200 |
| Scenario file mode | `result_ref=SCENARIO_FILE`＋`result_ref_id=script_files.id`＋descriptor | `.ready`存在時は同descriptor。朝削除後は同じmaster file snapshotから新fileを再生成 |

SnapshotはZstandard等の新規native依存を避け、JDK `Deflater` level 3で圧縮後、`api-inbox-response-aes` AES-256-GCM keyで暗号化する。AADはMessage ID、
response layout/version、owner ID。最大平文1,000,000 byte、最大暗号文1,050,000 byteをCHECK/guardする。圧縮bombを避けdecode時に期待平文上限を設定する。

Replay responseは新しいresponse Message IDとsentAtを持ち、Correlation IDは再送requestのMessage IDへ合わせ、result codeを`0200`とする。
保存済みbodyをbyte単位でそのまま返して古いheader/correlationを混入させない。

## 7. Inbox transaction/crash

| Crash | 状態 | Recovery |
|---|---|---|
| Inbox INSERT前/transaction中 | Row/業務ともrollback | 同Message IDを新規処理 |
| 業務＋Inbox commit後/reply前 | COMPLETED/ERROR | 再配送でreplay |
| Reply send後/JMS commit前 | DB確定、reply取消 | Request再配送、replay＋再send |
| JMS commit後/Web timeout | DB/reply/ACK確定 | 新Message ID＋同tokenで0200 |

DB transactionとJMSをXAで結合しない。Inbox replayによりDB先commitを安全にする。

## 8. API `mq_outbox`

### 8.1 Row

331の物理DDLではUI 242の項目に加え、`lease_owner varchar(64)`、`lease_until timestamptz`を持つ。Destinationは
物理Address `nk.async.work`/`nk.dead.letter`だけを保存する。Javaは閉じた`OutboxDestination`
（`ASYNC_WORK`/`DLQ`）からこの2値へのみ変換し、実Address文字列を利用者入力から設定しない。

### 8.2 State

```text
PENDING --claim/send/confirm--> SENT
   | send失敗
   +--> ERROR --due再claim--> SENT/ERROR
```

ERRORは最終破棄を意味せず、非同期要求にbusiness timeoutがないため再送を継続する。Attempt 10回または最古30分でcritical alertし、
自動削除しない。

### 8.3 Claim/send

1. `status in (PENDING,ERROR)`、due、lease期限切れを`FOR UPDATE SKIP LOCKED`で最大100件取得する。
2. 10秒lease ownerを設定して短transactionをcommitする。
3. Destination/layout/bodyを再decodeし、allowlistとMessage IDを検証する。
4. Persistent messageへ`_AMQ_DUPL_ID=message_id`を設定し、JMS transacted send/commitする。
5. DB短transactionでSENT/sent_at、lease clearを更新する。
6. Crashが4と5の間なら同Message IDを再sendする。Broker duplicate cacheまたはConsumer DB UKが重複を排除する。

再送delayは1秒、5秒、30秒、1分、5分capとし、outbox送信接続障害のapplication scheduleである。UIC-001のBroker受信再配送間隔とは別物。

## 9. Web `web_log_outbox`

- HTTP response確定後のWLGEVT01 payloadをWeb log AES-GCM keyで暗号化して保存する。
- Web dispatcherがlocal outboxを復号し、WLGEVT01のheader/field/semanticを完全decodeして保存rowのMessage ID/Correlation/layout/versionとの一致を検査後、SS 323の固定長平文電文を送信する。暗号鍵とWeb table accessはWebだけが持ち、API ingestは受信電文の検査と冪等INSERTを行う（SSC-007）。
- Message ID UK、Correlation、layout/version、status/attempt/next/lease、created/sentを持つ。
- Dispatcher algorithm/backoffはAPI outboxと同じ。HTTP request threadはsendを待たない。
- API `app_logs.source_message_id` UKが最終重複防止。DuplicateはINSERTせずJMS ACKする。
- APIは351 §3.3のREQUEST action/Details/表示metadataの正規化を適用し、DB INSERT/duplicate transaction確定後だけlistenerへ正常復帰する（SSC-008）。
- PENDING/ERRORの本文を管理画面へ表示せず、件数・最古時刻・error codeだけ監視する。

## 10. Internal work冪等性

`QWKREQ01`はmessage本文のIDを正本にせずDBを再取得する。

| State/DB | 同Message ID receive時 |
|---|---|
| RECEIVED | PROCESSINGへCAS、`processing_message_id`保存 |
| PROCESSING＋同ID | Crash recoveryとして処理再開 |
| PROCESSING＋別ID | 整合error。Ackせず調査/DLQ |
| COMPLETED＋answerあり | 冪等ACK、更新なし |
| ERROR | 冪等ACK。運用承認なしに再処理しない |
| CANCELLED | 業務処理せずACK |

`answers.question_id` UK、`async_jobs.message_id` UKが二重回答を防ぐ。再配送countを`retry_count=JMSXDeliveryCount-1`へbounded更新する。

## 11. Operation token lifecycle

- Webはform GETでtokenを発行し、sessionに用途/発行日時だけ最大10件保持する。
- Token有効期間は8時間idle session内。成功確定後に消費済みmarkし、同結果画面refreshでは再送しない。
- Timeout/503だけ同tokenをformへ戻す。Validation errorでAPI未送信の場合は同tokenを維持する。
- 409 payload不一致/optimistic conflictでは旧tokenを破棄し、最新GETで新tokenを発行する。
- APIはsession内token状態を信用せず、owner/token/HMAC/業務UKを正とする。

## 12. 保持・cleanup

| Data | expires/削除 | 削除禁止 |
|---|---|---|
| 参照request inbox | 完了24時間後 | PROCESSING、response復号/整合error |
| 更新request inbox | 完了7日後 | 対応業務UK/result ref不整合 |
| API mq_outbox | SENT 7日後 | PENDING/ERROR/lease中 |
| Web log outbox | SENT 7日後 | PENDING/ERROR/lease中 |
| Question operation token | Question物理削除まで業務UK保持 | 通知/質問存続中 |
| App log source ID | app_logs 90日保持と同じ | Security延長対象 |

Cleanupは当日backup成功後、run cutoff固定で実行する。Inbox削除後もquestion `(owner,operation_token)`等の業務UKを破壊しない。

## 13. Metric・alert

- Inbox PROCESSING/COMPLETED/ERROR count、oldest、replay count、token mismatch count。
- API/Web outbox status count、oldest pending、attempt histogram、send/duplicate count。
- Async duplicate ACK、same-token 0200、different-payload 0105、snapshot decrypt/rehydrate failure。
- Warning: outbox 5,000件または5分、critical 9,000件または30分。Fingerprint mismatchは1件からSECURITY/ACTION調査。

Metric labelへowner、token、Message ID、question本文を使わない。IDはlogだけに記録する。

## 14. PT/IT必須crash point

1. DB commit前/後、JMS send前/後、ACK commit前/後を個別にprocess killする。
2. 同Message ID同body、同Message ID異body、別Message ID同token同payload、同token異payloadを比較する。
3. Broker duplicate cache hit/missの両方でConsumer DB UKが重複0を保証する。
4. Outbox send後DB mark前、lease保持process停止、lease expiry後の別dispatcher回復。
5. HMAC current/previous/unknown key、ciphertext改ざん、snapshot最大body/decompression上限。
6. Scenario file replayを朝cleanup前後に行い、stale descriptorを返さない。

## 15. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-021 | HMAC canonical formatをlength-prefixed binary `NKOP1`へ固定 | 区切り衝突・Unicode揺れ・Password単純hashを防止 | Golden HMAC vector、key rotation PT |
| SS-D-022 | Read response snapshotを圧縮後AES-GCMで24時間保持 | DB commit後の厳密replayと機微本文保護を両立 | Inbox容量監視、最大1.05MB CK/PT |
| SS-D-023 | Outbox claimに短leaseを追加しJMS send中DB lockを保持しない | Dispatcher多重起動とDB lock長期化防止 | DDL列、lease crash IT |

## 16. 実装禁止事項

- Operation tokenだけで保存済み結果を返し、owner/layout/target/payload HMACを比較しないこと。
- Password/質問本文の平文・単純hash・canonical payloadをinbox/logへ保存すること。
- Outbox PENDING/ERROR、Inbox PROCESSINGを保持期限だけで削除すること。
- Broker duplicate cacheだけを冪等性正本にすること。
- XA追加、HTTP threadから直接internal Queue送信、outbox未SENTで質問受付成功を返すこと。

## 17. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Inbox/outbox、HMAC canonical、replay、lease、crash recoveryを初版作成。 |
| 2026-08-31 | 横断監査でLGNREQ01の認証前Inbox、HMAC、失敗counter/sessionの同一transaction境界を明記。 |
| 2026-08-31 | 横断監査でHMAC fingerprintを全Requestに必須化し、Inbox response暗号key名をcredential catalogに同期。 |
| 2026-08-31 | 横断監査でLogin UUIDと業務bigintをInbox result referenceで型別に分離し、Scenario再生成元IDを明記。 |
| 2026-09-03 | SSC-006によりOutbox destinationの保存値をUI 242/SS 331/DDLの物理Address allowlistへ統一。 |
