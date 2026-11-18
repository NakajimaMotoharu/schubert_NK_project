# Outbox・Inbox・冪等性・再送設計

SSC329（BUG1592/YKT1345）：ordinary JDBCの23505/2200H等を重複・確定業務結果へ判定する前にも、完了済resource closeの例外graphにErrorが無いことを確認する。Error付きSQLstateをnormal duplicate/replay/validationへ変換せず、同一fatalを伝播する。raw SQLExceptionを上位へ渡すだけの箇所・rollback secondaryをprimaryへattachする箇所と、graphを破棄してcatalog/業務結果を生成する箇所を区別し、各最終受取境界とowned cleanupまで追跡する。既正常SQLstate/Inbox・Outbox atomicity・commit/rollback境界・retry/backoff/ACK順は不変更、未確認commitを失敗確定/再実行許可へ読み替えない。113明示SQL catchは検索範囲だけであり、非SQLの同じresource marker catchも個別適用性を点検する。全対象の修正又は非該当根拠・独立再発防止/同source品質が揃うまで横展開を完了としない。

SSC323（2026-10-21、BUG1573/YKT1328/1323）：ordinary WebLogDispatcherのtyped failureCode決定前及びWebLogReplayWorkerの周期retry前にもSS322と同じcause/suppressed/JMS linked/SQL next・identity-visited検査を行う。内包Errorを同一fatalとして伝播、非fatal循環は有限帰還し既ERROR/attempt/lease/backoffと固定redactionを維持する。一般session catalogの所有契約は置換せずordinary二境界の純粋非I/O確認へ限定、graph書換え/新mark/rollback/close/権限操作0。自己所有workerのterminal/failedCycle0、temporary DBの未mark/既claim保持と非fatal通常後条件を独立確認する。API/Webを同sourceで照合し中間の成功全回帰を目的無く再演せず、実Root/native/拒否保留の受入へ転用しない。

SSC322（2026-10-21、BUG1572/YKT1328/1323、ordinary API Outbox）：send失敗をmarkFailureへ分類する前、及びowned workerがSQL/RTEをtemporary retryへ分類する前に、cause/suppressed/JMS linked/SQL nextの失敗graphをThrowable同一性のvisited集合で走査する。内包Errorは同一Errorとして伝播し普通失敗mark/周期retryへ正常化しない。Error無しの循環/重複edgeは有限帰還し既ordinary分類・lease/backoff/固定redactionを維持する。確認は非所有・非I/O、graphへ新cause/suppressedを追加せずDB/JMS/close/rollback/再送回数/wire/権限不変更。直接cleanupのSS320/321順位と一般TWR正常契約は置換しない。自己所有fixtureの全edge/循環/identity、未mark/未再試行と非fatal後条件を同sourceで確認し、実Root/native/未確認資源解放の証明へ代用しない。

SSC321（2026-10-21、Web ordinary send/BUG1569/1570・YKT1323/1326）：ArtemisRequestSender及びWebLogMessageSenderの自らopenしたJMS contextはbody後・例外時とも一回closeし、正常closeまで成功を返さない。primary Errorは同一性を保ち、非fatal JMS/Runtime/typed primary＋close Errorはcleanup Error同一性を優先して異なる元primaryをsuppressed保持する。他のprimary/secondaryは元primary保持・異なるsecondaryだけsuppressed、同一Throwableを自身へ追加しない。primary無しは既close型境界/固定redactionを維持する。WLGは復号後の全終了でplain wireをwipeし、decrypt/取得失敗時は未取得contextをcloseしない。TWR生成のself-suppressionに元Error保持を委ねない。正常wire/TTL/MessageID/duplicate cause-linked判定、commit/rollback回数・DB/lease/backoff/権限は不変更。これは実Root/native/業務回収の証明ではなく、ordinary未接続proxyの独立PTと同source品質を要求する。

SSC320（2026-10-21、BUG1566/1567・YKT1323/1324、ordinary API Outbox内部補足）：send/claim/markの短TX分割、固定MessageID duplicate排除、lease/backoff/SQL/外部wireは不変更。送信の非fatal primary＋JMS close Errorをtyped送信失敗だけに落とさず、そのcleanup Error同一性をfatal側へ伝播し、異なる元primaryをsecondaryへ保持する。既primary Errorはその同一性を保ち、close Errorを含むsecondaryで置換しない。primary無しの既close境界・固定redactionを維持し、同一Throwableのself-suppressionを行わない。Errorを普通再送の成功/失敗markへ正常化しない。DB初期化でまだcallerへ返していないconnectionにもSS332の一回owned close/複合順位を適用する。これは実Root/native停止の証明や未知cohortの回収許可ではない。

SSC157（2026-10-02、実装前）：新QSS/QSDの取得scopeをSS352のNKQRY1内部frameへ暗号保存し、成功/確定error（特にADMIN全件9001）を同じscopeへ拘束する。read-only stageの取得scopeをwrite現在認証で上書きしない。取得USER又は現在ADMINなら元scopeの凍結結果を許可、取得ADMIN→現在USERはQSS0103/QSD0104を非保存で返しSECURITY監査する。失効は先に0102。元snapshot/state/code/completed/expiryは不変更、未保存stageならInbox handlerへ渡す前に拒否。NTS/NTDはowner固定・raw profile不変更。通常QSS/QSDは無scope旧rawを9000で保護し、現在質問/Usernameから所有scopeを推測しない。12.8の保守はprefixのsyntax/layout/固定wireだけ検査し、旧raw検査と現在role非比較を維持する。24h/owner/HMAC/NONE/外部電文は不変更。

SSC156（2026-10-02）：最終retry ERROR＋新D commit後は元Wを再処理せず、同Dの実SENTを短いDB観測で確認してから元ACK。通常送信/mark前crashはD duplicate IDで再送する。元JMS sessionのhard crash/rollbackではBroker max4によるWコピーとDコピーがDLQに併存し得るため、exact-one物理コピーを仮定しない。元ordinary W proof/D metadataを不変で保全し、353 §7.2の同W論理隔離・個別承認整理を適用する。Broker生成コピーの欠落propertyをDから書換え/補完しない。停止時SENT未確認は非成功rollback。max4、no-XA、D!=W、body/header/correlation W保持、application ACK前SENTは不変更。

