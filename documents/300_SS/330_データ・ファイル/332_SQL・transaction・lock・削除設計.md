# SQL・transaction・lock・削除設計

## SSC341 Morning専用DBの既知SQL変換とconnection解放の限定fatal確認（2026-11-13）

BUG2852/YKT2359、SS341/343、WBS-P017-01.03/P017-02.03、PT-MDB-CAT341-001～012。対象はMorningDatabaseSessionの既知SQLException/BatchRepositoryExceptionから固定IOExceptionへ変換する既存20捕捉箇所と、そのexecute所有connectionのSQL close変換/closeReplaceだけである。既SS332のtyped priorityを先に適用し、batchのchecked IOException/未知Runtime/Errorを一般化して置換しない。SQL、DB role、transaction/commit/rollback回数、run/cutoff、原本・M/A/advisory・callback lifetime、正常結果を変更しない。

- 捕捉したSQLException又はBatchRepositoryExceptionを固定診断へ捨てる直前だけ、既storage.StorageIoExceptionのpure finite graph portでcause/suppressed/SQLException.nextをidentity visitedで確認する。到達可能なErrorは元objectで伝播し、非fatal循環は有限帰還、新IOExceptionのmessage/cause/suppressedへprovider本文/graphを保存しない。SQLExceptionでもBatchRepositoryExceptionでもないchecked IOException/CleanupStoppedException等は既固定化・既型順位のままとする。
- execute最外捕捉でこの確認がErrorを伝播する場合、finallyのprimaryにもその実Errorを記録してからthrowする。元SQLExceptionをprimaryのまま残して未知cleanupにErrorを上書きさせない。分類を追加したことでowned credentialのwipe/close、取得済connectionの一回close、Session.active=falseを省略しない。
- body成功後のconnection.closeがSQLExceptionの場合は、そのSQL graph確認後だけ既固定IOExceptionへ変換する。nonnullのSQL/BatchRepositoryException primary＋SQL secondaryは、既false選択で破棄する前にprimary graph→secondary graphの順で確認する。両方非fatalなら既固定結果を保持する。
- 既SQL primary＋未知cleanupのcleanup選択、未知Runtime/Error primaryの同一性＋新固定secondary、同一Throwableのself-suppression回避、checked IOException primaryの既処理を変更しない。既policyで先に選択されるunknown/checkedIOへ新しい一律graph分類を追加しない。null primary・取得失敗・直接Error等の既各経路と明確に区別する。

本補足は例外の既固定化境界だけの内部具体化であり、raw graphのlogging、追加DB/close/rollback/stop/再送、非同期callbackや合成capabilityから実所有を推定することを許可しない。実DB/Root/VM/原本/Backup/鍵/native/intent/permit等のHOLDは不変更。source強化review/静的確認と未実行PT・coverageを分離し、同sourceの全関連単体/実DB/所有後条件と451未完を保持する。


SSC320（2026-10-21、ordinary API Outbox/BUG1567）：factory自身がopenしたnonnull connectionのsetAutoCommit(false)を含む返却前setupはSQL/RTE/Error全てで保護し、失敗時に一回closeしてから失敗を伝播する。caller TWRへまだ渡っていないことを理由に未closeを許容しない。primary Errorは元identity、nonfatal primary＋cleanup Errorはcleanup Error identityを優先し、異なる元primaryをsecondaryへ保持する。非fatal同士は既primary/固定分類を維持し、同一Throwableを自身へsuppressed追加しない。setup close及び既rollbackの二次失敗に適用、追加rollback/close/claim/commit/JMS sendや新TXを発行しない。正常claim/mark TWR・短TX/no-XA・借用Connection非所有契約・SQL literal/role/backoff/leaseは不変更。WebLog等の既全体try/finallyは個別の適用/非該当確認とし、batchの既SQL/unknown変換を一括変更しない。

