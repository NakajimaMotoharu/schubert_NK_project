# Caddy・systemd・PostgreSQL・Java設定設計

## SSC335 Web管理HTTPの有限lock/join budget（2026-10-22）

Web管理のcloseWithinは既0～30秒入力を停止通知前に検証する。停止要求でstopping/DOWN・promotion拒否をlock待ち前に確定し、完了closedとは分離する。lock待ちとexecutor awaitTerminationは同じSystem.nanoTime単調deadlineの残量だけを消費し、零を無期限lock/waitへ変換しない。lock取得失敗・待機中の新IRQは固定IOExceptionで不確定帰還し、IRQflagを復元、vendor stopや完了cacheを推定発行しない。

Web固有の既IRQ表は維持する。呼出前IRQはlock取得待ちだけ一時clearし、取得後はJDK stopより前に復元する。既stop内のflag保存/復元と、その後のawaitが割込で不確定となる契約を変えず、全帰還で元通知を復元する。API SSC313の「一時clearのまま終端確認」と共通化しない。serverStoppedは正常start済みstop正常帰還後だけ、closedは実executor終端後だけ、成功子の再stop0/再join・未知時のowner保持・固定診断/例外順位は従来どおり。

SS342§5.2のWeb30秒phaseとSS352の残phase管理の内部補足。既HTTP/業務/SQL/権限/Unit・親30分を不変更。vendor stop(0)そのものを強制中断できる保証は追加せず、vendor非帰還は既UNKNOWN/Unit境界の残存リスクとして保持する。自己所有の有限HTTP/worker fixtureは実Web/Root/native/配備後条件の代用でない。BUG1627/YKT1380、SS354/SSC335、RD/UI変更不要。

SSC330（BUG1593/YKT1346、SS312/354参照）：ordinary API/Web readinessのDB/JMS admissionは、接続/probe/consumer/closeのfinite failure graphを通常startup catalog前に分類する。取得済Connection/JMSContext close各一回、DB失敗後のJMS開始0、JMS失敗後の業務ready0を維持する。直接primary Errorは同一objectで優先、直接close Errorが非Error primaryへ優先する既選択も不変更。捨てた非Error close secondaryの内包Errorも一時attachmentとcause/suppressed/linked/next分類で保持する。正常probe/固定診断/Queue管理側gate・Unit/Root/timeout/権限/順序は不変更、interface proxyの成功は実VM/Root/ordinary業務ready・所有の証明ではない。

SSC325（BUG1578/YKT1320）：Web借用frameの未知close後も固定診断のRTE/Errorは保護し、取得前固定policyとcallback/failure到達性fenceを持つ同frameを維持する。固定診断文・stop通知・Unit/親期限・隔離は不変更、dummy childの終了を実資源解放と認定しない。元source回帰実行中はMain/Testを変更しない。

SSC324（BUG1574/YKT1329）：SS313の既取得Web startup owner cleanupがUNKNOWNなら、元startup/後続ownerを保持した同frameで既固定ServiceProcessResources retentionへ入り、Root/native停止や解放完了へ読み替えない。取得前policy準備/無新規保持callback/到達性fenceを要求する。既Unitの期限・元親budget・停止/隔離・borrowed資源は不変更、同scopeのdummy child JVM終端は実Web/Root/native後条件の証明ではない。実環境の安全HOLDを解除しない。

## SSC319 ordinary受信のrollback資格

rollbackの試行前attemptedと正常後confirmedを別同期port/stateとし、同配送にresetする。既rollbackのErrorをdirect-processing Errorと誤認して二回目のbest-effort rollbackを発行しない。元Error identity、既一回のdirect Error rollback、native UNKNOWN/親Unit期限は維持、外部運用操作は増やさない。

SS321SSC319の同期確認port/stateをordinary API三consumerへ接続する。確認stateは取得前に準備し、同配送/contextのrollback正常帰還だけで普通retryを許す。未確認callback例外は既halted/terminal・fatal通知へ分離し、処理成功・正常close・新Rootの権限にしない。public listener互換・既UNKNOWN保持/親30分/Unit期限は維持、実Root/native/DB後条件は別資格。BUG1565/YKT1322。

## SSC318 UNKNOWN keeper内の二次失敗（2026-10-21）

実装補足：native fixed policyは取得前の明示getter呼出でretainer classを初期化し、単なるmethod reference作成だけで初期化済みと仮定しない。通常tick失敗時は、取得前準備した固定fallbackでmonotonicな1000ms待機を挟み、IRQ/park早期帰還でもその待機期限を維持する。fallback自体がVM障害等で不能でもUNKNOWNを正常終了へ変換しないが、VM健全性/低CPUを保証するとはしない。これは規約411の無制限busy loopを通常運用として許可する補足ではない。

SS316の固定UNKNOWN保持は、固定診断又は観測tickからRuntimeException/Errorが発生しても同failure frame/外側借用資源の保持を続ける。診断はbest-effortでraw原因を出さず、失敗してもnormal receipt/再close/Root再発行を行わない。観測portは資源取得前のclass初期化で準備しnative固定portだけを使う。通常観測は1000ms、IRQ時の保持/親30分/Unit期限を変更しない。process/VM自体が停止する障害まで保持を保証せず、persistent tick失敗時のCPU負荷等を残存リスクとして記録する。BUG1563/YKT1320/SS343354。

## SSC317 未start管理HTTPの完了解釈（2026-10-21）

API/Web管理serverは正常start完了が確認できない時、JDK stop(0)の正常返却だけをsocket/selector解放完了とは解釈しない。実停止通知・既stop/実executor joinを行ってもその状態は固定UNCONFIRMEDとし、closed/serverStoppedの成功cacheを立てず、nativeの既所有frame/外側借用資源保持へ接続する。正常start済みの従来の実stop/join/冪等完了は維持する。

根拠はJDK25.0.4未start bind及びsetup失敗後の独立port再bind反例（BUG1560/YKT1317）。vendor内部selectorの詳細原因は推定と区別する。cleanup中の新server.start、private JDK reflection、別FDへの権限変更、JDK更新によって正常停止を推定しない。完全解放が未保証のまま所有を保持する残存リスクを明記し、Root正常/DONE/新起動可能とはしない。SS316のUNKNOWN保持・親/Unit期限とRD/UI/業務契約は不変更。componentの固定失敗診断と実nativeの保持/後条件は別資格を要する。

## SSC316 API nativeの取得前所有・UNKNOWN保有（2026-10-21、S3b）

ordinary APIは全acquire/release/action portをその資源の取得前に準備し、ResourceScopeとServiceProcessResourcesの既native ownedReleaseを使ってbroker→application内側資源→management→consumerの所有を接続する。API管理HTTPはbindで全owner/state/未開始executorとbound serverを返し、native ownerが捕捉してからstart/configureする。既openはbind/startを合わせたcomponent互換entryとして元例外契約を維持し、startは一度だけ、停止要求後/重複startを拒否する。

native partial startup/closeが未確認なら、同failure frameで固定UNKNOWN保持し、外側Outbox/codecs/roots/broker/DB/key/Root scopeへunwindしない。close成功後だけ次ownerへ進む。API内側applicationのnative entryにも同ownedReleaseを適用し、legacy component/TWRの例外順位は不変更。API cleanup complete/finished通知は全既scopeが正常帰還した場合だけ。既hookは通知のみでclose/System.exitを発行しない。

保持helperはbootstrap既releaseを明示再利用する内部APIで、固定診断のみ・自動retry/正常receipt/新Root操作権限を持たない。親30分/既Unit・component期限は不変更、UNKNOWNを時間超過の正常終了にしない。Web返却済みphase/Executionは維持し返却前factory native経路だけ接続する。SS321343354/SSC316、BUG1547/1556/YKT1307。

## SSC315 API factory返却前の所有（S3a）

SS321SSC315のAPI provider設定保護/親broker取得前準備を適用する。factory内部の未返却資源はsupplier側で一度close、親brokerは正常返却した三factoryだけを所有し、未取得の推定close/親owner準備後置をしない。固定設定/権限/期限/業務不変更、partial cleanup例外の同一性・順序は境界別に維持する。native UNKNOWNの保持・Root/DB後条件は別S3b未完で、局所設定PTをそれらの実証へ流用しない。BUG1553/YKT1307、SS321354。

## SSC314 API JMSのclose phase（2026-10-21、S2）

SS321SSC314をSS342SSC158のUNKNOWN非正常化へ接続する。三consumer/親group/brokerは停止通知と成功子phase・全完了を分け、private final lock下の成功子だけを再close対象外とする。新callback/contextの拒否と既ACK/rollback/例外優先を維持し、close失敗後の再closeを無条件正常にしない。独立finite自己所有proxyで検証し、実親/DB/鍵/Root/Unit期限と未確認外側保持をその局所結果から認定しない。native partial factory/外側保持のS3は未完として別gateを要する。BUG1548/YKT1307/PG-D463、SS321/354。

## SSC313 API管理HTTPの停止要求・完了分離（2026-10-21、内部詳細補足/S1）

SS342SSC158の不確定close非正常化をAPI管理HTTPへ具体化する。固定loopback8091/5値info/route/method/readiness admissionは不変更。close要求はstopping通知で直ちにDOWNへ、private final lock下のclosed（完了）とは分ける。closedはJDK server.stop(0)が正常終了し、owned executor.shutdownNow後のactual terminationが所定残budget内に確認できた後だけ確定する。stop不確定はserverStoppedを確定せず、完了前の再closeをno-opにしない。stop確認済みでexecutor joinだけ未確認なら再closeはstopを再発行せずjoinを再確認する。これは保持handleのcomponent retry契約で、native UNKNOWNの自動retryや実VM/Unit停止の再発行許可ではない。

close()の既定上限30秒、内部closeWithin(Duration)は0～30秒のみ。null/負/上限超過は停止通知前に拒否する。lock待ちとexecutor待ちを同じ単調deadlineから差し引き、0を無期限waitへ変換しない。新割込はflag復元して不確定失敗、呼出前からの割込は一時的に保持/clearして実終端を確認し、全帰還で復元する（既READY005のJDK stop前のcaller interrupt保持を維持）。不確定lock/joinは固定IllegalStateException、provider stop Runtime/Errorは同一性を保持し、正常停止receipt/clean markerとしない。

