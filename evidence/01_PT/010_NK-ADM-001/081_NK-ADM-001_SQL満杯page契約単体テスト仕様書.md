# User50件/Log100件・SQL満杯page契約

2026-10-26、P013_QUERY_VALID_PAGE_STATE_BATCH_V1、主P01301/関連P01001-P01809-P01401-P01004追加費0、開始1/3/8pp cap10、used27残73/reset1793513544。077/079の追加仕様、UserQuerySqlContractTest.sql009FullPagePreservesAllFiftyRowsAndRequestedPage（PT-ADM-SQL009）、LogSqlContractTest.sql009FullHundredRowPageKeepsDescendingIds（PT-LOG-SQL009）。FUN008009/AUT002003/MON、UI225/235§11/236§4/SS323/332§3・411/451。

Userはtotal50/pages1/effective1・id1～50/username同順の独立valid tuple、要求page999999→独立期待Paged1,50,50,1,1,50/records50/順序id1～50・元page999999保持・bind now+page。Logはtotal100/pages1/effective1・id100～1の独立valid tuple、Paged1,100,100,1,1,100/records100/入力順を維持したtyped mapping。SQL自身のstable ORDER BY/limitは077/079と同時assert、実DB sortの実証にはしない。expectedはTest内の整数列/固定typed recordでProduction mapper等不使用。

自己public JDBC fixtureは既077/079のもの、valid正常rowだけでSQL fault・Graph9・実DB・backend・private反射・JCE・Root等なし。借用Connection三callのみ、RS→PS一回解放。境界50/100の複数rowループとresponse件数/first/last/limit、既single/emptyと関連回帰する。

QRY005の新PT-QRY-SQL009010二件とまとめ、既48＋新4=52method/7suiteを同sourceの一build/一JUnit/一exec/一sessionで検証する。新52IDではない。完全六source unit＋内包no-Code interfaceの七physical Main/CRC/四counter、禁止product probe0、Main非影響/当Test静的/traceを独立照合。原別source三Requestの100を合成しない。当source/run/実command/環境/coverage/hash/障害/結果は082/shared018manifestへ記録。全451・実DB/native/CHR/QA051・正式1964/53・17/190/工数null/全HOLD不変。
