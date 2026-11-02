# 継続監査のfixture・probe・故障注入準備仕様

本書は実装前の工具契約である。以下のT/P/F名はcommand名ではなく、全て **UNIMPLEMENTED**。製品・PT・IT実行、環境起動、配備を今回行わない。ケース正本はcases/scenarios/contracts、表の正本は各JSONとし、本書で値を転記管理しない。[512](512_結合構成・環境・データ.md)、[513](513_工具・故障注入準備仕様.md)、[514](514_追加fixture・工具・負荷計測仕様.md)、[541](../540_実行・管理/541_Codex実行・判定・証跡・再開.md)を継承し、より具体的な本書の条件を優先する。

## 1. 固定入力と独立oracle

F-IF-v3の正本は[interface-fixture-v3](../data/interface-fixture-v3.json)。U1/U2/U3=1/2/3、A1/A2=11/12、TUSER=201、作成User sequence=1001。F-BASE-v1の未解決prefixはSF101=`01`、game1のpath=`scenario/IT/01.scn`へ具体化した合成試験copyで扱う。SF101のdisplay titleは`IT章`、sectionは`IT節`、entry1001はdialogue/IT話者でvoice401/402、entry1002はnarration/音声なし。entry_index/audio_orderによる3recordを、DBが返した順から期待生成せず入力manifestの順序で手組する。SCN再生成metadata8はUI234の `Script file ID, Game code, Display title, Display path, Previous file ID, Previous title, Next file ID, Next title` に対応する8値で、UI正本のfield表記・大小文字をfield-oracle行で束縛する。DB列名とwire名を混同しない。

[フィールドoracle351行](../data/field-oracles-v3.json)はUI232共通Header17行とUI233～236のDATA/RECORD334行。幅・offset・型・順序・固定値は元UI行を正として、独立した標準UTF-8/NFC/整数format/UTC→JST変換/space又はzero paddingで計算する。Production codec/SQL/fingerprint/replay helperを呼ばない。NはASCII非負整数を固定幅zero-pad、XはNFC後byte数とcodepoint境界を検査し右space、Bは生byte、未使用fieldはprofileごとのfiller。業務Tのµsとwireのmillisecond（切捨て・丸めはUIの宣言に従う）を別値として持つ。Message/correlationは保存元M0と今回M1を別列で管理する。expected SHAは完成した独立byteに標準SHA-256を適用して得る。暗号は独立JCE AES/GCMとAAD/nonce/keyVersionで検算し、乱数nonceやJDK圧縮出力を固定ciphertext一致の期待へしない。圧縮時は展開後全byteと上限を比較する。

F-INSPECT-v3は[inspector-fixture-v3](../data/inspector-fixture-v3.json)とOPS040～044。canonical31route、各保存code、NKQRY1/NKREF1/AUTH_SESSION/ERROR、元M0・owner/token/receipt/OutboxSENTを独立生成し、現在roleや現在検索結果で保存snapshotを置換しない。現在DBのFK/CK/partial UKを破る「重複QWK」を投入して通常の合法状態に見せない。DDLが阻止する値のparser分岐はPT、ITは実DDLの拒否と合法なSENT/参照保持の結合を検証する。HMAC秘密はInspectorへ配布せず読取可能version名だけ。raw wire/cipher/context/鍵/nonce/DB原値はGit外private0600、公開にはhash/長さ/比較結果だけ。

## 2. Full master・選択fixture

Full-master合格条件は59,627files/19,240,707,190bytes、script_files262/entries99,661/audio37,256/links35,201/video20/music129を維持する。SS343のPG/PT最小1asset profileをfull-master ITへ代入しない。正本Current/productionを変更せず、承認済みread-onlyコピーと全inventory/移行mappingのhashを固定する。

Music選択は移行入力manifestからcategory=`曲`・section=`ゲーム`の候補を独立列挙し、`display_order, logical IDのUnicode順`の最小を選ぶ。選択したtrack/pair_key/roleと同category/sectionの全期待行・順序を**対象APIを呼ぶ前に**別manifestへ保存する。候補0/不正mappingならPREP-DATAで停止し別の恣意的選択へ切り替えない。通常masterの実値を未取得のまま実行可能としない。

