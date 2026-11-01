# Revocation独立graph 原三単体テスト仕様

source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、HEAD74566fc7bf0b1965bac96c997d6e3eb9312537ee、PG17720。開始1/2.5/5pp cap10・fresh79/残21、主F03/関連P015-01参照追加0。NK-WEB-001/002、AUT004/UI226232234/SS314331332352354、QA050/SSC171・328、元1424/1454/905、REVOCATION-GRAPH328001～003を継承。

原RevocationJdbcGraph328Test全三を改変せず実行。Main RevocationRetryCoordinator.preserveFatalは自身のJDK queue/identity set/cause/suppressed/SQLnextだけを使い、未呼出しtransaction.combineにある保留WSEへは委譲しない。Main classにはstatic資源初期化なし、instance field/constructor/dispatchOne/transaction/codec/wireは当wholeから一度も呼ばない。RevocationRetryException constructorは固定catalogだけ。PT_DEFAULT、1975のWSE/TIE九試験を分割/再送しない。実DB/接続/Logout/再送/暗号/認証/Root/native/VM/permit/Unit操作0。

|Test ID/method|入力と独立期待値|
|---|---|
|REVOCATION-GRAPH328001 graph328001SqlNextFatalCannotBecomeAnOrdinaryCatalog|SQL nextのcauseに先に作ったError、assertSameで元identity|
|REVOCATION-GRAPH328002 graph328002MixedCyclesAreFiniteAndLateFatalRetainsIdentity|SQL next循環/alias、fatal無し有限帰還、後追加suppressed fatalの元identity|
|REVOCATION-GRAPH328003 graph328003ExistingCausePriorityNullAndRedactionRemainFixed|cause/suppressed/next競合の既cause優先、direct Error、SQL leaf/null NPE、固定redacted catalog/cause null/suppressed0|

expectedは元literal/事前にnewしたobjectで、production methodから生成しない。正常/境界/異常/null/例外を当有限graphで確認し、元JUnit Timeoutのframework worker実総数は未測定null、fixture独自Thread0。並行/実再送/DB commit-closeは別契約のため非該当/未実施。全Source二/physical四=Code三（未実行Outcome含む）/NoCode SqlWork一を分母、constructorの自然B0と四counter100を区別して実測する。

command `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17720_revocation_graph_three_pt_v1.py`。正常compile14216同source六jar/JDK25.0.4/既qualified reporter、元whole三だけ選択。command/time/branch/HEAD/環境/input/XML/exec/hash/exitを公開manifest保存。旧source成功・別scope coverage合算0、正式1964/53・歴史17/190・工数null・新WBS受入0/QA051final/全HOLD維持。
