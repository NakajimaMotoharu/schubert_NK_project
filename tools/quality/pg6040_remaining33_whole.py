"""One necessary3976 after typed boundary and remaining33 constants;ordinary host fixtures only."""
import ast
import json
import os
import subprocess
from pyflakes.api import check
import pg6014_constants_whole as previous
from pg5780_jms_primary_whole import RUNTIME
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6034_corrected_boundary_static import SOURCE as OLD

SOURCE = '8c869d7cea21d587b859b3e72e3516d9d2deb5c8'
LABEL = 'PG6040'
SLOT = 'pg6040-remaining33-six-v1'
PLAN = BASE/'PG6038-remaining33-plan-v1/manifest.json'
PLAN_SHA = 'b4c01b12dde1c84f9266d821b5b4ded0767f332a00a519ca1faeb9ffd9358267'


def plan():
    if sha(PLAN) != PLAN_SHA:
        raise ValueError('all22 immutable predicted Main source hashes before PG')
    return json.loads(PLAN.read_bytes())


def server_source(head, digest):
    raw = previous.server_source(head, digest).replace('PG6014', LABEL).replace('pg6014', 'pg6040').replace(previous.SOURCE, SOURCE)
    parsed = ast.parse(raw); counts = {n: sum(isinstance(x, ast.Constant) and type(x.value) is int and x.value == n for x in ast.walk(parsed)) for n in (3973, 592, 1666)}
    if counts != {3973: 2, 592: 1, 1666: 1}:
        raise ValueError('all exact original verdict/result constants accounted for')
    class CurrentCounts(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value in (3973, 592, 1666):
                return ast.copy_location(ast.Constant({3973: 3976, 592: 593, 1666: 1667}[node.value]), node)
            return node
    raw = ast.unparse(ast.fix_missing_locations(CurrentCounts().visit(parsed)))
    if check(raw, '<current3976 ordinary host runner>') or any(s in raw for s in ('systemctl', 'qemu-system', 'virsh', 'sudo ', '/opt/schubert-nk/current', '--recover', '--resume')):
        raise ValueError('complete approved finite fixture profile;held runtime actions excluded')
    compile(raw, '<current3976 same-source runner>', 'exec')
    return raw


def driver_source(fresh):
    raw = previous.driver_source(fresh).replace(previous.SLOT, SLOT).replace('PG6014', LABEL).replace('pg6014', 'pg6040')
    old = "'tests': 3973, 'suites': 592, 'mainClasses': 1666"
    if raw.count(old) != 1:
        raise ValueError('one explicit expected current3976 inventory')
    raw = raw.replace(old, "'tests': 3976, 'suites': 593, 'mainClasses': 1667", 1)
    start = raw.index("'trigger': "); end = raw.index('}, sort_keys=True)', start)
    trigger = 'PG-D453..455: current typed encoder/unknown identity plus all22 remaining33 same-value constant conditions across API/batch/bootstrap. Current965/162 and all8511667/static/ABI qualified at32f;all22 predicted PG SHA exact. One necessary full3976/593 after these changes,not replay of old3973/965. Format allsix precedes any PT;full build/PT then independent all-byte/method equivalence/raw/actual coverage. Test/oracle/resources/gates unchanged from32f. No VM/current/Root/failed-cohort actions or historical native import.'
    raw = raw[:start]+"'trigger': "+repr(trigger)+raw[end:]
    compile(raw, '<new-only3976 driver>', 'exec')
    return raw


def prerequisites():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed operator/source first')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('canonical source/Test/gates frozen')
    p = plan(); paths = {r['path'] for r in p['sourcePlans']}
    if len(paths) != 22 or set(subprocess.check_output(['git', 'diff', '--name-only', OLD, SOURCE, '--', 'src'], cwd=ROOT, text=True).splitlines()) != paths:
        raise ValueError('exact22 predicted Main changes only;Test/fixture/resource unchanged')
    if subprocess.check_output(['git', 'diff', OLD, SOURCE, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('same build/quality/compatibility gates')
    for row in p['sourcePlans']:
        if sha(ROOT/row['path']) != row['predictedAfterSha256']:
            raise ValueError('all22 exact predicted formatted Main')
    sp = BASE/'PG6034-corrected-boundary-static-v1/manifest.json'
    if sha(sp) != '4be1ee7550f3cf719b5da6a362ad418c444eadd2deea7b7368c50807a20b3ad8':
        raise ValueError('original qualified32f all8511667/static proof retained')
    public = json.loads(sp.read_bytes()); pp = W/'pg6034-corrected-boundary-static-v1/manifest.safe.json'
    if sha(pp) != public['privateManifestSha256']:
        raise ValueError('actual prior full physical map')
    proof = json.loads(pp.read_bytes()); expected = dict(proof['allSourceHashes'])
    for row in p['sourcePlans']:
        if expected[row['path']] != row['beforeSha256']:
            raise ValueError('exact22 original source correspondence')
        expected[row['path']] = row['predictedAfterSha256']
    if {q.relative_to(ROOT).as_posix(): sha(q) for q in ROOT.glob('src/*/src/main/java/**/*.java')} != expected or len(expected) != 851:
        raise ValueError('every Main input fixed;no unrelated edits')
    qp = BASE/'PG6036-corrected-boundary965-v1/manifest.json'
    if sha(qp) != 'd640bbe1424f63e331b2aba8ba57c6789fa584fb201f75cb5fc63f4b68cd0ac6' or not json.loads(qp.read_bytes())['originalSelectedOverallAccepted']:
        raise ValueError('prior corrected965 is genuine,not failed6026 promoted')


def main():
    prerequisites(); server_source(SOURCE, '0'*64)
    fresh = RUNTIME.preflight(); os.umask(0o077)
    with (W/'pg6040-preflight-v1.safe.json').open('x') as f:
        json.dump(fresh, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    scope = {**vars(RUNTIME.previous.driver), 'SOURCE': SOURCE, 'LABEL': LABEL, 'server_source': server_source}
    exec(compile(driver_source(fresh), '<one necessary current3976>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