BUG1547/YKT1307/PG-D462/1294、SS342/354。S1は管理ownerだけの内部設計確定で、API親TWR・既JMS group/factoryのclosed前置・partial factory/UNKNOWN時の借用依存保持は同群の後続S2/S3調査・別詳細補足を必要とする。S1だけでAPI全native lifetimeやRoot真正終了を認定しない。constructor取得前state準備（SSC312）・外部画面/電文/SQL/role/親30分/既Unit期限は不変更、確定後は新規資源取得を行わずnormalclose冪等とする。

## SSC312 HTTP資源factoryの取得前owner準備（2026-10-21、内部詳細補足）

API/Web管理HTTPは、入力・固定loopback住所/port/backlog32を検証し、owner・全flag/lock・未開始executor（core/max1、queue32、daemon名は既定）・応答情報を先に準備してからHttpServer factoryを一度だけ呼ぶ。取得成功後は追加の未保護allocationを挟まずfinal serverへ格納してownerを返す。取得例外/nullは成功へ変換せず、未取得serverをcloseしない。factory内部で取得後に失敗した資源はfactoryの責務であり、callerが未返却資源を推定回収しない。WebHttpServerも未refreshのMVC context・private final lifecycleLock・ownerを先に準備してからTomcat supplierを一度取得しfinal格納、既startWithOwnerの捕捉callbackとvendor設定/startは既存try内を維持する。未refresh MVCはclose義務のある開始済資源として扱わない。

取得後の既start/stop/destroy/cleanup例外順位・失敗owner再試行・readiness・API8091/Web8081/業務8080・URL/電文/権限/SQL/制限を変更しない。実OOM/実運用漏えいを観測したとの認定ではなく、取得後のowner準備allocation gapを構造上除く。BUG1545/YKT1305、関連SS313/342/354、PG-D461。取得前準備→factory最後→final格納は実ClassFile順序を独立点検し、故意のOOMや稼働VM操作で検証しない。動的PTは通常の有限self-owned fixtureだけ、拒否PT代替や実親/native/配備証明とは分離する。

SSC237（2026-10-09、SSC187203実配線補足、BUG938/YKT707）：Caddy/Web/API各typed intentのbefore/after及びAPI保持確認、DONE前後を一つの同owner-thread完了順序へ接続する。pending/退役後の各gateは、同Root/保持原本graph/同ordinary世代・identity/socket/info/ready/run整合と全evidence行/seal/保持receiptをTX外で再読する。退役後gateをpeer/run照合だけで代用しない。SQL中は既純ownerを維持しDB再入しない。Caddy-before直前の独立重複full呼出は不要だが、retireReadyAfter内部のbefore/after証明は削除しない。失敗phaseを固定列挙、IO/RUNTIME/FATALだけとprocess-local monotonic経過（権限・期限ではない）を一回記録し、未知保持/元30分/逆順停止契約を維持。元例外message/stackや秘密を診断へ出さず、原因不明を時間超過だけで正常化しない。停止中のquery160中央値5.384061msは限定測定、旧timeout原因確定/性能受入ではない。キャッシュ・transport変更・期限緩和は本補足の対象外。

SSC235（2026-10-09、QA047内のPG758失敗世代復旧）：343の当source限定profileを適用する。親の元1800秒timeout143/RootDONE無しを正常終了へ置換せず、API/Web/Caddy/Artemisの捕捉同世代を発行直前再照合し、新M→A→専用DB/advisory71419602・固定十Unitの同private bus Refと実保持FDの下でCaddy→Web→API→残保守→Artemisを正規停止する。依存による先行停止は同世代の真正kernel/native/PID1/vendor witnessで検証し、stopを再発行しない。current七startup現物・親/child launchとsecurity・元原本/全24/Backup/Transfer/旧失敗証跡を保全する。全kernel/当native終端・後条件成立後だけ正規同epoch失効と既存Pair退役へ進む。配備/再起動/期限延長/未知ownerへの停止0。停止中Unitは固定LoadUnit/RefUnitで観測保持できるがstartはしない。各通常資源close不明は非成功・再隔離し、旧失敗のclose成功を推論しない。

SSC233（2026-10-09）：現PG631のcompleted601/正常停止・current Bootstrap20からPG682所有内部変更群へcode-only再束縛する固定profileは343SSC233を正とする。旧失敗/原本/全24-514/18Unitfile・hardening/既native設定・十主要と依存・元1800秒/各Unit期限を保持する。新candidateは187/SQL28/history29の同pin型付き資格、verify/activate別連続M-A/専用RODB/十Ref/保持dirFDで全21原値を照合し、同run/cutoff/activation新INVALID epoch・Root0400approval/currentだけを公開。daemon-reload/Unit配置/新permit/業務start/stopを当切替へ混在させない。GCは既normal20から有限idleだけ、旧unknownclose/成功推定をしない。正常全scope/独立post後だけ別fresh起動/所有/同source実nativeへ、host成功や候補署名だけでUnit/coverage/formalを受入しない。

SSC231（2026-10-09）：当PG631完成・正常全停止後の専用Bootstrap一回existing-onlyは343を正とする。既署名Unitの30s/Restart=no/disabled/SuccessExitStatus20・hardening/credential/name/UID/GID/groups/cap0/NNPを変更せず、新二sourceだけ正規入力世代として作成・私有退役する。新十Ref保持で当Bootstrapの元INVと新normal20を分離、他九主要18/全宣言/依存と18Unit source byteは保持。全24/既原本/Startup/Backup/current/approval/旧Proofを二読し、M-A/前postDB/Ref/FDの正常closeと実資源0を閉じる。古いBootstrap credentialの復元・Unit再配備/reload・通常service再start・空UserDBへの拡張・旧source native輸入を禁止する。

SSC230（2026-10-09、runtime635退役の当profile）：一回reload後も全十Unit主要18/全kernel/Job空・genuine新parentPID1及び元完了原本をexact保持する。Morning補助ExecStartは署名base＋既nativeのplain argv（--resume二引数無し）/exact未実行履歴、DropInPathsは既nativeだけ。補助履歴resetの許容はSSC229と同七Artemis/Caddy/API/Backup/Cleanup/Expiry/Webの同path/argv/ignore_errors＋exact n/a,n/a,0,(null),0/0だけ（Morningは上記plain argv）、Inbox/Bootstrap全config exact。CaddyPre/Runは同old又はpaired exact未実行、他hardening/credential/RW/argvはexact。主要143/0や旧UNKNOWNをn/aから正常化しない。現runtimefileの除去以外のUnit source/宣言/rootapproval/current/epoch/DB変更はしない。

SSC229（2026-10-09、SS343当PG631/e492新一回用resume固定profile）：Root0755/ACL access-default無し空runtimeを保持dirFDでnew-only pg635-once-resume.confへ、署名base/native literal＋同run --resume二引数だけ、reload一回。全十主要18/旧INV/143-30/全kernel・DB原本を保持し、SSC220の補助metadata resetを当七Unitだけへ限定、Inbox/Bootstrap全config exact、CaddyPre/Run両同old又は両exact未実行・片側混合拒否。n/aを旧正常close/新readyへ読み替えず、全新scope/独立post後に別一回start・新親元1800s同RootordinaryAPI-Web-Caddyを要求。設計公開は実起動/native/正式未受入。

SSC228（2026-10-09、固定failed30 pending code-only）：SS343 SSC228のe492原本・既INVALID/Unit全停止/現PG621と新source36fe候補を再認証し、verify/activateではUnit/ExecStart/drop-in/reload/start/stopを変更しない。正規切替の全scope正常/独立post後だけ別new-only一回用同run resumeを準備する。物理activeを移動せず同cutoff/activationを維持、新親Invocationに対する元1800秒budget・既Unit期限・same Root/ordinary API-Web-Caddy/真正DONE・逆順owned停止を要求する。旧INV3a2de/status30/close未知は新成功へ読み替えない。REUSED_SUCCESS保持期限削除0とNEW_SUCCESS実削除再試験を分離し、API readyやobserver0だけを親成功にしない。設計only公開・実装/VM/native/正式未受入。

SSC227（2026-10-08、SS343新candidate completed profile）：現PG548/source969の正規PG573 DONEとPG579 owned全停止をfresh PG602で再読した上で、署名済unusedPG600/source23b/BOMa634へのcode-only更新を新M-A/専用DB/十Ref保持下で行う。既Unit/config/DB/migrationは同byte、旧143/failed履歴は保持する。候補のhostRO/typedBOM・有限INVALID/approval/current delta・全scope正常後だけ配備を認定し、その後の通常Morningは新runで当source実Root→ordinary/真正DONE/逆順owned停止/native/CHRを閉じる。親30分/既Unit期限・固定agent/profile/nonreset/new-only/所有/identity/socket/info・SS343/451品質を変更しない。旧native18を変更三classへ輸入せず、新candidate未受入・設計only公開と区別する。

SSC218（2026-10-08、SSC187内部admission補足）：完成証拠のBackupObservationはList.copyOfした二rowと同runを上流constructorで固定する。MorningCompletionEvidenceは、nonnull確定後、全Backup rowのrunをbegins.database.runへ照合してから、begins二run・完全DB/Config handle・Backup target・outcome/manifest/exitcodeを合同し、各Backup resultとCleanup/Expiryのrun/result/receiptを検査する。handle完全等値から暗黙に導かれるrunを後段で再び拒否条件にせず、異runの有効typed pairと同run異handleをそれぞれ独立拒否する。全既拒否条件・固定diagnostic/redaction/純data性・正常/異常入力の受入集合を保持し、guard削除/人工反射/coverage除外・DBやauthority再構成はしない。独立正常/各境界/上流immutable pairの再発防止、当新sourceのfresh全回帰/静的解析/四counterと必要native同source再束縛を行い、旧別source成功を流用しない。RD/UI/DIF/画面/電文/DB契約は不変更。設計公開は実装・正式品質完了ではない。

SSC203（2026-10-07、BUG799/YKT570、SSC185内部境界補足）：完了の各compound DB read（Backup観測・Cleanup観測・Cleanup元参照全列/seal・Expiry再読）は、その直前/正常帰還直後のTX外で全Root/保持原本graph/同ordinary API-Web-Caddy世代・identity/socket/info/ready/run整合を独立に再認証する。SQLごとのTX内owner callbackは同owner-thread/alive/未確定完了禁止、同保持Sessionの六namespace inode/security、Root/M/A、元残budgetの継続検査を行い、全graph/HTTPの同じ証明を毎SQLへ再帰展開せず、DB再入・commit/rollbackはしない。全graph/全row/seal/receiptの実再読、SSC187各typed intent退役前後と原本DONE直前の全証跡再読は維持する。cache/別Connection/guard削除/no-op/期限延長/UNKNOWN正常化を禁止する。compound後の変化は成功を返さず隔離、SQL中の所有/namespace/期限失効も非成功。RD/UI/DIF不変更、独立境界・失効・再入拒否PTと変更群fresh回帰/実nativeを必要とする。

