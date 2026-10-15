"""One necessary integration: six new Test methods/four Test files, unchanged a9 Main."""
import ast
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import pg2798_jdbc_null_fixed_full_six as engine
import pg3026_extra_row_full_six as previous
from pg1446_current_cold_stage import W

SOURCE = previous.SOURCE
CASES = [
    ('pg3044-expiry-boundary-selected-v1', 'platform/ExpiryWorkerRequestTest.java', 6),
    ('pg3048-transfer-security-selected-v1', 'file/TransferCleanupTest.java', 6),
    ('pg3050-caddy-grammar-selected-v1', 'file/CaddyPublicConfigurationTest.java', 3),
    ('pg3052-caddy-lifetime-selected-v1', 'platform/MorningCaddyReadinessTest.java', 14),
]


def validate(snapshot):
    root = Path(__file__).resolve().parents[2]
    git = lambda *args: subprocess.check_output(['git', *args], cwd=root)
    whole = json.loads((W / 'pg3028-extra-row-full-qualified-v1/manifest.safe.json').read_bytes())
    if whole['actualExit'] != 0 or whole['result']['tests'] != 3685 or whole['result']['productionSource'] != SOURCE:
        raise ValueError('actual exact3685 qualified baseline required')
    base = whole['result']['sourceSnapshot']
    expected = {'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/' + p for _, p, _ in CASES}
    changed = set(git('diff', '--name-only', base, snapshot, '--', *engine.SCOPE).decode().splitlines())
    if changed != expected:
        raise ValueError('exact four Test-only changes; Main/resource/characterization unchanged')
    increase = 0
    for slot, relative, count in CASES:
        path = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/' + relative
        out = W / slot
        receipt = json.loads((out / 'manifest.safe.json').read_bytes())
        if any(receipt.get(k) != v for k, v in {'actualExit': 0, 'tests': count, 'FESAbortedNotRun': 0, 'nativeImported': False, 'vmActions': 0}.items()):
            raise ValueError('actual whole selected class required')
        payload = (out / 'selected.private.py').read_bytes()
        if hashlib.sha256(payload).hexdigest() != receipt['payloadSha256']:
            raise ValueError('actual selected payload immutable hash required')
        value = ast.literal_eval(payload.decode().splitlines()[0].removeprefix('INPUT='))
        current = git('show', snapshot + ':' + path)
        if hashlib.sha256(current).hexdigest() != value['files'][Path(path).name] or current.decode().count('@Test\n') != count:
            raise ValueError('every complete Test file byte equal to actual selected input')
        increase += count - git('show', base + ':' + path).decode().count('@Test\n')
    if increase != 6:
        raise ValueError('3685 plus exactly six independently selected methods required')


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG3026', 'PG3054').replace('3685', '3691')
    compile(raw, '<whole3691 six format gates first>', 'exec')
    return raw


def main():
    raw = inspect.getsource(engine.main).replace('PG2798', 'PG3054').replace('pg2798', 'pg3054').replace('3680', '3691')
    raw = raw.replace('3673 retained plus five independently real-DB Session methods and two owner-admission methods; changed JDBC Main;542suite1643', '3685 retained plus six independently selected methods in four Test files; Main unchanged;542suite1643')
    raw = raw.replace('BUG1251/YKT1017 changed JDBC null-resource Main and seven grouped tests require one fresh all-source/static regression; Source042 native not portable', 'Six new methods and four exact selected Test files require one grouped3691 integration; same a9 Main/member bytes; no VM or signature replay')
    ns = {**engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server_source': server_source}
    exec(compile(raw, '<new3691 necessary group transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