SSC310（2026-10-20、BUG1530/YKT1290、Expiry監査read局所補足）：SSC200保持SUCCESS照合からも呼ばれる`ExpiryAuditRepository.read`のStatement/ResultSet二scopeへSSC063199の既優先順位を明示適用する。取得後ただちにprimary記録とtyped try/finallyで保護し、取得nonnull確認/body中のSQL・未知Runtime/NPE/Errorを記録してから同じ資源を逆順に一度direct closeする。SQL primary＋SQL secondaryは原因/suppressedなし固定BatchRepositoryException、未知primaryは同一instanceを保持しsecondaryには新しい固定BatchRepositoryExceptionだけを追加する。同一Throwableも自身へ追加せず、SQL primary＋未知cleanupは未知cleanup同一instanceを優先する。成功bodyの結果も両close成功まで返さない。

`read`のnull Statement/ResultSet・必須DB列nullと既validSnapshot=falseだけを固定SQLDataExceptionへ分類し、最外側はSQLだけ固定BatchRepositoryExceptionへ変換する。getter/prepare/query/close等provider呼出をpure投影検査と分け、未知IAE/ISE/NPE/Errorを広いRuntime catchで正常化・固定化しない。public attempt/constructor null・不正step等の契約拒否は従来どおり。cutoff/ended/nullable before/after・既Snapshot検査、全SQL/bind/queryTimeout5秒・同run guard前後・取得失敗時未取得資源close0・借用Connectionのcommit/rollback/config/close禁止は不変更。

範囲は`read`二scopeのみ。SS343SSC304の`successful`直下usingJdbc二scopeはJava25 TWRの同一secondary/self-suppression契約を維持し、JdbcResourceFailuresへ置換しない。stage/finish直下のupdate/TWR/既変換契約は今回一括変更しない。既BAT287のprovider readRuntime固定期待だけを未知同一性へ是正し、SQL・null・不正DB投影の固定拒否は保持する。EXP310001..003の独立pure proxy反例/68合成/正常null投影、実DB既Expiry・保持SUCCESSと必要影響回帰・同source品質で追跡する。PG/PT/native/正式の完了は別認定。

SSC199（2026-10-06、BUG784/YKT560、SS341 Cleanup終端readback）：SSC063の合成順位をCleanupTerminalRepository.read/readRejected/references各二owned scopeにも適用する。SQL primary＋SQL secondaryは固定BatchRepositoryException、未知primaryは同一性＋新固定secondary、SQL primary＋未知cleanupはcleanup同一性を優先。同Throwable再送でもself-suppressionしない。Statement/ResultSetの一回direct finally closeは当Repository内のprivate typed scopeで行い、JdbcResourceFailuresは順位だけを判定する。全十四列のprovider getter/prepare/queryはpure projection検査の外に置き、enum/時刻/recordの不正値のみ狭くSQLDataExceptionへ分類する。driver Runtime/NPE/Errorを広いIllegalArgumentException catchへ含めない。body成功後もclose正常帰還まで値を返さず、borrowed Connectionのcommit/rollback/config/close0。既七step・同run/date/全列・親期限前後・SQL literal/返却shape・起動許可は不変更。CTERM006～008の独立projection/68合成×三経路・正常SQL後条件と必要全回帰/nativeを要求、host proxyを実所有の代用にしない。

SSC175（2026-10-04、QA048/SS331§9.4）：受付参照の孤児cleanupは固定`WEB_RECEIPTS` kindと`maintenance_cleanup_web_receipt_references(uuid,timestamptz,integer)`を用い、既存`CLEAN_BATCH_RUN` handleのatomic chunk境界へ接続する。NULL/無限・範囲外cutoff、limit1..1000、閉じたkind、同run/date/完全step identity・RUNNING状態を既存同様に検査する。親OS/session advisoryを保持した既定の順、両backup共有lock→現在run参照→親step NOWAIT→locator候補を維持し、statement中の観測だけで決定する。候補はreceipt_id順/最大1,000/FOR UPDATE SKIP LOCKED、現在業務questionsにquestion_idが存在しないものだけ。DELETE＋既存step target/success累積は同transactionで、共有step全kindの順序/累積を維持する。chunk0でもeligible EXISTSが真ならLOCK_BUSY非完了、未知/SQL/commit/close失敗はcallerがrollback/隔離し、単なるDML成功をstep成功にしない。単独孤児functionを呼んだ結果だけで親step終了を証明しない。SECURITY DEFINER/nk_owner・固定search_path/UTC・PUBLIC EXECUTE0、batchに完全signature EXECUTEのみ、Web/business直接権限は増やさない。新operation UUID生成/質問再発行/業務DB修復は本保守の責務ではない。

