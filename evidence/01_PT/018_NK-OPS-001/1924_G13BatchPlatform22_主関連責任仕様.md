# G13.07 Batch platform22 sourceの主担当・関連担当

2026-10-25 15:28 JST、G13_BATCH_PLATFORM22_SOURCE_V1/source64446不変更。開始.5/2/6pp・cap10、fresh06:26:14UTC使用1/残99/reset1793513544・secondarynull。現在窓残10以下/取得不能で保全、旧累計80/90条件は適用しない。

source rootは`src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/`。以下はファイル責任候補のみで、実Unitやnativeの検証ではない。原Main担当を名称から変更せず、InspectorUnitProbe/SnapshotはP00404、共有BackupUnitStartClient/MorningBackupUnitCycleはP01706、RootStartupContext/MorningGateEvidenceはP01803、実MorningServiceReadinessはP01807、FixedUnitCgroupNamespace/ApplicationUnitはP01804を維持する。

|source|primary/cost|直接artifact/目的根拠|
|---|---|---|
|platform/ArtemisUnitSnapshotTest.java|WBS-P004-04|InspectorUnitProbe/Snapshot、BROKERLIVE001..004|
|platform/BrokerJournalQueryTest.java|WBS-P004-04|InspectorUnitProbeのprocess IO、BROKERQUERY001..003|
|platform/CaddyAdmissionFenceTest.java|WBS-P017-06|BackupUnitStartClientのCADDY MarkerLease/順序、CADDYFENCE001..003|
|platform/CgroupPrimitiveOwnerTest.java|WBS-P018-04|FixedUnitCgroupNamespaceのFD借用、CGROUPFD001..008|
|platform/CleanupUnitCycleTest.java|WBS-P017-06|MorningBackupUnitCycle/cleanup Unit境界、CCYCLE001..003|
|platform/EnumValueCatalogCompatibilityTest.java|WBS-P018-04|ApplicationUnitをrootとしたliteral catalog、他Unit/Root関連保持|
|platform/ExpiryReceiptFixture.java|WBS-P017-06|BackupUnitReceiptGate/StartClientのsynthetic gate fixture|
|platform/ExpiryRequestBoundaryTest.java|WBS-P017-07|CleanupWorkerRequestの不変値、CORR-EREQ001..002|
|platform/ExpiryWorkerRequestTest.java|WBS-P017-07|CleanupWorkerRequestの固定byte oracle、EREQ001..004|
|platform/FailedProfileBoundaryTest.java|WBS-P017-06|CleanupFailedBackupRequest/BackupFailureSnapshot、CORR-CFREQ|
|platform/InspectorHeldStateContractTest.java|WBS-P004-04|InspectorUnitSnapshotのliteral状態、SNAPSHOT911001..009|
|platform/InspectorUnitCycleTest.java|WBS-P017-06|MorningBackupUnitCycleのUNKNOWN/reap/receipt order、IUC3246001|
|platform/InspectorUnitProbeFixture.java|WBS-P004-04|InspectorUnitProbeのpublic synthetic child/reader ports|
|platform/MorningNoPriorBrokerTest.java|WBS-P017-10|MorningBrokerUnitCycleのprior absence/fresh journal、ISSCOLD001..006|
|platform/MorningServiceReadinessNativeTest.java|WBS-P018-07|MorningServiceReadinessのcomponent、READY428010..012。実proc/socket/HTTPは実行しない|
|platform/MorningStopEvidenceTest.java|WBS-P018-03|MorningGateEvidence.stopのSS literal golden、ISSSTOP005..007|
|platform/RootGenerationCounterexampleTest.java|WBS-P018-03|RootStartupContextの世代literal、ROOTGEN1741|
|platform/RootGenerationTruthTableTest.java|WBS-P018-03|RootStartupContextの消失truth table、ROOT2118|
|platform/ServiceIntentReadyRetirementTest.java|WBS-P017-06|BackupUnitStartClient.MarkerLeaseのreadinessとretire境界、SSC178|
|platform/StoppedBackupFixture.java|WBS-P017-06|MorningBackupUnitCycle/ReceiptGateの固定manager/kernel fixture|
|platform/UnsupportedRootIdentityTest.java|WBS-P018-03|RootStartupContextの欠落identity port、SSC164|
|platform/UnsupportedServiceMarkerTest.java|WBS-P017-06|BackupUnitStartClientの未提供marker proof、SSC178186|

原9386v3 graph・9246正常Jar/snapshot・現source hashとSourceFile/CPをJDK javapで別照合。上literalを別parserでexpectedとして読む。5完全path選択/9catalog/8mapper/22近傍・旧826全canonical/関連/runtime/artifact witness/元logical優先を維持し、利用先やnamespaceでprimaryを捏造しない。19前群BUG1751を踏まえ全22primaryの元Main集合membershipをproducer前に確認する。

着手許可はpublic source/classfileのbyte読取と工具metadata vectorのみ。target class compile/load/init/JUnit/実proc/socket/HTTP/DB/Unit/VM/Root/cohort/native/Backup/鍵/intent/permit/配備/遠隔接続0。Nativeという名称だけで拒否PT認定はしないが、今回対象試験を実行しない。実操作HOLD/拒否未特定HOLDを解除せず、静的照合をその実証へ転用しない。旧成功確認再演0。

見込Java1651→1673/1789/Test686→708/824/未対応138→116、限定826→848、独立検証後だけ計上する。source責任を全method/RD/UI/SS/oracle/TestID/終了依存やPGPT工数率/実PT/coverage/正式受入へ変換しない。費用G13.07一回、元941943/481484/予算受入意味・正式1964-53/既17-190/工数null/QA051final/全current WBS scopeHOLD/全actualHOLD維持。限定成果保存後も独立PG/PTへ自走し通常小群/PMO待ち停止しない。
