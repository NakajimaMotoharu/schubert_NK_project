# G13.07・反射を含む25 sourceの静的責任/実行保留の分離

2026-10-25 14:06 JST、source64446不変更、G13_REFLECTIVE25_SOURCE_ONLY_V1、開始.5/2/5pp/cap10。fresh66残34/reset1793382075（05:03:13UTC）、fresh現在窓残10以下/取得不能で保全。旧累計80/90は停止条件にしない。

対象は元9386v3未確定から、既登録683/protocol10を除いた25 source（既知Mainの担当集合一つ、反射等の実行不確定理由を持つもの）。反射があることをsource担当不在と同一視せず、以下のliteral表と実source目的から主担当だけを確認する。一方、隠れた実行時参照・反射/DB/native実試験資格は未確認のままで、静的CP参照が一つという理由で動作を完了扱いしない。

|source（`.../dev/codex/schubert/nk/`以降）|primary/cost候補|根拠/既Test ID|
|---|---|---|
|api/application/log/LogApplicationFixture|WBS-P006-01|Log Inbox/JDBC境界fixture・PT-ADM-067..073、実DB実行なし|
|api/dispatch/ApiReadinessFailureGraph330Test|WBS-P018-05|SS312342354/READY-GRAPH330001..003|
|api/idempotency/JdbcScenarioSnapshotReplacementTest|WBS-P006-01|SS324333/IDEM-SR01..03、実DB実行なし|
|api/idempotency/SnapshotScratchOwnershipTest|WBS-P006-01|IDEM-SCRATCH001..004/BUG1453|
|api/messaging/inbound/ParentGraph334Test|WBS-P005-03|JMS-FACT334005/SS321354|
|api/messaging/outbound/OutboxFailureOwnershipTest|WBS-P006-02|IDEM-FAIL320001..006/SS324332354|
|api/messaging/outbound/OutboxSecondary330Test|WBS-P006-02|JMS330001..003/SS312324354|
|batch/mq/AcceptorObjectBoundaryTest|WBS-P017-10|OPS-MQ-OBJ001..002/SS321342|
|batch/mq/ArtemisDetailedValuesTest|WBS-P017-10|ISSBROKER001/SSC130|
|batch/platform/ServiceDeadlineArgumentTest|WBS-P018-03|OPS-DATA-511002/SSC137、引数境界|
|api/maintenance/SchemaHistoryAdmissionTest（bootstrap module）|WBS-P019-01|OPS-SCHEMA001..008/SSC095、履歴admission|
|bootstrap/FixedNativeCoverageRemovalDuringShutdownProbe|WBS-P018-08|固定native shutdown fixture、実行/TERMしない|
|bootstrap/SystemdBinderAbiTest|WBS-P018-03|SS354/SSC239/ABI001..002、実manager/library呼出なし|
|web/bootstrap/WebReadinessFailureGraph330Test|WBS-P018-06|WEB-READY-GRAPH330001..003/SS312342354|
|web/logging/JdbcWebSessionStoreTest|WBS-P015-01|WEB024..031/SS314331352、実DB実行なし|
|web/messaging/BrokerGraph334Test|WBS-P005-02|JMS-FACT334006..008/SS321354|
|web/messaging/ReplyCleanup333Test|WBS-P005-02|JMS-CLEAN333005..006|
|web/messaging/ReplyCommittedTerminalAdmissionContractTest|WBS-P005-02|JMS-TERM004/SS322§11|
|web/messaging/ReplyConsumerGraph332Test|WBS-P005-02|JMS-CONS332005..008|
|web/messaging/ReplyFatalIsolationContractTest|WBS-P005-02|JMS-ISO007..008/SS322§11|
|web/messaging/ReplyRollbackSignalContractTest|WBS-P005-02|UNC012..016/SS321352|
|web/messaging/ReplyRollbackUnconfirmedContractTest|WBS-P005-02|UNC004/SS321352|
|web/receipt/ReceiptFailureGraph329Test|WBS-P011-04|WEB-RECEIPT-GRAPH329001..003|
|web/receipt/ReceiptReferenceFaultTest|WBS-P011-04|RCPT005/BUG608、実DB実行なし|
|web/session/SessionRollbackAttachment329Test|WBS-P015-01|WEB-SESSION-ATTACH329001..003|

入力は旧9386v3（3b092052）・固定正常9246（989d9e91）・現register9402（6bc494ba）。当source/normal snapshot/hash、既CP/source metadataとliteral primary/全runtimeUncertaintyを照合。JDK javapのclass/SourceFile/参照symbolだけを独立確認し、値やraw disassemblyは保存しない。target compile/load/初期化/メソッド/JUnit/VM/DB/鍵/native/外部jobは0。原4222等の確認再演なし。

関連Main集合が空であるものへ偽の関連WBSを補填せず、runtimeUncertaintyは全25に保持する。旧683canonical保持、cost一field・primary・関連捏造/保留消去・hash/status/dup/missing・隣接非適用を反証。見込source登録1508→1533/1789/Test543→568/824・残281→256・限定683→708だが、検証後だけ計上する。原941/歴史943/481/484/予算/正式1964-53/17-190/工数null/QA051final/全actualHOLD・全WBS scope guardHOLDを維持。主担当へ費用再配賦0、実費はG13.07一度だけ。

完了後も残multi205/resource等51の独立責任対応・普通PG/PTへ継続し、通常群/commit/PMO返答待ちで停止しない。