SSC063/PG183（修正前）: BatchRunRepositoryのhistory/insert/replayed各Statement/ResultSet、abandon/finish Statement計8scopeへPG179のdirect finally close/SQL対unknown優先順位を適用する。begin/finishはSQLだけ固定化し、insertのid getterとpure BatchStepAttempt構築を分離して不正id等の値だけSQL不正へ変換する。SS331§8.3の未知Runtime非正常化と不正投影固定をこの境界で具体化し、旧BAT151のprovider IAE固定期待はBUG206/YKT162影響として訂正する。public不正入力、DB不正投影、全SQL/順序/件数/lock/borrowed transaction/terminal replayは不変更。017068・BAT151と既存BAT138～153へ追跡する。

SSC063/PG182（修正前）: BackupStepRepository.inspectのpair Statement/ResultSet2scopeへPG179のdirect finally close/SQLとunknownの例外順位を適用する。元のSQL-only catchとpresentのNULL固定拒否、14列/fullhandle/時刻/2状態一致/前後guard/borrowed transactionは変更しない。017066・BAT216/既存BAT210～225で68複合とpair/commit/replayの元期待を再確認する。BackupStep自体のprovider IAEは従来も未知であり維持、completeから呼ぶBatchRun.finishは別の横展開対象。

SSC063/PG181（修正前）: CleanupStepRepository.executeの2 owned JDBC scopeへPG179のdirect finally close/例外順位を適用する。counts/nullable累積/complete/reasonのJDBC取得とpure値構築を分離し、CleanupCounts/Reason/CleanupStepChunkの検査IAEだけをSQL不正に変換する。provider未知IAEは同一性を保持する。元presentによるNULL resource/NULL列の固定SQL拒否、7kind・limit・run guard・SQL/bind順・borrowed transactionは維持する。017064・BAT168と既存BAT162～169で68複合/独立rollback後条件を検証し、未確認Repositoryは未完了に保つ。

PG180のJDBC resource null契約: CleanupRepositoryのprepare/executeQuery結果はJDBCのnonnull resource契約を取得境界のObjects.requireNonNullで確立する。違反時は固定messageのNPEとして非正常拒否し、SQL column NULLの固定DB不正とは区別する。NPE正常化、未取得resourceのclose、borrowed Connectionの所有移転を行わない。062の4 null反例で既存の非正常性と解放責務を確認する。

SSC063/PG180（修正前）: 下記PG179のdirect JDBC close/SQLとunknownの優先順位をCleanupRepository.execute/readLogProgressの4scopeにも適用する。JdbcResourceFailuresは例外順位だけ共有する。countsの3getter、reason_code/completeの取得をprovider呼出としてconstructor/enum変換catchの外へ置き、CleanupCounts/CleanupChunk/CleanupReason変換の不正値だけSQL不正へ固定する。8kind allowlist、引数・limit・呼出SQL・元projection/NULL・取得後のborrowed未commit結果は変更しない。owned Statement/ResultSetのみcloseし、Connectionのcommit/rollback/config/closeはcaller専用。017062/063・BAT012と既存17件へ追跡し、全136複合と独立rollback後条件を確認する。BUG195/206・YKT154/162の他Repository分類は残す。

SSC063/PG179・BUG195/YKT154・BUG206/YKT162（修正前）: RunReferenceRepository/InspectionSummaryRepositoryは4 owned JDBC scopeをdirect finally closeで一度ずつ解放する。SQL primaryとSQL secondaryは固定BatchRepositoryException、未知Runtime/NPE/Error primaryは同一性を保ちsecondaryは新しい固定BatchRepositoryExceptionだけsuppressedへ追加する。同一Throwable再送を自身へ追加しない。既知SQL primary＋未知cleanupはcleanup同一性を優先する。body成功後もclose成功まで結果を返さない。借用Connectionはclose/config/commit/rollbackしない。不正DB投影はRunReferences/CleanupCounts/InspectionSummary構築だけを狭いIllegalArgumentException catchで固定SQL不正へ変換し、JDBC providerの未知IllegalArgumentExceptionを巻き込まない。既存null projectionはSQL不正、constructor/API nullは契約違反を維持する。private packageのJdbcResourceFailuresは例外順位だけを共有しJDBC closeやtransactionを代行しない。017060/061・BAT087/121、既存全16 PTで追跡する。他Repositoryと外部Infrastructure変換境界は別に分類する。

