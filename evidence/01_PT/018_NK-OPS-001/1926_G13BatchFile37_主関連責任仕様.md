# G13.07 Batch file37 sourceの主担当・関連担当

2026-10-25 15:30 JST、G13_BATCH_FILE37_SOURCE_V1/source64446不変更。開始.5/3/7pp・cap10、fresh06:29:26UTC使用1/残99/reset1793513544/secondarynull。fresh現在窓残10以下/取得不能等まで継続し、旧累計80/90停止は使わない。

限定source rootは`src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/`。表は複合file/fixtureのprimary責任候補であり、全関連を保持する。共有Mainの元担当を維持し、実ファイル操作/復旧/permit/Root等の権限や成功をmetadataから認定しない。

|source|primary/cost|直接artifact/目的根拠|
|---|---|---|
|file/BackupArtifactFixture.java|WBS-P017-05|BackupArtifactVerifier/ManifestReaderの公開fixture、BAT194..209|
|file/BackupPublicationFixture.java|WBS-P017-04|BackupBundlePublisher writer fixture、ManifestPublisher05/Inspector04関連保持|
|file/BackupRequestReadBoundaryTest.java|WBS-P017-03|BackupWorkerRequestFilesのread境界、SSC113114|
|file/BackupRetentionBoundaryTest.java|WBS-P017-05|BackupArtifactVerifier retention境界、BAK2120|
|file/BackupRetentionRejectionTest.java|WBS-P017-05|同Verifierの拒否・held FD条件、BAK4950|
|file/BackupStartIntentCollisionTest.java|WBS-P017-06|BackupStartIntentFilesのnew-only collision、BFENCE-NIO001|
|file/ExpiryOwnerTest.java|WBS-P017-08|CleanupExpiryExecutionの親remaining借用、EXPARENT002005|
|file/ExpiryResultContractTest.java|WBS-P017-08|同ExpiryExecutionの結果契約、EXP711|
|file/ExternalEntryRejectionTest.java|WBS-P018-03|RootServiceLauncherをrootとした外部entry拒否、他Main08/12関連保持|
|file/MainTerminationPortTest.java|WBS-P017-12|MorningProcessMain終端portをrootとする共有Main群、MAIN-TERM001..008|
|file/MaintenanceRetirementRecordsTest.java|WBS-P004-03|MaintenanceRecords/DurableRecordFilesのliteral oracle、BAT090..097|
|file/MaintenanceRunRetirementTest.java|WBS-P004-03|MaintenanceRunFiles/RunReferenceRepository、BAT098..113|
|file/MorningBackupMetadataTest.java|WBS-P017-03|MorningBackupArtifactsのliteral metadata、BAK2122|
|file/MorningBackupObservedCompletionTest.java|WBS-P017-12|MorningProcessMainのobserved completion、MMAIN009010|
|file/MorningCleanupCompletionTest.java|WBS-P017-07|MorningCleanupExecutionと七terminal、ISSSTEP003|
|file/MorningCompletedMainTest.java|WBS-P017-12|MorningProcessMainのall-scope return後completion、MAIN455001002|
|file/MorningCompletionRetirementTest.java|WBS-P017-12|MorningStartupLaunchOwnerのcompletion退役、COMPLETION790001..004|
|file/MorningGateEvidenceBrokerTest.java|WBS-P018-03|MorningGateEvidenceの固定broker wire、ISSBROKER002|
|file/MorningOriginalCompletionTest.java|WBS-P017-02|MorningNewRunAdmissionの原本completion binding、ORIG455001..003|
|file/MorningStartupLaunchOwnerAdmissionTest.java|WBS-P017-12|MorningStartupLaunchOwnerのuntrusted admission、OPS2776001..002|
|file/ObservationValueRedactionTest.java|WBS-P018-03|RootServiceFacts等のpublic value redaction、OBSDATA001002、broker10関連保持|
|file/PostgresObservationRowsTest.java|WBS-P018-03|MorningGateEvidenceのPG row serialization、PG-ROWS001|
|file/RetainedExpiryAuditTest.java|WBS-P017-08|CleanupExpiryExecutionのretained audit契約、EXPIRY-AUDIT-SSC302001..014、repo11関連保持|
|file/RetentionWireBoundaryTest.java|WBS-P017-05|MorningBackupRetentionの独立wire、RETWIRE001002|
|file/RootElfDigestPortTest.java|WBS-P018-03|RootServiceExecutableAdmissionのdigest port、ROOTELF-SSC306001..008|
|file/RootEntryRejectionTest.java|WBS-P018-03|RootCurrentPermitPreflight/Launcher側entry gate、ROOTGUARD001..003|
|file/RootFailedStartPairRecoveryTest.java|WBS-P017-12|RootFailedStartRecoveryのpair binding、ROOTPAIR001..008|
|file/RootPendingWaitTest.java|WBS-P017-12|RootStartupPendingのsequence/clock/identity、ROOTWAIT-SSC307001..012|
|file/RootRecoveryNativeAuthorityTest.java|WBS-P017-12|RootFailedStartRecoveryのpublic default contract、SSC168179|
|file/RootServiceEnvironmentTest.java|WBS-P018-03|RootServiceLauncher固定environment、ROOTENV001..003|
|file/RootServiceProofTest.java|WBS-P018-03|RootServiceLauncher/StartupProofFrameのliteral binding、ROOTPROOF/ROOTTICKET|
|file/StartupAdmissionViewOwnerTest.java|WBS-P018-03|StartupAdmissionFileのview FD契約、VIEWFD001..008|
|file/StartupLaunchBoundaryTest.java|WBS-P018-03|StartupLaunchRecordのpublic value、CORR-LAUNCH001|
|file/StoppedBackupCompletionTest.java|WBS-P017-12|MorningCompletionEvidenceのSTOPCOMP001..003、cycle/cleanup関連保持|
|file/TransferCleanupFailureTest.java|WBS-P017-09|TransferCleanupのunlink失敗後条件、SSC118|
|file/TransferIoBoundaryTest.java|WBS-P017-09|TransferCleanupのread-only fault入力、SS33312/SSC118|
|file/UnsupportedBackupVerificationTest.java|WBS-P017-03|BackupDatabaseWorkerの未提供verification拒否、SSC092|

元9386v3 graphと9246正常Jar/snapshot/現source hash・SourceFile/CPをJDK javapで独立確認。上literal表を別parserでexpectedとし、元実Main担当/関連集合/不確定理由を保持。全37を原Main集合membershipへ事前照合し、5完全path選択/9catalog/8mapper/37近傍/旧848全canonical・関連・runtime・artifact witness/元logical優先を確認する。曖昧な汎用fixtureとMain CPなしsourceは本群へ拡大しない。

public source/classfileのbyte読取とmetadata工具vectorのみ許可。ターゲットcompile/load/init/JUnit・実FD/native/VM/Root/DB/Backup/鍵/intent/permit/配備/Unit/サービス/遠隔操作なし。拒否PT実行の代替PASSではなく、Refusal対象と同じ操作の再試行もしない。既成功確認再演/Currentbaseline/oracle変更0。

見込Java1673→1710/1789/Test708→745/824/残116→79、限定848→885、独立確認後のみ計上する。file責任の補完と全method/RD/UI/SS/TestID/oracle/終了依存・PGPT工数率/実PT/coverage/正式受入を分離。費用G13.07一回、元941943/481484/予算受入意味・正式1964-53/17-190/工数null/QA051final/全current WBS auditHOLD/全actualHOLD不変。保存後も残source対応と許可済み独立普通PG/PTへ進み、小群/報告/PMO待ちで終了しない。
