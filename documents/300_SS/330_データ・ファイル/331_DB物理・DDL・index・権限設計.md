# DB物理・DDL・index・権限設計

## SSC396 Current audio roleの実効十一byte（2026-11-15）

BUG2943/YKT2472。Currentの有効movie_audio（11byte）を保存できるよう内部列だけ補正。適用済みV001..029/V002原文は不変、V030後の実効型varchar11/同名byte CHECK1..11とする。DDL/Java/PT/rollback詳細はSS343 SSC396、表示・電文・RD/UIは変更しない。実DB適用・再試験/切戻しはHOLDで未実施、既Backup/原本/role/grantを変えない。

## SSC340 nullable複合CHECKのTRUE確定・V029追補（2026-11-13）

BUG2846/YKT2405、WBS-P004-01.01～03、DAT001～009/UI241242243、PT-DB-NULL340-001～015。既承認の条件付きNN・ペアNULL・状態/参照整合をSQLへ落とす詳細補足であり、列・table・role/grant・index・wire・業務状態・保持期限を追加/変更しない。[PostgreSQL18 CHECK仕様](https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS)では条件のNULLも通過するため、単にnullable値をIN/比較/正規表現/byte長へ渡しただけで条件付きNNを証明してはならない。

次の五制約は正規条件全体のTRUEだけを許可し、FALSE及びNULL/UNKNOWNは23514として拒否する。`IS TRUE`又は同じ三値論理を確実に二値化する明示NN条件を用いる。既存の正常値・正常なNULL組合せと境界は保持する。

|Table / constraint|正規条件・条件付きNN|半端NULLの独立拒否例|
|---|---|---|
|`auth_sessions.ck_auth_sessions_revocation`|未失効はrevoked_at/revoke_reasonともNULL。失効済はrevoked_at NN、revoke_reasonは既6値LOGOUT/DISABLED/PASSWORD_RESET/ADMIN/EXPIRED/REPLACEDのNN。|revoked=true、revoked_at有、revoke_reason=NULL|
|`media_assets.ck_media_assets_pair`|VIDEOはpair_key/pair_roleともNULL。MUSICはpair_role NNでM/I/Nだけ。M/Iはpair_key NNかつ1～256 UTF-8 byte、Nはpair_key NULL。|MUSIC＋M/I＋keyNULL、MUSIC＋roleNULL|
|`notifications.ck_notifications_error`|ERRORは既5値error_code NNとerror_message NN。他stateは両NULL。|ERROR＋codeNULL＋message有|
|`request_inbox.ck_request_inbox_response_snapshot_pair`|body/keyともNULL、又はbody NNで29～1,050,000 byteかつkey NN/既ID format。再構成不可結果のsnapshot必須は324/352の既規則を維持。|ciphertext有＋keyNULL|
|`request_inbox.ck_request_inbox_result_reference`|PROCESSING用の全NULL、NONE＋両refNULL、AUTH_SESSION＋UUIDだけNN、USER/QUESTION/JOB/SCENARIO_FILE＋N12 bigint IDだけNN。state側の条件も従来どおり適用。|USER等type有＋idNULL＋uuidNULL|

V001～028とprovisioning/001_roles.sqlのbyte/checksumを保持し、`V029__strict_nullable_compound_checks.sql`で同名五CHECKをFlyway所有の同一migration transaction内に置換・検証する。NOT VALIDで既データを見逃さず、既存不整合でvalidationが失敗した場合はtransactionをrollbackして旧定義/旧行を保全する。値の推測、理由の補完、半端pairの削除/正規化、既migrationの書換えを行わない。制約数159/24 table、FK/UK/index/role/grant・既成功応答は不変更とし、版29の正常適用・拒否・旧checksum・schema履歴を独立照合する。

NULLを明示的に許すoptional条件、特にQA050のpending_context_revocations.expires_at=NULL（未知期限）は本是正の対象外であり、NULLから削除許可や認可を作らない。SQL外の参照実在/暗号/owner検査もこのCHECKで代替しない。DDL作成/公開・静的確認はDB適用やDB PT合格を意味せず、既存実DB/権限/VM等HOLDは維持する。


SSC310補足（BUG1530/YKT1290、2026-10-20）：SSC200の保持Expiry監査readbackはSS332SSC310に従い、read内owned Statement/ResultSet二scopeで既SSC063199例外順位を維持する。未知provider障害をclose SQLで置換せず、DB不正投影とprovider未知を分離する。DB schema/DDL/grant/SQL/監査全列・元cutoff/同日SUCCESS・query前後guard/借用transactionは不変更。SS343SSC304のsuccessful直下JavaTWRとstage/finish直下契約は別scopeとして維持する。設計反映自体は当source PG/PT・実DB/原本/native成功を意味しない。

SSC201（2026-10-06、SSC200/BUG788/YKT562、実装前具体化）：V028はmaintenance_read_success_progress(uuid,timestamptz,text,timestamptz)をappend-only追加する。引数は元run、原本元cutoff、CLEAN_LOGまたはCLEAN_INBOX_OUTBOX、元SUCCESS ended_at。NULL/非finite/UTC0001～9999外/未知stepは22023、自己backend/現在DB/bigint71419602 Exclusive granted不足は55000。nk_owner/SECURITY DEFINER/search_path=pg_catalog,schubert/TimeZone=UTC、PUBLIC REVOKE・schubert_batchだけEXECUTE。関数はOS/原本/成功rowの権限を授与せず、借用READ COMMITTED TX/同DB排他のもとで固定PK全rowを一度読むだけ。不存在0行、cutoff不一致/END欠落・非finite/END<cutoffまたはEND>元SUCCESS終了/全count非負・算術不一致/cursor NULL契約・Log位置境界不整合は55000。Log全8列とInbox全7列をrow_to_json全row/UTC textとしてSHA256(convert_to(...,'UTF8'))→lowerhex64のproof_sha256 text一列へsealし、cursor/参照ID/秘密のrawを返さない。基表grant/DML/row lock/修復/補完0、新table/index/column0、V001～027不変。累積progressは試行間継承を許すため一試行の件数と安易に同値にせず、完全SUCCESS14列・元原本と別に全保存状態/ENDを照合する。独立fixed JSON hash・全拒否・権限と旧migration hash/SQL後条件をPTし、同新source DB/BOM schema許可/Backup検査/nativeを横断する。

SSC200（2026-10-06、BUG788/YKT562、実装前補足）：§8.3の非backup同business_date/step既SUCCESS→新SKIPPED/ALREADY_SUCCESSFUL/all0を維持する。Cleanup/Expiryの元成功照合はsame-runだけに限定しない。同日/stepの唯一SUCCESS、異なるrow id・小さいattempt・元終了≦今回開始、完全14列/元run UUID・元anchor cutoff・固定summary/count/time/nullを実再読する。元cutoffは親保持原本SessionのUUID限定completed-run readonly lookupからのみ受け取り、DB rowのstarted_at/expiry_cutoff_at等から原本を推測しない。現在DB/advisory/原本/currentと元原本を各前後再照合し、借用Connection設定/commit/close禁止及びSSC063199 resource precedenceを維持する。元Log END/full progressとInbox full summary/cursorは元run/cutoffで別再読し、現在SKIPを元auditの更新や新件数にしない。Expiry元auditは元cutoff−7日・完全SUCCESS/ended一致、fresh selectorは現在cutoff−7日でselected=0だけを許し、非0/不明は起動拒否・SKIP保全、再purgeしない。新SQLは固定table/parameter・既role内SELECTのみに限定し、DDL/grant変更が必要な場合は本台帳で別具体化・append-only/独立権限PTを先行する。これはSSC117125126のsame-run前提だけを上書きする内部補足で、日次SKIP/Backup一意世代/既データ互換は不変更。

SSC155具体化（PG/PT、2026-10-01、V025実装前）：業務最終QWKのerror閉集合は`QUESTION_RETRY_EXHAUSTED`のみ（provider本文/例外文字列は保存しない）。detectedAtはUTC/PG µs、0001～9999の有限値をworkerで採取する。通常ASYNC rowはDLQ metadata5列すべてNULL、DLQ rowは全有値・QWKREQ01/001/320byte・dispatch D!=元Wとする。`uq_mq_outbox_dlq_original`は元Wのpartial UK。UPDATE triggerは既存DLQの5metadata/dispatch identity/correlation/destination/layout/body/created_atを不変にし、status/lease/retry/last_error/sent_at更新だけ許す。triggerはinvoker、search_path固定、PUBLIC実行権限をREVOKEし、既存role/grantを増やさない。旧DLQに真正metadataが無ければV025全体を拒否し、推測補完しない。既存workのUK/受付SENT証明・既存V001～024・既存table数23は不変更。

SSC152の旧state変換前検査：ACCEPTED notificationに対応するjobがRECEIVED以外なら、状態を推測修復せずV024全transactionを失敗させる。元row/constraint/Flyway履歴を保持して整合調査へ回す。正常legacy RECEIVEDだけRECEIVEDへstate-only変換する。新Job/通知mutationは同じtransactionで双方stateを確定する。

SSC152/155（PG/PT、2026-10-01、実装前）：notifications.stateはUI242のJob stateと同じRECEIVED/PROCESSING/COMPLETED/ERROR/CANCELLEDであり、notification_type ACCEPTEDとは別。V003履歴byte/checksumは不変更、append-only V024で旧state ACCEPTEDをRECEIVEDへ整合しcheckを置換、type/row identity/owner/body/time/version/grantは不変更。mq_outbox業務QWK最終DLQの追加profileは後続append-only V025に限定する。専用nullable列dlq_original_message_id uuid、dlq_original_transport_id varchar(128)、dlq_delivery_count integer、dlq_error_code varchar(32)、dlq_detected_at timestamptzを持ち、ordinary全NULL、DLQ QWK001/320byte全有値・元W!=dispatch message_id・count>=1・ASCII printable ID1～128・closed uppercase code・finiteUTCをcheck、元W partial unique indexを設ける。既存incompatible DLQ QWK rowを推測補完せずmigration失敗として保護。既存message_id UKと一般Outbox、role最小grantを維持し、DLQ送信retryでは専用列を変更しない。実SQL/check/旧履歴・原本・role・crash独立PT前は未完。

## 1. 目的・適用範囲

PostgreSQLの物理object、column型、default、PK/FK/UK/CHECK、index、schema/role/grantをPG工程で
version付きmigrationへ転記できる粒度で定める。本書はDDL実装そのものではなく、DDL生成・review・testの正本となる物理仕様である。

- 上位設計: [241_DB論理構成設計](../../200_UI/240_データ/241_DB論理構成設計.md)、
  [242_主要テーブル・制約設計](../../200_UI/240_データ/242_主要テーブル・制約設計.md)
- 関連RD: DAT-001～DAT-011、AUT-001～AUT-004、ASY-001～ASY-009、QST-007～QST-010、
  BAK-001～BAK-008、MIG-001～MIG-008
- 関連QA/RDF/UIC: QA-010、QA-013～QA-014、QA-024、QA-034～QA-040、QA-043、RDFなし、UIC-003
- 関連SS: [323_全電文layout・Java・DB対応表](../320_メッセージング/323_全電文layout・Java・DB対応表.md)、
  [324_Outbox・Inbox・冪等性・再送設計](../320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md)

## 2. Database・命名・型の共通規則

| 項目 | 物理仕様 | 根拠 |
|---|---|---|
| DBMS | PostgreSQL 18系の構築時最新minor、DB `schubert_nk`、UTF-8 | UI 241 §2、DAT-001 |
| Timezone | DB永続化は`timestamptz`、DB/session timezoneは`UTC`、表示・電文変換は`Asia/Tokyo` | UI 241、232、MSG-011 |
| 命名 | schema/table/column/index/constraintはlower snake_case、identifierは63 byte以内 | DAT-002 |
| ID | 電文N12対象は`bigint generated by default as identity`かつ`1..999999999999`のCHECK、identity sequenceもMAXVALUEを同値 | UI 242 §10.1、MQ-034 |
| Version | `bigint not null default 0 check (version between 0 and 999999999)` | UI 242 §10.1 |
| UUID | PostgreSQL `uuid`、Java `UUID`、生成はapplication側のCSPRNG | UI 242、323 |
| ハッシュ | SHA-256/HMAC-SHA-256のhexは`char(64)`、`check (value ~ '^[0-9a-f]{64}$')` | MQ-007、FIL-004 |
| 電文ID | `char(8)`/`char(3)`とし、layoutは`^[A-Z0-9]{8}$`、versionは`^[0-9]{3}$` | UI 232～236 |
| 本文byte数 | DB CHECKは`octet_length`を使い、JavaのNFC・control文字検査と二重化 | DAT-004、MSG-003 |
| 日時 | 作成/更新日時は`not null`、DB defaultは`clock_timestamp()`ではなくtransaction内で共通`Instant`を明示bind | DAT-004 |
| JSON | `jsonb`は監査detailsの定義済みkeyのみ。任意業務dataの逃げ場にしない | MON-003、OPS-005 |