SSC055/PG163（先行898cc267）: 親BatchRunRepositoryの全仕様は331 §8.3。親がexplicit transaction/RW/READ_COMMITTEDを所有し、前後の同run参照/自己DB排他、日別stepの最大99行FOR UPDATE、明示同run RUNNING recovery、通常成功skip/backup例外、全identity CASと同値terminal replayを実施する。Connection commit/rollback/close/config変更を行わず、返却後commitの成否はcallerが判定する。全bindは型付き・UTC4.2、同date/step内の過去別runを現在原本cutoffへ再束縛せず、legacy診断を投影しない。失敗時の一部DMLは未確定でrollback必須、単なるexecuteUpdate成功をstep完了にしない。

SSC049/PG162（先行d23b1afd）: 親Inspector summaryは331 §3.13の固定4列readだけを借用Connectionで実施する。InspectorLockHandoffと同じparent autoCommit=true/readOnly=false/READ COMMITTED、queryTimeout5秒、UUID＋JDBC4.2 UTC OffsetDateTimeの固定bind。開始時/返却直前割込を拒否し、statement/result全close後だけ0/1行のOptional値を返す。null4列/複数行/不正counts/SQL・close故障は原因/suppressedなし固定BatchRepositoryException。constructor/run nullや未知runtime/NPEは成功化しない。connection commit/rollback/close/config変更/新接続・progress補完を行わない。子引渡し前後の独立fresh queryであり、関数が実子状態やOS lockを認証するものではない。

SSC-055/PG-D-159（先行4c5dcb85）: 331 §3.12のrun参照readは新規collision/resume整合/GC保全の共通非秘密観測。親は単独所有Connectionのexplicit transaction・READ COMMITTED・readOnly=falseで実行し、固定OS/DB lockを対象file mutationまで保持する。single snapshotの存在と整合を返し、rollback/commit/lock解放後の結果を再利用しない。service停止やDB不通時は補完せず保全する。SQL readはrow更新/lock取得/backup成功を行わず、通常step/進捗writerも既存保守排他規約を守る。管理者の手動DMLや別connection共有を検査済みとして許可しない。

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

SSC056/PG160（先行8002b28b・3cf06b00）: Java InstantとPostgreSQL timestamptzの境界はJDBC4.2を使い、setObject(index, instant.atOffset(ZoneOffset.UTC))、getObject(column,OffsetDateTime.class)→null契約確認→toInstantに統一する。java.sql.Timestamp/getTimestamp/setTimestampで歴史暦やdefault timezoneを経由しない。SQL NULLは既存Optional/必須列検査を維持し、値0やepochへ補完しない。PG-D-159もこの規則を適用する。年月日だけのLocalDateは時刻へ変換せず既存date型対応を維持する。既存SQL/parameter番号/transaction/lock/µs範囲・wire表示は不変、新DB columnや推測backfillを追加しない。

独立PTは明示UTCのSQL literal/extract(epoch)と原本Instantで期待値を決め、同じJDBC変換でfixtureとexpectedを生成しない。UTC0001・1582前後・1900・現代µs・UTC9999とUTC/JST/NewYork session、両方向bind/projection、NULL/欠落/未知、全JDBC fault/close所有を対象classへ横展開する。元Timestampの年0001反例を固定記録し、同じ方式へ戻ることをstatic/architecture canaryで拒否する。現在の23 classと既存OffsetDateTime classの全回帰が完了するまでYKT128/SSC056を閉じない。

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