SSC154155（PG/PT、2026-10-01、実装前）：QSB受付は元Inbox source M0へQUESTION-bound暗号snapshotを受付transaction内で保存し、commit後に専用dispatcherをwake、対象QWK WのSENTを短DB観測する。request threadはJMS送信せず待機中connection/row lockを保持しない。SS312の総2秒単調budget超過はfresh9000としCOMPLETEDを書換えない。元proofが揃ったsame-token再送だけ0200。Inbox正常保持後のretained owner/token questionは重複防止だけであり、同canonical本文でも認証済snapshot/SENT根拠を失った場合は9000、異payload0105、新acceptance/alias/推測歴史時刻を生成しない。

通常Outboxのrow message_id＝body header＝NKMessageID＝_AMQ_DUPL_IDは維持。業務最終QWK DLQのみrow dispatch D／duplicate ID Dと、body/header/NKMessageID元Wを分ける。元correlation/320byte bodyとSS331不変metadata5列を保持、partial UKで元WにつきDLQ dispatchを一つにする。JMS senderはdestination-specific profileを再検証し、その他row/header不一致を拒否する。DB ERROR＋DのPENDING確定後DのSENTまで元ACKをしない。再配送は同Dを確認し、send後mark前crashもDで重複排除する。元work SENTの受付証明を変更しない。

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

### 5.1 非更新Message参照（SSC-024）

`JdbcInboxCoordinator.inspectMessage(connection, request)`は、callerが認証/ownerを確定した後、明示read-only transaction内でMessage IDだけを1 SELECTする。FOR UPDATE、INSERT、operation token検索、handler実行、保持期限更新、commit/rollback/connection closeを行わない。autoCommitまたはreadOnly=falseをTRANSACTION_REQUIREDで拒否する。

不在はOptional.empty、存在時は通常executeと共通のrow reader・layout/version/correlation/owner/token/HMAC照合を行い、一致した保存COMPLETED/ERRORだけREPLAY、PROCESSINGはIN_PROGRESSを返す。NULL/不正state/unknown key/照合不一致を成功へ補完しない。これはMessage参照snapshotであって新規受付の予約/lockではない。別Messageの同operation tokenを検索して確定扱いせず、最終write transactionでは通常executeの一意制約/再照合を必須とする。Scenarioはこの参照結果を復号・整合検証してから既存descriptorの再利用を判断し、file I/Oへread-only transactionを持ち出さない。

## 6. Response保存・再構成

### 保存元Message binding（SSC-033）

`JdbcInboxCoordinator.executeBound`は既存executeと同じ認証後・caller write transaction内のMessage/token検索、HMAC照合、一意制約競合再読、handler実行を用い、`BoundInboxExecution(sourceMessageId, execution)`を返す。新規EXECUTEDのsourceは受付Message ID、既存REPLAY/IN_PROGRESSのsourceは検証した取得rowのmessage_id。sourceを新request IDやtokenから推測しない。SELECTへ既存PK列を追加するだけでDDL/外部wire/retention変更はない。

Message検索はrowのmessage_id自体も要求IDに一致必須。Token検索は既定owner/token/HMAC確認を維持し、同tokenの別Messageへ新Inbox rowやaliasを作らない。source必須NULL/不一致は基盤/整合不成立でcaller rollbackし、元の保存snapshotを別要求へ付け替えない。旧`execute`は新内部algorithmのexecutionを返す互換API、`inspectMessage`は従来どおりMessage-only/read-onlyの戻り値を維持する。追加lookup・DB connection・commit/rollback/close所有は増やさない。

暗号replay側はsourceMessageIdをResponseSnapshotIdentityのAADへ使用し、保存header correlationもsourceに一致を確認する。利用者へ送る新headerのcorrelationは現在request Message IDとし、owner/layout/target/payload同一性、最新認証、保存body/ref/versionの検証を省略しない。Bound値それ自体を認証許可や暗号完全性の証明にしない。PT-IDEM-B01～B04で初回/同Message/別Message同token、競合INSERT再読、PROCESSING、NULL/誤PK/SQL fault、実AADでの復号、100並行と既存全API互換を検証する。

| 処理 | 保存方式 | Replay |
|---|---|---|
| Login成功 | `result_ref=AUTH_SESSION`＋`result_ref_uuid=auth_sessions.id`＋初回fixed responseの暗号化snapshot（331 §7.1） | session ciphertextとsnapshotを検査し同context/初回expiry・role/usernameを返す（SSC-013） |
| Login失敗/lock | 暗号化response snapshot | 同result/retry情報を返す |
| 参照/list/detail | 暗号化・圧縮済みfixed response body | Header Message/Correlation/sentAtを新response用に再構築しpayloadをdecode/encode |
| User更新 | `result_ref=USER`＋version/result | 現在値が進んでいても当該操作の保存versionを0200で返す |
| Question受付 | `result_ref=QUESTION` | receipt/question/submittedを業務rowから0200で返す。Outbox SENTも再確認 |
| Cancel/delete | `result_ref=JOB/QUESTION`＋確定日時 | 同じstate/deleted_atを0200 |
| Scenario file mode | `result_ref=SCENARIO_FILE`＋`result_ref_id=script_files.id`＋descriptor | `.ready`存在時は同descriptor。朝削除後は同じmaster file snapshotから新fileを再生成 |

SnapshotはZstandard等の新規native依存を避け、JDK `Deflater` level 3で圧縮後、`api-inbox-response-aes` AES-256-GCM keyで暗号化する。AADはMessage ID、
response layout/version、owner ID。最大平文1,000,000 byte、最大暗号文1,050,000 byteをCHECK/guardする。圧縮bombを避けdecode時に期待平文上限を設定する。

Replay responseは新しいresponse Message IDとsentAtを持ち、Correlation IDは再送requestのMessage IDへ合わせる。保存済み成功だけresult codeを`0200`とし、確定業務errorは元のerror result/retry/messageを維持する（SSC-013、UI232 §7の0200は成功profile）。
保存済みbodyをbyte単位でそのまま返して古いheader/correlationを混入させない。

