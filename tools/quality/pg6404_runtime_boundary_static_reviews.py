"""25 source-only boundary spans; no ADMIN/Unit/native/Web operation or replay."""
import inspect
import json
import os
import pg6394_startup_static_reviews as engine

G = engine.G
SPEC = {
    'BootstrapAdminMain': {
        (89, G): (1, 'The final process-entry closing/capture boundary consumes any Throwable only into the specified fixed bootstrap status50 and literal diagnostic. Termination is invoked with that observed status, not success. This is the approved standalone ADMIN entry contract, not ordinary JMS worker fatal ranking; this review issues no ADMIN operation.'),
        (123, G): (1, 'The entry operation failure retains default status50 and only fixed public diagnostics. Input nulls are rejected before actions; the subsequent finished label is an entry diagnostic rather than proof of successful schema/admin/bootstrap. No role/key/DB operation is performed by this applicability review.'),
        (130, G): (1, 'A failed PT capture changes the process result to50 and cannot create native qualification. The capture-complete diagnostic is printed only after a true capture result. An attempted/error capture remains distinct from confirmed stream evidence.')},
    'CaddyPublicConfiguration': {(165, 'CloseResource'): (1, 'current aliases the last already-owned directory in held. It is not a new acquisition. Recursive children enter ResourceScope immediately and remain in the held chain during child access; closing this borrowed alias locally would violate the parent lifetime. This review reads source only, not actual root/CA files.')},
    'CleanupExpiryExecution': {
        (260, 'EmptyCatchBlock'): (1, 'An actual typed purge failure leaves purgeSucceeded=false and after=null; no fabricated after count or unattempted failure is emitted. A separate observed health result determines WARNING versus FAILED. The empty catch deliberately preserves that result contract, not a successful purge.'),
        (266, 'EmptyCatchBlock'): (1, 'Typed management-health failure leaves healthy=false, forcing FAILED and preventing startup admission even if purge completed. It does not silently turn unavailable Ops into healthy or reuse a previous observation.')},
    'BackupUnitTermination': {(118, 'AvoidSynchronizedStatement'): (1, 'Private stateLock serializes the full quiescence observation against object state, not caller-monitor ownership. Exact parent/budget/manager/kernel checks are still required before Optional presence; synchronization itself proves no real Unit termination or lock release.')},
    'InspectorUnitProbe': {
        (252, G): (2, 'Both unchecked query/process result failures wipe the locally owned observation buffer before identical rethrow. Known interruption/IO map separately to fixed StopGate reason. No provider text or partially read bytes are returned as valid Unit evidence.'),
        (325, G): (2, 'Both unchecked later command observation failures wipe the owned byte buffer and retain failure identity, after explicit known IO/interruption mapping. The public result is never inferred from a command start or missing response.')},
    'MorningBrokerUnitCycle': {(231, G): (2, 'Both unchecked uncertainty paths enter the already-prepared retention owner before leaving the start/admission callback. The fixed production retention does not return; the AssertionError explicitly rejects a returning invalid seam, not normal readiness or release. No broker start/stop is executed here.')},
    'MorningCaddyReadiness': {
        (397, 'AssignmentInOperand'): (1, 'Pre-increment bounds each descriptor directory entry before examining its symlink; the fixed maximum rejects excessive enumeration. Only validated socket syntax is collected, followed by independent network/owner/generation checks. A count or symlink alone cannot certify ownership.'),
        (402, 'EmptyCatchBlock'): (1, 'A descriptor disappearing during read adds no owned socket evidence. Remaining listeners must still satisfy the exact captured owner checks; the absent entry is not a clean stop or a fabricated matching socket.')},
    'MorningPreviousBroker': {(379, G): (2, 'Both unchecked journal validation/parent-check failures wipe the just-returned owned bytes before identical rethrow. Successful returned bytes must meet explicit length and parent conditions. No previous journal/boot/owner is accepted from this source-only reason.')},
    'MorningServiceReadiness': {
        (235, 'AssignmentInOperand'): (1, 'The fixed descriptor-entry limit increments once per observed entry before any symlink evidence is accepted. It prevents unbounded scanning, while all subsequent listener and original actor checks remain independent requirements.'),
        (241, 'EmptyCatchBlock'): (1, 'A concurrently closed FD is skipped without adding an ownership witness. Missing evidence cannot satisfy the exact listener/socket requirement or prove process termination; this is not a retry or access to a live process by the review.')},
    'SystemctlStateSource': {(95, G): (2, 'Both unchecked command/projection/resource failures wipe owned bytes before identical rethrow; known command/IO/interruption failures use separate fixed reasons. Nonzero exit and oversized output are explicitly rejected. Source inspection does not invoke systemctl or infer actual service state.')},
    'WebHttpServer': {
        (167, G): (2, 'Startup Runtime/Error retains the same primary after cleanup of a standalone component; native callers registered their partial owner before the fallible start and therefore defer cleanup to that owned phase. This explicit owner/null split is not blanket proof that a failed native cleanup completed.'),
        (172, G): (2, 'Standalone failed-destroy Runtime/Error is suppressed only when distinct from the startup primary, preventing self-suppression. The original startup still propagates, never a successfully returned server. Actual cleanup uncertainty and native owner retention remain separate YKT1318/1329 domains.')}
}
TESTS = {
    'BootstrapAdminMain': ['api.bootstrap.BootstrapAdminMainTest'],
    'CaddyPublicConfiguration': ['batch.file.CaddyPublicConfigurationTest'],
    'CleanupExpiryExecution': ['batch.file.CleanupExpiryExecutionTest'],
    'BackupUnitTermination': ['batch.platform.BackupUnitTerminationTest'],
    'InspectorUnitProbe': ['batch.platform.InspectorUnitProbeTest'],
    'MorningBrokerUnitCycle': ['batch.platform.MorningBrokerUnitCycleTest'],
    'MorningCaddyReadiness': ['batch.platform.MorningCaddyReadinessTest'],
    'MorningPreviousBroker': ['batch.platform.MorningPreviousBrokerTest'],
    'MorningServiceReadiness': ['batch.platform.MorningServiceReadinessTest'],
    'SystemctlStateSource': ['batch.platform.SystemctlStateSourceTest'],
    'WebHttpServer': ['web.bootstrap.WebHttpServerTest']
}


def calculate():
    scope = {**vars(engine), 'SPEC': SPEC, 'TESTS': TESTS,
             'PLAN': engine.BASE/'PG6394-startup-static-review-v1/manifest.json',
             'PLAN_SHA': '36d0f91a905a865b9ba45da550c9c56acdfe2b1652f8478a1c595f8852cfabfd'}
    raw = inspect.getsource(engine.calculate)
    for before, after in (('len(decisions) != 19', 'len(decisions) != 25'), ('all19 individually', 'all25 individually'),
                          ('reviewed=19', 'reviewed=25'), ('161 other current', '136 other current')):
        if raw.count(before) != 1:
            raise ValueError('explicit25 source span reader '+before)
        raw = raw.replace(before, after, 1)
    exec(compile(raw, '<25 source-only boundary spans>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = engine.BASE/'PG6404-runtime-boundary-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = engine.sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=25, statusCounts=value['statusCounts'], manifestSha256=engine.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
