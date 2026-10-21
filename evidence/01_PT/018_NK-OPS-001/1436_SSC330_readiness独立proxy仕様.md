# SSC330 ordinary API/Web readiness proxy specification

BUG1593/YKT1346/SSC330、NK-MSG-001/002・NK-WEB-002、SYS001..004/MQ001..008、UI211/212/231/252、SS312/342/354。群1633の開始 .3/1/3共有ppを固定、P018-05主担当/P018-06 component、SQL既siteは1625/1345との重複費0。PGを省略しない。

PT_DEFAULT。予定Main8d77のまま新Test-only sourceを固定し、各moduleの自己所有DataSource/Connection/JMSContext/JMSConsumer/Queue interface proxyだけを実行する。外部network/DB/VM/Root/実credential/配備/permit/cohortなし。固定source archive/format→六testCompile→選択PT/static、既存原成功の再演ではない。5秒timeout。

API `ApiReadinessFailureGraph330Test` / Web `WebReadinessFailureGraph330Test` は同じ独立契約・各3method。期待は以下literal/別counter/元Error objectから作り、Production結果から生成しない。

|TestID（各API/Web）|fixture/独立期待|
|---|---|
|PT-API-READY-GRAPH330001 / PT-WEB-READY-GRAPH330001|DB isValid primary SQLのcauseにだけError、又はSQL primary＋捨てたConnection.close RuntimeのcauseにだけError。元Error、Connection取得/close各1、broker open/context close/consumer close各0|
|002|JMS createConsumerのRuntime.cause→JMSException.linked→SQL.next.cause Error、又は非fatal Runtime primary＋context.close Runtime.cause Error、又はconsumer.close Runtime.cause Error。元Error、DB取得/close各1、broker open/context close各1、consumer closeは最後modeだけ1、それ以外0|
|003|直接primary Error＋close別Errorはprimary優先、非fatal primary＋直接close Errorはclose優先。Error無しのcause/linked/SQLnextの混合循環＋非fatal closeは有限帰還し固定startup診断・cause null/suppressed0。全caseで取得済close各1、後続成功0|

API普通固定診断=`API Artemis receive queues unavailable`、Web=`Web Artemis reply Queue is unavailable`。JMS mode/Queue/consumerはinert fixture、送受信/接続しない。DBはisValid(2)だけ、SQL/commit/rollbackを呼べばfixture未知callで失敗する。DB失敗時にJMSを開始しない。

未修正Mainでは001/002のfatal assertion失敗を予測し003は既順位/固定非fatalをPASS期待。API赤は3＋baseline12=15/8（API停止時実9/5/F2、後段6not-run）、別Web赤も15/8（Web停止時13/6/F2、後段2not-run）。同source/全Testbytesで両原XMLを保存し、compile/timeout/errorを目的赤へ変換しない。PG後のgraph/secondary pure tests追加は別仕様とし、新機能の未実装compileを反例へ遡及しない。

当限定成功を実Root/Unit/DB不変/実ordinary業務ready/現在所有/native/CHR/全四100/451/正式へ読み替えない。原source/run/exit/XML/coverage/static/command/versionと公開hashを回収後に記録、未知/未実行はnull、全HOLD/正式1964-53/17-190/工数null/QA051final/PTALT代替0/原-v4不変。

設計はsource7fa7be822/PR194→main6dffaa0e0eac667d997700db93742bbc2c03e902へ三SS/914 sectionだけ通常mergeしremote確認済み。添付API100identity上限一回失敗・迂回0。formatter0、管理三0。TestSHA API301e5bbbdcdcdb611fdfde01f2061bf8b14de2a2620514d063fcf5ee03d64d30/Web1bff3207f54cbc10c711faa2feed81825e495b62da2a87f1612247d9fc2694ca、Main変更0/赤は次実行。
