"""35 Backup atomic-completion/archive ownership source spans; no Backup or Process invocation."""
import inspect
import json
import os
import pg6352_ordinary_boundary_static_reviews as previous

G = previous.G
I = 'AvoidInstanceofChecksInCatchClause'
SPEC = {
    'BackupCommitService': {
        (34, G): (2, 'Both unchecked two-step update/commit failures attempt rollback plus autocommit restoration on the borrowed parent connection before rethrow. A terminal value cannot escape before commit/restoration and the final interrupt check. No manifest value itself authenticates root artifacts.'),
        (38, G): (2, 'Both unchecked rollback/restoration failures apply explicit SS331/341/343 unknown-primary precedence. Unknown original remains identical with fixed secondary; known original cannot hide unknown cleanup. No raw SQL/provider diagnostics or partial two-step success is returned.'),
        (39, I): (2, 'Original Error is distinguished in each generic catch alternative to preserve its identity across failed rollback/restoration. The test is not recoverability by class name or a success fallback; direct fatal is rethrown.'),
        (40, I): (2, 'Original RuntimeException distinguishes unknown provider contract failure from known BatchRepositoryException. Only the former retains identity with a new fixed secondary. This preserves the declared mixed failure policy, not the ordinary JMS fatal rank.'),
        (41, I): (2, 'The fixed BatchRepositoryException catalogue is a known outcome, not arbitrary Runtime. Excluding it from unknown-primary preservation is necessary for known/known cleanup to remain a fixed batch failure without provider text.'),
        (45, I): (2, 'When original is known, cleanup Error must escape as its identical fatal object, not fixed ordinary batch failure. Original unknown has already been preserved above; this branch does not reorder unknown-versus-unknown precedence.'),
        (46, I): (2, 'When original is known, an unknown cleanup Runtime is propagated instead of normalized. This is distinct from declared SQL/repository cleanup and remains unsuccessful atomic completion.'),
        (47, I): (2, 'Cleanup BatchRepositoryException is recognized as fixed known catalogue while arbitrary Runtime remains unknown. All known/known combinations return only new fixed batch failure; no raw cleanup object or successful manifest is exposed.')},
    'BackupArchiveProcess': {
        (306, 'CloseResource'): (1, 'StdIoOwner captures the stream returned by the prebuilt acquire port in its own retained field. writeAndClose calls the same owner close, while outer resource scope closes on failures. closed marks one close attempt only; this source reason does not infer a physical pipe close after unknown failure.'),
        (346, G): (2, 'Both unchecked outer terminal-plan failures enter the prebuilt pending hold when confirmed remains false. A broken process collection cannot allow the borrowed resource frame to unwind as terminated; fixed production hold is not the returning test port.'),
        (360, G): (2, 'Both unchecked stop failures preserve the first primary after attempting the remaining owned Process handles. Secondary failures become fixed unavailable entries; no repeated business Backup or foreign process discovery is issued.'),
        (374, G): (2, 'While already handling known stop IO, the first unchecked later failure becomes primary and remaining owned handles are still attempted. Known failure does not erase unknown cleanup or certify terminal state.'),
        (387, G): (2, 'Both unchecked remaining-stop failures are counted only as secondary to an already retained unknown primary. This finite traversal is followed by the independent terminal hold, not assumed successful kill or permission to release unknown ownership.'),
        (401, G): (2, 'Both unchecked terminal-observation failures preserve the first unknown after still waiting the remaining owned handles. holdTerminal itself quarantines until that exact process is terminal before rethrow; unenumerable outer ownership returns to the pending hold.'),
        (407, G): (2, 'Both unchecked later terminal observations count fixed secondary failures while retaining the first primary. confirmed=true only follows the required per-handle terminal hold traversal; source reasoning is not proof that actual process/cgroup termination occurred.'),
        (450, G): (2, 'Both unchecked initial Process observation failures enter holdAfterUnknown rather than treating failure as dead. After terminal observation eventually returns, the identical first primary is rethrown; interrupted state is retained separately.'),
        (466, G): (2, 'Both unchecked subsequent terminal-observation failures remain quarantined with bounded backoff and interrupt consumption, never normal success from an observation exception. The fixed Unit/cgroup timeout remains an external contract, not a host test result here.'),
        (551, G): (2, 'Both unchecked pipeline factory failures enter the preconstructed pending port because a thrown factory does not enumerate every partly spawned process. Production hold never returns; a package Test port return still yields fixed failure, not an empty successful pipeline or kill claim.')}
}
TESTS = {
    'BackupCommitService': ['batch.backup.BackupCommitServiceTest'],
    'BackupArchiveProcess': ['batch.platform.BackupArchiveProcessTest']
}


def calculate():
    scope = {**vars(previous), 'SPEC': SPEC, 'TESTS': TESTS,
        'INPUT': previous.BASE/'PG6356-shared-boundary-static-review-v1/manifest.json',
        'INPUT_SHA': '0bb79cb5ff97ba4e376708e9e3f0ec0320aae833d496a74641a66ef2209114a9'}
    raw = inspect.getsource(previous.calculate)
    for before, after in (('len(decisions) != 21', 'len(decisions) != 35'), ('all21 explicitly', 'all35 explicitly'),
                          ('reviewed=21', 'reviewed=35'), ('296 other unreviewed', '191 other unreviewed')):
        if raw.count(before) != 1:
            raise ValueError('explicit35 backup/archive source reader '+before)
        raw = raw.replace(before, after, 1)
    exec(compile(raw, '<35 individually read Backup/archive spans>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = previous.BASE/'PG6358-backup-archive-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = previous.sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=35, statusCounts=value['statusCounts'], manifestSha256=previous.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
