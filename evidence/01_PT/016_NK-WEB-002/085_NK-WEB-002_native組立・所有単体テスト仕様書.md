# 085 NK-WEB-002 native組立・所有単体テスト仕様書

PG454 C4/native graph初回仕様（未実行）：CONFIG001 client initial1/12/20各実飽和、次要求send0/CAPACITY・全reply後pending0/default12/21拒否。CONFIG002 media上限1/2/20で実stream保持、次BUSY/fileopen0・IOException後全permit回復、0/21/null拒否。CONFIG003 parsed100ms/default2sを全8wire実instanceへ投影し独立固定100msを内部保持値と照合（expected Production生成0）、assembly timeout null/99.999ms/2s+1ns拒否。CONFIG004 native ordinaryは同validated initial/max/timeout/media/management portを使用。STOP005同lifetime停止flag後はownerの100ms pollを待たず受付拒否。LIFE001..003実hook登録/二重登録拒否/健康await/割込/failure/foreign shutdown待機→confirmed owner通知後のみ終了・flag保存。OUTER001はinstrumented別JVMでIO/runtime/fatalの実release UNKNOWN→割込後もattempt1/downstream0/生存を確認し、fixtureをSIGTERM143で停止する。これはordinary service native admission又は正常cleanupの認定でない。ServiceProcessResources既存実PG/五credential/PTをnative保持modeでも正常解放し、legacy compound/partial/null/並行回帰も実行する。全native Root/ordinary/PID同一owner・Caddy/DONE/CHR/同sourcecoverageの後条件は実VMまで未受入。

PG454 C3試験追加（未実行）：NATIVE-OWNER001 vendorのactual Tomcat start後に固定LinkageError、callback捕捉がstart前でport/mapping未公開、legacy自動destroy0、第一stop UNKNOWNでdestroy0・retry actual終了後socket再bind/二重destroy0。OWNER002 actual owned serverと同返却handle/実HTTP200/null owner前resource0、WebApplication同pairのowned実接続。OWNER003 legacy startup fatal×cleanup正常/別fatal/同fatalを独立identity/suppressed件数/cleanup一回で照合。NATIVE-BUDGET001002はLog/revoke実workerを非協力latchで保持しnull/負/>30拒否はworker健康不変更、zero/1ms joinUNKNOWN・実生存、解除後30sactual join→zero retry正常、旧割込/selfjoin/SQL再送も回帰する。期待時刻や終了boolをProductionから生成0、全native未受入。

2026-10-04、PG-D369、NK-WEB-002/NK-OPS-001。RD SYS002004/AUT002004/MQ003008/MON003/FIL001009、UI212223224226232237243253、SS312313314321342343352/QA047049050。既存承認設計の内部接続、業務仕様変更0、未受入。Program/class/methodの追跡は431/441とclass comment、現況456/460。PG453 sourceca0afeの3193成功を新sourceへ流用しない。

## 同一pair・内部所有能力

WebApplication.startWithCoreSessionDependencies/startWithCoreValidatedDependenciesと旧委譲：同じcoreを一度生成し、同じcoreからSpring adapterを生成することをsourceと独立動作で照合する。第二repository/曖昧なoverload/feature側pool-key所有を作らない。

| Test ID | Fixture/入力/操作 | 独立期待 |
|---|---|---|
| NATIVE-CORE001 | isolated host PG/Flyway、actual embedded Artemis、security実HTTP GET/login/実cookie。同callbackのSpring sessionへ固定reader/USER/a64をauthenticateし、passed core.mutateに手書きUUID0:123/QDL/未完了一件をfixture投入。public lifecycle.requireで読む | Login200/title/CSRF/current DB row、callback一回、同Spring fresh readで独立固定UUID/用途/未完了一件。UUID expectedをProduction generatorから生成0。source constructor pairも照合、DB実値だけでJava object identityを断定しない |
| NATIVE-CORE002 | null BiFunction/null path/負port、borrowすると失敗するDB/JMS fixture | null/local validation段階で拒否、DB/JMS0/HTTP bind0。Nullability静的/explicit boundary、NPE catch正常化0 |
| NATIVE-CORE003 | old Function/start/Map delegate、null returned Map/型不一致、DB/Artemis不可 | 既存SCR117..126が同new private経路で独立HTTP/SQL/resource後条件を確認、public既存互換・保護を弱めない |

## Full graphの限定独立試験（PG454 v8実行済、native未受入）

PG454 v8追補：GRAPH001の経路数は/login等を含む32の手書き固定集合であり、下記開始時記載の「31」は記述誤り。実fixtureと期待集合を変更せず、086/manifestの実32を正とする。GRAPH002は12必須constructor null slotを独立入力で確認する。READY003はactual vendor start後の非協力callbackとcaller interrupt/cleanup UNKNOWNを実際に作り、停止済み未開始executorを未終了と仮定しない。reply同一fatal primary/cleanupのself-suppression防止も追加し、9対象の全counter0を確認。後続native/worker budget/outer所有は未実行。

