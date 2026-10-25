"""Exact pure API readiness Test responsibility; unrelated unknown paths remain unknown."""
import trace_owner_join_api_fatal as previous

TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiReadinessPredicateTest.java'

def canonical(path,logical):
    if path==TEST and path not in logical:
        return dict(canonicalOwner='WBS-P018-05',canonicalCostOwner='WBS-P018-05',
          ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='P01805_RD171_UI252_SS342_PURE_API_READINESS_PREDICATE_TEST')
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        resolved=canonical(row['path'],logical)
        row.update(owner=resolved['canonicalOwner'],**resolved)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):
        raise ValueError('exact current readiness canonical join required')