Selective性能fixtureは正本masterの独立import manifestから6filterの候補値とmatch集合をofflineで計算する（SQL/Repositoryを使用しない）。predicate候補は `keyword,game,speaker,chapter,type,voice` のSS332で実装する単独/ANDに限り、候補をfield名→値のUnicode順に固定し、match件数が1..100かつ非match有の最初を採る。100件ちょうどを要求する根拠はないため、PERF036の期待件数はこの固定集合のN（1..100）とする。SQL結果から集合を学習しない。全99,661件の走査・結合を独立実装で二重検算しhashをレビューする。候補が無い場合はデータ不足としてBLOCKED、未承認のmaster書換え/架空match100で代用0。非選択検索と997pageはPERF042で別判定する。ISS-DATA/SELECTIVITYは具体選択仕様ができたD（データ生成・レビュー）であり、実データ準備は未完了。

## 3. P-CONFIG probe（190データ行、25headerを除外）

[config-bindings-v3](../data/config-bindings-v3.json)の各CFG IDにTest/SC/Assertion/元SS条件/全期待列/P-probeを保持する。観測recordは `run,SC,attempt,CFG,source,artifact,boot,Unit,Invocation,phase,key,typed_value,unit,before_ns,after_ns,private_raw_path,sha256,status`。実値の欠落/null/unknownをdefaultに置換しない。工具実装時は元SSの全列の意味を保持し、期待欄の文章をactual文字列へコピーして合格にする方法は禁止。

