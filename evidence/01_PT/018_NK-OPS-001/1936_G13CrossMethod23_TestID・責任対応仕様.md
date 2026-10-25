# G13.07 横断2 Test classの23method・既存Test ID・責任対応

2026-10-25 16:03 JST、G13_CROSS_METHOD23_TRACE_V1/source64446不変更、開始.5/2/6pp/cap10。fresh07:02:26UTC使用2/残98/reset1793513544/secondarynull、現在窓残10以下/取得不能等で保全、旧累計80/90停止なし。

API=`src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/BorrowedJdbcFatal329Test.java`、WEB=`src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/TargetBusinessControllerTest.java`。二つはfile primaryが未確定であり、下記methodの業務/実Main責任を分割して示す。1431の過去群主P00405をartifact主担当へ読み替えず、QuestionControllerの原Main担当P01618と質問明細・削除の業務P01623も区別する。

|source|method|既存Test ID/family|業務/契約WBS|実Main subject:原担当|既存独立期待値の根拠/適用範囲|
|---|---|---|---|---|---|
|API|borrowed329001UserSearch|PT-BORROWED-GRAPH329001|WBS-P010-01|UserQueryRepository:WBS-P010-01|user.search; borrowed connectionを閉じない|
|API|borrowed329002UserDetail|PT-BORROWED-GRAPH329002|WBS-P010-01|UserQueryRepository:WBS-P010-01|user.detail; marker変換catchのないmode2は仕様非該当|
|API|borrowed329003ScenarioRows|PT-BORROWED-GRAPH329003|WBS-P008-01|ScenarioRepository:WBS-P008-01|scenario.games|
|API|borrowed329004ScenarioSearch|PT-BORROWED-GRAPH329004|WBS-P008-01|ScenarioRepository:WBS-P008-01|scenario.search|
|API|borrowed329005ScenarioDetail|PT-BORROWED-GRAPH329005|WBS-P008-01|ScenarioRepository:WBS-P008-01|scenario.detail|
|API|borrowed329006MediaQuery|PT-BORROWED-GRAPH329006|WBS-P009-01|MediaRepository:WBS-P009-01|media.animationMenu; MediaQueryException09-03は関連|
|API|borrowed329007LogSearch|PT-BORROWED-GRAPH329007|WBS-P010-04|LogQueryRepository:WBS-P010-04|log.search|
|API|borrowed329008QuestionPaged|PT-BORROWED-GRAPH329008|WBS-P014-01|QuestionQueryRepository:WBS-P014-01|question.questionSearch; request13-01は関連|
|API|borrowed329009QuestionDetail|PT-BORROWED-GRAPH329009|WBS-P014-01|QuestionQueryRepository:WBS-P014-01|question.questionDetail|
|WEB|ntc001OnlyReceivedVisibleFormIssuesOneCurrentToken|NTC-BIZ001|WBS-P016-21|NotificationController:WBS-P016-21|RECEIVEDだけtoken1/他4state0、NTDREQ01|
|WEB|ntc002AndQdl002IndependentWholeRequestAndCompletionFirstWrite|NTC-BIZ002,QDL-BIZ002|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|literal304byte/302、first completedAt保持|
|WEB|qdl001OnlyVerifiedDetailIssuesOneAndInputRetryNeverIssuesReplacement|QDL-BIZ001|WBS-P016-23|QuestionController:WBS-P016-18|確認済detail token1、list50link/form0、再入力UUID0|
|WEB|ntc003AndQdl003AllPendingCapacityFreshRefusalHasNoUuidOrMutation|NTC-BIZ003,QDL-BIZ003|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|全10pending時409/UUID0/業務更新0|
|WEB|ntc004AndQdl004CurrentRetainedPurposeAndSessionRequiredBeforeMutation|NTC-BIZ004,QDL-BIZ004|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|token/session/用途不一致409、確認不正400|
|WEB|ntc005AndQdl005FailureCodesKeepSameTokenOrTerminalAndRefreshOnlyReads|NTC-BIZ005,QDL-BIZ005|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|固定errorcode、同token/最新state、refresh更新0|
|WEB|ntc007AndQdl007ActualApiOneChangeAndRetainedReplayWithoutPreRead|NTC-BIZ007,QDL-BIZ007|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|SQL業務version1、同token再送保持、nativeではない|
|WEB|ntc008AndQdl008OneHundredRealApiCallsKeepOneMutationAndNinetyNineReplays|NTC-BIZ008,QDL-BIZ008|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|100request/version1/replay99、Web TX0|
|WEB|ntc006AndQdl006UnknownTransportAndStoreCompletionNeverFakeSuccess|NTC-BIZ006,QDL-BIZ006|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|UNKNOWN/timeout/store commit-close不明を成功化しない|
|WEB|targetBoundaryAndLegacyAssemblyRemainClosed|NTC-BIZ006,QDL-BIZ006|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|constructor/null/foreign principal/legacy assembly境界|
|WEB|qdl009OwnerIsolationAndLiteralCodePointSummary|QDL-BIZ009|WBS-P016-23|QuestionController:WBS-P016-18|他owner404、先頭100codepoint/escape/業務更新0|
|WEB|ntc006AndQdl006RealHttpSameCoreActualApiCsrfListAndReplay|NTC-BIZ006,QDL-BIZ006|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|固定HTTP/DOM/CSRF/Replay期待。実HTTP未実行|
|WEB|ntc004AndQdl004InvalidBindingReadsFreshStateWithoutMutationOrReplacement|NTC-BIZ004,QDL-BIZ004|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|不正bind再表示、fresh read、更新/新token0|
|WEB|ntc006AndQdl006FatalIdentityIsNeverConvertedToRetryOrSuccess|NTC-BIZ006,QDL-BIZ006|WBS-P016-21,WBS-P016-23|NotificationController:WBS-P016-21,QuestionController:WBS-P016-18|元fatal identity保持、retry/successへ変換0|