## SSC234 同期CLOSING採取（2026-10-09、隔離PTのみ）

SSC196のINSPECTOR/BOOTSTRAP ordinary二roleだけ、同main ownerが同checkpointのTERMINAL export/callback正常帰還と業務entryのreturn/既診断を確認後、固定`<INV>.closing.exec`を一回同期採取する。追加hook/vendor hook順序依存0、Root execve/BEFORE_EXEC及びAPI/Web stop-holdは不変更。default agent無しは両点I/O0。TERMINAL失敗は従来通り、CLOSING失敗はBootstrap50/Inspector既IOExceptionへ固定診断、全正常export/postcheck帰還後のみ`Bootstrap|Inspector fixed PT native closing complete`を出す。元Unit権限/phase/session/argv/owner/receipt/期限/親30分を維持する。CLOSINGは業務成功や正常停止を発行しない、実終端/全資源後条件は独立認証する。

## SSC196 真正Inspector・Bootstrapの隔離PT terminal採取（2026-10-06）

SSC193/195の固定pin公開agent/held新inode採取を二roleだけ拡張する。対応はINSPECTOR→`schubert-nk-inbox-inspector.service`/既`resolveInspector()`、BOOTSTRAP→`schubert-nk-bootstrap-admin.service`/既schubert-api固定UID・primary GID・全必要groups。これらはphase ORDINARY/TERMINALのみ、session literal `INSPECTOR|BOOTSTRAP-<INV>-ordinary`、API/WEB alias・Root/before-exec・起動proof/profile転送を拒否する。既API/WEB四profileは不変更。agent無しdefaultは採取/I/O0、既argv/environment/receipt/exit/owner/元Unit期限・親30minは不変更。隔離配置時だけ既wrapperのJava optionに固定pin agent一項と必要roleのReadWritePathsを加える。任意option/path/socket/環境forward0。

Inspectorは既writeの正常帰還後に終端採取し、wrapperは従来どおりexact receipt＋JVM正常終端を判定する。Bootstrapは既runの全owned resource帰還と固定finished診断後・System.exit前に採取する。採取失敗は元正常0/10/20として受け入れず固定失敗診断/非成功終端とする。採取は実INV・Unit cgroup・NSS/groups/zeroCaps/NNP・pin・新private inode/正常close/dirsyncを前後照合し、データを起動権限/親成功へ使わない。新runでInspectorへ進む際はSS341のday＋step success/running/attempt条件と原本・旧Backup保護を先に独立照合し、成功済SKIPへ再検証operationを追加しない。Bootstrap既存20は別new-only合成2credentialだけを正規公開/退役し、退役済原本/activeaccount/全DB値不変を照合する。fresh全6→signed/current同source→各single/nativeNoMatch0・fulljournal/kernel/owned帰還・未網羅の独立記録を要する。正式/ITST合格の宣言ではない。


SSC195（2026-10-06、BUG754/YKT534、SSC193親FD補足）：普通UIDのheld O_RDONLY directory FDに必要なread/traverseのため、固定4role名だけを持つ非秘密pt-coverage親はSS343のRoot:Root0755・ACLなしとする。各role0700/exec0600、agent pin/RO/UID/groups/NNP、元scope/security/budget/defaultは不変更。operatorは正常owned停止/M/A/DB・原本Backup/旧exec保全を確認した区間でのみ既存親0711の同inodeを一回0755へ変更、runtimeはmode照合のみ。親readは固定role名を読むためだけで、private child内容/exec/session/credentialへ権限を付与しない。真正普通UIDで711拒否755成功を独立確認し、Rootだけの成功を両ordinary/nativeの代用にしない。

SSC194（2026-10-06、SSC193の普通TERM採取接続補足、BUG753/YKT533）：PT profile有効時だけ、既application Lifetimeの外側に固定main所有のstop holdを一つ設ける。追加hookはprovider操作/close/exitをせず、mainの採取完了又は非成功unwindまで待機する。元application hookのfinished解放だけでJVMがhaltしmainのdumpを切らない。mainは外側hold登録/owner照合→既runの全owned business scope帰還→既stopped診断→SSC193新terminal採取/全newfile及びdir正常返却→owner再照合/固定非秘密capture-complete診断→外側hold通常close→既終了要求の順。defaultは追加hook0、既停止・UNKNOWN保持・143を0へ補正しない意味・元Unit及び親期限・2FD/securityは不変更。Runtime.removeShutdownHookの正常true、not-owned false、不正null、及び公開APIが規定するshutdown-in-progressだけを分離し、thread.isAlive/GCから推定しない。失敗時は採取/marker/終端だけを完全成功へ流用せず、fatal/partial/不明及び全kernel後条件を含む独立native判定を要求する。host決定的並行及び実子JVM TERM143はcomponent証拠、実API/Web/native100/正式の代用ではない。

## SSC193 隔離PG/PTの固定native採取（2026-10-06、内部補足、業務仕様変更なし）

§4.2/§5のProduction既定argv・5環境項目・A/proofの2FD・same-PID exec・固定NSS/UID/GID/groups/caps/NNP・署名/current/Root全gate・親及びUnit元期限は不変更。隔離PG/PT VMだけで、Root管理agent `/opt/pgpt-tools-pg390/jacoco-agent.jar`（JaCoCo0.8.15、307843byte、SHA256 `fb5b0036a0899ea97edfa0fc2c7985b55f3f7c5695028163e5e60d4f3cf6075d`、Root:Root0644・parent0755・ACLなし・実Unit mountでRO）を完全一致で認証する。閉じたoptionは`-javaagent:<上記固定path>=output=none,append=false,dumponexit=false,sessionid=ROLE-INV-phase`の一項だけ、ROLEはAPI/WEB、phaseはroot/ordinary、INVは同managerが生成した非zero lowercase32hex Invocation。Root Unitの`${INVOCATION_ID}`展開値をRoot捕捉世代と照合し、同role ordinaryの固定Java argv index9へこの一項だけ引き継ぐ。JAVA_TOOL_OPTIONS、任意option/path/env、socket/TCP/JMX、attach/reset、private反射、Production compile依存、coverage除外は追加しない。既定及び無関係host agentでは当採取を有効にせず、予約prefixの重複・他role/phase/INV/未知optionは拒否する。

agentは`output=none`でpremain/終了時のpath作成・切詰め・再openを行わない。公開RT.getAgentとIAgent.getVersion/getSessionId/getExecutionData(false)だけを公開methodで呼び、pin済CodeSourceと固定version `0.8.15.202606040825`、前後sessionを確認して5byte以上16MiB以下の新規exec byteを取得する。実Root full preflight及びowner/元budget再照合後、exec直前に`<INV>.before-exec.exec`を当Root専用領域へ新規書込し、全新file/dir FDを正常閉鎖した後にRoot/owner/元budgetを再照合して既存2FDだけを継承する。failed execのknown終端は別`<INV>.terminal.exec`、未知/未帰還を正常へ変換しない。before-exec dumpだけでexec成功を認定しない。

ordinary API/Webは既存runの全owned application scopeが実際に帰還し、既存stopped診断を行った後・既存終了要求の前に、同role/INVの`<INV>.terminal.exec`を記録する。UNKNOWN保持やlive runの途中から終端dumpを捏造しない。採取点のattemptはagent/I/O前に一回消費し、partial/未知/既存fileを再試行・修復・成功扱いにしない。出力はSS343 SSC193のheld新0600 inode契約を用い、実Root/ordinary世代・NSS/cgroup/INV・pinを前後検証する。Root profileだけ通常普通argvへの型付き項目を許し、普通mainの起動権限を当profileから発行しない。

UnitのPG/PT限定ReadWritePathsは当role Root/ordinaryの新専用directoryだけを追加し、既存転送領域・UMask0027・最小権限は維持する。実dumpに同source/frozen class byte、boot/Invocation/PID/start/session/time、真正owned stop/manager journal/全kernel後条件を結び付け、失敗・skip・未実行・別sourceを100%へ算入しない。SS343/451及びPT-OPS-NC193/REXEC193/NFILE193/NCHECK193/NEXPORT193へ横断追跡。設計確定は実装・fresh全6・実native・正式認定の完了を意味せず、これらは台帳に未受入で維持する。

SSC187：API/Web/Caddyの同世代ready後も、正規原本DONEの直前・typed intent退役前後に実保守証拠を再読する。Backupだけは明示停止済みの同MorningBackupUnitCycle＋元TerminalReceiptを用い、completedReceipt参照同一/recheckCompletedBackup（同owner/baseline/stop結果/全kernel）を要求する。停止前KEEP_ACTIVE receiptの現存を再要求しない。Cleanup/Expiryの保持receipt、純peerとTX外DB整合、真正Root→ordinary/同socket/info/identity、原本の保持能力、元budget、逆順停止・UNKNOWN保持は変更しない。opaque cycleを実callback内で引き継ぎ、receipt値だけからownerを再構成したりno-op gateへ置き換えたりしない。SS341/343 SSC135136及びBUG704/YKT506、実装/PT/native未受入。

SSC137/S3失敗停止追補（実装前）：pending起動のAPI/Web slotは同M/原本/正常A後の親が、真正cold全Unit確認→durable intent→正常start client→実Root世代二読→launch公開まで所有する。未完成ordinaryが50等で退出してもRestart=on-failureを成功又は別起動のreadyへ読み替えない。捕捉した元PID/startTicksの真正proc消滅を同boot/root/Morningの下で二読後、固定slotを通常stop clientで停止し全Unit/kernel空を確認する。UNKNOWN/未捕捉/stop不明/終端不明では元M/DB/原本を保有して外側期限まで隔離。全停止した失敗は当回permit revoke＋残intent保全で非成功終了し、GC/coldから成功receiptを生成しない。これは境界接続の失敗枝でありready/completed/M最終close保証は別未受入。

