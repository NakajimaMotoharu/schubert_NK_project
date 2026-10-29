# 2721 Log検索表示 元whole16 単体テスト仕様

NK-WEB-001/FUN008/AUT/MON、UI225/235/SS311/313/323/352、PG-D925、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c/dev-foundation、Git0a2af85c85daa4a2da565542d754c5a970d9b8e4。元LogSearchViewModelTest386行8件/Results361行8件、二Main403行、LogSearchForm全body、LogRecord/LogType六値/LogLevel三値/LogId/HttpStatus/Elapsed/既読Page/TopBar/Principal/AuthenticationContext/IdValueを全body確認。実ログ/ファイル/DBを読まず、公開される値は全て手書き合成fixture。

|Test ID|入力と独立期待|
|---|---|
|WEB262～269|固定UTC timestampと固定3 UUID文字列、10optional全1024組、page0/100/101/999999、時刻降順・同時刻ID降順と重複拒否、null/USER拒否/immutable/closedBean-redaction、合成HTML固定text/escape、自己64task8thread/10秒|
|WEB286～293|固定日本語filter/ADMIN TopBar、0/1/100/101/201pageとclamp、独立percent-query literal、応答page/件数/順序不一致拒否、全fieldエラー順と日本語・byte制限、31日超・重複入力/null/USER拒否、closedBean/合成DOM、自己64task10秒|

expectedを同じProduction methodから作成しない。入力fixture count/手書きstring/独立bit表/明示DOM値を照合。fixtureには自己synthetic request/message/correlation IDと偽認証文脈のみ、raw実session/token/credential/原本データなし。LogRecord constructor/enum/helperは純値で通信なし。Main canonical P01614、TestUNKNOWN維持。

PG14612 checkedentryで元whole16/2を一回、二Source全五codephysicalを一exec測定、PG14614でXML/全normalinput/六Jar/static14224/原ownENV/一CRC/八metadata反例/全closure/counterを独立照合。JDK25.0.4/Platform1.13.4/JaCoCo0.8.15、outer180秒。自然branch0/未達は隠さず残す。実template/Browser/HTTP/DB/JMS/VM/Root/graph/cohort/鍵0・Main/Test/fixture変更0。新群.5/3/6pp cap10、event3111予定、primaryP01614。正式/工数null/全F03-451/HOLD維持。結果2722へcommand/time/環境/source/input-output/coverage/hash/関連BUGを保存。
