# User照会四method・独立oracle意味対応

2026-10-26、群G13_USER_QUERY_FOUR_ORACLE_SEMANTICS_V1/.5-2-5pp cap10、source21d7c30425e7aa9ce435e808035a94fa4d75c93b。WBS-G13.07は変更記録担当、既artifact/cost担当WBS-P010-01は保持。完全名UserQueryRequestのfollowup索引一致0を候補確認に用い、旧成功不存在とは推定しない。Production/Test/DB等を新実行しない既文書/Main/Testの静的意味レビュー。

## 承認期待値と既assertion

UI236§3のUSR DATAは1-based offset1/64/65/5/70/8/78/6/84/3/87/10、pageSize50・reserved全space。§5のUDTは12桁ID。SS323§9.4はUSR field順usernamePrefix/X1,role/X1,state/X1,page/N1,pageSize/N1、UDT userId/N1、owner actor decimal/version001/target REQUEST:layout、欠落はFFFFFFFF。SS324§3はSCHUBERT-NK-OP1＋LP四field＋U32件数＋name/type/value LP、HMAC-SHA256。trim/lowercase/page補正とMessage/context混入は禁止。

|Test ID / classのmethod|fixture・操作|既assertion/独立期待の根拠|残条件|
|---|---|---|---|
|PT-ADM-040 / adm040DecodeAndCanonicalKeepAllOriginalQueryFields|prefix6×role3×state4×page2=144組、detail ID両端2、Messageだけ変更/case変更|listDataは96byte spaceへUI offset0/64/69/77を手組、expectedは元入力list/page literal50。detail false/true・response layout literalを別assert。checkはDataOutputStreamでLP/name/type/NULLを手組し標準Macで比較|checkのlayout/name/type selectorがProduction detailRequestへ依存（BUG1777）。144組は1PT内のfixture数で、PT件数へ加算しない|
|PT-ADM-041 / adm041RealReadOnlyQueriesUseTheSameDecodedValues|UserApplicationFixture.seedのu1/u2 ADMIN,u3 USER、各一session、検索/明細|expected PagedResponseData(1,50,3,1,1,3)、IDs[1,2,3]/role別[1,2]・[3]、u3/session1/version0、ID999 empty、SQL注入文字literal empty。readOnly/autoCommit/connection保持。SQL後条件app_users3/Inbox0/log0/version和0はfixtureの独立固定値|BeforeAllが実DB fixture生成、queryの実後条件/transaction/権限を本レビューで再確認したとはしない|
|PT-ADM-042 / adm042NullMalformedAndResponseMismatchNeverPass|null、Q/S/length/version、不正role/state/pageSize/reserved/UTF8/zeroID/他layout、応答target/type/page不一致、closed/RW/USER caller|typed PermanentProtocolExceptionと固定redacted message/cause無し、null NPE、mismatch IllegalArgumentException、repository exception/AuthorizationExceptionを各assert|四不整合pageのassertThrows(RuntimeException.class)はNPE等も受け得る広い型。期待拒否型の独立詳細化は別候補・未是正、これを全NPE排除証拠にしない。DB部分はHOLD|
|PT-ADM-043 / adm043ConcurrentRequestsOwnIndependentCanonicalBuffers|自己100caller、n偶奇でdetail/list、actor/id/prefix/pageを入力から作る|expected listはnから計算、所有canonical二個を作りfirst close後zero配列/second digest不変・再check、Future.get20s|checkの上記selector依存。既sourceのthread/HMAC/closeを本工程では実行せず、鍵close群の再試行や並行成功へ転用しない|

checkのMac計算自体はProduction canonical bytes/計算methodをexpected生成に使わないが、metadata selector三箇所は検査対象を使っている。ADM040の個別bool assertは別防御として保持するものの、451の独立期待値要件を満たすため入力側の明示layoutへ切り離す。BUG1777/YKT1528を修正前起票した。QuestionQueryRequestTestの二getterは入力layoutから計算したexpectedと実値を比較するassertionで、同じoracle生成違反ではない。

## source/hashと状態

UserQueryRequest.java c85cf970f232c076bb5514a429388a7638a2bac2b9ffe9319f11a8f427f475fa、UserQueryRequestTest.java 15598648abf4a97144008c87fa08d25312e0cffc053ee48f182917df082af8be、UserApplicationFixture.java e284b4ced7b4165abac62aee068eaab943372cea11fa89cabbe5460840734d44。SS323 085a751480baf929bea7c80e758a66b3fffe4dee4a3f4fd84b6eed2b38e86523、SS324 2bc99fd66ca1121a1ab4ae44e97aab96b52d4cf4c8145f6a425f89c7b07ce774、UI236 0468f20da240ed61e056084f80e88f3b3f5d60b3afb70f23710a8320c5c653c9。

STATIC_ORACLE_REVIEW_COMPLETE_WITH_FINDINGS。新製品PT0/coverageなし/受入0、正式1964/53・個別17/190・工数null・QA051final・全安全HOLD維持。BUG1777の是正は別の着手見積/必要source固定・compile/許可された静的確認へ進む。ADM042の広いexception assertionも新たな品質不足候補として残し、実拒否型を推測して試験をPASSへ改変しない。DB/JCE/worker/実VM/Root/鍵close検証を起動しない。
