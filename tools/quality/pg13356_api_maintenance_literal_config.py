"""Frozen same-source API maintenance/monitoring Test literal PG, never target execution."""
from pg13352_authority_oracle_trace import state_after
BASE_SOURCE = 'b95a31982a8a6066a9608e56af5fd17d5665576e'
OLD_NORMAL = ('PG13346-authority-oracle-v1','310c52175ecb38fdab18ec14e791e0b240a38295e346322cfedad7b317d25de9')
PRIOR_TRACE = ('PG13352-authority-oracle-v1','47f00d04795ae89630f764cb8b24d5501213ee55782d51bc87f34225a8cf7a0e')
PREVIOUS_STATE = state_after
BASELINE_TEST_PHYSICAL = 1978
PATHS = {
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/ApplicationServiceUnitTest.java':('9a9e8acce5eeca54d895478c7552ab502a3d3ec754bb3c263a35bcc8569df8f6', 2, 'WBS-C02'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/AuthenticationInboxCleanupTest.java':('5dc645106eb8fcd9e3efaacc2a373151b9dfa8429bfe4f94e4d43abd70876101', 3, 'WBS-P004-02'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/AuthenticationInboxInspectorTest.java':('c7f75d3c896b2b66022d156f979e2e4f423ea939bfaf33981a4723ee2a1314b4', 3, 'WBS-P004-04'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/BackupRerunBoundaryTest.java':('9ba550bb6ec5f194b34e1382a0e9057a0673c839374ef224d43f50c713cca622', 4, 'WBS-P004-01'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxCleanupNonAuthenticationTest.java':('b6bc34635c0cd0caef650368a40085bc04a9d733a74733442715012627456e4a', 6, 'WBS-P004-02'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxDeletionBoundaryTest.java':('4a1d2f4e6dd6d9bce629ff706257c41aac51afd914575b585375ef2f6c48865d', 1, 'WBS-P004-04'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxInspectionBoundaryTest.java':('5c469dd85f776429ac1f127e54654885187d601ee50e21755dd1eb64a032e190', 6, 'WBS-P004-04'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxInspectionProgressBoundaryTest.java':('6fc560a595e274036a942ca802539812fd2d8eda25af563710b6ee67d25f27e9', 6, 'WBS-P004-01'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxInspectionProgressTest.java':('4dba4f152708c983f53be05d9b5c7db08b691a4209156bc136758e13c8336ab9', 2, 'WBS-P004-04'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectionParentBoundaryTest.java':('d00f9d430ab51dacd521a27517389533350a8861e12cd4f6ca60b541f0025046', 2, 'WBS-P004-01'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorDeploymentTest.java':('01e580e4793c13141db1332ea6373caa0e80c704449771c6e5aaafe999cc271b', 1, 'WBS-C08'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorEntryBoundaryTest.java':('6cb6c1d6c6b2864308f13d2f89052e98c05db813df62b035d386f8a964303f90', 1, 'WBS-P004-04'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorFailureGraph329Test.java':('f60bc56058d16c42549f210c7015eb9933814c16e19583cabf8cb0e29e10044c', 2, 'WBS-P004-04'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorLaunchConfigurationTest.java':('72cc30593edec18da5dc624a3821af5f3e4562ed5dc5e435c966044d8e2db8cf', 4, 'WBS-P004-04'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorLauncherTest.java':('5b803311962fea2d754e5eb276476d52915729e2069f33ce81bf99174fa11b29', 1, 'WBS-P004-04'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorProcessTest.java':('089dadfd95309305a27ec3592ea87857317ef34590736e4a09a9f8cbc68075b4', 1, 'WBS-P004-04'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/LogCleanupProgressBoundaryTest.java':('2c7b74c79ffd5b0edaaf4bb5268241ebc042156a5c60e72b6eea8aa07062cb60', 5, 'WBS-P004-01'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/OutboxCleanupBoundaryTest.java':('d8fbf2d2e35aef818f34bafb85e8c642f56753e5a123545f268a3f2ee6ac6c12', 4, 'WBS-P004-01'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/QuestionMutationInboxInspectorTest.java':('33dd3ba6fc86a6961e18e5455790d5a52c3115fe474e330a6eeeaafbe7270d29', 15, 'WBS-P004-04'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/QuestionQueryInboxCleanupTest.java':('d5151c5d1b593bd1ba9f46a1bb220c158574542da87b7f7a9104a13384d0dda3', 14, 'WBS-P004-02'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/ResultBoundResponseSnapshotCodecTest.java':('8e24e8ef14d8819f5f7791248e286f5b3078ec932018543dc2e821a5e05af0e6', 3, 'WBS-P006-01'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/RunReferenceBoundaryTest.java':('520a540b89d18f1d4c4d04db461d528f972e16ad9f7e624d73bf16d6478bdb3c', 2, 'WBS-P004-01'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiObservationContextTest.java':('5d591d15a30d8ab7fe86d3efaa4c88f3ba8174d2dd2e455f7dcb275416a63174', 2, 'WBS-P018-09'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxCleanupPublicationTest.java':('a3eab863af20c05c12b86fe3e74634d25cc1e51db74b3b31141a5dabdd4f89d0', 1, 'WBS-P018-09'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationPumpTest.java':('d4c3bb0c0efff2d3de5d958f384f0415f24fa03e37b9a6d7de6bea1644bf3db8', 2, 'WBS-P018-09'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationSourceTest.java':('bd02de816ccc5222c115fc1777a7e8337d7de89bfbf37d14b5af23ea3406a0e0', 1, 'WBS-P018-09'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiReadOnlyObservationAttemptTest.java':('02678b142d6c2213da1b63aab979587a85eef0f9ecf434b866f3b80ce08ec4c3', 10, 'WBS-P018-09'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiServiceMetricBindingTest.java':('3795077f2d03d3ec1be65b2eef55ef070127e082d40e95ffe99fd4b98c927ca7', 1, 'WBS-P018-09'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/AsyncJobCountRepositoryTest.java':('94c96393ca2af461ee1759bd8b779bf3667bdb0e033adb7b99d9f2cbf1be5572', 2, 'WBS-P018-09'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/DbQueryDurationMetricCollectorTest.java':('b5ea54cfcce8c0b7ce8b087ee12a92d99a6e6538f816dc54d847467cc515a43f', 1, 'WBS-P018-09'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OutboxObservationRepositoryTest.java':('cb415789474f63716abeacf9e152ab7da2ccb2ca140cddf508ae1b7a1f47e2fd', 3, 'WBS-P018-09'),
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorkerTest.java':('b768b133219184d0f87b61fdf68c4e1a3b3b2a24b00675b495b6517768ced107', 2, 'WBS-P018-09'),
 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/maintenance/ServiceDatabaseAdmissionTest.java':('9913cfacb9f90e0cbd4aee8f233c2e4af4754c33ca0718fe8a5fa44405330f9a', 2, 'WBS-P019-01'),
}
EXCLUDED = {'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/CleanupSafetyBoundaryTest.java': 'not same measured source', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxMaintenanceBoundaryTest.java': 'not same measured source', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxResponseInspectorTest.java': 'unsupported reflection or inverse-negative shape', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/NonAuthenticationInboxInspectorTest.java': 'not same measured source', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/StepCleanupBoundaryTest.java': 'not same measured source', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiFactoryObservationFixture.java': 'unsupported reflection or inverse-negative shape', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiMetricCatalogTest.java': 'not same measured source', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiScalarMetricExporterTest.java': 'not same measured source', 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/ApiStandardMetricSourceTest.java': 'not same measured source', 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/maintenance/MaintenanceJdbcProbe.java': 'unsupported reflection or inverse-negative shape', 'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/maintenance/SchemaHistoryAdmissionTest.java': 'not same measured source'}
PREFIX = 'api-maintenance-literal'
ORIGINAL_NUMBER = 13358
PREFLIGHT_NUMBER = 13360
NORMAL_NUMBER = 13362
STATIC_NUMBER = 13364
POST_NUMBER = 13366
TRACE_NUMBER = 13368
TRACE_POST_NUMBER = 13369
RECORD = 'evidence/01_PT/018_NK-OPS-001/2451_API保守監視33Test固定literal115件_製造静的確認結果.md'
BEFORE_RAW = 7746
BEFORE_TEST_RAW = 6244
BEFORE_CORRECTIONS = 1695
EXPECTED_CORRECTIONS = sum(n for _,n,_ in PATHS.values())
assert len(PATHS) == 33 and EXPECTED_CORRECTIONS == 115 and EXPECTED_CORRECTIONS+3*len(PATHS) == 214
