"""Preserve original fifteen paths/start estimate; correct scalar total149 with an import-time typed guard."""
import pg13286_web_business_literal_config as old
BASE_SOURCE = old.BASE_SOURCE
OLD_NORMAL = old.OLD_NORMAL
PRIOR_TRACE = old.PRIOR_TRACE
PATHS = old.PATHS
PREVIOUS_STATE = old.PREVIOUS_STATE
BEFORE_RAW = old.BEFORE_RAW
BEFORE_TEST_RAW = old.BEFORE_TEST_RAW
BEFORE_CORRECTIONS = old.BEFORE_CORRECTIONS
PREFIX = 'web-business-literal-v2'
ORIGINAL_NUMBER = 13302
PREFLIGHT_NUMBER = 13304
NORMAL_NUMBER = 13306
STATIC_NUMBER = 13308
POST_NUMBER = 13310
TRACE_NUMBER = 13312
TRACE_POST_NUMBER = 13313
RECORD = 'evidence/01_PT/018_NK-OPS-001/2443_Web業務十五Test固定literal149件_製造静的確認結果.md'

def checked_total(paths,expected):
    assert type(expected) is int and paths and all(type(n) is int and n > 0 for _,n,_ in paths.values())
    total = sum(n for _,n,_ in paths.values());assert total == expected
    return total

EXPECTED_CORRECTIONS = checked_total(PATHS,149)
assert len(PATHS) == 15 and EXPECTED_CORRECTIONS+3*len(PATHS) == 194