| Probe | 実観測・型付きprojectionと判定 |
|---|---|
| P-MQ-GLOBAL | 配布broker.xmlのschema解析と実Broker管理属性をkeyでjoin。NIO/persistence/cache/auto-create等はenum/bool、MiB=1048576byte、msは整数へ変換。journal実fileと起動consoleでもNIOを確認。pool等の初期値変更は承認ID/測定根拠がある場合だけ別版で比較。 |
| P-MQ-TOPOLOGY | 管理browseで6 Address/Queueの名前・durable・ANYCAST・producer/consumer数、実credentialのJAASrole ACLを採る。principal名をrole名と同一視しない。request5s/reply10s/internal0は実propertyとExpiryで確認。 |
| P-MQ-CAPACITY / P-MQ-PAGE | Address別memory/page/total byte・message上限/policyの管理実値を比較。各軸はMQ010、disk90%はMQ020、alert分母は合計容量。高水位、page limit、合計を混ぜない。 |
| P-MQ-REDELIVERY | 管理実効4/1000ms/5.0/30000msと、同Message受信1/5/25秒をMQ001で照合。application Outboxの±10%jitterとは別。 |
| P-JMS-CLIENT | 実ownerごとのconnection/session/consumer/transactionmode/windowと設定getterの安全投影、実sendcommit、DB/JMS所有を採る。純setter全12の異常matrixはPT、実listener1/4とACKはIT。 |
| P-WIRE-PROPERTY | 実BytesMessageのJMS/AMQ/NK許可propertyとHeader、TTL、長さをO-WIREで独立decode。password等をpropertyへ置かない。 |
| P-UNIT-DEPENDENCY | 真正PID1の全対象UnitをLoad/Ref保持しAfter/Requires/Wants/PartOf/BindsToを型付きUnit集合で比較（表示順のみ集合化）。SS342 SSC139に従いAPI依存でExpiry保守子を再実行0。 |
| P-UNIT-DIRECTIVE | 配布原byte/署名とsystemctl showのType/User/Group/WorkingDirectory/credential/umask/Restart/limit/timeoutをjoin。元開始時刻・PID等の動的履歴は宣言path/argv/ignore_errorsと別比較。Root→ordinaryの後続具体化を優先し「shell無し」を旧観測PID数固定へ解釈しない。 |
| P-JVM-RESOURCE | 同PID/start/Invocationのprivate argv・MemoryMax・RSS/heap/direct/metaspace/threadpoolを別採取し、Xms/Xmx/上限をbyteへ正規化。headroomは予算差であり追加allocationではない。 |
| P-APP-RUNTIME | 実bind/管理HTTP公開5情報/threads/queue/phase timeout、poolactive-idle-pending-max・minを計測。API業務HTTPは無、Web8080/8081・API8091loopback。秘密値のActuator露出禁止。 |
| P-PG-GLOBAL | 実運用roleの別RO接続からpg_settings/current_settingをnameで取得、unit/typeを含めて期待へ換算。planner effective_cache_size6GBはallocationに加算しない。SHOWを期待生成SQLへしない。 |
| P-PG-ROLE | catalogのrole設定に加え各実roleで新接続してstatement/lock/idle timeoutをSHOW。API/Web1500/500ms/15s、batch/backup/migration30min/5s/60s、ops10s/1s/15s。Inspector30s/5sとprocess30minを別記録、未設定idleを設定済みに補完0。 |
| P-HOST-BUDGET | 同窓のprocess/OS/cache/diskを独立収支。合計16GB/256GB相当と各SS予算、STANDARDでDEBUG2GB非起動を確認。shared/RSSを二重加算しない。 |
| P-DEPLOY-VALIDATION | Caddyfmt/adapt/validate、systemd-analyze verify、PGconfig/hba/schema/grant、ArtemisXML/topology、Javaartifact/infoの各出力・原exit・hashを採る。read-only確認とstart/配備権限を分ける。存在確認済commandは513に限定し、新工具はCLI未定。 |
| P-CONFIG-PRECEDENCE | Jar/default→common→service→非秘密env→systemdcredentialの入力5層を全filehashで固定。非秘密同keyに異なる許容値を置いた専有variantで最上位だけ採用を確認。unknown/duplicate/type/range/missingsecretは起動拒否。rawtemplate全byteSHAとeffectiveYAML SHAは別、comment-only rawdriftも署名照合で検知。 |
| P-APP-KEY | SS343の実keyと型/単位/初期値/許容rangeをrenderedfile→起動時安全投影→実bind/挙動へ結ぶ。rootは実保持inode/RO/RW/非重複、roleはDB/MQ実資格へ解決。key aliasを発明せず最終SS/configschemaで確認する。 |
| P-CREDENTIAL-CATALOG | 実Unit LoadCredentialとprivate root/fileのowner/mode/ACL/link/RO、consumer/purpose/version/hashを確認。valueは記録しない。backup archiveの固定17とruntime current/previous配布catalogは目的が異なる（OPS053）。db-backup実配布とarchiveのbackup-pgpass名を勝手に統一しない。 |
| P-CREDENTIAL-RUNTIME | rootmanager所有0550/file0440専用UID ACL5entry又は専用UID所有0500/0400・noACLの2合法形を別SCで確認。AESfile54..69byte、nlink1、filesystemRO、全保持前後属性、失敗時read/DB0。PTの全errno/parseは複製せず実UID結合を確認。 |
| P-INSPECTOR-INPUT | 実oneshotのCREDENTIALS_DIRECTORY/URL/run/cutoff/version名を全長/ASCII/UTCµs/canonicalで検査し、実owner/wrapper/親deadline/DBrunとjoin。root内部pathの未保証prefixやHMAC秘密を推測しない。 |
| P-RUN-BYTES | 実保持原本のanchor72/begin-active109/done140or141byteを独立literalで照合。元cutoff/activation/ended/resultの一致、fsync/no-replace/dirsyncを観測。 |
| P-RUN-LIFECYCLE | OPS045の各公開確定点で原本graph/active/全DB/実子終端を照合、start/resume/completeの前提と冪等性を固定。値record一致を起動許可へ変換0。 |
| P-RUN-GC | OPS050の400日strict比較/3DB参照0/plan/marker/全syncと部分保全。marker195..204byte、planは元done140/141byte。NKBRET1は別形式最大16MiB/4096name、roots/prestart65536byteと混同0。 |

