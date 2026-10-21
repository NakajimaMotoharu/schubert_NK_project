"""Normal client/control source review only; never invoke native starts/stops or recovery."""
import inspect
import json
import os
import pg6428_backup_normal_static_reviews as prior

G = prior.G
S = 'AvoidSynchronizedStatement'
R = 'CloseResource'
SPEC = {
    'MorningControlScope': {
        (248, G): (2, 'Both unchecked continuation failures request publication abort before propagating; the catch does not manufacture a completion or DB success. Abort can itself fail or retain ownership, so primary identity is not promised in that subcase. This local rule rationale does not certify safe physical release of the graph or M/A.'),
        (260, G): (2, 'After completion captured a graph owner, any outer checked/unchecked failure enters the existing non-returning retention port rather than normal M-close unwind. Without a captured owner, the original failure propagates. This does not claim that M is still held after a failed close or prove actual native lifetime.'),
        (279, G): (2, 'The captured graph observer is checked before failed operation unwinds to publication handling. A failing observer is not ignored or called success; its failure propagates into the enclosing protection. No expired inner capability is reacquired here and no actual stop is executed by source review.'),
        (296, G): (2, 'Publication abort is called only when the owner reference exists, under the enclosing M contract. A retained/failed abort cannot be interpreted as normal successful work. The normal callback return is untouched; real graph retirement and root completion remain distinct unproven dependencies.')},
    'BackupUnitStartClient': {
        (197, R): (1, 'The marker is deliberately transferred into the returned MarkerLease closure, which owns the exact begin token across possible start delivery and parent cycle. Before a lease is returned, the failure path attempts marker close and rethrows; a residue is not silently removed. This ownership rationale neither executes retirement nor proves real terminal conditions.'),
        (205, G): (2, 'Pre-start marker-publication failure attempts local marker close and then rethrows the original checked/unchecked failure, with a checked close failure suppressed. No systemctl request has yet been issued; unchecked close failure is not hidden as success. Existing factory/allocation residual contracts are not discharged by this reason.'),
        (337, G): (2, 'Service-profile marker publication uses the same pre-start failure contract: checked/unchecked begin failure closes only its local observation, preserves checked close diagnostics as suppressed and never returns a valid start attempt. Actual intent authority and unknown native ownership remain external.'),
        (373, G): (2, 'Once the retainedStart port was called, IOException/RuntimeException/Error is opaque possible delivery, yielding an Attempt with no process handle and UNKNOWN. It does not assert no client spawned, report terminal success, retry start or retire the durable marker. Actual caller retention is a separate condition.'),
        (546, S): (1, 'A preallocated private stateLock guards retainedStatus reads; caller-visible Attempt is not used as its own monitor. This local synchronization cannot manufacture a client or Unit termination receipt.'),
        (553, S): (1, 'Private stateLock keeps retained status, stream-attempt flags and marker-retained gate checks in one compound operation. A zero client exit is insufficient without both closure conditions and external same-owner gates. No actual requireRetained action occurs in this review.'),
        (572, S): (1, 'Live-daemon retirement gates and nested retireAfter share the same reentrant private stateLock. After-unlink uncertainty still throws and must be retained by the parent; the monitor is not readiness or retirement proof.'),
        (590, S): (1, 'Close-observation sets retireUncertain before invoking the possibly failing marker close. Under the private monitor, a second thread cannot reinterpret that uncertainty as a fresh retirement opportunity. Durable marker presence and actual owner release remain separate.'),
        (608, S): (1, 'Status, retired/retiring/uncertain flags and repeated gate/context observations form one private critical section. retireUncertain is set before marker action and retiring is cleared in finally even on failure. This ordering cannot itself authorize real retirement.'),
        (628, S): (1, 'Client reaping and stream-attempt cursor changes are serialized by the private preallocated lock. UNKNOWN/null/poison/previous attempt guards prevent issuing another start or repeating an uncertain close. This does not serialize foreign processes or prove worker quiescence.'),
        (646, R): (1, 'The obtained stdout alias is explicitly handed to closeBoth, or closeOne if obtaining stderr throws. Those helpers each make one close attempt and report a boolean. There is no successful stream-closure assertion if either attempt fails.'),
        (647, R): (1, 'stderr is assigned only from the retained process and then passed to closeBoth; stdout is already protected by a separate acquisition-failure cleanup. A failed close keeps Status.UNKNOWN. The streamsClosed flag means the pair was attempted, not proof that physical descriptors closed.'),
        (650, G): (2, 'Failure obtaining stderr first makes the single stdout close attempt, then rethrows to the outer opaque UNKNOWN/poison boundary. It does not continue to exitValue or grant retirement. Both checked and unchecked descriptor uncertainty remain non-success.'),
        (664, G): (2, 'Any I/O or unchecked context/descriptor/client failure poisons the retained attempt and returns UNKNOWN, without raw exception graph exposure, destruction or a second start. InterruptedException separately restores interruption. Caller must retain unknown owners.'),
        (680, G): (2, 'A stream close exception/Error maps only to false, never to a closed receipt. closeBoth attempts both streams even if the first fails; awaitClient leaves retainedStatus UNKNOWN. The false result is not actual descriptor-release evidence.')},
    'MaintenanceUnitStopClient': {
        (129, G): (2, 'After invoking the fixed stop start-port, checked/unchecked failure is possible delivery. The returned no-handle Attempt remains UNKNOWN and carries no source exception or command detail. No destroy, second stop, next-Unit permission or normal owner-unwind proof is produced.'),
        (170, S): (1, 'retainedStatus is read under the preallocated private stateLock, not a caller-visible monitor. Status does not equate client exit to whole-Unit termination.'),
        (177, S): (1, 'The entire bounded client observation, attempt-once descriptor flags and poisoned guard share the private monitor. Concurrent calls cannot repeat an uncertain descriptor close or turn a missing handle into reaping proof. Unit-state validation remains external.'),
        (189, R): (1, 'The stdout alias transfers to explicit closeBoth or closeOne if stderr acquisition fails. The helper result must be true before the code inspects client exit. It is not an unowned leaked local or an early try-with-resources close of another owner.'),
        (190, R): (1, 'stderr is explicitly passed to the two-stream close helper after successful acquisition. Both streams receive one attempt; streamsClosed prevents retry even when physical closure is unknown, while retainedStatus remains UNKNOWN on false.'),
        (193, G): (2, 'Unchecked stderr acquisition failure attempts stdout closure once then propagates into the outer poison/UNKNOWN handler. No successful client result, worker terminal receipt or subsequent stop is inferred from cleanup failure.'),
        (207, G): (2, 'I/O/unchecked observation failures poison the attempt and return opaque UNKNOWN. Null handle, interruption, timeout and failed stream closure are distinct non-success paths; interruption is restored in its dedicated handler. Nothing destroys a potentially still-owned process.'),
        (223, G): (2, 'closeOne contains checked/unchecked stream failures only as boolean false. closeBoth evaluates the second close even after a first false, but no false path can set a successful retainedStatus. Actual physical resource release and graph teardown remain unproven.')}
}
TESTS = {
    'MorningControlScope': ['batch.file.MorningControlScopeTest'],
    'BackupUnitStartClient': ['batch.platform.BackupUnitStartClientTest'],
    'MaintenanceUnitStopClient': ['batch.platform.MaintenanceUnitStopClientTest']
}


def calculate():
    scope = {**vars(prior), 'SPEC': SPEC, 'TESTS': TESTS}
    raw = inspect.getsource(prior.calculate)
    for before, after in (
        ('PG6426-api-thread-context-v1', 'PG6424-current4054-static-join-v1'),
        ('06001b6f4cfb66e4c1a4cc3f85969dcf1e2f67f78bed9cb31fd538ec3e757a1b', '1b291f7ae41b150e8e6cddb8ca78effbe1fff0d4345a3ad6ee79224b9659da2c'),
        ("'len(decisions) != 15'", "'len(decisions) != 41'"),
        ("'all15 individually'", "'all41 individually'"), ("'reviewed=15'", "'reviewed=41'"),
        ("'119 other current'", "'61 other current'")):
        if before not in raw:
            raise ValueError('exact41 ordinary source sites '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<ordinary client control source only>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = prior.engine.BASE/'PG6432-control-client-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = prior.engine.sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=41, statusCounts=value['statusCounts'], manifestSha256=prior.engine.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
