# 朝batch・backup・削除・再実行設計

SSC278（2026-10-13、BUG1162/YKT930）：親の全gate・原本・資源正常close後に得る既定SUCCESS0/WARNING10は、Morning controllerのType=oneshot/SuccessExitStatus=10でmanager正常終端へ対応させる。10を無視して0へ変換しない。真正同Root PID1 start job done・同activation NKDONE1の0/10・元30分・API/Web/Caddy・owned逆順停止及び全資源後条件は独立必須。30/50/70/143/signal/timeout/未知を許可しない。旧PG1759のDONE10とfailed10は保全し、新設定やGCから旧成功へ再解釈しない。未結線時の暫定「親SuccessExitStatus無し」だけを置換し、同日処理結果・Backup成功再用・再送契約は不変更。

SSC230（2026-10-09、SSC198228229当completed profile）：同e492の新親真正DONE1697.279879s/当同Rootordinary API-Web-Caddy・新正常owned逆順停止/独立全十kernel・peer-lock0/全24-504不変の後、別fresh所有でpg635-once-resume.confだけを正規退役する。元anchor/cutoff/activation/DONE/ISSUED epoch・旧二BackupSUCCESS/全Backup・今回十SKIPを保持し、operatorによるpending/INVALID化や原本/DB修復をしない。新通常NEW_SUCCESSの保持期限試験は退役全後条件後に独立実行し、REUSED_SUCCESSの削除0から保持期限実削除の成功を作らない。元親30分の完成証拠・現在の全終端と旧失敗143/30/UNKNOWNを区別し、再STOP/start/旧permit再利用をしない。

SSC203（2026-10-07、BUG799/YKT570）：親完了の各compound DB readはSS342の全peer/元graph/run整合をTX外の前後で確認し、TX内SQL境界は同保持原本namespace/owner-thread/Root/M/A/元budgetを継続認証する。元全row/progress seal・各typed intent退役前後の全証跡・DONE直前・同親30分を維持し、途中失効/変更/close不明は隔離する。業務再処理・同日SKIP/Backup契約変更0。

SSC202（2026-10-06、SSC200201/BUG788/YKT562）：隔離PG/PT VMの同日別run参照修正では、成功済みBackup二stepとCleanup七SKIPを持つ未完了runを保全し、027→028移行・pending code-only・一回用通常resumeを別の正常所有区間として認定する。元cutoff/activationをoperatorが更新せず、手DB terminal修復/日次業務再処理をしない。既成功Backupは元schema027の真正manifest/全byte/元二handleで通常same-run再用し、新profile028へ書き換えない。新規Backupだけ現在署名/profile028と整合させる。親fresh Invocationからの30分budget、実Unitの期限、API所有のままWeb/Caddy/原本DONE、失敗逆順停止・全後条件は既契約のまま。各段の実source/終了コード/全資源正常帰還を確認するまで次段の権限・成功を与えない。

SSC201（2026-10-06、SSC200/BUG788/YKT562）：Cleanup元SUCCESSのCLEAN_LOG/CLEAN_INBOX_OUTBOXに限り、元run/cutoff/終了時刻で331所定readonly全進捗照会を同owned DB TX下で実行し、64hex sealを元Entryに別保持する。元14列と全row sealを親のactual/issuer前・公開後/completion再読で比較し、cursorだけの変更・count/END変更・未完了/不足/別identityを拒否する。sealはデータであってresume/Unit/permit権限ではない。Log/Inbox以外にsealを付けない、現在SKIPのzero・fresh receipt・元原本所有前後を維持し、業務の再削除・raw cursor公開・新grant0。旧原本・旧progress・旧結果の更新/再解釈0。

SSC200（2026-10-06、BUG788/YKT562、実装前補足）：通常noargsの新runと明示same-run resumeの双方で、UI251§11/SS331§8.3の同日成功SKIPを維持する。Cleanup正常fresh receiptと今回七terminalを読んだ後、ALREADY_SUCCESSFULだけ元成功を同business_date/stepの唯一完全SUCCESSとして読取り、元の検証済原本anchor/run/cutoff・row/attempt/start/end/resultとLog END/Inbox progressを独立に保持する。同runであることを必須にせず、別日/不足/矛盾/非唯一/未来/今回handle同一/元非SUCCESSは拒否。親の現在M/A/DB/advisory・元30min budget・current/現activationと元原本照合を省略しない。Expiryも元原本と元cutoffのSUCCESS audit及び現在cutoff fresh MQ selected0を分離、元auditを更新/新stage/purgeへ流用しない。今回SKIP all0/ended=started・fresh Unit終端/receiptは維持し、元成功や旧receiptを今回業務実行の成功に算入しない。CompletionEvidence・prestart・issuer直前/公開後の全再確認へ同じ型付き元参照を通す。Backup same-run成功再用の既契約、失敗pair/Transfer/critical、owned逆順停止/全後条件は緩和しない。

SSC199（2026-10-06、BUG784/YKT560）：Cleanup終端/拒否/元成功参照のDB readbackはSS332のSSC063/199合成例外契約に従う。親の借用transactionと期限は保持し、未知provider/closeを既知DB失敗へ補完しない。各owned Statement/ResultSetは正常closeまで値不返却、七stepと十四列のvalue不正は狭いpure検査だけで固定SQL不正へ分類する。readback成功だけで原本・Unit・OS/root/Epoch authorityを追加しない。CTERM006～008の正常/異常/204合成・原行SQL後条件、必要全回帰/同source実経路を別に確認する。親未知時のretention/再隔離、古いUNKNOWN-close記録、業務結果/実receiptは不変更。

## SSC198 Backup途中保全後の正規resume（2026-10-06、BUG771/YKT551）

SSC198限定補足（同日17:02、通常resumeのUnit束縛）：未完了active/pendingの通常 `MorningResumeAdmission` は同activationを保持でき、元run/cutoffを変えない。「必ず新activation」を期待値にしない。親は新実Invocation/startから元30分budgetを持つ。operatorのpending配備とは別の正常所有区間でSS343所定の一回用runtime drop-inを準備し、durable新予約とobserver先行後に固定Morning Unitへ一回だけ外部startする。送達不明/既予約は再付着し同startを繰り返さない。ABANDONED化、requestの新transaction確認・置換、fresh Backupと後続処理はProduction通常resumeが行い、operatorでは行わない。元PG478のtimeout/旧close未知は新実行と別に維持する。

SS343 SSC198の限定operator退役・pending code-onlyはBackup成功/親正常closeではない。旧両RUNNING/全14列とdump-only.part/requestを保持する。通常の明示同run resumeだけが既beginBackup(recoverAbandoned=true)で旧両FAILED/ABANDONED＋新両RUNNINGを同transactionへcommitし、requireAbandonedRequestの新transaction再読後にSSC114 prepareResumeReplacementへ進む。新requestは元run/cutoffと新実開始時刻へ束縛し、旧requestのbyte/metadataを先に私有保全する。旧.partは自動修復/削除せず新attemptと別に保持、成功bundle/件数へ補完しない。旧6Backup＋新成功1が最大7で、未完成.partは保持する非適格世代であり、retentionで旧保全物を消してよい根拠にしない。新fresh worker/CONFIG実archive/両SUCCESS/後続削除・全原本/DONE・最外資源正常帰還は別必須。既成功day skip・期限・業務・operator DB更新権限を変更しない。

SSC187/BUG704：最終completionでのBackup実結果確認は、同親で実行を完了した既存MorningBackupUnitCycleの停止後証明を借用する。executeObservedのfresh正常receipt→明示stop client正常0→全kernel終端→同baseline/元receiptの停止後再読→request/intent退役を経た同cycleと元TerminalReceiptを保持し、最終検査ではcompletedReceiptの参照同一とrecheckCompletedBackupを再要求する。Backup明示停止後にKEEP_ACTIVE専用requireStillPresentを適用しない。完全GC coldは元receiptを持つ同cycleの停止後条件としてのみ受理し、coldからreceipt0を作らない。Cleanup/Expiryは従来どおり保持中のfresh receiptを厳密再読する。DB全行/原本/同M/A/同世代・同budgetの既存検査は省略しない。別cycle/未完了/別receipt/部分cold/別Invocation/未知/資源close不明は拒否し、通常完了へ変換しない。外部結果・Backup失敗時WARNING/SKIP・元30分期限は変更しない。

SSC175（2026-10-04、QA048の受付参照保守）：既存business cleanup/SESSION/INBOX-OUTBOX/LOGの順序とBackup失敗時六SKIPは不変更。既存`CLEAN_BATCH_RUN`のtechnical共有stepを一度だけbeginし、固定`WEB_RECEIPTS`→既存`BATCH_RUNS`→`INBOX_PROGRESS`→`LOG_PROGRESS`の順に処理する（既存3kind間の順は保持）。各chunkは現在原本run開始cutoff/親OS・DB排他/30分deadline/実両backup成功と完全step handleを保持し、1,000件以内のDELETE/累積を同TXでcommitする。全4kindが実完了した後だけ合算累積でfinishし、SKIP LOCKED残・rollback/commit不明/子失敗を0件完了にしない。孤児条件は物理questions不存在のみ、存続質問locator独自TTL0、Web/業務復元の片方向原則はSS313/331。新BatchStep・questions件数へのlocator加算・既存削除predicate変更はない。Backup失敗ならlocator削除も0、既存完全成功stepの通常skip/resume契約は保持する。新technical tableは両schemaを含む同一custom dumpに収め、旧成功bundleへのtable/hash追加はしない（SS343）。Production/DDL/独立PT/nativeは未受入。

SSC127/BUG375：同未完了原本の通常resumeで、旧Brokerの真正正常SIGTERM143を非成功UNKNOWNと混同しない。次Broker開始前にSS343§6.17の旧same-invocation停止journalと全終端を確認し、その実snapshot/summaryを保持する。143単独・client0・reset-failed・旧receiptから起動成功を作らず、次fresh Live/Ops/新journal/真正Expiry/全issuer gateを別に検証する。旧step/Backup/原本は不変、今回SKIP・producer receiptは新規とする。

SSC124（SSC117下位、実装前）：Backup失敗profileは成功manifestと排他的なNKCLEANFAIL1を用いる。実nonzero fresh Backup receipt＋実COMMAND_FAILURE/FAILED両stepの全14列を親子で独立再読し、同run/activation/boot/Epoch・同親deadlineへ束縛する。6削除stepの実SKIP/BACKUP_UNAVAILABLE/all0をbegin/commit/readbackし、DELETEやInspector不実行を確認する。Transfer/Artemis/Expiryを失敗理由で省略しない。Profileの完全byte契約・Root子の固定BACKUP readonly観測はSS343 SSC124。旧SUCCESS/既検証SKIPの値は改変しない。独立PTは018/291・292。

SSC124具体化：6固定削除kindのSKIPは新attemptを原子的にINSERTし、ended_at=started_at/BACKUP_UNAVAILABLE/all0をcommit後に同handleで独立再読する。既SUCCESSの有無でALREADY_SUCCESSFULへすり替えない。Transferは既存の実begin/実処理または正規ALREADY_SUCCESSFUL readbackを維持する。親のFAILED pair読取は既完了両handle・保存共通end・同advisory・未handoff・同callbackに限定し、書込み完了用guard（未完了限定）を緩和しない。子のpair guardはbase環境guardのみを渡し、自己再帰しない。既存未完了activeを残したまま別fresh runを生成しない。外部FAILED試験のために旧原本を成功done化・削除することは禁止し、既存同run全起動の正規完了または独立した隔離環境を先行条件にする。

SSC114（code前、SSC113の時刻具体化を補正）：Backup request.startedは各実Backup試行content開始時刻で、run.cutoffではない。明示resumeでは旧requestのDB両試行が同run/cutoff・旧開始時刻・ABANDONEDへ確定し、新両beginが同run/cutoffの新実時刻RUNNINGであることを同advisory/read-only新transactionで完全照合する。その後だけ旧request正規退役→新時刻new-only公開を同M/A/原本/新INVALID・全8終端/intent隔離scope内で許す。異run/未知/片不一致は旧file変更0、旧DBを消去/時刻上書きしない。結果後の参照再証明はpre-begin専用gateとは別で、同owner/thread/advisory/原本のcutoff一致を再読する。

SSC113（code前）：cold inactive BackupのGCで補助GetUnitProcessesが失敗するため、receiptは固定18field manager projectionの前後同値と既存BackupUnitTerminationの真正host cgroup2全終端を組み合わせる。kernel tree存在時は全nested/process照会を維持、不存在は固定host namespaceの前後再保持で証明し、query失敗をemptyにしない。明示同run resumeはM/A・原本・DB・新INVALID・残留intent拒否・全8終端の後だけ、同run/cutoffの固定request保持読取と前後metadata/namespace一致による再利用を許す。freshはnew-only、他request/異run/cutoff/不明は拒否。worker未実行をFAILED/SKIPPEDにしない。

SSC112実装前補足：root Morning外部入口の引数はnoargs（新規）又は厳密な `--resume <canonical非zero UUID>`（明示同run）だけ。runはDBやpermitから自動選択せず、cutoff指定/変更を認めない。既存durable原本を同run/cutoffでresumeし、新activationと同M/A/DB/advisory/current INVALIDを保つ。原本proofは同保持file ownerとcallback thread/lifetimeだけに束縛、終了後/別threadで無効。残留Backup marker/Expiry requestはresumeでもDB/原本変更/stop前に拒否。recoverAbandonedは明示resume時だけ許容し、実未実行をFAILED/SKIPPEDで代用しない。

SSC111実装前補足：Expiryは固定root Unit `schubert-nk-expiry-cleanup.service`からCleanupProcessMainのliteral `--expiry`だけで実行する。noargsのCleanup専用経路と任意argument拒否は維持。親はCleanup/Transfer実完了とArtemis genuine ready後、同run CLEAN_EXPIRY完全handleをcommitし、root request公開後にM/A保持・同advisoryだけを一回handoffする。子は固定私有credentialとrequest、同boot/INVALID Epoch/原本run/activation・Artemis Invocationを確認し、専用Connection/advisory内で実observe→audit stage commit→新transaction完全再読→purgeObserved→terminal commit→新transaction完全再読を行う。未知afterはNULLのまま、DB再読不明を0/10へしない。失敗後health正常・Expiry非criticalのときだけWARNING10を認め、critical/health不明は非成功。ALREADY_SUCCESSFULは既存完全SUCCESS auditとfresh selector対象0の確認が必要で新stage/purgeをしない。全native Unit終端・fresh receipt後だけ親はadvisory再取得/監査再読/原本・current確認→request最後の退役を行う。UNKNOWN/live childでは所有を解放しない。残留Expiry request/part/未知entryは次Morning M内・原本/DB/停止前で隔離する。S1ではgenuine code/Unitの配置と全終端だけを要求し、Expiryの未実行を結果0で代用しない。