Booleanと状態の不整合はCHECKで防ぐ。例えば`is_deleted=false`なら`deleted_at/deleted_by is null`、
`is_deleted=true`なら両方not nullとする。Stateごとの時刻columnは§8のCHECKで保護する。

## 3. Schema・extension・role・grant

### 3.1 Object

| 種別 | 名前 | Owner | 用途 |
|---|---|---|---|
| Schema | `schubert` | `nk_owner` | API/batchの業務table |
| Schema | `schubert_web_session` | `nk_owner` | Web technical session/outboxのみ |
| Schema | `schubert_meta` | `nk_owner` | Migration history |
| Extension | `pg_trgm` | DBA | 本文・logの部分一致GIN index |

`public` schemaの`CREATE`は`PUBLIC`からrevokeする。Application roleの`search_path`は使用schemaと`pg_catalog`を
明示し、DDLとSQLはschema修飾名を原則とする。

### 3.2 Role matrix

| Role | LOGIN | 権限 | 禁止 |
|---|---:|---|---|
| `nk_owner` | no | Schema/object owner。Migrationから`SET ROLE` | Service login |
| `schubert_migration` | yes | `nk_owner`への限定`SET ROLE`、migration時のみcredential配布 | 常時service利用 |
| `schubert_app` | yes | `schubert`のtableに必要なSELECT/INSERT/UPDATE/DELETE、sequence USAGE、非業務metadataの固定startup投影EXECUTE | Web schema、DDL、role変更、schema history直接SELECT |
| `schubert_batch` | yes | `batch_runs`の直接DML、allowlist済みmaintenance functionと非業務metadata固定startup投影のEXECUTE | その他tableの直接SELECT/DML、DDL、Web session/API Inboxのciphertext・復号key |
| `schubert_backup` | yes | Dump対象schema/table/sequenceのUSAGE/SELECTだけ | DML、maintenance function、DDL、SET ROLE、復号key、backup unit以外からのcredential利用 |
| `schubert_web_session` | yes | 同名schemaの既存3 tableだけDML＋QA048受付参照tableのSELECT/INSERT/DELETE、非業務metadata固定startup投影EXECUTE | `schubert`のUSAGE/SELECTを含む全権限、schema history直接SELECT |
| `schubert_ops_ro` | yes | 監視viewと非機密columnのSELECT | password/token/ciphertext/body、DML |

- Default privilegeもownerで明示grantし、`PUBLIC`へのtable/sequence/function権限を与えない。
- `schubert_ops_ro`は基底tableではなくsecurity-barrier viewを読む。本文、ciphertext、hash、IPはviewから除外する。
- QA-043/UIC-003承認に基づき、`schubert_backup`は`schubert-nk-backup.service`専用credentialとし、
  `schubert`、`schubert_web_session`、`schubert_meta`のdump対象objectへ明示grantする。`pg_read_all_data`やowner membershipは与えない。
- Backup roleはSELECTできるためciphertext自体は取得可能だが、AES keyを一切配布せず不透明dataとして保全する。
  対話利用をDB権限だけで禁止できるとは記述せず、専用OS user、credential mode、固定unit、監査で補強する。

### 3.3 Batch maintenance function

SSC095/PG312: 起動schema照合は引数なし `schubert_meta.startup_schema_history()` の六列installed_rank/version/type/script/checksum/successだけとする。SQL STABLE SECURITY DEFINER、owner nk_owner、search_path pg_catalog,pg_temp、history完全修飾、PUBLIC全revoke→app/web/batchへmetaUSAGE＋完全signature EXECUTEのみを同一migration transactionで配備する。失敗行/NULL versionをfilterしない。履歴tableのSELECT/任意metadata function/CREATE/owner追加はしない。V005は変更せずV023 append-only、DB fixtureで許可/禁止権限と全行を独立照合する。

`schubert_batch`の削除権限は、次の定型functionのEXECUTEだけに限定する。

| Function | 対象 | 主な引数 / 戻り値 |
|---|---|---|
| `schubert.maintenance_cleanup_notifications` | Notification | `run_id uuid, cutoff timestamptz, limit integer` / 対象・削除・skip件数 |
| `schubert.maintenance_cleanup_questions` | Question/Answer | 同上 / 集約別件数 |
| `schubert.maintenance_cleanup_sessions` | API/Web technical session | 同上 / schema別件数 |
| `schubert.maintenance_cleanup_message_stores` | Inbox/Outbox | 同上 / table別件数 |
| `schubert.maintenance_cleanup_logs` | App log | 同上 / 削除・hold skip件数 |
| `schubert.maintenance_cleanup_batch_runs` | Batch run | 同上 / 削除・調査中skip件数 |

Function ownerは`nk_owner`、`SECURITY DEFINER`、function固有の`SET search_path = pg_catalog, schubert, schubert_web_session`とする。
Schema/table名を引数にせず動的SQLを禁止し、`cutoff`/`limit`と当日backup gate・advisory lock/run IDをfunction内で再検証する。
`REVOKE ALL ON FUNCTION ... FROM PUBLIC`後、完全signature単位で`schubert_batch`にEXECUTEをgrantする。返却は件数と理由codeだけとし、
本文・ciphertext・pathを返さない。`batch_runs`記録とchunk transactionは341/332に従い、その他tableの直接DML grantは0とする。

### 3.3.1 共通cutoff契約（SSC-050、PG-D-129）

上表の全functionのcutoffは固定run_started_atであり、保持日数を差し引いた値ではない。内部でlog_cutoff = cutoff - 2160 hours、batch_run_cutoff = cutoff - 9600 hoursを導出する。signature/roleの追加・任意保持値引数はない。V013で旧5関数をappend-only置換し、全7 cleanupを既存maintenance_lock_inbox_backupへ統一する（名前は互換のため維持、owner内部helper）。

NULL/非有限cutoff・limit範囲外は22023。advisory競合は0/0/0/LOCK_BUSY、同run/JST当日/ended_at非NULL/SUCCESSのBACKUP_DB・BACKUP_CONFIGがlock済単一snapshotで揃わなければ0/0/0/BACKUP_GATE。他のSQL障害は伝播し全chunk rollback。全7関数は固定search_pathとTimeZone=UTCを持ち、所有者nk_owner/PUBLIC非許可/batchだけEXECUTEを維持する。DB gateだけでbackup実体・OS lock・通常API/Web停止確認が済んだとはしない。

Logはlogged_at < log_cutoffだけcandidate、hold > log_cutoffはskip（SS332/SSC-005維持）。Batch履歴はended_at < batch_run_cutoffかつ終了SUCCESS/WARNING/SKIPPEDで、現在run・終了NULL・同runにRUNNING/FAILEDがある調査対象は保持し、ended_at/id順でlockする。開始から400日でも終了400日未満は削除しない。保持値はUI251 §6に一致し変更しない。旧3引数を使う既存未実装callerもrun開始で呼ぶ。DB-011の旧閾値混用oracleを上位仕様に合わせて修正し、独立±1μs matrixを追加する。

### 3.4 Inbox検査用最小権限（SSC-049/QA-046）

UIC-006の保守検査主体はbatchとは別の専用DB roleを使用する。必要なInbox snapshot/参照先の読取りと固定保守functionだけを許可し、任意DML/DDL、他roleへのSET ROLE、Web session/schema、password hashの読取りを許可しない。batchの現行権限は増やさない。既存migrationは変更せずappend-onlyで反映する。暗号検査部品のtrueだけでSQL DELETEしてはならない。参照・期限・backup・競合保護の検査も必要である。

最初の認証参照検査用DB境界はPG-D-121/PT-DB-INBOX-017～024に対応する。`schubert_inbox_inspector`はLOGIN、NOSUPERUSER/NOCREATEDB/NOCREATEROLE/NOREPLICATION/NOBYPASSRLS、owner membershipなし。CONNECT/USAGE schubertと次の権限だけを追加する。credentialは検査process専用で、本番値はGitへ置かない。

| Object | 検査roleの許可 | 禁止/限定 |
|---|---|---|
| `maintenance_next_auth_inbox(uuid,timestamptz,uuid)` | EXECUTE。run_id、固定cutoff、after_message_id（最初はNULL） | PUBLIC/app/batch/Web/backup/opsへEXECUTEしない。最大1行、LGN/LOG応答だけ |
| `auth_sessions` | SELECT列: id,user_id,created_message_id,context_hash,context_ciphertext,key_version,issued_at,revoked,revoked_at | 任意DML/DDLなし。expires_at/last_accessed_at/client_address等の不要列を追加しない |
| `request_inbox`基底table、app_users/password、Web schema | V008時点は直接権限なし。追加は3.6のid/version列だけ | Inboxは候補functionだけから読む。認証user/password queryは呼ばない |

候補functionはnk_owner所有/SECURITY DEFINER、固定search_pathとUTCを設定。run_id/cutoff必須、無限cutoff拒否、advisory xact lock 71419602取得、同run・cutoffのJST business_dateのDB/config backup SUCCESS（ended_at必須）を確認してbackup行をID昇順FOR SHARE。未達は固定SQLSTATE 22023/55P03/55000で失敗し秘密値を例外へ出さない。
`processing_state IN (COMPLETED,ERROR)`、LGN/LOG response、`expires_at < cutoff`、`message_id > after`の候補をMessage PK昇順で1行だけFOR UPDATEし、AUTH_SESSION参照があれば当該auth_sessionsをFOR SHAREする。全Inbox列は既存composite型で検査processだけへ返す（SQLは明示列）。snapshot/参照欠落はJava検査で保持し、SQL単体で復号・整合合格としない。直接base table SELECTも不要。
callerの明示transaction中に構造/認証参照検査を行い、終了までlockを保持する。autocommit呼出しで返った行を将来のlock保証に使わない。最終DELETE/非認証候補/固定runの再実行状態/oneshotは別の未完了gateで、候補取得functionの実装だけでBUG-014を完了にしない。

