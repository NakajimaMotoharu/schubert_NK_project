# Session・認証 独立graph原八単体テスト仕様

source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、HEAD52fc424c686800e0a60397755bcfe81250a9b239、PG17700、低1/標準3/高6pp cap10・fresh78/残22。主F03、P015-01/P002-01参照追加費0。NK-WEB-001/NK-AUT-001、FUN001/AUT001..004、UI226/242、SS312/314/331/352/354、SSC328/329/330・BUG1591/1596/YKT1065を継承。

1975で保留中のGraph9はTemporaryInfrastructureException/WebStartupExceptionの二Main/三Testであり、今回のSessionStoreException/AuthenticationInfrastructureExceptionは別のmodule-local実装で、その呼出しも委譲もない。元905/902の責任分離へ照合。保留解除/別名で同処理再試行ではなく、JDK Throwable/SQLExceptionの固定有限graph・例外constructorだけの独立通常PT。PG本体二各36行・原四Test全189行を全文読取済み。前checkpointのTest216行表記は189へ追記訂正し、旧文を保全する。

|原Test ID/method|入力/操作・独立期待値|
|---|---|
|CAUSE3404-003/mixedCauseAndSuppressedCyclesTerminateAndReachableFatalRetainsIdentity|二RuntimeExceptionのcause/suppressed循環、fatal無し帰還/後追加Errorが元identity|
|SESSION-GRAPH328001 graph328001SqlNextFatalCannotBecomeAnOrdinaryCatalog|SQL.next.causeに元Error、assertSameで保持|
|SESSION-GRAPH328002 graph328002MixedCyclesAreFiniteAndLateFatalRetainsIdentity|SQL next循環/alias、初回帰還/後追加Error identity|
|SESSION-GRAPH328003 graph328003ExistingCausePriorityNullAndRedactionRemainFixed|cause/suppressed/nextの競合、Sessionは既cause優先・direct fatal/null NPE・固定catalog/cause null/suppressed0|
|CAUSE3404-002/suppressedCyclesTerminateAndReachableFatalRetainsIdentity|suppressed循環、fatal無し帰還/後追加Error identity|
|AUTH-GRAPH328001 auth328001CauseFatalCannotBecomeAnInfrastructureResult|causeとsuppressed alias循環、元cause Error identity|
|AUTH-GRAPH328002 auth328002SqlNextCycleTerminatesAndPreservesTheOriginalFatal|SQL next循環、初回帰還/後追加cause Error identity|
|AUTH-GRAPH328003 auth328003ExistingSuppressedPriorityNullAndRedactionRemainFixed|Authは既suppressed優先・direct/cause-only/混合循環/SQL leaf/null NPE・固定catalog/cause null/suppressed0|

期待値は先にnewした元Throwable、SSのmodule固有順序とliteral固定診断。production classifierでexpectedを作らず、SessionとAuthの順序を勝手に統一しない。全正常/境界/異常/例外/nullと有限帰還を元assertion/@Timeoutで確認。fixtureの並行/再送・業務commit/rollback/closeは非該当/別試験であり成功に代入しない。JUnitが元Timeoutのframework workerを使うが、fixture独自Threadや外部processを作らず、実DB/接続/JMS/権限/鍵/Root/native/VM操作0。

PT_DEFAULT。command `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17700_session_auth_graph_eight_pt_v1.py`。JDK25.0.4・正常compile14216同byte六jarと元qualified reporterを使用、原whole八だけ選択、改変/新fixture/heldcase抽出なし。source/branch/HEAD/command/実環境/時刻/exit/input/XML/exec/hashをmanifest保存。二Source全physical二/Code二を分母、四counterの実測後だけ技術資格を計上する。実Root/native/正式1964-53/歴史17-190/工数null/QA051final/1975その他HOLDを保持。
