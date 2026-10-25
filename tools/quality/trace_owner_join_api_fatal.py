"""Exact committed-fatal callback Test follows its API lifecycle responsibility, not package guessing."""
import trace_owner_join_api_web_life as previous

TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiCommittedFatalBindingTest.java'

def canonical(path,logical):
    if path==TEST and path not in logical:
        return dict(canonicalOwner='WBS-P018-05',canonicalCostOwner='WBS-P018-05',
          ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='P01805_RD171_UI252_SS321342_COMMITTED_FAILURE_LIFETIME_BINDING_TEST')
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        resolved=canonical(row['path'],logical)
        row.update(owner=resolved['canonicalOwner'],**resolved)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):
        raise ValueError('exact current callback canonical join required')
