# Scenario SQL前入力境界・単体仕様

2026-10-26、NK-SCN-001/ScenarioRepositoryとScenarioPreSqlBoundaryTest、原P00801担当費/関連P00901追加0、assessment2044。FUN003/004・AUT001/003/UI223/234§7.1/SS312332354/451。実装Main変更0、新九method/九ID。着手1/3/8 cap10、Media13と共有計22/2run（別13を本九へ重複計上しない）。

|Test ID|method|入力と独立期待|
|---|---|---|
|PT-SCN-PRE001|scnPre001GamesNullBeforeSql|gamesのconnection/actorを単独null、各NPE message connection/actor、JDBC0|
|PT-SCN-PRE002|scnPre002SpeakersNullBeforeSql|Optional.empty gameで同二null＋request単独null/message request、JDBC0|
|PT-SCN-PRE003|scnPre003RoutesNullBeforeSql|NUKITASHI1で同三null契約、JDBC0|
|PT-SCN-PRE004|scnPre004FilesNullBeforeSql|NUKITASHI1/prefix1で同三null契約、JDBC0|
|PT-SCN-PRE005|scnPre005SearchNullBeforeSql|全Optional.empty/Page1/size100で同三null契約、JDBC0|
|PT-SCN-PRE006|scnPre006DetailNullBeforeSql|ScriptFileId7で同三null契約、JDBC0|
|PT-SCN-PRE007|scnPre007Body257BytesBeforeSql|本文ASCII257/X256でFieldEncodingException、JDBC0|
|PT-SCN-PRE008|scnPre008Speaker129BytesBeforeSql|Speaker ASCII129/X128で同例外、JDBC0|
|PT-SCN-PRE009|scnPre009Chapter257BytesBeforeSql|章ASCII257/X256で同例外、JDBC0|

fixtureは公開合成actor ID7/USER/usernameとJDK Connection自己Proxyだけ。DTO構築はassert前、expectedはUI幅/literal/null契約から独立作成しProduction出力を使わない。実DB Connectionを開かず、任意JDBC method呼出しはcount++/AssertionErrorで失敗させる。各caseのuntouchedを検査、独立postでもNoSql handler lambda hit0/保留product probe0/try内専用helper0を要求。rowsのnon-null境界probeは許容しSQL実行と混同しない。

全対象はtry/JDBC前のみ、14entry境界のうちScenario六を担う。SQL/row/catch失敗/表示順/検索結果/transaction/並行/再送/実DB/大容量fileの合格は本九に含めない。Graph9二Main/Root11/実環境/鍵等HOLDは保持。先行static/GJF→固定source/正常六compile0/PT0/NullAway→閉22/2一JUnit→全XML/CRC/一session/完全二Repository source四counter/全Main/旧Test不変/trace、command/env/source/exit/hash/BUGと未実行は006へ保存。四100の不足を隠さず、新九IDを九WBS受入へ変換しない。
