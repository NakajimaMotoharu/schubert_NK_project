# API GC register-before-activate PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351/411/451、PG-D607/group2012、WBS-P018-09/C07参照0加算。開始fresh34残66/reset1793382075/2-4-8pp/cap10はPG8522/event2012固定。固定core1.17.1 SHA9ca47dfaの公開bytecodeでconstructorにはlistener登録がなく、bindToでNotificationEmitter.addNotificationListener、closeで同SDK listener解除を行うことを確認する。metadataを別に固定しprivate reflection/GC強制/外部process観測を使わない。

## 製造・所有
ApiGcMetricRegistrationは固定serviceAPIのfresh未bind JvmGcMetricsを作り、保持するowner Predicateのtrue ackを得てからbindToする。STDはfactory/JMX/source/owner未読、DEBUG閉鎖source/null境界を先に拒否。owner false/例外ならbind0、factory/owner/bindの元Runtime/Errorをそのまま伝播。bind失敗時にも同handleは既ownerに保持され、callerが既存resource scope契約に従ってcloseする。helperは暗黙close/registry close/再試行/旧handle検索/保持をしない。自身instance field0。

callerはGC専用namespace/同lifecycle一回・fresh candidateと保持成功ackの契約を満たす（no-op trueや既bind済みcandidateは契約違反）。返却/無応答だけで外部ownerを認定せず、当PG/PTのownerは自分のfresh JVMの明示List.addのみ。実Root/実VM/サービス/旧GC handleを対象にしない。実runtime assembly/停止/GC event stream/readiness/STD運用/standard textは後続未完。

## 新APIGC001～014（14/1）
1. own fresh JVMのdefault SDKを実bind、ownerが正確な一handleを先に保持、標準metric/固定API tag、ownerがregistryより先にclose。GC強制やイベント到達を成功条件にしない。
2. STD source/factory/owner読取0、public default候補生成を遅延。
3. fake portのfactory→OWNER→BIND固定順/一回/同resource/source、closeはcallerだけ。
4. source/mode/owner/factory null拒否。
5. 空/小文字/末尾空白/未知mode拒否、source/factory/owner未読。
6. closed DEBUG拒否/factory-owner0。
7. factory返却null拒否/owner0。
8. factory Runtime/Error同identity/owner-bind0。
9. owner falseでbind-close0。
10. owner Runtime/Errorでbind-close0、元identity。
11. bind Runtime/Error時の同resource保持/primary同identity、callerが正確なhandleをclose、helperの暗黙close0。
12. 同installerで二owner/sourceを混ぜない。
13. 有限64並行・独立source/owner/SDK fake・join10sec/sleep0、各handle caller close一回。
14. ownerがretain後false/例外でもbind0・保持状態を破棄せず、既ownerによる同handle cleanupのみ（helperによる再発行なし）。

fakeは公開JvmGcMetrics subclassのbindTo/close overrideだけ、base constructorの自己JMX metadata read以外にactivationなし。実default一件も新own JVMだけ、private GC internals/既VM/DB/Backup/鍵/permissions/network/service/deploy/Root/intent/permit操作0。caller cleanupの実測を既環境操作へ流用しない。oracleは固定event順/identity/固定role・SDK公開契約/独立callback記録、production methodでexpected生成なし。

normal六/NullAway/format→original14（一exec）→新Main1実line-method-class-branch100/CRC0/session1/PMD-CS-SB-missing0→全physical/source-owner/field0/role/SDK ctor-bind-close公開metadata→1786。全command/環境/OS-JDK/source/branch/時刻/exit/input/expected/actual/XML/exec/counter/static/log/hash/BUG-YKTを新only公開manifestへ。実装済み違反は修正前915/916、fail/skip/unrun非PASS/除外追加0/別source counter合算0。

現在PT/coverage UNRUN。正式1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/CHR/F03Root11/全actualHOLD・元-v4-v5/欠測不変更、通常区切り停止なし。