SSC107/BUG322（親30分と子起動の非循環化）：`schubert-nk-morning-controller.service`は、親自身が固定Backup/Cleanup/Artemis/Expiry/API/Web/Caddyを順に起動・実終了/ready確認する全体one-shot Unitとする。`Type=oneshot`＋`TimeoutStartSec=30min`を親ExecStart全体のsystemd期限に用い、`Type=simple`の起動完了を親完了へ読み替えない。親Unitからこれら子への`Before=`を設定すると親内から子を同期起動する経路と循環するため付けない。`schubert-nk-morning.target`は親のみを必須起動・親完了後に到達し、各子を並列Wantsしない。各子の既存`After/Requires`は親の明示起動の追加拒否条件であり、親の同run/M/A/step証明を代替しない。start送達UNKNOWN時は30分で勝手にM/Aを正常unwindしない。Unit timeoutではSIGTERM→非成功、`SendSIGKILL=no`のため応答不能processを安全に強制終了できたとは扱わず、marker/current INVALID/全Unit実状態を保全しoperator隔離と次回admission拒否を続ける。単調時計の親budgetと実systemd timeout/起動順・timeout後の保全はPG/PT実測まで未認定。RD/UI差分なし。

SSC106（Backup startの同boot残留保全）：親は同runのM/A/原本・requestを保持したまま、固定Backup Unitへのstart client呼出前にroot private tmpfsの`backup-start.intent`をnew-only・空0600・force/readbackで公開する。不明公開ではstart0件。次回親はM取得後・新run/明示resumeとUnit変更の前にmarker不存在を厳密確認し、残留・IO不明を拒否する。start送達不明/親死亡では自動削除せず、成功retireは今回fresh Invocation/receipt0・全cgroup終端・明示stop後の全終端・同原本/marker inode照合を要する。marker単独は送達/成功証明ではなく、同boot内の後続admissionをfail-closedにする下限である。boot越えはsystemd jobも失われるが、fresh boot/current/run/Unit終端を別途検査する。現時点でparent hard-timeout・実Unit・実backup受入は未達。

SSC105/PG340（停止時点とA所有の整合）：SSC086/100の既定順を正とし、親の前段固定8 stopは真正Morning・連続M/同原本/独立start禁止下で発行する。Aは全stop client実終端＋各Unit終端の後で取得し、そのM/A内で全8をfresh再観測する。従前SSC102の「M/A保持中」はA取得後の後段worker停止に適用し、前段でA取得済みと読み替えない。前段で既得stop attemptがUNKNOWNならMを正常unwindさせず保持・reapする。startがhandleを返す前の不確定は別に保全閉鎖を要し、IOExceptionを一般的な未起動証明としてMを解放しない。A取得後の再観測失敗では変更0・未公開で拒否する。これらのread-only結線だけでINVALID/permit・全親完成にはならない。

BUG315/PG340: `MaintenanceUnitStopClient.stop`のstart呼出後IOException/Runtime/Error/null handleは、呼出前root/policy拒否と違ってspawn不存在を証明できない。原因やraw commandを外へ出さずhandleなし`Attempt.UNKNOWN`とし、親`MorningStopPass`は通常帰還・次stop・変更へ進まない。handleがないため同attempt自身ではreap成功へ遷移できず、実親Unit/cgroup全終端とhard timeout時の別保全を設計・実測するまでR2/正式親受入に算入しない。この保守的な限定修正を、永久待機が安全に運用可能と証明したものと解釈しない。

SSC102/PG319: 親停止clientは真正root Morning/M/A/同原本保持中に固定8 Unit順の完全名だけを `systemctl --system --no-pager --no-ask-password stop` へ渡し、直前にSSC101 policyを毎回再取得する。shell/任意env/commandlineは使わず、非秘密allowlist・stdin close・stdout/stderr discard。client exit0・全owner closeが確認できてもfresh SSC100 Unit/kernel終端とArtemis clean journalは別gate。非0/start不明/最大120秒超/割込/close不明はsuccess不可、未終端clientは自動SIGKILL・destroyせず親がM/Aを保持するopaque unknown handleで隔離しreapする。client結果をboolだけにしない。unit側TimeoutStopSec/親30分上限の確認は別に継続。

SSC101/PG318: 停止命令より前に固定8 Unitそれぞれの実効 Id/LoadState/KillMode/SendSIGKILL を固定systemctl showで再観測する。ASCII/LF・512byte以下・各1回の完全key集合を要求し、固定Id/loaded/control-group/no以外を停止0回で拒否する。実効policy読取成功は停止client実終了・真正cgroup終端・clean journalの代用ではない。Caddy package既定の `SendSIGKILL=yes` は不適合であり、NK専用drop-in `SendSIGKILL=no`/`TimeoutStopSec=30s` を非起動配備し実効値を再照合する。初期未配置Unitを偽Unitで補完しない。

SSC100/PG317: 親停止対象を固定8名 caddy.service→schubert-nk-web.service→schubert-nk-api.service→schubert-nk-cleanup.service→schubert-nk-inbox-inspector.service→schubert-nk-expiry-cleanup.service→schubert-nk-backup.service→artemis.serviceの順に限定する。daemonへInspector oneshot receipt ABIを流用しない。親終端12field（Id/LoadState/ActiveState/SubState/Job/MainPID/ControlPID/Slice/Delegate/ControlGroup/InvocationID/StateChangeTimestampMonotonic）を前後一致で確認し、inactive/dead又はfailed/failed・Job空/PID0だけは必要条件。loaded/system.slice/Delegate=no・真正root/kernel祖先/固定leaf一点MISSING又は存在時の固定ControlGroup非空一致＋全nested process空・全closeを別に満たす。worker Type/Restart/receipt、stop前SendSIGKILL=no、Artemis clean journal、独立start禁止、M/A/原本/INVALIDは別必須。GCでfield履歴が消えることもあるため、projection安定だけを排他にしない。初期未配備をloaded/fake成功へ補完しない。

SSC094/PG311 接続順補足: reboot後morningと05:00 update/rebootを混在させない。新runはM内で専用db-batch admission/session advisory/全3参照不存在確認後に原本startする。resumeは原本照合先行可。固定Caddy→Web→API→Artemis停止と前回backup/Inspector/cleanup/Expiryの全cgroup終端確認、A取得後のfresh再確認、current INVALIDを経て、両backup step beginを同transactionでcommitしてからworker request公開/起動する。PostgreSQLはmorning先頭依存でありこの停止対象ではない。root credential/専用DB契約は343 §6.15。schema/release/BOM未達の限定接続をProduction受入・backup成功・permitへ読み替えない。
SSC104/PG326（親DB所有具体化）：親の`MorningDatabaseSession`は両backup begin同transaction commit確定後だけautoCommit=trueへ戻し、同じ単独Connectionのsession advisoryを保持してCleanup子への一回限り同期handoffを許す。handoff開始前に自己lockの厳密1回所有をDB照会し、明示unlock/残余0を確認してから子callbackを呼び、子の真正全終端をcallerが確認した後に同Connectionへ再取得・照会する。親Session APIはcallback中の再入・別thread・未commit・二重handoffを拒否する。commit/状態切替/DB確認/子終端が失敗・不明ならparent Connectionをcloseして非成功とし、原本やM/Aを勝手に解放しない。これはDB lockの貸出だけであり、両backup現物・子専用DB session/Unit/DELETE成功の証明ではない。
SSC104/PG328（子DB所有具体化）：子Cleanupは自分の固定root Unit contextに結び付く別の非pool `schubert_batch` Connectionを開く。固定loopback `schubert_nk` URL、role/session_user・DB名・nonrecovery・RW/ReadCommitted/autoCommit=trueを照合し、子自身のfresh承認release/BOM/schema検査後にsession advisory71419602を一度取得、同backendの`pg_locks`で所有を確認する。callbackは同期借用Connectionを受け、帰還時も状態/lock/root contextを再確認し、全JDBC owner close完了後にだけ成功値を返す。秘密password copyは消去しJDBC診断を外へ出さない。子Connectionの取得だけでbackup現物・原本・停止Unit・DELETE許可を満たしたとしない。

## 1. 目的・追跡

毎日05:00 JSTの計画停止、package update、OS reboot、DB/config backup、条件付き業務data削除、
transfer/Expiry清掃、依存順起動、失敗時の継続/打切り、二重起動防止と再実行を定める。

- 上位設計: [251_朝バッチ・バックアップ・起動停止設計](../../200_UI/250_運用・非機能/251_朝バッチ・バックアップ・起動停止設計.md)
- 関連RD: AVL-001～AVL-010、OPS-001～OPS-017、BAK-001～BAK-008、BKO-001～BKO-008
- 関連SS: [332_SQL・transaction・lock・削除設計](../330_データ・ファイル/332_SQL・transaction・lock・削除設計.md)、
  [333_大容量結果file・media・Range配信設計](../330_データ・ファイル/333_大容量結果file・media・Range配信設計.md)
- 関連QA/RDF/UIC: QA-013、QA-014、QA-024、QA-029、QA-033、QA-038～QA-040、QA-043、RDFなし、UIC-003

## 2. Unit・step構成

| フェーズ | Unit/step ID | Timeout | 成功・失敗の後続 |
|---|---|---:|---|
| 05:00開始 | `schubert-nk-maintenance.timer` | - | `maintenance.service`を1回起動 |
| 停止/update | `schubert-nk-maintenance.service` | 60min | 更新警告はreboot継続、安全性判定失敗はreboot/公開停止 |
| Reboot後束ね | `schubert-nk-morning.target` | - | 下記unitを順序起動 |
| DB | distribution PostgreSQL unit | 120s | 失敗は後続全停止 |
| Backup | `schubert-nk-backup.service` / `BACKUP_DB`,`BACKUP_CONFIG` | 30min | 失敗は業務data削除だけskip、起動続行 |
| Cleanup | `schubert-nk-cleanup.service` / `CLEAN_*` | 30min | 個別warningは継続、root/DB safety異常は後続停止 |
| Broker | `artemis.service` | 120s | 失敗はAPI以降停止 |
| Expiry | `schubert-nk-expiry-cleanup.service` | 10min | critical/health異常はAPI以降停止 |
| API | `schubert-nk-api.service` | 120s | 失敗はWeb/Caddy停止 |
| Web | `schubert-nk-web.service` | 120s | 失敗はCaddy停止 |
| 公開 | `caddy.service`＋smoke | 30s | 失敗は公開停止、運用介入 |

## 3. Run identity・排他

SSC055/PG163（先行898cc267）: 親step履歴は331 §8.3のBatchRunRepository。root原本/OS lock/子終端を確認したcallerがbegin/finishとcommitを所有する。runとstep時刻を分け、当日非backup成功済みだけ新attempt SKIPPED、backup2stepは毎回実行する。残存RUNNINGは明示同run回復時だけABANDONED相当FAILED、別run/不明root/99超/時計逆転は保全拒否。今回attempt件数とrun累積を混同しない。各step終了値の完全一致再試行だけ冪等にし、未確認child/backup/cleanupをSUCCESSへ補完しない。詳細型・固定診断・transaction・24PTは331 §8.3/017021～024を正とする。

SSC-055/PG-D-158: 固定namespaceの原本file lifecycleは343 §6.15。親はOS flockの内側でscopeを開き、start成功後だけ停止/updateへ進み、reboot後resumeで同activation/cutoffと前回完了の有無を区別する。completeには実子終端・許容morning終端・step永続記録を先に確認する。file側の全graph検証をDB legacy ID非衝突/親の成功証明へ代用しない。

SSC-055/PG-D-156（先行b6b5f0f6）: run_id/cutoffの唯一の原本は343 §6.13のroot永続anchor。DBが停止してもreboot後に同じbyteを復元できる。各保守起動/明示resumeには別activation UUIDを用い、completionはそのactivationにだけ対応する。過去completionを新activationの成功として使わない。原本→activation begin→activeをdurable公開するまでは停止/update/rebootを行わず、親の許容morning終端を確認してcompletion→active消去をdurable確定する。backup失敗時の削除skip/起動継続をこの追加metadataで禁止しない。途中失敗/不明完了はactiveと原本を保全する。原本fileの完成だけで親全体・永続step・GCを実装済みにしない。

SSC-049/PG-D-147: root controllerのfile adapterは実効UID0、/runと/run/schubert-nkのroot:root0755・ACLなし・RW tmpfs、maintenance.lockのroot:root0600・通常file・nlink1・size0・同deviceを検証する。NOFOLLOWで各directoryとentryを保持してからflockを取得し、獲得直後/処理後に固定pathを再openして同dev/ino・権限・ACLを確認する。元の保持能力は全保守callback終了まで存続し、entry/root close失敗で成功にしない。競合はcallback0回でDUPLICATE、admission/IOは固定診断で失敗。root以外の親、ACL追加、別FS、symlink/hardlink、未知属性、inode交換を受理せず、adapter自身が作成/chmod/unlinkして修復しない。特権rootによる保守中の置換は運用禁止であり検証だけで敵対rootを封じ込めたとはしない。

- Maintenance全体の`run_id`はUUID、`business_date`は開始時点のJST日付、`run_started_at`はUTC `Instant`で固定。
- OS排他は`/run/schubert-nk/maintenance.lock`を`flock(LOCK_EX|LOCK_NB)`。DB接続後は固定
  `pg_try_advisory_lock(71419602)`も取得。両方を持つprocessだけcleanup/morningを実行。
- Lock取得失敗は何も停止/削除せずexit 20、SYSTEM/BATCH alert。Lock file本体を手動削除して解除しない。
- 各stepは`batch_runs`へRUNNINGをINSERTし、成功/WARNING/FAILED/SKIPPEDで完了。Process異常のRUNNING残留は
  次回起動時にABANDONED相当のFAILEDとし、同じrun IDの新attemptで再開。

## 4. 05:00計画停止・update・reboot

SSC-049/PG-D-146のOS排他部品: LinuxFileLockは親が既に型/所有/ACL/namespaceを検証して保持したlock inodeだけを独立O_RDONLY|O_CLOEXECでopenし、flock(LOCK_EX|LOCK_NB)成功後だけcallbackを呼ぶ。EWOULDBLOCKはcallback0回の競合結果、他errno/open/close失敗は非成功。callback終了・例外時も全FDを閉じ、close完了前に成功結果を返さない。FDは複製/公開せずcloseでlockを解除、既存lockfileの削除/作成/内容変更をしない。対象はlocal /runのOS lockでありNFS/SMBの異なる意味へ拡張しない。実util-linux flockと相互排他をPTで検証するが、root配布/親inactive/実backup/DB lock引渡しを本部品だけで実装済みとしない。

### 4.1 実行順

1. OS lock取得、run ID生成、host/app/schema/version、disk、Queue/DLQ、未処理job、active session件数を記録。
2. Caddyをmaintenance responseへ切替えるか停止し、public 55160の新規業務requestを遮断。
3. WebへSIGTERM。HTTP新要求を止め、MQ待機を最大30秒で完了/エラー化。
4. APIへSIGTERM。Consumer receive停止、処理中DB/JMS transactionを最大60秒でcommitまたはrollback/requeue。
5. Artemis停止、journal flushとclean stopをunit resultで確認。
6. PostgreSQL fast shutdown、`pg_isready`不応答とunit inactiveを確認。
7. Package metadata更新→noninteractive upgrade、実行前後のpackage list/kernel/reboot-requiredを記録。
8. Package manager lock、dpkg未完了、filesystem、boot partition、kernel/initramfsの安全性を検査。
9. Reboot安全なら`systemctl reboot`。安全でなければpublicを開けずexit 30で運用待ち。

