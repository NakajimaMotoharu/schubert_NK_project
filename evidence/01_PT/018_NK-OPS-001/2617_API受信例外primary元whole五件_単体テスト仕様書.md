# 2617 API受信例外primary 元whole五件・単体テスト仕様書

着手前2026-10-30 JST、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c/normal14216。群CURRENT_INBOUND_PRIMARY_ORIGINAL_FIVE_PT_V1、開始0.5/2/4pp cap10、WBS-F03/関連P00503追加予算0。別の既存原whole InboundTransactionsPrimaryContractTest（182行/全5method/Fixture/message/EqualFailure全body読了）を非改変で通常PTにする。初期化と全既存callback/helperまで確認し、1975の9ID/3class・Temp/APIStartup/WebStartup graph portを呼ばず、同graph9の新fixture/抽出/代替ではない。実Artemisを含むSyncRequestListenerTest wholeはHOLDのまま、mock部分抽出0。

Main InboundTransactions全94行、DlqSender全123行/FatalDlqMetadata全23行・FailedJmsIsolationException/UnconfirmedJmsRollbackException全bodyを確認。fixture JMSContext/Messageは元JDK Proxyだけ、rollback/commitはprivate intの更新、未宣言methodはAssertionError。isolate二ケースのcreateProducerは固定例外を投げるのでproducer/send・ActiveMQQueue生成より前に失敗する。getSessionMode/metadata getter/setterは固定値/private memoryだけ、broker/factory/connect/socket/DB/file/key/Root/native/control/実運用再送操作なし。観測対象の表現としてrollback/isolateを呼ぶが、実JMS資源を取得・回収・再試行するものではない。

RD MQ008/010/UI231251/SS312・321・352/BUG1485-YKT1245/PT-JMS-PRE001～005（元宣言P001～005）、PG-D873。Main canonical/cost P00503、元Testのcanonical UNKNOWNならnull維持。既1916/1216は先行責任/期待値資料として参照し、旧run結果を現source成功へ転用しない。

|元method/Test ID|fixture/入力・操作|独立期待値|
|---|---|---|
|jmsP001 / PRE001|同一primaryをproxy.rollbackが投げる|原primaryがcause、suppressed0、rollback1/commit0、self-suppressionなし。|
|jmsP002 / PRE002|別objectだがequals trueの二例外|causeはprimary、元secondaryが一個suppressed、rollback1/commit0。identityをequalsで同一扱いしない。|
|jmsP003 / PRE003|proxy.rollbackが元AssertionError|同一fatalが直接伝播、rollback1/commit0・primary suppressed0。|
|jmsP004 / PRE004|protocol primaryをcreateProducerが投げる|FailedIsolationのcause同一primary、rollback1/commit0、自己suppression0。|
|jmsP005 / PRE005|別isolation failureとprotocol|cause同一isolation、protocol一個suppressed、rollback1/commit0。|

各期待は先に作るfixture object/literal count/SSの単位契約で、Production methodからexpectedを生成しない。元wholeの正常/異常/直接Error/identity/再送不能後条件だけを検証、nullや全graph/実providerの全条件網羅を推測しない。全Sourceのcoverageにmissが残れば未達のまま保存、追加人工呼出・別exec合算・除外はしない。新Test ID0、Production/元Test不変更。

実command=python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14252_inbound_primary_whole_five_pt.py。新-onlyslotで元Test hash86c39396/normal6b53六Jar/既JDK25.0.4/JUnit共通Reporterを固定してjavac→JUnit/JaCoCo一session、件数5/FES/未実行0を確認。14254独立postは元XML・終了/全入力・SDK・exec/sessionCRCとInboundTransactions完全Source一physicalの四counterを測定し、未網羅はFAIL等へ捏造せず未達を表示する。helperのcoverageをこのSource unitへ混ぜない。結果2618にOS/JDK/版/日時/branch/source/command/exit/path/hash/未網羅/関連障害を保存。既正式/個別受入/全451/F03/QA051final/全actualHOLD/原本保全・二held工具metadata前除外を維持する。
