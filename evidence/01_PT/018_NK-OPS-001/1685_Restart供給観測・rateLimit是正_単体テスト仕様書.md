# 1685 Restart供給観測・rateLimit是正 単体テスト仕様書

NK-OPS-001/P01809/C07/RD171/UI252§8/SS351§7/BUG1668-YKT1419/PG-D555/group1903。AlertThresholds.restarts・MonitoringPolicyEngine.restartsへ件数と独立boolean rateLimitedを追加し、RestartHealthMonitor.observe/snapshot/constructor/Evaluationを結線する。実systemd/Unit状態・履歴取得・再起動制御/DB/Root/VM/鍵/配備は呼ばない。Service enumは論理keyであり実owner資格でない。

| Test ID / method | fixture/操作/独立期待値 |
|---|---|
| THRESH011/013/014 / AlertThresholdsTest.threshold011RestartWindowBoundaries等 | count0/1/4/5/MAX・flag=false→N/W/W/C/C、flag=trueの0/4→C。負countはflag両値とも拒否、64caller従来W維持 |
| RESTARTFLAG001 / MonitoringPolicyEngineTest.restartFlag001RateLimitIsIndependentOfCountAndInvalidCountCannotMutateState | count0 false=N/true=C・固定RESTART/API/count1、負count true拒否/旧event不変。MONPIPE既72keyへfalseを明示し既境界維持 |
| RESTARTMON001 / restartMon001KnownNormalUnknownAndPartialFlagsRemainDistinct | 既知0/falseと未知・片側正常の2flagを区別、event捏造0 |
| RESTARTMON002 / restartMon002CountAndRateLimitUseIndependentFixedGoldenMatrix | count0/1/4/5/MAXの固定N/W/W/C/Cとflag=true全C。countのみ異常W/C、flagのみtrueでもC、condition/service/count1/時刻固定 |
| RESTARTMON003 / restartMon003MissingOrPartialNormalCannotBridgeFiveMinuteRecovery | W0/N1→未知180/片側正常181/182→N200/499→500で初close、元count/first-last不変 |
| RESTARTMON004 / restartMon004RateLimitCriticalNeedsTenMinutesAndCauseConfirmation | count0/trueでC0→count1/falseでstickyC1/count2→N2、602未確認open/603確認済close |
| RESTARTMON005 / restartMon005GapNullNegativeAndReversedTimeCannotFakeRecovery | nullService/Optional/context・負/MIN count・逆行拒否、旧event保持。W0/N1→gap300/599open/600close |
| RESTARTMON006 / restartMon006ConcurrentSameOwnerAndDifferentOwnerKeepExactEvents | 64caller count1/両flag・同elapsed0→C/count64/元時刻、別API owner W/count1不変 |
| RESTARTMON007 / restartMon007EveryClosedServicePreservesCountAndIndependentFlagIdentity | 全6Serviceで0false正常→4falseW1→0trueC2、condition/owner/count2/first1-last2を固定期待 |
| RESTARTMON008 / restartMon008GeneratedEvaluationContractsUseIndependentBooleanAndIdentityOracles | self/同値/null/他型/全field差/typed両bool、空hash1221152・非空JDK Event identity加算/固定text/nullOptional拒否、生成6methodを当ordinary/byte/javapへ結合 |

expectedはSSの独立条件/固定件数matrix/明示秒時系列/JDK Boolean1231/1237と31fold・Object identityから作り、Productionの判定やhashを期待生成に使わない。flag不明をfalse正常とせず回復は両側既知のみ。件数はcallerが既に供給した同owner/直近10分の観測、rate-limitは独立した既知状態であり実managerの状態同定/時間窓/collector期限・cause真正性は別未受入。既type/byte理由と新生成6は当普通PTへ結合し、99methodを四counterへ合成0/除外追加0。

元製造monitor新8＋追加是正engine1＋必要既212→当221PT/29suite・59Java/実54＋metadata1/全1755Main/全98source・86追加physical予定、四編集92不変2新を実測して1686へ。7578host/7580独立/7582正常六compile/7584全Jar/7586trace/7588review、環境/日時/OS/tool/branch/source/command/exit/input/XML/output/CRC/coverage/static/BUG/hashを各原manifestへ。旧212/当別source成果の合算/失敗等の合格加算0。

見積3/5/9pp上限10/fresh25/75・元窓0/reset1793306748、元-v4-v5/usagecursor不変更。元製造8・手戻りBUG1668/新是正case1・既212当再資格・tool費を区分。正式1964/53/原190新受入0/工数null/QA051final/PTALT0/whole451-native-CHR/全actualHOLD不変更。