SSC137/S3内部接続（2026-10-01、実装前）：API/Web RootはA取得後、当回実ISSUED・原本・ownerと自己Invocation/PID/startTicksを検査する。pending枝では同Morning真正生存/元単調期限に加え、A正常close・発行commit後にその親が真正start client正常帰還/対象Root manager-kernel-manager二読後公開した自己launchが必須。completed枝は同activation真正done0/10・全graph/active/pending無し・同Morning正常0/10/fullkernel終端receiptが必須、旧pending ticket/GC/空Invocationで代用不可。全release/config/六root/schema/BrokerOpsの正常close後、actual A FD/dev/inoと実17field sealed proof、保持setpriv ELFを既存native execへ接続する。固定Java唯一link /usr/bin/java→/opt/jdk-25.0.4/bin/javaのroot管理chain/version/ELF/前後一致を検証、A期間の管理者変更は禁止。別PID fork/第三継承FD/shell/任意argv/秘密envは禁止。Root候補capは用途限定で実測、ordinary childは五cap全部0。API/Web全業務ready後だけA解放/次service/Caddy/DONEへ進む。Morning全0/10は全resource/M正常close後だけ。M最終close未知後の既ready停止競合は別未受入、成功扱いしない。現未完成Rootやunassembled ordinary50は限定境界観測でありUnit完成認定ではない。

SSC127/BUG375：vendor Artemis Unitだけに`SuccessExitStatus=143`を指定し、Javaの正規SIGTERM/Shutdown hook完了後の通常exitをinactive/deadとする。143をworker成功へ流用しない。旧Unitのfailed143はreset-failedせず、SS343§6.17のsame-invocation全停止journal・全kernel終端・Code1/時刻を独立確認したときだけ次fresh起動のbaseline dataへ使う。SIGKILL/timeout/signal/unknown/不正journalは拒否。固定Stop policy/control-group/SendSIGKILL=no/Restart=on-failure/zeroCapsは不変更。未起動trusted候補配備は旧/new署名BOM・実旧8Unit byte・M/A/全終端を保持し、Artemis固定1directiveだけを追加する（既存drop-in/設定/失敗stateを修復しない）。

SSC111/SSC109補足：root Cleanup/Expiryも署名release原本をPID1 host viewで読むためroot prestartに限りCAP_SYS_PTRACE/CAP_DAC_OVERRIDEをbounding setに残す。Ambientは空、NoNewPrivileges/ProtectSystem=strictを維持し、API/Web/Backupの最終worker zeroCapsを変更しない。Expiryはoneshot/Restart=no/RemainAfterExit=yes/SuccessExitStatus=10/TimeoutStart=10min/TimeoutStop=60s/KillMode=control-group/SendSIGKILL=no/Delegate=no、Artemis After/Requires、親の明示startと同残budgetで管理する。private残留requestをRuntimeDirectory自動消去で隠さない。未完成PGPT candidateの配置は隔離VMで保全後だけ行い、production enable/正式合格としない。

SSC107/BUG322（PG/PT）：親Morning候補の`Type=simple`＋`TimeoutStartSec=30min`はJava親全体の上限でなく、`Before=Backup/Cleanup/...`も親処理完了barrierにならない。親を`Type=oneshot`にし`TimeoutStartSec=30min`を実行中全体に適用する。親から子への`Before=`は外し、親がM/A/原本を所有して固定Unitを明示起動する。morning targetは親だけを`Requires`し`After`で親完了を待つ。旧「全unitをWants」は廃止し、子の並列自動起動を禁止する。`SendSIGKILL=no`と後続保全を維持し、timeout時にOS lock解放/Unit終端/marker修復を推定しない。実効Type/MainPID/timeout、短縮隔離probe、全Unit依存順と親の30分単調budgetはPTで確認する。Web/API/Artemis `Type=simple`の個別readinessは引き続き別pollであり、その`TimeoutStartSec`を長期稼働期限へ転用しない。RD/UI変更なし。

SSC191（BUG720/YKT511、QA047内管理操作）：普通API/Webが真正ready後に管理者所有の正規`systemctl stop`を受けた場合、JVMの全owner正常返却後のSIGTERM終了はCode1/status143、旧Unitではfailed/failed/result exit-codeになり得る。143単独・manager冷停止・GCを正常scope返却/worker成功へ読み替えない。生存時同boot/Invocation/PID/ticks・ordinary identity/署名class/Unit・start、停止後full18/時刻/固定policy/kernel/旧PID消失を束縛し、同Invocation全journal（未選別、最大4MiB）からtrusted PID/UIDのexact `API|WEB cleanup complete`→`API|WEB process stopped`各1を順序・start～end内で確認する。重複key/cursor・foreign/null/未知型・不正UTF8・未知cleanup/fatal・未完/信号/timeoutは拒否。これは当管理停止の独立witnessでありUnit成功、親0/10、旧工具close成功ではない。固定UnitへのSuccessExitStatus143追加やreset-failedだけで表示を修復しない。後続は新fresh owned起動、ready/全後条件を別に実証する。保持工具のhandoffはSS343 SSC191/SS353§20.2の別限定入口に従う。

## 1. 目的・状態

Caddy、systemd、PostgreSQL、Artemis、Web/API/batch Java processの初期実効値、入力file、port、resource上限、
hardening、timeout/readinessと検証方法を定める。

- 状態: `確定`。Artemis再配送・容量とDB backup role分離はQA-041～043/UIC-001～003承認済み
- 上位設計: UI 211～212、231、251～253
- 関連RD: SYS-002～SYS-004、SYS-012～SYS-014、OPS-001～OPS-012、MON-001～MON-013、
  PER-001～PER-010、AVL-001～AVL-010
- 関連QA/RDF/UIC: QA-007、QA-010～QA-011、QA-016、QA-021～QA-022、QA-027、QA-029、QA-041～QA-043、RDFなし、UIC-001～UIC-003
- 関連SS: [321_Artemis物理構成・JMS設定設計](../320_メッセージング/321_Artemis物理構成・JMS設定設計.md)、
  [341_朝batch・backup・削除・再実行設計](341_朝batch・backup・削除・再実行設計.md)

## 2. Host・network・port

| Component | Bind/default | Public firewall | 備考 |
|---|---|---|---|
| Caddy HTTPS | `<global-ip>:55160` | allow 55160/tcpだけ | TLS終端、初期internal certificate |
| Web HTTP | `127.0.0.1:8080` | deny | Caddyからだけ |
| Web management | `127.0.0.1:8081` | deny | health/readiness/metrics、Caddy非proxy |
| API application HTTP | disabled | deny | Browser/HTTP APIを持たない |
| API management | `127.0.0.1:8091` | deny | health/readiness/metrics |
| Artemis CORE/JMS | `127.0.0.1:61616` | deny | Web/APIのみ |
| Artemis console | `127.0.0.1:8161` | deny | OS tunnelと専用管理credential |
| PostgreSQL | `127.0.0.1:5432`,`[::1]:5432` | deny | app/migration/batchのみ |

OS firewallはdefault deny inbound、55160/tcpのみallow。Loopback serviceを`0.0.0.0`/`::`へbindしない。
Port変更はconfig manifestを更新し、firewall・Caddy・client URL・health probe・ITを一括反映する。

## 3. Caddy

SSC186（2026-10-05、内部補足）：Caddy startの同owner複合fenceは、scope前後に両ordinary peer/current/launch/identity/socket/info/ready→同DB整合→両peerを確認する。その間のAPI/Web各intentは既存context→純粋owner→same token/inode/current/permit→純粋owner→contextを保持し、局所ownerは同Root/M/保持原本/元budgetだけを検証する。局所intent検査へfull両peer/同DB再検査を再入させず、複合前後へ集約する（検査省略ではない）。起動preflight前の既存起点で親の同Linux単調remainingNanosから30秒の下限を一回固定し、起点を遅らせたりpollで再生成したりしない。親残量が30秒未満なら親期限を優先、境界同値/clock異常は拒否。System.nanoTimeのprocess-local originとLinux絶対期限を混ぜない。真正Caddy ready認証の前後に当起動期限を要求し、成功後の継続peer/DONE/退役検査は元親期限で拘束する（成功後も30秒startup期限を継承して健全なdaemonを拒否しない）。Caddy30秒/親30分、全固定認証、失敗時逆順全終端/不明保持、RD/UI/業務仕様は不変更。

SSC178（2026-10-04）：親の固定Caddy startはworker oneshot ABIを使わず、固定daemon実効profile・真正manager/kernelの同boot/Invocation/MainPID/startTicks/cgroupと本人listenerを前後照合する。`caddy validate`成功は起動成功でなく、実daemonとTLS検証付きHTTPS `/login` 200まで必要。API/Web同世代readyの連続確認と両intent保持を送達不明のfenceとし、別start/restartを二重発行しない。元親30分及びCaddy30秒期限を維持し、失敗時公開停止・逆順全終端/不明隔離はSS341§10へ従う。

### 3.1 Caddyfile論理形

`<GLOBAL_IP>`、certificate、upstreamは配備時にrenderし、Gitはplaceholder付きtemplateを管理する。

```caddyfile
{
    admin off
    auto_https disable_redirects
    skip_install_trust
}

https://<GLOBAL_IP>:55160 {
    bind <GLOBAL_IP>
    tls internal

    request_body {
        max_size 2MB
    }

    header {
        Strict-Transport-Security "max-age=31536000"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "same-origin"
        -Server
    }

    reverse_proxy 127.0.0.1:8080 {
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-Host {host}
        transport http {
            dial_timeout 2s
            response_header_timeout 30s
            read_timeout 60s
            write_timeout 60s
        }
    }
}
```

- `file_server`、asset/transfer root、Caddyの直接media配信を定義しない。
- Caddyは外部から受けた`Forwarded`/`X-Forwarded-*`を信用せず、直接peerから再構成する。前段proxyなしのため
  `trusted_proxies`を設定しない。Webはremote addressがloopbackの場合だけCaddy headerを採用。
- CSPは352 §7.2のfixed allowlistをWebが設定し、Caddyで上書きしない。Inline script/styleを許容しないためnonceも使用しない。
- Access logはJSON、path/status/duration/bytes/remote IP/request IDだけ。Cookie、Authorization、query string、request/response bodyを
  filter除外する。Filter非対応の導入minorではaccess logを最小化し、Web WLGEVT01を業務監査正本とする。

### 3.2 TLS・検証

