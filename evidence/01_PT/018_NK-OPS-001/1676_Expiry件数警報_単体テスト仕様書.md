# 1676 Expiry件数警報 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171-MON005～013/UI252/SS351§7/PG-D551/group1893（quota訂正1894/実receipt1895）。ExpiryBacklogMonitor.observe/snapshot/constructor・Evaluation constructor/生成5method。供給OptionalLongとメモリ時系列だけ、実queue読取り/selector purge/API起動停止/Root/VM/JMS/DB/鍵/配備0。工具誤転記是正1678と製品PG/PTを区別する。

| Test ID / expiryMon method | 入力・操作・独立期待値 |
|---|---|---|
| EXPIRYMON001 / 001KnownNormalAndUnknownDoNotInventAnEvent | 既知0と未知を別present flagで保持、初期/正常/未知でevent捏造0 |
| EXPIRYMON002 / 002ExactCountBoundariesHaveFixedSeverityAndKey | 999 normal/1000 warning/4999 warning/5000 critical/MAX critical、固定EXPIRY/BROKER/count1/first-last UTC |
| EXPIRYMON003 / 003MissingBreaksWarningRecoveryWithoutErasingOldEvent | warning0→normal1/unknown180→normal200/499→500の全5分後に初close、旧event immutable/count1/first-last0 |
| EXPIRYMON004 / 004CriticalStaysStickyUntilTenNormalMinutesAndCauseConfirmed | critical0→warning1でもcritical/count2、normal2→602原因未確認open→603確認済close、first0/last1 |
| EXPIRYMON005 / 005ExplicitGapRestartsTheFiveMinuteWarningRecovery | warning0/normal1→300 explicit gap、599open/600close |
| EXPIRYMON006 / 006NullNegativeAndReversedTimeCannotChangeAcceptedEvent | null Optional/context・-1/Long.MIN_VALUE・逆行拒否、旧event同一/後正常6→306で復旧 |
| EXPIRYMON007 / 007ConcurrentSameOwnerAndIndependentOwnerHaveExactCounts | 64同owner1000/5000・同elapsed0、最終critical/count64/first-last0、別ownerwarning/count1不変 |
| EXPIRYMON008 / 008GeneratedEvaluationContractsUseIndependentBooleanAndIdentityHashes | self/同値/null/他型/各bool-Optional差・typed accessor両bool、空true hash38161/false38347・Event JDK identity加算/全field固定text・nullOptional拒否 |

expectedは固定SS閾値/明示時系列/JDK Boolean true1231・false1237/Object identityの31foldで独立計算し、production threshold/lifecycle/record hash等で作らない。Eventは既immutableメモリfixtureでObject hash/text非overrideの同byteを確認し、生成5は当class/javap/source/ordinaryへ結合してJaCoCo分子/分母へ加算0。既生成72も当GENB7/WEBLOG8/ASYNCQUEUE8の必要回帰で実行、除外追加0。

未知は正常0にせずevent保持/復旧窓切断、nonconsecutive/逆行/negative/nullとcause要件は既共通を保持。mode-neutral health kernelでDEBUGに限らず利用可能だが、実broker source/owner/集計/時計・原因flag真正性や制御権限は未受入。新8/必要既Batch monitoring192→当200PT27suite/全55Java・実48＋metadata1予定、別source歴史API98/Web27のcounter/PASS合算0。

run7518/独立7520/正常六compile7522/全Jar7524/trace7526/review7528、環境/branch/source/command/time/exit/input/output/XML/four100/static/BUG/hashは原manifestと1677へ結合。原-v4-v5/群2-4-8pp上限10不変更、元窓0/reset1793306748、実費fresh訂正24開始・旧23基準cap33を保守維持/23→24共有未配賦、tool修正費を元製造8へ変換しない。正式1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/native/CHR/actualHOLD不変更。
