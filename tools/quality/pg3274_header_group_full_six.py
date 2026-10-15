"""One necessary Header Test-only integration, 3701; immutable Main a9.

Rebase numeric code literals, never SHA strings. Bind archive/head only AFTER
legacy template transformations. BUG1281 prevention; no runtime replay.
"""
import ast
import hashlib
import inspect
import json
import re
import subprocess
from pg1446_current_cold_stage import W
import pg2798_jdbc_null_fixed_full_six as engine
import pg3258_statement_group_full_six as previous

SOURCE = previous.SOURCE
ROOT = previous.ROOT
TEST = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/header/HeaderModelTest.java'


def rebase(raw, old_run, new_run, old_tests, new_tests, bindings=None):
    bindings = bindings or {}

    class Literals(ast.NodeTransformer):
        def visit_Constant(self, node):
            value = node.value
            if type(value) is int and value == old_tests:
                return ast.copy_location(ast.Constant(new_tests), node)
            if isinstance(value, str):
                if value in bindings:
                    value = bindings[value]
                elif not re.fullmatch('[a-f0-9]{40,64}', value):
                    value = value.replace(old_run, new_run).replace(str(old_tests), str(new_tests))
                return ast.copy_location(ast.Constant(value), node)
            return node

    tree = ast.fix_missing_locations(Literals().visit(ast.parse(raw)))
    compile(tree, '<rebased code literals without digest rewriting>', 'exec')
    return ast.unparse(tree)


def validate(snapshot):
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT)
    old = json.loads((W / 'pg3260-statement-group-full-qualified-v1/manifest.safe.json').read_bytes())
    proof = json.loads((W / 'pg3270-header-protocol-qualified-v1/manifest.safe.json').read_bytes())
    if old['actualExit'] != 0 or old['result']['tests'] != 3699 or old['result']['productionSource'] != SOURCE:
        raise ValueError('actual qualified3699 baseline required')
    changed = set(git('diff', '--name-only', old['result']['sourceSnapshot'], snapshot, '--', *engine.SCOPE).decode().splitlines())
    if changed != {TEST}:
        raise ValueError('exact Header Test-only change; all Main/settings/resources unchanged required')
    result = proof['result']
    if proof['actualExit'] != 0 or any(result[k] != v for k, v in {'actualMavenExit': 0, 'originalWrapperExit': 1, 'tests': 84, 'suites': 17, 'mainClasses': 174, 'headerTests': 7, 'staticIssues': 0, 'FESFlakyNotRun': 0, 'productionSource': SOURCE}.items()):
        raise ValueError('independent actual Protocol84 and preserved wrapper1 required')
    if any(result['coverage'][k]['missed'] != 0 for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']):
        raise ValueError('all Protocol four counters100 required')
    current = git('show', snapshot + ':' + TEST)
    if hashlib.sha256(current).digest() != hashlib.sha256(git('show', result['testSource'] + ':' + TEST)).digest():
        raise ValueError('Header byte identical to actual independently qualified84 source required')
    before = git('show', old['result']['sourceSnapshot'] + ':' + TEST)
    if current.decode().count('@Test\n') != 7 or before.decode().count('@Test\n') != 5:
        raise ValueError('exactly two new actual methods, no removed test required')


def server_source(head, digest):
    # No real digest enters the long historical replace chain.
    # Legacy builders validate SHA syntax before constructing their payload.
    # Repeated c/d are valid hex but contain no changing numeric count fragment.
    head_marker = 'c' * 40
    digest_marker = 'd' * 64
    raw = previous.server_source(head_marker, digest_marker)
    for marker in [head_marker, digest_marker]:
        if marker not in raw:
            raise ValueError('late-bound fixed head/archive marker required')
    raw = rebase(raw, 'PG3258', 'PG3274', 3699, 3701, {head_marker: head, digest_marker: digest})
    if head_marker in raw or digest_marker in raw:
        raise ValueError('all archive/source fields bound after numeric transformations required')
    return raw


def main():
    raw = inspect.getsource(engine.main).replace('PG2798', 'PG3274').replace('pg2798', 'pg3274').replace('3680', '3701')
    raw = raw.replace('3673 retained plus five independently real-DB Session methods and two owner-admission methods; changed JDBC Main;542suite1643', '3699 retained plus Header two actual methods/one Test file and independent three mutation rejections; unchanged a9 Main;542suite1643')
    raw = raw.replace('BUG1251/YKT1017 changed JDBC null-resource Main and seven grouped tests require one fresh all-source/static regression; Source042 native not portable', 'BUG1279/YKT1045 Header oracle correction and two actual methods require one3701 integration; no Main/VM/sign/deploy/Root replay')
    ns = {**engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server_source': server_source}
    exec(compile(raw, '<one necessary Header3701 transport>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
