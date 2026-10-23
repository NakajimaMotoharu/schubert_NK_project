# 1564 TimedFilesystemMonitor 実行結果

2026-10-23、1563/group1819。最初のsource `f4d8010ba6a9e891edc56859c7773dae126a2032` はPG7064-timed-filesystem-host-v1の通常verify/六format0、70PT/10suite/FES/rerun/flaky0、manifest SHA `9dd5a120dad3207de82164237227d686f37b845c889520ea748a88ea0c0fdd14`。PG7066-timed-filesystem-post-v1 SHA `3aa480ea8cb88e58c078fdd2176a70eb5894602191ac5da7a73cf9d8134eb055`、実19class＋metadata1/単一sessionCRC0、L382/M89/C19/B191全miss0、元XML/21source一致。新ALERTCONT二件/TIMEDFS六件は1563の固定期待値、new8＋必要回帰62の真正実行であり元成功の再演ではない。

この最初のsourceは**PT成功・静的品質未受入**。PMD raw15/exit4のうちAlertLifecycle129 AvoidDuplicateLiteralsは適用対象と判断しBUG1649/YKT1402を修正前起票した。四guardの同一固定診断を単一定数へ統合し、修正後sourceから新70PT/CRC/四counter/静的/実Jarを検証する。元raw15を削除/偽0化せず、元70を新source成功へ転用しない。Checkstyle/SpotBugs/lint/Werror/NullAwayは元0。

BUG1648/YKT1401は共通postのcommand fieldが実wrapperでなくlibrary既定名だった工具不足。元manifest/child command/実XML/exec/sourceは保持する。当初のcommand fieldはlibraryの既定表現であり、当時の実sys.argvを採取済みと解釈しない。新helperは実sys.argv/orig_argv・entrypoint/library/loaded公開Python sourceのhashを別記録し、任意CLI値を保存せず、実行中の工具変更を拒否する。1565の有限管理試験と新runへの適用で再発防止を確認する。元試験をその補完だけのため再実行しない（今回の新70再試験はBUG1649によるProduction変更のため必要）。

公開pathは各 `evidence/provisional/<job名>/manifest.json`、元原物は `work/pgpt-runs/PG379/pg7064-timed-filesystem-host-v1` と `pg7066-timed-filesystem-post-v1`。環境/command/時刻/OS/JDK25.0.4/Maven3.9.12/hashは原記録を参照し、実入口不採取という不足も併記する。実VM/Root/DB等0、HOLD/正式1964-53/原190新受入0/工数null/QA051final/PTALT0は不変更。
