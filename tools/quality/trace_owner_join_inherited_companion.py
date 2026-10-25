"""Two literal fixture/interface responsibilities; never infer from inheritance in general."""
import trace_owner_join_static_companion as previous

PREFIX='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'
DECISIONS={
    PREFIX+'file/MorningCurrentInvalidationTest.java':('MorningCurrentInvalidation','Store','Store','invalidate','WBS-P018-03'),
    PREFIX+'platform/MorningPreviousBrokerTest.java':('MorningPreviousBroker','Query','Fixture','collect','WBS-P017-10')}

def canonical(path,logical):
    if path in DECISIONS and path not in logical:
        owner=DECISIONS[path][4]
        return dict(canonicalOwner=owner,canonicalCostOwner=owner,
          ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',
          basis='EXACT_TWO_LITERAL_NESTED_INTERFACE_SOURCE_RESPONSIBILITY_1906_NOT_RUNTIME_PT')
    return previous.canonical(path,logical)

def join_rows(rows,logical,source_hashes,change_owner):
    result=previous.join_rows(rows,logical,source_hashes,change_owner)
    for row in result:
        decision=canonical(row['path'],logical);row.update(owner=decision['canonicalOwner'],**decision)
    return result

def validate(rows,original,logical,source_hashes,change_owner):
    if rows!=join_rows(original,logical,source_hashes,change_owner):
        raise ValueError('exact reviewed two interface responsibilities required')