SSC-052/PG-D-140: 新たに実装するQSB/NTC/QDLの成功snapshotは352 §11.2.1のNKREF1内部prefixで参照type/id/operation tokenとwireを同じ暗号認証へ束ねる。DB列ref/tokenを改変して別targetへ付替えた場合、同じ取消/削除日時でも復号後prefix照合で拒否する。既存NKENC1外側/認証/query/User更新/error profileは不変。業務rowからの再構成や同日時の一致だけを認証bindingの代替にしない。参照・UK・Outbox状態等の業務検証は引続き必要で、このcodecだけでは更新3routeの保守削除を許可しない。

### 6.1 Login replayの凍結・整合検証（SSC-013）


成功も失敗も初回688byte LGNRSP01/001を上記snapshotへ保存する。成功はAUTH_SESSION参照を併記、失敗はNONE。成功の発行時username/role/発行日時/初回8h期限はsnapshotを正とし、現在のuser情報やidle延長後のexpires_atから推測しない。Header/全DATA byte/成功semantic、保存Message相関・layout/version・Inbox state/result/refの組合せを検証する。成功snapshotはauth_sessionsの参照UUID/created_message_id、AADのuser/session、復号context/hash、immutable issued_atと初回8h期限に一致必須。不在・不整合・unknown key・復号不能は9000/運用errorとし保存結果を成功推測しない。

再送は元結果の提示だけであり、新session発行、idle延長、失効解除、password再照合、counter/audit再更新を行わない。後で失効・期限切れ・権限変更されていても元結果を変更せず、通常の認証context検証は現在DB状態を正として拒否/認可する。Web sessionや現在権限をsnapshotだけから認証済みとみなしてはならない。初回0000/確定0101/0106の保存、成功0200・失敗元codeでの新Header再構築を独立byte oracleで検証する。

SSC-043: Webの0200受信後の現在認証確認は314 §3.1を正とする。新Message IDの既存IF-003を通常API認証へ通し、成功応答を全検証してから元Login snapshotをWebの早期principalへ投影する。Login再送・session新規発行・元snapshotの書換えではない。0102/一時障害/不正応答時はWeb認証を付与せず、probe後の各業務API認証も維持する。

### 6.2 Logout Inbox（SSC-015）

LOGREQ01はprotocol検証後、raw hashに一致するsessionのUserを先にlockし、Inbox owner用user IDだけを取得する。未失効/既失効/期限切れ/account状態から業務actorを発行せず、このlookupでidle延長/監査/失効更新を行わない。不明contextは0102でInboxを新規保存しない。Known contextはowner付きInboxを開始し、NEWのhandlerだけ312 §4.2の失効専用serviceを呼ぶ。これにより同Message ID再配送の監査重複を防ぐ。別Messageの既失効要求は元revoked_at/0200と当該要求の監査を確定する。

HMACは§3の全Request規約どおりowner decimal、LOGREQ01/001、target `REQUEST:LOGREQ01`、DATA field 0件、tokenなし。header contextはHMACへ混入しない。同一ownerの同Message再送は元操作結果を提示し、別contextを追加失効しない。owner不一致/同ID異metadataは既定の恒久整合error。保持は更新requestとして完了+7日。

初回0000/0200はCOMPLETED、AUTH_SESSION参照UUIDと280byte LOGRSP01暗号化snapshotを既存列へ併記する。既知ownerの0102はERROR/NONE＋snapshot。AADはrequest Message ID/layout/version/owner。Replayはheader/280byte/全DATA semantic/相関・state/refの組合せを検証する。成功では保存header contextのhash、session UUID/owner、revoked=true、元revoked_at（wireはmillis）を参照へ照合し、不在/不整合/鍵不明/復号不能は9000の一時基盤型とする。失敗は0102だけを保持し、後の状態で成功へ置換しない。新response headerのMessage ID/sentAt、再送request Message IDへのcorrelation、当該requestのcontextを設定し、成功だけ0200へ統一する。新たな失効、idle延長、権限付与はしない。

### 6.3 Scenario保存結果の検証（SSC-026）

GAM/SPK/RTE/SCF/SRC/SCN responseは初回fixed header+DATA+recordsを§6の既存AES snapshotへ保存する。AADは要求Message ID/対応response layout/001/認証owner。初回成功0000はCOMPLETED、確定9001（容量上限）とSCNの0104（対象不在）はERROR。0102/9000は非保存の応答とし、失効/一時障害を成功snapshotへ変換しない。正常responseは要求と対応するlayout必須。

SCN成功の現在Script file IDは要求IDに一致する。FはSCENARIO_FILE数値参照＝そのScript file ID、Iおよび他query/ERRORはNONE。Record数/順序・I/F排他・descriptor各fieldは既存codec/typed semanticで再検証する。暗号化body内のcapture headerは完了stage時刻のmillis、DB completed_atは同stageのmicrosとして保存し、読取時に同一millisを確認する。利用者へ返すheaderは別の送信stage時刻へ再構築する。

読取はsnapshot/AAD/key/復号に加え、全header、actual total length、要求Message相関、対応layout/version、全DATA/record semantic、初回codeとInbox state/ref、完了時刻、SCN要求IDと参照を確認する。不在/不整合/未定義値は一時基盤型9000でdeny closed、平文/原因/suppressed情報は返さない。未検証snapshotからquery結果や認証actorを作らない。

再構築は再検証済みactorのownerと現在要求のsnapshot identityが一致必須。保存payloadは変えず、response Message ID/sentAt/current request contextを新しいheaderへ設定し、Correlation IDはrequest Message IDとする。成功のreplayだけ0200、ERRORは元0104/9001。旧header contextを認証に使わない。復号buffer/一時DATA/recordsは使い終わりに消去する。

この部品はDB/file/JMS I/Oを所有しない。Fの物理存在/属性/hash確認、朝削除後の元master snapshot照合・再生成・Inbox descriptor置換、最終write transaction/再送/送信は別gate。復号済みdescriptorだけで物理file確認を完了扱いしない。

## 7. Inbox transaction/crash

| Crash | 状態 | Recovery |
|---|---|---|
| Inbox INSERT前/transaction中 | Row/業務ともrollback | 同Message IDを新規処理 |
| 業務＋Inbox commit後/reply前 | COMPLETED/ERROR | 再配送でreplay |
| Reply send後/JMS commit前 | DB確定、reply取消 | Request再配送、replay＋再send |
| JMS commit後/Web timeout | DB/reply/ACK確定 | 新Message ID＋同tokenで0200 |

DB transactionとJMSをXAで結合しない。Inbox replayによりDB先commitを安全にする。

