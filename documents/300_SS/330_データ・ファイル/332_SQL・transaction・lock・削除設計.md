# SQL・transaction・lock・削除設計

## 1. 目的・追跡

RepositoryのSQL、page/count、所有者scope、transaction isolation、optimistic/pessimistic/advisory lock、
Outbox lease、論理・物理削除の順序を定める。SQL文の実装は必ずnamed parameterまたはprepared statementとし、入力をSQL文字列へ連結しない。

- 関連UI: 213、223～225、241～242、251
- 関連RD: FUN-003～FUN-013、AUT-001～AUT-004、ASY-001～ASY-009、QST-005～QST-010、
  DAT-003～DAT-011、BAK-006～BAK-008
- 関連SS: [312_処理sequence・method・例外・transaction設計](../310_アプリケーション/312_処理sequence・method・例外・transaction設計.md)、
  [331_DB物理・DDL・index・権限設計](331_DB物理・DDL・index・権限設計.md)
- 関連QA/RDF/UIC: QA-034～QA-040、RDFなし、UICなし

## 2. Transaction共通規則

| 項目 | 設計 |
|---|---|
| Isolation | 既定`READ COMMITTED`。個別の一貫性はrow/advisory lock、CAS、UKで保護 |
| Read-only | 参照serviceは`readOnly=true`。大容量file出力へDB transactionを持ち出さない |
| Command | Inbox INSERT～業務更新～critical audit～Inbox完了を1 transactionで確定 |
| 時刻 | SSC-016: 単一業務操作のservice入口で`Clock.instant()`を1回取得し、その業務状態更新とcritical auditへ同じInstantをbind。受信時刻、Inbox完了（324の保持起点）、response header構築、transaction外Outbox送信確認/失敗は別stageの時刻として区別する |
| Timeout | API同期command 1,500ms、query 1,500ms、batch step 30min、lock timeout API 500ms/batch 5s |
| Retry | DB deadlock/serializationをlistener内で自動loopしない。RollbackしJMS redelivery/inboxへ委ねる |
| Rollback | Checked business errorは予期responseをInbox ERRORでcommit、DB/MQ/I/O例外はtransaction rollback |
| Connection | Open Session in Viewを無効。Template/view層でlazy loadしない |

API requestごとに`SET LOCAL application_name`を変更せず、pool設定のservice名を固定する。
`statement_timeout`、`lock_timeout`、`idle_in_transaction_session_timeout`は342のDB/connection設定を正とする。

## 3. Page・並び順・query構築

- Scenario検索・Logは100件、User・通知・質問回答は50件とし、UI 222～225の機能別page sizeを変更しない。
  `page` 1未満は1、最終page超過は最終pageへ補正し、0件時はpage=1/totalPages=1。
- 画面互換のためpage番号式を使い、`offset = (page - 1) * pageSize`。同一主sort keyの末尾にstable IDを必ず付ける。
- Count SQLとlist SQLは同じpredicate builder/parameter objectから生成し、所有者・論理削除条件の漏れを防ぐ。
- Dynamic sort columnはenum→SQL fragmentのallowlistだけ。利用者入力のcolumn/directionをそのまま挿入しない。
- Scenario以外の新規queryでは`ILIKE` patternは`\`、`%`、`_`をescapeし`ESCAPE '\'`を付与する。検索入力はNFC後のUTF-8 byte上限を先に検査する。

## 4. Scenario・Speaker・Media query

### 4.1 Scenario search（IF-005）

SSC-017: UI223/234の実際の要求は本文/game/話者名/章/type/voice/pageであり、speaker ID/file IDへ置換しない。下記predicateの必要なものだけをallowlist fragmentから構築し、値は全てprepared statementへbindする。Countとlistは同じfilterから一つのSQL statement snapshotで得る（CTE＋lateral等）。通常READ COMMITTEDの別statement間でcount/listをずらさない。

| 条件 | Predicate・bind |
|---|---|
| 本文 | `e.body_search LIKE ?`、NFC/trim後の`%keyword.toLowerCase(Locale.ROOT)%` |
| Game | `g.code = ?`、指定code |
| Speaker | `s.name = ?`、名前完全一致。任意gameとの不一致は0件 |
| 章 | `f.chapter_title ILIKE ?`、`%chapter%` |
| Type | `e.entry_type = ?`、dialogue/narration |
| Voice | `EXISTS/NOT EXISTS`したvoice link。se/bgm/otherは対象外 |

