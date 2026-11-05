# QA054 メニューmarker・Trace・Controller単体仕様

NK-WEB-001 / WebHttpLogKind/WebRequestTrace/MenuController。RD FUN002/FUN008/MON003/TST004、UI223/235/252/264、SS312313323324351355、QA054/UIC011/SSC336/main f6df0102f。

|Test ID|class.method|独立期待値と観点|
|---|---|---|
|PT-WEB-MENU001|MenuAuditContractTest.menu001EveryGateAndBoundaryUsesIndependentTruthTable|mark/GET/200/root/actorの全条件表、HEAD/POST/case/status99..600/他route/匿名はfalse。REQUEST種別は常false|
|PT-WEB-MENU002|MenuAuditContractTest.menu002ClosedKindsHaveLiteralMetadataAndNullContracts|閉2kindのliteral category/action/message、method/route null拒否|
|PT-WEB-MENU003|MenuAuditContractTest.menu003SuccessfulUserAndAdminModelsMarkOnlyTheirOwnTrace|USER7/ADMIN9card・既menu view/brandを維持、成功model後だけmarker、terminal claim一回|
|PT-WEB-MENU004|MenuAuditContractTest.menu004FailedOrMissingScopeDoesNotForgeAMenuSuccess|principal/model null、foreignprincipal、model失敗でmarker0、scopeなしは既menu結果不変。SessionStoreException constructorだけでfailuregraph未実行|
|PT-WEB-MENU005|MenuAuditContractTest.menu005NestedMarkersDoNotInheritAndEachNoMqEventSelfCorrelates|nested currentだけmark/別thread継承0、noMQは各event自身、businessMQある場合最初ID維持、null境界|
|既存REQ004/006/007/008 全10method|WebRequestTraceTest全@Test|変更Trace全sourceの既仕様回帰。固定controller source inventoryとmemorySpringServlet、属性故障redaction、全route/actor、nested owner/二重close/100並行、null/未知を維持|

新5＋既存10=全15を一つの選択exec/sessionで実行する。旧成功の再確認目的ではなくTrace Main変更後の必要回帰。旧Testは実VM/DB/JMS/鍵/held四/Producer/ingestを呼ばないことをsourceで確認した。所有するpublic repo controller/config sourceをinventory照合として読む。MockServletRequest/Response・Caddy metadatafilterはmemoryのみで実network/permission付与0。固有2-5のPrincipalは0-format合成contextのimmutable表示fixtureで認証や発行に使わず出力しない。

実際のProducer/APIingestはheld graphへ依存するため製造・PG強化レビューと静的検査を実施し、当15へ含めない。REQUEST local/outbox/DB＋MENU別eventID、HTTP結果不変、未知/null/collisionのmetadata故障、API16bind/UK/ACKをsourceレビューで追跡する。実HTTP/暗号/SQLtransaction/再配送の未実測をPASSへ変換しない。

実行command・OS/JDK/tool・source・終了code・静的・line/method/class/branch全100・normal全physicalCRC・TestID/XML・BUG・manifest path/hashは045結果へ保存。期待値はUI/SS固定tableでありproductionから生成しない。現時点NOT_RUN、第一V/CHR/native/451/正式受入は未完。
