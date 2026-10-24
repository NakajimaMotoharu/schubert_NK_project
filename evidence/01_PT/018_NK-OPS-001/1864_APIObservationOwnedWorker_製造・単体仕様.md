# API観測owned worker・製造/単体仕様

2026-10-25/PG-D635/NK-OPS-001/WBS-P018-09、RD171/UI252/SS311332342351、1862-63に続く同API経路。開始HEAD022214cdcc19e88228f46ce6d430c57fb6ef0aed/origin一致clean、製品f82e3e1ee、fresh55残45/reset1793382075、低4/基準7/高10pp・cap10を固定。直前54→55の共有境界1は前群/本群へ配賦せず、元/v4/v5・正式/工数/品質/HOLDを維持する。

OwnedApiObservationWorkerはcallerが保持する未起動owner。既pump/failure port/nano port/同同期一回starterを取得前に準備し、constructorは未起動Java Threadだけ（Pool/SQL/VM/サービス/配置/鍵0）、一回startを許す。start呼出し中flag/latchを保持し、stopと競合してThreadがまだNEWでもawaitStoppedを正常完了しない。偽starterが未起動を返す場合はstart失敗、再start不可。普通試験のstarter/同期doubleはpackage-privateであり、実callerはJDK同期Thread.startを使う。

workerはpumpを呼び、非fatal SQLExceptionだけ次tickへ送り、Runtime/Error/未知割込は元failureを通知して非正常終端する。SQLException graph内fatalは既helperで優先、callback secondaryも同primary/fatal契約を維持し、NPEを一時正常へ変更0。1秒waitはpumpの15秒観測を呼ぶ内部tickであって業務retry/QA050/停止deadlineではない。handlerは固定tokenだけでprovider text/stack/secretを出さない。

requestStopはpump停止/欠測とprivate synchronizer一回通知のみ。awaitStoppedはcallerの既残予算supplierと単調時刻を使い、最初に捕捉した残予算を経過差分で減算し、途中の大きい値で延長しない。start呼出し中/Thread aliveを共に待ち、元deadline内joinとpump quiescenceを全部確認する。割込は元残予算で継続し最後に復元、自己join・0/負/逆行時計・停止失敗/unknownは固定IOException等で非正常・永久unconfirmed、後でThreadが消えても自動正常化/再startしない。callerは既UNKNOWN保持policyで同owner/Pool frameを維持する。Unit/親残予算生成・実Pool/実Rootの認定は本群外。

OBSOWN001～044を新規44件予定。constructor/null/resource-free/default start、二重/停止前/同期starter失敗・曖昧start、SQL復帰/同fatal/Runtime/checked割込と通知compound、待機・SQL中stop/UNKNOWN、残予算0負増大/clock逆行・RTE/Error/割込正常と期限切れ、start中stop/自己join・再停止とunknown非正常維持、factory null/clock異常/旧owner誤使用を独立typed fake JDBC/clock/starter/private Semaphore doubleで検証。許可された普通JVM内の私有Threadのみ、App Main/VM/Root/cohort/native/実DB/サービス停止は実行しない。sleep同期0、latch/futureはbounded/finally解除し元Threadを回収、fake未知ownerの状態を実cleanへ読替0。

source固定→9132 normal六→9134新44→実rawに必要なら9135個別context→9136全worker一Main四counter/静的/NPE→9138全1841見込/旧1840同byte/244owner/五arch→1865結果・計測・scan・保存push。実caller start/stop/native/全source/451の未実行を合格へ加算しない。通常区切り停止なし、群cap/共有枠保全を維持。

## 個別Test ID・独立oracle

共通fixtureは同名TestのFixture/Harness/Signal。正常入力は手書きrow3/5/7・age2/4/6、取得前port0、独立remaining portは既deadlineまでの差又は表記literal。操作はconstruct/start/requestStop/awaitStoppedで、JUnit元XMLのobsOwnNNNへOBSOWN-NNNを一意対応させる。期待値をProduction methodで生成しない。clock/Thread lifecycle実測は普通JVM内の当fixture限定で、IT/ST性能値ではない。