本文/章の`%/_/backslash`はCurrent RepositoryのPostgreSQL LIKE pattern解釈を維持する。literal化は未承認の検索結果変更になるため行わない。値bindによるSQL injection防御とpattern解釈は別問題である。空条件はpredicate自体を除く。

Listは`e.display_order,e.id`順、100件。複数voiceは最小link `display_order,audio_file_id`の1件だけを代表音声にし、countはentry単位。UI234 PAGED48の99,999,900件を超えれば9001。必須line NULL/0、未知enum等は架空値へ補完せず一時整合異常9000、移行検証でも検出する。

SSC-018: 検索/明細で表示するSpeaker名はCurrentと同じFK先`speakers.name`（地の文は未設定）とし、保持用`script_entries.speaker_label`へ置換しない。File/current/前後の表示titleはCurrent `ScriptFileSummary.displayTitle`と同じくchapter、section、file名の順にJava `isBlank()`でない最初の値を使う。NULL/空文字だけをSQL `coalesce/nullif`で処理するとASCII/Unicode空白で結果が変わるため、snapshot row mappingで明示判定する。選んだ非blank値を勝手にtrim/加工せずwire不適合metadataは移行検証へ返す。

### 4.2 Scenario file/detail（IF-003/004）

- File一覧はgame/prefixで絞り`f.display_order,f.id`順、titleはchapter/section/file名の最初の非空値。前後fileは全gameの`g.display_order,f.display_order,f.id`順。
- Detailはfile PK lookup後、UI223に従い`entry_index,display_order,id`順へ1開始Entry sequenceを割当て、同entryのvoice linkを`display_order,audio_file_id`順へ1開始Audio sequenceで展開する。音声なしはAudio sequence0の1record。
- 閾値はentry数ではなく音声展開後のrecord数。200件以下はMQ反復record、201件以上はdescriptor mode。Threshold判定と行取得は同一read-only transaction。
- 最大10,000件をJavaのimmutable snapshotへ取得しcommitした後、`.part`へ固定長recordを書く。超過は`9001`。

### 4.3 Speaker/Media

- Speaker一覧は指定game（未指定は全game）のentryを名前`GROUP BY s.name`で集計し、`count(e.id)` desc、`s.name` asc。同名はgameをまたいでも1候補、wire内部IDは集計対象の`min(s.id)`。Narration/未使用speakerは一覧に出さない。最大500候補超は9001。Routeはgame/prefix集計・prefix昇順、UI223固定map外は未分類、2桁でないmetadataを勝手に補完しない。
- Audioはentry→link `display_order`→audio ID順、Video/MusicはUI 223のdefined category/section/display orderを維持。
- Descriptor queryは`storage_relative_path`をWeb画面に返さず、署名対象のlogical ID/size/hash/MIME/file nameだけ投影する。

## 5. User/Login SQL・lock

### 5.1 Login試行

1. `username_key`でUserを取得し、存在すれば`FOR UPDATE`。
2. IP rowは`INSERT ... ON CONFLICT (client_address) DO NOTHING`後、`FOR UPDATE`。Lock順は常にUser→IPとする。
3. User不存在でも現行encoding IDと同一parameterの固定dummy PBKDF2 hashを必ず照合し、IP counterを更新する。
4. 成功時は両counter/window/lockをclearし、auth sessionをINSERT。User sessionを`FOR UPDATE`で
   `last_accessed_at,id`順に取得し、3件目以降の古いactive rowをREPLACED revoke。
5. 失敗時は15分窓の開始時を確定し、5回到達で`locked_until=:now+15min`。Username存在有無でresult文言を変えない。

### 5.2 Optimistic update

```sql
update schubert.app_users
   set status = :status,
       version = version + 1,
       updated_at = :now,
       updated_by = :actor_id
 where id = :target_id
   and version = :expected_version;
```

1件なら成功、0件ならPKを再読し、不存在は`0104`、version相違は`0105`。Version上限なら
CHECK例外へ依存せず事前検査で`9001`。Password resetとstatus/role変更の成功時は、対象のactive
`auth_sessions`を同一transactionでrevokeする。

