"""One necessary ordinary3988 whole after grouped HTTP ownership and locked flag edits."""
import ast
import inspect
import json
import os
import subprocess
from pyflakes.api import check
import pg6088_jms_owner_whole as prior
from pg6114_http_owner_qualification import SOURCE
from pg5940_private_lock_compile import ROOT, W, BASE, sha

LABEL = 'PG6118'
SLOT = 'pg6118-http-owner-six-v1'


def declared_inventory():
    raw = inspect.getsource(prior.prior.declared_inventory)
    if raw.count('(3979, 594)') != 1:
        raise ValueError('one full declaration inventory including original repeat10')
    scope = dict(vars(prior.prior))
    exec(compile(raw.replace('(3979, 594)', '(3988, 595)', 1), '<3988 declarations>', 'exec'), scope)
    return scope['declared_inventory']()


def server_source(head, digest):
    raw = prior.server_source(head, digest).replace('PG6088', LABEL).replace('pg6088', 'pg6118').replace(prior.SOURCE, SOURCE)
    tree = ast.parse(raw)
    if {n: sum(isinstance(x, ast.Constant) and type(x.value) is int and x.value == n for x in ast.walk(tree))
            for n in (3985, 595, 1667)} != {3985: 2, 595: 1, 1667: 1}:
        raise ValueError('exact whole result/verdict dimensions')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self, node):
            if type(node.value) is int and node.value == 3985:
                return ast.copy_location(ast.Constant(3988), node)
            return node
    raw = ast.unparse(ast.fix_missing_locations(Counts().visit(tree)))
    if check(raw, '<ordinary3988>') or any(x in raw for x in ('systemctl', 'qemu-system', 'virsh', 'sudo ', '/opt/schubert-nk/current', '--recover', '--resume')):
        raise ValueError('finite self-owned fixtures only;held operational entrypoints excluded')
    compile(raw, '<3988 source locked>', 'exec')
    return raw


def driver_source(fresh):
    raw = prior.driver_source(fresh).replace(prior.SLOT, SLOT).replace('PG6088', LABEL).replace('pg6088', 'pg6118')
    before = "'tests': 3985, 'suites': 595, 'mainClasses': 1667"
    if raw.count(before) != 1:
        raise ValueError('one integrated current inventory')
    raw = raw.replace(before, "'tests': 3988, 'suites': 595, 'mainClasses': 1667", 1)
    start = raw.index("'trigger': "); end = raw.index('}, sort_keys=True)', start)
    trigger = ('SSC312/BUG1545/YKT1305: three HTTP owner factory-before-state allocation gaps corrected, '
               'three independent acquisition Tests;BUG1544 locked closed modifier grouped in same source. '
               'Original1939/318 and all851/1667/JVM/publicABI qualify first. One necessary current3988/595 '
               'integrated regression;old8703985 and599925 not imported. Ordinary finite host fixtures only;'
               'noVM/current/Root/failedcohort/permit;native/CHR/global100/451/trace/formal separate.')
    raw = raw[:start]+"'trigger': "+repr(trigger)+raw[end:]
    compile(raw, '<newonly3988 driver>', 'exec')
    return raw


def prerequisites():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean source/Test/operator first')
    if subprocess.check_output(['git', 'diff', SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('canonical Main/Test/gates remain fixed')
    qp = BASE/'PG6114-http-owner-qualification-v1/manifest.json'
    op = BASE/'PG6116-http-owner-order-v1/manifest.json'
    q, order = [json.loads(p.read_bytes()) for p in (qp, op)]
    if (q['source'] != SOURCE or q['actualExit'] != 0 or (q['tests'], q['suites'], q['physicalMain']) != (1939, 318, 1667)
            or order['source'] != SOURCE or order['actualExit'] != 0 or order['qualificationSha256'] != sha(qp)
            or len(order['owners']) != 3 or not all(x['publicAbiUnchanged'] for x in order['owners'])):
        raise ValueError('genuine current1939/allthreeownership qualification before whole')
    private = W/'pg6114-http-owner-qualification-v1/manifest.safe.json'
    if sha(private) != q['privateManifestSha256']:
        raise ValueError('original qualified source/class map hash')
    proof = json.loads(private.read_bytes())
    if {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')} != proof['allSourceHashes']:
        raise ValueError('all851 current source hashes match original1939')
    declared_inventory()


def main():
    prerequisites(); server_source(SOURCE, '0'*64)
    fresh = prior.prior.previous.RUNTIME.preflight(); os.umask(0o077)
    with (W/'pg6118-preflight-v1.safe.json').open('x') as stream:
        json.dump(fresh, stream, sort_keys=True); stream.flush(); os.fsync(stream.fileno())
    scope = {**vars(prior.prior.previous.RUNTIME.previous.driver), 'SOURCE': SOURCE, 'LABEL': LABEL, 'server_source': server_source}
    exec(compile(driver_source(fresh), '<one current3988 whole>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
