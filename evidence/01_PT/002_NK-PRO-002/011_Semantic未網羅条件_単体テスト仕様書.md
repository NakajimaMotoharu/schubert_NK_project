# NK-PRO-002 Semantic未網羅条件・独立境界単体テスト仕様

2026-10-25、Program NK-PRO-002、主WBS-P002-02、群PROTOCOL_SEMANTIC_MISSED_BOUNDARIES3_V1、開始1/3/8pp/cap10、共有9/残91/reset1793513544、専有実費/実N-T/工数null。旧source3154/9682当単一runの25missed line/3method/19branchを契機に、code変更でなく必要な直接component試験を追加。関連RD MSG001～011/MSG-F01～09・UI234～236・SS322§9/SS323、既Program001/P06・009/010。PGの省略/期待値緩和なし。

新class SemanticDirectBoundaryTest、対象PayloadSemanticValidator.validate/validateUserCreation/validatePassword/validateDateRange/validateQuestionSubmission/validateWebLog。TypedPayloadValuesのfunctional portへ独立literalを渡し、named scalarの先行拒否でsemantic未実行にならないよう分離する。fixtureはfield名と入力だけを組み立て、expectedは以下UI/SSの固定算術/条件に置く。Production methodからexpectedを作らない。

| 新Test ID / method | 入力・操作 | 独立期待値と根拠 |
|---|---|---|
| PT-PRO-002-SEM001 / sem001PasswordCharacterByteAndUsernameLimits | UCRREQ01 Username FixtureOwner、passwordの12/128 ASCII、64絵文字、11/129文字、65絵文字、末尾ASCII space、username同値/大文字同値、username記号。UPWREQ01は128ASCII/64絵文字 | 12～128codepointかつUTF-8 256byte以下、末尾spaceなし、usernameとの大小同値は禁止。64絵文字=64codepoint/256byteで受理、65=260byteで拒否。各invalidはLayoutValidationException。文字数/byteをProduction算出してexpectedへ使わない |
| PT-PRO-002-SEM002 / sem002InclusiveDateLimitsAndOneSidedFilters | LGSREQ01 Page1/size100、20260101→20260201/同+1ms、逆転、両側なし/片側のみ。NTSREQ01 Page1/size50、20260101→20270102/同+1ms | 2026年1月31日を含む31日ちょうどは受理、+1ms拒否。2026年365日＋1日=366日ちょうど受理、+1ms拒否。逆転拒否、片側なしは範囲比較非適用で受理。固定17桁JST文字列で期待値を独立指定 |
| PT-PRO-002-SEM003 / sem003QuestionAndWebLogTextContracts | QSBREQ01質問の正常/空/末尾space、WLGEVT01 GET/ABCDEFGH/get/GE/ABCDEFGHIと/safe、relative、query付きpath | 質問空/末尾ASCII space拒否。HTTP methodは大文字ASCII3～8、pathは先頭slashかつqueryなしを受理。他はLayoutValidationException、HTTP送信/実Log記録なし |

同一run品質確認は既semantic8＋既PAGE3＋既PayloadTypeCatalogTest.allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes一件＋新SEM3=15case/4suite。新IDは3件だけ。既normal64methodの目的は正常switch全layoutの到達確認で、expected件数64/69型/14record layoutはUI/SS独立根拠を既仕様に参照する。入力shapeをProduction catalogから作ることと、正常条件の固定期待/roundtripを分離し、roundtripだけで全oracle/Programを資格認定しない。既normal64の他Test/IndependentNamedFieldOracle.verifyAllは実行しない。

安全判定PT_DEFAULT：今回もmemory値/collection/Unicode/byte/time parse/例外assertのみ、実認証/credential/DB/JMS/HTTP/VM/Root/cohort/native/鍵/配備/intent/permit/RuntimeHookなし。Test fieldのpassword/Username/Log名は合成値で実秘密ではなく、拒否操作の再試行/探索ではない。自己所有有限JUnit/normal compilerとnew-only host directory/XML/execに限定し、旧exec unionなし。

新Testをformat後source commitへ固定、同source六module normal compile/null/lint/format（PT0）、Main/test byte差と必要な新Test PMD/Checkstyle、Main同byteの既SpotBugs入力証拠の適用範囲を照合する。実15/4はsource/依存/command/exit/時刻/OS/JDK/XML/sessionを保存、独立postで当class CRCと全line/method/class/branch countersを確認。未知/未実行/Failed/skipped/abortedをPASSにせず、四100は実証まで未達。障害を発見したら修正前915/916を起票。全Program/全六module PT/正式1964-53/17-190/QA051final/全HOLDは別gateとして保持し、通常群後も継続する。
