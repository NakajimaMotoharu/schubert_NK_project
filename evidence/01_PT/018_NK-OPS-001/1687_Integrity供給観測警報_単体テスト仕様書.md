# 1687 Integrity供給観測警報 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171/UI252/SS351§7・12/PG-D556/group1905。IntegrityHealthMonitor.observe/snapshot/constructor・Evaluation。供給count/閉Service/メモリ時系列だけ、実file/DB/key/config/probe/修復/退役/Root/VM/配備0。論理keyはINTEGRITY_CONFIGで実owner/source資格ではない。

| Test ID / IntegrityHealthMonitorTest method | fixture/操作・独立期待値 |
|---|---|
| INTEGRITYMON001 / integrityMon001KnownZeroAndMissingDoNotInventOrConflateEvents | 既知0はpresent真/未知は偽、初期/両入力でevent捏造0 |
| INTEGRITYMON002 / integrityMon002OneOrMaximumFailureIsCriticalWithFixedIdentity | 1/MAXともC、固定INTEGRITY_CONFIG/BATCH/count1/first-last0/open |
| INTEGRITYMON003 / integrityMon003NormalEvenConfirmedAndMaximumElapsedCannotAutoClose | C0→正常1/601/86400でcause両値とも同event保持。別ownerのelapsed MAX/nano999999999・Instant.MAXでも自動close0/元count時刻不変 |
| INTEGRITYMON004 / integrityMon004UnknownAndExplicitGapKeepOldEventAndNewViolationHistory | C0→未知1/gap正常2/正常602は同event。異常603でC/count2/first0-last603、旧event count1保持 |
| INTEGRITYMON005 / integrityMon005NullNegativeAndReversedTimeRejectWithoutMutatingEvent | nullService/Optional/context・-1/MIN count・逆行拒否、旧event保持/以後正常でも解除0 |
| INTEGRITYMON006 / integrityMon006EveryClosedServiceUsesItsOwnImmutableLogicalKey | 全6Serviceの個別ownerでC/count1、1日正常でも同eventを保持 |
| INTEGRITYMON007 / integrityMon007ConcurrentCallersKeepExactCountAndIndependentOwner | 64callerの1/MAX・同elapsed0→C/count64/元時刻、別API owner/count1不変 |
| INTEGRITYMON008 / integrityMon008GeneratedEvaluationUsesIndependentBooleanAndIdentityOracles | self/同値/null/他型/全field差/typed bool、hash38161/false38347・非空はJDK identity加算/固定text/nullOptional拒否。生成5methodを当ordinary/class/javapへ結合 |

expectedはSS固定閾値1・自動close禁止/明示時系列/JDK Boolean true1231-false1237と31fold・Object identityから独立作成し、Production閾値/hashを期待生成へ使わない。未知を0正常へ変換せずsnapshot維持/連続性切断、無効値は既Poller作用前に拒否。Serviceは既閉enumであり実観測対象の証明ではなく、collector期限/実異常証拠/調査・権限付き退役は別未受入。

元製造新8＋必要既221→当229PT/30suite・61Java/実56＋metadata1/全1757Main/全100source・88追加physical予定、旧98不変2新。7594host/7596独立/7598正常六compile/7600全Jar/7602trace/7604review、全source/run・環境/日時/OS/tool/branch/command/actual exit/input/XML/output/CRC/四100/static/hashを原manifestと1688へ結合。生成新5＋既99は当直接契約に紐付け四counterへ合成0/除外追加0、旧221/別source/失敗/未実行を合格へ加算0。

見積2/4/8pp上限10/fresh26/74・元窓0/reset1793306748、元-v4-v5/usagecursor不変更。元製造8/追加発見/手戻り/既221再資格/tool費を分離し、共有枠を専有費/N-Tへ換算0。正式1964/53/原190新受入0/工数null/QA051final/PTALT0/whole451-native-CHR/全actualHOLD不変更。