APIの独立oracleは1431（SHAea7121841475c0bed4e0ce3ef84534846db00d8d051b2039223a50553e95a938）。SQL primary/next.cause/marker+close fatalは元Error identity、非fatalはrepository固有literal診断/result、prepare/execute/Statement.close各1、borrowed Connection commit/rollback/close各0。SS312324332354/SSC329/BUG1592/YKT1345を参照し、元run/sourceの成功を現sourceへ転用しない。

WEBは016_NK-WEB-002/083（SHA9fc856dfea8c2bd56d0448ba4ed8f605decee436bde54d33b1f6d5f5fc693324）のRD FUN010013/NTF001..012/QST005..010/AUT002、UI224232236/SS313314323324332351/QA049。共通token契約P01503・form/escape/validation P01507と、取消・削除業務API P01402は関連として保持し、各screen/Controllerの担当を上書きしない。Test familyが複数methodに現れる場合は`source#method`とfamilyの組で一意にし、新しい実行Test ID/件数を作らない。

JDK25の工具だけをcompileし、JavacTask.parseのみで当2sourceの@Test method名/位置/parameter countを抽出する。analyze/generate/target compile-load-init/JUnitは行わない。独立postは正常9246の当2Test class bytesに対するJDK javap宣言とJUnit Test annotationを読み、同じ23method集合・SourceFile/hash・原Main subject担当へ照合する。固定spec別parse・構文7vector・metadata改変negativeを確認し、構文の一致をassertion/oracle全件合格やcallee解決の証明とはしない。

実DB/SQL/Loopback/HTTP/broker/Root/VM/子target JVM/credential/鍵/intent/permit/配備/Unit/遠隔操作0。工具自身の限定JVMだけを所有して有限終了を記録する。旧成功確認再演/拒否試行/Currentbaseline/oracle変更0。

成果は23methodの初期対応であり、file登録1781/1789/残8・正式1964-53/17-190/工数null/QA051final/全current auditHOLD/全actualHOLDは不変更。原941943/481484/費用受入意味保持、費用G13.07一回。保存後は必要な当source通常PT資格又は他独立PGPTへ進み、小群/報告/PMO返信待ちでは停止しない。
