# 1564 TimedFilesystemMonitor 実行結果

## 是正後の当source検証

固定source `d96df9f09b46dee9aa75276d474e118609ee890c`。PG7068-timed-filesystem-host-v2真正verify/六format0、同70PT/10suite・F/E/S/rerun/flaky0、SHA `3a375183d403d80c1d5c12fb0201d03bb7486d3a5ba4bc617451510d36770223`。PG7070-timed-filesystem-post-v2 SHA `55456e2cb24d49f35766b3a17179c56a0e133a484592235529eb4eb7f61ac25a`、全元70XML/21source一致、実19class＋metadata1/CRC0/実単一session、L382/M89/C19/B191全miss0。実入口7068/7070・library・helper・全loaded公開Python sourceを別hashで採取し終了時同byte確認、元command不足を推測修復0。

BUG1649の適用対象DuplicateLiteralsは解消し、固定messageのnegative testも当sourceで成功。PMD raw14/exit4を全個別分類：Mode25/26/27のimmutable private primitiveとgetter同名はCONTEXT_NOT_APPLICABLE、Metric13/15/24はSS351 metric別label表のREQUIRED_CONTRACT（独立26golden）、Threshold115はpercentage上限100のREQUIRED_CONTRACT。Window27/AlertLifecycle131・177・186/TimedFilesystem42・73の同期はprivate短い純粋値lock・外部callback/I/O/共有this monitorなし、並行/状態不変/欠測gap/回復境界の当70で確認したCONTEXT_NOT_APPLICABLE。Window32の@Nullable private違反起点resetは1562どおり内部欠落状態のCONTEXT_NOT_APPLICABLE（外部はOptional/NullAway/normal-unknown negative）。未分類0・抑制/除外0、rawを0へ偽装0。SpotBugs/Checkstyle/Production・Test lint/Werror/NullAway0。

PG7072-timed-filesystem-six-compile-v1は同sourceの六Main/Test compile/package0、PT実行0/UNRUN_NOT_PASS_COMPILE_ONLY、SHA `9c45436ca5ab710ae44d3481e7ba6bd7e3a50f34a1cb42e8a79ccdbfd7207fb5`。PG7074-timed-filesystem-six-post-v1は真正0、SHA `0feff9c36b9e44a63d9f0f7351ec830b3b1015e205f20de80a9fa34cb5ae8884`。当1689物理classの旧1669全byte不変、新20＝実19＋metadata1は当70実行対象に全一致、追加24source主所有、ArchUnit五rule0。実入口7072/7074/hash・loaded工具の無変更も確認。全体451/正式への算入0。原4222/common44再演0、元sourcef4の70を新d96へ転用0、同source新runの実測だけを採用する。

## 初回結果の保全

2026-10-23、1563/group1819。最初のsource `f4d8010ba6a9e891edc56859c7773dae126a2032` はPG7064-timed-filesystem-host-v1の通常verify/六format0、70PT/10suite/FES/rerun/flaky0、manifest SHA `9dd5a120dad3207de82164237227d686f37b845c889520ea748a88ea0c0fdd14`。PG7066-timed-filesystem-post-v1 SHA `3aa480ea8cb88e58c078fdd2176a70eb5894602191ac5da7a73cf9d8134eb055`、実19class＋metadata1/単一sessionCRC0、L382/M89/C19/B191全miss0、元XML/21source一致。新ALERTCONT二件/TIMEDFS六件は1563の固定期待値、new8＋必要回帰62の真正実行であり元成功の再演ではない。

この最初のsourceは**PT成功・静的品質未受入**。PMD raw15/exit4のうちAlertLifecycle129 AvoidDuplicateLiteralsは適用対象と判断しBUG1649/YKT1402を修正前起票した。四guardの同一固定診断を単一定数へ統合し、修正後sourceから新70PT/CRC/四counter/静的/実Jarを検証する。元raw15を削除/偽0化せず、元70を新source成功へ転用しない。Checkstyle/SpotBugs/lint/Werror/NullAwayは元0。

BUG1648/YKT1401は共通postのcommand fieldが実wrapperでなくlibrary既定名だった工具不足。元manifest/child command/実XML/exec/sourceは保持する。当初のcommand fieldはlibraryの既定表現であり、当時の実sys.argvを採取済みと解釈しない。新helperは実sys.argv/orig_argv・entrypoint/library/loaded公開Python sourceのhashを別記録し、任意CLI値を保存せず、実行中の工具変更を拒否する。1565の有限管理試験と新runへの適用で再発防止を確認する。元試験をその補完だけのため再実行しない（今回の新70再試験はBUG1649によるProduction変更のため必要）。

公開pathは各 `evidence/provisional/<job名>/manifest.json`、元原物は `work/pgpt-runs/PG379/pg7064-timed-filesystem-host-v1` と `pg7066-timed-filesystem-post-v1`。環境/command/時刻/OS/JDK25.0.4/Maven3.9.12/hashは原記録を参照し、実入口不採取という不足も併記する。実VM/Root/DB等0、HOLD/正式1964-53/原190新受入0/工数null/QA051final/PTALT0は不変更。
