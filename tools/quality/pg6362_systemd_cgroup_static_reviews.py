"""27 source-only native binding/cgroup/management applicability spans; no native invocation."""
import inspect
import json
import os
import pg6352_ordinary_boundary_static_reviews as previous

G = previous.G
SPEC = {
    'LinuxSystemdSession': {
        (100, G): (2, 'Both unchecked native-call failures publish uncertain=true before propagating the identical failure. Session/arena are not reported closed or reused; fixed outer observation retains pending. Source inspection neither calls sd-bus nor proves any live native owner.'),
        (136, 'AvoidDuplicateLiterals'): (1, 'The literal free selects the pinned libc void-release ABI rather than systemd pointer-return release. Repeated fixed ABI symbol in the exact allowlist is deliberate, not user-controlled dispatch or a new native call issued by this review.'),
        (140, G): (2, 'Both unchecked pointer-read/release failures retain uncertain state and prevent outputState from becoming unowned success. State transitions record actual completed output before release; failed native invocation is never silently retried.'),
        (174, G): (2, 'Both unchecked reads of the returned sd_bus_new pointer leave the native address in the preowned output slot and mark uncertain. A partly returned address is not overwritten with NULL or treated as safely released.'),
        (373, 'AssignmentInOperand'): (1, 'end++ advances only after a non-NUL byte read inside the fixed4097 bound. NUL is tested before copying, final length4096 limit rejects overlong strings, and the outer property projection separately validates public values. No unbounded C string read is inferred.'),
        (395, G): (2, 'Both unchecked Arena.close failures mark uncertain and leave retainedClosed=false. check also enforces original thread and live session. A returned signal or attempted release is not confirmed physical closure.'),
        (524, G): (2, 'Both unchecked MethodHandle failures retain original Runtime/Error identity rather than normalizing an unknown FFM contract. The handle symbol allowlist/ABI construction is separate from per-call observation; no arbitrary native handle is invoked here.'),
        (526, G): (1, 'Only the remaining checked Throwable from polymorphic MethodHandle invocation is mapped to fixed system-manager unavailable. Runtime/Error were rethrown first; provider text and arguments do not become public diagnostics.')},
    'FixedUnitCgroupNamespace': {
        (139, 'AssignmentInOperand'): (1, 'A nonnegative unique descriptor is stored at descriptors[count++] only after fixed-capacity guard and duplicate check. This is transfer to the preallocated owner before later operations, not a leaked temporary or dynamic FD acquisition in this review.'),
        (153, 'AssignmentInOperand'): (1, 'Nested descriptor transfer occurs only with a retained parent, fixed capacity and nonnegative/nonduplicate child. The post-increment consumes the next owner slot; all later close traversal uses that exact stored list.'),
        (173, G): (2, 'Both unchecked first close failures retain unknown primary, still attempt remaining owned descriptors via drain and append only fixed secondary diagnostics. closed marks consumed close attempt, not independently verified namespace release.'),
        (188, G): (2, 'During known close failure, the first later unknown becomes primary before remaining owned descriptors are drained. The policy preserves unknown versus known precedence without self-suppression or raw FD/provider diagnostic publication.'),
        (204, G): (2, 'Both unchecked remaining close failures set preallocated secondary flags for an already retained unknown. They never become normal resource completion; outer fixed Unit/namespace/ownership checks remain independent and are not executed here.')},
    'ArtemisManagementReadinessClient': {
        (100, G): (2, 'Both unchecked operation-encoder failures preserve original identity, including Error. Only checked provider encoding failures proceed to fixed management classification; no arbitrary management operation is accepted from the catch.'),
        (102, G): (1, 'The encoder E extends Exception requires a generic checked catch after Runtime/Error distinction. Checked InterruptedException restores the flag and all checked failures emit fixed readiness unavailable, not successful encoding or raw provider output.'),
        (318, G): (2, 'Both unchecked session/request/reply/resource-close failures preserve unknown identity. The requestor is owned locally in TWR while ClientSession remains caller-borrowed; deadline checks before/after exchange remain necessary.'),
        (320, G): (1, 'Only checked Core-client failures become fixed management unavailable, restoring interrupted state when appropriate. A null/unsuccessful management reply is already rejected; neither a real broker readiness proof nor a management exchange is produced by this source reason.')}
}
TESTS = {
    'LinuxSystemdSession': ['bootstrap.LinuxSystemdSessionTest'],
    'FixedUnitCgroupNamespace': ['batch.platform.CgroupPrimitiveOwnerTest'],
    'ArtemisManagementReadinessClient': ['batch.mq.ArtemisManagementReadinessClientTest', 'batch.mq.ArtemisManagementEncoderBoundaryTest']
}


def calculate():
    scope = {**vars(previous), 'SPEC': SPEC, 'TESTS': TESTS,
        'INPUT': previous.BASE/'PG6358-backup-archive-static-review-v1/manifest.json',
        'INPUT_SHA': '7ef99f90b7192abf4c570705b43fa83eae72aa951abd99c71d1a504477bc5250'}
    raw = inspect.getsource(previous.calculate)
    for before, after in (('len(decisions) != 21', 'len(decisions) != 27'), ('all21 explicitly', 'all27 explicitly'),
                          ('reviewed=21', 'reviewed=27'), ('296 other unreviewed', '164 other unreviewed')):
        if raw.count(before) != 1:
            raise ValueError('explicit27 source-only reader '+before)
        raw = raw.replace(before, after, 1)
    exec(compile(raw, '<27 individual systemd/cgroup/management source spans>', 'exec'), scope)
    return scope['calculate']()


def main():
    rows, value = calculate(); os.umask(0o077); out = previous.BASE/'PG6362-systemd-cgroup-static-review-v1'; out.mkdir()
    for name, item in (('decisions.json', rows), ('manifest.json', value)):
        if name == 'manifest.json':
            value['decisionsSha256'] = previous.sha(out/'decisions.json')
        with (out/name).open('x') as f:
            json.dump(item, f, ensure_ascii=False, sort_keys=True, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0, reviewed=27, statusCounts=value['statusCounts'], manifestSha256=previous.sha(out/'manifest.json'))))


if __name__ == '__main__':
    main()