### 7.1 Scenario段階処理と同Message排他（SSC-027）

単一API process・単一service instanceを起動契約とする。同Messageのsnapshot取得～file生成/検証～最終DB確定は同一private lockで直列化する。UUID hash下位8bitを使う固定256本のfair ReentrantLockを所有し、動的なMessage履歴/cache/認証情報を保持しない。異なるMessageのhash衝突は処理を直列化するだけで結果を共有しない。待機中はDB connection/transactionを取得せず、業務timeoutを追加しない。Interruptは状態を復元して一時基盤型へ返し、未取得lockをunlockしない。Callback失敗/nullでも取得lockを必ず解放する。外部から取得できるthis/class monitorに依存しない。

このlockはDB冪等性の代替でも複数JVM分散lockでもない。受付開始前のsingle-instance/full root gateが未完了の間は内部部品として扱い、本番dispatcherへ登録しない。新たなPG session advisory lease/追加DB connectionは導入せず、既存pool上限8とREAD COMMITTEDを維持する。

1. Read-only transactionで現在contextを非更新検査し、owner付きcanonical/HMACでMessage Inboxを参照。既存結果は§6.3で復号/整合検査し、新規だけquery snapshotを取得する。全query結果をimmutableへ切り離し、commitとconnection closeを確認してから次段階へ進む。
2. DB外で必要なfileを生成/検証。既存Fは物理完全性確認が成功した時だけ同descriptorを再利用。MISSINGだけ再生成候補とし、属性/hash/リンク/不明I/Oは再生成で隠さず失敗とする。再生成用DB snapshotもread-onlyで取得・終了後に使い、元metadataとrecord count/hashが一致することを生成前に確認する。既存結果が失われた場合は別結果へ補完しない。
3. 最終write transactionで新しい時刻の通常verify（User→session lock/idle touch）を行い、事前ownerとの一致を確認してから通常Inbox executeへ接続。DBのUK/identity/HMACと保存結果を再検査する。初回COMPLETED/ERRORの保存を確定し、file I/O/JMSをこのtransactionへ持ち込まない。
4. 朝削除後のF再生成では、最終認証と元Inboxのrow lock/identity/旧snapshot一致を確認してdescriptorを含む暗号snapshotだけ置換する。Message/owner/canonical/state/result reference/初回completed_at/expires_atは不変。競合・不一致はrollbackし、新readyを勝手に削除しない。物理内容が不一致のfileを置換で正当化しない。
5. 最終commitとconnection close成功後に新headerで応答を再構築し、JMS所有者へ返す。認証失効は非保存0102、確定0104/9001は保存ERROR、一時障害は固定一時型とする。Rollback/commit/close/clock/UUID/鍵の不確定を成功にせず、原因・suppressed・bodyを外へ返さない。保存済み成功だけ再送0200。失敗後のreadyは次回朝清掃まで保全する。

独立PTはMessage衝突/100再送/interrupt/lock寿命、段階時刻、DB connection・row lock非保持中のfile I/O、owner/role/失効再確認、Inbox24h保持、元結果再生成とdescriptor置換、JDBC/鍵/file/JMS故障後条件を区別する。最終serviceの未接続箇所は合格へ算入しない。

SSC-027のDB置換境界: `JdbcInboxCoordinator.replaceScenarioSnapshot`はcaller-owned writable transactionを要求し、SCNREQ01/001→SCNRSP01/001、COMPLETED/SCENARIO_FILEに限定する。`FOR UPDATE`後の共通identity/HMAC検査に加え、expected/current/replacementのstate/ref/layout/version/completed_at、expected/currentのkey versionと暗号byte全体を照合する。更新は`response_body_encrypted`と`response_key_version`だけで、件数は厳密1。Bind用一時byteは成功/例外とも消去し、callerのcommit/rollback/closeを代行しない。復号/物理fileの検証と認証は段階service責務であり、このDB部品だけで保証したとはしない。PT-IDEM-SR01～SR03の独立SQL/JCE-HMAC・競合・故障後条件へ追跡する。

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
- APIは351 §3.3のREQUEST正規化と、QA-054の限定ACTION/MENU_VIEWED・共通Details/表示metadata規則を適用し、DB INSERT/duplicate transaction確定後だけlistenerへ正常復帰する（SSC-008/336）。MENU_VIEWEDも同じevent Message IDを再配送し、source UK重複時は既存行不変/追加0とする。LOG_SEARCHEDはWeb電文から受け付けない。
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

`answers.question_id` UK、`async_jobs.message_id` UKが二重回答を防ぐ。再配送countを`retry_count=min(JMSXDeliveryCount-1,3)`へbounded更新する。実delivery metadataは非cap（SSC156）。

## 11. Operation token lifecycle

- Webはform GETでtokenを発行し、session全用途でpending＋consumed合計最大10件、用途/UUID/発行日時/任意の初回完成時刻を暗号保持する（QA049、SS314）。
- Token有効期間は8時間idle session内。検証済0000/0200の初回時刻をconsumed markとして保持し、同結果GET refreshでは再送しない。保持中の同token/同入力POSTは現在API認証と既存HMAC/保存済み結果を検証してreplayする。
- Timeout/503だけ同tokenをformへ戻す。Validation errorでAPI未送信の場合は同tokenを維持する。
- 409 payload不一致/optimistic conflictでは旧formで自動再操作せず、明示最新GETへ誘導する。容量による退役は新formの枠が必要な場合だけ最古consumed1件、pendingは捨てない。全pending10件は新form拒否。退役/不在token POSTは409、API送信/新UUID/自動再操作0。
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

### 12.1 削除前検査の責務分割（SSC-049/QA-046）

UIC-006の検査processは、(1) 暗号snapshot・固定長構造、(2) DB owner/result/業務UK参照、(3) 固定run/backup/期限/lockと削除の原子性、を全て満たした行だけ削除対象とする。いずれか未検証なら保持する。通常replayの認証/idle延長や応答送信は起動しない。

第一部品 `InboxResponseInspector.isStructurallyValid(identity, completion)` は副作用を持たず、NKENC1復号、AAD、identity/layout/version、header相関、実byte長、保存completed_atとwire時刻のmillisecond一致、response kind、resultとCOMPLETED/ERRORの対応、全DATA/record/semanticを検証する。結果はbooleanだけで、平文・context・DTOを返さない。不存在snapshot、不正暗号/鍵/metadata/byte/semanticはfalse。呼出しnullは契約違反として拒否しNPEを正常扱いしない。復号/分割bufferはfinally消去する。

