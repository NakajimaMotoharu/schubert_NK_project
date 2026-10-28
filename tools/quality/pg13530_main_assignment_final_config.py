"""Frozen final4 Main assignment sites; no authority or application operation."""
from pg13512_main_assignment_trace import state_after as previous_state

BASE_SOURCE = 'df0c755d82564f2a637206a1bda5c33c7df7006c'
OLD_NORMAL = ('PG13506-main-assignment-seven-v1','821f7dee356d4af38311c7cac5f79254e06f6aa8d4d3cf9bfd70e65be018595b')
PREFIX = 'main-assignment-final-four'
ORIGINAL_NUMBER = 13532
PREFLIGHT_NUMBER = 13534
NORMAL_NUMBER = 13536
STATIC_NUMBER = 13538
POST_NUMBER = 13540
BASELINE_TEST_PHYSICAL = 1978
EXPECTED_CORRECTIONS = 4
RECORD = 'evidence/01_PT/018_NK-OPS-001/2477_Main残代入四件_製造静的結果.md'
MEASUREMENT = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
PATHS = {
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningBackupArtifacts.java':('8bc88f0ee11c4c70316aef8675ef9772cc316a9d808274f8314fc226382d1235',['PMD-02861'],'WBS-P017-03','READ'),
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/MorningPermitPublication.java':('9e56961ce7a0227cc35b2e11f702d660ef185c7d35f5b0bb2cdf3148c0728cdf',['PMD-02880'],'WBS-P018-03','PHASE'),
 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/NativeCoveragePrivateFile.java':('06f1b384d1a82f5163cc7c71f5adb2a39419754682be60fd411760589b33bf47',['PMD-06188'],'WBS-P018-08','SIZE'),
 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/ReleasePayloadVerification.java':('341d360a0b31ece1d72c69f95157e702ea5b3dfc68c1a882f648c0df60135d4a',['PMD-06195'],'WBS-P018-02','LINE'),
}
assert len(PATHS) == sum(len(value[1]) for value in PATHS.values()) == EXPECTED_CORRECTIONS