### 5.3 Active ADMIN 0人化防止

```sql
select pg_advisory_xact_lock(71419601);
select id
  from schubert.app_users
 where role='ADMIN' and status='ACTIVE'
 order by id
 for update;
```

ADMIN数を減らし得るrole/status操作だけ固定lock key `71419601`を取る。自分の無効化/USER化を拒否し、
更新後のactive ADMIN countを再読して1以上を確認してからcommitする。Advisory lock keyは本用途だけに使う。

## 6. Inbox・operation token

### 6.1 取得順

1. `message_id` rowを`FOR UPDATE`。
2. 無ければowner/operation token rowをpartial UKと同じ条件で`FOR UPDATE`。
3. 両方なければPROCESSINGをINSERT。Unique violationは1回だけ再select。
4. HMACとlayout/owner/targetが一致したCOMPLETED/ERRORはreplay、PROCESSINGは`9000`。不一致は`0105`。

`PROCESSING`はhandlerと同じtransaction内だけ存在し、rollbackで消える。長期PROCESSINGを時刻だけで奪取しない。
Read response snapshotは参照時点のpayloadを暗号化保存し、replay時に現在DBから別内容を作らない。

### 6.2 受付結果のOutbox確認

Question submitはreplayでも`mq_outbox.status`SENTを確認し、PENDING/ERRORならdispatcherを起床して
2秒の残余時間だけ待つ。SENT未確認は既存question IDを作り直さず`9000`。

## 7. Outbox claim・lease

### 7.1 Claim SQLの論理形

```sql
with due as (
  select id
    from schubert.mq_outbox
   where status in ('PENDING','ERROR')
     and next_attempt_at <= :now
     and (lease_until is null or lease_until < :now)
   order by next_attempt_at, id
   for update skip locked
   limit :limit
)
update schubert.mq_outbox o
   set lease_owner = :owner,
       lease_until = :now + interval '10 seconds'
  from due
 where o.id = due.id
returning o.*;
```

Claim transactionはここでcommitし、JMS send中にDB row lockを持たない。`markSent` / `markRetry`は
`where id=:id and lease_owner=:owner`とし、leaseが別workerへ移っていれば上書きしない。

### 7.2 再送schedule

- Application outbox: 1秒、5秒、30秒、1分、以降5分cap。Jitterは±10%だが、初回2秒内の受付確認用sendには入れない。
- Broker redeliveryは321のQA-041/UIC-001承認済み値（1秒、5秒、25秒）を正とし、本application scheduleと混同しない。
- Attempt数上限で自動破棄しない。10回または30分でcritical alert、運用者が原因を解消する。

Web log/revocation outboxも同じclaim形とし、schema/table名と保持仕様だけ変える。

## 8. Async job・取消競合

### 8.1 RECEIVED→PROCESSING

```sql
update schubert.async_jobs
   set state='PROCESSING', started_at=:now, state_changed_at=:now,
       processing_message_id=:message_id,
       retry_count=:delivery_count - 1,
       version=version+1
 where id=:job_id and state='RECEIVED';
```

0件の場合はjobを`FOR UPDATE`で再読し、COMPLETED/ERROR/CANCELLEDは冪等ACK、PROCESSINGは
`processing_message_id`一致のみcrash recovery、不一致は整合errorとする。

### 8.2 取消

```sql
update schubert.async_jobs
   set state='CANCELLED', cancelled_at=:now, state_changed_at=:now,
       version=version+1
 where id=:job_id
   and owner_user_id=:actor_id
   and state='RECEIVED';
```

Workerと取消の更新先着commitが勝つ。取消成功時は同transactionでnotification stateもCANCELLEDにする。
PROCESSING/COMPLETED/ERRORはrollbackではなく業務error`0107`をInbox ERRORでcommitする。

### 8.3 Answer完了

1. Jobを`FOR UPDATE`しPROCESSINGとmessage IDを再検証。
2. `answers(question_id UK)`へINSERT。Unique violation時はexisting answer/provider/timeを検証し、同一なら冪等完了。
3. Job/notificationをCOMPLETED、同じ`:now`でstate_changed/completed/answered_atを更新。
4. Critical auditをINSERTしcommit。