このtrueはDB参照の実在・整合、期限到達、削除許可を意味しない。後続のDB参照検査/競合保護/保守function/起動が完了するまでBUG-014は未完了。対応Test IDはPT-DB-INBOX-001～008、PG-D-119。

### 12.2 認証結果参照の削除前照合（SSC-049/QA-046）

`AuthenticationInboxInspector.isConsistent(connection, identity, completion)` は12.1の全構造検査を必須前段とし、LGNRSP01/LOGRSP01だけを扱う。Loginは匿名AAD、Logoutはowner付きAADを必須とし、他layoutやowner形態不一致をfalseとする。callerの明示transaction（autocommit=false）を要求し、commit/rollback/close/row lockを代行しない。

Loginは6.1の`LoginReplayService.restore`、Logoutは6.2の`LogoutReplayService.restore`の既存read-only整合検証を共用する。Logoutの保存header contextは元sessionとのhash照合のためだけに使い、通常認証を呼び出さない。復元wireは外へ返さず即時消去する。SQL/暗号/参照不備はfalse、呼出しnullは契約違反。Login後のusername/role/status/idle期限変更は過去の成功を改ざんとみなさず、session不在・immutable参照/context不整合は保持する。Logoutはowner/UUID/hash/失効状態/失効時刻を照合する。

この部品は鍵/参照検査だけであり、後続の限定DB functionが同transactionでInbox・参照をlockするまで削除許可にはしない。正常/破損、owner/Message、DB欠落/故障、null、並行、鍵世代、DB非更新はPT-DB-INBOX-009～016へ追跡する。非認証layoutの検査と削除function/oneshotは別の未完了gateである。

### 12.3 検査から削除までの所有境界（SSC-049/QA-046、PG-D-122）

非公開の認証Inbox保守serviceは専用roleのfresh connectionと明示transactionを一操作内で所有する。固定run/cutoff、UUID昇順cursorから1候補を取得・lockし、canonical route/version/owner/token、期限、既知fingerprint key version、12.1/12.2の構造と参照を検査してから331 §3.5の条件付き削除を呼ぶ。SAVEPOINT、connectionの外部公開、remote I/O、外部callback、検査と削除の間のcommit/rollbackは禁止。snapshot/context鍵はprocess寿命中不変とし、終了までclose/rotationを競合させない。

元requestのpassword/canonical平文は保存しないため過去のHMAC再計算は行わない。保存HMACの形式と既知versionを検査し、snapshot AAD/headerと業務参照の整合を証明範囲とする。HMAC秘密keyを検査主体へ配布せず、読取り可能versionの非秘密allowlistだけを使用する。未知versionは保持する。

不整合は保護して次のcursorへ進めるが、SQL/commit/close故障は固定の非秘密運用失敗とし正常終了にしない。commit成否不明時は既削除の可能性を記録し、同じrun/cutoffで冪等再走する。rollbackで不明commitを取り消せたとは扱わない。正常削除の成功結果はcommit・resource終了後だけ返す。外へ出す診断は固定理由と件数のみ。参照sessionが既にcleanup済みなら保持するという現行保護条件と朝batch順序を変更しない。

12.2の統合falseは原因を暗号破損と断定せず「検証未成立の保護WARNING」とする（内部replayは復号/参照/読取り失敗を同じfalseに集約する）。削除serviceで観測したSQL例外は失敗とし、検査後も明示queryでtransaction healthを確認する。aborted transactionへのCOMMITがROLLBACKへ変わっただけで正常結果を返さない。実装/試験はPGPT004の011仕様PT033～040に対応する。

### 12.4 検索・Scenario・media・User保存結果の参照検査（SSC-049、PG-D-123）

`NonAuthenticationInboxInspector`はowner付きのGAM/SPK/RTE/SCF/SRC/SCN、AUD/ANM/ANL/VID/MCT/MCS/MTR/MED、USR/UDT/LGS、UCR/UST/URL/UPW/ULKのRSP01計22 layoutを扱う。12.1構造検査と明示transactionを前提にbooleanだけを返し、通常認証、role再判定、更新、file生成、送信、transaction終了を行わない。Question/通知7応答は初期22種の対象外であり、照会4種の追加は12.8に従う。更新3種は未検証のまま保護する。

保存可能codeは既存の6章replay契約と同一。0000は全22、0200はULKだけ。9001はUDT以外、0104はUDT/SCN/AUD/VID/MED/UST/URL/UPW/ULK、0105はUser更新5種、0100はUCR/UPWだけ。その他のcodeは正常な固定長形式でも保持する。errorはNONE参照を必須とする。

通常のquery成功はNONE参照であり、保存後に変化した検索結果・名前・role・statusを過去snapshotと再比較しない。User更新成功はUSER参照と保存DATAのUser ID一致、実在するapp_users.id、現在versionが保存version以上を検証する（N9範囲、巻戻し/再採番なし）。UCR保存versionは0、他の0000は1以上、ULK0200は0も許可する。元password/request不保存のため旧更新内容の再計算や現在ADMIN権限を歴史的成功の証明条件へ追加しない。

SCNのIはNONE、FはSCENARIO_FILE参照と保存Script file ID一致を必須とする。FはUI237/SS333のUUID・日付path・4800×record数・hash形式のdescriptorを検証し、script_files.id/game_idと保存Game code（NUKITASHI1=1、NUKITASHI2=2）を照合する。期限切れ生成.ready fileは正当に削除され得るため、本DB transaction内でfile IO/再生成を行わず実体存在を必須にしない。生成4800-byte record fileのhashとraw masterのscript_files.sha256は異なる対象であり比較しない。現在master内容全体の同一性を証明したとは扱わない。

DBはUserのid/version、Scenarioのid/game_idだけを読む。NULL/欠落/多重row/不一致/SQL故障は未検証としてfalse、呼出しnullは契約違反。復号・分割bufferをfinally消去する。専用roleへの最小列grant、参照lock、期限/backup/条件付き削除接続は後続append-only SQLとserviceのgateであり、このtrueだけで削除してはならない。PT-DB-INBOX-041～048。

### 12.5 全候補の検査・削除の共通所有service（SSC-049、PG-D-125）

