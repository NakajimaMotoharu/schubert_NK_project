# 1239 直接unknown再送出：七scope・十三指摘の型根拠

source682a4b99eb0b95bcd4f1cd276fea75b5f2e62e3b、WBS-F03主費、開始.25/.75/2pp（event1417）。PG実物を点検し、当箇所は既SS343/352どおり正しく、Production変更不要と判断した。汎用catch全体の免除・拒否PT代替ではない。

5922/元1328 actual0、全851 Main/1666実classpathを固定したjavac parse/analyzeでcatch1094箇所を取得。既helper/独立fixture compile0、`-proc:none/-implicit:none`、Production method/PT/VM/DB/サービス実行0。private manifest **bd5bf95bc9b301958f6f0cac23437f79cb3889fd6bc74cbb5f1ed9ec5323fc2b**、source/class/提供annotation/固定third-party BOM・helper/fixture/command全hashはWorkPG379/pg5922-current-catch-facts-v1へ保存。型factは合格や適用性判定そのものではない。

個別点検対象：ArtemisManagementReadinessClientのputAcceptorsOperation/putRolesOperation/putExpiryOperation/putAddressSettingsOperation/query各RuntimeException|Error（十診断）、LinuxSystemdSession.Native.invokeのRuntimeException|Error（二）、WebBrokerContexts.closeのError（一）。全てresolved parameterをbody一statementで同じinstanceのままthrowし、その直後により広いException/Throwableのchecked redaction catchがある。再代入/別throw/return/cleanup/retry/Throwable graph探索はない。削除すると未知/fatalを固定checked/ordinary failureへ正常化するため、この型区別のcatchは必要である。

反証unitは他object throw/代入/close呼出し/return/誤catch型/新wrapperを拒否、pyflakes/unit0後5924実0。各source/hash/全parameter span/型/symbol/control/隣接境界/元独立期待をjoinした十三行だけを記録し、following checked catch自体や資源post/Root/DONE/DB不変の適合へ広げない。raw十三指摘は保持、適用理由を一括抑制0。

独立期待の対応：ArtemisUnknownBoundaryTestのmqUnknown001/004（NPE/Runtime/Errorの同一instance・有限proxy・一回呼出し）、LinuxSystemdSessionTest.nativeInvocationPreservesUnknownRuntimeFatalAndSanitizesCheckedFailures（固定MethodHandleの正常/null/checked/Runtime/Error、実Systemd接続無し）、WebBrokerContextsTest.closeIsIdempotentAndPreservesFatalOverOrdinary（合成factory/同Error・非成功時非closed/再回数）。Testソース/旧790のsemantic identityだけを参照し、進行中PG5926の当source原XMLへjoinするまではcurrent PASS/refsを空のまま保持する。旧source試験成功を輸入せず、新規試験発行0。

公開`evidence/provisional/PG5924-direct-boundary13-v1/manifest.json` **93cf3ddad9386c7e1a670b0d8d2aae836fba454f7be1ae534de674e81a4a4b65**、decisions **3785851958f559b97d6399ef69bf9c20cacaa250f7dbc35f02a615d01b7f4729**。**pending545/未点検999/raw1544**、新個別根拠十三/新実行PT0/coverage加点0/代替完成0。正式1964/53/17-190/工数null/QA051final・原v3v4/実VM等HOLDは不変更、原全体3973のsource固定を維持して独立残F03へ継続する。
