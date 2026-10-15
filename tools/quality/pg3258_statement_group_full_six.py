"""One necessary integration of two independently selected Session Tests; Main a9."""
import ast
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import pg3248_cycle_group_full_six as previous
from pg1446_current_cold_stage import W

SOURCE = previous.SOURCE
ROOT = previous.ROOT
TEST = previous.PREFIX + 'repository/MorningDatabaseSessionTest.java'


def validate(snapshot):
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT)
    old = json.loads((W / 'pg3250-cycle-group-full-qualified-v1/manifest.safe.json').read_bytes())
    if old['actualExit'] != 0 or old['result']['tests'] != 3697 or old['result']['productionSource'] != SOURCE:
        raise ValueError('actual exact3697 old full required')
    base = old['result']['sourceSnapshot']; engine = previous.previous.previous.engine
    changed = set(git('diff', '--name-only', base, snapshot, '--', *engine.SCOPE).decode().splitlines())
    if changed != {TEST}: raise ValueError('one exact Test-only change, unchanged Main/settings/resources required')
    out = W / 'pg3256-completion-guard-selected-v1'; receipt = json.loads((out / 'manifest.safe.json').read_bytes())
    if any(receipt.get(k) != value for k, value in {'actualExit': 0, 'tests': 63, 'FESAbortedNotRun': 0, 'nativeImported': False, 'vmActions': 0}.items()): raise ValueError('actual whole63 with both cases required')
    payload = (out / 'selected.private.py').read_bytes()
    if hashlib.sha256(payload).hexdigest() != receipt['payloadSha256']: raise ValueError('immutable actual selected payload required')
    data = ast.literal_eval(payload.decode().splitlines()[0].removeprefix('INPUT='))
    content = git('show', snapshot + ':' + TEST)
    if hashlib.sha256(content).hexdigest() != data['files'][Path(TEST).name] or content.decode().count('@Test\n') != 63:
        raise ValueError('new Test file byte equal to successful selected63 required')
    if content.decode().count('@Test\n') - git('show', base + ':' + TEST).decode().count('@Test\n') != 2:
        raise ValueError('3697 retained plus exactly two new Test methods required')


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG3248', 'PG3258').replace('3697', '3699')
    compile(raw, '<whole3699 same a9 Main>', 'exec'); return raw


def main():
    engine = previous.previous.previous.engine
    raw = inspect.getsource(engine.main).replace('PG2798', 'PG3258').replace('pg2798', 'pg3258').replace('3680', '3699')
    raw = raw.replace('3673 retained plus five independently real-DB Session methods and two owner-admission methods; changed JDBC Main;542suite1643', '3697 retained plus two real-DB Statement/completion guard methods in one Test file; unchanged Main;542suite1643')
    raw = raw.replace('BUG1251/YKT1017 changed JDBC null-resource Main and seven grouped tests require one fresh all-source/static regression; Source042 native not portable', 'Two new methods/one actually selected63 Test file require one3699 integration; same a9 sealed native28; no VM/sign/deploy replay')
    ns = {**engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server_source': server_source}
    exec(compile(raw, '<necessary whole3699 transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
