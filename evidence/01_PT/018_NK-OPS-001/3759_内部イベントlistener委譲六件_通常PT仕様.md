# 内部イベントlistener委譲六件・通常PT仕様

Program NK-MSG-001/NK-MSG-002、主WBS-P012-01、関連WBS-P006-05。RD MQ006..010/ASY002/MON003、UI213/231/235§12/236§14、SS312§8-9/321§6-8/322/323 QWKREQ01・WLGEVT01。原932の両wrapperはUNBOUNDであり未実装を意味しない。既107候補・PG23420 counter名簿とプログラム既証拠を確認し、現両SourceFile全Codeの資格は未結合。旧InternalEventListenerTestは実embedded brokerを含み実行/compileしない。元PTの期待値を省略して置換せず、既承認の提供interfaceへの委譲境界を追加測定する。

対象=QuestionWorkListener/WebLogListener constructor/public onMessage/package observer overloadの両全SourceFile。共通TransactedEventListener/Guard/Codec/InboundTransactionsは依存であり今回の全分岐受入対象ではない。Test EventListenerForwardingPortTest、各method末尾001..006がTest ID PT-JMS-PORT-001..006。一run六method、一JVM、一exec、一session、manual coverage除外0。branch分母0なら自然ゼロ/N-A/率null、branch100と捏造しない。line/method/class及び全Codeの実値を記録する。

|ID|入力・操作|独立期待|
|---|---|---|
|001|Question public、delivery count3、固定transport ID/Clock|SS literal QWKREQ01/E/I/320/64と固定ID・JST timestamp、受信時刻、delivery-aware override一回、mode→process→commit|
|002|WebLog public、SAM processor|SS literal WLGEVT01/E/I/2336/2080/REQUEST/INFO/GET /login/200/0、mode→process→commit|
|003|両observer overloadへ同じ提供message二回|各呼出一commit、rollback observer0、提供interface自体にInbox dedupはない（業務再送無重複は未試験）、caller context close/start/producer作成等は全拒否|
|004|両constructor processor/Clock null、public context/message null、observer null|NPE契約拒否、transaction操作0、正常扱いcatch禁止|
|005|両AUTO_ACKNOWLEDGE context|IllegalStateException、mode読取一回、業務/commit/rollback0。本文未読はsource順序根拠、独立read counter未測定|
|006|両processorが同一synthetic RuntimeExceptionをthrow|例外同identity、mode→process→attempted→rollback→confirmed、commit/close0、suppressed0|

wire期待はProduction encoder/registryを呼ばずSSの独立byte offset literalで手構築、Header256のmagic/version/layout/EI/二UUID/sentAt/context space/長さ/予約space、QWK64/LOG2080固定data。原本・実session/token/credentialを含まない合成message/request/receipt IDのみ。実データsemantic validator業務処理は呼ばない。FixedPayload defensive copyも変更後再取得で検証。postでは入力構築literalとassert recipe/否定metadata、原XML、normal CRC、SourceFile全physical/all Code、明示全method、現在source/依存・static hashを照合する。

安全着手: JMSContext/BytesMessageはJDK Proxyの提供interfaceで未宣言callbackはAssertionError、ActiveMQQueueは既pinned SDK value constructorのみ。JMS connection/provider/consumer/server/producer送信は無し。実network/DB/VM/Root/cohort/nativeFFM、業務QuestionWorker/WebLogIngest、intent/permit/鍵/四held初期化はHOLD。例外rollbackのみInboundTransactionsのpurecallbackへ到達、static DlqSenderはpredicate/value初期化だけ、send/isolateFatalは未実行。JDK Clock/UUID/charset/ZoneIdのSDK自身動作をsyscall-zeroと主張しない。元native/Root/helper Testや拒否操作の抽出・代替ハーネスではない。全graph/SDK/command/static preflight成立前にUnit起動しない。

JDK25.0.4、JUnit1.13.4、JaCoCo0.8.15、PMD7.28-recordfix/Checkstyle14.3。normal22084 Main7aedと六静的22086をhash結合して再利用。自Test一sourceのみjavac -proc:none --release25 -Xlint:all -Werror、静的check後source commit/push固定、runner430 prepare/static/run <source>（PYTHONPATH tools/quality）、限定timeout120秒/Test10秒、owned command c.ENV。不正終了/FESabort/skipped/not-runは合格不可。PG23426format/23428compile/23430static/23432preflight→23434sourcepub→23436Unit→23438独立post→23440pub予定。実時間/command/OS/JDK/source/hash/結果/counterはmanifestへ。

着手見積1/3/7pp cap9、通常477継続、fresh残10%以下停止/5%まで保全。開始草稿oracle refs空はwriter前拒否/イベント無し/製品0、SS実正本二参照へ是正後4322一回。formal1964/53、新leaf0、工数null、whole暫定93・候補107は独立名寄せまで加算せずpending扱い。原成功/七stash/Currentbaseline/原本保全、IT/ST未完。