- QA-022に従い初期はCaddy internal CA/IP certificate。警告を許容するがHTTPへdowngradeしない。
- Private keyはCaddy専用state/credential、root/Caddyのみ読取。Fingerprint、有効期限、検証手順をconfig manifestへ記録。
- Domain/公的証明書移行時はsite address/TLSだけ変更。`tls_insecure_skip_verify`はupstream/clientとも使わない。
- Deploy前に`caddy fmt --diff`、`caddy adapt --validate`、`caddy validate`、起動後TLS/header/loopback upstreamを試験。

SSC178内部配備補足（2026-10-04）：初期IP/internal CAの公開入口は55160だけで、admin API・HTTP80への自動redirect listener・host trust store自動書込を無効とする。固定IPはliteral IPv4又はbracket付きIPv6、bindは同じIP（IPv6ではbracketなし）、DNS・proxy・任意URLへの変更は受けない。外部業務画面や既定55160のTLS契約は不変更。固定Caddy daemonはUser/Group=caddy、SupplementaryGroups空、Type=notify、Restart=no、start/stop30s、KillMode=control-group、SendSIGKILL=no、NoNewPrivileges=yes、bounding/ambient五capを全0、UMask0027。ExecStartPreは単一 `/usr/bin/caddy validate --config /etc/caddy/Caddyfile`、ExecStartは単一 `/usr/bin/caddy run --config /etc/caddy/Caddyfile`、任意wrapper/reload/環境出力を使わない。親はdelivery前のcold実効profileと固定configを読み、成功後はfresh Invocationの実validate終了0、同manager/kernel/cmdline/ordinary identity、本人FDの同IP55160 LISTEN inodeとHTTPS200を前後確認する。

固定configは `/etc/caddy/Caddyfile` root:caddy0640・single-link・no ACL、祖先はroot:root0700/0750/0755の固定directory（配備時に既定0755を維持）。公開CAだけを `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt` から読む。`/var`及び`/var/lib`はroot:root、caddy以下はcaddy:caddy、directory0700/0750/0755・no ACL、証明書0600/0640/0644・single-link・上限64KiBとする（SSC183：Caddyが生成するowner-only0600も固定公開CAにだけ許す、設定0640専用は不変更）。保持inodeの前後同一性と証明書のCA属性/有効期限を確認し、そのCAだけをtrust anchorとして通常hostname検証を維持する。private key・credentialを親の証跡へ取得せず、TLS検証無効化、未知CA代入、旧/run復元をしない。署名candidateのconfig template/BOMを確定してから正規配備し、未配備distributionのdefault profileを合格にしない。実VM/coverage/正式認定は別途未完了。

SSC180（2026-10-05、BUG680/YKT485）：Caddyのcoldは「一度も起動していない」ことと同義ではない。delivery前の固定profileに加え、真正managerの `Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic` を固定追加読取し、既存12field/全cgroupの型付きquiescent Observationとの同Invocation・同停止状態を照合する。固定config/Root親/当M・DB・原本・元budgetは継続所有する。前後同じmanager・同terminal・同kernelが必要で、未実行と正常停止履歴は次の二ケースだけとする。

- 初回no-history：inactive/dead、MainPID/ControlPID0、Job空、Invocation空、Result=success/ExecMainCode=0/ExecMainStatus=0、start/exit monotonic0。固定単一validate/runの実効設定はあるが両Exec entryのstart/stopはn/a・pid0・code(null)・status0/0であり、実validate成功を捏造しない。
- normal-history：inactive/dead、各PID0/Job空、全kernel空、非zero32hex Invocation。Result=success/ExecMainCode=1/ExecMainStatus=0、start monotonic>0/exit>=start、単一validateとdaemonの真正Exec entryがいずれもcode=exited/正常0・実start/end非n/a・非zero PIDである。実systemdの正常0表現はstatus=0、既存fixture互換0/0も値0だけを受け、signal/非zero/未知表示・異常履歴・矛盾・driftは拒否する。

捕捉したcoldの前Invocationを同親のCaddy start factory/preflightまで拘束し、CLI発行前に同coldとwhole-kernelを再照合する。起動後のreadyは当captureと**異なるfresh Invocation**で、Result=success/未終了code0/status0・start>0/exit0、真正validate正常0、既存同manager/kernel/ordinary identity/本人FD55160/TLS200の前後検査を満たすこと。旧Invocationをfreshへ使わず、start受付だけの成功認定、reset-failedによる履歴抹消、旧/run復元・旧permit再利用はしない。start/stop各30秒、親30分及び失敗時Caddy→Web→APIの逆順停止・不明時所有保持は変更しない。RD/UI/画面・電文・業務の変更を伴わない内部再起動境界の補足であり、設計公開は実装/PT/native/正式完了とは区別する。

SSC192（2026-10-05、BUG730/YKT517）：normal-historyの補助Exec履歴について、正規daemon-reload後に保持された正常停止F18と、両Exec entryがexact未実行表示へ戻る組合せを補足する。固定config、inactive/dead、MainPID/ControlPID0/Job空/全kernel空、非zero32hex旧Invocation、Result=success/ExecMainCode=1/ExecMainStatus=0、start monotonic>0/exit>=start及び前後同一manager/kernel/Root/M/DB/原本/元budgetは緩めない。補助履歴の許容集合は、従来の「validate/run両方正常実行」又は「validate/run両方が固定path/argv/ignore_errors=no・start/stop n/a・pid0・code(null)・status0/0と完全一致」だけとする。片側だけ正常/未実行の混合、改変、欠落、null、未知、異常F18は拒否する。この保持F18は旧世代を新readyから拒否するためのdataのみであり、n/aから旧validate実行成功・旧close正常・新readyを認定しない。初回no-historyの空Invocation/Code0/startexit0条件と、新起動の異なるfresh Invocation・真正validate実行・ordinary identity/本人socket/TLS・全通常返却条件は不変更。reset-failed/履歴抹消/Unit期限変更/旧permit復元はしない。独立literal反例と同source fresh全回帰、実親から新Caddy/DONE/退役後条件の実証まで実装受入は未完とする。

## 4. Systemd dependency・unit設定

SSC181（2026-10-05、BUG685/YKT490）：専用Caddyの実効NSS groupsはprimary `caddy`だけで、kernelの全Uid/Gid及びgroupsを固定identityへ一致させる。`SupplementaryGroups=`の空設定はsystemdの追加指定を消すだけで、accountの既存NSS supplementary所属（distributionの`www-data`等）を削除しない。配備管理者は起動前にgetent/passwd/group/idの実値を前後認証し、未知・余剰groupがあれば起動gateを緩めず配備未完として隔離する。実測で特定済みの当VM `caddy`→`www-data`余剰所属だけを是正する場合、真正M/A/限定DB所有、固定全Unit/kernel終端、同署名/current/原本/Backup/DB/旧記録の完全保全を先行し、root私有before-imageを同期保存してから管理者の正規group操作で当memberだけを除去する。primary/passwd/他group/他memberは不変更、現在NSSが専用primaryのみ・完全保存後条件・全owned scope正常帰還を確認し、未知・途中失敗は隔離/所有保有とする。Applicationがgroupを自動修復せず、一般的usermod/全group再作成・権限緩和・既存原本/permit復元は禁止。真正fresh Caddy identity/TLS/DONE/intent/親全終端及び独立反例の再試験まで実環境の完了とはしない。上位業務/RD/UI/公開port/画面の変更を伴わない内部配備補足。

SSC101/PG318: Caddy package実Unitの既定 `SendSIGKILL=yes` を親保守停止へ採用しない。NK専用非起動drop-inで `SendSIGKILL=no` と `TimeoutStopSec=30s` を設定し、daemon-reload後の実効 Id/LoadState/KillMode/SendSIGKILL を親の固定8対象と同じ閉集合で確認する。既定Caddyを実測せずにpolicy合格としない。policy確認はstop client/全cgroup終端/Artemis journalの代用でなく、未配置Unitのfake/alias禁止を維持する。

### 4.1 Dependency

| Unit | `After` | `Requires` | `Wants`/note |
|---|---|---|---|
| `schubert-nk-backup` | PostgreSQL | PostgreSQL | 失敗はmorning続行 |
| `schubert-nk-cleanup` | backup | PostgreSQL | Backup成否はDB rowで分岐 |
| `artemis` | cleanup | cleanup | Cleanup safety failureで起動不可 |
| `schubert-nk-expiry-cleanup.service` | Artemis | Artemis | API Consumer前に実行。SSC099: SS341§2の完全名、別名expiry-cleanup.serviceを作らない |
| `schubert-nk-api` | expiry, Artemis, PostgreSQL | Artemis, PostgreSQL | SSC139: expiryの実前処理は正規issuer/Root許可で必須、API dependencyによる保守子再実行は禁止。readiness poll後にWeb |
| `schubert-nk-web` | API, Artemis, PostgreSQL | API, Artemis, PostgreSQL | technical DBが必要 |
| `caddy` | Web | Web | Packageの自由先行起動をdisable |

SSC104/PG324：上表Cleanupはroot MorningがM/A保持中に同期起動する真正oneshotであり、空の成功Unitを置かない。固定非秘密requestはsystemd `LoadCredential`でprivate受渡しし、`db-batch`はroot Cleanup専用processへ固定配布する。Unitの0/10は実削除・skip/警告・transferを記録した親検証済終端だけに対応し、safety failure/起動不明は非成功でArtemis `Requires`を遮断する。root実行権限は現物backup root/原本検証のためだけで、shell/任意argv/env/Secret出力は禁止。service templateの完成・配備は全親/子契約と別PTを経るまで未認定。
SSC104/PG326：子のroot contextは`schubert-nk-cleanup.service`自身のUID0、固定PID1/boot、自己PID-start/InvocationID/MainPIDと厳密cgroupで認証し、親`schubert-nk-morning-controller.service`のcontextを流用しない。起動時と帰還時に再確認し、異Unit/変更/不明は削除0・非成功。これはM/A/原本・両backup・DB advisoryを証明しない。

`schubert-nk-morning.target`は親MorningだけをRequires/Afterし、通常bootの`multi-user.target`からWantsする。親が全子を順序起動・終端照合し、BackupのFAILEDは
親がその事実を同runへ記録してCleanupの削除skipを選び、後続起動する。子をtargetから並列Wantsしてはならない。