既存の認証限定AuthenticationInboxCleanupを`InboxCleanup`へ改称し、transaction/resource/health/commit/固定非秘密例外処理を複製せず共用する。constructorはfresh connection provider、AuthenticationInboxInspector、NonAuthenticationInboxInspector、既知fingerprint version集合を受け、鍵は全呼出し終了まで不変・生存とする。外部callback/connection/SAVEPOINT/途中commitは禁止のまま。参照検査だけのpublic APIから削除を呼べるようにはしない。

V010の全完了期限済候補を取得し、24 canonical REQ/RSP対応、version001、owner（Loginのみなし）、User更新5種token必須/他はなし、fingerprint形式/既知versionを検査する。未知/未実装route、metadata不整合、snapshot欠落/暗号・参照不整合はPROTECTEDを返し、そのUUIDの次へ進める。auth2応答は12.2、他22は12.4を呼び、trueの同transactionだけV010限定削除を呼ぶ。false/SQL条件不一致を削除成功にしない。最短保持はV010の24h/168h条件を満たすこと。

NULL必須DB列/SQL/health/commit/close故障は12.3どおり非秘密の運用失敗。同run/cutoffで再走し、commit成否不明を無理に成功/未実施と断定しない。返却はcommit/resource終了後のDELETED/PROTECTED/ENDとcursorだけ。owner/token/context/cipher/DTO/SQL値を診断へ出さない。警告件数・全run持続状態・oneshot/朝batch接続は別の後続gate。

旧認証PT033～040は同serviceの回帰として維持する。新PT057～064で全22 query/User route、SCN I/Fと参照lock、24h/168h、未知を含む混在cursor、非認証のSQL/commit故障・100並行を検証する。既存の「非認証layoutへの変造は候補外END」という期待だけを、3.6承認の全候補走査に合わせPROTECTED/保持へ更新する。PROCESSING/未期限は引き続きEND。この内部走査契約変更はRD/UIの外部動作変更ではない。

### 12.6 永続progressとの原子的接続（SSC-049、PG-D-128）

InboxCleanupへinspectStoredNext(run)とrunChunk(run,maxSteps)を追加する。既存inspectNextの単一候補PTは維持し、process用入口は必ず永続経路とする。privateなtransaction共通methodだけがfresh connectionを開き、class内部から渡す処理だけを実行する。外部callback/connection公開は追加せず、従来のhealth/commit/rollback/close/固定cause-free例外の処理を複製しない。

inspectStoredNextはV012 openでprogress行をlockし、同じSELECTのtop-level transaction IDを内部保持する。返却run/cutoff、必須列/型/件数、cursorと非負の累積countの不変条件を再検査する。completed_atありなら保存済み結果だけを返す。未完了なら保存cursorで12.5の候補検査・条件付き削除を行い、その結果をV012 recordへ同じtransactionで保存する。健康確認・commit・close成功後だけ戻り値を返す。不明commit/close障害は例外とし、次回同runでDBを再読取りするまで件数を推測しない。

InspectionProgressはInspectionRun、Optional UUID cursor、inspected/deleted/protectedのlong累積値、complete booleanの不変recordとする。NULLは禁止、count>=0、deleted<=inspected、protected=inspected-deleted、inspected=0とcursorなしを同値とする。加算でoverflowする検査式を使わない。内部projectionだけにID/cutoffを持たせ、toString/運用診断ではID/cursor/cutoffをredactして件数・完了flagだけを出す。completed_atの有無はDB制約に従いcompleteへ射影し、任意SQL列/DTOを外へ出さない。

runChunkはmaxSteps=1～1000だけを受け、先頭からinspectStoredNextを最大指定回数実行する。各stepは独立の所有transactionで、返却complete=trueで早期終了する。上限到達で未完了ならcomplete=falseを返し、工程成功にしない。無限loop/自動SQL retry/新run採番/時計でcutoffを進める処理はしない。全processの30分制限・親のOS lock/通常API停止・backup実file gate・鍵寿命は341/343の起動実装で保証し、この部品だけで完了扱いしない。

PT081～088で混在正常/保護/未対応cursor、1/1000上限・途中再開・既完了、独立wire/JCE＋実DDL、全null/矛盾DB結果/SQL・resource故障、deleteとcheckpointの間のfailure/不明commit/再読、100並行の一意累積、旧認証/非認証の回帰と全line/method/class/branch100%を検証する。

### 12.7 時間制限付き全件走査（SSC-049、PG-D-130）

InspectionRunExecutorは既存InboxCleanupを所有processの鍵寿命内で使用し、固定run/cutoffでrunChunk(run,1000)をENDまで呼ぶ。時計は壁時計でなくSystem.nanoTime相当の単調経過時間を使用し、開始から30分未満だけ進行を許可する。各chunkの前後で時間とthread interruptを確認し、境界30分一致/超過・時計後退・interruptで新しいchunkを開始しない。long nanoTimeの自然wrapは差分計算で許容し、壁時計変動でcutoffを変えない。

InspectionExecutionのstatusはSUCCESS/WARNING/TIME_LIMIT/INTERRUPTED/STORAGE_FAILURE。SUCCESSはENDかつ保護0、WARNINGはENDかつ保護ありだけ（exit相当0/10）。他はexit相当50であり、不明commitや時間内に終わらなかった検査を成功にしない。Optional lastConfirmedに最後にcommit/closeまで成功したprogressだけを保持する。失敗時の値は最後の確認点であり最新DB件数/未削除証明ではない。未取得を0件へ変換しない。失敗が起きたchunkの途中commit件数は次の同run再読で確認する。

SSC-453：終了コード相当値は各Status列挙子が生成時に保持する必須intとする。SUCCESS=0、WARNING=10、TIME_LIMIT/INTERRUPTED/STORAGE_FAILURE=50。InspectionExecution.exitCodeは保持値を返す。名称、宣言順、public署名、正常／警告とprogressの整合性検査、後段ゲートを維持する。列挙子を追加する際は終了コードと独立期待値を同時に定義する。

InboxMaintenanceExceptionはSTORAGE_FAILUREへ射影し、自動SQL retryしない。予期しないprogramming例外・NPEは正常扱いせず起動境界まで伝播する。interrupt flagは消去しない。SUCCESS/WARNINGが得られてもその後のcredential/DB/provider resource close・親の全gateが成功するまで実process exit0/10へ確定しない。OS lock/backup実体/通常API停止/鍵file/本番main・systemd unitは別の未完了gateであり、run executor単体で省略できない。