## 9. 所有者・role scopeのSQL強制

| 対象 | USER predicate | ADMIN predicate | 非scope時 |
|---|---|---|---|
| Question list/detail | `q.owner_user_id=:actor_id and q.is_deleted=false` | `q.is_deleted=false`。owner filter任意 | 404/`0104` |
| Question delete | `q.id=:id and q.owner_user_id=:actor_id` | `q.id=:id`。actor role再検証 | 404/`0104` |
| Notification | 常に`n.owner_user_id=:actor_id` | ADMINも本人分の通知操作だけ | 404/`0104` |
| User management | 呼出し自体を禁止 | ADMINのみ、targetはPK | 403/`0103` |
| Log | 呼出し自体を禁止 | ADMINのみ | 403/`0103` |
| Media/scenario | 認証済み全User | 同じ | 401/`0101` |

AuthorizationをControllerとviewに任せず、Repositoryが受け取る`ActorScope`から定型predicateを必ず生成する。
ADMINの全件検索とUSERのowner検索は別query IDにし、`OR (:is_admin...)`で一本化しない。

## 10. Question/Answer論理削除

```sql
update schubert.questions
   set is_deleted=true, deleted_at=:now, deleted_by=:actor_id,
       version=version+1
 where id=:question_id
   and is_deleted=false
   and (:admin_scope or owner_user_id=:actor_id)
returning id, owner_user_id;

update schubert.answers
   set is_deleted=true, deleted_at=:now, deleted_by=:actor_id,
       updated_at=:now
 where question_id=:question_id and is_deleted=false;
```

- SQLの`:admin_scope` literal切替は概念表記であり、実装はADMIN/USER別SQLとする。
- QuestionはAnswer無しでも削除可。Answerがあれば同一transactionでdelete tripleを一致させる。
- Notification/jobは更新しない。Notification detail SQLはquestion削除済み時に本文/answerをprojectionせず「削除済み」表示用flagだけ返す。
- 同じoperation tokenの再実行はInbox/result refから元`deleted_at`を`0200`で返す。

## 11. 朝batchの物理削除

### 11.1 Cutoff・事前条件

Batch開始時の`:run_started_at`を全stepで固定する。当日`BACKUP_DB`/`BACKUP_CONFIG`がSUCCESSでなければ
業務data/inbox/outbox物理削除をSKIPPEDとし、application起動はQA-029に従い続行する。

### 11.2 Notification

Deletion candidateは次のいずれか。

- `state='CANCELLED' and state_changed_at < :run_started_at`（前回日中までの取消）
- `state in ('COMPLETED','ERROR') and state_changed_at <= :run_started_at - interval '24 hours'`

RECEIVED/PROCESSINGは削除しない。`id` 昇順で最大1,000件ずつ別transactionでDELETEし、各chunkを
`batch_runs` countへ加算する。中断後は同じcutoffで再開しても冪等。

### 11.3 Question/Answer aggregate

Candidateは全条件を満たすものだけ。

```sql
select q.id
  from schubert.questions q
 where q.is_deleted = true
   and q.deleted_at < :run_started_at
   and not exists (
       select 1 from schubert.notifications n where n.question_id=q.id
   )
 order by q.id
 for update skip locked
 limit 1000;
```

QuestionをDELETEすればanswer/async_jobはCASCADEする。Notificationは先stepで削除済み、FK RESTRICTも最後の安全網とする。
候補中に新規notificationが作られる業務flowはないが、FK競合はDELETEをrollbackし、次回へ送る。

### 11.4 Technical cleanup順

1. Expired/revoked `auth_sessions`、expired `login_ip_attempts`、expired Web HTTP session。
2. SENTかつsent_atから7日超のAPI/Web outbox。PENDING/ERROR/lease中は対象外。
3. 参照Inboxはcompleted後24時間、更新Inboxは7日。PROCESSING、decrypt/error中、result ref不整合は対象外。
4. App logは90日の保持別定義に従い、`logged_at < :log_cutoff`の行を時刻/ID順に最大10,000件lockする。
   `security_hold_until > :log_cutoff`は保全中としてskip、NULLまたは`<= :log_cutoff`は期限到達として削除する。
   target/deleted/skippedは同lock対象chunkで集計し、保全行の存在を成功件数に隠さない。