Update command自体の非0はWARNINGとし、dpkg状態とboot可否が正常ならreboot/復旧を続行する。
自動`kill -9`を使わず、stop timeoutはunit FAILED・証跡保存・public停止とし、強制終了は353の運用判定に委ねる。

### 4.2 Reboot不成立のwatch

Maintenance開始から60分でreboot完了markerが更新されない場合、外部監視はcriticalとする。
同一server内監視だけでreboot hangを検出できると仮定しない。

## 5. Reboot後の起動順・gate

SSC093/PG310（code着手前）: root親の実行主体は固定schubert-nk-morning-controller.serviceとし、RootStartupContextのMORNINGだけで実UID0/kernel proc/PID1/boot/自己PID-start/固定MainPID-Invocation-ControlGroupを認証する。M獲得後/A獲得後/host観測前/帰還前にも再確認する。API/Web service proof enum・秘密配布は不変更。cold/post-stop backup Unitは既存18fieldに加え固定Id/Slice/Delegate/ControlGroupを別観測し、Id一致/Slice=system.slice/Delegate=no/非空groupが固定/system.slice/schubert-nk-backup.service一致を要求する。真正host /proc/1/rootからsys/fs/cgroup/system.sliceの全NOFOLLOW祖先を保持、rootUID/GID・directory0555/0755・ACLなし・dev/inoとsysfs/cgroup2を検査する。固定leaf open一点のMISSINGだけ不存在として受け、祖先欠落/権限/一般IO/link/close不明は拒否。leaf存在時は既存GetUnitProcesses全process空＋Unit前後安定を必要とする。root context・実効配置・祖先identity・Unitを前後照合し全FD close完了後だけquiescenceを返す。これはfresh Invocation/receipt0/実backup成功を証明しない。固定UnitのDelegate=no/zeroCaps/NoNewPrivileges/ProtectControlGroupsと親以外のstart/restart/migration禁止は配備・運用上の別必須条件で、敵対rootを封じ込める保証ではない。親側は開始client実終端→fresh worker全cgroup終端→明示stop/全終端→request retireまで連続M/A内、unknownでは排他/sourceを通常unwindしない。

SSC-086（起動排他の内部具体化）: root親は従来のmaintenance.lock（M）を保守callback全体で保持する。別root所有`/run/schubert-nk/startup-admission.lock`（A）は起動観測から子readyまでの短期排他とする。変更側はM取得→固定対象停止→A取得→全対象のInvocation/cgroup終端再確認→旧起動許可失効→変更/必要保守→同boot/Broker/現在runに束縛した許可確定→A解放→固定Unit起動の順。A取得前の停止結果を再利用しない。再確認失敗は変更0回・非公開、親は既存停止手順へ戻すか拒否する。設定/release/root/Broker/鍵の変更も同規則を必須とする。起動側はAだけを取得し、取得前に業務DB/JMS/fileを開始しない。現許可のread-only検査と必要gateを終えて同OFDを子readyまで保持する。Mを起動側へ引き渡さず、M保持中の親による起動/readiness待ちとの循環を作らない。A自体は保守完了や起動順の証明ではなく、失効/確定済み現許可も必須。未実装gateは非成功のまま。

```text
PostgreSQL readiness
 -> BACKUP_DB + BACKUP_CONFIG
 -> CLEAN_BUSINESS   (backup successのみ、failureはSKIPPED)
 -> CLEAN_TECHNICAL  (backup successのみ)
 -> CLEAN_TRANSFER   (backup成否にかかわらず、root safety必須)
 -> Artemis readiness
 -> CLEAN_EXPIRY
 -> API readiness
 -> Web readiness
 -> Caddy validate/start
 -> loopback/public smoke
```

Backup serviceがFAILEDでもmorning target自体はcleanupへ進み、cleanupがDBの当日成功rowを見て
BUSINESS/TECHNICALをSKIPPEDにする。Transferは独立実行。Transfer rootの実体/権限/重複異常だけは
Artemis以降を開始しない。

### 5.1 許可発行の実観測集合（SSC108、PG379、実装前）

SSC134：十段CONFIG根拠は親の実bundle完成判定の終端とする。新規成功・実成功再用・真正worker非0のすべてで親操作を呼び、非0時は同owner/同begin/request/原本/INVALID/元期限/明示stop/全終端を確認して完成拒否と両FAILED記録を確定、archive公開なし。commit後の独立現在pair全14列、再用時元SUCCESS全14列を保持する。未知/未呼出し/読戻し不明はCONFIG closureを作れずpermit不可。local0は完成判定操作が正常終端した事実だけを表し、business FAILEDを成功化しない。具体byte/参照/hash/非任意証拠の契約はSS343§6.17。六実削除SKIP・Transfer/Expiry実続行・全必須工程後の起動継続は不変更。

SSC115（実装前、2026-09-30）：親の実Backup結果callbackは正常fresh非0/明示stop/全終端の後だけ既存両beginを固定COMMAND_FAILUREで原子的FAILED確定・独立再読する。worker試行済bundle不成立の両開始済stepを記録するのであり未実行featureをFAILEDに代用しない。archive/MANIFEST生成や過去成功の採用は行わない。原本/current/request/終端再証明→request→最後にintent退役の順はSUCCESSと共通。不明/timeout/signal/結果commit不明は隔離を維持。後続未結線の途中Mainは30のままで起動成功/permitを偽装しない。BUSINESS/TECHNICAL SKIPPEDと独立Transfer/Expiryは実後続工程で記録・実行する。

`roots_sha256`/`prestart_steps_sha256`はSS343§6.17のcanonical実観測のSHA-256とする。親は同一M/A、原本activation、DB session、現boot、新INVALID Epochを保持し、必要な全10stepの完全attemptとcommit後readbackを収集する。原本・root・currentの安全条件違反、UNKNOWN、欠落、未実行はdigest作成/許可発行を拒否する。

Backupは毎回真正workerのfresh Invocationと全cgroup終端を観測する。正常exit0は実archive/config/credential/manifest/公開後検証・DB両step SUCCESSまで成立して初めてSUCCESS。正常非0 exit-codeは新Invocation/start/exit時刻・前bus/全kernel/後bus一致を確認してFAILEDへ進める。signal/timeout/不明を正常FAILEDへ変換しない。FAILED時は実DB両stepの記録/再読とBUSINESS/TECHNICAL削除のBACKUP_UNAVAILABLE SKIPPEDを要求するが、Transfer/Expiry及び他必須gateは省略しない。起動継続は全必須保守が実際に完了した場合だけ許可する。

Backup固定startの後は同じ親30分budget内でfresh worker結果→明示stop→fresh全終端→実artifact/両step結果確定→原本/current/request再照合→同request退役→最後に同inode marker退役の順とする。いずれか不明ならmarkerを残しM/Aの正常unwindを禁止する。安全不正は親停止、真正workerの業務失敗とは別分類。S1だけ実証しても全Morningのexit0/10、StartupPermitを発行しない。

## 6. DB backup

### 6.1 作成

SSC068/PG186: step2の低位0700/new-only保持child能力は333§7.6。既存0750日付directory能力を流用せず、専用backup主体が生成しcallerが入場/同device/metadata/namespaceを確認する。private能力の単体成功は実archive生成・親排他・worker終端を代替しない。

1. Backup rootをabsolute・real pathで検証し、`/`、home、asset/transfer/log/Artemis root自体または配下を拒否。
2. `yyyyMMdd-HHmmss-<runId>.part`をmode 0700でCREATE_NEW。同一mountの確定先とする。
3. Systemd credentialで渡された`.pgpass`を`PGPASSFILE`へ指定し、passwordをcommand line/environment実値へ出さない。
4. QA-043/UIC-003承認済みの`schubert-backup` OS user固定unitから、`schubert_backup`専用credentialで
   `pg_dump --format=custom --no-owner --no-privileges --schema=schubert --schema=schubert_web_session --schema=schubert_meta --file=<part>/schubert_nk.dump schubert_nk`
   を実行する。`schubert_batch` credentialでdumpしない。
5. Exit 0、file >0 byte、`pg_restore --list`成功、dump SHA-256を検証。
6. DB/app/schema/OS/JDK/PG/Artemis version、開始/終了、file size/hashを`MANIFEST.json`へ記録。Secretなし。

SSC090/PG305: systemd runtime credential `backup-pgpass`は固定名で既存保持inode/ACL readerを使い、最大65536byteのcaller-owned raw byteとして読む。配布root/fileの前後属性・同device・closeを検証する。libpqはgroup/world permission bitのあるpassword fileを無視するため、root ACL0440材料を直接PGPASSFILEへ渡さない。専用backup Unitのprivate tmpfs0700内にCREATE_NEW0600の専用コピーを生成し、borrowed original FDを子に保持して渡す。所有byteは全終了で消去し、全子終端確認後のみcopy消去・unlink・directory sync。不確定終端/closeは非成功・保全。password実値をenv/argv/logへ出さず、backup-pgpassをAPI/Web固定5材料へ追加しない。専用OS/DB主体・実archive/manifest/DB両step/世代管理の既定gateは維持する。

SSC091/BUG271: 保持parent FDを子argvから読む工具は、取得済全子へTERMを要求した後で全子の実終端まで待つ2passとする。TERM/5秒timeout/割込/unknownを終端証明へしない。割込は待機中記録し全終端後にflag復元、unknown identityも終端後だけ帰還する。終端不明の間はborrowed callback/FD/M・A/partを保持し、通常例外unwind・FD再利用・次job・copy消去をしない。単調30分は元の非成功判定を確定させるが能力解放の根拠ではなく、固定Unit hard timeoutと全cgroup停止/親再起動barrierは別必須。独自SIGKILLなし。startPipeline不成立は取得されない子の実終端をJDK内部処理で補完せず、filename stdin未送信のまま固定worker callback内隔離・親全cgroup確認へ接続する。このcaller接続が未達なら全例外経路/backup完成とは認定しない。

### 6.2 Config・credential backup

SSC121・BUG366：静的復旧config固定allowlistはcommon.yml/api.yml/web.yml/batch.yml/api.env/web.env/backup-profile.json/inbox-inspector.envの8名。暗号credential固定allowlistはdb-api/db-web/db-batch/db-migration/backup-pgpass/mq-api/mq-web/mq-maintenance/mq-ops/api-context-aes-current/api-inbox-response-aes-current/operation-hmac-current/web-session-aes-current/web-revoke-aes-current/web-log-aes-current/artemis-users/db-inbox-inspectorの17名。後者をRootがage暗号化して保存し、普通Backup workerへ生secretを渡さない。runtime同run Inspector env/request/ownerはarchive対象外。過去成功bundleのcatalog/hash/DBを追加名へ書換えず、通常resumeは元成功を実再検証し、新生成時だけ現行全role catalogを採用する。

SSC092/PG309（実装前）: 固定backup Unitの入力はroot親がM/A/原本/停止/current INVALID/backup両step begin commit後に作る非秘密requestだけ。format version/run UUID/内容生成開始時刻から既存manifest規則で出力名を導出し、任意path/command/UID/credential名/DBattemptを受け付けない。new-only root600 requestを専用0700/run namespaceへ公開しLoadCredentialでworkerへ渡す。workerは固定NSS・自己Unit/kernel・runtime・backup root admission後new-only700 part/600dump→Productionコピー/実dump・list→全close/廃棄成功のみexit0。旧part再利用・DB更新なし。親はfresh Invocation/receipt0/全cgroup空/前後安定を確認するまでM/Aと隔離を保持し、起動clientのexitだけを成功にしない。RemainAfterExit=yes/Restart=no/KillMode=control-group/SendSIGKILL=no、親回収後の明示stop/終端再確認まで旧requestをretireしない。

SSC090/091 PG307/308補足: startPipeline呼出のIOException/Runtime/Errorは一部spawn不明なので、固定one-shot Unit内でborrowed callbackを非復帰隔離する。builder生成と開始直前割込はspawn前に拒否できる。隔離中の割込はclearしてparkを継続し、Unit全cgroup停止を親が確認するまでM/A/partを保全する。外部process停止後の元例外rethrowは保証しない。Production copyは新UUID.part0600を保持し、原本namespace照合/readback/heap消去を済ませてから固定dumpへ渡す。全terminal-positive return後のみ全zero書込/force/close/readback/元inode-name再照合/unlink/dirsync。不確定unlink後の復元再作成なし。

- `/etc/schubert-nk`の非秘密configはroot所有のtar、path traversal/symlinkを入れず`config.tar`へ固定。
- Credential directoryはrootが専用allowlistだけ読み、recovery用公開keyのみをhostに置き、
  `age` recipient暗号化の`credentials.tar.age`へする。復号private keyは当該server/backupに置かない。
- Archive中のfilename/permission一覧は機密扱いとし、暗号文本だけのhash/sizeをmanifestへ出す。

`age`の導入versionとrecipient fingerprintはrelease/config manifestへ記録する。別暗号工具への交換は
backup/restore手順の変更・rehearsalなしに行わない。

### 6.3 確定・7世代

SSC133補足（PG/PT内部具体化、2026-10-01、実装前）：Morningは真正backup完了後/Cleanup前に、保持backup root、同Root/M/A/原本/借用DB/元30分の下で世代を観測する。新規両SUCCESS時だけ正規directory名のmanifest/全4file inode・hash・ACL・完全DB成功pairを検証し古い名前順の超過分を削除、現在bundleが最新保持集合に入らなければ拒否する。既存成功再利用/FAILEDは削除呼出し0、一覧を前後比較し未観測成功数は未観測と記録。未知名/.part/通常directoryでないもの/manifest・archive不整合/既知非成功pairは保護理由を保存する。SQL/close/owner/未知Throwableは不確定を正常warningへ変換せず保全。削除直前に全bundle/DBを再照合し保持childとnameのdev/ino/所有/policyを確認、固定3archive→MANIFESTの順に各保持entry属性を再確認してunlink+sync、実emptyとname同inode確認後に既存removeEmptyChild+親sync。partial削除/再読失敗は完了にせず、後続で同世代を自動的に再削除しない。末段まで借用rootを閉じず、一覧・全保持bundle・root identity・原本を再照合する。外部仕様/7世代/失敗保護/既存低位APIを変更しない。

1. 全fileのfsync、directory fsync後、`.part`をsuffixなし確定directoryへatomic rename。
2. 確定後にSHA-256を再照合し、`batch_runs`のDB/config両stepをSUCCESS。一方失敗は当日backup不成立。
3. 新規backup成功後だけ、正規名・通常directoryの成功backupを古い順に並べ、8世代目以降を削除。
4. Unknown name、symlink、manifest不整合、`.part`は自動世代削除せずwarning。既存7世代をbackup失敗時に削除しない。

