# 1683 Backup供給観測警報 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171-MON005～013/UI252/SS341351§7/PG-D554/group1901。BackupHealthMonitor.observe/snapshot/constructor・Completion/Evaluationの普通単体試験。供給観測とメモリ時系列だけ、実Backup/status探索/DB/鍵/Root/VM/配備/保持原本/退役0。BATCHは本kernelの固定論理keyであり、実観測owner/source資格を認定しない。

| Test ID / BackupHealthMonitorTest method | fixture/操作/独立期待値 |
|---|---|
| BACKUPMON001 / backupMon001KnownNormalMissingAndPartialStayDistinctWithoutInventedEvents | scheduled=false/success=false/failures0は正常、欠測/片側正常はflagを分けevent捏造0 |
| BACKUPMON002 / backupMon002FixedSeverityAndPartialAbnormalEvidenceAreIndependent | scheduledとtodaySuccessの4組×failures0/1/2/MAX。予定run後当日successなしはW、2連続失敗はC、他N。固定BACKUP/BATCH/count1/元UTC。completionのみ異常W、failuresのみ2でもCを検出、未知正常復旧0 |
| BACKUPMON003 / backupMon003PartialOrMissingCannotBridgeWarningRecovery | W0→N1→欠測180/片側181/182→N200/499→500で初close、元event不変/count1/first-last0 |
| BACKUPMON004 / backupMon004CriticalNeedsTenMinutesAndConfirmedCauseDespiteLowerWarning | C0→W1でもstickyC/count2→N2、602原因未確認open/603確認済close、first0/last1 |
| BACKUPMON005 / backupMon005GapInvalidAndNullObservationsCannotFakeRecovery | Optional/context null・負/MIN failure・逆行は旧event保持して拒否。W0/N1→300 explicit gap/599open/600close |
| BACKUPMON006 / backupMon006ConcurrentSameOwnerKeepsExactCountAndOtherOwnerIndependent | 64caller W/C同elapsed0、最終C/count64/first-last0、別ownerW/count1の同event不変 |
| BACKUPMON007 / backupMon007CompletionGeneratedContractUsesIndependentBooleanHashAndText | self/同値/null/他型/全component一差/typed両bool、hash31×1231+1237=39398・falsefalse39584、固定text、生成5methodを当byteへ結合 |
| BACKUPMON008 / backupMon008EvaluationGeneratedContractUsesIndependentIdentityAndBooleanOracles | self/同値/null/他型/両bool・Optional差/accessor、空hash1221152/非空はJDK Event identityの加算・固定text/nullOptional拒否、生成6methodを当byteへ結合 |

Completionはcallerの同日・同scheduled-runを表す一観測で、05:00の経過やtoday/failure履歴を本kernelが計算・推測しない。statusと連続失敗数は別Optional、既知異常は片側だけでも検出するが正常復旧は両側既知のみ。未知を正常0へ置換せず正常windowを切断する。原因flag/UTC/monotonicの真正性・外側collector期限/権限/実Backup結果は別未受入。

expectedはSSの4組×固定回数・明示時系列・JDK Boolean hash/31fold/Object identityから独立に作り、Production閾値/record hashを期待生成へ使わない。generated11はJaCoCo分子/分母へ合成0、既生成82も当普通回帰の直接契約と同byteへ結合、除外追加/条件緩和0。

元製造新8＋必要既204→当212普通PT/28suite・57Java/実52＋metadata1/全1753Main/全96source・84追加physical予定（実数は1684）。7562host/7564独立/7566正常六compile/7568全Jar/7570trace/7572review、環境/日時/OS/tool/source/branch/command/exit/input/XML/output/CRC/四100/static/hash/関連BUGは原manifestと1684へ。失敗/未実行/別sourceを合格へ加算0。

開始見積2/4/8pp上限10・fresh25/75・元窓0/reset1793306748、元-v4-v5/usagecursor不変更。正式1964/53/原190新受入0/工数null/QA051final/PTALT0/whole451-native-CHR/全actualHOLD不変更。既protected alertの実手動退役経路は別未受入。
