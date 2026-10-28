"""Two measured missing header branches; original whole eight methods remain unchanged."""
from f03_lgs_boundary_trace import state_after as previous_state

BASE_SOURCE = 'e8e06bedba3311c8335dbb5ba9c4fdffafd86acf'
OLD_NORMAL = ('PG13572-lgs-boundary-two-vectors-v1', '849422e3b3794d6c1d580ffc016c36e1bc83b8864eefd33ab1eae10b3793db7a')
PREFIX = 'lgs-remaining-two-branches'
ORIGINAL_NUMBER = 13592
PREFLIGHT_NUMBER = 13594
NORMAL_NUMBER = 13596
STATIC_NUMBER = 13598
POST_NUMBER = 13600
BASELINE_TEST_PHYSICAL = 1978
EXPECTED_CORRECTIONS = 0
RECORD = 'evidence/01_PT/018_NK-OPS-001/2483_Log検索wire_残二branch結果.md'
PATH = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/LogSearchWireClientTest.java'
PATHS = {PATH: ('0e6b055009637450cbbe12d453725d38375dfc76c8adde4a793ec32576a32707', 0, 'WBS-P016-14')}
BASELINE_REFERENCES = [('PG13573-lgs-boundary-two-vectors-v1', '3107b605c91cdf57d2317fb12254925b9ca9da11c26d225c2365c82c39cb2281')]
VECTOR_IDS = ['WEB273-VALID-FOREIGN-LAYOUT', 'WEB273-PHYSICAL-LENGTH']