### 6.4 MANIFEST.jsonの値・byte契約（SSC058/PG165）

先行8a606fc7。以下はmanifest内容の契約であり、実artifact検証・DB成功・root/OS/子終端の代用品ではない。

- Production型は .batch.backup.BackupFileDigest(size,sha256)、BackupVersions(host,app,schema,os,jdk,postgresql,artemis,age)、BackupManifest(databaseStep,configurationStep,startedAt,contentFinishedAt,versions,recipientSha256,dump,configuration,credentials)。file byte codecは .batch.file.BackupManifestCodec.encode/decode。record accessor、計数/名前導出、全内部parse/renderを017033～036/BAT178～193で追跡する。
- 両stepは既存BatchStepAttemptの完全handle（id/run/cutoff/step/attempt/startedAt/skipped）。databaseStepはBACKUP_DB、configurationStepはBACKUP_CONFIG、両skipped=false、idは相異なる、run/cutoffは同一。attempt番号・開始時刻は同一である必要はなく、各完全handleを記録して取り違えを拒否する。DBの実在/状態・同一bundleへの永続bindingは後続で別検証する。
- startedAtは内容生成の開始、contentFinishedAtはdump/list/tar/ageの内容生成終了の観測時刻。両UTC0001～9999・µs、startedAt>=両step.startedAt、contentFinishedAt>=startedAt。fsync/atomic確定/再hash後の最終step.ended_atとは区別する。名前に使うstartedAtのJST年は0001～9999。
- directoryNameはstartedAtのAsia/Tokyo yyyyMMdd-HHmmss＋ハイフン＋canonical run UUID。µsはmanifestに保持し、directory名だけ既定の秒表示。既存同名/partとの衝突は後続CREATE_NEWで拒否し、上書きやsuffix推測をしない。
- 3file名は schubert_nk.dump / config.tar / credentials.tar.age の固定集合。各sizeは正long、SHA256はlowercase64hex、3size合計はlong overflowしない。configurationBytesは後2fileの合計、totalBytesは全3file。manifest自身のsize/hashを内部へ循環記載しない。recipientSha256もlowercase64hexで、元public recipientのfingerprintをcallerが独立算出する。
- host/app/os/jdk/postgresql/artemis/ageは各ASCII1～128byte、先頭英数字・後続英数字または . _ + - の非秘密release token。schemaは001～999の3桁。任意command出力/path/credential/JSON/制御文字を受け入れず、versionが実環境と一致するかは生成側で別確認する。public診断toStringは値全体をredactする。
- 全nullはconstructor/API境界で拒否し不変条件を先に確立する。型/範囲/format不正は固定IllegalArgumentException、NULLはnull契約違反。decodeでJDK/parseのraw入力をcause/suppressedへ出さない。入力byte/返却byteのmutable所有を共有せず、同一不変modelの並行encodeを許す。
- Canonical JSONは下記順・key名と固定database名、ASCIIのみ、余白なし1行＋末尾LF1つ、最大4096byte。数値は符号/先頭0なし10進（size/id/attemptは正）。UUIDはlowercase36、時刻は必ずyyyy-MM-ddTHH:mm:ss.ffffffZ。意味上同じでもkey順違い/空白/CRLF/BOM/escape/大文字hash/省略µs/指数数値/unknown/duplicate/欠落/NULL/末尾追加は拒否。全string値が上記ASCII許可集合に収まるためescapeを生成しない。
- decodeは固定schema全fieldを構築し、再encodeとのbyte完全一致も確認する。dateの自動補正/別表現を許可しない。独立goldenをProduction encodeで生成しない。
- 形式: {"format":"NKBACKUP1","database":"schubert_nk","runId":"<UUID>","cutoff":"<UTC6>","startedAt":"<UTC6>","contentFinishedAt":"<UTC6>","databaseStep":{"id":<N12>,"attempt":<N2>,"startedAt":"<UTC6>"},"configurationStep":{"id":<N12>,"attempt":<N2>,"startedAt":"<UTC6>"},"versions":{"host":"<token>","app":"<token>","schema":"<N3>","os":"<token>","jdk":"<token>","postgresql":"<token>","artemis":"<token>","age":"<token>"},"recipientSha256":"<hex64>","files":{"schubert_nk.dump":{"size":<positive long>,"sha256":"<hex64>"},"config.tar":{"size":<positive long>,"sha256":"<hex64>"},"credentials.tar.age":{"size":<positive long>,"sha256":"<hex64>"}}} LF
- 制約として、この型は「申告された観測値」が整合することだけを保証する。actual dump/list/age/restore・3file metadata/hash・全file集合・原本/DB両stepへの信頼binding・成功後7世代削除は別必須。archive平文/秘密key、任意path、未検証claimからSUCCESSを生成しない。

### 6.5 実backup artifactのread-only検証（SSC059/PG166）

先行4da9e96b。BackupArtifactVerifierは「信頼されたmanifest申告値と現存byteの一致」を検証する。生成/復元/age実行・fsync/rename・DB成功・rootのmanifest binding・7世代管理は別必須であり、本部品成功で補完しない。

- 親rootはOS排他とbackup rootの設定/非重複/realpath/FS権限・durability能力を別途確認してから、保持したOwnedTransferDirectory、専用schubert-backupのUID/GIDを渡す。UID/GIDは1～unsigned32上限、実効UID0。rootを閉じたり任意pathを再解決せず借用する。NASのサーバ側ACL/fsync保証を単なるUnix mode/読取成功で証明したことにしない。
- verify(BackupManifest)はdirectoryNameで既存子だけをNOFOLLOWで保持する。backup rootと子は専用backup UID/GID・0700・directory/nlink>=2、RW・ACLなし。子は親と同device。子の全entryはMANIFEST.json/schubert_nk.dump/config.tar/credentials.tar.ageの正確な4件（重複/NULL/未知/不足を拒否）。part名や別runへfallbackしない。
- dumpは専用backup UID/GID・0600、config.tar/credentials.tar.age/MANIFEST.jsonはroot:root0600、regular/nlink1。全fileは子と同deviceで、manifest3fileの正sizeと一致する。MANIFEST.jsonは341 6.4のcanonical encode長とbyte完全一致。親rootが最終manifestを作成する責務をここで固定するが、格納先親がbackup主体所有であるため別の信頼bindingなしにmanifest自身を信頼しない。
- 各保持inodeのmode/uid/gid/nlink/size/dev/ino/mtime/ctime・ACLをIO前後に照合。読取り前後のchannel.sizeを別観測し、最終EOFも確認する。65536byte bufferでstreaming SHA256、残長を超えて読み進めず0byte進捗も固定失敗。fileの途中短縮/過長/変更/同名差替えを成功にしない。MANIFESTの期待byte/hashはcallerの信頼manifest由来だがPTの期待値はProduction codecから生成しない。
- 全4file読取後、全entryを名前から再保持して元snapshotと照合し、正確な全file集合と子snapshot・親から再openした子identity・借用root snapshotを再確認。byte内容を変えず通常readによるatime更新は比較しない。敵対rootや検査後の第三者変更をこの一回の検査で封じ込めたとは主張せず、親排他/actor停止・最終使用時再検証を維持する。
- 全操作はinstance内直列化し、所有child/entry/channelを閉じた後だけ実測MANIFESTのBackupFileDigestを返す。path/FD/channel/ファイル集合やarchive内容を結果へ公開しない。既存fileの作成/chmod/chown/書込/unlink/sync・root closeをしない。
- 単調時計30分と割込を各IO境界/読取loop前後・最終帰還前で確認する。期限以上/割込は固定非成功・flag保持。blocking OS readをJava協調検査で強制中断できるとはしない。clock引算は既存30分契約同様wrapを許し、逆転は拒否する。
- nullは境界/invariant契約違反として拒否しNPEを正常化しない。IO/既知不正状態/crypt provider失敗は固定StorageIoException、raw path/bytes/cause/suppressedを出さない。未知Runtime/Errorのidentityを保持し、cleanup IO失敗を添える場合も固定診断だけ。bufferは全終了で消去し、close失敗を成功へ算入しない。
- Production class/内部port・snapshot/安全close helperは.file.BackupArtifactVerifierの責務内、全public/private methodを017038/039/PT-BAT-194～209へ追跡する。package/module依存は既存Storage/Batch/Java標準のまま。PTは実Linux保持inode・公開合成byteと非特権metadata adapterを区別し、実root配布/NAS/IT/STの完了を宣言しない。

### 6.6 root manifestとbackup両stepの原子的確定（SSC061/PG168）

BUG193/YKT152の例外優先規則追補（修正前f030f647）: rollback/autoCommit復元が宣言SQLだけでなく未知Runtime/NPE/Errorを投げた場合も、先行primaryが未知RuntimeまたはErrorなら同一性を保持し、secondaryは固定失敗へredactしてsuppressed1件とする（同じthrowable再送でもself-suppressionしない）。先行primaryが既知SQL/Repository/停止理由なら、未知cleanup Runtime/Error自身は同一性を保って非正常に伝播させ、既知cleanupだけを固定DB失敗へ集約する。いずれも復元完了/commit成功と扱わずconnectionを破棄する。同じborrowed transaction規則のStepCleanupServiceにも適用し、固定Infrastructure変換を正本とする別境界はその契約で非正常化を確認する。

先行26fb3bad。root生成manifestを信頼binding recordとして扱うが、単なるJava値の受領は信頼確立ではない。rootが内容生成成功・実byte照合後にCREATE_NEW/0600でmanifestを生成し、writerを全close、fsync/atomic確定/再hashすること、読取側がuid0/gid0/0600/nlink1/ACLなし・保持inode/前後属性・canonical byte・namespace・原本run/cutoffを確認することが別の必須条件。backup user作成inodeのchownで真正化しない。低権限者が親directoryを変更してもroot所有file内容は改変できず、別の真正manifestへの入替えは全handle/name/hash照合で拒否、同一真正bundleの再使用だけ冪等である。root侵害や保守中の管理者変更を本方式が封じ込めるとはしない。PG166の期待値照合だけで生成元を証明せず、生成・信頼readerは後続実装する。

- Production .repository.BackupStepRepositoryは借用親Connection、.backup.BackupCommitServiceは同借用Connectionのtransaction境界を所有する。原本/OS排他/停止/実artifactの継続保全はcaller、DB専用backup credentialは使わず既存schubert_batchを使う。新table/FK/DDL/grantは追加せずV001～020不変、400日/7世代保持不変更。
- inspect(manifest,observedAt)は親explicit read-write READ_COMMITTED transaction、自己DB advisory・run identityをRunReferenceRepositoryで前後検査し、2idを昇順FOR UPDATEで読取る。query timeout5秒。全14列id/run_id/business_date/step/attempt/started_at/ended_at/status/target_count/success_count/failure_count/byte_count/error_code/error_summaryの所有ResultSet/Statementを閉じるまで返さない。WHERE id INの行を信用せずmanifest完全handle2個と各列を照合し、欠落/余分/重複/NULL/未知/取り違えを拒否する。
- 観測時刻はUTC0001～9999/µsでcontentFinishedAt以上。DB/CONFIGの両方RUNNINGだけはended=NULL、4counts0、error2列NULLを要しOptional.empty（未完了）。両SUCCESSだけは共通ended>=contentFinishedAtかつ<=observedAt、µs、error2列NULLを要す。DB target=success=1/failure0/bytes=dump.size、CONFIG target=success=2/failure0/bytes=configurationBytes。これは対象file数でmanifest自体を数えない。片SUCCESS・異なるended・WARNING/FAILED/SKIPPED/未知status・別run/pair/handle・count不正を未完了から補完せず保全拒否。
- complete(manifest,endedAt)はinspectを先に行い、両SUCCESSなら保存済共通endedだけを返し現在時刻で書き換えない。両RUNNINGならBatchRunRepository.finishでDB→CONFIGの順に同一endedAt/SUCCESS/NONEと上記独立count/byteを記録し、再inspectで両確定値の一致を確認する。Repositoryはcommit/rollback/connection closeをしない。途中失敗は呼出側が全rollback、片方だけcommit禁止。
- BackupCommitService.complete(connection,manifest,endedAt)は入口autoCommit=true/read-write/READ_COMMITTEDを要求し、割込を前後確認、setAutoCommit(false)→Repository complete→commit→setAutoCommit(true)→割込再確認→保存end返却。既知SQL/Repository failureは固定BatchRepositoryException。transaction処理の失敗はrollback成功後だけautoCommitを復元し、rollback失敗なら復元しない。commit不明は成功にしないが次回同manifestのinspectで永続両SUCCESSを再読できる。後commitの復元/割込失敗も今回返却は非成功、保存済み結果を上書きしない。全障害後のconnection破棄はcaller必須。
- 未知Runtime/NPE/Errorを正常扱いせずprimary identityを保持、既知cleanup SQLのsuppressedは固定例外。input/cause/SQL/manifest値を診断へ出さない。全API nullを境界で拒否、Connectionはcaller単独所有、異なるconnectionの並行呼出しだけを許す。
- 017041～044/BAT210～225で独立合成manifest/SQL後条件、borrowed read/complete・全列/全JDBC位置/NULL/close/割込/commit不明/rollback/2connection・同ID再試行を検証する。new部品の全line/method/class/branch100%、全既存PT/static/traceを再実行。成功rowだけでcleanup許可せず、生成/信頼reader/最新真正bundle選択/親全体/7世代/実NK CHR/IT/STは未完了。

### 6.7 root MANIFESTの保持inode読取り（SSC062/PG169）

SSC063/PG170・BUG195/YKT154: 本節/§6.5/§7.4のresource compoundはSS333冒頭の明示close優先順位を適用する。同一unknownのbody/close再送をself-suppressionで置換しない。既知IOとunknown cleanup/fatalを区別し、byte消去・全所有close・元unknown同一性を維持する。IO/commandの正常条件や既存expectedは変更しない。

先行c2da887a。BackupManifestReaderは§6.6のroot生成済MANIFESTを、callerの原本両stepと単一の正規directoryへ束縛して読む。root CREATE_NEW/0600生成・writer close/fsync/atomic/実体検証の正当な運用が信頼前提であり、任意root作成fileを暗号学的に認証する機構ではない。専用backup user所有directory上のroot所有fileは低権限者が内容を書けないことを利用し、別真正manifest入替えをfull handle/name照合で拒否する。

