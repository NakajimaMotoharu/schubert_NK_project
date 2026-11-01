# Receipt・所有JDBC 原三単体テスト仕様

source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、HEAD2ae61c645db5fc7cc854299b4ca583de924e75be、PG17760、開始1/3/6pp cap10・fresh79/残21。主F03/関連P011-04参照追加費0、NK-WEB-002/FUN001/AUT004/DAT009・UI241242/SS312313331§9.4/332354・QA048/SSC175/329/BUG1592/YKT1348、元1448/1452/1912を継承。

原ReceiptFailureGraph329Test全三/257行、Repository179/Exception10とReceiptReference・SessionStoreExceptionの呼ぶ関数を全文確認。前checkpointのRepository181は179へ追記訂正、元文保持。PT_DEFAULT、自己JDBC proxy/固定ID・UTC/手製SQLException graphだけ、実DB/業務SQL/認証/operation token/署名/鍵/Root/native/VM/permit/外部通信0。保留classifierへ委譲せず、1975やDB依存別Testの分割/新fixtureではない。

|Test ID/method|入力・操作|独立期待値|
|---|---|---|
|RECEIPT-GRAPH329001 receipt329001SelectedSqlGraphPreservesFatalAfterOwnedSetupClose|getConnection/setAutoCommitでcause/suppressed/next内包Error三mode|先にnewしたError identity、取得前close0/取得後1、rollback/commit0|
|RECEIPT-GRAPH329002 receipt329002BothSqlCleanupGraphsCannotDisappearBeforeFixedCatalog|read ResultSet/Statement/rollback/Connection・register InsertCloseでsecondary SQL graph|元fatal identity、取得済Connection/Statement各close1・該当ResultSet close1、それ以外0・rollback1/commit0|
|RECEIPT-GRAPH329003 receipt329003ExistingUnknownPriorityAndFixedNonFatalCyclesAreUnchanged|非fatalSQL循環/同一Throwable、unknown primary＋direct secondary Error、SQL primary＋unknown close、primary/secondary Error競合|SQLは固定catalog/cause null/suppressed0、既unknown同一性＋固定Receipt marker、SQL＋unknown closeはunknown優先、primary Error identityを保持。全取得scope各1close/rollback1/commit0|

Receipt固有の既unknown優先をAPI共通規則で変更しない。expectedは元objectと固定catalog/marker・明示counter、Productionから生成しない。正常/境界/異常/null相当の欠落・例外/close graphを当経路で確認、取引成功や実DB不変/owner認証を証明したことにしない。並行/実再送/同receiptの競合は別契約で未実施。元JUnit Timeout framework worker実数null・fixture独自Thread0。

対象全二Source/三physical=Code二/NoCode Work一。未実行method/branchも分母、exception自然B0とstrict四100を区別。command `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17760_receipt_owned_graph_three_pt_v1.py`。正常compile14216同source六jar/JDK25.0.4/既qualified reporter、元whole三だけ選択。元command/time/環境/branch/HEAD/exit/input/XML/exec/hashをmanifest保存、旧Source成果/exec union0。正式1964/53・歴史17/190・工数null/新WBS受入0/QA051final/全HOLD不変更。
