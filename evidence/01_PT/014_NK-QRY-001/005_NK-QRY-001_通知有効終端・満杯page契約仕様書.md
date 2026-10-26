# 質問通知・有効状態投影/満杯page追加仕様

2026-10-26、P013_QUERY_VALID_PAGE_STATE_BATCH_V1、主P01301/関連P01401等追加費0、開始1/3/8pp cap10・used27残73/reset1793513544。QRY003の追加、Main変更予定なし。FUN011～013/QST005～010/NTF001～012、UI224/236/SS312/323/332§3/9・411/451。

|新Test ID/method|入力・操作|独立期待値|
|---|---|---|
|PT-QRY-SQL009 / sql009ValidProcessingCancelledAndFiveErrorCodesRemainTypedData|NTD3/ADMIN8、正常business rowのPROCESSING/CANCELLED及びERROR五code、全row有効。error-code入力literalとexpected enumは独立固定表|PROCESSINGはstartedのみ、CANCELLEDはcancelledのみ、ERRORはstarted+errorAt+error code/message、その他timestampなし。PROCESS_FAILED→PROCESS_FAILED、SYSTEM_UNAVAIL→SYSTEM_UNAVAILABLE、RESOURCE_LIMIT→RESOURCE_LIMIT、DATA_INTEGRITY→DATA_INTEGRITY、PROTOCOL_ERROR→PROTOCOL_ERROR。questionId/body保持/answerなし/owner8/target3、borrowed所有不変更|
|PT-QRY-SQL010 / sql010FullQuestionPagePreservesFiftyUnansweredRows|QSS empty/USER7、total50/pages1/effective1、valid UNANSWERED row50件/ID50～1/各本文と受付ID/username固定|Paged1,50,50,1,1,50、独立QuestionSummaryRecord ID50～1/CodePoint100summary/answerAt empty、wire page整合/owner7とRS→PS解放|

SQL009のERRORは保存済みbusiness状態の有効投影で、SQLException/RuntimeException/Graph9故障注入ではない。未対応code/不正状態/必須NULLは入力しない。正常typed schemaの時刻mask・削除flag・本文の契約をPGで事前照合、実行後禁止product probe0を独立確認する。各期待値はUI236状態表/固定UTC/enum対応literalから構成し、Production parser/mapper/enum.valuesでexpectedを生成しない。private reflection/実DB/外部所有/crypto/VM等なし、全HOLD維持。

ADM081の新二と合わせ、新4＋関連48=52method/7suite・一source/run。既sourceの成功を新sourceへ移植/旧execの合成をせず、全六source unit/七physical Mainを独立測定。no-Code interfaceの四0/0はN/A保持、Repository未到達は未達。新methodsだけのPASSを全program受入とせず、正式1964PT/53scope・17/190/工数null/QA051final不変。結果・command/OS/JDK/tool/branch/commit・coverage/BUG・manifest hashは006/shared018へ格納する。
