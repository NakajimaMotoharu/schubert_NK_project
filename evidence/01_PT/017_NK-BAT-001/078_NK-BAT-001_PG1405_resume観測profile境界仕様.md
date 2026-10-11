# NK-BAT-001 PG1405 resume・完了観測・profile境界（実行前仕様）

Program BatchRunRepository.beginMorningResume/verifyFinished、BackupProfile.consume。RD OPS009/DAT009、UI251、SS3318.3/332/341/343、既023/024及びSSC110/116。WBS-P017-02.02/.03/P017-06の限定試験subset。Production769/PG1292不変更、変更は試験のみ、native/VM/原本/全6再回帰は発行しない。

|Test ID|fixture/操作|独立期待値/根拠|
|---|---|---|
|PT-BAT-RUN1405001|隔離PG18.6/DDL V001～028、固定RUN/UTC NOW/step CLEAN_LOG/旧成功なし。ordinary morning-resume→finish→readback|attempt1/non-skipped、SQL RUNNING/0/NULL、finish後SUCCESS/5/3/0/9/NULL/NULL。readback前後の全行は同一。SS331通常削除の再開をBackup専用skipへしない|
|PT-BAT-RUN1405002|固定通常RUNNING handle、skip=true handle又はend=NOW-1s。同親connectionのJDBC probeと全row前後|両入力IllegalArgumentException、probe種類集合empty・取得済statement/row0・全行不変。正常結果をreadbackで作らず、異常入力をDB参照前に拒否|
|PT-BAT-PROFILE1405003|SS343 literal JSON goldenの先頭をbyte0x7f(DEL)へ置換、所有bytearrayでconsume|IllegalArgumentException、全所有byteが0へwipe。許容ASCII0x20..0x7e及びLFから手算出。UTF8負byteの拒否と正の127の拒否を別確認|

実行予定はPG1406のoffline selected Maven/Spotless/NullAway/SpotBugs/JaCoCo・target XML/exit/同classbyte資格。DBは新隔離fixtureだけ（実VMへ接続0）、空き容量のためtmpfs上のprivate new-only temp領域を使う。既target証跡は私有へ保全、既Current/原本Backup/stash/旧失敗は削除しない。

この時点は未実行。失敗/skipped/not-runは合格にしない。期待値は固定SQL後条件・明示byte範囲・前後不変から独立に規定、Productionでexpectedを生成0。結果/実時刻/branch/test-source/Main-source/tool環境/command/coverage/static/関連BUGとhashは079/manifestへ実行後に記録。sourceコード違反を見つけた場合は修正前915/916へ起票。選択counterの改善を四100/全体正式へ読み替えない。
