# Query例外catalog五種 独立単体テスト仕様

PG18030/event3710、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備、HEADbfdd9e3f8d42133302023c72d6c3da60df43f3f7/dev-foundation。主F03/関連原責任P01004・P00903・P01301・P00801・P01001は参照費0。開始見積1/3/6pp cap10固定、start前最後82%使用→直後fresh83%使用/残17%・同reset1793774153、間の1ppは当群専有費と推定しない。

NK-ADM001/FUN008009/AUT003、NK-MED001、質問/通知query、NK-SCN001、各元query programとUI225/235/236・SS332（Scenario§14）/333/ResultCode UI232、PT-ADM005006058059・PT-MED012013・PT-QRY003005・PT-SCN002006007/新PG-D1116。五Main全bodyとResultCode定義を読了、2981/2036等後続索引を確認。元repositoryのDB/Graph/SQLstate分類Testを抽出・改作・代替実行しない。

|Test ID/class・method|入力|独立期待値|
|---|---|---|
|QUERY-CATALOG001/LogQueryException ctor/resultCode|capacity false/true|9000/9001、log query is unavailable/cause null/suppressed0|
|QUERY-CATALOG002/MediaQueryException ctor/resultCode|同|9000/9001、media query is unavailable/cause null/suppressed0|
|QUERY-CATALOG003/ScenarioQueryException ctor/resultCode|同|9000/9001、scenario query is unavailable/cause null/suppressed0|
|QUERY-CATALOG004/UserQueryException ctor/resultCode|同|9000/9001、user query is unavailable/cause null/suppressed0|
|QUERY-CATALOG005/QuestionQueryException ctor/resultCode|既知nonnull TEMPORARY_FAILURE/RESOURCE_LIMIT・null|指定9000/9001を保持・question query is unavailable/cause null/suppressed0、nullはinvariant NPE|

expected code/messageは各programの固定catalog契約と上表に手書きし、Production getterをexpected生成へ使わない。Question型に不存在のboolean容量判定やclosed code集合を無断追加しない。boolean型はfalse/true以外/nullを表せず偽fixture・skippedを作らない。enum unknown文字列はProtocol既試験へ参照する。並行/再送/SQL・資源後条件は当不変catalogの外側責務。

PT_DEFAULT：固定exception値/ResultCode enumだけ、実query/SQL/DB・SQLstate分類/Throwable graph/認可/provider/credential/key/IO/crypto/clock/Root/native/VM/Thread0、JDK内部初期化効果null。ctorと単純getterの全Source一classずつを新五件/一suite一JVM/一execで測定。primitive四種は実branch両側、Questionは自然B0=N/Aを区別。normalJar/現source/snapshot・全closure/CRC/単一session/XML/FES・全counter・公式filter不変更/除外0/union0、未達は未達とする。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg18030_query_catalogs_five_pt.py。normal14216/Spot14224同Mainで再用、Java25.0.4/親180秒。3453とmanifestへ実環境/時刻/command/終了code/branch/HEAD・input/Main/Test/class/exec hash/XML・coverage/独立oracle/BUGを保存。新quality五は普通5786の既methodへ偽装しない。新Source初測定は既Productionの資格補完/新規製造0、正式1964/53/歴史17/190/新受入0/工数null/QA051final/451/全HOLD維持。
