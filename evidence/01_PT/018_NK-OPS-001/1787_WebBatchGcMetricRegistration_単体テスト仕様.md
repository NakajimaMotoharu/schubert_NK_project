# Web/Batch GC owner-before-bind PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351/411451、PG-D608/group2014、WBS-P018-09/C07参照0加算。開始fresh35残65/reset1793382075/2-4-8pp/cap10はPG8544/event2014固定。1785/1786のAPI owner-before-bind契約を役割固有に実装し、API既14を確認再演しない。Main2/Unit2/POM・上位不変更。

WebGcMetricRegistrationは既HttpMetricContract.detailedMetricsEnabled（未知mode診断invalid monitoring mode）、BatchGcMetricRegistrationは既MonitoringModePolicy.parse（CONFIG_INVALID）。fixed service WEB/BATCH、STD factory/JMX/source/owner未読、DEBUGは閉鎖/nonnull境界後にfresh GC候補をborrowed activateOwnedへ渡す。owner保持true→SDK bindのみ、false/throwはactivate0、bind失敗も同handleを既ownerが保持、暗黙close/registry close/retryなし、fields0。caller契約は専用GC namespace/同lifecycle一回/fresh候補/保持成功ackと所有close、no-optrue不可。共通Bootstrapや相互app参照を増やさない。

新WEBGC001～014、BATCHGC001～014（各14/1、計28/2）を各roleの独立literal/記録callback/identityで確認する。001 own fresh JVMのSDK実bind/固定role/owner closeが借用registryより先、002 STD全未読、003 FACTORY→OWNER→BIND→caller CLOSEの順/一回/同handle、004 null source/mode/owner/factory、005空/未知/小文字/余分空白modeで未読、006closedDEBUG拒否/STD未読、007nullfactory返却、008factoryRuntime/Error identity・owner0、009ownerfalse bind0、010owner例外identity/bind0、011bind例外でも既owner同handle保持/暗黙close0、012二独立scopeを混ぜない、013有限64並行/join10秒/各owner一回close、014retain後false/throwでもactivation0・同handlecaller cleanupのみ。expectedはfixed role・event順/identity/各既mode契約とSDK公開bytecodeに基づきproductionで生成しない。

SDKは既core SHA9ca47dfa、constructor/bind/closeの独立metadataは8540原a50ecec9を同jar byte確認で参照し読取の反復を省く。各新JUnitはown fresh候補だけ、強制GC/外部process/実VM/Root/DB/鍵/Backup/network/service/配備/intent/permit/旧handle操作0。fake bindTo/close overrideはactual listener登録せず、real001の新候補だけownerが同JUnitでclose。

8546正常six/NullAway/format→8548 original28（一exec）→8550実新Main2 line-method-class-branch100/CRC0/session1/全raw PMD-CS-SB-missing0/metadata反例→8552全1817/191source owner見込/field0/five edges→1788。全command/環境/OS-JDK/branch/source/時刻/exit/input/expected/actual/XML/exec/coverage/static/log/hash/BUG-YKTはmanifest/1788へ。未実行/失敗/skip非PASS、安易な除外/別source counter合算0。新14の再実行はsource変更に必要な資格のみ。

着手時28/coverage UNRUN、formal1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/CHR/F03Root11/全actualHOLD/元-v4-v5/欠測保全。実assembly/GC stream/実owned停止/standardtext/endpointは別未受入。通常小区切りでは停止せず次safe PG/PTへ。
