"""Seventeen normal fixed request/session source sites, not real retirement or recovery."""
import inspect
import json
import os
import pg6428_backup_normal_static_reviews as prior

S = 'AvoidSynchronizedStatement'
R = 'CloseResource'
SPEC = {
    'BackupWorkerRequestFiles': {
        (53, S): (1, 'A private final monitor serializes the entire new-only prepare sequence, including part identity, publication and parent recheck. Replacing only individual accesses with concurrent containers would not protect this compound protocol. Encoded content is zeroed in finally. This local exclusion is not cross-process M/A admission.'),
        (91, S): (1, 'The same reentrant private monitor keeps read/equality/directory validation and missing-only prepare atomic within this object; nested read/prepare use the same monitor. Missing is the sole swallowed typed condition, with directory equality checked before preparing. Caller same-run proof remains external.'),
        (120, S): (1, 'The compound replacement protocol holds its private monitor across previous read, same-run/strict-newer validation, caller proof, repeat equality, retire and prepare. The proof callback is a required external precondition, not manufactured by synchronization. This static statement does not approve or execute any real replacement.'),
        (145, S): (1, 'Read snapshots and directory/file identity rechecks are serialized with writes on this instance. The temporary maximum-plus-one buffer is wiped in finally; the returned consumed request is independent of that buffer. File and directory ownership remain borrowed from the enclosing scope.'),
        (170, S): (1, 'Retire equality, same-file recheck, unlink and durability sync form one local critical section. The documented full Unit-termination precondition is not inferred from source equality or the monitor. No actual retirement is executed or accepted by this review.')},
    'CleanupWorkerRequestFiles': {
        (262, S): (1, 'Empty-namespace observation and directory equality share a private final monitor with normal request methods. DirectoryStream closes with try-with-resources and unknown entries cause failure, never automatic repair. Cross-process/real startup admission is outside this local rule rationale.'),
        (291, S): (1, 'Exact owned-name enumeration is checked as a whole under the same local monitor, rejecting duplicates, unknown names and missing entries before directory recheck. It does not infer that any actual child is quiescent or authorize retirement.'),
        (328, S): (1, 'New-only content publication, inode and byte verification are one compound monitored protocol. The buffer is wiped on every exit; the monitor does not replace the external owner/role and directory contracts. Actual permit/Unit actions are not part of this source review.'),
        (372, S): (1, 'The private monitor protects read plus before/after file and directory checks from this instance concurrent writes. The maximum-plus-one temporary byte array is cleared in finally; only the exact-sized returned copy escapes. No native filesystem stability claim is added.'),
        (408, S): (1, 'Expected/actual comparison, repeat snapshot, unlink, sync and parent identity form one monitored local operation. Both byte arrays are cleared in finally, including errors. External terminal/owner prerequisites are still required and no real retire is issued.')},
    'MaintenanceRunFiles': {
        (311, S): (1, 'The private scopeLock prevents overlapping six-root callback sessions from this owner. Nested ResourceScope acquisition closes in reverse order; session.invalidate executes in finally before those scopes unwind. A monitor alone does not prove live DB or native resource release.'),
        (668, R): (1, 'The views.get alias borrows the current OwnedTransferDirectory from recursive ResourceScope frames. It must not close that directory early: each acquisition is paired with OwnedTransferDirectory::close in its own frame, and recursive child aliases remain within the callback. This is a scoped-ownership false-positive rationale, not an extra coverage exclusion.'),
        (684, R): (1, 'The selected parent aliases either current or the earlier maintenance view so sibling attempts opens under the correct parent. Both aliases are borrowed; child acquisition alone owns the new resource, and ResourceScope closes it on callback exit. Closing parent here would violate the still-live outer frame.'),
        (1098, S): (1, 'The private session stateLock serializes open-check, begin, operation and final interrupt observation against finish/invalidate. It is a compound lifecycle invariant, not a map-performance question. Checked I/O/crypto failures map to fixed unavailable and unknown failures are not fabricated as success.'),
        (1180, R): (1, 'The roots.get alias is owned by the enclosing execute ResourceScope stack, not by this record decoder. The decoder captures only the borrowed root reference and file snapshot; byte arrays are zeroed in finally. Session lifetime gates prevent use after enclosing scope invalidation.'),
        (1249, S): (1, 'The same stateLock serializes finish with session work; finally sets open=false even if begin or namespace verification fails. finish cannot certify a successful namespace when that verification threw. Actual storage/native conditions remain unproven.'),
        (1260, S): (1, 'Unconditional invalidation shares the private stateLock and clears open before the six owned outer directory scopes close. It supplies local session-lifetime exclusion only, with no foreign resource shutdown, failed-cohort recovery or terminal success implied.')}
}
TESTS = {name: ['batch.file.'+name+'Test'] for name in SPEC}


def calculate():
    scope = {**vars(prior), 'SPEC': SPEC, 'TESTS': TESTS}
    raw = inspect.getsource(prior.calculate)
    for before, after in (
        ('PG6426-api-thread-context-v1', 'PG6428-backup-normal-static-review-v1'),
        ('06001b6f4cfb66e4c1a4cc3f85969dcf1e2f67f78bed9cb31fd538ec3e757a1b', '2da516f19954d662b9cec1d2db70cbc0a1a8c0d7b31f09da22737158102f42bf'),
        ("'len(decisions) != 15'", "'len(decisions) != 17'"),
        ("'all15 individually'", "'all17 individually'"), ("'reviewed=15'", "'reviewed=17'"),
        ("'119 other current'", "'102 other current'")):
        if before not in raw:
            raise ValueError('exact seventeen fixed source sites '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<normal fixed request source review>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = prior.engine.BASE/'PG6430-fixed-request-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = prior.engine.sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=17, statusCounts=value['statusCounts'], manifestSha256=prior.engine.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