設定値の型差・内部順序正規化はSS343/353の範囲だけ。JSON object key表示順だけならrawhashは別保存しtyped内容を比較、journal event/cursor順、argv、wirebyte、画面順、業務SQL順を集合化しない。過去SSC137のJava唯一link仮定はSSC143の固定二段へ、cross-runはSSC200のNKPRESTART2/NKEXPIRYSKIP2へ更新する。旧保存byteを新版へ書換えない。

## 4. 実故障の準備と安全な再現

T-COMMIT-v3は専有PGプロトコルproxyでCOMMIT requestとCommandComplete/ReadyForQueryの**clientへの応答だけ**を切る。COMMIT可視化は別RO接続で対象PK集合/全値とtransaction終端を確認し、proxy応答を送る前のbarrierと突合する。commit前分岐はCOMMIT転送前に切断、commit済分岐はserver応答捕捉後clientへ未配送で切断、server応答未取得はUNKNOWNのまま。手SQLで同じ更新を作る/関数mockでcommit成功と返す方法は不可。proxyはDBsecretを公開せずraw私有、通常transportとの同source対照を持つ。

T-JOURNAL-v3はMQ005/006。完全停止した専有copyのversion2.56.0 record形式をvendor sourceから校正し、header/length/checksumの検査対象1byteと検知message/classをfixture manifestに事前固定する。位置/元byte/新byte/全hash、正常copy起動対照、破損が実検知されるproofが必要。未検知はINVALID_STIMULUS、空Queueになったことを検知成功にしない。元journalは不変更、自動初期化なし。新instance移行・restoreはSEV1承認と対象二者確認の開始依存を維持する。

T-MQCAP-v3はbroker管理の実memory/paged/persistentSize/件数と投入body/header/properties/overheadの対応を100/200/400件の専有予備fixtureで校正する。上限直前/同値/超過の実計上を受信0で確認し、body byteだけを容量とみなさない。byte軸試験は件数上限未到達、件数軸はbyte未到達、両者ORは別SC。正式容量を縮小して合格0。校正表と本文の実投入境界表をレビューしてから開始する。

T-TIME-v3は同hostCLOCK_MONOTONICとBroker送達時刻の同一Message timelineを取得する。delay起点は前配送のrollback確認→Broker再配送待ち、終点は次consumer callback入口。dispatcher/application retryはfailure時刻→next_attempt_atで別計測、±10%jitterを含める。計測器の前後呼出intervalとscheduler遅れを同source正常対照100回で校正、下限/上限/clock分解能/負荷窓/採取overheadを表へ固定し**環境レビュー済みの許容差がなければ開始不可**。SS354が認める環境事前定義であり、設定1/5/25秒や順序を緩和しない。任意の50ms等を無根拠に加算しない。

実OSclose故障、送達不明、samePID exec中Zはfixtureが実境界を観測できることを先に確認する。実closeのUNCONFIRMEDをproxy成功やFDが後から消えた事実で正常closeへ補完0。各既存HOLDは解除せず、許可された専有fixtureに限る。

## 5. 観測器・JDKの影響

O-FSはO-FILEのaliasで、fs.jsonlにdev/ino/type/uid/gid/mode/nlink/size/mtime/ctime/ACL/readOnly/名前集合/hash/FDownership/phaseを型付き保存。O-OSはO-UNIT＋O-FDのaliasでos.jsonlにPID1/boot/INV/PID/startTicks/argvSHA/NSS全UID-GIDgroups/caps/NNP/cgroup/tasks/全FDとmanager/kernel前後値を保存する。O-METRICはmetric.jsonlにmetric名/type/許可label/整数又はdecimal値/単位/採取前後monotonic/source timestampを保存する。単なる文字列dumpは不可。

