"""Frozen four-file mechanical PG scope; no dynamic Test permission is conferred."""
from pg13200_systemd_test_literal_trace import state_after

BASE_SOURCE = '41359340de234b8bea7578d957bcbf4df6ab951f'
OLD_NORMAL = ('PG13194-systemd-test-literal-six-compile-v1','6c6809515a4ae056dad337e44b5ffd8e26b617e0292e88df7082b3ddcddea1b9')
PRIOR_TRACE = ('PG13200-systemd-test-literal-trace-v1','14eeb898ff39831293d062df06e2a081220a001ac5fc929705fdcb88fbbd3ea5')
PATHS = {
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/MaintenanceRunFilesTest.java':('8c9ee992e068ba004c3d7ab0a55ee1d9cf5284db0d1c8eba61da3272fe5f10c1',32,'WBS-P004-03'),
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/DurableRecordFilesTest.java':('45ccd0307b2eb4aee3af4cb86c941e1580d24ad83a695ba5700563b9df303941',33,'WBS-P004-03'),
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/persistence/MediaRepositoryTest.java':('e0cfbab7437fa73102ed430498d9bbf971f8cb33422a33f63a51159911b74a4e',32,'WBS-P009-01'),
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchRunRepositoryTest.java':('4cc95fbacb6faacca786530a8fbc64f6d94f15078623632a8d439693825f8903',22,'WBS-P017-02'),
}
PREFIX = 'resource-db-literal'
ORIGINAL_NUMBER = 13204
PREFLIGHT_NUMBER = 13206
NORMAL_NUMBER = 13208
STATIC_NUMBER = 13210
POST_NUMBER = 13212
TRACE_NUMBER = 13214
TRACE_POST_NUMBER = 13215
RECORD = 'evidence/01_PT/018_NK-OPS-001/2430_資源DB四Test固定literal119件_製造静的確認結果.md'
BEFORE_RAW = 8438
BEFORE_TEST_RAW = 6936
BEFORE_CORRECTIONS = 987
EXPECTED_CORRECTIONS = 119
PREVIOUS_STATE = state_after