- Production .file.BackupManifestReader、read(String directoryName,BatchStepAttempt databaseStep,BatchStepAttempt configurationStep)→不変BackupManifest。callerはroot原本から両完全handleを供給し、backup rootの設定/ancestor/realpath/FS durability・OS排他・account UID/GIDを既定gateで確認して保持rootを借用させる。nameはASCII8桁日付-6桁時分秒-lowercase canonical UUID形の1segmentだけ、part/絶対/相対区切り/別名/NULLを拒否。最終的にmanifest.directoryNameと完全一致を要す。新たな任意path探索や最新選択は行わない。
- 実効UID0。root/子directoryは専用backup UID/GID（1～unsigned32）0700・nlink>=2・size>=0、RW/ACLなし、子と親同device。固定MANIFEST.jsonはroot:root0600のregular/nlink1・同device・size1～4096、ACLなし・RW。mode/uid/gid/nlink/size/dev/ino/mtime/ctimeをtypedで全取得し、欠落/null/誤型/不一致は固定拒否する。NASの追加保証はcaller責務のまま。
- 保持entryからbounded読み、前後channel.sizeと実read数・buffer進捗を照合し、全size読了後に1byte EOF(-1、position0)を別確認する。zero/短縮/過長/進捗矛盾は失敗、再試行で勝手に補完しない。前後inode全属性を照合し、同名entryを再保持、子directoryとrootから再保持した子、最後にrootを照合する。read atimeは比較に含めない。
- canonical decodeは既存§6.4 codecを利用し、database/configuration完全handleとnameをcaller値へ照合。未来のDB SUCCESS、現存3archiveのhash/妥当性、7世代、子終端、親完了は推定しない。次段は§6.5でこの取得値と実3file/canonical bytesを再照合し、§6.6でDB pairを結合する。読取り後の第三者変更を永続防止する保証ではなく、親排他/actor停止/使用時の再検証を維持する。
- 全操作はinstance内直列化、所有child/entry/channelだけをcloseしてから不変値を返す。root close/作成/chmod/chown/書込/unlink/fsyncはしない。単調30分/割込をIO境界と返却直前まで検査し、clock内に届く割込も取りこぼさずflagを保持する。blocking OS readの即時強制中断を保証しない。
- nullは契約違反、NPEを正常化しない。既知IO/不正metadata/codec不正は固定StorageIoException、raw path/byte/cause/suppressedを返さない。codecのIllegalArgumentExceptionだけを狭い呼出境界で集約し、未知provider Runtime/Errorのidentityを保持する。channel closeの既知IOはTWRへ渡す前に固定例外化、bufferを全終了で消去する。未知primary/closeの組合せでも成功へ変換しない。
- 017046/047/BAT226～241で全method/line/class/branch100%、実Linux保持inodeと非特権synthetic UID境界、独立golden、name/full handle/null、全metadata/全IO出現点/close複合/読取り進捗/変更/中断/並行を検証する。Production expected生成は禁止。shared fixtureを使ってもgolden byte/名前/UID/sizeを固定独立値とし、readerが返した実値のsanitized traceをcollector独立期待に照合する。

### 6.8 root MANIFEST新規公開（SSC064/PG175）

先行51b872ed。`.file.BackupManifestPublisher.create(BackupManifest trusted, UUID partId)`は既存の`trusted.directoryName()+".part"`へMANIFESTだけを新規作成する。constructorは借用root、InodeSecurityCalls、backup UID/GID（1～unsigned32）を受領する。callerは原本両handle・閉じた実archiveの検証済claim、root設定/ancestor/realpath/FS durability、連続OS排他/actor停止を別途保証する。任意claimが正しいことをwriterは証明しない。

- 実効UID0、親/子はbackup UID/GID・0700 directory/nlink>=2/size>=0、同device、RW、ACLなし。既存子だけをNOFOLLOW保持し、新directory/command/DB操作はしない。
- UUID.partは`createPrivatePart`によるCREATE_NEW0600。新inodeはroot:root regular/nlink1/size0・同device・RW/ACLなし。既存UUID.partはCOLLISION、上書き/chown/自動削除/再利用をしない。
- canonical encodeのbyteを正進捗（返却countとbuffer位置一致）で全書込し、前後size、force(true)、writer closeを確認する。属性はmode/uid/gid/nlink/size/dev/ino/mtime/ctimeのtyped9項目。書込前後はidentity(mode/uid/gid/nlink/dev/ino)不変と最終長を確認する。
- writer close後、保持entryをbounded readbackしbyte一致、前後sizeとEOF、全9属性不変を確認する。公開直前に同名partを再保持して元snapshotと照合する。publishAs(partId,MANIFEST.json)のno-replace rename＋directory syncで公開し、既存MANIFESTは衝突として両fileを保全する。
- rename前後はdev/ino/mode/uid/gid/nlink/size/mtime不変（renameに伴うctimeだけは比較対象外）。公開後readbackと再保持ではctimeを含む全属性一致。子directoryは書込に伴うsize/time変化を許すがdev/ino/mode/uid/gid identityを維持し、親から再保持した子と照合。親root自体の全属性は不変を要求する。
- 所有child/entry/channel/writerの全close後、親root・実効UID・単調30分/割込を再確認してのみ正常帰還。全IO前後とloopで期限/割込を確認しflagを保持。instance内直列化、借用rootをcloseしない。PG170のResourceScopeでunknown identity・既知IO redaction・複合優先順位を維持し、encode/readback bufferは全終了で消去する。NULLは境界違反、NPEをcatchして正常化しない。
- 失敗時のpart/公開済fileは保全。新規専用であり再実行の再利用判断はcallerの別検証とする。最終directory rename、Reader＋ArtifactVerifierの再検証、DB pair確定、実dump/tar/age/7世代は別の必須残件。
- PTは017053/BAT242～257、独立golden・実Linux FDとsynthetic UIDを区別し、全4coverage100%と静的解析を要求。writer専用fixtureとする。低位write/read portは既存InspectorEnvironmentPublisher.Ioを再利用するが環境fileのpolicy/上書き/再利用規則は借用しない。

### 6.9 bundle directory公開能力の境界（SSC065/PG176）

SS333 §7.5の低位publishChildは、保持backup root内で正規`<directoryName>.part`から`<directoryName>`へno-replace公開するための能力である。batch callerが両名、所有/同device/全4file/全byte検証、全file forceと子directory syncを完了した後だけ呼ぶ。後段は確定directoryのReader＋ArtifactVerifierとDB両step確定を必須とする。低位API実装だけでこれらを完了扱いにしない。失敗part/不確定finalの調査、再実行、新backup検証後の7世代整理は既定どおり保全優先。

### 6.10 検証済bundleの耐久化・確定後照合（SSC066/PG177）

BUG204/YKT160修正前追補: forcePendingとverifyWithinのpackage内返値は不変BundleSnapshot（manifest digest、子directoryのtyped snapshot、全4fileの名前→typed snapshotのMap.copyOf）とし、外部public verifyは従来digestだけを返す。確定後はmanifest digest、子dev/ino/nlink/size/mtime、全4fileの9属性を元のforce済観測へ照合する。子mode/uid/gidは同じpolicy固定値を各phaseで既に検査し、renameに伴う子ctimeだけは許容する。file ctimeは変更を許さない。Map/metadata/capabilityをpublic結果へ出さず、同byte別inode cloneをforce済とみなさない。新forcePendingの安全なStorageIo reasonはMISSING/COLLISIONを保持し、従来public readonly確認の固定診断は不変更。

先行f224f646。`.file.BackupBundlePublisher.publish(BackupManifest trusted)`は既存新規partの4fileを耐久化・確定し、確定後MANIFESTのBackupFileDigestを返す。callerがroot生成manifest/閉じた3実archiveのtrusted claim、原本、固定account/root設定、連続OS排他と全actor停止を保証する。DB成功/command成功/世代削除/不明partの自動再利用を本APIが推定しない。

- 借用root/security/backup UID/GID・IO・単調時計をconstructorで確立する。全呼出はinstance内直列。単一の開始tickを操作全体で共有し、各phaseで30分予算をリセットしない。package内だけのReader.readWithin/Verifier.verifyWithin・forcePendingへ同じclockと開始tickを渡す。既存public reader/verifyは従来どおり自分の開始tick・readonly/final-directory限定を維持する。
- ArtifactVerifierのpackage内forcePending(expected,Force,started)だけは既存`directoryName+.part`を対象にする。既存public verifyのfile集合/属性/byte/hash/所有/再保持/診断/IO順を変更せず同一検査engineを用い、各保持entryでread/hashに成功した後、同じcapabilityを狭いForce callbackへ渡す。callback後はその元snapshotと全属性を再照合する。元pathを再解決しない。
- ForceはopenWriter（WRITEのみ、CREATE/TRUNCATE/内容writeなし）→size期待長→force(true)→size期待長→closeを全終了ResourceScopeで行う。4fileすべての成功・全entry/namespace再照合後だけ子directory syncし、全owned close・親確認まで成功した場合だけ次段へ進む。
- root.publishChild(part,final)で同親no-replace・親sync。確定後Reader.readWithinでroot manifestと原本両handle/nameを読む。返却manifestの全値がtrustedと一致し、Verifier.verifyWithinの全4file/hash結果がpending時のmanifest digestと一致した後だけ返却する。再検証はrename前の結果だけで省略しない。
- 操作全体の各IO境界/loop・所有close後・最終帰還まで同じ30分/割込契約を維持する。各phase入口も共有開始tickで検査する。blocking syscallの即時強制中断は保証しない。NULLは境界/invariant違反。既知IOは固定StorageIoException、衝突reason保持、未知Runtime/ErrorはResourceScopeの同identity・固定secondary規則。全読取bufferは既存engineの全終了消去を維持する。
- 失敗時はpartまたはfinal現物を保全、renameやsync不確定を元へ戻さない。最終Reader/Verifier失敗もDB成功へ進めない。既存finalとの衝突は双方不変、別generationへのfallbackなし。DB pair確定は§6.6の別caller段であり、本返値だけでcleanup許可しない。
- 017055/056・BAT258～273で独立4file/golden・共有期限・全IO/force/close/rename/sync/再読・crash/置換/並行・nullを検証する。既存read-only fixtureのmutation拒否を維持し、publisher専用fixtureを拡張して区別する。実dump/tar/age/restore/最新bundle・7世代・親全体は別残件。

### 6.11 root検証からDB両step確定へのcaller（SSC067/PG184）

先行483dc405。file.BackupBundleCompletionはpublic constructorで借用admitted root/同inode security/backup UID・GIDを受け、complete(parent,directoryName,databaseHandle,configurationHandle)をprivate lock内で直列実行する。parentは単独借用autoCommit=true/RW/READ_COMMITTEDで自己advisory lockを保持する。親の連続OS排他・生成子終端・停止状態・真正handle原本はcaller必須条件であり本部品から推測しない。

- API境界でConnection/name/2handleのnullを拒否。任意BackupManifest値をpublic入力にせず、6.7 Readerでroot所有canonical manifest/完全handle/nameを再読し、6.5 Verifierで同じmanifestに実4file・hash・owner/ACL/namespaceを照合する。各phaseの全owned closeを完了するまでDB処理を行わない。reader/verifierの既存期待値・read-only性を維持する。
- monotonic開始tickを1回取り、既存readWithin/verifyWithinへ同値を渡す。phase前後/DB前後の期限30分・割込を検査し、別phaseで予算をresetしない。既知IO/期限/割込は固定StorageIoException、DBの既知失敗は既存BatchRepositoryException、未知Runtime/NPE/Errorは非正常伝播。raw診断/manifest実体/秘密をlogへ出さない。
- 実file検証後に現在Instantを1回取得してMICROSへ切り下げ、6.6 BackupCommitServiceへmanifestと同時刻を渡す。UTC範囲/contentFinished以降は既存DB service境界で検査し、invalid clockを成功時刻へ補完しない。保存済両SUCCESSの再送は保存endを返し、現在時刻で書き換えない。新規DB/CONFIGは同一transactionでのみSUCCESS。
- commit後の期限/割込でも今回成功値を返さない。既にcommit済みならrollbackしたと偽らず、callerはConnectionを破棄し、次回にroot/4fileを再検証した上で既存保存済結果を照合する。失敗時fileの削除/修復、DB片成功補完、親排他の解除、borrowed root/Connection closeはしない。
- 017070/071・BAT274～281は独立golden/SQL後条件・161 IO・境界/NULL/未知・commit不明/並行/再送を確認する。constructorのpackage内clock/既存engine差替えはPT用で任意manifestをpublicに受け入れる代替入口ではない。実archive生成/最新真正bundle/7世代/親全体/実Linux deploymentは別未完了。

## 7. Business/technical cleanup

SSC117実接続補足：Cleanup開始前baselineはinactive/dead・fresh全kernel終端。親同budget内で型付きfresh正常0/10 receiptと開始/終了monotonic/Invocationを保持し、active/exitedでも全nested process空を独立検証する。成功CleanupはArtemis Requiresのため当回active/exitedを保持し明示stopしない（Backupだけ既存explicit stop）。親advisory handoffはBackup結果確定/readback後一度だけで、子全終端後に再取得してからDB結果readback→request→専用intentの順に退役する。handoff内で親Accessを呼ばない。次Morningは既存正規全8stopで旧Cleanupを停止する。root private `/run/schubert-nk/cleanup-request/cleanup-start.intent` は空0600/new-only/force/readback/同owner同inode退役、M取得直後・原本/DB/Unit変更前にrequest/part/intent/未知entry全clearを確認。UNKNOWN/reacquire失敗は同owner/同30分とmarkerを保全し通常unwindしない。

