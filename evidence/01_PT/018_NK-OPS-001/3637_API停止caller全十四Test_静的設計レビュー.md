# API停止caller全十四Testの静的設計レビュー

対象ApiProcessLifetimeTest全412行/14 @Test、helper event()、nested HookDriver.mainをsourceとして確認した。current Main7aed、BUG2416/YKT2161。主P01805/開始.5/2/5cap6。Mainのstop/stopping/remainingStopNanosは同budgetへ委譲し、原60秒/初回clock前通知/clock故障後expiry/closeのfinished通知を維持する。原305/1872を独立期待の正本として参照する。

1872の旧method-select10方針は歴史であり、今回の実行許可ではない。whole14にはheld TemporaryInfrastructureExceptionを実際に構築するguard拒否、子JVM/OS TERM、Runtime hook登録/除去が含まれるため、compile/execute/部分抽出/新fixtureを行わない。全14の当source動的結果はNOT_RUN/HOLD。静的レビューを実行PASS、PT免除やcoverageへ換算しない。

| 静的点検ID | 元Test参照/actual method | 独立期待と現sourceの対応 |
|---|---|---|
| REV-API-CALLER001 | 1872/LIFEBUDGET001 / lifeBudget001 | clock nullを拒否。unstarted Thread objectと実hook登録を区別する |
| REV-API-CALLER002 | LIFEBUDGET002 / lifeBudget002 | 停止前false/remaining未開始ISE/clock0、closeで初回一読。新getterはbudgetの未claim falseと一致 |
| REV-API-CALLER003 | LIFEBUDGET003 / lifeBudget003 | clock100→109、再stopでrenew0、59,999,999,991ns/総2読。共通claimの一回性を維持 |
| REV-API-CALLER004 | LIFEBUDGET004 / lifeBudget004 | failは停止trueと60秒、stopped healthを再読せず固定IOException。failedは別stateのまま |
| REV-API-CALLER005 | LIFEBUDGET005 / lifeBudget005 | close反復/同owner shutdownで期限renew0、経過29nsで59,999,999,971ns/総2読 |
| REV-API-CALLER006 | LIFEBUDGET006 / lifeBudget006 | clock ISE/NPEは同一objectを最初に伝播、停止true/remaining0/再通知未読。NPEの正常化を期待しない |
| REV-API-CALLER007 | LIFEBUDGET007 / lifeBudget007 | 初回close Error同一/remaining0、close finallyのfinished通知により別thread shutdownが帰還。primitive20だけではcaller finallyを証明しない |
| REV-API-CALLER008 | LIFEBUDGET008 / lifeBudget008 | health=falseがfail/stopへ進み固定IOException、同最初budget/総2読 |
| REV-API-CALLER009 | LIFEBUDGET009 / lifeBudget009 | clock保留中にstopping=true、二stopで一capture、解放後60秒。現claimはclock前AtomicBoolean公開。旧caseはflag公開とbeginの隙間でownerがremainingを読む順を直接試験していない |
| REV-API-CALLER010 | LIFEBUDGET010 / lifeBudget010 | default固定System.nanoTimeの0～60秒。実Unit期限/実停止完了の証明ではない |
| REV-API-CALLER011 | 305/READY006（subcase TERM） / ready006ActualJvmTermWaitsMainOwnerAndNeverSelfExits | child起動行→TERM→kill exit0/child143→whole-owner-returned/EOF/stderr空。Component childであってadmitted ApiProcessMain/Rootではない。今回は未実行 |
| REV-API-CALLER012 | READY004 / ready004BorrowedDelegatesStopGuardAndActualDeliveryPreserved | 元event/metadata同一、停止前delegate呼出3、停止後3guardはTemporary例外で呼出増0、null delegate拒否。metadataの4はdeliveryCountであってdelegate回数ではない |
| REV-API-CALLER013 | READY005 / ready005HealthFailureInterruptedAndNormalStopDistinct | null health拒否、health喪失/interruptは非成功で割込保持、通常stopは正常、自己shutdownは自分を待たずhealthも再読しない |
| REV-API-CALLER014 | READY006（subcase HOOK） / ready006HookWaitsOuterOwnerAndRestoresInterrupt | 別thread hookはouter close前帰還0、後は割込を復元し終了、close反復可。install/removeは実Runtimeであることを隠さない。今回は未実行 |

READY006は元305がhookと実子JVM TERMの両方を含む。元IDを改番せず、TERM/HOOKというsubcaseとfull methodで一意に対応させる。静的点検IDはPT実行件数へ算入しない。

helper event()はQWKREQ01 header・new byte[64]のtransport identity fixture。guardはbodyをdecodeしないので、この元eventからtyped質問業務、認証context、JMS ACK/rollback、DB後条件を証明しない。元の期待をtyped成功へ補正しない。

HookDriverは実Runtime hook、process、TERM、agent dumpを実行するsourceである。future qualificationでは原runnerの非空surefire.test.class.path、parent/childのagent出力・session/CRCと終了順/真正dumpのprofileを先に照合する。primitive20のConsole commandをそのままcaller全体へ流用しない。source中の-javaagent引渡しだけで子の正しい証跡分離が確認済みとは扱わず、現在の20件は子JVMを起動していない。具体runner profileが未照合のため、この点検だけで新たな計測障害を断定しない。

## 追加のcaller再発防止（全件NOT_RUN/HOLD）

| Test ID | 追加する独立期待/関連既case | 未証明範囲 |
|---|---|---|
| PT-OPS-API-STOP-OWNER001 | callerの停止観測後・初回clock未確定時に別ownerがremainingを要求。未開始例外でなく同claimの確定待ち、解放後元60秒。LIFEBUDGET002/009＋primitive APISTOP019を参照 | 実ApiProcessLifetime経由の並行順序、original whole Test/graph |
| PT-OPS-API-STOP-OWNER002 | caller stop/fail/closeの最初clockで同一RTE/NPE/Error、stopping true/expiry0/renew0、closeのfinishedはfinallyで通知。LIFEBUDGET006/007＋APISTOP020 | callerの各通知経路/故障/close後条件。primitiveだけで代用しない |
| PT-OPS-API-STOP-OWNER003 | 原14全体のguard・health・same owner/別owner・hook/TERMと新stateの整合、旧literal/終了順を保持 | whole caller当source/run、実hook/child/guardと後続資源。Root/Unit/native受入はさらに別 |

Source7aedの正常22084/六静的22086、primitive20/22110、caller委譲bytecode22096を参照する。それらはcallerの動的PASSではない。新code/Test/実coverage/sourceproof/leaf増分0、unique390/whole88/正式1964-53/工数null。BUG2416/YKT2161はOPENのまま。