## 12. Deadlock・競合防止

| 処理 | Lock順 |
|---|---|
| Login | User → IP attempt → auth sessionsの時刻/ID順 |
| User管理 | ADMIN advisory lock（必要時）→ target user ID → auth sessions ID順 |
| Question submit | Inbox/token → question → job → notification → outbox（新規INSERTのみ） |
| Cancel/worker | job ID → notification ID → answer（完了時） |
| Logical delete | Inbox/token → question ID → answer question ID → audit |
| Cleanup | batch advisory lock → 対象tableのPK昇順。異なtableを逆順lockしない |

DB deadlockが発生した場合は一時障害としtransaction全体をrollbackする。UI更新を内部で再試行せず、
operation tokenによる再操作またはJMS redeliveryで整合を保つ。

## 13. Query plan・性能確認

| Query | Baseline/threshold | 確認 |
|---|---|---|
| Scenario search | 99,661 entry、100件page | selective検索p95 1.5秒以内、stable order、不要seq scanなし |
| Question USER/ADMIN | 同時10名、データはPT造成 | partial btree、論理削除漏れ0 |
| Log search | 90日保持規模 | 日付条件必須、trgm GINの有無をEXPLAIN ANALYZE |
| Notification cleanup | 状態＋cutoff | 1,000 chunkがlock/transactionが後続を防げない |
| Outbox claim | 10,000 row上限 | index scan、SKIP LOCKEDでdispatcher間重複0 |

`EXPLAIN (ANALYZE, BUFFERS, WAL, SETTINGS)`は非本番・個人情報なしの実測dataで行う。Plan証跡はPT/IT結果へ保存し、
テスト用の`enable_seqscan=off`等を本番設定に残さない。

## 14. Error mapping

| SQL/DB結果 | Domain result | 処置 |
|---|---|---|
| PK不存在/scope外 | `0104` | 存在有無の差を出さない |
| Optimistic UPDATE 0件 | `0105` | 現在versionを取得し再表示 |
| Operation token/HMAC不一致 | `0105` + SECURITY log | 保存結果を返さない |
| State CAS 0件 | `0107`または冪等`0200` | 再読状態で決定 |
| Constraint violation（予期UK） | 冪等再読または`0105` | Constraint名をallowlist mapping |
| Deadlock/connection/timeout | `9000` / JMS rollback | 内部SQLを表示しない |
| N12/N9上限 | `9001` | 容量異常としalert |

## 15. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-027 | APIの通常isolationをREAD COMMITTEDとし、必要な整合だけCAS/row/advisory lockで強制 | UI 241のtransaction境界を過度なSERIALIZABLE retryなしで保つ | Repository/PTにlock/crash case |
| SS-D-028 | Active ADMIN保護用advisory lock keyを`71419601`へ固定する | 複数User row間の不変条件を同時操作で守る。外部仕様影響なし | 同時ADMIN更新PT、lock key重複禁止 |
| SS-D-029 | Pageを現行互換のOFFSET式とし、全sortにstable IDを加える | UI 223のpage操作を維持しながら同値順の不安定を除去 | CHR-SEARCH-001/PTでpage境界照合 |

## 16. 実装・試験の禁止事項

- Owner predicateをJava取得後filter、viewのbutton非表示、URL推測困難性で代替しない。
- 大容量file書込、JMS send、外部I/Oの間にDB transaction/row lockを保持しない。
- `SKIP LOCKED`で取れない行を成功扱いしない。Lease期限後へ回す。
- Batchはbackup成功確認なしにnotification/question/inbox/outboxを物理削除しない。
- Test時のDB互換modeやH2でPostgreSQL lock/constraint試験を代替しない。

## 17. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Query、scope、transaction、lock、outbox lease、朝の削除SQLを具体化。 |
| 2026-08-31 | 横断監査でpage sizeをUIの100/50件に機能別統一し、offsetを`pageSize`基準へ是正。 |
| 2026-09-03 | SSC-005を反映し、Security log holdのcutoff判定とtarget/deleted/skipped集計を具体化。 |