SSC108/PG379補足：許可のprestart観測はSS341§5.1/SS343§6.17の固定集合とする。親/各worker/ArtemisのInvocationは真正managerとhost kernelの同一boot観測へ束縛し、command client exitを結果としない。Morning root Unitの保持root書込みとPID1由来確認に必要な最小権限・ReadWritePathsは実配備で照合し、未配置Expiryを空成功Unitで代用しない。API/WebのzeroCaps契約は変更しない。host injected PTと実VM coverageを同一sourceへ束縛し、外部main/namespace/native分岐を除外しない。

SSC109実装前：親候補はstrictを維持して`ReadWritePaths=/run/schubert-nk /var/lib/schubert-nk/maintenance /srv/schubert-nk/backup`の固定mutation対象へ限定する。共有/run,/var,/var/lib,/var/lib/schubert-nkを広域RWへしない。root親CAP_SYS_PTRACEはPID1由来確認、CAP_DAC_OVERRIDEは専用backup0700内のroot-owned archive生成に用途限定し、実VMで最小性を確認する。全CAP許可/ProtectSystem=fullは回避策にしない。API/Web/BackupのzeroCaps及びcredential配布範囲は維持する。単なる設定候補を実Morning受入へ算入しない。

### 4.2 Java service共通

SSC-087: root前段も共通sandbox内で動き、ProtectSystem=strictを解除する`+`/shell/setnsは使わない。PrivateUsers/PrivatePIDsや固定permit fileの古いbindを追加せず、PID1/system managerが同じhost/bootであることを検証する。root前段のread-only保持host能力だけで現在host FSを観測し、exec前に全closeする。普通serviceにはA短期FDとsealed公開proof以外のhost能力を移さない。private RO観測をhost故障のRO状態と混同しない。

SSC-086: 完成時の直接Java入口は同Unit/same PIDのroot前段`RootServiceLauncher`とする（ExecStartの`!` prefix、shellなし）。前段は既存root起動管理の全root/Ops/schema/現在起動許可をread-only検査し、native execveで固定`/usr/bin/setpriv`→固定`/usr/bin/java`→従来service mainへ置換する。!はSupplementaryGroupsも無効化するので、固定account/groupのNSS解決値を明示`--reuid/--regid/--groups`へ渡す。init-groups/任意account/任意commandは禁止。全bounding/inheritable/ambient capabilityをdropしNoNewPrivilegesを保持、最終UID/GID/groups/5cap fieldを子が再確認する。他のsandbox/ReadWritePaths/5個LoadCredentialは従来値のまま。root前段のprivate sourceはappへ移さず、前段の秘密copy/DB/JMSはexec前にcloseし、成功execでroot JVM全heapを破棄する。Aの短期同OFDとsealed非秘密proof以外を意図的に継承しない。!前段もtrust boundaryの一部としてPT対象、まだ完成していないProduction Unitは現状の拒否mainを維持する。

| Directive | Web/API | 理由 |
|---|---|---|
| `Type` | `simple` | Java processを直接ExecStart、shellを挟まない |
| `User`/`Group` | service別専用account | OS権限分離 |
| `WorkingDirectory` | `/opt/schubert-nk/current/<web|api>` | release symlinkのread-only artifact |
| `EnvironmentFile` | `/etc/schubert-nk/<service>.env` | 非秘密・0600 root:service、古い環境を残さない |
| `LoadCredential` | DB/MQ/AES/HMAC secretを個別file | Secretをenv/argv/Gitへ出さない |
| `UMask` | `0027` | 新規fileのgroup以外読取禁止 |
| `Restart` | `on-failure`, `RestartSec=5s` | Process/protocol異常復旧 |
| Start limit | interval 600s, burst 5 | Poison/config errorのrestart loop停止。UI 252と一致 |
| `TimeoutStartSec` | 120s | readinessは別poll、起動hangのbound |
| `TimeoutStopSec` | Web 30s/API 60s | UI 251のgraceful上限 |
| `SendSIGKILL` | `no` | Timeout後の自動強制終了を禁止 |
| `LimitNOFILE` | 65536 | MQ/DB/media FD、leak監視 |

SSC-080/BUG-256/YKT-192: Web/APIの必須EnvironmentFileは各々`src/deployment/config/<service>.env.template`から固定1行`SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk`＋LFをrenderし、root:service0600で配布する。systemd managerが読み、serviceは値だけを起動前検査する。重複・未知/secret/alias・JVM option・placeholder・CRLFを含むfileは配布前拒否し、Java側も受領した値が固定rootと一致しなければ設定file読取前に停止。実root/manager配布はLinux ITで確認する。JVM optionは引続きUnit固定、秘密はLoadCredentialのみであり、envへ追加しない。

SSC-075: 起動前のOps Core management属性照会はSS321 §10の管理namespace限定一時reply Address/Queue権限を用い、各request 2秒で打ち切る。systemdの120秒上限を個々の無期限broker応答待ちの代用にしない。Ops credentialはWeb/API application roleへ流用せず、management一時Address/Queueの作成/削除失敗・close失敗はreadiness falseとして残す。

SSC-020: APIのUser/primary Groupはschubert-api専用を維持し、Transfer読取group schubert-webをSupplementaryGroupsへ追加する。Asset用のschubert-readと同様、共有対象は承認済みdataだけであり、Web/APIのcredentialやprivate runtime fileをgroup-readableへ変更しない。APIが作った新規日付directory/partに限り、保持inodeへgroup=schubert-webと0750/0640を明示設定して検証する。既存root/childの所有者・mode不一致は起動/処理失敗とし、applicationが修正しない。Provisioningと起動probeでgroup membership・新規作成権限を検証する。

SSC-079/BUG-253/YKT-191: Web/APIのreleaseとconfigはUI243/SS343の`root:schubert` directory0750・非秘密file0640なので、両unitの`SupplementaryGroups`へ`schubert`を明示し、OS accountの暗黙の補助groupに依存しない。APIは既存`schubert-read schubert-web`、Webは既存`schubert-read`を維持する。`schubert`は非秘密release/configの読取にだけ用い、`/etc/schubert-nk/credentials`のroot:root0700、private runtime、service別LoadCredentialの秘密権限は緩和しない。PTではmode/groupの独立固定oracleと両unitのdirectiveを照合し、実Linuxでのgroup provisioning/credential分離と起動後の実読取はIT開始条件へ残す。

### 4.3 Hardening

Web/API/batchは`NoNewPrivileges=true`、`PrivateTmp=true`、`PrivateDevices=true`、`ProtectSystem=strict`、
`ProtectHome=true`、`ProtectKernelTunables=true`、`ProtectKernelModules=true`、`ProtectControlGroups=true`、
`ProtectKernelLogs=true`、`ProtectClock=true`、`ProtectHostname=true`、`RestrictSUIDSGID=true`、`LockPersonality=true`、
`RestrictNamespaces=true`、`RestrictRealtime=true`、`RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6`を初期値とする。

- Web read-only: asset/transfer/current/config。Writeは`RuntimeDirectory=schubert-nk/web`とsystemd credential参照だけ。
- API read-only: asset/current/config。Writeはtransfer rootと`RuntimeDirectory=schubert-nk/api`。
- Batch write: backup/transfer/runtime。Credential/configはread-only。対象root以外の`ReadWritePaths`を与えない。
- Java JITを破壊する`MemoryDenyWriteExecute=true`は適用せず、他directiveとservice accountで防御。

`systemd-analyze verify`、`systemd-analyze security`、実機のroot/path権限負testをrelease gateにする。

### 4.4 Timer

`OnCalendar=*-*-* 05:00:00 Asia/Tokyo`、`AccuracySec=1min`、`RandomizedDelaySec=0`、`Persistent=false`。
Missした05:00をboot時に即実行してreboot loopを起こさない。Miss検出はmonitor/alertと手動`morning-run`で扱う。

## 5. Java/JVM・Spring process

### Private Inspector unit補足（SSC-049、PG-D-144）

`schubert-nk-inbox-inspector.service`はUser/Group=`schubert-inbox-inspector`の固定非root専用identity、Type=oneshot、Restart=no、SuccessExitStatus=10、TimeoutStartSec=30min/TimeoutStopSec=60s、KillMode=control-group/SendSIGKILL=no。ExecStartはrelease内の固定receipt wrapper、Java main直接起動を親の成功判定に使わない。DB/current2の必須LoadCredentialとprevious2の選択profileは343 §6.8。EnvironmentFileはroot所有静的設定とroot所有per-run2値だけ。Java option/classpath/commandをbatchが任意上書きする仕組みを作らない。

§4.3のNoNewPrivileges/PrivateTmp/PrivateDevices/ProtectSystem=strict/ProtectHome等の共通hardeningを維持し、asset/transfer/backupへのwriteを与えない。readonly release/configとprivate runtime credentialだけを利用しHTTP/JMS listenerを起動しない。After/RequiresはPostgreSQL、Beforeは通常Artemis/API/Web/Caddy、通常起動順を変えず親cleanupの内部で同期起動する。既に動いているAPI/Webを子unitが勝手に停止するConflictsは追加しない。親のinactive確認・OS lock・backup照合は別gate。

検査中は通常API/Web停止のため、その未使用枠内でInspector heap Xms128m/Xmx512m、Direct64m/Metaspace192m、ReservedCodeCache128m、MemoryMax1024Mを上限とする。UTF-8/UTC/ExitOnOutOfMemoryError/enable-native-access=ALL-UNNAMEDを固定し、heap dump自動出力は無効。実RSS/GC/timeout/TERM/権限配布は後続Linux IT。PTはmain・wrapperの全終了分岐、template/directive/profileの独立matrixとShellCheck/systemd-analyze検証を記録し、実unit起動成功と混同しない。

### 5.1 Resource

| Process | Heap | Direct/Metaspace上限 | systemd `MemoryMax` | Native headroom | Thread/pool |
|---|---:|---:|---:|---:|---|
| Web | `-Xms384m -Xmx768m` | 128m / 192m | 1536M | 448m | HTTP 16/max32、MQ wait 12/max20 |
| API | `-Xms512m -Xmx1024m` | 256m / 256m | 2048M | 512m | Sync consumer 4/max8、async 1、DB pool 8 |
| Batch | `-Xms256m -Xmx768m` | 128m / 192m | 1536M | 448m | DB connection 1、step worker 1 |
| Artemis | `-Xms768m -Xmx1024m` | 256m / 192m | 2048M | 576m | 321のbroker thread/config |

