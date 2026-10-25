"""Exact API Main fixture responsibility; preserves every earlier canonical mapping."""
import trace_owner_join_api_life as previous

TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessObservationFactoryTest.java'

def canonical(path,logical):
    if path==TEST and path not in logical:
        return dict(canonicalOwner='WBS-P018-05',canonicalCostOwner='WBS-P018-05',
          ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='P01805_RD171_UI252_SS342_MAIN_OBSERVATION_FACTORY_TEST')
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        resolved=canonical(row['path'],logical)
        row.update(owner=resolved['canonicalOwner'],**resolved)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    previous.require(rows==join_rows(original,logical,source_hashes,change_owner),'exact current canonical join')