collectorが開くRODB接続・一時FD・bus Ref・observer自身のthreadはownerタグで特定し、service所有数から除外する場合は明示した個体と寿命だけ。未特定FD/peerを「計測器」として除外0。JDK内部generatedclass/hiddenclass/ThreadIDやOS粗粒度mtimeは原値保持と観測範囲を分け、SS353 SSC284の操作前realtime-coarse下限/精密上限・非減少・identity不変を満たす有限metadata差だけ扱う。採取していない過去時刻を後付けしない。

SS343/342 SSC193/196/234のcoverage計測はPGPT source資格である。pin JaCoCo0.8.15、output=none/append=false/dumponexit=false、getExecutionData(false)、同role/INV/session/frozen CRC、TERMINAL→CLOSINGの順とnew-only原本、before-exec/terminal/closingを別資格で照合する。ITはこれらの最終PGPT完了証拠をCとして受領し、同source全体へ旧execをunionしない。追加agentによるFD/thread/bytecode/時間影響を記録し、正式性能本判定はunagented STANDARD窓を別採取する。JDK生成要素を誤った業務件数/coverage期待でNGにしない。

gauge比較はsource状態をbarrierで保持し、独立原値の前後区間に含まれるsampleだけ使用する。timestamp gaugeは実success ended_at秒（精度はmetric表現）を独立DB/Unit receiptへjoin、collector採取時刻を期待値にしない。変動中sampleは境界を跨ぐため再取得、欠測はNOT_JUDGED。decimal丸めはexposition桁の区間として比較し、未規定のstaleness猶予やSLAを追加しない。alertの1s採取は試験側の観測周期、設計の評価周期を1sへ変更する設定ではない。

## 6. 開始判定と再開

B=設計判断はissuesの個別条件だけ、C=最終PGPT/SS/release/464照合、D=fixture生成/工具/環境/権限校正を別記録する。Dの仕様があることと工具実装済みは別で、全ITはNOT_EXECUTED。各工具の実装/独立自己検査/存在・用途確認/校正review、source/environment/active job/途中証跡のjoin、HOLDと承認を全て満たすまで実行不可。未収束・UNKNOWN・既予約は同jobへ再付着し、同Message/token/Unit操作を自動再発行しない。最終版差分によるcase更新はレビュー完了後にのみ新attemptを予約する。

## 7. schema oracleと読取SQL準備

[schema-oracle-v3](../data/schema-oracle-v3.json)はSS331の原文blockから独立期待manifestを作る入力索引であり、273blockを273DB要件とは数えない。IT-DB-004では列/制約/索引/role/functionの宣言をtyped rowへ展開してreviewする。document管理/履歴は実catalog要求から外し、承認済み後続V008～028等の追加を旧総括21tableへ切り詰めない。各objectのSS条件IDと親UI241/242を保持する。純上下限・全CK組合せはPTの担当。

T-DB-v3のread-only collectorが実装すべきSQL形は次のとおり（未作成commandではない、今回は実行しない）。実対象database/schemaをmanifestと二者照合してから専用RO接続で実行する。

```sql
SELECT n.nspname,c.relname,a.attname,pg_catalog.format_type(a.atttypid,a.atttypmod) AS type,
       a.attnotnull,a.attidentity,pg_catalog.pg_get_expr(d.adbin,d.adrelid) AS default_expr
FROM pg_catalog.pg_namespace n
JOIN pg_catalog.pg_class c ON c.relnamespace=n.oid
JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped
LEFT JOIN pg_catalog.pg_attrdef d ON d.adrelid=c.oid AND d.adnum=a.attnum
WHERE n.nspname IN ('schubert','schubert_web_session','schubert_meta') AND c.relkind IN ('r','p')
ORDER BY n.nspname,c.relname,a.attnum;
```

constraintはpg_constraint/pg_get_constraintdefからconname/type/columns/FKtarget/actions/deferrable/validated、indexはpg_index/pg_get_indexdefからunique/列順/expr/partialpredicate/validを全取得。role/ACL/defaultACLはpg_roles/aclexplode/pg_default_acl、functionはpg_proc/pg_get_function_identity_argumentsからsignature/owner/securitydefiner/search_path/EXECUTEを取得する。schema修飾と型を正規化して期待manifestの各列へjoinし、SQL式の単なる空白差とpredicate/action差を分ける。current_settingやpg_catalogをexpectedへ転記しない。実roleの禁止statementはSQLSTATE42501とrow/namespace非更新を確認、権限追加/SETROLE回避は行わない。

