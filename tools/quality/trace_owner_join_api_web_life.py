"""Canonical Web ordinary-close test follows original485 WebLifetime P01806, not change group."""
import trace_owner_join_api_main as previous

TEST='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebLifetimeOrdinaryCloseTest.java'

def canonical(path,logical):
    if path==TEST and path not in logical:
        return dict(canonicalOwner='WBS-P018-06',canonicalCostOwner='WBS-P018-06',
          ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='P01806_RD171_UI252_SS313342_WEB_LIFETIME_ORDINARY_CLOSE_TEST')
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        resolved=canonical(row['path'],logical)
        row.update(owner=resolved['canonicalOwner'],**resolved)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    previous.previous.require(rows==join_rows(original,logical,source_hashes,change_owner),'exact current Web ordinary canonical join')