SSC104/PG324：Cleanupは真正oneshotが成功条件を満たして初めて後続Artemisを許可する。親root MorningはM/Aと原本run/activation/cutoffを連続保持し、子起動前に同runの非秘密固定request（`NKCLEAN1`、UUID2値、UTC µs cutoff、検証済MANIFESTのlowercase SHA256）をroot所有private sourceへ新規公開する。requestは相関材料であり権限ではない。親のsession advisoryは子前に明示解放・fresh子Unit全終端後に再取得し、子は自己専用DB sessionで同advisoryを取得する。子は真正root context/同原本、API/Web全終端、schema/release、当日同run両backup成功と4file現物/hashを自身で照合し、これらが不明なら削除0件で失敗する。既存Step/Log/Inbox/transferの順序・同cutoff・30分全体上限・warning/失敗記録を維持し、0/10だけを後続可能にする。単体codec/Unit loadedやDB row単独をcleanup成功へ読み替えず、未実装入口は起動拒否とする。
SSC104/PG331：子のMANIFEST SHA照合は343の固定root read-only候補選択で行い、候補なし/複数/交換/途中失敗は削除0・非成功。MANIFEST一致はfile claimに過ぎず、同bundleの3archiveとMANIFEST自体の4file再hash、両backup成功DB row/handle照合を後続必須gateとして残す。旧`.part`や別runの存在を自動修復・採用・削除しない。
SSC104/PG332：子の限定backup観測は、同一`CleanupWorkerRequest`を既存`BackupManifestReader.findCleanupClaims`へ渡した後、返った同一manifestを既存`BackupArtifactVerifier.verify`に渡し、実測MANIFEST size/SHAをrequestのcanonical SHAと照合する。全file保持・closeが完了した後だけ、子専用`CleanupDatabaseSession`から同期借用した非pool Connection（既取得advisory・schema済）で、autoCommit=true/RW/READ_COMMITTEDを確認→read-only transaction開始→`BackupStepRepository.inspect`で同run両stepの共通SUCCESS endedを確認→rollback成功→autoCommit復元を要求する。RUNNING/片成功/別handle/実file不一致、rollback/復元不明は削除0・固定非成功、borrowed Connection/backup rootは閉じず、呼出側が失敗Connectionを破棄する。これは当該時点のbackup限定観測で、親連続M/A、同原本、子lock/Unit・全固定actor終端・最終DELETE使用時の再検証を代替しない。RD/UI変更なし。
SSC104/PG335：子`CLEANUP` actorのAPI/Web停止観測は、親専用`MaintenanceUnitTermination.create`を偽親snapshotで流用せず、同じwhole-Unit/kernelleaf observerに子専用固定factoryを設ける。子factoryは真正`CLEANUP` root snapshotと対象`WEB`/`API`だけを受け、他actor/他Unitは照会前に拒否する。両者それぞれloaded/inactive/dead・Job空/PID0と固定cgroup/全nested process空/前後同一のfresh観測を要求し、片方のnot-found・active・未知は子の後続preflight/DELETEへ進めない。観測はその時点の読取であり親M/A・独立start禁止・永続停止保証を生成しない。子入口ではprivate/DB前とpreflight後に両者を再観測し、全closeとroot再検査後だけ限定結果を返す。後段DELETE直前のfresh再確認も別必須で、観測のみで0/10を許さない。RD/UI差分なし。
BUG313/PG335：上記read-only stop観測で生じる既知`StopGateException`は子preflight境界でraw causeを付けない固定IOExceptionへ写し、外部mainの安全失敗30に揃える。未知Runtime/NPE/Errorは同一identityで非正常伝播し、値・秘密・manager出力をdiagnosticへ出さない。割込flagは保持し、停止不明をinactiveへ補完しない。Unit未配備を30以外の既定process失敗へ放置しない。
PG332実装判断：Readerはcanonical MANIFEST claim SHAとrequestを等値確認して返し、Verifierは同一claimのcanonical MANIFEST byteと実disk 4fileのbyte/hash/ownerを照合してから返す。したがってVerifier戻りSHAとrequestの再比較は既存二条件から必ず導かれ、独立拒否分岐にならない。無意味な到達不能branchを作らず、Reader/Verifier双方の実拒否を別々にPTで確認する。

### 7.1 必須gate

SSC-049/PG-D-148: 親OS lock保持下で、削除開始前にAPI/Web各unitのId/LoadState/ActiveState/SubState/Job/MainPID/ControlPIDを固定systemctl showで読み、対象Id一致・loaded/inactive/dead・Job空・PID各0を全件確認する。not-found/masked/failed/active/遷移中/残job・PIDは通さない。7fieldは各1回、ASCIIのみ・末尾LF1つ・1～1024byte、未知/重複/欠落/CR/NULは失敗。unitごと5秒、非zero/IO/close/timeout/interruptは無条件に後続不可、割込flagを保持する。前後の割込確認と再実行時のfresh観測を必須とし、古い結果をcacheしない。これは停止実行やcgroup全検査ではない。親は保守中の再起動を禁止し、通常stop timeout/TERM/復旧の既存設計を維持する。

- 同じ`business_date`のBACKUP_DBとBACKUP_CONFIGがSUCCESS。Dump/manifest directoryが現存しhash再照合済み。
- `run_started_at`を全DELETEのcursor/cutoffに使い、実行中の現在時刻で対象を広げない。
- API/Webはinactive、DB batch advisory lock取得済み。未満足は削除0件でSKIPPED/FAILEDを記録。

### 7.2 Step順

SSC063/PG178・BUG195/YKT154（修正前追補）: LogCleanupServiceのSessionLeaseとacquire/closeで取得するStatement/ResultSetの5所有releaseは明示SQL scopeで内側から一度ずつ解放する。borrowed Connectionは閉じない。body成功後も全close成功までsummaryを返さず、未取得資源はcloseしない。SQLException/BatchRepositoryException/CleanupStoppedExceptionは既知失敗、他Runtime/NPE/Errorは未知失敗と区別する。未知primaryは同一性を保持し、cleanup失敗には固定DATABASE_FAILUREだけをsuppressedへ追加する（同じThrowable再送でも自身を追加しない）。既知primary＋未知cleanupはcleanupの同一性を優先する。既知同士ならprimary停止reasonを保ち、最外側でraw SQL cause/suppressedを除去する。既存LOCK_BUSY/TIME_LIMIT/INTERRUPTEDの理由、割込flag、lock取得/解放順と所有Connection破棄責務を変更しない。constructor/API境界nullは契約違反であり正常化しない。transaction rollback/autoCommit復元は別責務で、この資源scopeが回復成功を推定しない。017058/BAT026・029で公開JDBC複合故障と実lockの後条件を検証する。

SSC057/PG164: 非Log/非秘密Inboxの7kindは331 §3.14のStepCleanupService→CleanupStepRepository→V020を使用し、DELETE/step累積を一緒にcommitする。borrowed親Connectionはchunk間だけautoCommit=true、既取得自己session lock/OS排他を保持し、各chunk前後に30分・interruptを検査する。完了はchunk0＋残候補0の実確認後、FKdeferredは保全した非完了として親へ返しWARNING/次回保持の判断を維持する。backup/lock/SQL/commit不明は未完了、rollback成功前のautoCommit復元は禁止。shared step内の別kind累積・今回service差分を区別し、finishは親が全kind・実Inbox/Log等を照合した後だけ行う。実親結線/全清掃完了はこのserviceだけでは成立しない。

| Step | 対象 | Chunk | 失敗時 |
|---|---|---:|---|
| `CLEAN_NOTIFICATION` | COMPLETED/ERRORは状態遷移から24時間以上、CANCELLEDはstate_changed_atが固定run開始cutoff未満（SS332 §11.2） | 1,000 | Chunk rollback、FAILED、question削除へ進まない |
| `CLEAN_QUESTION` | 論理削除済み＋notification不存在 | 1,000 | FK競合はskip/warning、他DB異常はFAILED |
| `CLEAN_SESSION` | UI 251の失効/期限条件 | 1,000 | Failed tableを記録しtechnical後続は独立 |
| `CLEAN_INBOX_OUTBOX` | expires/SENT+7日、PROCESSING/PENDING/ERROR除外 | 1,000 | 異常rowを削除せずalert |
| `CLEAN_LOG` | 90日超。`security_hold_until > log cutoff`は除外、NULL/期限到達は削除 | 10,000 | Chunk単位再開、hold件数をskipped記録 |
| `CLEAN_BATCH_RUN` | 400日超、RUNNING/FAILED調査中除外 | 1,000 | 証跡保護を優先しskip |

SQL、lock、delete順は332 §11を正とする。Batch roleは基底tableを直接DELETEせず、331 §3.3のallowlist済み
maintenance functionを呼び出す。各chunk commit後にcountを更新する。
Process kill後は未削除rowだけ残り、同cutoff再実行で0件/残件を冪等処理する。

SSC-051/PG-D-136のCLEAN_LOG再開: 331 §3.9の永続cursor/累積を使い、同run/cutoffで全holdを含む各chunkを一度だけ数える。target0のENDをDBへ記録するまで完了としない。親のattempt件数は開始時と終了時のmaintenance_read_log_cleanup_progress累積差分、run累積は別記録。row lock競合/SQL異常/commit不明は未完了、再開時はDB状態を読取り直す。CLEAN_BATCH_RUNでlog progressの完了400日・調査保護も別chunkで清掃する。持続cursorのない旧関数を親側の無限retryで補わない。親process実装/OS gateは引き続き必須。

### 7.3 非公開Inbox検査process（SSC-049/QA-046）

SSC120・BUG365：Cleanup fresh正常30は成功0/10でもUNKNOWNでもない既知業務拒否として型付き観測する。failed/failed・exit-code・ExecMainCode1/Status30、fresh Invocation/monotonic、前後busと独立全kernel終端が一致した後だけ親advisoryを再取得する。実7step最新保存行の不存在/RUNNING/terminalと全列を同原本/期限下で独立読取し、未実行をFAILED/SKIPへ埋めない。別Inspector全終端、runtime env/inspector-owner/inspector-start.intent不存在、同request/maintenance-owner/current INVALIDを確認後、request→maintenance-owner→cleanup-start.intentを退役し、cycleが返ってからMain30を伝える。Broker/Expiry/permitは進めない。通常拒否にstop/reset-failedは不要。明示同run resumeは新activation/Epochで既存ABANDONED→次attempt/既成功SKIPを使い、元chunk/成果を保持する。signal/timeout/70/未知1/親期限・再取得・読戻し・退役不明は従来retain/隔離、残留を自動修復しない。

SSC119（2026-09-30、S2実caller接続前）：真正Cleanup childは自身のschubert_batch専用connectionを保持する。Inspector開始前に同run summaryを読取り、InspectorEnvironmentFilesのRoot所有同run環境をnew-only公開する。既存固定Unit engineの閉鎖INSPECTOR選択だけをCLEANUP actorへ許可し、任意Unit/pathやMorning全停止権限を渡さない。`/run/schubert-nk/cleanup-request/inspector-start.intent`をRoot0600で先行durable公開する（cleanup-start.intent/cleanup-requestと別entry）。親Morningが保持するM/A・同原本・現boot/Epoch・元の30分deadlineの条件を引き継ぎ、Cleanup/Inspector自身の起動から30分を再計時して延長しない。実削除の前後にも親生存・固定identity/deadlineを検査し、親死亡/期限を正常続行しない。

Inspectorは結果保持のRemainAfterExit=yesとし、開始前inactive/dead・前Invocation、開始後fresh Invocation・正常0/10・開始終了monotonic・全kernel process空を前後再読する。client0や古いDB ENDを子未実行の代替にしない。InspectorLockHandoff callback内で真正Unit終端を待ち、typed receiptを保持して固定Inspectorだけ明示stop/全終端を確認する。子の未知状態はcallback正常復帰を禁止する。子終了後Cleanupの自己advisory再取得が成立してから、同run summaryのEND/全累積とreceipt0/10をInspectionAttemptで独立照合する。環境/Inspector intentは同原本・parent/deadline・DB再読・全終端後だけ退役する。後続のCleanup active/exited保持（Artemis Requiresによる再実行防止）とは停止方針を分ける。未知状態のmarkerを削除・repairして起動可へ戻さない。

Cleanupは固定Backup rootを真正PID1 host-viewのread-only能力で検証できるが、mutation capabilityに昇格しない。UnitのRW許可は固定Transfer rootとInspector環境/intentのruntimeだけとし、Backup/config/credential全体へ書込権限を増やさない。元SUCCESS成果と今回SKIPPEDの参照はSSC116/117のまま分離する。全Cleanup・Artemis・Expiry/issuer接続と実証が閉じるまで、この補足だけでPG/PT完了にしない。

SSC049/PG162（先行d23b1afd）の親summary・attempt照合: 子へのDB引渡し前に331 §3.13の同run summaryをOptionalで読み、未開始0行は「未開始」として保持する。子のfresh起動・実終端・wrapper結果を別途確認してDB lockを再取得した後、同run/cutoffのsummaryを再読する。after不存在/未END/別identity、receiptが0/10以外、保護あり累積とreceipt10の不一致は非成功。beforeが存在すれば同identityで全3累積の非減少が必須。before既ENDならafterのcounts/ENDが完全不変でなければ非成功。attemptはafter累積−before累積（before不存在の差分基準だけ0）、run累積と分けて記録する。既完了再開のattempt0でも累積保護ありならWARNING10を維持する。現在時刻/推測cursor/receiptだけから件数を補完しない。純照合関数は不正を固定IllegalArgumentException、nullは契約違反とし、引数値を診断へ出さない。返却型もattempt各値<=cumulative、0/10と累積保護の整合をconstructorで保持する。実子unit・OS排他・実backup/親step記録の接続は引き続き別必須条件。

UIC-006の検査をbackup成功後のcleanup内部で実施する。通常API/Web inactive条件、固定run/cutoff、backup gateを維持する。検査中はHTTP/JMS Consumerを生成せず、DB snapshot/参照の検査だけを行う。batchのadvisory lockを別connectionから二重取得して自己deadlockさせないよう、検証・削除chunkのconnection/lock所有者を実装前に明示する。検査前後のlock断絶や他runの結果流用を許可しない。異常行は削除せず固定理由・件数だけを返し、暗号文・平文・鍵をbatchへ渡さない。SQL/権限/oneshot wiringのPT完了まで本stepを完了扱いしない。

SSC-049/PG-D-122のlock所有: 親batchはOS flockを保守全体で保持する。検査を開始する前に前段transactionを完了しDB session advisory lockを解放し、専用processが自身のDB transactionで71419602を取得してから候補を検査する。検査・DELETE・commitの間にlockを渡さない。親はprocess終了後にDB advisoryを再取得して後続へ進む。引渡し区間に別DB主体がlockを取得した場合、検査側/親の再取得失敗は失敗として停止し、検査未実施を成功にしない。OS lockを放す実装や、検証済結果を別transactionへ渡す実装は不可。実oneshot/異常終了の試験は後続gateとし、SQL単体PTで実運用結線完了とはしない。

SSC-049/PG-D-150（先行0797b369）: InspectorLockHandoffは親の単独所有Connectionを借用する同期境界。開始割込・nullを拒否し、autoCommit=true/readOnly=falseを確認。pg_catalog.pg_locksの自身backend・現在DB・classid=0/objid=71419602/objsubid=1・ExclusiveLock/grantedを照会して既保持を確認する（shared/two-int別namespace不可）。pg_advisory_unlockを1回だけ行い、自己保持なしを再照会する。再入取得が残る場合、余分なunlockで強制解除せず子0回で失敗。各SELECTはqueryTimeout=5秒、結果1行/non-null Booleanだけ、全ResultSet/Statement close故障も非成功とする。

上記完了後だけ同期callbackを1回呼ぶ。callbackは同runの検査子の終了確認まで復帰せず、親connectionを操作/共有せず、秘密情報を返さない。全callback終了（IO/Runtime/Error/nullを含む）のfinallyで親のautoCommit/readOnlyを再確認し、pg_try_advisory_lockと自己保持再照会により再取得を確認する。競合/SQL不明は失敗、待機lockやunlock反復をしない。全再取得/close確認後だけnon-null値を返し、最後の割込もflagを保った非成功にする。借用connectionのcommit/rollback/closeをせず、失敗後はcallerが必ず破棄する。SQL/IOのraw cause/suppressedは固定Failureへ正規化し、未知Runtime/NPE/Errorは正常化しない。callbackの結果だけでCLEAN_INBOX SUCCESSを記録せず、既存receipt/同run永続progress照合は別必須。OS lock・停止/backup・実子unit・credential/run束縛の確認はcallerの未完了gateとして残る。

