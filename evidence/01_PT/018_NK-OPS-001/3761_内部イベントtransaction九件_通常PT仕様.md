# 内部イベントtransaction九件・通常PT仕様

Program NK-MSG-001/WBS-P005-03、RD MQ006..010/ASY002/MON003、UI213/231/251、SS312§8-9/321§6-8・§11/322§5・§11。対象はTransactedEventListener全SourceFile/全Code（default callback lambda含む）。existing InternalEventProcessor四PT18586/DeliveryMetadata二PT14244は元成功を再認証/新資格せず、入力依存として使用する。原932/109候補・23420 counterroute・005 program仕様結果を事前確認、共通delegateの現全Code資格未結合。未実装や元broker PT失敗を断定しない。

独立EventTransactionPortTest、PT-JMS-TXP-001..009。入力はSS322/323のmagic/header256/EI/QWK64・total320、WLG2080・total2336のzero-based literal wire、synthetic公開message/correlation/request/receiptのみ。Production encoderでexpectedを生成しない。効果はJDK Proxy JMSContext/BytesMessage/JMSProducer・固定Clock・queue valueだけ、未宣言操作はAssertionError。JMSProducer.sendも提供interface callbackで実送信無し、createProducerはメモリProxy、connection/provider/consumer/broker/DB/VM/Root/native/actor/鍵/held4全HOLD。元consumer/native/Root Tests compile-run/抽出0。

|ID|fixture/入力・操作|独立期待|
|---|---|---|
|001|ASYNC_WORK/WEB_LOGを直接constructor→public onMessage|E/Iの明示layout/長さ/data、mode→process→commit、body read一回|
|002|null destination/detectedBy/processor/Clock、非event destination全enum|それぞれNPE/IllegalArgumentException、処理0|
|003|context/message/observer null、非transaction mode|拒否、body/business/commit/rollback0（bodyReads独立counter）|
|004|BytesMessage body length読取が元JMSException、legacy/observer両overload|同identity、rollback一回、observedはattempted→rollback→confirmed、legacy noop lambdaも実行、suppressed0|
|005|Clock/processor/commitが元RuntimeException|同identity・各先行stageだけ呼出、rollback通知順、部分成功や再試行無し|
|006|両routeのmagic byte一つ不正|protocol拒否、body同一、提供DLQ callbackに同じmessage、SS321§11の10限定property・persistent2/TTL0・固定DLQ、commit後CommittedFatalInboundException|
|007|transport ID129 byteでDeliveryMetadata不正|processor0、isolation成功terminal、元IDはUNAVAILABLE、他固定metadata|
|008|isolation callback send RuntimeException|FailedJmsIsolationException、同primary/同protocol suppression、attempted→rollback→confirmed、commit0|
|009|通常processor failureとisolation failureでrollback自身RTE|UnconfirmedJmsRollbackException/FailedJmsIsolationException、primary/rollback同identity、rollback一回、confirmed0、UNKNOWNを成功へしない|

対象SourceFile全normalphysical/各Code methodを列挙、一exec/session/CRCと独立postを結合。全branchの実値100を要求し、自然ゼロのwrapperとは分離、delegate依存全SourceFile/DLQ sender/実再送の全分岐資格を推定しない。line/method/class/branch missがあれば未達を記録し除外で埋めない。FES/abort/skip/timeout/未実行を成功へ加算しない。新九caseは当delegateの独立contract測定でありProduction機能九件ではない。原成功/原baseline/stash7/原本/二untracked保護継承。

Main7aed unchanged、normal22084/六static22086再利用。JDK25.0.4/JaCoCo0.8.15/JUnit1.13.4/PMD7.28 recordfix/CS14.3、自己Test一fileのみproc:none/Xlintall-Werror、graph+SDK+command/static preflight後source commit固定。runner436 prepare/static/run <commit>（PYTHONPATH=tools/quality）、Unit120秒/Test10秒、c.ENV隔離。PG23466/68/70 prepare/static、23472preflight、23474sourcepub、23476Unit、23478independentpost、23480pubを予定、是正後の別source/slotは元証跡保持の上追記。日時/OS/JDK/command/source/input/期待recipe/actualXML/counter/hashはmanifestへ。fresh見積1/3/7pp cap9、通常区切り後も477継続、10%新規停止/5%保全。正式1964/53/newleaf0/工数null、全451/IT-ST未完。
