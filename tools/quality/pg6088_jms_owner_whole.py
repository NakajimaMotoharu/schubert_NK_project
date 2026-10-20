"""One necessary same-source3985 ordinary fixture whole after JMS ownership corrections."""
import ast
import inspect
import json
import os
import subprocess
from pyflakes.api import check
import pg6060_expiry_current_whole as prior
from pg6082_web_factory_qualification import SOURCE
from pg5940_private_lock_compile import ROOT, W, BASE, sha

LABEL = 'PG6088'
SLOT = 'pg6088-jms-owner-six-v1'


def declared_inventory():
    raw = inspect.getsource(prior.declared_inventory)
    old = '(3979, 594)'
    if raw.count(old) != 1:
        raise ValueError('one complete explicit source declaration inventory')
    scope = dict(vars(prior))
    exec(compile(raw.replace(old, '(3985, 595)', 1), '<3985 ordinary declaration guard>', 'exec'), scope)
    return scope['declared_inventory']()


def server_source(head, digest):
    raw = prior.server_source(head, digest).replace('PG6060', LABEL).replace('pg6060', 'pg6088').replace(prior.SOURCE, SOURCE)
    tree = ast.parse(raw)
    if {n: sum(isinstance(x, ast.Constant) and type(x.value) is int and x.value == n for x in ast.walk(tree))
            for n in (3979, 594, 1667)} != {3979: 2, 594: 1, 1667: 1}:
        raise ValueError('exact whole verdict and result dimensions before update')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value in (3979, 594):
                return ast.copy_location(ast.Constant({3979: 3985, 594: 595}[node.value]), node)
            return node
    raw = ast.unparse(ast.fix_missing_locations(Counts().visit(tree)))
    if check(raw, '<ordinary3985 host fixtures>') or any(s in raw for s in (
            'systemctl', 'qemu-system', 'virsh', 'sudo ', '/opt/schubert-nk/current', '--recover', '--resume')):
        raise ValueError('approved ordinary finite fixture profile;held runtime excluded')
    compile(raw, '<current3985 complete definition>', 'exec')
    return raw


def driver_source(fresh):
    raw = prior.driver_source(fresh).replace(prior.SLOT, SLOT).replace('PG6060', LABEL).replace('pg6060', 'pg6088')
    old = "'tests': 3979, 'suites': 594, 'mainClasses': 1667"
    if raw.count(old) != 1:
        raise ValueError('one exact same-source whole inventory')
    raw = raw.replace(old, "'tests': 3985, 'suites': 595, 'mainClasses': 1667", 1)
    start = raw.index("'trigger': "); end = raw.index('}, sort_keys=True)', start)
    trigger = ('BUG1537/YKT1297/SSC311: five Main JMS ownership boundaries; three consumer state-before-acquire, '
               'API preallocated three groups, Web guarded provider configuration and state-before-factory. '
               'Six new independent JUnit cases,previous3979 source cases retained. Current selected1933 then '
               'provider925 qualifications and actual JVM order/ABI/source851/physical1667 first. '
               'Necessary integrated current3985/595,not old-source replay or additive PASS. '
               'Allsix format before PT;ordinary owned temp fixtures only,no actual VM/current/Root/cohort/permit; '
               'native/CHR/global100/451/trace/formal remain separate.')
    raw = raw[:start]+"'trigger': "+repr(trigger)+raw[end:]
    compile(raw, '<new-only3985 driver>', 'exec')
    return raw


def prerequisites():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed source and operator first')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw',
                                'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('same canonical Main/Test/gates fixed')
    qpath = BASE/'PG6082-web-factory-qualification-v1/manifest.json'
    opath = BASE/'PG6084-web-factory-order-v1/manifest.json'
    q, order = [json.loads(p.read_bytes()) for p in (qpath, opath)]
    if (q['source'] != SOURCE or q['actualExit'] != 0 or (q['tests'], q['suites'], q['physicalMain']) != (925, 150, 1667)
            or order['source'] != SOURCE or order['actualExit'] != 0 or order['qualificationSha256'] != sha(qpath)
            or not order['publicAbiUnchanged'] or not order['allOwnershipBoundariesVerified']):
        raise ValueError('genuine925 and all current ownership proof before whole')
    private = W/'pg6082-web-factory-qualification-v1/manifest.safe.json'
    if sha(private) != q['privateManifestSha256']:
        raise ValueError('original qualified physical/source map hash')
    proof = json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all851 current Main unchanged')
    declared_inventory()


def main():
    prerequisites(); server_source(SOURCE, '0'*64)
    fresh = prior.previous.RUNTIME.preflight(); os.umask(0o077)
    with (W/'pg6088-preflight-v1.safe.json').open('x') as f:
        json.dump(fresh, f, sort_keys=True); f.flush(); os.fsync(f.fileno())
    scope = {**vars(prior.previous.RUNTIME.previous.driver), 'SOURCE': SOURCE, 'LABEL': LABEL, 'server_source': server_source}
    exec(compile(driver_source(fresh), '<one necessary3985 ordinary whole>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
