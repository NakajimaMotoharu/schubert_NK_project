"""One grouped full regression after nine new Tests and two Test-fixture repairs."""
import ast
import inspect
import json
import subprocess
from pyflakes.api import check
import pg6890_data4213_whole as prior
import pg6188_native_ownership_whole as base
import pg6922_db_fixture_selected as selected
from pg5940_private_lock_compile import ROOT, W, BASE, sha

LABEL = 'PG6930'
SLOT = 'pg6930-fixture4222-six-v1'
QSHA = '7a60d8e3ebf2acad4bc4f80bf24a38ba2272c77b07e9e79f1b03ff59d083035c'
OLD = '2e3cdb6ff6b0b7c3af0e33413affbda6fdbb2c3f'
NEW_TESTS = selected.TESTS | {
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/LegacyReceiptValueTest.java',
 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/ObservationValueRedactionTest.java'}


def guard(source):
    selected.green_guard(source)
    raw = subprocess.check_output(['git', 'diff', '--name-status', OLD, source, '--', 'src'], cwd=ROOT, text=True)
    expected = {'A\t' + p for p in NEW_TESTS} | {'M\t' + p for p in selected.FIXTURES}
    if set(raw.splitlines()) != expected or len(raw.splitlines()) != 6:
        raise ValueError('four new Test classes and two repaired Test fixtures only; Main/old oracles fixed')


def original_source():
    source = json.loads((W / selected.SLOTS['green'] / 'begin.safe.json').read_bytes())['source']
    guard(source)
    return source


def declared_inventory():
    raw = inspect.getsource(base.declared_inventory)
    if raw.count('(4023, 605)') != 1:
        raise ValueError('one independent full declaration tuple')
    scope = dict(vars(base))
    exec(compile(raw.replace('(4023, 605)', '(4222, 660)', 1), '<all4222 declarations>', 'exec'), scope)
    return scope['declared_inventory']()


def server_source(head, digest):
    raw = prior.server_source(head, digest).replace('PG6890', LABEL).replace('pg6890', 'pg6930')
    tree = ast.parse(raw)
    if {n: sum(isinstance(x, ast.Constant) and type(x.value) is int and x.value == n for x in ast.walk(tree)) for n in (4213, 656)} != {4213: 2, 656: 1}:
        raise ValueError('two full test result/verdict counts and one suite count')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self, node):
            return ast.copy_location(ast.Constant({4213: 4222, 656: 660}[node.value]), node) if type(node.value) is int and node.value in (4213, 656) else node
    raw = ast.unparse(ast.fix_missing_locations(Counts().visit(tree)))
    if check(raw, '<grouped4222 original runner>'):
        raise ValueError('complete runner namespace')
    return raw


def driver_source(fresh):
    raw = prior.driver_source(fresh).replace(prior.SLOT, SLOT).replace('PG6890', LABEL).replace('pg6890', 'pg6930')
    before = "'tests': 4213, 'suites': 656, 'mainClasses': 1669"
    if raw.count(before) != 1:
        raise ValueError('one new full dimension tuple')
    raw = raw.replace(before, "'tests': 4222, 'suites': 660, 'mainClasses': 1669", 1)
    start, end = raw.index("'trigger': "), raw.index('}, sort_keys=True)', raw.index("'trigger': "))
    trigger = ('Necessary grouped Test-only qualification after legacy Receipt one, public observation values two, '
      'and Test DB ownership six new methods plus two constructor cleanup repairs since original4213. '
      'Every Production Main/old oracle/build/gate unchanged. Original red failures and same-oracle green21 first. '
      'One new-source4222/660 actual inventory, not 4213+9 PASS arithmetic. Six format/compile/null/static preserved. '
      'Only finite owned test fixtures; no actual Root/current/failedcohort/VM/DBBackup/key/permit/Unit/native/CHR action. '
      'Global100/F03/formal and canonical acceptance separate.')
    return raw[:start] + "'trigger': " + repr(trigger) + raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed source/operator first')
    guard(source)
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('all source/Test/gates fixed')
    qp = BASE / 'PG6928-db-fixture-green-original-v1/manifest.json'
    pp = W / 'pg6928-db-fixture-green-original-v1/manifest.safe.json'
    if QSHA is None or sha(qp) != QSHA:
        raise ValueError('freeze genuine green21 original first')
    q, p = [json.loads(x.read_bytes()) for x in (qp, pp)]
    if not (q['actualExit'] == 0 and q['source'] == source and (q['tests'], q['suites'], q['physicalMain']) == (21, 10, 1669) and sha(pp) == q['privateManifestSha256']):
        raise ValueError('genuine same-source green21/all8511669')
    if {x.relative_to(ROOT).as_posix(): sha(x) for x in ROOT.glob('src/*/src/main/java/**/*.java')} != p['allSourceHashes']:
        raise ValueError('all851 actual Main fixed')
    declared_inventory()


def definitions():
    scope = {**vars(base), 'LABEL': LABEL, 'SLOT': SLOT, 'original_source': original_source,
      'prerequisites': prerequisites, 'server_source': server_source, 'driver_source': driver_source}
    exec(compile(inspect.getsource(base.main).replace('pg6188', 'pg6930'), '<grouped4222 whole>', 'exec'), scope)
    return scope


if __name__ == '__main__':
    raise SystemExit(definitions()['main']())