PT097～104は実DB/既存独立wire fixtureと注入単調clock・thread interruptで、空/既完了・保護あり・1,000件越え・時間前/一致/超過/自然wrap・DB故障/最後の確認点・同run再開・例外/redaction/record null契約・全Java4種100%を確認する。時間待ちsleep、reflection、productionからexpected生成は禁止。

### 12.8 質問・通知の照会snapshot検査（SSC-049、PG-D-139）

12.4の初期22種へNTSRSP01/NTDRSP01/QSSRSP01/QSDRSP01の4照会を追加し、非認証26種・認証を含む28 canonical routeとする。UI236のpage50/最大50件、NTS record624/QSS record672、NTD data8896/QSD data8352、全field・状態・日時・削除済み条件を12.1の固定長/typed semanticで検証する。owner付きAAD・version001、明示transaction、NONE参照を必須とし、構造が正しくても型付き参照付きは保護する。

保存許可codeはNTS/QSSが0000/9001、NTD/QSDが0000/0104だけ。0200は再送時に構築するheaderであり初回照会snapshotの保存許可にはしない。0100/0102/0103/0105/0107/9000等の未確定・未対応codeは保護。errorはUI232/323の数値zero・文字space・record0 profileを必須とする。

6章の参照/list/detailの凍結snapshot契約に従い、現在のquestions/notifications/answersの有無や本文、現在のowner role/statusを過去の照会結果へ再比較しない。ADMIN照会の他利用者Questionを現在ownerと同一に強制しない。通常認証・再送・body再生成・DB参照権限の追加なし。保存wire自体のowner AAD/相関・schema意味検査は省略しない。

V015の4 canonical REQ01/RSP01 routeを既存owned InboxCleanupへ追加し、tokenなし・ownerあり・最短24時間・strict expires<cutoff・同transaction ID/hash・固定backup/lockという12.3/12.5の保護を維持する。QSB/NTC/QDL更新3応答は本追加の対象外でPROTECTED、業務UK/result ref照合完了まで削除許可しない。

004の041/042・PT-DB-INBOX-161～168で独立byte offset golden/JCE、4route×保存code、page0/1/50、状態/本文/null/未知/誤owner/誤ref、24h±1μs、backup/lock、rollback/commit不明の再開、100並行、V001～014不変と全既存route回帰を確認する。照会検査の成功を質問業務実装・本番oneshot・工程全体完了には算入しない。

### 12.9 質問更新3応答の参照検査（SSC-049/052、PG-D-141）

変更前登録9535086f。`QuestionMutationInboxInspector`はcaller所有の明示transactionでQSB/NTC/QDLだけを検査する。owner/token必須、identityとcompletionのlayout/version001/snapshotが一致し、成功は352 §11.2.1のNKREF1を期待ref/tokenで検証してから既存全wire検査へ渡す。既存構造検査のprivate algorithmを同package内部で共用し、復号済みwireや検証済flagをpublicへ公開しない。ERRORは従来のraw fixed responseのNKENC1、NONE参照だけとする。

| response | 保存可能な成功 | 保存可能な確定ERROR | 成功参照の条件 |
|---|---|---|---|
| QSBRSP01 | 0000/0200 | 0100/9001 | QUESTION。wire Question ID/refが一致、questions.owner/token/receipt/submitted_atを照合。async_jobs.question_id/owner/message_id/correlation_id/received_atが元受付に一致。QWK相関/SENTは後述 |
| NTCRSP01 | 0000/0200 | 0104/0107/9001 | JOB。async_jobs.ownerがsnapshot owner、state=CANCELLED、version1以上、cancelled_at/state_changed_at一致、wire取消日時がDBのmillisと一致。現在Notificationが残っていればjob/question/owner/CANCELLED/確定日時一致。正常な朝削除後のNotification不存在は許容 |
| QDLRSP01 | 0000/0200 | 0104/9001 | QUESTION。is_deleted=true、version1以上、deleted_at/by必須、wire日時がDBのmillisと一致。0000はdeleted_by=保存owner、0200は既存削除者を維持（当時ADMINが他owner分を操作可能）。Answerがあればdelete tripleをquestionと完全一致、なければ許容 |

時刻は有限・wire表現範囲、業務確定時刻はInbox completed_at以前。DB同士の同時刻契約はmicrosecond一致、wire比較だけmillisへ切詰める。受付後の質問論理削除やjob状態遷移、actorのrole/status変更は過去結果の不整合としない。Question/Jobそのものが不存在なら保護し、親の既存cleanup順を変更したり推測復元して削除しない。

QSBはUI232 §8の新Message IDを持つQWKだけを元受付requestへのCorrelationで照合する。331 §3.11の限定projectionで、宛先nk.async.work・QWKREQ01/001・320byte・SENT・sent_atあり・leaseなしを確認。HeaderのEVENT/INTERNAL・全space context・Message/Correlation・長さ、DATAのreceipt/question/jobをcodecとDB参照で検証する。受付ごとQWK一件のpartial UKを使い、同相関の重複・別layout・不正body・PENDING/ERROR・欠落を成功推測しない。QWK/SENT確認は同transaction、send/dispatcher起床は保守processの責務外。先行Outboxの正当な物理削除で証明できない行もPROTECTEDのまま警告する。

NTC 0107は個別error profile（競合時PROCESSING/COMPLETED/ERROR、取消日時space）を検査し、現在job状態へ上書きしない。0102/0103/異token0105/9000を保存済み業務結果として認めない。SQL/暗号/型/参照不備はfalse、caller nullは契約違反。borrowed connection/codec/keysは閉じず、SQL commit/rollback/DB更新/外部IOなし。参照lockと検査→削除は既存owned InboxCleanup/V016の同transactionで保持する。保存/replayの通常業務service・worker・公開認証は別途実装/PT必須。

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

## QA-054 API LOG_SEARCHEDと結果再送（SSC-336）

