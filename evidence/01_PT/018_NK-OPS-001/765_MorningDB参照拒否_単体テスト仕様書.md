# MorningDB参照拒否（実未実行）

Program NK-BAT-001／MorningDatabaseSession.Session.observeBackup・guard／RD OPS009～017・BAK／UI251／SS341343・451。Main3b7f/PG2126固定、Java25.0.4/実隔離PG18/Flyway028、既成功3635全回帰は新二試験へ流用しない。

PT-MDB2402-001：独立三業務日のRUNNING二行を正規begin、正規fail後にAUTO/READONLY/HELDを別fixture faultとして提示。全case観測はIOException、SQL二行のFAILED/日時/全計数/reasonは不変。faultを解除した普通観測では二行・独立固定FAILED(1,0,1,0)/COMMAND_FAILUREと固定ended、prior空を確認。execute正常close後も独立SQLとclient/advisory0・実接続closeを確認。観測によるbusiness mutation0。期待値はSQL literalとSSでありproduction expected生成0。

PT-MDB2402-002：未完RUNNING観測と正規FAILED後のactive handoff内観測を拒否。前者RUNNING二行不変、後者FAILED二行不変、handoff結果30を保持、close後SQL/client/advisory0を確認。null/同一pairずれは既MDB015、正常FAILED・prior/reuseは既全scope。新two methodsは実PG上で必須実行、notrun/skipped/abortedは非合格。

command=`python3 -B tools/quality/pg2402_morning_observation_selected.py`（所定PYTHONPATH）、新only LAN隔離snapshot・testclasses・coverage・DB。既2300/2301全六MainJAR/exec/fixtureXML/dependency hashを固定し新試験だけjavac -Xlint:all -Werror。同Main九＋九latest nativeは各元manifest/hashの資格に従い18streamだけ合成、旧0fd入力0・早期Inspector terminal0。全MainCRC不一致0が必須、成果は限定PTで正式認定しない。actual結果/XML/hash/四counter/BUGは実終了後追記。群終了のfresh全回帰は統合triggerで別実行。

独立工具literal/full namespace/latest stream/真正PG依存/entry fixture1、format1.36.1/static0。着手群見積り.5/1.5/4週次共有pp（P017-01のSession主担当、VM0／共通全回帰K01別）、実個別費/N/Tnull、原/v3不変更。
