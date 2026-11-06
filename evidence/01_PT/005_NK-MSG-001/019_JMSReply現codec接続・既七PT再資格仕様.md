# JMS Reply・現codec接続の既七PT再資格仕様

Program NK-MSG-001、主WBS-P005-02。対象MainはJmsReplyDecoderの全10methodと直接返却値ValidatedReply（全source）。RD MQ004/005/008、UI231/232、SS321§8/9・322§5、原001/013/014を正とする。current Main4217/normal20990、原PG18644/b093のJMS14成功は別source・別依存の歴史証拠として保持する。

再資格の理由は、QA054でPayloadCodec/LayoutFieldCatalog/PayloadSemanticValidator/WebLogEventDataが変更されたこと。原protocol63（002029/PG19458）にはJMS decoderのclass-selectorがなく、原b093のJMS結果を現codec接続全体へ転用できない。実装・Test自身は同byteでも、この依存変更に対応する既whole JmsReplyDecoderTest七件だけをcurrent normal web/protocol JARで再資格する。codecを呼ばないGuard七は再演しない。新method/Test設計/製造完了を加算しない。

|再資格case|元Test ID|JmsReplyDecoderTest method|独立期待・根拠|
|---|---|---|---|
|RQ001|PT-JMS-005|acceptanceReplyUsesExactRegisteredAsyncProfile|SS322のQSBRSP01 S/A、data64/total320・固定field offsetとliteral bodyを保持。他profile/kind/route/propertyを拒否|
|RQ002|PT-JMS-005/008|validReplyProducesAnImmutableRedactedResult|LOGRSP01 S/S、data24/total280の手組literal全byte/correlation、0200既profile保持、provider/返却配列の変更がownerを壊さない、NULL constructor拒否|
|RQ003|PT-JMS-006|nullTypeBodyLengthAndCopyAnomaliesAreRejected|null/nonBytes/負長/上限超過/欠落body/短長不一致を固定拒否|
|RQ004|PT-JMS-006|destinationMustBeThePermanentApprovedAddressWithoutReplyTo|固定permanent address/FQQNだけ許可、foreign/temporary/null/blank/不正queue/replyTo/別addressを拒否|
|RQ005|PT-JMS-006|requiredHeadersPropertiesAndValuesDenyMissingBlankAndMalformedInputs|必須header/propertyの欠落/NULL/blank/未知・deliveryCount0/負expiryを拒否|
|RQ006|PT-JMS-005/006|transportAndWireValuesMustExactlyMatchTheReplyHeaderAndRoute|persistent/TTL/protocol/layout/message/correlationのwireとの完全一致|
|RQ007|PT-JMS-CANON-002|identityPropertiesMustRetainExactLowercaseCanonicalUuidText|UI232 byte offset24/60のliteral UUID二つとproperty、正規形だけ許可しuppercase/短縮/部分短縮/前後spaceを拒否（元11vector）|

RQ番号は同じ既存methodの今回の照合labelであり、新規PT件数ではない。期待wireは原Testの手書きASCII/固定byte offsetで、production encoderでexpectedを作らない。全7methodと全helper330行を確認した。fixtureはpublic JMS interfaceを実装するown Proxy/Mapとunconnected Artemis destination値だけ。未知callbackはUnsupportedOperationException、ConnectionFactory/JMSContext/session/consumer/send/receive/DB/HTTP/Root/native/キー/held四を呼ばない。default temporary destinationのSDK/JDK内value生成は実brokerの作成・業務session発行ではない。SDK全syscall0は主張しない。

Test sourceは原b093/hashと同一のまま固定してTestのみcompileする。API/storage/bootstrap/batch JAR・driver・broker serverをruntime classpathへ入れず、current web/protocolと旧pinと一致するJMS/Artemis未接続値SDK/JUnit・current JSpecify1.0.1だけを用いる。新fixture/元held wholeからのmethod抽出・元期待値変更なし。Main NullAway/SpotBugsは同byteのnormal20990/20992、Test静的は同source/同適用文脈の元判断との一致を確認し、必要な変更classpath静的チェックだけを行う。

一own JVM/一exec/sessionで全七を実行し、F/E/skipped/aborted/not-run0・元method集合一致・正常OS終了を要求する。二Sourceの全normal physicalだけを分母に残し、line/method/class未達0・decoderのbranch未達0、recordの自然branch0はN/Aと明記する。JaCoCo既定compiler filter不変更、手動exclusion/旧exec合成0。raw probe hitとsource counterを混同しない。全closureのMain classID/normal byte・held四の初期化/呼出無しを独立照合し、他依存Sourceのpartial counterは全体100%へ換算しない。

compile/unit/report/static/source/hash・OS/JDK/tool・command/exit・原XML/公開XML/exec/expected/actual・BUG/SSCの証跡は当programの新manifestと020結果へ一意に記録する。途中失敗は保持し、実装済み契約違反なら修正前にBUG/YKTへ起票する。Guard7/原protocol63/原JMS14の確認再演0。実broker/実NK CHR/native/全451/親leaf/IT-STは未受入、正式1964PT53scope/工数nullを維持する。