初回成功ログ検索の結果snapshot取得後、LOG_SEARCHED/ACTION保存とInbox・再送結果の成功確定を同じ業務transactionに含める。既存の原子性・排他・結果保持契約を維持し、監査失敗ではrollbackする。保存済み応答の再送/同一要求の競合では成功確定を一度だけ行い、LOG_SEARCHEDを増やさない。INBOX_REPLAYED等の必要MQ記録は独立期待値とし、成功ACTIONの代替にしない。検索snapshotとcommit後の監査DB後条件を別々に検証する。再送間隔/保持期限/operation token契約の変更はない。

## SSC-431 Login現在context probeのfatal保全（2026-11-16）

MqLoginContextProbe.isActiveの既七catch(JMSException/JMSRuntimeException/JmsRequestReplyException/PermanentProtocolException/IllegalArgumentException/IllegalStateException/DateTimeException)は固定UNAVAILABLEへ変換する前に既JmsRequestReplyException.preserveFatal(failure)を呼び、cause/suppressed/SQLnext/JMSlinkedの元Error identityを有限に保存する。header/IF003現在context再確認/UUID freshness/256byte request/全reply検査/0102 false/他非success固定例外/timeout1ns..2s/12wait/再Login禁止/所有request-sendercopy-reply-data-records全消去/正常認証ロール/公開API/秘密非保持を変えない。Provider本体は変更しない。catch唯一のfinal MqLoginExchangeExceptionはsuper(message,null,false,true)によりcause/suppressedを保持できず今回のmissing-guard条件に非該当、固定reason INVALID_INPUT/UNAVAILABLEと例外秘匿を独立回帰契約にする。新PROBEGRAPH001は各七catch族の公開合成Error graph（JMSlinked→SQLcause含む）を既memory senderから与え元Error/256ownedcopy全zero/pending0と同one-slot clientで別freshID正常復帰を検証する。新LOGINFAILVALUE001は二reasonの固定message/nullcause/disabledsuppression/initCause拒否/null constructor/enum閉集合lookup/values防御を独立literalで確認する。元MqLoginClientTest8/ProbeTest3/ProviderTest5の全16本文・独立wire・100並行/get10/stop-await5及び既固有例外/消去期待は保持、compile依存するfixture helperは抽出せず元whole class全実行する。新2＋旧16全18を一source/run、既明示safeWeb18sourceと現在Protocol176だけfreshRootNullAway/static/物理CRC-init/XML/default/raw対象Probe/Provider/ExchangeException全sourceで照合する。旧162/166/Protocol130は確認再演0、実JMS broker/socket/DB/auth session/鍵/Root2Actual4/VM/native/aru/HOLDや旧全WebAPIjar読取抽出を行わない。

BUG3065/YKT2556、状態:設計確定・main反映前、PG/PT/正式未完。

## SSC-441 Inbox閉Reasonの固定SQLstateとhash契約PT（2026-11-16）

BUG3100/YKT2572のInboxException.sqlState閉enum switchを、Reason五定数が既固定SQLstateをprivatefinal metadataで保持する表現へ置換する。MESSAGE_ID_REUSE/OPERATION_TOKEN_REUSE=23000、FINGERPRINT_KEY_UNAVAILABLE=55000、STATE_CORRUPT=XX000、TRANSACTION_REQUIRED=25000の順序・name/ordinal/values/valueOf/可視性を完全保持する。private enum constructorだけで五つのnonnull literalを一度代入し、package-private accessorをouter privatehelperから読む。privatehelperはObjects.requireNonNull(reason,reason)を元と同じmessageで先に行い、SQLException継承/constructor/message/SQLstate/errorCode/reason getter/throw identity・全caller public ABIを変えない。閉定数のprivate constructionへ到達しないnull guardや反射用経路を足さず、NullAwayとliteral閉包でfield invariantを確立する。生成MatchException defaultだけが表現から不要になるので、coverage除外/到達不能合格/別enum binary/私有反射/無意味instanceを使わない。BUG3101/YKT2573の新Request fixtureは独立期待retainedを保持し、単一entry Map.of.getから実HashMapへのput/getへ変えてhash-equalityを実操作で確認する。元21のTest ID・入力・期待・全assertとMain1の他bodyを逆展開formatted exactで確認する。SS範囲内の内部詳細でRD/UI/DIF/QA変更不要。先にSS324352354914だけをmainへ反映してからPGし、新Core同run全21/freshMain14Root/適用未分類0/current15physical15CRC-initXML/同singleexecraw必須四100を要求する。五SQLstateとNullableReason拒否のgoldenは元21を保持、元raw不足PG35714を残し旧exec合算0。全caller source/既public ABIの一致を確認するが、実DBcoordinatorや全module/全451/native/CHR/終了依存の受入にはしない。Actual4/Root2/鍵/VMDB/native/aru/HOLDを維持、古いRootや無関係PTを確認だけで反復しない。

状態:設計確定・main反映前、実装/全21再資格/全体品質は未完。


### SSC-462 応答snapshotの一般診断（2026-11-18）

EncryptedResponseSnapshotの一般診断はSS351の固定文字列を返す。keyVersion()とciphertext()は既保存・復号の値契約を維持する。DBの列、暗号の形式、キー選択、応答の再送、byte配列の防御的copyに変更はない。PT-IDEM-007/008、PT-P01810-CATALOG-008は固定診断と、合成値に対する明示取得・既処理期待を別々に照合する。


### SSC-463 Inbox結果参照の一般診断（2026-11-18）

InboxResultReferenceはSS351で定めた固定診断を返す。type()、numericId()、uuid()の値と、種別別の妥当性、保存・再送、既電文と一般診断を区別する。PT-IDEM-REFERENCE001～003とCATALOG-013で全種別と独立値を照合する。


### SSC-464 Outbox値の一般診断（2026-11-18）

OutboxEntry／OutboxRequestの一般診断はSS351の固定文言とする。宛先、ID、DLQ、本文copy、retry時間・SQL行、電文・順序と各明示取得の契約を維持する。CATALOG-022/023は閉じた合成値の独立試験で確認し、実送達と監査は別条件。

## SSC-466 一時バッファの通常診断

`WipingByteArrayOutputStream.toString()` の出力は `WipingByteArrayOutputStream[<redacted>]` に固定する。byte数、容量、内容を通常診断へ連結しない。既 `size()`、書込みの境界検査、戻りbyteの所有、消去、正規化とHMACの処理は維持する。PT-IDEM-WIPE-001〜004、PT-P01810-CATALOG-015、SS351。
