# 1563 TimedFilesystemMonitor 単体テスト仕様書

2026-10-23、PG-D524/P018-09/C07共有費0、着手1/2/5pp・上限10pp、共有9/残91/reset1793306748。RD MON005～013/UI252/SS351§7・10。新通常8＋必要回帰62=70PT/10suiteを予定する。定義とTest IDは下記、実行結果は1564以降。

一つのservice/FILESYSTEM owner内にwarning/criticalのContinuousConditionWindow、AlertThresholds、AlertLifecycleを接続。OptionalDoubleの欠測はsuppliedValuePresent=falseとして明示し、違反期間と回復期間を切断するがopen event/count/lastSeenを変えない。再観測で以前の回復期間を復活させない。consecutive=falseでも回復期間を切断し、新たな正常継続を0から計算する。無効percent/null/負・逆行contextは更新前に拒否する。全体private lock内は純粋値処理だけ、対象collector/実clock/実source/制御は一切取得しない。

AlertLifecycle.interruptContinuity(elapsed)は欠測/gapをNORMALとして渡さず、既eventを保持したまま回復起点だけを空にする新内部接続API。elapsedを更新し、null/負/逆行では無変更。既observe契約/既正常継続の挙動は変更しない。clearanceは既ObservationContextの明示値だけを使用し、欠測を原因撤去の証拠にしない。

|Test ID/method|独立期待値・観点|
|---|---|
|PT-OPS-ALERTCONT001 / alertContinuity001|null/負/逆行の固定拒否とopen count/時刻不変、empty ownerでも切断可 |
|002 / alertContinuity002|Warning5分・critical10分正常の途中でgap、再開後満期間までopen。criticalは再開後も明示cause確認が必須 |
|PT-OPS-TIMEDFS001 / timedFs001|80%の299.999999999秒は無警告、300秒でwarning、event identity/countとNORMAL5分のclose |
|002 / timedFs002|90%の59.999999999秒は無警告、60秒critical、10分正常＋cause確認まで維持 |
|003 / timedFs003|欠測のsuppliedValuePresent=falseとsnapshot不変、再観測でwarning/critical期間を再利用しない |
|004 / timedFs004|正常回復中の欠測・明示gapで回復timerをreset、欠測だけでeventをcloseしない |
|005 / timedFs005|null service/listではなく当APIのpercent/context/Evaluation.event、NaN/±Inf/負/>100、逆行で状態不変。空/境界0/100 |
|006 / timedFs006|自己所有executorの同一時点並行観測で一owner・count整合、immutable snapshotとlocal status literal、有限終端 |

期待値はSS351の80/90・5分/1分・回復5/10分、固定Instant/Duration/literal frameから独立作成。実clock/sleep/任意path/ID/log/DBを使わず、supplied値を実Filesystem正常性へ読み替えない。旧4222/common44の確認再演・異source/exec/coverage合算0。新method/例外/null/全分岐、同source実CRC/単一session/四100/静的、正規Jarへのbyte接続を要求する。工程成功でも全C07/全体451/native/CHR/正式認定は別。