Web/API共通: `-Dfile.encoding=UTF-8`、`-Duser.timezone=UTC`、`-XX:+ExitOnOutOfMemoryError`、
`-XX:MaxDirectMemorySize=<table>`、`-XX:MaxMetaspaceSize=<table>`、`-XX:ReservedCodeCacheSize=128m`、
`-Xlog:gc*=info:stdout:time,uptime,level,tags`。Native headroomはcode cache 128m、thread stack、GC/JIT/JNI、NIO、launcher/OS allocationを含み、
同時最大時にも`MemoryMax`との差を0にしない。
Heap dump自動出力は無効のままとし、機密値を含むdumpを通常log rootへ作らない。

ITはRSS/heap/direct/metaspace/thread/GC pauseを実測し、上位16GB配分内だけで調整する。メモリ上限を広げる場合、
PostgreSQL/Artemis/OS/headroomの合計16GB以内を同時更新する。

SSC-019/021によりTransfer writer/Readerはshared storageのJava25公開FFM限定native portを使用する。Classpath起動のAPI/Web（storageを使用するbatchも）へ`--enable-native-access=ALL-UNNAMED`を明示し、JPMS化する場合は該当module名へ限定する。Native accessはOS権限分離の代替ではない。Linux/glibc・procfs self FD・必要attributeを共通readinessで、renameat2 no-replace・directory fsyncをwriterのreadinessで検証し、不成立時は起動成功としない。Systemdの既存hardeningを外さず、実機ITでWeb read-only/API限定writeのFD相対操作を確認する。

SSC-022の診断専用probeは333 §7.4へ従う。業務producer/HTTP開始前のexclusive startupで所有済診断fileだけを検査・清掃し、失敗/不確定公開/cleanup failureでreadinessを成功にしない。通常業務ready非削除、Web read-only、hardeningは維持する。

SSC164（内部接続補足）：Morningのready判定は捕捉Rootと同一のboot/PID1/Invocation/MainPID/startTicks/cgroupを、ordinary移行後もmanager/kernel前後で照合する。UID0 Root認証を流用せず、固定NSS ordinary identity/全groups/五cap0/NNP1/固定mainを独立確認する。管理socketは本人FD inodeのexact127.0.0.1（IPv4及びIPv4-mapped IPv6）のみで、wildcard/::1/他inodeを拒否。HTTP200UPと発行permitのreleaseDigestに一致する保持manifest由来の5値を、同じsocket inode及び同親/API世代の前後検査で認定する。API ready→Web真正Root→Web全業務ready→Caddy/原本完了の既存順序は維持、ready単独を親成功にしない。同M/DB/原本/epoch・元30分budgetを維持、unknown/停止不確定は保全する。詳細PTと各scopeの採取不足は018/311及び456に記録する。

### 5.2 Spring主要値

SSC185（2026-10-05、内部TX/所有補足）：保持原本を完了する直前のBackup/Cleanup/Expiry evidenceは、同じ借用DBの短transactionで各後条件を再読する。そのtransaction内のowner callbackはRoot/M/A/原本capability・同ordinary API/Web/Caddy世代/identity/socket/ready・元残budgetの純粋な検査に限り、同ConnectionへのDB再読・commit/rollback・autoCommit変更を再入させない。DB全体のrun整合はevidence再読の前後及び各transactionの外側で独立検査し、transaction内のadvisory/timeout/role/SQL後条件は既存Repositoryで維持する。intent保持中と正規退役後のpeer条件を分け、各phaseのRoot/原本/peer検査をDB外側の整合検査の前後にも行う。別Connectionで旧ownerを代用・guard省略・権限緩和・UNKNOWN正常化は禁止。同DBのtransaction状態を保持する独立stateful試験と、元sourceの実失敗を保全したsame-source fresh回帰/実VM completionを必要とする。RD/UI/業務仕様・Current/DIFは変更しない。

| Key | Web | API |
|---|---|---|
| `server.address` | `127.0.0.1` | Main HTTP disabled |
| `server.port` | `8080` | `-1`相当 |
| `management.server.address/port` | `127.0.0.1:8081` | `127.0.0.1:8091` |
| Exposed actuator | `health,info,prometheus` | `health,info,prometheus` |
| Health details | loopbackでも`never`、component statusはlog/metric | 同じ |
| HTTP threads | 16 initial/max32、queue 32 | management最小 |
| Graceful shutdown | enabled、phase timeout 30s | enabled、phase timeout 60s |
| DB pool | Web technical max 2/min 1、connect 3s | max 8/min 2、connect 3s |
| JMS request wait | 2s、semaphore 12/max20 | Listener 4/max8、async 1 |

Actuatorはloopbackのみで、environment/configprops/heapdump/loggers/shutdownをexposeしない。`info`はrelease commit、
app/config/schema/protocol versionだけ。Secret/path/account/Queue bodyを出さない。

SSC158（API内部実現補足）：普通APIの管理HTTPだけはJDK HTTP serverで上記閉鎖契約を実現する。固定127.0.0.1:8091、GET `/actuator/health`・`/actuator/health/readiness`はstatusのみ、DOWNは503/UPは200。`/actuator/info`はstartup proofのactual release hashと一致する保持manifestから検証した5値のみ、`/actuator/prometheus`は秘密を含まないready gauge。その他path/methodは拒否。全31登録検証・DB/JMS/storage probe・Outbox開始・SYNC4/WebLog1/ASYNC1が揃い、同ownerがReady.releaseを正常完了した後のみUP。解放失敗又は停止競合は非成功、Aが空いたことやsystemd activeだけはready証拠ではない。stop/fatal/Outbox不健康でDOWNとし、新業務guard→consumer drain→Outbox join→codec/root→factory→pool/credentialを外側所有の順序で閉じる。hookはstop通知＋owner完了待ちだけ、callback threadから資源close/System.exitしない。取得中TERM/uncertain closeも成功receiptを作らない。Morning側のsame-PID socket/Invocation/startTicks前後照合と原本完了は後続実装であり、当HTTPのUP単独では親完了を認定しない。

## 6. PostgreSQL 18

### 6.1 `postgresql.conf`初期値

| Key | Value | 理由 |
|---|---:|---|
| `listen_addresses` | `127.0.0.1,::1` | Loopback専用 |
| `port` | 5432 | UI default |
| `max_connections` | 40 | API 8＋Web 2＋batch/migration/ops＋管理・復旧余裕 |
| `shared_buffers` | 2GB | 16GB host/PG 4GB budgetの初期値 |
| `effective_cache_size` | 6GB | OS cacheを含むplanner hint、allocationではない |
| `work_mem` | 8MB | 同時sort/hashの倍率消費をbound |
| `maintenance_work_mem` | 512MB | Migration/index/maintenance、app同時多重なし |
| `max_worker_processes` | 8 | 小規模single host |
| `max_parallel_workers` | 4 | CPU/メモリ上限 |
| `max_parallel_workers_per_gather` | 2 | 1 queryの占有防止 |
| `temp_file_limit` | 2GB | 異常sortのSSD枯渇防止 |
| `wal_compression` | on | WAL容量抑制 |
| `min_wal_size` / `max_wal_size` | 1GB / 4GB | Checkpoint・30GB DB budget |
| `checkpoint_timeout` | 15min | 小規模の初期値 |
| `checkpoint_completion_target` | 0.9 | I/O平準化 |
| `deadlock_timeout` | 500ms | API lock timeoutと合わせ早期検出 |
| `password_encryption` | `scram-sha-256` | MD5非使用 |
| `ssl` | off | Loopback内のみ、OS・rolesで保護 |

`log_statement=none`、`log_parameter_max_length=0`、`log_parameter_max_length_on_error=0`とし、password/質問本文の
bind値をPostgreSQL logへ出さない。Connection/disconnection、checkpoint、lock wait/deadlock、autovacuum、
error severityは記録するが、slow queryの本文はapplicationのquery ID/duration metricで代替する。

### 6.2 Roleごとのtimeout

SSC-069/PG-D-187（2026-09-20）: §6.1の運用eventを`log_connections=on`、`log_disconnections=on`、`log_checkpoints=on`、`log_lock_waits=on`、`log_autovacuum_min_duration=0`で具体化する。slow SQL本文は`log_min_duration_statement=-1`、`log_min_duration_sample=-1`、`log_transaction_sample_rate=0`で無効にし、失敗SQL本文は`log_min_error_statement=panic`、DETAIL/HINT/QUERY/CONTEXTは`log_error_verbosity=terse`で抑止する。error severityは既定の記録を維持する。PostgreSQL自身のprimary error MESSAGEには不正入力値を含む場合があるため、これだけで任意入力の秘密非出力を保証しない。型付きbind/入力検証・実配備のOS log/redaction確認は別gateとし、raw DB logをPTエビデンスへコピーしない。

