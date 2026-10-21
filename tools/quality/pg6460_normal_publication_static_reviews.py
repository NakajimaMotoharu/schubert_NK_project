"""Fifty-six ordinary source reasons; held recovery11 and missing semantic12 stay unresolved."""
import inspect
import json
import os
import pg6394_startup_static_reviews as engine
from pg6450_morning_sequence_qualification import original_source

G, E, T = engine.G, engine.E, engine.T
S = 'AvoidSynchronizedStatement'
A = 'AssignmentInOperand'
SPEC = {
    'BackupStartIntentFiles': {
        (163, G): (2, 'Before a service-intent owner is returned, checked/unchecked assembly failure attempts the locally owned directory close and rethrows. Checked close failure is suppressed, not treated as success; unchecked close can supersede, never authorize start. Normal lease ownership is separately transferred to the returned marker owner; this review grants no real startup authority.'),
        (207, S): (1, 'A private final monitor serializes gate, snapshot and missing-only observation with begin/retire on this instance. An existing or unknown marker fails; it is not automatically repaired. This local monitor does not prove M/A, external process or Unit state.'),
        (224, S): (1, 'The compound new-only create/force/sync/identity/gate sequence shares the private reentrant monitor. begun becomes true only after durable checks; later failure leaves residue and cannot authorize a start. Actual publication or ownership is not demonstrated by source review.'),
        (257, S): (1, 'The package-scoped existing-marker capture serializes begun/token identity and before/after gate checks. Its documented caller failed-generation proof is external and remains held; the monitor itself creates no recovery or retirement authority. No such operation is executed or independently investigated here.'),
        (274, S): (1, 'Same-owner token identity, begun, gate and snapshot checks surround the single unlink under one private monitor. The external whole-Unit/original prerequisite is not inferred from equality or synchronization. This review executes no retirement and does not certify successful persistence after an unknown return.'),
        (290, S): (1, 'Same-object token ownership and marker snapshot/gate observations are one compound synchronized read. It cannot substitute a previous boot or foreign token, nor prove actual ownership merely because local locking succeeded.'),
        (318, S): (1, 'The fixed-marker preservation branch uses the same reentrant monitor and entered-before-MISSING guard so unknown/invalid existing entries are not silently replaced. All actual recovery/quarantine prerequisites stay outside this static warning rationale and held; no real marker is read or changed.'),
        (352, S): (1, 'The locally owned directory close is serialized with marker observations. This is a lifecycle critical section, not a concurrent-map optimization. A thrown close is not converted into terminal success or evidence that a real owner released.')},
    'MorningPermitPublication': {
        (158, A): (1, 'The single phase[0] increment compares each callback ordinal against the literal three-boundary order, after owner check and before expected-state/gate/proof observations. A failed ordinal stops publication; it is not retried or accepted. This local integer progression alone conveys no permit authority.'),
        (205, G): (2, 'Before publication started, any checked/unchecked intent-observation close uncertainty calls the pre-retained nonreturn port. aborted becomes true only after normal close; normal return cannot fabricate successful release after an exception. Actual parent lifetime still needs independent evidence.'),
        (232, G): (2, 'After publication may have started, checked/unchecked failures cannot produce a normal abort receipt: they enter the existing retention port. The source catch is required, but its delegated revoke/quarantine actions and original/current state are not exercised or authorized by this review; safety holds remain unchanged.')},
    'MorningStartupLaunchOwner': {
        (159, E): (1, 'This catch contains only a secondary diagnostic failure after a nonnull primary is already UNKNOWN. It returns to the original completion catch and its retain call, not to successful completion or release. Normal phase/null behavior is explicitly separate; actual parent retention is not proven here.'),
        (159, G): (2, 'The fixed failure classification, clock, string construction and sink are protected for both RuntimeException and Error. Same independent current23 cases exercise the two secondary origins and types; no Throwable message or graph is printed. The raw warnings remain visible and current whole binding is still required.'),
        (302, E): (1, 'A typed Caddy-readiness IOException means not yet ready only within the same remaining parent/caddy floor. The next bounded loop still rechecks peers and budget; failure outside that window stops the owned graph. It is not an ignored success or a new startup retry.'),
        (307, G): (2, 'Readiness/budget/peer uncertainty after Caddy start enters the existing stopOnly path before the original failure may propagate. Unknown termination must retain and cannot authorize ordinary parent unwind. Real Unit stop/quiescence is not established by this local source reason.'),
        (311, G): (2, 'After confirmed stop, a checked/unchecked failure closing the attempt observation goes to retain instead of reporting released resources. It neither retries a consumed close nor retires an actual intent in this review.'),
        (400, G): (2, 'Any uncertain completion/retirement/readback failure calls the now-protected failure diagnostic and immediately the existing retention port. Original23/JVM proves the diagnostic edge only; actual DONE, resource lifetime and native termination remain separate unproven dependencies.'),
        (435, G): (2, 'stopOnly catches all checked/unchecked stop, owner, budget and kernel-observation uncertainty and retains. A zero client exit is insufficient without fresh quiescent observation; no unknown state is normalized into stop success.'),
        (491, G): (2, 'The fixed API/Web sequence retains returned owners before the next launch and reverses only those owners on launch/completion failure. Capacity2 now precedes acquisition and immutable snapshots do not expose the mutable list. The production stop port is the existing nonreturn-on-unknown implementation; arbitrary failing replacement ports are not certified.'),
        (518, G): (2, 'Uncertain stop, whole-child observation, preserved handle, original, DB or parent recheck enters retain instead of continuing the earlier-owner unwind. Existing captured unit/termination references are used and no real stop is issued by this static review.'),
        (634, E): (1, 'Only ConnectException from the fixed same-generation readiness socket is temporarily interpreted as not listening. The same child and parent deadlines, original/DB/earlier readiness checks continue; other I/O is not swallowed, and no ready result is fabricated.'),
        (659, G): (2, 'A failed observation close after the known terminal path cannot set observationClosed or unwind: the existing retention port is invoked. No second successful close, startup or retirement is inferred from uncertainty.'),
        (665, G): (2, 'Without a captured ticket, a potentially delivered child failure retains immediately. With the captured identity, existing stop/whole-terminal verification precedes closing the observation or propagating failure. This source path does not authenticate any currently running child.'),
        (680, G): (2, 'Any secondary stop/termination/original/DB/budget/observation uncertainty is retained before the primary failure may return. Parent scope release is not authorized by catching Error, and no failed-cohort recovery is performed by this check.'),
        (746, T): (1, 'The pinned rule prohibits thread management in J2EE containers. SS311/343 define this batch as a standalone process; the 25ms sleep is a bounded readiness observation interval on its own thread, not creation/control of a managed container task or proof of actual readiness.'),
        (748, T): (1, 'Restoring the current thread interruption after InterruptedException preserves the existing fixed failure contract. The batch is not a J2EE-managed component and this notification operation creates no foreign thread or stop authority.'),
        (757, T): (1, 'Clearing only the current interruption after an existing retention park prevents a hot retry notification. It does not release the holding frame, certify cleanup, extend the parent budget or manipulate a container-managed worker; actual native lifetime remains unproven.')},
    'StartupAdmissionFile': {
        (235, A): (1, 'guard checks primitive capacity before native open; the valid distinct FD is stored into the preallocated slot before increment. No boxing, List grow or callback allocation intervenes. Duplicate/negative descriptors are rejected before adoption, preserving existing ownership rather than fabricating a fresh one.'),
        (247, A): (1, 'After parent membership and bounded-capacity guards, a valid distinct directory descriptor is stored in its fixed primitive slot and count increments once. The assignment is the required nonallocating capture, not an accidental conditional mutation.'),
        (259, A): (1, 'Entry FD capture follows the same prechecked primitive capacity, parent and duplicate constraints. Post-increment records exactly one newly valid descriptor; no heap growth can lose that descriptor between native return and registration.'),
        (280, G): (2, 'close consumes this owner once, then an unchecked primary drains earlier descriptors before rethrowing that same primary with fixed secondary markers. It does not certify kernel release from a consumed cursor and never retries an uncertain descriptor.'),
        (296, G): (2, 'The first unknown drain failure supersedes a previous known storage error only after remaining descriptors have each been attempted. Prior known/unknown exception precedence is explicit; fixed normalization happens after the reverse drain, not before it can strand remaining owners.'),
        (313, G): (2, 'During reverse drain, secondary checked/unchecked close failures are recorded only in preallocated primitive flags so later descriptors are still attempted. Suppression markers are constructed after all attempts; failure flags do not stand in for successful physical closure.')},
    'StartupPermitFiles': {
        (86, S): (1, 'A private final stateLock protects the complete fresh-epoch/current replace and before/after directory checks. This internal transaction is not a concurrent-map use case and local synchronization alone never authenticates boot, original or external owner state.'),
        (115, S): (1, 'INVALID/current/permit bindings, private part write/readback, three issue proofs and current replacement form one reentrant local critical section. Content is zeroed in finally. The caller must still supply every actual prestart proof; no real issue action is performed here.'),
        (164, S): (1, 'The same-attempt INVALID/derived-ISSUED comparison and current replacement are serialized with reads/issue. The code does not accept a foreign/undecodable current or delete retained files. Actual revocation/ownership is outside this source warning check and remains held.'),
        (196, S): (1, 'current read and begin/finish namespace snapshots share the private stateLock with writers. This prevents local interleaving of the compound observation; it does not replace immutable original, directory or cross-process admission checks.'),
        (212, S): (1, 'Issued reads recheck publication intent on both sides of exact permit decoding under the same local monitor. Missing/corrupt/INVALID never grants admission and no state is repaired to make the read succeed.'),
        (248, S): (1, 'Package-only revoked-state correlation is serialized with current state, verifies exact INVALID and binds the retained permit bytes, then clears its temporary buffer. Its trusted M/A prerequisite is not created by synchronization; no actual recovery or reuse is exercised.'),
        (284, S): (1, 'Issuer readback checks current ISSUED and the exact attempted permit under the same monitor. It is a publication barrier, explicitly not Root admission or a substitute for actual external readiness/ownership checks.')}
}
TESTS = {
    'BackupStartIntentFiles': ['batch.file.BackupStartIntentFilesTest'],
    'MorningPermitPublication': ['batch.file.StartupPermitFilesTest'],
    'MorningStartupLaunchOwner': ['batch.file.MorningStartupLaunchOwnerTest', 'batch.file.MorningStartupLaunchOwnerAdmissionTest', 'batch.file.MorningCompletionRetirementTest'],
    'StartupAdmissionFile': ['batch.file.StartupAdmissionFileTest'],
    'StartupPermitFiles': ['batch.file.StartupPermitFilesTest']
}


