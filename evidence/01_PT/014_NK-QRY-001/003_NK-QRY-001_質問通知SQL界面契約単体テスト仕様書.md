# NK-QRY-001/NK-NTF-001 質問通知四query SQL界面契約仕様

2026-10-26、P013_QUESTION_SQL_INTERFACE_CONTRACT_V1、主P013-01/関連P014-01追加費0、開始1/3/8pp cap10、used27残73/reset1793513544。FUN011～013/QST005～010/NTF001～012、UI224/236/241、SS312§10/323/332§3/9/411/451/SSC157。対象QuestionQueryRequest.query全四dispatchとQuestionQueryRepository四projection、Main変更予定なし。

後続索引QuestionQueryRepositoryは1459/1930/1936を候補として照合。旧DB115/旧source資格/原既eight plainは当sourceへ転用せず、新SQL界面を実DB再演の代替としない。新QuestionSqlContractTest/PT-QRY-SQL001～008八method＋関連QuestionQueryPlainContractTest八methodを固定source/一run16/2suiteで検証する。

## PT_DEFAULT、安全範囲とoracle

public JDK Connection/PreparedStatement/ResultSet proxyのみ、driver/URL/backend/DB/network/private reflection/外部process/旧fixtureなし。全rowは有効な合成値、callback未定義methodはAssertionError、SQL/不正DB値/close等fault注入なし。Graph9/preserveFatalへ入る例外経路、実Root/VM/鍵/permit/native等を実行せずHOLD維持。例外はquery前の明示null/USERのusername指定禁止だけ。禁止product probe0を独立postへ要求する。

SQLはSS332§9のUSER質問owner限定/ADMIN質問非削除全件/通知はADMINも本人だけ、count/list共通predicate、日時降順+ID降順、limit50をliteral fragmentで確認。bind expectedはUI236 byte offsetと固定UTCから独立構成、SQLから逆算しない。row expectedは固定typed record/直接text・Unicode codepoint100の既知literalから作り、Production mapper/summary/codecでexpected生成しない。borrowed ConnectionはautoCommit=false/readOnly=trueの参照二callとprepare一回のみ、commit/rollback/close/config0、ResultSet→Statement一回解放。

|Test ID/method|fixture・入力・操作|独立期待値|
|---|---|---|
|SQL001/sql001QuestionEmptyPagesSeparateUserAndAdminOwnership|USER7/ADMIN8、QSS empty/page999999、total0/pages1/effective1|USERだけowner bind7、ADMINにowner predicateなし、十一optional bind各null＋page最後（USERは十二＋page）、Paged1/50/0、原page保持|
|SQL002/sql002QuestionFilterMasksUseTypedDuplicateBinds|ADMIN八、五filter32mask keywordé_%\\/usernameunit7/stateANSWERED/from/to|username/state各二、escaped substring三、UTC from/to各二の固定11bind＋page。入力SQL埋込なし|
|SQL003/sql003QuestionSummaryCountsCodePointsNotUtf16Units|有効ANSWERED row・本文😀100＋tail/時刻microsecond|独立QuestionSummaryRecordのsummary😀100、UTC ms切捨て、question/receipt/username/state/answeredAtが固定一致|
|SQL004/sql004QuestionDetailBindsTargetAndOwnerAndKeepsFullText|USER/ADMIN各missingとfound（answered/unanswered有効値）|detail3 bind、USERのみowner7、非削除predicate、Optional.empty又は独立全文data、summaryへ切捨てない、response originalID一致|
|SQL005/sql005NotificationFiltersAlwaysBindCurrentActorIncludingAdmin|USER7/ADMIN8・type/from/to八mask・empty page|全てowner first=当actor、type二/from二/to二＋page、通知updatedAt/ID降順、question deleted textはSQL NULL契約|
|SQL006/sql006NotificationRowsPreserveDeletedLabelAndOwnerScope|deleted false/trueのvalid通知row|falseはUnicode100summary、trueは「削除済み」、Booleanflag/type/state/UTC ms一致、ADMINでもowner8|
|SQL007/sql007NotificationDetailsPreserveOptionalStatesWithoutRevivingDeletedText|RECEIVED非削除/COMPLETED非削除/RECEIVED削除、各missingも検証|Optional時刻/本文/回答/questionId有無が固定一致、削除data空/復活なし、全てtarget3+owner bound、originalIDresponse一致|
|SQL008/sql008NullBoundariesAndUserUsernameGuardNeverTouchJdbc|四wire各repo/connection/actor独立null、USER質問username指定|明示NPE又はQuestionQueryException/VALIDATION_ERROR、connection/prepare/close0、SQL catch未到達|

全体counterはcomplete Request/Repositoryと内包RowMapper interface三物理classを照合。interfaceのCodeなし/空counterはN/Aとして保持、0/0を100へ変換しない。normal六compile/NullAway-Werror→16宣言/依存byte preflight→一JUnit→独立XML/CRC/session/禁止probe/四counter・static当hash→Logと新二pathのbatch trace。異常/並行/実DB後条件は未実行で明示し、四100未達を隠す除外0。

command/branch/source/環境/終了/結果・coverage/hash/BUG/SSCは004結果及びshared018公開manifestへ記録。正式1964PT/53scope、17/190、新受入0、工数null/QA051final/全HOLD維持。PG reviewと新PTを進めるが、実経路や全PGPTの完了とはしない。
