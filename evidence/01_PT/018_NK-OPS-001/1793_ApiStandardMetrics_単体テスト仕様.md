# API standard metric role内組立 PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351/411451、PG-D611/group2020、WBS-P018-09/C07参照0加算。開始fresh36残64/reset1793382075/1-3-6pp/cap10はPG8588/event2020固定。既ApiJvmMetrics/ApiSystemMetrics/ApiGcMetricRegistrationを一つのApiStandardMetrics.bindへ結線する新Main1/Unit1、旧helper/POM/上位不変更。

内部順序はJVM→CPU-FD→GC。非resource二段を先にし、GCは既owner保持ack後だけactivate、callerが借用registryと同GC handleを所有しpartial failure時も自身でcloseする。公開bindの各lambdaは既roleのhelper/同source/mode/ownerを固定captureし、ユーザー選択factoryではない。STANDARDは三action/owner/JMX/sourceを読まない。DEBUGはnonnull全境界/closedを先に検査しforward fail-fast、元Runtime/Error identityを保持、helper自身の暗黙close/rollback/retry/保持fieldなし。実endpointやshutdown authorityは追加しない。

新APISTD001～013（13/1）、oracleは固定順序/identity/役割値と独立Runtime・固定SDK公開名/type（8493/8540/8565の同jar byte）。001 own fresh JUnit実三段、JVM gauge/CPUcount/FD/fixedAPI/GC handle一個、caller GC_CLOSE→REGISTRY_CLOSEの独立event順。002 STD三portとowner/source全未読、003記録portのJVM-SYSTEM-GC各一回/借用source未close、004 source/mode/owner/三action null、005空/未知/小文字/余分空白で未読、006closedDEBUGは全phase前拒否、007各phase Runtime時は前段だけ/後段0/同primary/borrowed保持、008各Error同様・正常化0、009実GC owner falseでも前段metricとcaller同handleを保持/未activation・暗黙close0、010retain後ownerRuntime/Error同identity・再送0、011closedSTD未読/再close0、012二実default registry/GC ownerを混ぜず各caller GC先close、013有限64並行/三記録port・192calls/join10sec/sleep0。expectedをproductionで生成しない。

GC実candidateはown新JVM内のfreshだけ、GC強制/既handle/外部process/実VM/Root/DB/鍵/Backup/network/service/配備/intent/permit操作0。直接helperの旧14/28/4222確認再演なし、当組立に必要な新13だけを実行。8590正常six/NullAway/format→8592新13一exec→8594当新Main（lambda含む）line-method-class-branch100/CRC0/session1/全raw PMD-CS-SB-missing0/metadata反例→8596全1821/199owner見込/fields0/五edge0・三既helper同byte/標準SDK根拠→1794/scan。旧helperの部分実行counterや旧source成功を新source全体資格へ合算しない。

全command/環境/OS-JDK/branch/source/時刻/exit/input/expected/actual/XML/exec/coverage/static/log/hash/BUG-YKTはmanifest/1794へ。除外追加/別source counter合算0、failed-flaky-skipped-notrun非PASS。着手時13/coverage UNRUN、formal1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/CHR/F03Root11/全actualHOLD・元-v4-v5/欠測保全、通常区切り停止なし。
