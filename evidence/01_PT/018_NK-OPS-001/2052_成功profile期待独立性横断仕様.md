# 成功profile期待・fixture分類の独立化

2026-10-26追記訂正（BUG1821/2055/PG10349）：下記416はassert prefix字句数（import/helper名等を含む）で、実assertion呼出し数は未計測null。保持条件は元全token/全assertionの保持であり、件数を416と仮定しない。原値/元開始見積りは履歴保持、製品PT/正式受入へ変更なし。

2026-10-26、BUG1817/YKT1568、G03.01。関連UI232 §§5/7、各既存programのRD/UI/SS・原PT仕様/Test IDを保持する。本仕様は横断的なTest oracle是正の補足で、元program別PTの期待結果や未実施状態を上書きしない。

|source|原canonical owner/cost|対象呼出し数|対象|
|---|---|---:|---|
|UserCommandServiceTest|P01002|1|結果DTOの正常/異常profile invariant期待|
|UserMutationReplayServiceTest|P01003|1|非保存error fixture選択|
|QuestionMutationApplicationServiceTest|P01402|1|入力ResultCode別の期待拒否選択|
|QuestionMutationReplayServiceTest|P01302|8|wire生成二件、response fixture/再送code/負例期待六件|
|SessionOperationTokenLifecycleTest|P01503|1|完了可能な成功codeと拒否codeの期待選択|

package/classの完全pathはPG10332/10339 sourceChanges/sourceHashes。元@Test/method/Test ID・各program仕様は変更しない。原担当費をG03へ移管せず、関連追加費0で参照。Production classifierやwireValue/ResultCode本体は変更しない。

全12の `code.usesSuccessProfile()` をTest側の明示比較 `code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS` へ変更。UI232の0000/0200だけが成功data規則であり、ほかの0100～0107/9000/9001はerror。ここでenum identityはTestが指定するfixture入力で、Production classifierを期待値生成へ呼ばない。

|静的metadata ID|入力/操作|独立期待と根拠|
|---|---|---|
|AST-RSP-001～012|UI232の12code/nameの固定表と実source内predicateのOR/二identityを字句検査|SUCCESS/0000とIDEMPOTENT_SUCCESS/0200だけtrue。他10はfalse。Product enumをload/実行せず、sourceの実patternへ照合。|
|META-RSP-NEG001～020|五sourceごとにOR→AND/0200→FORBIDDEN/==→!=/code→otherCodeの四変異|元token復元guardが全て拒否。製品入力/製品試験ではない。|
|META-RSP-SOURCE|全五sourceの明示比較を逆変換して旧sourceへ比較、当normal全class比較|元416assertion/全非分類token保持。GJFの隣接SQL文字列は独立連結して同値照合。全Main1843/他Test不変。|

実command=tools/quality/pg10332_result_profile_oracle_plan.py→--emit-patchをapply_patch→当source固定→pg10334_result_profile_oracle_static.py/pg10336_result_profile_oracle_six_compile.py（-DskipTests）→pg10339_result_profile_oracle_post_v2.py。stage/OS/JDK/tool/source/exitはmanifestへ保存。比較演算子は共通LEXが一文字ずつ返すため==/||の実token規則を検査し、位置は実tokenから導出する。

元DB/key/crypto/exception graph/実Web等のPTはNOT_EXECUTED_HOLD。新しい製品実行/新fixture harnessでそれらを迂回しない。上記はsource/ASTの静的metadataだけで、製品PT PASS数・実測coverage・native/正式受入へ加算しない。元null/異常/例外/並行/再送の実Testは元状態を維持する。全G03/F03/451・四counter100・QA051final・全安全HOLDは不変更。