unitのM/G、JVMのm/g、PostgreSQLのMB/GBは各製品の設定単位でbyteへ投影し（いずれも当該設定では1024倍系列）、Transferの48,000,000byte/1fileおよびroot3.5/4.5/5GBのdecimal値と混ぜない。物理16GB/256GB相当、OS予約・共有memory・planner hintは別収支。元単位・実byte・換算式を両方保存する。

Transferのbyte境界fixtureは完全readyの4800倍行と、試験所有の正規UUID.partの残余byteを組み合わせて指定logicalbyteへ合わせる。全fileの名前/owner0640/link1/ACL0/dev/hash・残余根拠をmanifestへ固定、起動scanと所有条件を通す。root容量gaugeを偽装しない。filesystem%試験では別の専有fillfileを実割当し、sparse logicalsizeを物理使用率へ換算しない。byte軸の他条件はfiles=100、count軸の他条件は100,000,000byteで非支配とする。

## 8. HTTP nameと補助sourceの区別

[http-input-bindings-v3](../data/http-input-bindings-v3.json)に、作成時実装source d3edd2c5の5templateの存在・hash・HTTP nameを記録した。操作token=`operation_token`、User楽観version=`expected_version`、Password確認=`password_confirmation`。NTC/QDLはpath IDとhidden `id`も送る。ケースのT0は正規GETが発行した用途/target/version/actorの実UUIDで、任意固定UUIDへhiddenを書き換えて正常試験にしない。各GETのCSRF hidden名/値を同sessionへbindする。これは実入力口の確認であり、期待業務値を現行実装から導く操作ではない。最終releaseで再照合し、未定義fieldの受理や意味変更で帳尻を合わせない。

F-IFのQ1はIF025では「今回作成する期待行template」で、開始時Q/Job/Notification/Answer/workOutbox/locator0、sequence501/601/701。照会/取消/削除ではSCの状態variantを実seedする。初期seed済み501と新規作成501を同じfixtureへ同居させない。ownerが本人限定の通知はADMINも当actor、質問全scopeのADMINだけU1所有を対象とする。

T-RECEIPT-v3は未実装の故障注入profile。親実Unit engine/専用DB/本物PID1/全kernelを使い、専有試験childだけを既知終了0（DBsummary protected1なら期待10）にする署名試験artifactへ置き換える。改変箇所/hash/親子版差を記録し、偽manager property/元receiptの手編集をしない。親の不一致拒否を検証する用途に限定し、実Inspector正常10/正常stop/親再取得の正系は最終releaseそのもので別に必須。試験child成功を最終Inspector資格・PGPT品質へ合算しない。通常childを改変せずに再現できる外部故障であればその方式をレビューして使用する。今回作成/配備/実行は0。

## 9. T-MEMORY-v3（未実装）

PERF046専用の署名試験artifactにだけ一回故障入口を設ける。外側observerのrun/SC/boot/Unit/INV/PIDticks/所有nonce/一回予約を前後照合し、heapは8MiB×最大128回を保持、MemoryMaxは本人cgroup内のnative匿名memoryを64MiB×最大32回確保して各pageへ実touchする。命令1回ごとに外側collectorへ非秘密receipt、既定上限/120秒watchdogを守りhost全体OOMへ拡張しない。上限値・hardening・ExitOnOOM・dump無効は本番設定を維持する。注入hookの全byte差/署名/sourceとinstrumentation影響を記録し、Production期待生成関数を流用しない。