SSC-036、Log query SQL補足: UI225 §2/235 §11のLog検索・LGSRSP01の許可levelはINFO/WARN/ERRORである。app_logsに診断TRACE/DEBUGが存在してもwire enumの拡張・INFOへの置換をせず、表示用count/listの共通predicateへ`level IN ('INFO','WARN','ERROR')`を必ず適用する。明示Level条件はこの集合内で追加する。診断rowを削除・改変しない。空filterは画面が扱う全3levelを意味し、診断だけなら0件/page1となる。表示対象とtotal/pageの不一致、診断rowによる応答全体9000を起こさない。UI235のFrom/Toはoptionalのまま。§13の「日付条件必須」は計測caseであり、未指定/片側指定をAPIで拒否・期間補完する意味ではない。PG-D-090/PT-ADM-055～060で実DB混在・診断のみ・全filter・wire/count/list・無更新を確認する。

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

SSC-023: snapshot前の認証事前確認は312 §3.3.1のread-only JOIN SELECTで行い、User/sessionをlockせずidleも更新しない。READ COMMITTEDの参照結果を将来の認証保証にせず、file I/O後の最終write transactionで現在の認証/認可を再確認する。既存の通常認証verifyをread-onlyへ置換しない。

SSC-027補足（4.2のScenario再生成）: 最終write transactionで324 §7.1のrow lock/owner/HMAC/旧snapshot一致を確認してから、`update schubert.request_inbox set response_body_encrypted=?,response_key_version=? where message_id=? and processing_state='COMPLETED'`を実行する。SQL後条件は更新1件、他17列（初回completed_at/expires_atを含む）不変。失敗はcaller rollback、commit確認後にのみ応答する。PT-IDEM-SR01～SR03で本番DDL/限定app roleの実PostgreSQLにより検査する。

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
       retry_count=least(:delivery_count - 1, 3),
       version=version+1
 where id=:job_id and state='RECEIVED';