BUG-080/YKT-071: backup判定はFOR SHAREした同一query結果のstep集合だけを使う。別statementのEXISTSで新しいSUCCESSを追加採用しない。lock待ち中に別backupが完了した場合は当該snapshotでは55000として保持し、次transactionで両行を取得し直す。[PostgreSQL 18 row locks](https://www.postgresql.org/docs/18/explicit-locking.html)のtransaction寿命とREAD COMMITTEDを前提に、PT021で実DBのlock待ちを観測してsnapshot境界を固定する。単に存在検索が成功しただけでlock取得とみなさない。

### 3.5 認証Inboxの条件付き削除（SSC-049/QA-046、PG-D-122）

V009をappend-only追加し、`maintenance_delete_auth_inbox(run_id uuid, cutoff timestamptz, message_id uuid, expected_xact text, expected_response_sha256 bytea) RETURNS boolean`だけを検査roleへEXECUTE許可する。nk_owner/SECURITY DEFINER、固定search_path/UTC、PUBLIC・他service roleのEXECUTE禁止、直接DML禁止を維持する。

callerは3.4の候補取得時に同じSQLから`pg_current_xact_id()::text`と`sha256(response_body_encrypted)`を内部に保持する。検査成功後、同一所有transaction・同じrun/cutoffでだけ削除関数を呼ぶ。関数はNULL/非有限cutoff/非decimal transaction ID/32byte以外のhashを22023、transaction ID不一致をfalseとして拒否する。その後71419602と同一locked queryによるbackup gateを再確認し、Message一致・暗号文SHA-256一致・完了state・LGNREQ01/LGNRSP01またはLOGREQ01/LOGRSP01・両version001・tokenなし・owner形態・NONE/AUTH_SESSION参照形態・有限日時・created<=completed・expires>=completed+168時間・expires<cutoffを全て満たす1行だけ削除する。実削除1=true、非該当/既削除=false。固定run/cutoffはprocessの不変run recordを使用し、関数へ別日時を差替えない。

SQL自体はAES/HMAC検証器ではない。専用processが検証前にこの関数を呼ばないこと、候補/参照/backupのlockを検証開始からcommitまで保持することをJavaの所有境界とPTで保証する。transaction IDはtop-level IDでSAVEPOINT rollbackの証明にはならないため、所有serviceは新規connectionを外へ公開せずSAVEPOINT/外部callback/途中commitを使用しない。検査credentialを奪った任意SQL主体への暗号証明をこの関数が提供するとは主張しない。V001～008は変更しない。V006の汎用Inbox削除の置換と全layout結線は別の残件であり本追加だけでBUG-014を完了にしない。

対応PT-DB-INBOX-025～032はSQLの全引数/条件/権限/lock/再実行・正常削除のmatrix。Javaの検査接続は別PTで認証の正常/不整合/故障/並行を検証する。

### 3.6 全候補走査と24応答の限定削除（SSC-049、PG-D-124、V010）

V010で`maintenance_next_inbox(uuid,timestamptz,uuid)`と`maintenance_delete_inbox(uuid,timestamptz,uuid,text,bytea)`を追加し、検査roleだけへEXECUTEする。所有/固定search_path/UTC/SQLSTATE・1行/固定run/cutoff/top-level transaction/hash・SAVEPOINT禁止・SQLだけでは暗号証明にならない制約は3.4/3.5を継承する。V008/V009は認証限定の既存contractとして変更せず維持する。

共通内部`maintenance_lock_inbox_backup(uuid,timestamptz)`はSECURITY INVOKER、PUBLIC/検査role/他serviceへEXECUTEを与えずnk_ownerのdefiner関数からだけ呼ぶ。NULL/有限cutoff、71419602、同run/JST日付/ended_at付きDB/CONFIG SUCCESSを単一locked queryで確認する。失敗22023/55P03/55000、backup snapshot途中追加を採用しない。外から共通helperを呼べたことを削除前検証とみなさない。

候補はlayoutを限定せずCOMPLETED/ERRORかつexpires<cutoffをUUID昇順1行FOR UPDATEする。未知/未実装layoutもJavaで保護WARNINGとして数えられるよう返す。PROCESSING・未期限は候補外。参照type AUTH_SESSION/USER/SCENARIO_FILEだけ、それぞれauth_sessions.id/app_users.id/script_files.idをFOR SHAREして返す。不在参照はJavaがfalseとする。Question/JOB等は参照検査未実装として保持し、この段階では削除許可しない。

追加SELECT列はapp_users(id,version)、script_files(id,game_id)だけ。任意DML/DDL、password/username/role/status、master本文・path/hash、base Inbox、Web schema、SET ROLE禁止を維持する。User/Scenario参照の明示CASTはJava projection用でありDDL型を変えない。

条件付き削除の許可routeはLGN/LOGとSS324 §12.4の22種、計24 canonical REQ01/RSP01対応だけ。LGN ownerなし、その他owner必須。LGN/LOGとquery17種はoperation_tokenなし、User更新5種はtoken必須。両version001、同Message/ciphertext hash、完了state、有限created/completed/expires、created<=completed、expires<cutoffを要求する。最短保持はLGN/LOG/User更新5種168時間、query17種24時間。NONE/型付き参照の形態はDDLとSQLで検査し、実応答codeとの参照整合は同transactionのJava検査を必須とする。認証はNONE/AUTH_SESSION、User更新はNONE/USER、SCNはNONE/SCENARIO_FILE、他queryはNONEだけ。対象外/再削除=false。

PT049～056で実SQL全引数/分岐/各24route/token/owner/ref/期限境界、最小列権限/禁止42501、参照とbackup/advisory競合、rollback/同run再走、未知候補保持・PROCESSING除外を検証する。migration inventory期待値は承認された追加に合わせ10へ更新し、旧1～9のhashを保全する。SQL matrixをJava coverageと偽らない。Java全候補の原子的検査接続・oneshot・V006置換は後続gateでありV010だけでBUG-014を閉じない。

### 3.7 通常batchからのInbox削除迂回を廃止（SSC-049、PG-D-126、V011）

QA-046承認済みの実行主体分離をV011で具体化する。V001～010は不変とし、既存signatureのmaintenance_cleanup_message_stores(uuid,timestamptz,integer)をOutbox専用に置換する。schubert_batchのEXECUTEは維持するが、本関数はrequest_inboxを読み書きせず、全state/layout/暗号/参照のInboxをそのまま残す。Inbox件数をOutbox chunk件数へ合算しない。検査processの未起動/失敗を本関数のOKで代替せず、341の親processが必須の検査stepを別途実行・確認する。

API mq_outbox→Web web_log_outboxの順にID昇順FOR UPDATE SKIP LOCKED、合計limit 1～1000。SENTかつsent_at < cutoff−168時間、lease_until IS NULLまたは<cutoffだけを削除する。期限同値/未来/lease中/PENDING/ERRORを保持。NULL/非有限cutoff/不正limitは22023。V010内部helperのadvisory/同run/JST日付/成功backup単一locked snapshotを共用し、55P03は従来の0/0/0/LOCK_BUSY、55000は0/0/0/BACKUP_GATEへ閉じたcodeだけ変換する。他例外は伝播しtransaction rollback。返却target/deletedは実Outbox削除件数、skipped0、OKはOutboxの本呼出し成功だけを表す。行lock待ちをSKIPした候補を成功件数へ加算しない。

owner nk_owner、SECURITY DEFINER、固定search_path/UTC、PUBLIC/他service EXECUTEなし、通常batchのInbox/base table権限追加なし。動的SQL/汎用table引数/任意検査済flagを設けない。V008～010の専用検査関数はそのまま。PT065～072と旧DB/Outbox回帰で、Inbox全保持、Outbox境界/chunk/rollback、backup集合の途中追加/競合、権限・全DELETE経路の役割を確認する。旧PT-DB-011の不正Inbox削除期待は、承認済みBUG-014修正として保持2行/Outbox0削除へ変更し根拠を残す。全run/oneshot/参照未対応が残るためBUG-014/YKT-012を閉じない。

### 3.8 Inbox検査の永続checkpoint（SSC-049、PG-D-127、V012）

run単位の再開状態をDBの非秘密tableに置き、各候補の削除/保護判定とcheckpoint更新を同じ所有transactionでcommitする。OS runtime fileや別transactionの件数保存を削除確定の証明にしない。通常業務tableの仕様は変えず、同run/cutoffの再開と別attempt記録の責務を分離する。

| inbox_inspection_progress列 | 型・制約 |
|---|---|
| run_id | uuid PK。batchの固定run ID。任意の公開session/tokenではない |
| cutoff | timestamptz NOT NULL、finite。初回値不変 |
| after_message_id | uuid nullable。DBのUUID順cursor、最初NULL |
| inspected_count | bigint NOT NULL default0、>=0 |
| deleted_count | bigint NOT NULL default0、0..inspected_count |
| protected_count | bigint NOT NULL default0、inspected_count−deleted_count |
| completed_at | timestamptz nullable、非NULLならfinite。ENDだけで設定 |

PK名pk_inbox_inspection_progress。CHECK名ck_inbox_inspection_progress_cutoff/counts/cursor/completed。inspected_count=0とcursor=NULLを同値にする。部分index ix_inbox_inspection_progress_completed(completed_at,run_id) WHERE completed_at IS NOT NULL。base tableの通常API/Web/batch/検査roleのSELECT/DMLは全0。V005 defaultで継承されるschubert_app権限は新tableだけ明示REVOKEする。owner nk_ownerと既存全schema backup用schubert_backupのSELECTだけを維持し、backup復元に進捗を含める。backupへのDML/検査EXECUTEは許可しない。秘密・ciphertext・復元応答・参照id・理由詳細を保存しない。DDL増分は22table、PK22、CHECK149、既存FK23/UK30/trigger1は不変として独立inventoryへ明記する。

- maintenance_open_inbox_inspection(run_id,cutoff)は検査roleだけのSECURITY DEFINER。V010 helperで固定backup/advisoryを確認し、初回INSERT ON CONFLICT DO NOTHING後に当該progressをFOR UPDATE。保存cutoffとの不一致は55000。既完了なら状態を返すだけで再走・件数初期化しない。current transaction IDはJavaが同じSELECTから保持する。
- maintenance_record_inbox_inspection(run_id,cutoff,expected_after uuid,expected_count bigint,message_id uuid,outcome text,expected_xact text)は検査roleだけ。同run/backup/lock/transaction、cursor/count一致を再確認。NULL/不正count/非decimalxact/未知outcome・message形態は22023、stale状態/cutoff/xact/既完了は55000。許可outcomeはDELETED/PROTECTED/ENDだけ。DELETED/PROTECTEDはDB UUID順でcursorより後、count+1、対応countだけ+1。DELETEDは当該Message不在、PROTECTEDは期限済完了行の存在を追加確認する。ENDはmessage=NULLかつcursor以後に期限済完了候補なしだけを許可し、completed_atをDB時刻で記録する。算術overflow/SQL障害は削除もcheckpointもrollback。これら条件は暗号証明ではなく専用Java所有transactionを必須とする。
- maintenance_cleanup_inbox_progress(run_id,run_cutoff,limit)は通常batchだけ。backup/advisoryを共用、finite cutoff/1～1000を検査。completed_atがrun_cutoff−400日より古く、別run、同runのRUNNING/FAILED batch_runsがない完了状態だけ、completed_at/run_id順FOR UPDATE SKIP LOCKEDで最大limit削除。未完了/調査中/期限同値・未来を保持。返却count/OK、0/LOCK_BUSY、0/BACKUP_GATEの閉形式をV011と共通にする。他例外は伝播。親のCLEAN_BATCH_RUN内で従来履歴清掃と別のbounded chunkとして呼び、件数を混同しない。

全3関数は固定search_path/UTC、PUBLIC/他service EXECUTEなし、任意table/path/SQL引数なし。V001～011はappend-only不変。通常batchの検査・Inboxアクセス権限を増やさない。全runの状態は再起動後もDBから取得し、親batchのattempt件数は起動時と終了時の累積差分、run累積値は別項目として二重計上しない。commit結果不明時は同runで再読取りするまで成否/件数を推測しない。

PT073～080はSQLの全状態遷移・制約・権限・atomic rollback/lock・保持400日・migrationを検証する。Java接続は別PT081～088、oneshot/親processは後続gate。完了progressだけで正常API停止・backup実file検証・鍵配布・IT/STが完了したとは判定しない。

### 3.9 Log保全行を含む永続走査（SSC-051、PG-D-136、V014）

BUG-104の先頭hold反復を解消するため、V001～013は変更せず非秘密table log_cleanup_progressを追加する。業務log内容/保持値/hold条件は変更しない。

| 列 | 型・条件 |
|---|---|
| run_id | uuid NOT NULL PK pk_log_cleanup_progress |
| cutoff | timestamptz NOT NULL、finite。初回固定run_started_at |
| after_logged_at / after_id | timestamptz / bigint、初回ともNULL、以降走査済み最後の(logged_at,id) |
| target_count / deleted_count / skipped_count | bigint NOT NULL default0、非負、deleted<=target、skipped=target−deleted |
| completed_at | timestamptz nullable、END時だけfinite値 |

CHECKはck_log_cleanup_progress_cutoff/counts/cursor/position/completedの5個。cursorは日時/IDのNULL同値かつtarget=0と両NULLを同値、positionは非NULL時finite日時・logged_at<cutoff−2160時間・id1..999999999999。完了日時finite。部分index ix_log_cleanup_progress_completed(completed_at,run_id) WHERE completed_at IS NOT NULL。owner nk_owner、PUBLICとdefault継承app権限はREVOKE、backup SELECTだけ維持、通常API/Web/batch/検査roleの基底SELECT/DMLなし。独立inventoryは23table/PK23/CHECK154、FK23/UK30/trigger1不変。

- maintenance_cleanup_logs(uuid,timestamptz,integer)の4出力signatureを維持。入力finite/limit1..10000、既存同run/JSTbackup/advisory gateの後に同run progressを初回INSERTしFOR UPDATE、cutoff不一致55000。既完了は0/0/0/OK。以後(logged_at,id)>cursorの保持期限済行を昇順最大limit選び、hold込みtarget・削除・skipのdeltaと最後のcursorを同transactionで保存する。target0でだけcompleted_atを確定。holdを削除せず一度だけ数え、同run再開時に再集計しない。既完了後の再検査は新runを使う。
- 永続cursorが未取得行を飛び越えないよう、Log候補だけFOR UPDATE NOWAITとする。row lock競合は当chunkのINSERT/DELETE/checkpointを例外blockでrollbackし0/0/0/LOCK_BUSY、cursor/累積不変、完了扱い禁止。通常削除候補を消すだけの他cleanupのSKIP LOCKEDは変更しない。任意privileged writerによる過去logged_at差替え/過去行追加が並行する状況を全件保証しない。通常API/Web停止・親OS lock条件は必須。
- maintenance_read_log_cleanup_progress(uuid,timestamptz)は同backup/advisory、finite入力、cutoff一致を確認し、累積target/deleted/skippedとcomplete booleanだけを返す。未開始は0/0/0/false。cursor/log ID/本文/秘密を返さずtable自体のgrantを追加しない。親はattempt前後の累積差分で記録し、commit成否不明時は同runで再読取りする。
- maintenance_cleanup_log_progress(uuid,timestamptz,integer)はlimit1..1000、既存gate、400日超の完了行だけをcompleted_at/run_id順SKIP LOCKEDで削除する。現在run、未完了、同runにRUNNING/FAILEDの調査対象、期限同値/未来は保持。既存inbox progressと同条件・別bounded呼出し。全8 cleanupのgateをPTで照合する。

3関数はnk_owner/SECURITY DEFINER/固定search_path=pg_catalog,schubert,schubert_web_session/UTC、PUBLIC非許可・batchだけEXECUTE。新2関数も完全signatureでgrant。算術overflow/他SQL異常は伝播し削除と進捗をrollback、NPE/null/未開始を完了へ変換しない。旧functionのhold再計上を期待したPT095/DB011は本修正の承認済み独立oracleへ更新し、旧V013反例はrollback-onlyで別検証する。

### 3.10 照会4routeの条件付き削除追加（SSC-049、PG-D-139、V015）

V001～014を不変としmaintenance_delete_inboxの既存signature/owner/SECURITY DEFINER/search_path/UTC/EXECUTE権限を維持してNTSREQ01/NTDREQ01/QSSREQ01/QSDREQ01だけ追加する。合計28 route。4種はowner必須・operation_tokenなし・REQ/RSP両version001・NONE参照のみ、最短24時間・expires<cutoff。既存認証2/更新5の168時間と参照条件は不変。任意table/SQL引数、新table/列/role/grantなし。

Javaの同transaction内snapshot検査はSS324 §12.8を正とし、SQLだけで暗号完全性を主張しない。未検証QSB/NTC/QDL、誤route/version/owner/token/ref/hash/transaction、未backup/lockは削除不可。既存V010の全引数/WHERE/SQLSTATE回帰に加え041/PT161～168で4種のactual deleted/protected/ENDと独立時刻/role/rollback後条件を確認する。

### 3.11 質問更新の最小参照・限定削除（SSC-049/052、PG-D-141）

9535086fで変更前登録。V016 append-onlyで324 §12.9の参照検査を支える。V001～015を変更せず、通常batch/他serviceへのInbox鍵・本文・DML権限は追加しない。

- `maintenance_next_inbox`のQUESTION参照はquestionsをFOR UPDATE、存在するanswers/async_jobsをPK順FOR SHAREする。JOB参照はasync_jobsをFOR UPDATE、存在するnotificationsをPK順FOR SHAREする。親rowのFOR UPDATEはFKによる子INSERTも阻止し、Answer/Notification不存在確認のphantomを削除まで防ぐ。見つからない親を補完しない。
- 検査roleへの列SELECTはquestions `(id,owner_user_id,operation_token,receipt_id,submitted_at,is_deleted,deleted_at,deleted_by,version)`、async_jobs `(id,question_id,owner_user_id,message_id,correlation_id,received_at,state,state_changed_at,cancelled_at,version)`、answers `(question_id,is_deleted,deleted_at,deleted_by)`、notifications `(job_id,question_id,owner_user_id,state,state_changed_at)` に限定。本文・password・Userの現在roleは不要で追加しない。
- `maintenance_read_question_work(uuid)`は検査roleだけEXECUTE可能なnk_owner/SECURITY DEFINER、固定search_path/UTC、NULL拒否の限定projection。元受付Correlation・nk.async.work・QWKREQ01/001・実body長320に絞ってrowをFOR SHAREし、Message/Correlation/body/status/sent_at/lease有無だけ返す。任意Outbox/DLQ本文へのbase SELECTは付与しない。通常app/batch/Web/backup/ops/PUBLICは実行不可。戻り値は暗号検査成功flagではない。
- `uq_mq_outbox_question_work`は`correlation_id`のpartial unique index、predicate `destination='nk.async.work' AND layout_id='QWKREQ01'`。UI231の受付ごとwork一通を実現し、読取row lock中の同相関差替えを防ぐ。既存重複はmigration失敗として保全し、削除や勝手な統合をしない。DLQ用outboxとは別scope。
- `maintenance_delete_inbox`へQSB/NTC/QDLの3 canonical routeを追加。owner/token必須、最短168h、成功QSB/QDLはQUESTION・NTCはJOBの正N12参照、ERRORはNONE。既存の同transaction ID/response hash/backup/有限時刻/strict expiryを維持し、SQL単体を暗号認証の代替にしない。

045/046 PT177以降で実PG18、最小role、partial UK/不正projection/全route、親子lock/並行INSERT阻止、exact168h、失敗rollback/commit不明/永続再開を検査する。未完了の業務writer/replayや親OS/backup実体を本SQL合格へ含めない。

### 3.12 原本runの限定DB参照照会（SSC-055/PG-D-159）

先行4c5dcb85。V018は`schubert.maintenance_read_run_references(uuid,timestamptz)`だけを追加する。nk_owner所有/SECURITY DEFINER、search_path=pg_catalog,schubert・timezone=UTC、PUBLIC実行を剥奪しschubert_batchだけEXECUTEする。app/Web/backup/ops/inspector/PUBLICに許可しない。基底progress SELECT/DML、新table/column/index、既存V001～017の変更はない。run_id検索は既存batch(run_id,step) indexと2progress PKを利用する。

引数NULL・非有限cutoff・UTC0001～9999外を22023で拒否。自己backend/現在DBのbigint namespace（classid0/objid71419602/objsubid1）・granted ExclusiveLockがないと55000。shared/two-int/別backendでは不足。関数が自動取得/解放せず、観測だけではsession/xact lockの保持寿命を証明しない。親はOS flockとDB排他をfile mutation/参照再確認まで連続保持する。backup前の新run採番にも使うため本関数はbackup gateを要求しない。

同じRETURN QUERYのsnapshotで非NULL Boolean4列を必ず1行返す: `has_batch_history`、`has_inbox_progress`、`has_log_progress`はstatus/完了/年齢によらず同run存在、`identity_consistent`は同run全batch.business_dateがcutoffのAsia/Tokyo日付に一致し、同run両progress.cutoffが完全一致する場合true。不存在はconsistent=true。step.started_at/ended_atを原本cutoffとして比較/補完せず、無関係runは結果へ混ぜない。SQL失敗/permission不明は非成功で保全。新runは3flag全false必須、resumeは原本が別途存在しconsistent=true、GCは3flag全falseに加えて343の全file/400日/active/未完了条件が必須。read結果だけで親/GC完了を証明しない。

004の055/056・PT-DB-INBOX-241～248で3存在flag全8組合せ、全status/日付/µs/UTC-JST/上限、違うrun、cutoff不一致、権限・lock namespace/並行/rollback、catalogと旧migration不変を独立期待値で検証する。通常API/wire/Current oracle変更なし。

### 3.13 親用Inbox検査summary照会（SSC049/PG162、先行d23b1afd）

V019は`schubert.maintenance_read_inbox_summary(uuid,timestamptz)`をappend-only追加する。nk_owner/SECURITY DEFINER、固定search_path=pg_catalog,schubert/TimeZone=UTC、PUBLICを剥奪しschubert_batchだけEXECUTE。基表SELECT/DML、専用検査open/record/delete、cursor/応答本文/参照ID/秘密への権限は増やさない。他app/Web/ops/backup/inspector/PUBLICは拒否。新table/column/indexなし、V001～018不変。

NULL/非有限/UTC0001～9999外の引数は22023。§3.12と同じ現在DB・自己backend・bigint71419602/Exclusive/granted保持がなければ55000。関数はlock取得/解放をしない。progress PKの同runを一度readし、存在してcutoffが完全一致しなければ55000、存在しなければ0行。返却は`inspected_count bigint, deleted_count bigint, protected_count bigint, complete boolean`の4非NULL列だけで、completeは保存completed_at IS NOT NULL。rowを作成/lock/更新/補完せず、年齢/status/現在時刻で絞らない。0行を0件完了へ変更しない。戻り値は保存済みENDの観測であり、実子のfresh起動・終端/OS排他/backupの証明ではない。backup失敗時の状態調査にも使えるreadなので本関数自体ではbackupを要求せず、削除/子起動の既存backup gateは別に必須。

親は341 §7.3の連続OS lock下で、前段transactionを終了して親session advisoryを保持し、autoCommit=true/readOnly=false/READ COMMITTEDで開始前を読む。子終了後にDB lockを再取得してからfresh readする。途中結果を別run/cutoffへ流用せず、DB不通・不明・identity不一致は非成功。関数内の自己lock観測だけでOSやsession/xactの連続保持を推測しない。

004/059・060、DB251～258で未開始/未完了/完了・累積long境界・UTC/JST/歴史時刻・違うrun/µs・全role・自己lock namespace・fresh snapshot/rollback/並行・no-DML/旧migration/catalogを独立SQL後条件で検証する。

### 3.14 非Log/非Inbox cleanupの原子件数・終端照合

精度補足: PostgreSQLのtimestamptz引数は型変換後すでにµs精度であり、元のtext/JDBC nanosを復元して検査できない。Java入口は非µsを拒否し、SQLは型が保持する有限UTC範囲/大小関係を検査する。nanosecondをSQLで黙示roundした結果だけでJava境界の合格とはしない。Repositoryは返却chunk件数<=指定limitも独立検査する。

SSC057/PG164（先行78bde51a）。非Log/非秘密Inboxの7種類を、既存の削除predicate/保持期間/最大1,000/既定SKIP LOCKEDを変えず、同一RUNNING stepへの原子件数記録と組み合わせる。

- V020のmaintenance_execute_cleanup_step(p_run_id uuid,p_cutoff timestamptz,p_step_id bigint,p_attempt integer,p_started timestamptz,p_kind text,p_limit integer)をnk_owner/SECURITY DEFINER、search_path=pg_catalog,schubert,schubert_web_session、timezone=UTC、PUBLIC revoke/batchだけEXECUTEで追加する。任意SQL/基表権限/table/columnを追加せず、V001～019は不変。
- run/cutoff/started/id/attempt/kind/limitのNULLは22023。UTC0001～9999有限µs、cutoff<=started、id1..999999999999/attempt1..99/limit1..1000を検査する。kindはNOTIFICATIONS/QUESTIONS/SESSIONS/OUTBOX/BATCH_RUNS/INBOX_PROGRESS/LOG_PROGRESSだけ。LOGS/unknown/aliasは禁止。kindからstepをCLEAN_NOTIFICATION/CLEAN_QUESTION/CLEAN_SESSION/CLEAN_INBOX_OUTBOX/CLEAN_BATCH_RUNへ固定対応し、progress2種はCLEAN_BATCH_RUNへ属する。
- 既存maintenance_lock_inbox_backup(run,cutoff)で自己DB advisory/同run・当日backupの固定row lockを先に取得し、次にmaintenance_read_run_referencesのidentity_consistentを確認、最後にbatch_runsのfull handle(id/run/business_date=JST cutoff/step/attempt/started)をFOR UPDATE NOWAITで取得する。RUNNING/ended NULLとtarget=success>=0/failure=0/bytes=0を必須とし、欠落/別identity/terminal/不整合は55000で保全拒否する。これは普通の削除件数だけを積むstep用であり、Log/Inspector/backup/transferの件数を混入しない。
- 戻り7列はtarget_count/deleted_count/skipped_count（今回chunk）、step_target_count/step_success_count（既知のstep保存累積、または明示NULL）、complete boolean、reason_code text。全行必ず1行。OKは今回target=deleted/skip0と非NULL step累積(target=success)、completeは今回chunk0のときだけtrue。LOCK_BUSY/BACKUP_GATEは今回chunk0・両step累積NULL・completefalse（未読を0にしない）。QUESTIONSのDELETE内23503だけはnested blockをrollbackし、FOREIGN_KEY_CONFLICT/chunk0/既lock済みstep累積/completefalseを返す。他SQL異常/他kindのFKは伝播して全chunk rollbackする。理由/件数にraw constraint名/SQL/値を含めない。
- 7種類の既存maintenance_cleanup_*関数を固定CASEで呼ぶ。返却の1行/非NULL/limit/target=deleted/skip0/reasonを検証する。guard拒否は上記unknown累積形式で返す。正chunkの削除とstep target_count/success_countへの加算は同transactionでUPDATEする。bigint overflow、件数相違、0/複数updateは失敗しDELETEを含めrollback。status/end/旧error/failure/bytesは変更しない。parent callerだけがcommitする。
- target0のOKをそのまま全件完了としない。同transaction内で現行7関数の削除候補条件を使い、lockで除外しないEXISTSを新snapshotで照会する。通知/質問/3session表/2Outbox表/履歴/2progress表の全構成が候補0ならcompletetrue。候補ありならLOCK_BUSY/chunk0/unknown累積として停止し、成功の補完や無限loopをしない。保護条件を満たす行（active/期限内/通知あり/調査中等）は候補に含めず、保護行を失敗・削除件数へ加算しない。通常app停止/OS排他は依然callerの前提。
- Java .batch.repository.CleanupKind.step()は8kindの既定step対応を持つ（LOGS=CLEAN_LOGも対応）。CleanupStepRepository.execute(attempt,kind,limit)はLOGS/skipped handle/step不一致をDB操作前に拒否、nullは契約違反とする。borrowed autoCommit=false/RW/READ_COMMITTED、RunReferenceRepositoryで前後自己DB/identity/割込を確認し、timeout5秒/7typed bind/JDBC4.2 UTCで固定関数だけ呼ぶ。7列全NULL契約・0/複数行・type/bounds/理由整合を検証し、owned close完了後だけ返す。Connection取得/config/commit/rollback/closeなし。SQL/不正投影/owned closeはcause/suppressedなしBatchRepositoryException、unknownRuntime/NPE/Errorは正常化しない。
- CleanupStepChunk(attempt,kind,CleanupCounts chunk,Optional<CleanupCounts> stepCounts,boolean complete,Reason reason)は上記4reason/optional累積規則をconstructorで確立する。既知累積は今回chunk以上、各count非負/target=deleted/skip0。identity/toStringはredact、unknownをemptyで表し0に変換しない。FKは既知保存累積だが非completeであり、未削除aggregateを成功件数へ算入しない。
- .batch.cleanup.StepCleanupServiceはcallerの単独borrowed Connection（開始autoCommit=true/RW/READ_COMMITTED、親が既取得session advisory/OS排他・停止・実backup）を使い、run/step/kindを固定して最大1000ずつtransaction化する。SQL内でDELETE＋件数を確定してからcommit→autoCommit復元→割込/単調時計30分未満を確認する。0件completetrueまで続ける。LOCK_BUSY/BACKUP_GATEは既存CleanupStoppedExceptionの固定reasonで停止し未完了。FKだけはrollback済み0件/保存累積を確定し、deferred=trueの結果で呼出側へ返す（親のWARNING/次回保持判断と全親step finishは別責務、全削除完了とはしない）。
- 正常chunkの保存累積−今回chunkを初回beforeとし、後続は直前committed累積と一致必須。step保存累積は以前の同step構成kind/同handle再開を含み、今回service呼出し差分と区別する。commit応答不明/rollback不明は結果を返さず、次回同handleでDB保存状態を再読する。rollback成功前にautoCommitへ復元して暗黙commitしない。未知runtime/Errorでも失敗transactionをrollbackして再throwし、SQL/close診断はredactする。
- StepCleanupSummaryはattempt/kind/before/after/deferredを保持し、非負単調/同対象・0skipを検証する。afterは保存済step全体、after-beforeは今回呼出しで確認できた差分であり、中断前の件数を推測しない。deferred時は全削除済み/ENDと表示しない。serviceはBatchRunRepository.finishやOS/子/backup生成を代行しない。親の全kind順序/失敗規則・通常Question/pending revoke・実Log/Inspector結線は残る。

## 4. Account・Session

### 4.1 `schubert.app_users`

| Column | PostgreSQL型 / default | NN | Constraint・index |
|---|---|---:|---|
| `id` | bigint identity | yes | PK、1..999999999999 |
| `username` | text | yes | `octet_length` 1..64 |
| `username_key` | text | yes | UK、`octet_length` 1..96。表示usernameのNFC/trim/Locale.ROOT lowercase比較keyはbyte増幅し得る（SSC-014） |
| `password_hash` | text | yes | 1..255 byte |
| `role` | varchar(5) | yes | CHECK USER/ADMIN |
| `status` | varchar(8) | yes | CHECK ACTIVE/DISABLED |
| `failed_count` | integer / 0 | yes | CHECK 0..5 |
| `failure_window_started_at` | timestamptz | no |  |
| `locked_until` | timestamptz | no | index where not null |
| `last_login_at` | timestamptz | no |  |
| `password_changed_at` | timestamptz | yes |  |
| `version` | bigint / 0 | yes | 0..999999999 |
| `created_at`,`updated_at` | timestamptz | yes |  |
| `created_by`,`updated_by` | bigint | no | FK self ON DELETE RESTRICT |

Index: UK `uq_app_users_username_key`、`ix_app_users_role_status(role,status,id)`、partial
`ix_app_users_locked_until(locked_until) where locked_until is not null`。Active ADMIN 0人化は多rowの条件であるため
CHECKではなく、332のadvisory transaction lockと再検索で防ぐ。

### 4.2 `schubert.auth_sessions`

| Column | 型 | NN | Constraint・index |
|---|---|---:|---|
| `id` | uuid | yes | PK |
| `user_id` | bigint | yes | FK app_users RESTRICT |
| `context_hash` | char(64) | yes | UK、lower hex CHECK |
| `context_ciphertext` | bytea | yes | `octet_length > 28` |
| `key_version` | varchar(16) | yes | allowlist format |
| `issued_at`,`last_accessed_at`,`expires_at` | timestamptz | yes | `issued_at <= last_accessed_at <= expires_at` |
| `revoked` | boolean / false | yes |  |
| `revoked_at` | timestamptz | no | revokedとの複合CHECK |
| `revoke_reason` | varchar(32) | no | LOGOUT/DISABLED/PASSWORD_RESET/ADMIN/EXPIRED/REPLACED |
| `client_address` | inet | yes |  |
| `created_message_id` | uuid | yes | UK |

Index: `ix_auth_sessions_user_active(user_id,last_accessed_at desc,id) where revoked=false`、
`ix_auth_sessions_expires_at(expires_at)`。同時2 session上限はtransaction内lockで古いrowをrevokeする。

### 4.3 `schubert.login_ip_attempts`

`client_address inet PK`、`failed_count integer not null check 0..10`、`window_started_at timestamptz not null`、
`locked_until timestamptz null`、`updated_at timestamptz not null`。Cleanup indexは`ix_login_ip_attempts_updated_at(updated_at)`。

## 5. Scenario・Media master

| Table | Columnと制約 | Index・FK | 関連UI/RD |
|---|---|---|---|
| `games` | `id smallint PK check 1..2`、`code varchar(16) UK check NUKITASHI1/2`、`title text NN check octet_length 1..256`、`display_order smallint NN UK check 1..2`、`created_at timestamptz NN` | 2件の初期dataをmigrationで固定 | UI 223/242、DAT-006 |
| `script_files` | `id bigint identity PK`、`game_id smallint NN`、`display_order bigint NN check 1..N12`、`storage_relative_path text NN check 1..512 byte`、`display_path text NN check 1..512 byte`、`file_name text NN check 1..256 byte`、`section_code varchar(64)`、`chapter_title text check <=256 byte`、`sha256 char(64) NN`、`byte_size bigint NN check >=0`、`created_at NN` | FK game RESTRICT、UK `(game_id,storage_relative_path)` / `(game_id,display_order)` / `(id,game_id)`、index chapter/title trgm | UI 223/242/243、DAT-003～006 |
| `speakers` | `id bigint identity PK`、`game_id smallint NN`、`name text NN check 1..128 byte`、`normalized_name text NN check 1..128 byte`、`is_protagonist boolean NN default false`、`notes text`、`created_at NN` | FK game RESTRICT、UK `(game_id,normalized_name)` / `(id,game_id)`、trgm name | UI 223/242、FUN-004 |
| `script_entries` | `id bigint identity PK`、`game_id smallint NN`、`script_file_id bigint NN`、`display_order bigint NN UK`、`entry_index integer NN check >=0`、`line_number integer check >=1`、`entry_type varchar(9) NN`、`speaker_id bigint`、`speaker_label text check <=128 byte`、`body text NN check octet<=4096`、`body_search text generated always as (lower(body)) stored`、`raw_block text NN`、`created_at NN` | 複合FK file/game CASCADE、speaker/game RESTRICT、UK `(script_file_id,entry_index)` / `(id,game_id)`、GIN body_search gin_trgm_ops、speaker/display_order | UI 223/242、FUN-003～005 |
| `audio_files` | `id bigint identity PK`、`game_id smallint NN`、`storage_relative_path/display_path text NN check 1..512 byte`、`file_name text NN check 1..256 byte`、`basename text NN check 1..255 byte`、`audio_role varchar(11) NN check 1..11 byte`、`container varchar(16)`、`duration_ms bigint check >=0`、`byte_size bigint NN check >0`、`sha256 char(64) NN`、`created_at NN` | FK game RESTRICT、UK `(game_id,storage_relative_path)` / `(id,game_id)`、basename index | UI 223/242/243、FUN-005 |
| `entry_audio_links` | `entry_id bigint NN`、`audio_file_id bigint NN`、`game_id smallint NN`、`link_type varchar(5) NN check voice/se/bgm/other`、`display_order smallint NN check 1..999`、`created_at NN`、PK `(entry_id,audio_file_id,link_type)` | 複合FK entry/game CASCADE、audio/game RESTRICT、UK `(entry_id,link_type,display_order)`、index audio ID。Deferred constraint triggerで1 entry/type 999件以下 | UI 242、DAT-006 |
| `media_assets` | `id bigint identity PK`、`logical_id varchar(64) NN UK`、`media_type varchar(8) NN check VIDEO/MUSIC`、`title text NN check 1..256 byte`、`category text NN check 1..64 byte`、`section text check <=128 byte`、`storage_relative_path/display_path text NN check 1..512 byte`、`file_name text NN check 1..256 byte`、`byte_size bigint NN check >0`、`sha256 char(64) NN`、`mime_type varchar(64) NN`、`parent_logical_id varchar(64)`、`pair_key text check <=256 byte`、`pair_role char(1)`、`display_order integer NN check 1..9999`、`created_at NN` | Self FK parent logical ID RESTRICT、UK `(media_type,storage_relative_path)`、index `(media_type,category,section,display_order,id)` | UI 223/242/243、FUN-006～007 |

`script_entries` CHECKは`dialogue`なら`speaker_id is not null`、`narration`なら`speaker_id is null`を保護する。
Storage/display pathのsegment検査はJava/migrationで実施し、DBではNUL禁止、octet上限1..512。実storage pathの1 segment/basenameはOS適合上1..255 byte、電文・表示・download用`file_name`は1..256 byteとし、両者を混同しない。
`storage_relative_path !~ '(^/|\\\\|(^|/)\\.\\.?(/|$)|//)'`を最低限のCHECKとする。

`media_assets`は`pair_role is null or pair_role in ('M','I','N')`をCHECKする。VIDEOは`pair_key/pair_role`=
NULL、MUSICのM/Iは両方NNかつ`pair_key` 1～256 byte、Nは`pair_key` NULLとする複合CHECKでpairの半端状態を拒否する。

## 6. Question・Answer・非同期・通知

### 6.1 `schubert.questions`

| Column | 型 / default | NN | Constraint |
|---|---|---:|---|
| `id` | bigint identity | yes | PK、1..N12 |
| `receipt_id` | char(26) | yes | UK、`^[0-9A-HJKMNP-TV-Z]{26}$` |
| `owner_user_id` | bigint | yes | FK app_users RESTRICT |
| `body` | text | yes | `octet_length(body) between 1 and 4096` |
| `operation_token` | uuid | yes | UK with owner |
| `submitted_at` | timestamptz | yes |  |
| `is_deleted` | boolean / false | yes |  |
| `deleted_at` | timestamptz | no | delete triple CHECK |
| `deleted_by` | bigint | no | FK app_users RESTRICT |
| `version` | bigint / 0 | yes | 0..999999999 |

Index: UK `(owner_user_id,operation_token)`、
`ix_questions_owner_active(owner_user_id,submitted_at desc,id desc) where is_deleted=false`、
`ix_questions_admin_active(submitted_at desc,id desc) where is_deleted=false`、
GIN `body gin_trgm_ops where is_deleted=false`、`ix_questions_deleted(deleted_at,id) where is_deleted=true`。

### 6.2 `schubert.answers`

`id bigint identity PK`、`question_id bigint NN UK FK questions ON DELETE CASCADE`、`body text NN check octet_length between 0 and 4096`、
`answered_at timestamptz NN`、`provider_type varchar(16) NN check STUB/EXTERNAL_AI`、`is_deleted boolean NN default false`、
`deleted_at timestamptz`、`deleted_by bigint FK app_users RESTRICT`、`created_at/updated_at timestamptz NN`。Delete triple CHECKをquestionsと同じに設ける。

### 6.3 `schubert.async_jobs`

`id bigint identity PK`、`question_id bigint NN UK FK questions CASCADE`、`owner_user_id bigint NN FK app_users RESTRICT`、
`state varchar(12) NN check (RECEIVED,PROCESSING,COMPLETED,ERROR,CANCELLED)`、
`message_id uuid NN UK`、`correlation_id uuid NN`、`processing_message_id uuid UK null`、
`received_at/state_changed_at timestamptz NN`、`started_at/completed_at/error_at/cancelled_at timestamptz null`、
`retry_count integer NN default 0 check 0..3`、`last_error_code varchar(64)`、`last_error_message varchar(256)`、
`version bigint NN default 0 check 0..999999999`。

Index: `ix_async_jobs_fifo(state,received_at,id)`、`ix_async_jobs_state_changed(state,state_changed_at,id)`、
`ix_async_jobs_owner(owner_user_id,state_changed_at desc,id desc)`。`processing_message_id`はConsumerが状態をPROCESSINGへ移した
Message IDであり、redelivery時の同一work識別に使う。

### 6.4 `schubert.notifications`

`id bigint identity PK`、`job_id bigint NN UK FK async_jobs RESTRICT`、`question_id bigint NN FK questions RESTRICT`、
`owner_user_id bigint NN FK app_users RESTRICT`、`notification_type varchar(12) NN check ACCEPTED/COMPLETED/ERROR`、
`state varchar(12) NN check (RECEIVED,PROCESSING,COMPLETED,ERROR,CANCELLED)`、`accepted_at/state_changed_at timestamptz NN`、`error_code varchar(16)`、`error_message varchar(512)`、
`created_at/updated_at timestamptz NN`。

`error_code`は351 §5.3の5値だけ、ERROR時はcode/messageともNN、他stateでは両方NULLのCHECKとする。

Index: `ix_notifications_owner(owner_user_id,state_changed_at desc,id desc)`、
`ix_notifications_cleanup(state,state_changed_at,id)`。Manual delete columnは設けない。Jobとnotificationのstate同期は必ず同一transactionで更新する。

## 7. Message整合table

### 7.1 `schubert.request_inbox`

| Column | 型 | NN | 制約・用途 |
|---|---|---:|---|
| `message_id` | uuid | yes | PK |
| `correlation_id` | uuid | yes | index |
| `request_layout_id`,`request_version` | char(8),char(3) | yes | format CHECK |
| `owner_user_id` | bigint | no | FK app_users RESTRICT、Login前NULL |
| `operation_token` | uuid | no | owner scope partial UK |
| `request_fingerprint_hmac` | char(64) | yes | 全Requestのcanonical HMAC、lower hex CHECK |
| `fingerprint_key_version` | varchar(16) | yes | HMAC key ID、current/previous allowlist |
| `processing_state` | varchar(12) | yes | PROCESSING/COMPLETED/ERROR |
| `result_ref_type` | varchar(16) | no | NONE/AUTH_SESSION/USER/QUESTION/JOB/SCENARIO_FILE |
| `result_ref_id` | bigint | no | USER/QUESTION/JOB/SCENARIO_FILE用。Generic FKにせずserviceでtype検証 |
| `result_ref_uuid` | uuid | no | AUTH_SESSION用。`auth_sessions.id`をserviceで検証 |
| `response_layout_id`,`response_version` | char(8),char(3) | no | ペアNULL CHECK |
| `response_body_encrypted` | bytea | no | Replayに必要な場合だけ |
| `response_key_version` | varchar(16) | no | ciphertextとペア |
| `created_at`,`completed_at`,`expires_at` | timestamptz | yes/no/yes | state/time CHECK |

Index: partial UK `uq_request_inbox_operation(owner_user_id,operation_token) where operation_token is not null`、
`ix_request_inbox_expires(expires_at)`、`ix_request_inbox_correlation(correlation_id)`。Loginのoperation tokenはowner未確定のため
`owner_user_id` NULLのpartial UK対象外とし、Message IDでだけ冪等化する。

- `owner_user_id is null` は`LGNREQ01`だけ、その他RequestはNN。`operation_token is not null`は323 §9の更新layoutだけとする。
- PROCESSINGは`completed_at/result_ref_type/result_ref_id/result_ref_uuid/response_layout_id/response_version/response_body_encrypted/response_key_version`を全てNULL。
- COMPLETED/ERRORは`completed_at`、response layout/version、`result_ref_type`をNN。`NONE`は両ref NULL、`AUTH_SESSION`はUUIDだけNN、
  `USER/QUESTION/JOB/SCENARIO_FILE`はbigint IDだけNNとする排他的CHECKを設ける。SCENARIO_FILEのIDは再生成元`script_files.id`である。
- Response snapshotは`response_body_encrypted`/`response_key_version`の両方NULLまたは両方NN。Password/context等を含む再構成不可結果はsnapshotを必須とし、平文保存しない。

SSC-052/PG-D-140: 新3更新QSB/NTC/QDLの成功はresponse_body_encryptedへ352 §11.2.1の参照/token付き内部profileを必須保存する。別列result_ref/tokenは復号後に照合する期待値であり、暗号内targetから上書きしない。新列/table/grantや既存migration変更なし。NONEの確定errorと既存認証/query/User更新は従来profile。unbound成功を推測変換するmigrationは行わず保護し、後続のDB検査/writer/replay接続を別途確認する。

### 7.2 `schubert.mq_outbox`

`id bigint identity PK`、`message_id uuid NN UK`、`correlation_id uuid NN`、`destination varchar(32) NN`、
`layout_id char(8) NN`、`layout_version char(3) NN`、`body bytea NN`、
`status varchar(8) NN check PENDING/SENT/ERROR`、`attempt_count integer NN default 0 check 0..100`、
`next_attempt_at timestamptz NN`、`lease_owner varchar(64)`、`lease_until timestamptz`、
`created_at timestamptz NN`、`sent_at timestamptz`、`last_error_code varchar(64)`、`last_error_detail varchar(256)`。

Destination CHECKは`nk.async.work` / `nk.dead.letter`のallowlist。Indexは
`ix_mq_outbox_dispatch(status,next_attempt_at,id)`とpartial `ix_mq_outbox_lease(lease_until) where status='PENDING'`。
Lease pairは両方NULLまたは両方NNとする。

## 8. Log・batch

### 8.1 `schubert.app_logs`

`id bigint identity PK`、`logged_at timestamptz NN`、`service varchar(8) NN`、`category varchar(8) NN`、
`level varchar(5) NN`、`action varchar(64) NN`、`message varchar(512) NN`、`request_id uuid`、`message_id uuid`、
`correlation_id uuid`、`source_message_id uuid UK null`、`actor_user_id bigint null FK app_users RESTRICT`、`actor_username varchar(64)`、
`http_method varchar(8)`、`request_uri varchar(256)`、`status_code smallint check 100..599`、`remote_address inet`、
`duration_ms bigint check >=0`、`security_hold_until timestamptz null`、`details jsonb NN default '{}'::jsonb`。

`service`は`WEB/API/BATCH/BROKER/DB/CADDY`、`category`は`REQUEST/ACTION/SECURITY/MQ/SYSTEM/BATCH`、
`level`は`TRACE/DEBUG/INFO/WARN/ERROR`のCHECKとする。
`details` top-level keyも351のevent catalogで定義した値だけをapplication validatorで受け付ける。
`security_hold_until`は`category='SECURITY'`の行だけに設定可能とするCHECKで保護し、
Security holdの対象IDは`app_logs.id`、保全中は`security_hold_until > cleanup cutoff`とする。
期限未設定または期限到達後は通常の90日削除対象とし、ops viewへは同列を投影しない。

`request_uri`は`octet_length <= 256`、`details`はserialized UTF-8 1,024 byte以内をCHECK/投影前validatorで保護し、
WLGEVT01およびLGSRSP01へ暗黙truncateなしで変換可能にする。

Partitionは初期releaseで使わず、indexを`logged_at desc`、`(category,logged_at desc)`、`correlation_id`、`message_id`、
GIN `message gin_trgm_ops`に限定する。容量実測がthresholdを超えた後のpartition導入は別migrationとし、SSで無断変更しない。

### 8.2 `schubert.batch_runs`

SSC-055/PG-D-156（先行b6b5f0f6）: このtableのstarted_atは各stepの時刻でありrun原本ではない。親は343 §6.13のimmutable root永続anchorからrun_id/cutoffを復元し、business_dateを既存SQLと同じAsia/Tokyo日付で導出する。最小step時刻・progress・現在日時による原本backfillをしない。原本/active/activation/completionの状態とstep状態は異なる。run原本不明legacyは保持してresumeを拒否する。原本GCは完了400日超・active/未完了activationなしに加え、batch_runs/Inbox progress/log progressの同run参照0をOS/DB lock下で検査する。原本fileを追加するために旧V001～017へ列/tableを後書きしない。具体的な参照照会の限定DB入口と親step Repositoryは別PG/PTで必須。

`id bigint identity PK`、`run_id uuid NN`、`business_date date NN`、`step varchar(32) NN`、`attempt smallint NN check 1..99`、
`started_at timestamptz NN`、`ended_at timestamptz`、`status varchar(10) NN check RUNNING/SUCCESS/WARNING/FAILED/SKIPPED`、
`target_count/success_count/failure_count bigint NN default 0 check >=0`、`byte_count bigint NN default 0 check >=0`、
`error_code varchar(64)`、`error_summary varchar(512)`。

SSC-077/BUG-237: V001～020を不変とし、V021で`CLEAN_EXPIRY`監査専用のnullable `expiry_cutoff_at timestamptz`、`expiry_before_count bigint`、`expiry_after_count bigint`を追記する。他stepでは3列すべてNULL。Expiry stepは3列すべてNULL（未観測/失敗/skip）または3列すべて非NULL（観測済み）とし、有限cutoff・非負count・after<=beforeをCHECKする。SUCCESSは3列必須、`expiry_before_count-expiry_after_count=success_count=target_count`、`failure_count=0`。既存`byte_count`をこのstepの削除対象推定byte数、既存`target_count/success_count/failure_count`を対象/削除/失敗数として使う。旧SUCCESS行はcutoff/前後値を推測できないため、V021は事前検出して安全停止し、自動backfillしない。親はimmutable run原本の開始cutoffから7日を引いた値とDB監査cutoffを照合し、借用同transactionで監査列とstep結果を確定する。既存他step計数、索引、role/grantを無断変更しない。V005の`schubert_app`に対する既存table-level DMLは新列にも継承されるので、V021でapp専用の追加grantを行わないという意味であり、appから新列へのアクセスを拒否する意味ではない。PostgreSQL catalog/制約/権限/旧migration hashと実再実行PTが揃うまで完了扱いにしない。

SSC-078/BUG-238: V021の3列同時CHECKではSS341 §9のpurge前durable観測を記録できないため、V001～021を不変としてV022で同名CHECKをtransaction内置換する。Expiryの未観測rowは3列全NULLでSUCCESS不可。purge前に確定した観測rowは有限cutoff・非負beforeを必須、`expiry_after_count=NULL`、`target_count<=expiry_before_count`、`success_count=0`、statusはRUNNINGまたは非成功とする。失敗・中断でafter不明ならNULLを維持し、仮のafter=beforeや削除成功数を作らない。purge後に実測afterを得たrowだけ3列非NULLとし、`0<=after<=before`。SUCCESSはafter必須、`before-after=success_count=target_count`かつfailure0を保つ。非Expiryは常に3列全NULL。親は固定runから導いたcutoff、before/target/推定byteをpurge前にDB確定し、purge後の実測結果・terminal stepを同一後続transactionで確定する。commit不明・再実行では原本と保存済みrowを再読取し、未知afterを推測しない。V022はrole/grant/indexや既存SUCCESS rowを変更しない。PT-DB-018以降・PT-BAT-284以降で旧V021拒否/V022許容・失敗・rollback・同runを検証するまで親清掃は未完了。

UK `(business_date,step,attempt)`、partial UK `(business_date,step) where status='SUCCESS' AND step NOT IN ('BACKUP_DB','BACKUP_CONFIG')`、index `(run_id,step)`、
`(status,started_at desc)`。通常stepの成功済み再実行はSKIPPEDとして別attemptを記録する。

SSC-054/BUG-138/PG-D-145: UI251 §11のbackup例外に従い、BACKUP_DB/CONFIGだけ同日複数SUCCESSを許容し、再実行前の成功履歴をSKIPPED等へ書換えない。同日stepのattempt1～99・UKは維持し、99超は繰返し/上書きせず停止。V017で既存success indexのpredicateだけappend-only修正し、旧migrationは不変。他index/role/grant/保持期限は不変。最新成功backupの実directory/manifest/hash選択・DB/configの同一成果物照合は親backup/cleanup実装の別必須責務であり、本制約修正だけでは配備・backup完了を意味しない。

### 8.3 親step履歴の借用Repository

SSC055/PG163（先行898cc267）の親step Repository契約:

- ProductionはBatchStep（BACKUP_DB、BACKUP_CONFIG、CLEAN_NOTIFICATION、CLEAN_QUESTION、CLEAN_SESSION、CLEAN_INBOX_OUTBOX、CLEAN_LOG、CLEAN_BATCH_RUN、CLEAN_TRANSFER、CLEAN_EXPIRY）、BatchStepAttempt、BatchStepResult、BatchRunRepository。原本由来BatchRunを受け取り、business_dateだけcutoffのAsia/Tokyo日付から導出する。step.started_atは呼出側が一度取得した別のnow。新now/終了timeはUTC0001～9999・µs、run.cutoff以上。原本backfillやclock丸め/補完はしない。
- Repositoryは単独所有の借用Connection、autoCommit=false/readOnly=false/READ_COMMITTED。各操作前後にRunReferenceRepositoryの自己DB排他/同run identity整合を確認する。OS lock/原本正本/fresh子終端を代行しない。全PreparedStatementはtimeout5秒。Connection生成/config変更/commit/rollback/closeなし、callerが成功後commit・失敗後rollback/破棄する。途中のINSERT/UPDATEだけで確定済みとしない。
- begin(run,step,now,recoverAbandoned)は同business_date/stepをattempt昇順LIMIT100 FOR UPDATEで全読取。12非秘密列id/run_id/business_date/step/attempt/started_at/ended_at/status/target_count/success_count/failure_count/byte_countだけを投影し、error_code/summaryを返さない。最大99行、id1～999999999999/一意、attempt1～99/厳密昇順、同date/step・UUID必須、全非負counts、µs/UTC時刻、RUNNINGだけended=NULL・terminalはended>=started、全時刻<=nowを検証。同run行のstartedは原本cutoff以上。未知status/null/不整合は保全拒否。既存別runのcutoffをstep時刻から推測しない。
- 次attemptはその日/stepの最大値+1（初回1）、99超では一切更新しない。既RUNNINGはrecoverAbandoned=trueかつ全件同runの場合だけ、保持した各id/run/started/RUNNING/endedNULLをCASしFAILED・ended=now・固定ABANDONED診断へ更新、件数は保存する。false/別run RUNNINGは失敗。明示recoveryのcallerは子全終端/同run原本/OS排他を事前確認する。過去SUCCESS/WARNING/FAILED/SKIPPEDや別run診断を書換えない。
- 非backupは同日/stepの既SUCCESSがあれば新attemptをSKIPPED（started=ended=now、4counts0、ALREADY_SUCCESSFUL）としてINSERT。backup2stepは毎回RUNNINGをINSERTし、既SUCCESSを保持する。他の新規もRUNNING/endedNULL/4counts0/診断NULL。RETURNING idは1行必須・有効id・全close後だけimmutable BatchStepAttempt(id,run,step,attempt,startedAt,skipped)を返す。日をまたいでresumeしても原本business_dateを使う。
- finish(attempt,endedAt,result)はskipped handleを拒否し、全handle identity（id/run/date/step/attempt/started）かつRUNNING/endedNULLに対してterminal値をCASする。更新1件だけ新終了、0件は同identityとended/status/4counts/error_code/error_summaryが全て同値の場合だけ冪等成功（IS NOT DISTINCT FROMでNULL比較）。それ以外/複数件は失敗。過去終了を新timeや異なるresultで上書きしない。DB全資源と最終排他/割込確認後だけ返却する。成否不明commitは同じfinish値の再試行か新beginの既SUCCESS skipで扱い、未観測件数を補完しない。
- BatchStepResultはStatus SUCCESS/WARNING/FAILED/SKIPPEDとtarget/success/failure/bytes各非負long、Reasonの固定組。SUCCESSはfailure0・NONEのみ。SKIPPEDは4counts0・ALREADY_SUCCESSFULまたはBACKUP_UNAVAILABLE。PROTECTED_RECORDSはWARNING、ABANDONEDはFAILED。DATABASE_FAILURE/COMMAND_FAILURE/SAFETY_FAILURE/IO_FAILURE/TIMEOUT/INTERRUPTEDはWARNINGまたはFAILED。保存codeはNONEだけSQL NULL、それ以外はenum名、summaryは対応する固定文だけ。任意exception/SQL/path/body/credentialを保存しない。保護skipをfailureへ勝手に置換せず、累積/今回差分はcallerが別責務として正しく分類する。
- public型のnullは契約違反、不正value/timeは固定IllegalArgumentException。不正DB投影/SQL/owned closeはcause/suppressedなしBatchRepositoryException、開始/最終割込はflag保持で非成功。未知Runtime/NPE/Errorを正常化しない。全recordのtoStringはidentity/診断実体をredact。nullや未知値を0/SUCCESSへ補完しない。
- V001～019/DDL/grant/保持期限・外部動作は変更しない。原本と実親全stepの結線/実backup/子unit/全cleanup loop/ITSTは本Repositoryだけでは完了にならない。017/021～024・BAT130～153、411/451の独立SQL/golden/全JDBC位置・4coverage100へ追跡する。

## 9. Web technical schema

### 9.1 `schubert_web_session.web_http_sessions`

`id uuid PK`、`session_id_hash char(64) NN UK`、`attributes_ciphertext bytea NN`、`key_version varchar(16) NN`、
`created_at/last_accessed_at/expires_at timestamptz NN`、`max_inactive_seconds integer NN check 1..28800`、
`version bigint NN default 0`。Index `expires_at`。任意Java serializationは保存しない。

### 9.2 `schubert_web_session.pending_context_revocations`

`id uuid PK`、`context_ciphertext bytea NN`、`key_version varchar(16) NN`、`requested_at timestamptz NN`、
`attempt_count integer NN default 0 check 0..100`、`next_attempt_at timestamptz NN`、`expires_at timestamptz NULL`（NULL=現在API期限未確認）、`last_error_code varchar(64)`、
`lease_owner varchar(64)`、`lease_until timestamptz`。Index `(next_attempt_at,requested_at)`、`expires_at`。
QA050承認によりexpires_at NNだけを実末尾のappend-only migrationで解除し、旧V003等は変更しない。既存値を自動削除proofにせず、未知をLogin/requested_at+8hで補完しない。既定列/lease/index/権限を維持し、attempt_countは100飽和後も継続する。row削除は自分のlease CAS＋検証済0000/0200だけとし、期限NULL/経過・一般0102・復号不能をcleanupで削除しない。初期backoff後15分の継続再試行とIT/ST性能問題時の間隔調整はSS314/354に従う。

### 9.3 `schubert_web_session.web_log_outbox`

`id bigint identity PK`、`message_id uuid NN UK`、`correlation_id uuid NN`、`layout_id char(8) NN check WLGEVT01`、
`layout_version char(3) NN`、`payload_ciphertext bytea NN`、`key_version varchar(16) NN`、
`status varchar(8) NN check PENDING/SENT/ERROR`、`attempt_count integer NN default 0`、`next_attempt_at timestamptz NN`、
`created_at timestamptz NN`、`sent_at timestamptz`、`last_error_code varchar(64)`、`lease_owner varchar(64)`、`lease_until timestamptz`。
Index `(status,next_attempt_at,id)`、SENT cleanup用`sent_at where status='SENT'`。

### 9.4 `schubert_web_session.web_receipt_references`（QA-048、2026-10-03）

SSC175（2026-10-04、QA048内部接続）：孤児削除の固定kindは`WEB_RECEIPTS`、既存`CLEAN_BATCH_RUN`のtechnical共有stepへ割り当てる。新BatchStep/table引数/業務質問counter変更はない。1,000件以下のchunkで、全3列・PK/id index・明示grantを追加する末尾migrationと同時に、既存atomic `maintenance_execute_cleanup_step`の閉じたkind集合へ追加する。固定孤児functionの返却は既存と同じtarget/deleted/skipped/reason、削除対象は`NOT EXISTS questions(id=question_id)`だけで、logical deletion・age・tuple不一致・API検証不能を孤児へ読み替えない。同run開始cutoff/当日両backup/自己advisory/現在run identity/完全RUNNING step handleを検証し、DELETEと累積countを同TXで確定する。SKIP LOCKEDの0件は非lock eligible照会で不存在の場合だけ完了、残対象があればLOCK_BUSY/非成功・count不変。rollback/commit-close不明は成功化しない。詳細はSS332/341、backup/migrationはSS343。新table/function/役割・indexの独立SQL/PTと実適用は未完了。

| Column | 型 / 制約 | 内容 |
|---|---|---|
| receipt_id | char(26) PK、`^[0-9A-HJKMNP-TV-Z]{26}$` | 検証済IF025公開受付ID |
| question_id | bigint NN CHECK 1..999999999999 | 同結果の既存N12質問ID。業務FKなし |
| submitted_at | timestamptz NN、finite、millisecond整合 | 検証済IF025 UTC受付時刻 |

列はこの3個だけで、PK indexによるreceipt検索とcleanup用`ix_web_receipt_references_question_id(question_id)`を設ける。Web roleへこのtableのSELECT/INSERT/DELETEだけを明示grantし、UPDATE/任意schema grantや業務schema権限は追加しない。INSERTの同PK同値は冪等、競合値のUPDATEは許可しない。nk_ownerが所有しPUBLICをREVOKE、schubert_backupへSELECTを明示grantする。

孤児cleanup用の固定`schubert.maintenance_cleanup_web_receipt_references(run_id uuid, cutoff timestamptz, limit integer)`をappend-only migrationで追加する。既存保守契約と同じrun開始cutoff・当日両backup成功・advisory gate・bounded chunkを検証し、owner内部の固定SQLで業務questionsにquestion_idが実在しないrowだけを削除する。table/schema引数・動的SQL・任意TTLを禁止する。SECURITY DEFINER/固定search_path/UTC/PUBLIC EXECUTEなし、schubert_batchへ完全signatureのEXECUTEだけをgrantし、直接Web/business table DML/SELECTをbatchへ追加しない。件数・skip/理由codeだけを返し、本文/受付tupleは返さない。通常API/Web停止・実backup確認と内部孤児照合/削除を結び、別世代restore・並行更新は当該証明が揃うまで保持する。grant・backup inventory・migration末尾採番・独立DDL/権限/cleanup PTは実装時に一貫更新し、旧migration/hashは変更しない。

業務側DB（APIが管理するquestions/関連業務data）が正である。`schubert_web_session.web_receipt_references`はreceiptIdからquestionIdを解決するためのtechnical locatorだけとし、検証済IF025のreceiptId/questionId/submittedAtの3値以外を保存しない。本文・回答・password・認証context・operation token・owner・結果snapshot・検証済flagを蓄積しない。

SCR019のGETごとにlocatorを読む短Web transactionを終了してからfresh MessageIDのIF030を現在API認証で呼び、API側の現在owner認可に加えてquestionId/receiptId/submittedAtを照合する。日時比較は既存wireのUTC millisecond精度へ揃え、DBの追加microsecondを誤不一致にしない。表示はこの要求で取得したAPI結果だけをHTML escapeし、request scopeへ置く。不一致・他人・削除済み・locator欠落・API確認不能は既存error処理へ進め、古いlocatorやsessionから受付成功/本文を補わない。

IF025成功後のWeb保存は3値をimmutableに登録する。同receiptの同値再登録は冪等、異なる値の競合は上書きせず非成功・診断とする。業務commitとWeb保存は別transactionなので一時欠落が起こり得る。その際、業務受付を取り消したと仮定せず、新operation tokenで質問を再生成しない。保持中の同token/同入力の正規再操作からAPIの既存確定受付結果を取得し、Web参照登録を再試行する。参照欠落のURLだけからquestionIdを推測して復元する保証はしない。

Backup/restore後もWeb値は信頼せず毎GETのAPI検証を省略しない。修復は正規APIの検証済み結果を根拠にWeb参照を合わせる片方向とし、Web参照を正として業務DBを書き換えない。Webから業務schemaへの直接接続/FK/権限は追加しない。cleanupは当日backup gateの下、業務質問が物理削除されたlocatorだけを固定保守functionで削除し、存続する質問のlocatorへ独自TTLを設定しない。実装・DDL適用・独立PTは未完了であり、QA048承認による設計条件である。

## 10. FK・ON DELETE・constraint名

| Parent -> Child | ON DELETE | 理由 |
|---|---|---|
| `app_users` -> session/question/job/notification/log actor | RESTRICT | UserはDISABLEDとし監査参照を残す |
| `questions` -> `answers`,`async_jobs` | CASCADE | 朝処理の最終aggregate物理削除 |
| `questions` -> `notifications` | RESTRICT | Notificationが残る間の本文削除防止 |
| `async_jobs` -> `notifications` | RESTRICT | 運用追跡とcleanup順を保護 |
| `games` -> master | RESTRICT | 誤ったgame削除を禁止 |
| `script_files` -> `script_entries` | CASCADE | Staging/swapのfile aggregate再構築 |
| `script_entries` -> link | CASCADE | Entry再構築 |
| `audio_files` -> link | RESTRICT | 参照中audioの削除禁止 |

Constraint名は`pk_<table>`、`fk_<child>_<parent>_<column>`、`uq_<table>_<purpose>`、
`ck_<table>_<purpose>`、indexは`ix_<table>_<purpose>`とする。同名のimplicit indexを重複作成しない。

## 11. Migration DDLの順序・検査

1. Role/databaseはDBA用provisioning、schema/extension/tableはversion付きmigrationに分離する。
2. Schema、table、constraint、index、grant、initial dataの順で作成する。大量master用GIN indexはload後に作成する。
3. ID identity sequenceのMAXVALUEとtable CHECKを同じmigrationで設定する。
4. `information_schema`、`pg_constraint`、`pg_indexes`、`aclexplode`の実測結果を本書と機械照合する。
5. Web credentialで`select * from schubert.app_users`がpermission denied、API credentialでWeb schemaがpermission deniedとなる負のtestを必須とする。
6. DDL実行後にorphan、game不一致、state/time不整合、delete triple不整合、電文数値上限超過が0件であることを検査する。

## 12. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-024 | Application IDを`bigint identity`、公開/相関IDを`uuid`/ULID系charに分離し、電文N12/N9の上限をDDLでも保護する | UI 242の上限をDB正常値とcodec例外の不整合にしない | DDL/PTでsequence上限とCHECK境界を検証 |
| SS-D-025 | Web用roleに業務schemaの`USAGE`さえgrantせず、専用schemaの4 technical tableだけを列挙許可する（QA048受付参照はSELECT/INSERT/DELETE） | UI 211/241の「Webは業務DBを読まない」をcredential層で強制 | Security ITで権限負のtest必須 |
| SS-D-026 | Outbox/revocationに`lease_owner`/`lease_until`を追加し、同時dispatcherとprocess異常時の回復をDB上で保護する | UIの責務・外部仕様を変えず、SKIP LOCKED取得後の長時間JMS I/O中にDB lockを保持しない | 324/332のlease転移、競合PTに反映 |

## 13. PG・PT・ITへの引継ぎ

- PGはmigrationを本書から実装し、ORMのautomatic DDL updateを禁止する。
- PTは全PK/FK/UK/CHECK/default/index、各上限、ON DELETE、optimistic lock、active ADMIN保護を検証する。
- ITはrole/grantの負の権限、大量データquery plan、backup/restore後のconstraint・sequence継続を検証する。
- 上位にないtable/columnを実装便宜で追加する場合は、先にSS更新とPG工程の914台帳管理を行う。

## 14. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | UI 241/242を物理schema、型、制約、index、role/grantへ具体化。 |
| 2026-08-31 | 横断監査でIP lock 10回と整合するよう`login_ip_attempts.failed_count`を0..10へ是正。 |
| 2026-08-31 | 横断監査で内部error code 64 byteと通知用16 byte code/message 512 byteを物理型・CHECKへ反映。 |
| 2026-08-31 | 横断監査でLog path/detailsをUI 235の256/1,024 byteに統一。 |
| 2026-08-31 | 横断監査でmasterのpath/file/title/category/section等をUI 234/235のwire byte上限へ統一。 |
| 2026-08-31 | 横断監査でDB service role名をUI 212の`schubert_*`名に統一（MQの`nk_*` userと分離）。 |
| 2026-08-31 | 横断監査でbatch権限をUI 212のallowlist保守function方式へ修正し、固定search_path・PUBLIC revoke・直接DML禁止を具体化。 |
| 2026-08-31 | 横断監査でmetadata file名256 byteとstorage segment 255 byteを分離し、link/media/notification/logのNN・state・複合CHECKを補強。 |
| 2026-08-31 | 横断監査で全RequestのInbox HMACをNNとし、state/result/response snapshotのNULL組合せCHECKを追加。 |
| 2026-08-31 | 横断監査でLoginのUUID sessionとbigint業務参照を分離し、Inbox result referenceの型別排他的CHECKを追加。 |
| 2026-08-31 | 横断監査で`pg_dump`のSELECT要件とbatchのciphertext閲覧禁止が両立しないため、専用`schubert_backup` role案をQA-043/UIC-003として保留。 |
| 2026-09-01 | QA-043/UIC-003承認を反映し、dump専用`schubert_backup`と通常保守用`schubert_batch`のrole/grantを確定。 |
| 2026-09-03 | SSC-005を反映し、`app_logs.security_hold_until`とcategory制約、cutoff判定、ops非公開を確定。 |
SSC061/PG168: backup両完全handleの同一transaction確定/照合を341 §6.6で具体化する。BackupStepRepositoryは既存batch_runsの14列を2id昇順FOR UPDATEで全値検査し、両RUNNING/同一end両SUCCESS以外を保全拒否。BackupCommitServiceがborrowed Connectionのrollback/commit/再読を所有。新table/FK/DDL/grantなし、V001～020と400日保持を変更しない。root manifestの生成/保持inode信頼・実体/OS前提はcaller未完了gateとして明示する。

## SSC-434 Revocation AAD所有fieldの消去を一箇所へ集約（2026-11-16）

RevocationPayloadIdentity.aadで作成したowned六field byte配列の既finally消去loop（元順Arrays.fill(field,0)）を同classのprivate static eraseFields(byte[][])へ同bodyで一箇所集約し、finallyはこのhelperを一回呼ぶ。六field内容/32bitBE長/UUID全bit/epoch秒signed64+nanos32bit/返却配列/取得前検証/消去順・回数・例外優先/公開API/QA050再送間隔/暗号仕様を変更しない。PG34695で通常return/例外finallyの同一消去loop二重生成を確認、正常aad公開package口からhelper全条件を検証する。正常・異常を架空に増やさず、実OOM/ThreadDeath/非公開反射/SDK代替/到達不能/coverage除外で穴を隠さない。原RevocationValueContractTest4とExceptionValueContractTest1の全source/独立113byteAAD期待/境界/null/clone/value/列挙期待はbyte exact保持、新Test定義0。freshMain5RootNullAway/静的/currentProtocol176/物理182CRC-init/XML、一source/runの必要whole5とraw対象六classのLINE/METHOD/CLASS/BRANCH100を確認し、補足INSTRUCTION/COMPLEXITY不足はそのまま明記する。旧5成功/default/rawを新sourceへ流用又はexec合算0。Claimed/PendingRepository/Root2Actual4/実鍵-DB-JMS-取消再送/VM/native/aru/HOLDは操作せず、helperを公開・外部設定・新portへしない。

BUG3074/YKT2431、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-435 Revocation AAD所有fieldの取得を終了保護領域内へ移す（2026-11-16）

RevocationPayloadIdentity.aadのowned六field取得をcleanup領域内へ移す。try前では要素が全てnew byte[0]である六slot配列の形だけを確立し、元literalの六expr（purpose/table/UUID/time/format/version）を元順でtry内のfields[0]..[5]へ代入、その後の長計算/ByteBuffer/返却値はそのまま保持する。既finallyのprivateeraseFields(fields)一回で、version.getBytes(null)等の部分取得中断も取得済み全slotを元順zeroする。空slotをnullにせずconstructor/factory内部invariantとNullAwayで担保、未取得slotのemptyzeroは無害。元null版の例外型/NPE診断・正常113byteAAD・元expr順/UUID秒nanosBE/版byte/返却配列/公開API/QA050再送/暗号仕様を変更しない。SSC434時点は原全5成功だがrawLINE1未完、PG34724の5I/1LINE未達とBUG3074/3075を保持して品質完了へ算入0。元二Testclass/全5本文と独立AAD/境界/null/clone/列挙期待はbyte exact、新定義0。新source必要whole5/freshMain5RootNullAway/全静的/182physicalCRC-init/XML/raw六classの必須四100を検証、補足I/complexityも値を明記。実OOM/ThreadDeath/偽例外port/私有反射/除外/到達不能/旧exec合算で穴を隠さない。実鍵/DB/JMS/再送/Root2Actual4/Claimed-Pending/VM/native/aru/HOLDを追加しない。

BUG3074/3075/YKT2431、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-438 batch理由の固定診断metadata責務（2026-11-16）

BatchStepResult.Reasonの固定11診断を各enum定数のfinal nullable diagnosticSummary fieldで表し、private constructorの@Nullable String引数へ既定値を明示しsummary()はそのfield読取とする。NONEのみsummary NULL、ALREADY_SUCCESSFUL→step already successful for business date、BACKUP_UNAVAILABLE→verified backup unavailable、PROTECTED_RECORDS→protected records retained、ABANDONED→previous same-run attempt abandoned、DATABASE_FAILURE→batch database operation failed、COMMAND_FAILURE→batch command failed、SAFETY_FAILURE→batch safety check failed、IO_FAILURE→batch file operation failed、TIMEOUT→batch step deadline reached、INTERRUPTED→batch step interruptedの既存固定文を完全保持する。enum名/順序/ordinal/public descriptor、Reason.code()及びallows(Status)の全body、外側recordのStatus/Reason NN・各計数非負/SUCCESS failure0/SKIPPED全0と17許容27拒否の44組合せ・固定秘匿診断を変更0。private constructorは閉じたenum初期化だけでnullableは既存NONEの契約を表し、任意入力/例外/SQL/path/body/credentialを診断へ取り込まない。switch式が生成するsummary default1分岐6命令の未実行BUG3085を除外/到達不能/反射/偽enumで埋めず、既定値を保持する責務表現へ是正する。元独立全4Testsource/fixture/全期待をbyte exact保持、新sourceのfreshMain1RootNullAway/全静的/同singleexec全4/current179physicalCRC-initXML/raw全三Codeclassで確認する。DB schema/値互換/transaction/原本/所有/権限/HTTP/UI/電文/DIF変更0、元8反射fixtureやRoot2Actual4/DB鍵/VM/native/aru/HOLDを実行・抽出・代替0。旧sourceのdefault四100/raw不足を新sourceへ加算0、正式/全WBS/451/終了依存は別受入を維持。

BUG3085/YKT2431、状態:設計確定・main反映前、PG/PT/全criteria・終了依存/正式未完。