一回予約を外側へ耐久保存し、再起動後に同注入を再発行しない。JVM actualOOMEとkernelcgroupOOMをJVM/GC/memory.events/真正PID1/同世代terminalで区別する。単なるError throw/kill/proxy例外はこの2mechanismの代用不可。故障前に専有hostのmemory収支/監視/保全容量/元HOLDと回復所有手順を確認、条件未充足ならBLOCKED。PGPT/current/停止中VMへは接続しない。実験終了は旧close正常化とは別で、原失敗保全・正規新所有gate・同ID/DB/MQ整合・全後条件を満たしてだけ復帰とする。今回、この工具の実装/起動/割当/注入は行わない。

## 10. 衝突・反復の再現

FILE062のUUID衝突は本物のdirectory/no-replace結合を必要とする。推奨T-FAULTは生成UUIDをprivate barrierで取得した後・CREATE_NEW又はready公開前に一時停止し、当専有namespaceへ別の試験所有actorが同名regular fileを一回作成して衝突させる。元A/Bのbyte/hash/全属性を保存してからwriterを解放し、非上書きと新UUIDへの有限再試行を観測する。RNG proxyだけの結果は実FSの合格にしない。総試行3/4が未決のall_collideだけB、1回衝突後成功と既存file不変は確定。

競合反復はSS354に従い100回、各rの初期clone/seedを分ける。UUIDの試験側suffixは `100000*(r-1)+worker_index`（worker0..99999）等の衝突しない独立整数表へbindし、同一SCが意図して共有するMessage/tokenだけ同一値にする。正規Web発行token/contextの値は上書きせず、生成結果を同r private manifestへbindする。worker数×反復数をcase/SC数へ加算しない。確率競合の元seed/失敗r/worker/時系列を原証拠へ保存する。

## 11. QA051承認後の比較artifact（未実装）

作成中にorigin/mainが7147c428（PR202、QA051/UIC010/SSC184承認）へ進んだ。初期8b91944dからの差分はUI225/252/264、SS351§4.1/355§8.1と関係台帳。既存SS4275block本文は不変、新12blockを追加レビューした。QA051の二点（action名称と相関付き比較）は回答待ち解消。PGPT d3eddの未回答表記は旧sourceの記録で、現在状態はmainを優先する。比較実装/独立検証/実NKCHR-L01/正式・他HOLD/PGPT枠停止の解除とは別。

T-LOG-COMPARE-v3のinputはLOG022のSC、SS351から固定したoperation/category/action/store/count/HTTPfield表、既存ログ保全before、Current固定baseline参照、Web request→wireM0→API audit及びlocal event→outbox→DB source_message_idのprivate binding、整合after。outputはfield/element/keyごとの旧値・NK期待値・actual・相関証拠・追加技術行の根拠とrawhash。汎用uppercase、全category除外、watermarkのみの今回行認定、秘密raw出力を禁止する。

| 旧値/操作 | 確定NK対応 | 範囲 |
|---|---|---|
| 空actionのREQUEST | HTTP_REQUEST_COMPLETED/REQUEST | 同じ実HTTP eventの相関がある行だけ |
| login_success | LOGIN_SUCCEEDED/SECURITY | 同Login成功/同操作categoryの根拠、REQUEST別行は別期待 |
| scenario検索のsearch | SCENARIO_SEARCHED/ACTION | 同SRC実検索、同category、REQUESTとは別に検証 |
| menu/log_search旧業務行 | 個別caller/cardinalityはISS-LOG-CALLER-MAPPING | 当HTTPのREQUEST1は確定。REQUESTがあるだけで旧業務行欠落を免除せず、未定義のMENU_*等を発明しない |

比較工具は独立合成入力で正常対応・欠落1・同event重複1・別request誤結合・同時刻/大IDnoise・未知追加行・既存行変異・未登録DOM順序差を検証してから実経路へ接続する。これらは工具資格/PTで、IT実経路の合格に代用しない。LOG022は実NK HTTP→local/outbox/MQ/API/DBで確定した記録責務を確認し、Current側は固定原artifactをread-only参照する。PGPTの元実NKCHR-L01をITへ移管して解消しない。menu/log_search等の未対応行があればBの該当比較だけNOT_JUDGED、未登録件数差を包括許可0。承認済み二点を再質問しない。
