# 2513 JMS長寿命owner六箇所 現source点検仕様

2026-10-29、PG-D822予定、START2892/費用参照訂正2893、source17ab52b25/Main/Test不変更。開始0.5/2/4cap10・fresh29残71/reset1793774153。主F03、canonical API factoryP00503/Reply・Web factoryP00502参照のみ・追加予算0。原2892のP01805は前群Readinessからの手転記誤り、BUG2078/YKT1826へ訂正前起票し原event保持・2893追記。実費/予算/sourceRowsは変更せず、主担当を変更担当から推定しない。元save866ccf74e7cc6c35beeacf1c4b09bf178b189d7c/push43216真正0/remote一致。

ApiBrokerContexts全Main（constructors/open/close）、WebBrokerContexts全Main（factory setup/constructors/open/close）、ArtemisReplyConsumers全Main（bind/static及びinstance start/delivery/close）と1279/1281/1468/1473の既契約を読取確認する。旧source870の成功を現sourceへ輸入せず、今回の取得alias/移管だけを個別rawIDへ束縛する。既normal13596/静的13599当source不変更参照、確認再演なし。

|PMD ID|資源・期待所有契約|
|---|---|
|00156|sync factory。容量3/ownerClosed/scratch/observerを最初のacquire前に用意し、返却直後ownersへ捕捉。後続assemblyが失敗すれば逆順保護、UNKNOWN observerの非帰還を成功解放とはしない。|
|00157|webLog factory。既保護assembly中に取得・即ownersへ捕捉、全profile完成後retained fieldへ公開。ctorの局所TWRでlive ownerを閉じない。|
|00158|async factory。同ownersへ捕捉後は単純field代入、正常owner closeは逆順と各成功phaseのみ記録。未知をclosedへしない。|
|07337|openedはfinal contextの借用aliasで取得資源ではない。bind後のowner捕捉、同lock/startAttempted、static start失敗時closeとinstance partial owner保持を区別する。|
|07338|consumerはJMSContextの従属owner、登録後のlive配送に必要。即TWRでlistenerを閉じず、runtime.context closeが全consumerを所有。実providerのclose帰還は当静的理由では証明しない。|
|07357|configuredは設定済factoryを最後にfinal factory/owner二fieldへ同identity移管。全port/lock準備後取得・setup failureは一度close/UNKNOWN引渡し、正常close帰還後だけclosed。|

SS321/342/343 SSC311/315/316/333/334、NK-MSG001002/NK-OPS001・MQ001～008/SYS004、UI231/243/253、既FACT334002003008/JMS014024/JMSWEB001..003を参照。credentialは借用境界の寿命、immutable Stringの物理消去を保証しない。ここでfactory/credential/key/targetを構築せず、実JMS/native/Graph9/Root/VM/Unit/DB/permit/私有raw/held工具を操作しない。

13772は当三source全hash/PMD半開span/owner/契約、13774は別XML・独立offset・誤owner/source/false-0/provider/graph/runtimeの負metadata、13776/78は六current参照だけ追加する。raw/原WBS/全995旧runtime/正式1964-53/17-190/工数null/QA051final/全HOLD保持、実行PT/coverage/新受入0。以前の意味的理由の参照はあるためfirst-ever理由数は不明nullとし、新参照六だけを数える。BUG2078訂正と全三scope照合・予防反例が揃うまでYKTを完了にしない。