| ID | 入力・事前条件/操作 | 期待値・算出根拠 |
|---|---|---|
| OBSOWN001 | pump/failure/nano/starter/signal各nullでconstruct | NPE境界拒否、starter/DB factory0 |
| OBSOWN002 | 正規portsでconstruct、awaitにnull | 全port未読・未起動、await null拒否 |
| OBSOWN003 | 公開constructor→SQL fixture保持中stop→release/await | 固定thread名/非daemon、取得/rollback/close各1、真Thread終端・欠測 |
| OBSOWN004 | start後もう一度start | IllegalState、実starter1 |
| OBSOWN005 | start前stop→start/await | start拒否、budget未読/Thread0 |
| OBSOWN006 | 同期starterのRTE | 同instance、再start不可、未起動資源の後条件 |
| OBSOWN007 | 同期starterのError | 同Error、factory0、未起動を安全回収 |
| OBSOWN008 | starterがNEWのままreturn | start失敗、DB0、成功起動へ読替なし |
| OBSOWN009 | 実Thread.start直後にstarterがRTE | 元RTE保持、進行SQLをstop/drain・一回close |
| OBSOWN010 | signal awaitが未知InterruptedException | 元checked通知、worker割込flag復元、終端 |
| OBSOWN011 | 一回目SQL例外、fixture nanoを15秒へ進め再tick | 次fresh観測2回目、fatal通知0、各conn一回cleanup |
| OBSOWN012 | SQL graph causeにError | 同Error通知/uncaught、SQLを正常一時扱いしない |
| OBSOWN013 | query RTE | 元RTE通知/uncaught、閉鎖確認後終端 |
| OBSOWN014 | query Error | 元Error通知/uncaught、閉鎖確認後終端 |
| OBSOWN015 | query RTE＋通知RTE | 元primary維持、secondary一件を同graphへ保持 |
| OBSOWN016 | query RTE＋通知Error | 同secondary Error優先、元graph保持 |
| OBSOWN017 | 未知割込＋通知RTE | 元割込にsecondary保持、RTE非正常終端 |
| OBSOWN018 | 未知割込＋通知Error | 同Error非正常終端、secondary graph保持 |
| OBSOWN019 | stop要求後のsignal割込 | 未知障害通知0、元stop後条件・割込処理 |
| OBSOWN020 | idle workerへstop/await | 同Thread終端＋pump quiescence双方 |
| OBSOWN021 | SQL fixture保持中stop→release | 保持中quiescent=false、cleanup後だけ正常await |
| OBSOWN022 | conn closeが不確定、有限diagnostic return | worker終了だけでは不足、await IOException・pump非quiescent |
| OBSOWN023 | SQL進行中、初回残予算0 | 待機成功0、UNKNOWN/同worker保持 |
| OBSOWN024 | 初回-1/Long.MIN_VALUE、以後Long.MAX_VALUE | 初回一読・clock未読でIOException、負値wrapによる延長0 |
| OBSOWN025 | 初回2ms、経過1ms、以後予算50秒 | 残1ms一回joinがtimeout→即UNKNOWN。clock/budget各2読、追加loopで正常化0（BUG1734根拠訂正） |
| OBSOWN026 | stop clock 1→0逆行 | 固定IOException・UNKNOWN、延長0 |
| OBSOWN027 | remaining port RTE | 同instance・停止要求/UNKNOWN維持 |
| OBSOWN028 | remaining port Error | 同Error・停止要求/UNKNOWN維持 |
| OBSOWN029 | stop nano port RTE | 同instance・UNKNOWN維持 |
| OBSOWN030 | stop nano port Error | 同Error・UNKNOWN維持 |
| OBSOWN031 | 私有待機caller割込、第三budget読後にSQL解放 | 元予算で完了しcaller割込flag復元 |
| OBSOWN032 | 私有待機caller割込＋元予算満了 | IOExceptionと割込flag双方維持 |
| OBSOWN033 | starter呼出し保持中（Thread NEW）、短予算 | startingを見てtimeout UNKNOWN、Thread未生存だけで成功0 |
| OBSOWN034 | 同starter保持中、旧残予算内に解放 | start呼出し帰還とThread終端双方まで待つ、stop後DB0 |
| OBSOWN035 | worker自身からawaitStopped | 自己join拒否・UNKNOWN永久維持、fixture私有handleで回収 |
| OBSOWN036 | 重複stop/未起動await | signal通知一回だけ、資源再操作0 |
| OBSOWN037 | 真Thread終端後の再await | budget再取得0、同owner閉鎖確認 |
| OBSOWN038 | timeout後にfixtureでThreadを終端し再await | UNKNOWNはIOExceptionのまま、再予算/自動正常化0 |
| OBSOWN039 | resource-free factoryがnull返却 | NPEを通知/非正常終端、DB0 |
| OBSOWN040 | pump nano RTE | 同primary通知/uncaught、factory0 |
| OBSOWN041 | pump nano Error | 同fatal通知/uncaught、factory0 |
| OBSOWN042 | signal RTE/Error及びstopなし通知 | 同failure又はIllegalStateで非正常、誤通知を通常tickへ読替0（BUG1734追加vector） |
| OBSOWN043 | stop signal release RTE/Error | 同failure・永久UNKNOWN、後続await再試行0 |
| OBSOWN044 | factoryが使用済一回ownerを返却 | IllegalState非正常通知、DB再取得/再処理0 |
