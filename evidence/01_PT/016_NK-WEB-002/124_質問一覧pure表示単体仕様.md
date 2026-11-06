# SCR022 質問一覧pure表示 単体仕様

Program NK-WEB-002 / WBS-P016-22。RD FUN-012/QST-006/008、UI224/236、SS313/314/323/332、QuestionListViewModel success/invalid/getters/toString経由でrow/link/encode。現Main D8不変更。全16methodの独立oracleは固定labels/JST日時・row10field・URI文字列。Production methodをexpected生成に使わない。

Fixtureはimmutable QuestionSummaryRecord/PagedResponseData、合成表示Principal、QuestionSearchForm.bind、既検証Spring URI文字処理のみ。正常filtered50行はkeyword é &+・ANSWERED・date2026-11-01・owner readerに一致させる。USER同owner/ADMIN別owner、双方form role不一致、3状態と日時不整合、first/middle/last/clamp、Unicode99/100/101、順序・重複・件数・null・immutable/copy、自己所有2worker8taskの隔離を照合する。並行poolはtry-resourceと各10秒join。再送は状態を持たないpure projectionのため非該当、実再送保証には拡大しない。

通常PT_DEFAULT、具体範囲はPMO957。実controller/HTTP/DB/JMS/VM/Root/鍵/実session/held4は実行しない。元Controller carrierの既成功は確認再演しない。shared012/profile062でprepare/static、Git source固定後全16を一回、単一exec/全physical CRC/全四counter100/strictpost。Main正常PG20112/六SB20114はsameD8の既成功を再利用、全回帰/全451へ合算0。環境/command/対象commit/exit/XML/hash/coverageと障害は結果125・元manifestへ保存。群3990原1/3/6pp cap8、真正終端後freshを共通end_fieldsで結合。正式1964/53・歴史17/190・工数null、全SCR022/HTTP/DOM/owner認可/終了依存未受入。

|Test ID|method|
|---|---|
|PT-WEB-QLIST001|emptyReturnsPlainView|
|PT-WEB-QLIST002|allStatesHaveIndependentRows|
|PT-WEB-QLIST003|userPagingLinksAndClamp|
|PT-WEB-QLIST004|adminAndUserFilteredLinksAreLiteral|
|PT-WEB-QLIST005|invalidFormsStayUnpaginated|
|PT-WEB-QLIST006|roleMismatchRejectsBothDirections|
|PT-WEB-QLIST007|wrongEffectivePageRejects|
|PT-WEB-QLIST008|rowCountMismatchRejects|
|PT-WEB-QLIST009|duplicateIdsReject|
|PT-WEB-QLIST010|ownerScopeAndSummaryLimitReject|
|PT-WEB-QLIST011|inconsistentAnswerTimestampRejects|
|PT-WEB-QLIST012|orderRulesAreIndependent|
|PT-WEB-QLIST013|nullBoundariesReject|
|PT-WEB-QLIST014|outputSnapshotIsImmutable|
|PT-WEB-QLIST015|unicodeBoundaryAndAdminCrossOwnerAreValid|
|PT-WEB-QLIST016|parallelViewsKeepActorsSeparate|