SSC-063追補（2026-09-23、BUG195/YKT154）: callbackが未知Runtime/NPE/Errorで失敗した場合も再取得を必ず試みる。再取得時にSQL失敗が重なっても元の未知callback例外を同一identityで保持し、再取得失敗はraw SQL/cause/suppressedではなく固定secondaryだけで表す。値を返さず、callerは借用Connectionを破棄する。既知IOException＋再取得SQLは従来どおり固定Failure。これは既存の未知非正常化/再取得義務を具体化したもので、未知と別未知・fatal cleanupの一般優先順位は独立PTを経て別途確定する。442判断記録の親実測は修正前の失敗を示すので、現codeが本追補を満たすとは扱わない。

SSC-049/PG-D-127再開状態: 専用processは331 §3.8の永続progressを同run/cutoffでlockして読み、候補処理とcursor/件数を同transactionで確定する。各row transactionを1件chunkとして使うため1,000上限を超えず、processは最大1,000回ずつのbounded呼出しを繰り返し30分のunit制限内でENDまで進む。途中中断は未完了、最終ENDでのみ検査stepをSUCCESS（保護0）またはWARNING（保護あり）へ集約する。未対応/不正rowもcursorを進めて保護件数へ加算し、先頭同一rowの無限再走をしない。commit不明時は同runでDB状態を再読取りし、削除済み行の件数を失わない。親attempt件数はそのattempt開始時/終了時の累積差分、run累積は別項目とする。既完了runは保存状態を返すだけ、鍵/参照修復後の再検査は新しい保守runで行う。CLEAN_BATCH_RUNでは完了progressの400日保持とRUNNING/FAILED調査保護を確認し、331の専用清掃関数で削除する。SQL/Javaだけでは専用unit/親のOS lock引継ぎ・backup実体gateは未完了。

SSC-050/PG-D-129: 全maintenance_cleanupの第2引数は固定run_started_atとし、log90日・batch履歴400日の保持閾値をcaller側で二重に差し引かない。SQL側でも当日backupの状態・終了・同runをrow lockの単一snapshotで再検証する。Batch履歴は完了ended_at基準、現在runと同run内のRUNNING/FAILED調査中を保持する。親processの実backup照合とOS lockは別途必須であり、このSQL補正で省略しない。

SSC-049/PG-D-130: run executorは324 §12.7の単調時計30分とinterruptを各最大1,000呼出しchunk前後で確認する。END/保護0だけSUCCESS、END/保護ありWARNING、途中停止/DB障害はFAILED相当50。最後の確認済み累積値を「最新総数」と誤記せず、次attemptは同runで永続状態を再読する。30分はprocess unit上限でも維持し、Java協調停止だけで長時間SQLの強制停止を保証したとしない。親の実backup/key/OS lock/終了後close検証は別gate。

### 7.4 Inspector unitのfresh終端観測（SSC060/PG167）

先行81e0e64b。これはread-onlyの観測部品でありstart/stop/OS排他/quarantine/DB summary接続ではない。341 §7.3の同期callbackは実子終端まで戻らず、古いunit結果やPID2値だけを終了証明にしない。

- .batch.platform.InspectorUnitSnapshotは固定unit schubert-nk-inbox-inspector.serviceのshow出力18propertyをparseする。Id/LoadState/ActiveState/SubState/Job/MainPID/ControlPID/InvocationID/ExecMainCode/ExecMainStatus/ExecMainStartTimestampMonotonic/ExecMainExitTimestampMonotonic/Result/Type/Restart/RemainAfterExit/KillMode/SendSIGKILL。順序は不問、各1回・集合完全一致、ASCII1～2048byte・各行LF・末尾LF1、CR/NUL/高bit/未知/重複/欠落を拒否する。値に任意path/command/改行を持ち込まない。
- Id完全一致、LoadState=loaded、Type=oneshot、Restart=no、KillMode=control-group、SendSIGKILL=noを必須とする。RemainAfterExitはyes/noの観測値（現行unit設定はnoを維持）。他状態・ResultはASCII小文字の英数/hyphen1～64token、Jobは空または1～uint32のcanonical decimal、PIDは0～uint32、ExecMainCode0～6/Status0～255、monotonic µsは0～uint64のcanonical decimal。先頭0/符号/空白/overflowを拒否し、InvocationIDは空またはlower32hexの非nil ID。すべて型/範囲を構築時検査し、不変snapshot/toString redactとする。
- snapshot.quiescentはJob空・MainPID/ControlPID0かつ inactive/dead、active/exited、failed/failedのいずれかの必要条件だけ。これ単独を全process終端証明にしない。fresh receiptはその条件に加え今回InvocationID非空/開始前のOptional IDとは別、ExecMainStart>0、Exit>=Start、ExecMainCode=1、ExecMainStatus=0または10、Result=success、active/exitedまたはinactive/deadが必要。failed/failedやsignal/timeout、開始未観測、古いIDはreceiptなし。0/10をsystemctl clientの終了codeへ混同しない。今回runとの対応は親が同run環境の寿命とfresh起動を別途保証する。
- InspectorUnitProbeはread()、quiescent()（Optional snapshot）、completionAfter(Optional<UUID>)を供給する。quiescentはread→必要条件→固定GetUnitProcessesの正確なASCII `a(sus) 0\n`→再readで全18property不変、全command成功/資源解放/割込なしの時だけ存在する。非空/未知/過長process出力は終了を認定せず、command内容やPID/commandlineをlog/evidenceへ保存しない。Main/Control PIDとcgroup再帰の独立確認を重ね、TasksCurrent欠落を0としない。
- showは /usr/bin/systemctl --system --no-pager --no-ask-password show --property=<固定18field> <固定unit>。process照会は /usr/bin/busctl --system --timeout=5s --no-pager call org.freedesktop.systemd1 /org/freedesktop/systemd1 org.freedesktop.systemd1.Manager GetUnitProcesses s <固定unit>。shell/環境任意commandを介さず、既存NativeProcessのclear-env固定5変数（PATH/LANG/LC_ALL/SYSTEMD_COLORS/TERM）・stderr破棄を使う。show受信2049byte/process受信10byteで上限を検出、process空vectorは9byte。読取command各5秒、非0/IO/timeout/割込/null resourceは合格にしない。
- 全stdioを取得順に所有し、後続getter/IO/close失敗でも先行資源を閉じる。known IO/停止例外は既存StopGateExceptionの固定message/reasonへredactしcause/suppressedにrawを出さない。unknown Runtime/NPE/Errorは正常化せずidentity保持、既知cleanupのsuppressedも固定化。読取query自身へのTERMは可、SIGKILLは禁止。query子終了とInspector unit全終端は別概念。生byteはparse/比較後に消去し、値を外へ返す前にも割込flagを保持して再確認する。
- 未開始/GCによるInvocationID欠落、途中遷移、manager故障は成功ではない。現在RemainAfterExit=noなので取り逃した終端を古い結果で補完しない。後続controllerで結果保持設定/新起動barrier・起動不明時の停止待ち/OS lock寿命・SIGTERM shutdown・再開admissionを具体化する。期限を過ぎて子が残る場合に正常callback returnしてOS lockを閉じる実装は禁止する。
- OPS009/UI251/SS311/341/343、018021～024/PT-OPS-UNIT-001～016。単体は独立18field literal・公開process mockと実ローカルread-only tool確認、全resource/NULL/境界/並行/4coverage・静的解析を行う。本番root/systemd配布や実unit起動のIT/ST合格ではない。