```

0件の場合はjobを`FOR UPDATE`で再読し、COMPLETED/CANCELLEDおよび確定済み業務ERRORは冪等ACK、最終retry ERRORは既存DLQ dispatch DのSENT確認後だけACK（SSC156、SS312 §9/SS353 §7.2）。PROCESSINGは
`processing_message_id`一致のみcrash recovery、不一致は整合errorとする。
実delivery countはmetadataへ非capで保存する。retry_countだけDDL上限3に制限し、actual countを捏造しない。

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
2. Questionをlockし削除flag/時刻/actor三点を継承して`answers(question_id UK)`へINSERT。既存answer/provider/time/削除三点を検証し、同一なら冪等完了、矛盾は整合errorとし上書きしない。
3. Providerの`AnswerResult.answeredAt`を有限UTC microsecondへ正規化し、job started_at/received_at以前を拒否する。同じ値でanswer answered_at、Job/notification state_changed/completed/answered_atを更新する（SSC156）。STUBは現在時刻・空本文。wire projectionだけmillisecondへ切詰め、DB時刻をwire精度に合わせて変更しない。
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

SSC057/PG164: 非Log/非秘密Inboxの7cleanup callerは331 §3.14のV020を用い、既存DELETEとRUNNING stepの件数加算を同transactionで確定する。backup→full step NOWAIT→候補のlock順、既存predicate/1,000/SKIP LOCKEDは不変。0件は候補非lock EXISTSで0を確認した場合だけ終端、残行はLOCK_BUSY非成功。FK23503はQUESTIONSだけ保全deferredで上位へ返し、全削除済みにしない。詳細optional累積/型/rollback/30分は331 §3.14、PG163のbegin/finish・親OS/実backup/全kind順序を代行しない。

Batch開始時の`:run_started_at`を全stepで固定する。当日`BACKUP_DB`/`BACKUP_CONFIG`がSUCCESSでなければ
業務data/inbox/outbox物理削除をSKIPPEDとし、application起動はQA-029に従い続行する。

SSC-050/PG-D-129: SQLへ渡すcutoffは全cleanupでrun_started_atに統一する。log_cutoffはその2160時間前、batch_run_cutoffは9600時間前を関数内で計算する。有限値だけを許可し、331 §3.3.1のlock済backup2件判定を全cleanupへ適用する。Log holdの比較相手は従来どおりlog_cutoffでありrun_started_atへ変えない。Batch履歴の400日はstarted_atでなくended_atから計測し、同runのRUNNING/FAILED調査を保護する。

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

SSC-049/PG-D-126補足: V011以降のmaintenance_cleanup_message_storesは上記2のOutboxだけを処理し、3のInboxを読み書きしない。通常batchのOKをInbox検査完了の証明にしない。Inboxは専用processの候補lock→暗号/参照検査→条件付き削除という同transactionの経路だけで処理する。全件検査の未起動/失敗は親stepで非成功として記録・警告し、検査しない削除へfallbackしない。通常batchの直接Inbox権限は追加しない。

## 12. Deadlock・競合防止

SSC-051/PG-D-136（BUG-104）: §11.4 Log chunkは331 §3.9の永続(logged_at,id) cursorでholdも走査済みへ進め、DELETEと累積countを同commitする。limitを満たすholdだけのchunkでも次のeligibleへ進み、target0/END前に完了としない。同run後続の保全行再計上はしない。Log候補だけNOWAITを採り、競合時は全chunk rollback・LOCK_BUSYで進捗不変。SKIP LOCKEDで未取得行より先のcursorを確定する方式は使わない。[PostgreSQL 18 SELECT lock](https://www.postgresql.org/docs/18/sql-select.html)と[PL/pgSQL例外blockのrollback](https://www.postgresql.org/docs/18/plpgsql-control-structures.html)を根拠に実DBで検証する。他cleanupの既定SKIP LOCKED/保持値は不変。

| 処理 | Lock順 |
|---|---|
| Login | User → IP attempt → auth sessionsの時刻/ID順 |
| User管理更新（SSC-031） | context owner候補の非locking lookup → ADMIN advisory lock（減員し得る時だけ）→ actor/target/必要active ADMINのUser ID昇順 → context session owner再照合lock＋通常verify/ADMIN認可 → Inbox → command対象session ID順/監査 |
| Question submit | Inbox/token → question → job → notification → outbox（新規INSERTのみ） |
| Cancel/worker | job ID → notification ID → answer（完了時） |
| Logical delete | Inbox/token → question ID → answer question ID → audit |
| Cleanup | batch advisory lock → 対象tableのPK昇順。異なtableを逆順lockしない |

DB deadlockが発生した場合は一時障害としtransaction全体をrollbackする。UI更新を内部で再試行せず、
operation tokenによる再操作またはJMS redeliveryで整合を保つ。

SSC-031のUser集合はactor候補/targetと、減員時だけrole=ADMINかつstatus=ACTIVEの全rowをORで選び、ORDER BY id FOR UPDATEで同時に取得する。通常verifyでactorを先に単独lockしてからadvisory/別targetへ進むことは禁止する。Session ownerを再照合する前の候補lookupは許可判定ではない。preludeとverify/Inbox/commandの間でcommit/closeしない。ADMIN減員以外へ71419601を無条件適用せず、固定keyの用途を拡大しない。直接command部品PTはcallerがこの順序を満たすfixtureとし、本番登録は実preludeとの接続・相互更新/再送PT後だけ許可する。

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

## SSC-424 JDBC資源nonnullと発行・監査の明示終了（2026-11-15）

AuthSessionService.issue及びSessionAuditWriter.writeの全owned PreparedStatement/ResultSetは取得直後に既RequiredColumn.requireValueを通しnonnullを確立する。provider返却nullは既22004 SQLDataExceptionとして拒否し、発行側は既9000固定AuthenticationInfrastructureExceptionへ変換する。正常SQL/順序/binding/lock/rowcount/時刻8時間/microsecond/DIF016/監査JSON/role/owner/暗号/format/public API/呼出元TX所有を変更しない。Connectionは借用でcommit/rollback/close/setAutoCommitを行わず、取得できたstatement/rowだけを一回逆順にcloseする。各nonnull資源の本体を明示try-catch(SQLException|RuntimeException|Error)-finallyで保護、catchはnullable primaryへ同一failureを保存して再throwし、finallyはAPI database内の小さいstateless JdbcResourceCleanup.close(primary,SqlClose)でcloseする。SqlCloseはthrowsSQLExceptionに限定したfunctional interface、cleanupはstatic操作だけを持つ非生成可能interfaceで余分なconstructor/instance状態を持たない。action nonnullは呼出前提。close成功はprimary graphへ変更0、primary無しclose失敗は同一SQL/RTE/Errorを伝播、primary有りclose失敗は元primary.addSuppressedで元graphを保持、同一instance self-suppressionはJDK IllegalArgumentException/causeをTWR同様に維持する。Batchの別failure precedence helperを流用せずAPI→Batch依存0、fatal分類の追加/変更も0。INSERT ciphertextはprepare/nonnull検査まで含む最外側の既finallyで必ずzeroにし、取得失敗を保護域の外へ出さない。resource nullは取得無しでrelease0、row nullでも既statementは一回closeする。外部設定/provider/driver接続/資格/権限/秘密/DDL/電文/承認済DIFを追加変更0。

原issue8/audit9の全Test本文・独立三AESgolden/固定hash/完全SQL/UTC/JSON/alias/error/所有/finite workerを保持し、Issueの既純粋Proxy FixtureへnullStatementAt/nullRowAtのdefault空値controlだけを追加する。新AUT-ISS-RESOURCE001/002はstatement五箇所(USER/INSERT/ACTIVE/REPLACE/AUDIT)とrow二箇所(USER/ACTIVE)のnull返却を独立に与え、9000固定/cause-suppression初期0/owned row-statement一回close/借用TX変更0/entropy-nonce-ciphertext全zeroを確認する。新JdbcResourceCleanupTest全五はaction null前提、通常closeの呼出一回/primary不変、primary無しSQL-RTE-Error同一、primary有り各closefailureの正確なsuppressed identity、selfaliasの元IllegalArgumentException causeを固定graph期待で検証。期待をproduction cleanup/hash/codecで作らず元literalと独立公開objects/countersだけを使う。新七だけ新定義、旧十七は新Main必要再資格で新規加算0、全二十四を当source一singleexecにしてfreshRootNullAway/static/Code物理実測/CRC-init/XML/default+raw必須四を照合する。新interface/SqlClose/package Code0は自然値、未実行をcompiler除外/到達不能/旧exec合算へしない。実DB/生session/Root/cohort/VM/native/aru/actual4/Root2/SDKbackend/HOLDは未受入を維持する。

BUG3033・YKT2553/2546。状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-425 JDBC型付き終了所有契約（2026-11-15）

SSC424のcallback越しclose所有がSpotBugs OBL一件として未確定となったため、JdbcResourceCleanupへStatement専用closeStatement(primary,statement)とResultSet専用closeRows(primary,rows)を追加する。両者はnonnullを明示検査し、直接resource.closeを一回呼び、SQL/RTE/Error失敗はprimary無しで同一throw、有りで元primary.addSuppressed、自分自身の場合も元JDK IllegalArgumentException/causeを維持する。既close(primary,SqlClose)及び原五testは保持する。親Issue/Auditは型付きadapterへ変更するだけで、SQL/binding/8h/DIF016/暗号/borrowed Connection/TX/INSERT最外側消去/既例外graphを変更しない。実漏れは未確認で、抑制/除外による静的合格にはしない。既取得SDK com.google.code.findbugs:jsr305:3.0.2 の実在javax.annotation.WillClose（RUNTIME retention、通常parameter所有契約）をAPI provided依存として宣言し、各typed parameterへ付与する。注釈はclose責任の宣言でありSuppressFBWarnings等の抑制ではない。SDK変更/ダウンロード/実DB/driver/権限/外部経路追加0。原SpotBugsannotations4.10.4に同annotationがあるとのBUG3034初記述は誤認であり、実SDKメタデータの照合で訂正する。新二testは両adapterごとにnull前提/正常/SQL-RTE-Error/primary/alias/一回closeをJDK純粋Proxyと独立identityで検証し、新合計九＋既十七の必要全二十六をfresh同source compile/NullAway/static/CRC/XML/必須四rawで測定する。原二十四未実行をPASSへ加算0、旧compile/static一件は歴史証拠として保持する。

関連BUG3033/3034・YKT2553・SSC424。状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-426 API取消JDBC資源nonnullと明示終了（2026-11-15）

AuthSessionRevocationServiceのlogoutCurrent/revokeAll/updateにおけるowned statement五取得/row四取得を取得直後RequiredColumn.requireValueでnonnullに確立し、既SSC425 JdbcResourceCleanup.closeStatement/closeRowsと明示primary(SQL/RTE/Error同一再throw)-finallyで一回終了する。SQL文字列/binding/order、User/session lock後clock採取/microsecond、期限境界、既取消済idempotent/監査理由/ADMIN認可/N12/allowed-reason/rowcount/例外分類/元graph/selfalias/borrowed Connection/TX所有を変更しない。悪いnull providerは既22004に統一、resource無しをcloseしない。Audit/Hash/helperは既同byte、実DB/driver/Root/サービス/VM/鍵/権限/HOLD変更0。原SessionRevocationJdbcPortTest8の完全SQL/固定SHA/JSON/UTC/lock後時刻/全null/role/owner/理由/再送/rowcount/cleanup/並行期待を保持し、無期限pool closeだけshutdownNow→await10assert/classTimeout30に是正する。既fixtureへnullStatementAt/nullRowAtのdefault空controlを追加、新二件はLogout U/S/X/LとADMIN T/A/X/L statement及びU/S/T/A rowのnullを独立入力して固定9000/owned一回/borrowedTX0/後続処理非発行を検証。原八＋新二全十をfresh閉じたMain/RootNullAway/static/CRC-init/XML/実Code必須四で測る。旧DBfixture/旧012全APIjarを流用しない。

BUG3035/3036、YKT2546/2553、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-427 認証検証のnonnull終了とprivate carrier（2026-11-15）

AuthenticationContextVerifier.verify/readSessionの三owned statement/二row取得へ既RequiredColumn.requireValueを置きnonnull・22004を確立し、既typed JdbcResourceCleanupとprimary SQL/RTE/Error同一再throw/finally一回終了を使う。verify/inspectReadOnlyの公開signature、SQL literal/順序/User→session lock/currentActor/role/期限/readonly非lock非touch/UTC/8h greatest touch/rowcount/固定失敗分類/borrowedTX/秘密/電文は不変。private VerifiedSessionは二fieldを当class内のreadSession→verify/inspectだけへ運ぶ非公開carrierであり、参照するのはid()/actor()だけ。recordの値同一性・自動表示・hashを業務契約として使わないため、private static final classへ整理しfinal UUID sessionId/final AuthenticatedActor authenticatedActor、constructorでObjects.requireNonNull二つ、同名二accessorだけを持たせる。外部型/serialization/wire/public値契約の変更0、不要なprivate値操作やテスト専用口を追加せず、全残Codeを通常公開業務経路で意味ある期待により検証できる形にする。測定から既Codeを除外/到達不能認定せず、旧record形状は歴史として保持し新形状を独立測る。原AuthenticationVerifierJdbcPortTest6のSQL/hash/currentDB actor/readOnly/拒否/nullcolumn/rowcount/cleanup/未知RTE/並行全期待を保持、workerのみshutdownNow/await10assert/Timeout30へ有限化する。既FixtureのnullStatementAt/nullRowAt default空controlとacquired記録を追加、Mapのnullable要素とruntimeFailure nullableをJSpecifyで明記する。新資源null二はverify User/Session/Touch及びinspect READ statement、verify User/Session及びinspect Session rowのnullで固定9000/取得済一回close/borrowedTX0/最後SQL一致を独立検証。原六＋新二の全八、Main閉包11（SDKjsr305だけ追加で既取得/全Protocolは同byte）/freshRootNullAway/static/全物理CRC/XML/default及びraw必須四を照合。実DB/driver/旧全APIjar/Root2/Actual4/VM/native/aru/HOLD操作0。

BUG3039/3040、YKT2546/2553、状態:設計確定・main反映前、PG/PT/正式未完。

2026-11-15 SSC427継続補足（BUG3041）: private field名のみsessionId/authenticatedActor、既id()/actor()/nonnull invariant/SQL/public結果は不変、新fixture user labelは新側constant化・元6期待除去inverse保持。初回static32/未実行8を保存しfresh必要資格へ。