根拠: [PostgreSQL18 logging](https://www.postgresql.org/docs/18/runtime-config-logging.html)。配備雛形は`src/deployment/postgresql/`、全directiveとHBA16規則をPT-OPS-PGCFG-001～008で独立照合する。log保存先/rotationは配備環境とSS351で管理し、雛形だけで全運用完成としない。

`schubert_backup`行と後続hba entryはQA-043/UIC-003承認済みのrelease値である。

| Role | `statement_timeout` | `lock_timeout` | `idle_in_transaction_session_timeout` |
|---|---:|---:|---:|
| `schubert_app` | 1500ms | 500ms | 15s |
| `schubert_web_session` | 1500ms | 500ms | 15s |
| `schubert_batch` | 30min | 5s | 60s |
| `schubert_backup` | 30min | 5s | 60s |
| `schubert_migration` | 30min | 5s | 60s |
| `schubert_ops_ro` | 10s | 1s | 15s |
| `schubert_inbox_inspector`（SSC-049） | 30s | 5s | 専用単発transaction、process上限30min。既存provisioningに未設定のidle値を設定済みとしない |

Long-running migrationは個別migrationで`SET LOCAL`し、roleの無制限化をしない。

### 6.3 `pg_hba.conf`

```text
local  all          postgres                              peer
host   schubert_nk  schubert_app,schubert_web_session,schubert_batch,schubert_backup,schubert_ops_ro  127.0.0.1/32  scram-sha-256
host   schubert_nk  schubert_app,schubert_web_session,schubert_batch,schubert_backup,schubert_ops_ro  ::1/128       scram-sha-256
host   schubert_nk  schubert_migration                    127.0.0.1/32  scram-sha-256
host   schubert_nk  schubert_migration                    ::1/128       scram-sha-256
host   schubert_nk  schubert_inbox_inspector              127.0.0.1/32  scram-sha-256
host   all          all                                   0.0.0.0/0     reject
host   all          all                                   ::/0          reject
```

実際のhbaはroleごと1行へ分割してreview可能にする。`schubert_web_session`のhba接続を許しても、
331のgrantで業務schemaは不可。Remote CIDR、trust、password、md5を追加しない。

## 7. Artemis process・config

SSC103/PG321：`artemis.service`は実instance `/var/lib/schubert-nk/artemis`を専用`schubert-artemis`で起動する。`After/Requires=schubert-nk-cleanup.service`は必須であり、cleanup未配置を偽Unit/依存無視で補完しない。trusted root側がprivate regular0600の`/etc/schubert-nk/credentials/artemis-users`にJAAS hashed user propertiesを事前配置し、Unitは固定`LoadCredential`でprivate `/run/credentials/artemis.service/artemis-users`を受ける。vendorの`etc/artemis-users.properties`期待場所へはUnit private namespace内のread-only bindを使い、host既存fileを上書き/削除しない。秘密値・raw propertyをargv/env/log/Gitへ出さない。Unit構文・実効policy/credential bind・専用UID・起動/停止・journal cleanはそれぞれ独立判定し、loadedだけをbroker readinessやclean stopへ読み替えない。systemd bind適用順の実測に失敗すれば安全停止し別SSCで再判断する。

- `broker.xml`、Address/Queue/security/JMS値は321を正とする。Acceptors 61616/console 8161はloopbackだけ。
- Instance root `/var/lib/schubert-nk/artemis`は`schubert-artemis` 0700、journal/paging/large messageは別subdirectory。
- systemd `MemoryMax=2G`、JVM heap 1G/direct 256M/metaspace 192M、native headroom 576M、`LimitNOFILE=65536`、`Restart=on-failure`、start limit 5/600s、
  `TimeoutStartSec=120s`、`TimeoutStopSec=60s`、`SendSIGKILL=no`。
- `global-max-messages=50000`、`global-max-size=512MiB`、`max-disk-usage=90`、NIO File Journal、auto create/delete false。
  Address full/paging/page limitは321 §5.3のQA-042/UIC-002承認値を正とする。
- CredentialはJAAS/propertiesへhashとして格納、LoadCredentialから起動時にservice private runtimeへrender。
  Plain passwordを`broker.xml`、unit、argv、Gitへ置かない。

### 7.1 再配送確定値（QA-041/UIC-001）

`max-delivery-attempts=4`、`redelivery-delay=1000`、`redelivery-delay-multiplier=5.0`、
`max-redelivery-delay=30000`とし、実効delayを第1=1秒、第2=5秒、第3=25秒に固定する。Rendered `broker.xml`の
schema validationとIT時系列で321 §5.4との一致を確認する。

### 7.2 容量確定値（QA-042/UIC-002）

UI 231の合計保存上限をmemory＋disk pagingで実現する。321 §5.3に従い、`global-max-size=512MiB`、
Address memory high-water合計448MiB、`PAGE`、Address別page limit、page-full `FAIL`、disk-full `BLOCK`とする。
Rendered `broker.xml`はAddress別6組のbyte/件数上限、合計4.75GiB、page size 8MiB、read page 16MiB/100件を検証する。

## 8. Resource・disk合計・実測gates

| 分類 | 設計budget | Gate |
|---|---:|---|
| PostgreSQL | 4GB | RSS/shared/work memory合計、temp/WAL、query plan |
| Artemis | 2GB | JVM/direct/RSS、Queue 41,000件相当 |
| API | 2GB | 8 DB connection、8 sync consumer max、codec/file mode |
| Web | 1.5GB | 20 wait/20 stream、session/outbox |
| OS/Caddy/cache | 3GB | 停止/起動・broker I/Oを含む |
| Safety/DEBUG | 3.5GB | STANDARDでDEBUG 2GBを起動しない |

SSD 256GBはUI 253の45/35/30/10/5/10/80/5/36GB配分を維持。Filesystem 80% warning、90% critical。
`MemoryMax`とJVM heapを同値にせず、direct/metaspace/thread/native用余裕を残す。

ITはSTANDARD modeで10 concurrent user、20 media stream、Scenario file mode、backup/cleanupの個別・組合せを実測。
Upper limitの変更は実測証跡、合計budget、config manifest、354試験期待値を一括更新する。

## 9. Configuration validation・drift

| Component | Deploy前 | 起動後 |
|---|---|---|
| Caddy | fmt/adapt/validate、bind/cert/key permission | TLS/header/upstream/55160/firewall |
| Systemd | `systemd-analyze verify`、unit diff、user/path | `systemctl show`のMemoryMax/restart/timeout/hardening |
| PostgreSQL | config/hba parse、`postgres -C`、role/grant diff | `SHOW`実効値、pg_isready、remote接続拒否 |
| Artemis | XML schema、address/security diff | Management APIのAddress/Queue/journal/security/effective settings |
| Java | Java 25/toolchain、config schema、secret permission | `/info`のversion、health、JVM flag/resource |

実効値をsecret除外のcanonical JSONにしSHA-256をrelease/operation manifestへ保存。Driftは次回朝処理でwarning、
security/port/root/schema/protocolの差異はreadiness false。自動で未承認configへ書き戻さない。

## 10. 公式仕様参照

- [Caddy `reverse_proxy`](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
- [Caddy `header`](https://caddyserver.com/docs/caddyfile/directives/header)
- [PostgreSQL 18 resource configuration](https://www.postgresql.org/docs/18/runtime-config-resource.html)
- [PostgreSQL 18 connections and authentication](https://www.postgresql.org/docs/18/runtime-config-connection.html)
- [Artemis Address Settings](https://artemis.apache.org/components/artemis/documentation/latest/address-settings.html)

Minor/patch導入時は必ず導入versionの公式資料とconfig validatorで再確認する。QA-042/UIC-002承認設定のArtemisは
`page-limit-*`とAddress別`disk-full-policy`を両方備える2.50.0以上を起動前gateとする。

## 11. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-036 | Web/API management portを8081/8091に分け、API main HTTPを無効化 | UI 211の非公開Actuator、APIのBrowser直接応答禁止を強制 | Port/firewall/readiness IT |
| SS-D-037 | PostgreSQL初期値をshared buffers 2GB、max connections 40、role別timeoutに固定 | 16GB hostでwork memoryの乗算増加とpool上限をbound | Query plan/負荷実測で調整証跡 |
| SS-D-038 | Java OOM時はprocess exit、heap dump自動生成なし、systemdは5回/10分でrestart抑止 | UI 252の値で、復旧と機密保護、restart loop防止を両立 | OOM/limit IT、runbook、metric |

## 12. 禁止事項

- Caddy以外のportをglobal/LAN bind、Artemis console/Actuator/PostgreSQLをfirewall例外公開。
- Secretのunit `Environment=`/argv・Caddyfile/broker.xml/application YAML/Gitへの平文格納。
- Systemdを迂回した`java -jar`・broker・batchの手動常用起動。Stop timeout時の自動SIGKILL。
- PostgreSQLの`trust`/MD5認証、remote hba、application superuser、Webへの業務schema grant。
- Artemis redeliveryをQA-041/UIC-001承認値の1秒、5秒、25秒以外でrelease確定すること。
- UIの用途別合計保存上限を`max-size-bytes`へ直接転記すること、全Address `BLOCK`へ戻すこと、QA-042承認値を無断変更すること。
- `schubert_batch`へdump対象tableのSELECTを与えること、`schubert_backup`へDML/DDL/SET ROLE/復号keyを与えること。

## 13. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | Caddy/systemd/JVM/PostgreSQL/Artemisの初期値、hardening、validationを作成。 |
| 2026-08-31 | 横断監査でPostgreSQL role名をUI 212の`schubert_*`に統一。 |
| 2026-08-31 | 横断監査でCSPをnonceなし・same-origin外部asset方式へ統一。 |
| 2026-08-31 | 横断監査でWeb DB poolをUI 212の上限2へ修正し、Artemis容量設定をQA-042/UIC-002保留として追加。 |
| 2026-08-31 | `pg_dump`用の`schubert_backup` role候補をtimeout/`pg_hba.conf`へ反映し、QA-043/UIC-003回答待ちとした。 |
| 2026-08-31 | 横断監査でJVMのheap/direct/metaspace合計がMemoryMaxへ達していた値を是正し、process別native headroomを確保。 |
| 2026-09-01 | QA-041/UIC-001承認を反映し、Artemis再配送設定と実効delayを1秒、5秒、25秒へ確定。 |
| 2026-09-01 | QA-042/UIC-002承認を反映し、Artemisのmemory high-water、disk paging、page/disk full設定をrelease値へ確定。 |
| 2026-09-01 | QA-043/UIC-003承認を反映し、`schubert_backup`のtimeout/hbaとbatchとの権限分離をrelease値へ確定。 |

## SSC309 same-PID exec世代の一時状態

世代専用の再照合はLinux非leader exec切替中のstat Zを同PID/startTicksの未終端確認として保持する。Z単体から生存/ready/終了を発行しない。self/PID1/初回Root捕捉のstate制限は不変更。boot/Unit/Invocation/cgroup/ticksは従来どおり二読一致、X/x/未知/不正/再利用は拒否。ordinaryのUID/GID/groups/caps/NNP・cmdline・所有socket・実HTTP200 UP/infoの前後照合を必須にし、true zombie/未readyは元期限内のpending、期限延長/再起動/UNKNOWN正常化なし。SS343/354・SSC164/BUG1470/YKT1233に横断追跡する。

## SSC-468 API／Web接続確認と取得で共有する固定role

ServiceDatabaseAdmissionは、非nullのService値に対しAPI→schubert_app、WEB→schubert_web_sessionの閉じた不変対応表を使用する。表に定義のない値で既roleへfallbackしない。ServiceDatabaseSourceは同じ初期化で検証済みAdmissionのpackage内roleを参照し、取得時のuser設定に用いる。既定applicationName、URL形式、DBおよびrole確認、サービス外入力の拒否、既SQLSTATE、設定や認可・資格記録・公開ABIの変更はない。提供元への接続や実認証の再試験とは分け、既承認のメモリ内二Port全31、当source/build、型ごとの単一exec、生のbranch/line/method/class、例外の同一性と資源順を確認する。別のServiceDatabaseSource.closeに残るlock/wipe例外後条件の測定は独立管理する。