一次資料（2026-09-13確認）: [systemd v259 D-Bus](https://raw.githubusercontent.com/systemd/systemd/v259/man/org.freedesktop.systemd1.xml)、[service](https://raw.githubusercontent.com/systemd/systemd/v259/man/systemd.service.xml)、[dbus-unit.c](https://raw.githubusercontent.com/systemd/systemd/v259/src/core/dbus-unit.c)。GetUnitProcessesはcgroup再帰とmain/control PIDを集約する。ExecMain時刻は現在または直前の実行で、fresh対応を別途確認する必要がある。

## 8. Transfer cleanup

333 §12のsecure directory walkを使い、backup失敗時も実行する。Root正常で個別file削除失敗はWARNINGとし
後続起動。Root不正/重複/mount read-only/permission不正は対象0件でFAILEDとし、Artemis/API/Web/Caddyを開始しない。

| 拡張子 | 処理 | 理由 |
|---|---|---|
| `.part` | cutoff前なら削除 | 中間file |
| `.ready` | cutoff前なら削除 | 取得成否にかかわらず次回朝削除 |
| 不明file/symlink/device/socket | 削除せずWARNING | 誤削除/攻撃防止 |
| root/日付directory | rootは不変、空の正規日付dirだけ削除 | 広範囲削除防止 |

## 9. Artemis Expiry cleanup

SSC125/BUG369（実装前）：実Artemisはsimple/on-failure/Remain=noで、worker oneshotのType/Restart/activating-start判定を流用しない。固定daemon18propertyのlive観測はactive/running・Job空・MainPID>0/ControlPID0・fresh非nilInvocation・start>0/end0等のmanager前後一致を照合する。これだけでreadiness/復旧/許可にせず、同Morning所有と実start、SS321全Ops/journal recoveryの実証を必要とする。Expiryは親の元30分deadline/真正Root Morning生存・同原本/INVALIDをprivate maintenance-ownerへ束縛し、現行実Expiry入口のDB/MQ/purge/commit前後へguardを継承する。親Cleanup handoff終了/全7step readback後にExpiry用の一度限りの別handoffを認める。実0/10/既知30と全kernel終端・元runの完全監査を戻ってから照合し、未知結果をFAILED/SKIPへ埋めない。正規issuerと原本完了が閉じるまでS2完了としない。293/294、SSC117/119下位。

1. Broker readinessと`nk.expiry.q` healthを確認。`nk_mq_maintenance`のLoadCredentialで管理APIへloopback接続。

SSC-076: この保守専用credentialの管理電文はSS321 §10の`nk.expiry.q`個別RBACに限定する。`countMessages`/`removeMessages`へ渡すselectorは固定`_AMQ_ACTUAL_EXPIRY`と数値cutoffから組み立て、null/空を送らない。DLQ/他Queue/Broker全操作の管理権限は付与しない。権限の実Broker正負試験だけで本節の削除/再実行/永続記録を完了扱いにしない。
2. Brokerが保持するexpiry timestampが`run_started_at - 7 days`より前のmessageをselectorでcount/byte見積り。
3. Count/byte/cutoffを記録した後、同selectorをArtemis management operationでpurge。Queue/journal fileをOSから削除しない。
   SSC-077: `batch_runs`の`CLEAN_EXPIRY`行には`expiry_cutoff_at`/`expiry_before_count`/`expiry_after_count`をV021以降で保存し、既存target/success/failure/byteに対象/削除/失敗/推定byteを対応させる。既存`started_at`からrun原本開始時刻を推定しない。監査値はstep結果と同一DB transactionで確定し、不確定commitは同run/cutoffの原本とDB行を再読取りして判定する。
   SSC-078: V022以降はpurge前に固定cutoff・実before・対象件数・推定byteを`CLEAN_EXPIRY RUNNING`へ確定し、`expiry_after_count`は未知のままNULLとする。purge後にだけ実afterとstep terminalを同一後続transactionで確定する。crash/通信断/DB commit不明でafterをbeforeや0へ補完しない。同run再実行は元行の観測値を保持したまま、残件を同cutoff selectorで再確認する。旧V021最終監査の正本rowと他stepは変更しない。
4. 実行後countで削除差分を照合。DLQは対象にしない。
5. SSC-085（UI251 §8/SS321 §12との誤記整合）: Purge失敗はERRORを記録し、ExpiryがCritical未満・broker health正常ならWARNING exitでAPI起動。Critical以上（件数5,000以上または設定済byte Critical以上）またはhealth不正はFAILEDで停止。warning閾値を停止境界に読み替えない。

## 10. Readiness・smoke

SSC178（2026-10-04、内部接続補足）：API ordinary ready→Web全業務ready→固定Caddy validate/実daemon/証明書検証付きHTTPS `/login` 200→同原本completeの順とする。元の親M/専用DB/原本/ISSUED/30分deadlineを連続保持し、API/Webは同捕捉boot/Invocation/PID/startTicks/cgroup/本人管理socket/署名5info/readyを各段前後で再検査する。Caddy送達中はAPI/Web両intentが連続した隔離fenceとなり、別receiptを捏造しない。成功時の稼働サービスintent退役は専用live-ready能力でWEB→API、同inode/同親/元deadline・実client0/全client資源closeと全ready/Caddy確認を前後に満たす。worker終了用退役とは別能力とする。通常後段失敗はCaddy→Web→APIを逆順停止し全kernel終端後に観測ownerを閉じ、残留intentを保全して許可abort。送達/停止/半退役/原本完了不明は非成功・所有保持で隔離し、成功へ補完しない。

| Component | Probe | 成功条件 |
|---|---|---|
| PostgreSQL | `pg_isready`＋readonly/read-write probe | 想定DB/schema version、role/grant、WAL/disk正常 |
| Artemis | CLI/management/readiness | acceptor loopback、journal、全Address/Queue、disk/duplicate cache |
| API | loopback management `/actuator/health/readiness` | DB/MQ/asset/codec/Consumer全UP |
| Web | loopback management readiness＋`/login` | MQ reply Consumer、technical DB、descriptor verifier全UP |
| Caddy | `caddy validate`→service active→HTTPS | Loopback `/login` 200、global IPは利用可能な監視地点から確認 |

Readinessは認証情報・Queue内容・DBデータをbodyへ返さない。Caddy公開後のsmoke失敗はCaddyを再停止し、
部分的に利用可能な状態を継続しない。

## 11. 再実行仕様

SSC116/BUG350（2026-09-30、実装前補足）：通常Morning resumeと手動Backupのportを分離する。通常で同run元SUCCESSがあるBackupは元成功bundle一対（DB/CONFIGの完全handle、同content開始/終了/attempt、実4file）を再読・実再検証し、今回両stepをSKIPPED/ALREADY_SUCCESSFUL、件数/byte全0として保存・commit後独立再読する。元成功と今回skipのhandleは別で、元の保存結果・成果を変更しない。最新の同runbundleを選び、異なる試行の片成功を組み合わせず、片方欠落/未知/不整合は拒否する。

§5.1/SSC108のfresh Backup Invocationは通常成功resumeでも必須だが、その真正子は「既存成果の実再検証」を行い、再生成しない。固定ASCII/LF profile NKBACKUPVERIFY1をNKBACKUP1と相互受理せず、元run・content開始・manifest SHA・dump size/SHAのみ許す（任意path/command/SQL/attempt禁止）。既存規則でdirectoryを導出し、普通Backup UIDが保持inode/owner/ACL/size/hashを確認して実pg_restore --listを実行する。親rootは元4file・元完全DB結果と今回両SKIPを保持前後に照合する。root0600 manifest/config/credential archiveを子のために緩めない。今回真正fresh子/全終端とこれらの証明後だけBackup完了能力/起動根拠とする。再検証失敗はpermit不可、新INVALID・保全対象保持、元SUCCESSをFAILEDへ書換えず、生成失敗経路へ流用しない。手動Backupの再生成・複数SUCCESS例外はSSC054の既存規則のみ。

SSC117/BUG351（2026-09-30、実装前補足）：真正Backup失敗後は成功manifestを捏造せずNKCLEANFAIL1の別固定profileで現run/activation/boot/Epoch・実非0fresh Backup receipt・完全FAILED pairを束縛し、真正Cleanup子が両COMMAND_FAILUREを全列再読する。BUSINESS/TECHNICAL削除6stepのみ実SKIPPED/BACKUP_UNAVAILABLE/全count0をcommit/readbackしDELETE/Inspectorは呼ばず、実Transferと独立Artemis/Expiryは続行する。成功済stepのskipは元terminal/Log進捗/Inbox summary/Expiry auditと今回SKIPを別identityで照合する。Cleanup後の親advisory再取得・全終端の後にExpiryを別一度限りhandoffし、同じ親30分budget/M/A/原本/INVALID ownerを保持する。Expiry auditは元SUCCESS handleだけで読む。今回SKIP handleを元auditへ渡さず、fresh selected0・cutoff/元audit全列・今回terminalを検証する。Transferの実高位callerは固定root・正規日付dir・NOFOLLOW walk・cutoff・集計・保持前後条件を実行し、既存低位unlink/sync能力を再使用する。

| Command | 前提 | 再実行動作 |
|---|---|---|
| `morning-run --resume <runId>` | Public/app停止、lock取得 | SUCCESS stepはSKIPPED、FAILED/ABANDONEDの次attemptを同cutoffで実行 |
| `backup` | PostgreSQL UP、root安全 | 毎回新directory、最新成功を当日成功に使用 |
| `cleanup --run-id` | 同runのbackup gate | 条件付DELETE、既削除は0件SUCCESS |
| `transfer-cleanup --run-id` | App停止、root safety | 既削除fileは0件、unknownは繰返しwarning |
| `expiry-cleanup --run-id` | Artemis UP、API停止 | 同cutoff selectorの残件だけpurge |

新しい日時でresume対象を再計算しない。別日へ進む場合は新run ID/business dateを作る。
SSC-054/BUG-138: 手動backup再実行は通常成功stepのskip例外。331 §8.2のbackup2stepだけ同日複数SUCCESSを保持し、新attempt失敗で既存成功を消去・状態変更しない。最新成功の実artifactを検証し、通常step成功一意性・固定run/cutoffと全backup gateは維持する。DB制約修正を実backup生成/検証完了と混同しない。
Manual commandもsystemd transient scopeまたは対応oneshot unitを通し、root shellでJava/SQL/scriptを直接実行しない。

## 12. Exit code・終了判定

SSC178：Morning全体の正常値は実Backup/Cleanup7step/Expiry及び元SUCCESS/auditを同DBで完全再読した結果からだけ集約する。実Backup FAILED・六BACKUP_UNAVAILABLE・実Transfer/Expiry続行、許容Cleanup/非critical Expiry警告はWARNING10、全正常はSUCCESS0。未実行/不明/critical/安全性異常を10へ正規化しない。現在保持原本Sessionのcompleteを経て全graph・done全値を照合し、外側原本6FD/DB/credential/Mと最後のroot検査が正常帰還したnative typed経路だけが0/10を返す。途中のholder値やAPI/WebUP、原本file単独から親成功を生成しない。全close不明は0/10不可。PG/PTの正常値でIT/STを合格にしない。

| Code | 分類 | Systemd/operation |
|---:|---|---|
| 0 | SUCCESS | 後続へ進む |
| 10 | WARNING | Unitは設計済みwrapperでsuccess扱いに変換しalert。後続継続 |
| 20 | DUPLICATE/LOCKED | 二重実行なし、alert、自動再試行なし |
| 30 | SAFETY_GATE_FAILED | 削除/公開/後続停止、運用介入 |
| 40 | BACKUP_FAILED | Business cleanup skip、transfer/app起動は続行 |
| 50 | COMPONENT_FAILED | 依存後続を開始せず運用介入 |
| 70 | CONFIG/USAGE | 無操作で終了、修正後再実行 |

WARNINGをunit失敗としてdependencyを止めないよう、wrapperが`batch_runs`の状態を記録後に
systemd向け処理を明示する。予期外exception/signalは50扱い。

## 13. 証跡・機密除外

SSC-049/PG-D-144: private Inspector子unitだけは343 §6.8のreceipt wrapperを入口とする。JVM正常終了と検査成功を分離し、wrapperの0/10/50/70を親が同run/cutoffの永続progress・unit終了状態と照合する。子unitのSuccessExitStatus=10は「警告付きで子processが終了した」という扱いに限り、親CLEAN_INBOX stepを自動成功にしない。親だけがWARNING/件数/attemptをbatch_runsへ記録した後に後続へ進む。childの0だけで親OS lock/停止/backupを省略せず、古いunit結果/別run/不確定commitは成功へ補完しない。

Run ID、business date/cutoff、host、app/schema/config/package version、step/attempt、開始/終了、status、
target/success/failure/skipped count、byte数、duration、exit/error code、backup manifest hashをDBとstructured logへ記録する。

Command line全体、password、credential pathの内容、質問/回答本文、物理file path、backup暗号平文は記録しない。
Package名/versionと非秘密config hashは記録可。

## 14. PT・IT必須観点

- Timer、手動、二重起動、OS lock/DB lock、step中process kill、reboot不成立。
- Caddy/Web/API/Artemis/PostgreSQL各stop timeout、transaction rollback/requeue、自動SIGKILLなし。
- `pg_dump`非0、0 byte、list不正、hash不一致、config暗号失敗、rename失敗、容量不足。
- Backup専用role以外でのdump、dump roleのDML/SET ROLE/復号key取得、backup unit外からのcredential利用を負の試験にする。
- Backup成功/失敗分岐、7/8世代、既存世代保護、別test DBへのrestore。
- Notification全5state/cutoff境界、Question FK競合、chunk間kill/resume、保持対象外。
- Transfer root誤り、symlink/device/unknown file、個別失敗、root自体の保護。
- Expiry 7日境界、management権限拒否、warning/critical分岐、DLQ不変。
- 起動順全分岐、API/Web readiness内訳、Caddy公開前後smoke。

## 15. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-033 | Morning排他をOS `flock`＋DB advisory lock `71419602`の二重にする | Reboot前後・手動/systemdの二重実行と、DB別host起動誤りを検出 | Unit/wrapper/PTにlock case |
| SS-D-034 | Credential backupをoffline private key式`age`で暗号化する | Server内backupと復号keyの同時漏えいを防ぐ。UI 251の暗号archiveを具体化 | Package/recipient fingerprint/recovery rehearsal |
| SS-D-035 | Cleanupはrun開始cutoff固定＋chunk commit＋同run resumeとする | 中断再開で対象範囲を広げず、大量DELETE lock/WALをbound | Batch repository、kill/resume IT |

## 16. 禁止事項

- Backup成功rowだけを信用し、dump/manifest/hash現存を確認せず業務dataを削除すること。
- 環境変数・glob・未検証のrootで再帰削除すること。Backup/transfer root自体を削除すること。
- Package update/backup失敗を無記録でsuccess化する、またはbackup失敗だけでapplicationを停止継続すること。
- Expiry/DLQ/journal fileをOSから直接削除、DLQを7日purge対象にすること。
- 再実行で新しいcutoffを使い、元run開始後のdataを追加削除すること。

## 17. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | 計画停止、backup、cleanup、Expiry、readiness、resume・exit codeを詳細化。 |
| 2026-08-31 | 横断監査でbatch cleanupを331のallowlist済みmaintenance function経由に固定し、文言誤りを修正。 |
| 2026-08-31 | `pg_dump`用SELECTとbatch保守権限を分離する`schubert_backup`案をQA-043/UIC-003として保留。 |
| 2026-09-01 | QA-043/UIC-003承認を反映し、専用backup OS/DB role・credential・固定dump commandを確定。 |
| 2026-09-03 | SSC-005を反映し、CLEAN_LOGのSecurity hold期限判定とskipped記録を確定。 |

## QA-048承認反映：業務質問削除後の受付参照cleanup（2026-10-03）

業務DBを正とし、既存question/answerの条件付き物理削除が確定した後に、SS331 §9.4の固定maintenance_cleanup_web_receipt_referencesを既存cleanupの同run/当日backup gate/通常API・Web停止の下でbounded chunk実行する。質問が物理削除済みの孤児だけを対象にし、論理削除flag、Web session期限、独自経過日数やAPI0102だけではlocatorを消さない。復元した孤児も同じ条件で照合し、件数/skip/失敗はbusiness削除件数と分けて記録する。batchへ直接業務/Web table read/delete権限は増やさず、owner内部固定SQLの判定と実削除を同transactionで行う。API/Web稼働中GETはcleanup待ちの古いlocatorを成功根拠とせず毎回IF030で拒否する。独立PTは存続questionの保全・物理削除済み孤児・別受付tuple・backup失敗・restore/途中rollback・limit/cutoff/lock・権限負試験と件数照合を含む。新functionの適用/実caller/証跡が揃うまで実装完了としない。

## QA-050承認反映：失効再試行rowの保全（2026-10-03）

pending_context_revocationsはAPI/Web sessionの期限cleanupと分け、expires_at NULL/経過、attempt_count=100、一般0102、未知、復号不能を理由に朝batchで削除しない。検証済0000/0200と現在leaseの確認を行うWeb retrierが削除を所有し、固定maintenance functionにも推測期限削除を残さない。必要な旧鍵は未解決row/borrowerが0になるまで保全する。15分継続再試行とIT/ST性能問題時の間隔見直しはSS314/354。実cleanup/restore/鍵rotationの独立PTで保全を確認する。
# 朝batch・backup・削除・再実行設計

SSC202（2026-10-06、SSC200201/BUG788/YKT562）：隔離PG/PT VMの同日別run参照修正では、成功済みBackup二stepとCleanup七SKIPを持つ未完了runを保全し、027→028移行・pending code-only・一回用通常resumeを別の正常所有区間として認定する。元cutoff/activationをoperatorが更新せず、手DB terminal修復/日次業務再処理をしない。既成功Backupは元schema027の真正manifest/全byte/元二handleで通常same-run再用し、新profile028へ書き換えない。新規Backupだけ現在署名/profile028と整合させる。親fresh Invocationからの30分budget、実Unitの期限、API所有のままWeb/Caddy/原本DONE、失敗逆順停止・全後条件は既契約のまま。各段の実source/終了コード/全資源正常帰還を確認するまで次段の権限・成功を与えない。
SSC202工具起動前失敗限定回収（BUG797）：参照子missing filenameの実exit2、SAVE/Ref/設定変更/start0を実証し、当管理Javaのboot/PID/ticks/Root/子0/専用DB/locksを現在値固定した場合に限りowned PIDへTERMし、消失・全peer/lock0・十Unit/kernel/全原値不変更を確認して別新scopeへ進める。回収は異常終了であり旧close正常化/一般UNKNOWN補修/業務Unit強制終了の根拠にしない。
SSC202同範囲起動前失敗（BUG798）：既知の署名base security取り違えが十Ref取得前に失敗しSAVE空/runtime空・全原値不変更の場合、固定child/parentのboot/PID/ticks/Root/argv/全task-childを認証して当child→parentのowned TERMだけで回収する。既DBidle TX期限後peer0は正常closeでなく、前後全原値・全peer/lock0と独立拒否再現を保存、新scopeへ別所有で進む。一般UNKNOWN・業務Unit強制終了・旧close正常化へ拡張しない。release原本Root:schubert0640と/etc配備Unit Root:Root0644は既署名profileのまま別検査し、権限を変更しない。


## SSC337 LogCleanup借用transactionの複合故障（2026-11-06）

BUG2317/YKT2062。§7.2の5資源releaseとは別に、LogCleanupService.transactionにも§6.6の既borrowed transaction規約を明示適用する。開始済みで未commitのbody SQL/Runtime/Error失敗はrollbackを一度試み、正常rollback後だけautoCommitをtrueへ復元する。rollback/復元のSQL・未知Runtime/NPE/Errorで先行未知primaryを覆わず、同一objectのまま再送出し、新しい固定DATABASE_FAILUREをsecondaryへ一件追加する。同じThrowableが再送されても自身へaddSuppressedしない。既知SQL/BatchRepositoryException/CleanupStoppedException primaryに未知cleanupが重なる場合はcleanup同一性を優先、既知同士は固定DATABASE_FAILUREとする。回復がすべて正常なら元の既知停止reasonを保持する。

commit済みflag確定後の失敗はrollbackしたと偽らず、回復/再commit/再送を発行せず非成功でcallerのConnection破棄へ渡す。rollback不明後のautoCommit復元・回復retry・借用Connection close/新接続を追加しない。通常chunk結果/累積/lock取得解放順・割込flag・共通期限・SQL/DB構造・業務UI/wire/承認DIFは不変更。公開executeの独立JDBC proxyで未知/既知/同一Throwable・commit前後・rollback/復元/借用close回数を照合し、実DB後条件・native・451全体の認定とは分ける。詳細設計内の既契約適用補足でありRD/UI変更・利用者QAは不要、PG/PT・main公開の完了は別に記録する。

## SSC-437 CleanupKind親stepの固定metadata責務（2026-11-16）

CleanupKindの閉じた九種から親BatchStepへの対応を各enum定数のfinal parentStep fieldで表す。private enum constructorへ固定BatchStep引数を追加しObjects.requireNonNullで内部invariantを確立、step()はfinal fieldを返す。対応はNOTIFICATIONS→CLEAN_NOTIFICATION、QUESTIONS→CLEAN_QUESTION、SESSIONS→CLEAN_SESSION、OUTBOX→CLEAN_INBOX_OUTBOX、LOGS→CLEAN_LOG、WEB_RECEIPTS/BATCH_RUNS/INBOX_PROGRESS/LOG_PROGRESS→CLEAN_BATCH_RUNの既存九件を完全保持する。enum名/定義順/ordinal/values-valueOf/public method descriptor/function()/maximumRows()/親BatchStep.backup/SQL識別子/DDL/削除条件/transaction/実行権限/HTTP電文/画面/承認DIFを変更0。private constructor内部引数だけで外部binary method/type kindは変えず、enumは不変metadataで実処理/原本/所有/commitの証明ではない。元switch式のraw生成default1分岐6命令不足BUG3083は除外・到達不能宣言・反射で埋めず、責務を既定値に保持する表現へ修正する。元Boundary二Testclass四＋独立値四の全三class8のfixture/入力/独立期待/全sourceを変更0、新sourceのfreshMain10RootNullAway/全静的/同singleexec全8/current186physicalCRC-init/XML/raw全十Codeclassで再検証する。旧default四100/別source/rawを現source合格へ加算0、未実行/HOLDのrepository/SQL/DB/Root2Actual4/鍵/VM/native/aru/終了依存を代替0。内部詳細補足でRD/UI/QA変更不要、全WBS/正式受入は個別criteriaと終了依存が満たされるまで更新しない。

BUG3083/YKT2431、状態:設計確定・main反映前、PG/PT/全criteria・終了依存/正式未完。
