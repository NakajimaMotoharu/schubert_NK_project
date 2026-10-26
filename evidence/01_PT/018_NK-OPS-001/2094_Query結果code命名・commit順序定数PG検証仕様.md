# 2094 Query結果code命名・commit順序定数PG検証仕様

2026-10-26、BUG1852/YKT1603・BUG1853/YKT1604。基点source95894757e2bd7f392262497ea620873430ccc5f1/PG10612正常。群P010_QUERY_SEMANTIC_CONSTANTS_V1、主責P01004/関連P01001-F03の重複費0、開始1/3/7週次枠pp cap10、実専有費/実token null。

PG1852-NAME001：UserQueryApplicationServiceTestのSYSTEM_ERROR_RESULT宣言/全identifierをIDEMPOTENT_RESULTへrename、literal0200は不変。UI232§7の処理済み冪等応答、9000 System一時障害と区別する。Production catalogから期待値を作らず同じTest-local固定値を保持する。

PG1853-ORDINAL001～005：LogQueryApplicationServiceTestのf.commits.get()==1三/==2一/==3一に、Test-local FIXTURE_FIRST_COMMIT_ORDINAL=1/SECOND=2/THIRD=3を使用する。序数は既fixture観測順だけを表し、未確認の業務段階名や外部仕様を発明しない。他の数値/条件/処理/独立expectedを変えない。

事前条件は元正常入力/二source hash一致・既job終端。操作は明示二sourceのidentifier/条件五だけ変更、format、逆rename/定数逆展開で全元tokenと同値String連結保持、誤名/誤値/参照欠損/他assert変更のmetadata反例、固定四Testの必要静的で旧39→34と残全属性保持、新固定sourceの六正常compile/package/PT0、独立全Main1843と他Test・当二SourceFile・原owner/cost/traceを検証する。

元34文脈非該当判断は新sourceへ無条件転用せず、原10622/10624へのhash参照と当sourceの逆展開・原実制御/新静的rowの一致で限定継続性を確認する。実行PT/coverageへは転用0。元DB/JMS/故障/key/graph/@BeforeAll/fixtureを選択実行又は別harnessで起動しない。

各class既traceと485のP01001/P01004、UI232/SS311/352の既要求を維持。結果2095/同番号公開manifestへsource/command/OS/JDK25.0.4/Maven3.9.12/static tool version・真正exit/hash/未実施を保存。coverage null、元動的NOT_EXECUTED_HOLD・全F03/451未受入、正式1964-53/個別17-190/工数null/QA051final不変。前置checkはPG-D681の戻値分岐、非0で本体へ進まない。