def calculate():
    pom = 'src/schubert-nk-batch/pom.xml'
    if engine.sha(engine.ROOT/pom) != engine.sha(engine.W/'pg6448-morning-sequence-green-v1/source'/pom):
        raise ValueError('same original standalone batch POM before thread-rule context')
    scope = {**vars(engine), 'SPEC': SPEC, 'TESTS': TESTS, 'original_source': original_source,
        'PLAN': engine.BASE/'PG6458-current4056-static-plan-v1/manifest.json',
        'PLAN_SHA': '57bcf05beb942adae204ed0c21439a999b445ad2869c423c759a671f0912e35d'}
    raw = inspect.getsource(engine.calculate)
    for before, after in (
        ('PG6384-web-fatal-callback-retry-qualification-v1', 'PG6450-morning-sequence-qualification-v1'),
        ('pg6384-web-fatal-callback-retry-qualification-v1', 'pg6450-morning-sequence-qualification-v1'),
        ('7896c2a6d7d650cf2a67f9270e0ad039360c7a5ba073cf84685adddc578295f7', '8eb15b608718eb0f9eac4a92ccd03db4882a5436876d13c66563beedc3daf3c0'),
        ('len(decisions) != 19', 'len(decisions) != 56'), ('all19 individually', 'all56 individually'),
        ('reviewed=19', 'reviewed=56'), ('rawFindings=1355', 'rawFindings=1361'),
        ('161 other current source spans', '11 held recovery source spans'), ('14 prior missing', '12 prior missing'),
        ('current4052 whole', 'current4056 whole'),
        ("for module in ('bootstrap', 'web'):", "for module in ('batch',):")):
        if before not in raw:
            raise ValueError('explicit current1361/fiftysix source binding '+before)
        raw = raw.replace(before, after)
    exec(compile(raw, '<fiftysix ordinary batch source reasons>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = engine.BASE/'PG6460-normal-publication-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = engine.sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=56, statusCounts=value['statusCounts'], manifestSha256=engine.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
