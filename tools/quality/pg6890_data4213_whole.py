"""One grouped new-source4213 regression, Main unchanged; never confirmation replay."""
import ast
import inspect
import json
import subprocess
import pg6862_web_deadline_whole as prior
import pg6188_native_ownership_whole as base
import pg6884_data_boundary_selected as selected
from pyflakes.api import check

ROOT, W, BASE, sha = base.ROOT, base.W, base.BASE, base.sha
LABEL = 'PG6890'
SLOT = 'pg6890-data4213-six-v1'
QSHA = '2814d78fe5ee54672c9a40a6aeaac151a125a75d3a68a4e48ab94390decaac78'


def original_source():
    source = json.loads((W / selected.SLOT / 'begin.safe.json').read_bytes())['source']
    selected.guard(source)
    return source


def declared_inventory():
    raw = inspect.getsource(base.declared_inventory)
    if raw.count('(4023, 605)') != 1:
        raise ValueError('one independent declaration tuple')
    scope = {**vars(base)}
    exec(compile(raw.replace('(4023, 605)', '(4213, 656)', 1), '<all4213 declarations>', 'exec'), scope)
    return scope['declared_inventory']()


def server_source(head, digest):
    raw = prior.server_source(head, digest).replace('PG6862', LABEL).replace('pg6862', 'pg6890')
    tree = ast.parse(raw)
    if {n: sum(isinstance(x, ast.Constant) and type(x.value) is int and x.value == n for x in ast.walk(tree)) for n in (4209, 653)} != {4209: 2, 653: 1}:
        raise ValueError('two verdict/result test and one suite dimension')
    class Counts(ast.NodeTransformer):
        def visit_Constant(self, node):
            return ast.copy_location(ast.Constant({4209: 4213, 653: 656}[node.value]), node) if type(node.value) is int and node.value in (4209, 653) else node
    raw = ast.unparse(ast.fix_missing_locations(Counts().visit(tree)))
    if check(raw, '<grouped4213 original runner>'):
        raise ValueError('complete runner namespace')
    return raw


def driver_source(fresh):
    raw = prior.driver_source(fresh).replace(prior.SLOT, SLOT).replace('PG6862', LABEL).replace('pg6862', 'pg6890')
    before = "'tests': 4209, 'suites': 653, 'mainClasses': 1669"
    if raw.count(before) != 1:
        raise ValueError('one exact new tuple')
    raw = raw.replace(before, "'tests': 4213, 'suites': 656, 'mainClasses': 1669", 1)
    start = raw.index("'trigger': ")
    end = raw.index('}, sort_keys=True)', start)
    trigger = ('Grouped qualification of four new independent Test methods in three new Test classes since original4209. '
      'Every Main/old oracle/build/gate unchanged. Independent retention full-byte deletion/255-256 boundary and public-data diagnostic/deadline invalid-argument no-IO checks. '
      'One necessary new-source4213/656 original whole closes pending same-source quality/counter/trace, not replay of old success or 4209+4 arithmetic. '
      'All six format-beforePT/compile-null-Werror/actual static, finite owned fixtures only. '
      'No actual Root/current/cohort/VM/DBBackup/key/permit/Unit/native/CHR operations. Global100/F03/formal remain separate.')
    return raw[:start] + "'trigger': " + repr(trigger) + raw[end:]


def prerequisites(source):
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean fixed source and operator first')
    selected.guard(source)
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('all source/Test/gates fixed')
    qp = BASE / 'PG6886-data-boundary-original-v1/manifest.json'
    pp = W / 'pg6886-data-boundary-original-v1/manifest.safe.json'
    if QSHA is None or sha(qp) != QSHA:
        raise ValueError('freeze genuine original42 first')
    q, p = [json.loads(x.read_bytes()) for x in (qp, pp)]
    if not (q['actualExit'] == 0 and q['source'] == source and (q['tests'], q['suites'], q['physicalMain']) == (42, 11, 1669) and sha(pp) == q['privateManifestSha256']):
        raise ValueError('genuine same-source selected42/all8511669')
    if {x.relative_to(ROOT).as_posix(): sha(x) for x in ROOT.glob('src/*/src/main/java/**/*.java')} != p['allSourceHashes']:
        raise ValueError('all actual851 Main fixed')
    declared_inventory()


def definitions():
    scope = {**vars(base), 'LABEL': LABEL, 'SLOT': SLOT, 'original_source': original_source, 'prerequisites': prerequisites, 'server_source': server_source, 'driver_source': driver_source}
    exec(compile(inspect.getsource(base.main).replace('pg6188', 'pg6890'), '<grouped4213 whole>', 'exec'), scope)
    return scope


if __name__ == '__main__':
    raise SystemExit(definitions()['main']())
