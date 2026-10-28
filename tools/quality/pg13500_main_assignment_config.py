"""Frozen4 Main/7 assignments; source-only evaluation order, no native/target invocation."""
from pg13492_positioned_literal_trace import state_after as previous_state

BASE_SOURCE = 'ff8149dd27decbe683b48d1cbb5f2cb59ecca83a'
OLD_NORMAL = ('PG13486-positioned-current-literal-v1','7c2d971b10807387a897132984dc14472936ce6e65e4a75e8ba519f4644fff65')
PREFIX = 'main-assignment-seven'
ORIGINAL_NUMBER = 13502
PREFLIGHT_NUMBER = 13504
NORMAL_NUMBER = 13506
STATIC_NUMBER = 13508
POST_NUMBER = 13510
BASELINE_TEST_PHYSICAL = 1978
EXPECTED_CORRECTIONS = 7
RECORD = 'evidence/01_PT/018_NK-OPS-001/2473_Main代入七件_製造静的結果.md'
MEASUREMENT = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
PATHS = {
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/StartupAdmissionFile.java': ('39640390a7cbee7bc4ae5770a2dd68bc3a246c049d387ac709b8fb99c140dc1b',['PMD-02934','PMD-02935','PMD-02936'],'WBS-P018-03','INDEX'),
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/FixedUnitCgroupNamespace.java': ('5c104d015bc23112d7d155ac030850ea6f4cad9ef0c24a7c7d989bbf2ba5212d',['PMD-03077','PMD-03078'],'WBS-P018-04','INDEX'),
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MorningCaddyReadiness.java': ('7252e8f22ffe9a00e2528cc6ad33c853fa7f103d92027fb6f1bb94ca10783316',['PMD-03132'],'WBS-P018-07','LIMIT'),
 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MorningServiceReadiness.java': ('534b4750d8fcb7a017f65a3d99cc895d5cc3f69791078f9223c2afaaa5a73153',['PMD-03140'],'WBS-P018-07','LIMIT'),
}
assert len(PATHS) == 4 and sum(len(value[1]) for value in PATHS.values()) == EXPECTED_CORRECTIONS
