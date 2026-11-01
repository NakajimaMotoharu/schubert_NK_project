"""Exact independently evidenced Test-owner candidates; no runtime or acceptance inference."""
from types import MappingProxyType
import trace_owner_join as base

MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/UserQueryRequest.java'
ROOT='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/admin/'
RULES=MappingProxyType({
 ROOT+'UserQueryCanonicalCoreTest.java':('bff3bdd906735fc3b2b49d52f7a00ac7f1dad8a2ae515535eee09cb2660b42a1','EXPLICIT_2012_CORE001_004_AND_2014_SAME_BYTE_USER_QUERY_P01001'),
 ROOT+'UserQueryResponseBoundaryTest.java':('72a9ccd0477fd81896d59d24224f14fb9e261ca9ad6a23a1d8e992ae8e93a1a1','EXPLICIT_2008_VAL001_004_AND_2014_SAME_BYTE_USER_QUERY_P01001')})
def canonical(path,logical,current_sha256):
    resolved=base.canonical(path,logical)
    if resolved['ownershipStatus']!='UNKNOWN' or path not in RULES:return resolved
    digest,basis=RULES[path]
    base.require(current_sha256==digest,'same immutable explicitly registered Test bytes required')
    main=logical.get(MAIN)
    base.require(main is not None and main.get('owner')==main.get('costOwner')=='WBS-P010-01','explicit original Main owner and cost required')
    return dict(canonicalOwner='WBS-P010-01',canonicalCostOwner='WBS-P010-01',
        ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis=basis)
