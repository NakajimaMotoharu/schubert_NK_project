"""One necessary integration of three new public Expiry boundary Tests; Main a9.

451/K01; PT-OPS-3204-001. Exact three Test files, including shared helper suite.
"""
import ast
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import pg3054_boundary_group_full_six as previous
from pg1446_current_cold_stage import W

SOURCE = previous.SOURCE
ROOT = Path(__file__).resolve().parents[2]
PREFIX = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'
CASES = [('pg3200-expiry-connection-selected-v1', 'repository/CleanupDatabaseSessionTest.java', 10),
         ('pg3202-expiry-audit-selected-v1', 'repository/ExpiryAuditRepositoryTest.java', 7)]
HELPER = PREFIX + 'platform/RootReleaseAdmissionTest.java'


def validate(snapshot):
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT)
    old = json.loads((W / 'pg3056-boundary-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if old['actualExit'] != 0 or old['result']['tests'] != 3691 or old['result']['productionSource'] != SOURCE:
        raise ValueError('exact actual3691 baseline required')
    base = old['result']['sourceSnapshot']
    changed = set(git('diff', '--name-only', base, snapshot, '--', *previous.engine.SCOPE).decode().splitlines())
    if changed != {PREFIX + path for _, path, _ in CASES} | {HELPER}:
        raise ValueError('exact three Test-only changes; unchanged Main/config/characterization required')
    increase = 0
    for slot, relative, count in CASES:
        path = PREFIX + relative
        receipt = json.loads((W / slot / 'manifest.safe.json').read_bytes())
        if any(receipt.get(k) != v for k, v in {'actualExit': 0, 'tests': count, 'FESAbortedNotRun': 0, 'nativeImported': False, 'vmActions': 0}.items()):
            raise ValueError('actual selected whole class required')
        payload = (W / slot / 'selected.private.py').read_bytes()
        if hashlib.sha256(payload).hexdigest() != receipt['payloadSha256']:
            raise ValueError('immutable selected payload SHA required')
        data = ast.literal_eval(payload.decode().splitlines()[0].removeprefix('INPUT='))
        for target in [path, HELPER]:
            raw = git('show', snapshot + ':' + target)
            if hashlib.sha256(raw).hexdigest() != data['files'][Path(target).name]:
                raise ValueError('actual selected Test/helper byte identity required')
        increase += git('show', snapshot + ':' + path).decode().count('@Test\n') - git('show', base + ':' + path).decode().count('@Test\n')
    if increase != 3 or git('show', snapshot + ':' + HELPER).decode().count('@Test\n') != git('show', base + ':' + HELPER).decode().count('@Test\n'):
        raise ValueError('exact three new methods and unchanged shared suite count required')


def server_source(head, digest):
    return previous.server_source(head, digest).replace('PG3054', 'PG3204').replace('3691', '3694')


def main():
    raw = inspect.getsource(previous.engine.main).replace('PG2798', 'PG3204').replace('pg2798', 'pg3204').replace('3680', '3694')
    raw = raw.replace('3673 retained plus five independently real-DB Session methods and two owner-admission methods; changed JDBC Main;542suite1643', '3691 retained plus three real-DB public Expiry boundary tests; Main unchanged;542suite1643')
    raw = raw.replace('BUG1251/YKT1017 changed JDBC null-resource Main and seven grouped tests require one fresh all-source/static regression; Source042 native not portable', 'Three new methods/three Test files/shared helper require one new3694 integration; same a9 Main/native27 byte join; no guest replay')
    ns = {**previous.engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server_source': server_source}
    exec(compile(raw, '<whole3694 necessary Test-input integration>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
