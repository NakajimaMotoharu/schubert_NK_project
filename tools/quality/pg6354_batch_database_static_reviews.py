"""35 batch database/cleanup source applicability spans; no actual database or lock operation."""
import inspect
import json
import os
import pg6352_ordinary_boundary_static_reviews as previous

G = previous.G
V = 'AvoidUsingVolatile'
C = 'CloseResource'
SPEC = {
    'CleanupDatabaseSession': {
        (208, G): (2, 'Both Runtime/Error callback/admission failures retain the unknown primary until the consumed credential and single-use connection close. Known SQL/IO/repository failures map to fixed unavailable. closeReplace follows SS332 known/unknown precedence, not the ordinary JMS sender fatal policy; a fixed secondary does not expose raw provider data.'),
        (272, C): (1, 'The acquired statement is protected immediately by try/finally, checked for null and closed exactly once even if timeout/query/row work fails. ResultSet has its own nested owner. The Connection is borrowed by query and remains owned by execute.'),
        (280, G): (2, 'Both unchecked row-body failures are captured before row finally close; JdbcResourceFailures applies the explicit SQL/unknown ranking and fixed secondary before the owned statement closes. No incomplete projection returns as successful cleanup.'),
        (291, G): (2, 'Both unchecked statement/body/row-close failures retain primary until the acquired statement closes once. Known SQL can yield to unknown close; an unknown primary retains identity plus fixed secondary. This source reason does not certify actual DB lock release.')},
    'MorningDatabaseSession': {
        (514, G): (2, 'Both unchecked admitted callback failures retain primary while finally invalidates callback-scoped Session and consumes credential/connection. No live JDBC handle escapes. closeReplace is the declared known/unknown contract; failed close is never true Morning completion or reused backup authority.'),
        (615, C): (1, 'The statement acquired by query is immediately guarded by direct try/finally; null/setup/bind/query/row failures cannot skip its one close. The shared parent connection is never owned by this nested query.'),
        (622, G): (2, 'Both unchecked row callbacks retain primary until direct ResultSet close under JdbcResourceFailures SQL/unknown precedence. Row failure is not a valid scalar, role or receipt projection.'),
        (633, G): (2, 'Both unchecked query/row-close failures retain primary until Statement close and then rethrow. Manual resource scopes preserve SS332 fixed-secret-free secondary precedence; replacing them with generic JMS or SSC304 exactTWR would change the approved contract.'),
        (663, V): (1, 'active is a visibility gate invalidated in execute finally; escaped/late Session calls must reject before JDBC use. Volatile does not make the connection cross-thread safe: guard also binds the original callback thread.'),
        (664, V): (1, 'backupCommitted publishes only the committed begin state; guarded operations require matching immutable backupBegins and original run. Visibility is not a surrogate for durable SQL/readback or native ownership.'),
        (665, V): (1, 'handoffStarted is the one-attempt publication flag for callback-scoped maintenance handoff. Original-thread guard still forbids concurrent use; it is not a retry lease or permission to repeat an unconfirmed operation.'),
        (666, V): (1, 'inHandoff gates parent operations while its advisory lock is intentionally borrowed by a synchronous child. Guarded lifetime/thread checks remain necessary; volatile is visibility, not proof of actual lock acquisition or child termination.'),
        (668, V): (1, 'backupFinished gates post-terminal readback; matching committed handles and same callback are checked independently. A visible flag alone cannot mint genuine Backup or Root completion.'),
        (671, V): (1, 'cleanupVerified gates later parent operations only after the existing seven-step verification returns. The connection and run are not exported; real row/Unit evidence is separate from this source applicability decision.'),
        (672, V): (1, 'expiryHandoffStarted preserves the one-attempt state across guarded entry checks. It is not an atomic multi-step protocol or cross-thread JDBC permission; original-thread/lifetime/run/receipt predicates remain required.')},
    'CleanupTerminalRepository': {
        (311, G): (2, 'Both unchecked retained-original projection/resolve failures retain primary until owned ResultSet close, with guard/run/step/attempt/SUCCESS conditions checked before the value may escape. Provider calls stay outside pure value catches under SSC199.'),
        (323, G): (2, 'Both unchecked result/cleanup failures retain primary across the owned statement finally close under SS332 JdbcResourceFailures ranking. The repository borrows the transaction and never commits/closes/configures the parent Connection.')},
    'ExpiryAuditRepository': {
        (184, G): (1, 'Stage update SQL/RTE maps to fixed BatchRepositoryException; zero-update is successful only after explicit same-handle stage readback. This stage/TWR contract is not read-scope SSC310 or successful-scope SSC304 and is not mechanically rewritten by a cleanup policy review.'),
        (243, G): (1, 'Terminal update SQL/RTE cannot become completed audit; a zero-row update needs exact terminal readback before return. Owned update statement closes before success. Normal/null/count/handle predicates remain unchanged; no actual audit mutation is issued here.')},
    'InspectorLockHandoff': {
        (47, G): (2, 'Both unknown Runtime/Error callbacks are retained while finally attempts mandatory parent lock reacquisition. The exact primary survives known reacquisition failure with a new fixed Failure secondary; no unknown callback is normalized to a successful child result.'),
        (50, 'DoNotThrowExceptionInFinally'): (1, 'Mandatory reacquisition failure must withhold an otherwise computed callback result. With unknown callback the same primary remains; otherwise finally emits fixed Failure. Suppressing this throw would incorrectly report successful handoff without the parent lock.'),
        (75, C): (1, 'Locally owned prepared statement is declared directly in TWR, before null checking/timeout/query. It closes after the nested row on all normal/exception paths; parent Connection is borrowed.'),
        (78, C): (1, 'The query ResultSet is declared directly in nested TWR before present/row checks, closes once before returning a scalar and before statement close. This source fact is not an actual advisory unlock or reacquisition evidence.')},
    'LogCleanupService': {(168, G): (1, 'Precommit SQL/RTE attempts rollback and restores autocommit only after that return; rollback SQL failure becomes fixed DATABASE_FAILURE. When committed=true, a late guard failure is propagated without pretending the durable chunk rolled back. No automatic retry/delete or actual DB cleanup is performed in this review.')},
    'MaintenanceMutationGuard': {
        (53, C): (1, 'Owned timeout prepared statement is bound directly in TWR before nonnull/timeout/parameter operations; its Connection is borrowed. Parent deadline checks precede and follow the transaction-local timeout binding.'),
        (57, C): (1, 'Owned timeout ResultSet is nested TWR before nonnull/one-row/exact-bound-timeout checks and closes before Statement. Failure cannot silently disable timeout or permit mutation past the parent deadline.')}
}
TESTS = {name: ['batch.'+path+'Test'] for name, path in {
    'CleanupDatabaseSession': 'repository.CleanupDatabaseSession',
    'MorningDatabaseSession': 'repository.MorningDatabaseSession',
    'CleanupTerminalRepository': 'repository.CleanupTerminalRepository',
    'ExpiryAuditRepository': 'repository.ExpiryAuditRepository',
    'InspectorLockHandoff': 'cleanup.InspectorLockHandoff',
    'LogCleanupService': 'cleanup.LogCleanupService',
    'MaintenanceMutationGuard': 'cleanup.MaintenanceMutationGuard'}.items()}


def calculate():
    scope = {**vars(previous), 'SPEC': SPEC, 'TESTS': TESTS,
        'INPUT': previous.BASE/'PG6352-ordinary-boundary-static-review-v1/manifest.json',
        'INPUT_SHA': '24fc1a1ac1503d1f2ff19751b9154a0561c15ad0392e40c6f9ac533cba12a9b6'}
    raw = inspect.getsource(previous.calculate)
    for before, after in (('len(decisions) != 21', 'len(decisions) != 35'), ('all21 explicitly', 'all35 explicitly'),
                          ('reviewed=21', 'reviewed=35'), ('296 other unreviewed', '261 other unreviewed')):
        if raw.count(before) != 1:
            raise ValueError('explicit35 current source reader '+before)
        raw = raw.replace(before, after, 1)
    exec(compile(raw, '<35 individually read batch database/cleanup spans>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = previous.BASE/'PG6354-batch-database-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = previous.sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=35, statusCounts=value['statusCounts'], manifestSha256=previous.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
