# NK-MSG-001 返信envelope factory単体仕様

対象JmsMessageFactory.INSTANCE/createReply、関連RD MQ003/008・UI231/232§3/5/233 IF001/SS311/321§8 SSC151。Program005、Test PT-JMS-ENV001～004、新JmsReplyEnvelopeContractTest四method。662は開始前0.5/1.5/3pp/cap10、原Goldenvector/期待/副作用/着手条件を保存。Main6b53を不変更、原OutboundJmsAdapterTestのbroker fixtureを呼ばず、新unitを実broker互換/transaction/TTL/DLQや初回Vの代替へ使わない。

ENV001：独立UI232 byte offsetからASCII headerを構築。Login error LGNRSP01/S/S/432+256=688、QSB error QSBRSP01/S/A/64+256=320、code0100。認証slotはLogin全space/QSBは公開synthetic零64hexで、認証/実session/key操作なし。実bodyの内容はerror profileのspaceとし、本unitはpayload業務検証を主張しない。responseUUID2/correlationUUID1、header version001、JST20260903120000000/reservedspaceをliteralに設定、production encoderでfixture/expectedを作らない。期待=JMSContext#createBytesMessage→writeBytes→correlation→NKMessageID→NKLayoutID→NKProtocolVersionの一回ずつ、body byte不変更/同値・戻りmessage identity、propertiesは独立literal Map。send/producer/commitや未列挙APIはproxyが即失敗する。

ENV002：null context/body、255byteの短header、LGNREQ01 request、宣言688と実689、実1,000,001byteを拒否し、create回数0。messageKind/max/actuallengthの三OR全条件を個別に確認。ENV003：createはRTE/Error、残五stageはchecked JMSException/RTE/Errorを各注入、計17faultvector。期待は同一Throwable/原順序のprefixだけ・再送/後続call0。fixture/validwire/exceptionはassert前に構築して誤検知を防ぐ。ENV004：providerがnull messageを返す契約違反は一create後NPEで止まり、正常扱い/後続message操作をしない。

実行は固定JDK25 javac→既存JUnitConsoleで新wholeclassのみ・autoextensions/parallel false・180秒有限、一回JaCoCo appendfalse session。全physical factory enumのline/method/class/branchを原exec/CRCと独立照合、手動除外/旧exec合算なし。既存PMD/Checkstyleを実行し、未分類指摘をPASSにしない。Source/Main/Test/依存/command/終了/環境/coverage/hashと原失敗は006結果及びpublic manifestへ保存する。並行/再送は本factoryがtransaction ownerでないため非該当、No retryは17faultvectorで確認。実broker/DB/VM/Root/FD/credential/post/native/全451/正式受入/親WBSは未完のまま保つ。
