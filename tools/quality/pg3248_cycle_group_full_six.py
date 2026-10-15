"""One necessary integration: three cycle Tests/two files, same a9 Main.

451/K01/PT-OPS-3248-001; qualified3694 is history, not these new Test results.
"""
import ast
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import pg3204_expiry_group_full_six as previous
from pg1446_current_cold_stage import W

SOURCE = previous.SOURCE
ROOT = Path(__file__).resolve().parents[2]
PREFIX = previous.PREFIX
CASES = [('pg3244-backup-cycle-selected-v1', 'platform/MorningBackupUnitCycleTest.java', 12),
         ('pg3246-inspector-cycle-selected-v1', 'platform/InspectorUnitCycleTest.java', 4)]


def validate(snapshot):
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT)
    full = json.loads((W / 'pg3206-expiry-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if full['actualExit'] != 0 or full['result']['tests'] != 3694 or full['result']['productionSource'] != SOURCE:
        raise ValueError('exact actual3694 prior full required')
    base = full['result']['sourceSnapshot']
    changed = set(git('diff', '--name-only', base, snapshot, '--', *previous.previous.engine.SCOPE).decode().splitlines())
    if changed != {PREFIX + p for _, p, _ in CASES}: raise ValueError('exact two Test-only changes and unchanged Main/resources/settings required')
    increase = 0
    for slot, relative, count in CASES:
        path = PREFIX + relative; receipt = json.loads((W / slot / 'manifest.safe.json').read_bytes())
        if any(receipt.get(k) != value for k, value in {'actualExit': 0, 'tests': count, 'FESAbortedNotRun': 0, 'nativeImported': False, 'vmActions': 0}.items()): raise ValueError('actual whole related suite required')
        payload = (W / slot / 'selected.private.py').read_bytes()
        if hashlib.sha256(payload).hexdigest() != receipt['payloadSha256']: raise ValueError('immutable selected input required')
        data = ast.literal_eval(payload.decode().splitlines()[0].removeprefix('INPUT='))
        content = git('show', snapshot + ':' + path)
        if hashlib.sha256(content).hexdigest() != data['files'][Path(path).name] or content.decode().count('@Test\n') != count:
            raise ValueError('all new Test file bytes must equal actually successful selected class')
        increase += count - git('show', base + ':' + path).decode().count('@Test\n')
    if increase != 3: raise ValueError('3694 retained plus exactly three new Test methods required')


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG3204', 'PG3248').replace('3694', '3697')
    compile(raw, '<3697 six-module format first and whole tests>', 'exec')
    return raw


def main():
    engine = previous.previous.engine
    raw = inspect.getsource(engine.main).replace('PG2798', 'PG3248').replace('pg2798', 'pg3248').replace('3680', '3697')
    raw = raw.replace('3673 retained plus five independently real-DB Session methods and two owner-admission methods; changed JDBC Main;542suite1643', '3694 retained plus three cycle handoff/recheck methods in two Test files; unchanged a9 Main;542suite1643')
    raw = raw.replace('BUG1251/YKT1017 changed JDBC null-resource Main and seven grouped tests require one fresh all-source/static regression; Source042 native not portable', 'Three new methods/two actually selected Test files require one3697 integration; same a9 native28; no VM/sign/deploy replay')
    ns = {**engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server_source': server_source}
    exec(compile(raw, '<whole3697 grouped Test-only integration>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
