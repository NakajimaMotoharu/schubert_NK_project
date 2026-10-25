"""Four exact main-path ownership decisions; no package wildcard or historical reallocation."""
import trace_owner_join_api_readiness as previous

PREFIX='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/'
TRANSPORT='src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/'
DECISIONS={
    PREFIX+'LinuxSystemdSession.java':('WBS-P018-03','P01803_SSC239_295_EXISTING_SYSTEM_MANAGER_TRANSPORT_RELOCATION'),
    PREFIX+'SystemManagerObservation.java':('WBS-P018-03','P01803_SSC239_295_EXISTING_SYSTEM_MANAGER_OBSERVATION_RELOCATION'),
    TRANSPORT+'FailedJmsIsolationException.java':('WBS-P005-03','P00503_MQ008010_UI231_SS321322352_CONSUMER_FAILED_ISOLATION'),
    TRANSPORT+'UnconfirmedJmsRollbackException.java':('WBS-P005-03','P00503_MQ008010_UI231_SS321352_CONSUMER_UNCONFIRMED_ROLLBACK')}

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        owner,basis=DECISIONS[path]
        return dict(canonicalOwner=owner,canonicalCostOwner=owner,
          ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis=basis)
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:row.update(owner=canonical(row['path'],logical)['canonicalOwner'],**canonical(row['path'],logical))
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):
        raise ValueError('explicit exact four-main canonical mapping required')