PG454 C2独立fixtureを具体化（新source、未実行）：NATIVE-READY001は実管理HTTP固定JSON5/健康503→一回real Ready capability→200→健康喪失503、GET以外405・不明path404・metric0/1・秘密値0。READY002はrelease前owner死亡/release IOException/release後死亡、再attemptでA二重発行0。READY003はvendor既開始server/NULL factory/unknown version/固定8081 bind collision、失敗時socket再bindとfatal identity。READY004はrelease中実closeでUP0。READY005は実health handlerをinterrupt無視latchで保持しcloseWithin0を二回UNKNOWN、interrupt flag維持/UP0、latch解除後actual executor終了→retry close正常・client socket切断を確認。READY006はnativeの先行bind→owner捕捉→start一回、停止前後second start拒否、null/負/31s budget拒否。

NATIVE-STOP001/002は単一Admissionの初期拒否/admit一回/lease数/空drain/UNKNOWN/再admit拒否、zero/negative/null/>30s/割込/並行lease releaseを独立確認。STOP003は実Tomcat・Servlet AsyncContext・実HTTPでbefore-A503、admit後Login200、既存ASYNC保持中に新Login503/zero drain UNKNOWN、ASYNC実完了後だけdrain成功、実mappedPathsと停止後拒否を確認。STOP004はterminal AccessLogのnull metadata/duplicate completion/未知属性・next valve・禁止overrideを確認しServlet-finallyでlease解放0。

BUG652/READY006追補：bind-only ownerのpromoteはactual start完了前にIOException、release callback0/UP0。その後一度actual startでき、invalid early callからAの仮消費を生成0。BUG653/YKT462追補：actual JDK25.0.4 HttpServer.stop0前のinterrupt=trueをfinallyで保存し、Web cleanup awaitはUNKNOWN＋flag=true、startup primaryに固定close IOExceptionがsuppressed、二次finally assertionでprimaryを覆わない。独立Work probeはJDK stop0そのもののflag clearを確認するだけでProduction期待値を生成しない。API同stop0のready005もcaller flag保持/管理DOWNを実HTTPで横断し、provider closeとactual group drainは別契約を維持する。

NATIVE-GRAPH001はisolated PG・actual embedded Artemis・real Linux NOFOLLOWの私有Asset/Transfer capability、full固定configから実MVC controllerを全生成しHTTP/Loginと実31業務path集合をUI/SS由来の手書き一覧と照合する。全17依存、same-pair token/invalidation/Logout、readonly file/media、REQUESTを一つのgraphへ投入。static annotation inventoryだけを成功根拠にしない。GRAPH002はnull必須依存/返却mapの型/別旧controller重複拒否。実ordinary VM/nativeの代替ではない。後続worker/partial所有・30s全体budget/outer frame保持は同群に加えるまで未受入。

全業務port/samepair/borrowed root/current三codec→reply先行→Log/revoke→actual MVC全生成・fixed mappings→management DOWN/info5→Ready release一回→受付UP。Sourceの静的集合だけをactual生成の証拠にしない。QUERY/CSRF/owner/version/retained tokenは既存実API+独立golden/SQL/HTTPを再利用するが実結果は各sourceで再実行する。

後続Test ID NATIVE-GRAPH001..008=actual full mapping/各feature依存・null/duplicate/欠落拒否、real protected HTTP・MQreply/REQUEST/media、三purpose/Root read-only借用・resource0、startup部分失敗。NATIVE-READY001..006=独立info JSON5/固定health-readiness503DOWN→200UP→503DOWN/GET以外405/unknown404/metric0→1/Ready一回/前後owner死亡/partial stop、独立factory故障とconfirmed close。NATIVE-STOP001..008=新HTTP拒否/同期・ASYNC・media actual drain、両workeractual join、単一30秒budget/phase retry、replies-before-root-key-broker-pool終端、UNKNOWN時callback/frame/borrowed資源保持/fatal identity・誤正常marker0。各fixture/input/独立期待は実装前に追記し、未実装を合格としない。

native physicalは現在VM/boot/Unit/PID/Invocation/DB/原本Backup/fullBOMを再認証し、正規candidate27→同親Root/ordinary API/Web identity/generation/socket/info→A/UP→Caddy→OriginalProof正規complete/intent退役→実NK CHR/native same-source coverageへ進む。部分Core/管理HTTP成功を同親全体の受入へ加算しない。IT/ST完了は別工程。

## 実行・品質

Linux/JDK25.0.4/Maven3.9.12/PostgreSQL18.6/Artemis2.56.0（PG453 frozen runtime dependencyと照合）。関連suite・全6module canaryをまとめて限定実行、untracked本文含む私有source tar/hash/dirty/source/actual/XML/4coverage/静的と実到達targetを捕捉する。既存Full owned群のacceptanceはfull graphを固定したfresh全6へ集約（管理文書/helperだけで全回帰を反復0）。line/method/class/branch100・独立expect・negative null・例外/並行/owned stop・秘密/traceを所定scopeで確認、not-run/skip/flaky/別source成功の合算0。

実command/branch/source/開始終了/OS/tool/actual/coverage/BUG/YKT/SSC/安全artifact hashは086/manifestへ記録。raw credential/password/session/cookie/token/context/key/DBdump/providerログは私有WorkだけでGitに入れない。
