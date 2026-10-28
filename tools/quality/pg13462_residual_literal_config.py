"""Frozen selected20 current Tests/46 printable constants;70-source baseline pin is immutable."""
from pg13458_residual_literal_plan import PATHS,EXCLUDED
from pg13452_current_printable_trace import state_after

BASE_SOURCE = '99fa8e93a67184377012d90cb41fdbc11a86cfad'
OLD_NORMAL = ('PG13446-current-printable-literal-v1','06c38882aaace8836626a112de79083a89ae2a374db1df6c565c16fbe2f99cb8')
PRIOR_TRACE = ('PG13452-current-printable-literal-v1','0c376e10e5de4b19b790e7a1cb10543f0d9a6498afc03325a49bc650e8f21c66')
CURRENT_BASELINE = ('PG13460-residual-literal-current-baseline-v1','222dd677172d3eea139934bb08d076c289a2e27bfe26730f370b7bdc7806d659')
GLOBAL_BASELINE = ('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
PREVIOUS_STATE = state_after
BASELINE_TEST_PHYSICAL = 1978
PREFIX = 'residual-current-literal'
ORIGINAL_NUMBER = 13464
PREFLIGHT_NUMBER = 13466
NORMAL_NUMBER = 13468
STATIC_NUMBER = 13470
POST_NUMBER = 13472
TRACE_NUMBER = 13474
TRACE_POST_NUMBER = 13475
RECORD = 'evidence/01_PT/018_NK-OPS-001/2468_残literal現在診断・20Test46件_製造静的結果.md'
BEFORE_RAW = 6395
BEFORE_TEST_RAW = 4893
BEFORE_CORRECTIONS = 3046
EXPECTED_CORRECTIONS = sum(n for _,n,_ in PATHS.values())
assert len(PATHS) == 20 and EXPECTED_CORRECTIONS == 46 and EXPECTED_CORRECTIONS+3*len(PATHS) == 106
