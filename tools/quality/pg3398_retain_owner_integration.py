"""Necessary whole3707/543 integration for the new real retained-owner component."""
import argparse
import ast
import inspect
import json
import subprocess

from pyflakes.api import check

import pg3350_oracle_boundary_group_integration as template
import pg3372_maintenance_group_integration as previous
import pg3396_retain_owner_related as related
from pg3274_header_group_full_six import rebase

ROOT, SOURCE, W = template.ROOT, template.SOURCE, template.W
RENAMES = [('PG3350', 'PG3398'), ('pg3350', 'pg3398'), ('PG3352', 'PG3400'),
           ('pg3352', 'pg3400'), ('PG3354', 'PG3402'), ('pg3354', 'pg3402')]


def validate(snapshot):
    related.validate(snapshot)
    p = W / 'pg3396-retain-owner-related-v1'
    proof = json.loads((p / 'manifest.safe.json').read_bytes()); r = proof['result']
    related.base.require(proof['actualExit'] == r['actualExit'] == r['mavenExit'] == r['staticSixModules'] == r['FESFlakyNotRun'] == 0
                         and r['tests'] == 33 and r['suites'] == 8 and r['mainClasses'] == 1643
                         and r['allMainResourcesDebugSameBytes'] is True, 'genuine related33 allMain/format/static proof')
    related.base.require(not subprocess.check_output(['git', 'diff', r['sourceSnapshot'], snapshot, '--', *related.base.engine.SCOPE], cwd=ROOT),
                         'exact actually related-tested inputs')
    counters = r['modules']['batch']['retainMethodCounters']
    related.base.require(counters['LINE'] == {'missed': 0, 'covered': 3}
                         and counters['METHOD'] == {'missed': 0, 'covered': 1}, 'actual child retain method observation')


def adapted(function, overrides):
    raw = inspect.getsource(function)
    for old, new in RENAMES:
        raw = raw.replace(old, new)
    raw = raw.replace('3704', '3707').replace('542suite1643', '543suite1643')
    raw = raw.replace('3702 retained plus Media independent UTF8 max and Morning new interrupt; existing Exec/max oracles corrected; Main a9 unchanged;543suite1643',
                      '3706 retained plus one actual retained OS owner child and interrupt/post-lock contract; Main a9 unchanged;543suite1643')
    raw = raw.replace('BUG1291/1292 actual wrong implementation rejections and related44 require one whole3707; no Main/VM/sign/deploy/Root replay',
                      'one new retain caller-lock/interrupt/ownedTERM Test and actual related33 require one whole3707; Main/VM/sign/deploy/Root unchanged')
    namespace = {**template.__dict__, **overrides}
    exec(compile(raw, '<3707 function code before actual metadata binding>', 'exec'), namespace)
    return namespace[function.__name__]


def server_source(head, digest):
    # Distinct from historical nested builders' own c/d late-binding sentinels.
    h, d = 'f0' * 20, 'e1' * 32
    raw = previous.server_source(h, d)
    tree = ast.parse(rebase(raw, 'PG3372', 'PG3398', 3706, 3707, {h: head, d: digest}))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value == 542:
            node.value = 543
    return ast.unparse(ast.fix_missing_locations(tree))


def independent_server():
    tree = ast.parse(rebase(previous.independent_server(), 'PG3372', 'PG3398', 3706, 3707)); hits = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value == 542:
            node.value = 543
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == 'batch' and isinstance(value, ast.Tuple) and ast.literal_eval(value) == (1302, 173, 568):
                    value.elts = [ast.Constant(x) for x in (1303, 174, 568)]; hits += 1
    related.base.require(hits == 1, 'exact independent batch1303/174/568 tuple')
    raw = ast.unparse(ast.fix_missing_locations(tree))
    related.base.require(check(raw, '<independent3707>') == 0, 'complete independent namespace')
    return raw


def native_build(*args):
    full, original, capsule, *digests = args
    if any(full.get(k) != v for k, v in {
            'productionSource': SOURCE, 'tests': 3707, 'suites': 543, 'mainClasses': 1643,
            'FESFlakyNotRun': 0, 'staticSixModules': 0}.items()):
        raise ValueError('actual independent3707/543 full required')
    # BUG1300: transform template code only, never nested actual input dictionaries.
    old = json.loads((W / 'pg3374-oracle-boundary-full-qualified-v1/manifest.safe.json').read_bytes())
    related.base.require(old['actualExit'] == 0 and old['result']['tests'] == 3706
                         and old['result']['suites'] == 542, 'genuine old template authority')
    seed = previous.native_build(old['result'], original, capsule, *digests)
    tree = ast.parse(seed)
    bindings = {}
    body = []
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in ['FULL', 'ORIGINAL_FULL', 'CAPSULE_FULL']):
            bindings[node.targets[0].id] = ast.literal_eval(node.value)
        else:
            body.append(node)
    related.base.require(bindings == {'FULL': old['result'], 'ORIGINAL_FULL': original,
                                      'CAPSULE_FULL': capsule}, 'exact three removable data bindings')
    tree.body = body
    raw = rebase(ast.unparse(tree), 'PG3372', 'PG3398', 3706, 3707)
    raw = raw.replace('PG3376', 'PG3402').replace('PG3402-native-join-v1', 'PG3402-native-join-v2')
    tree = ast.parse(raw)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value == 542:
            node.value = 543
    raw = ast.unparse(ast.fix_missing_locations(tree))
    raw = ('FULL=' + repr(full) + '\nORIGINAL_FULL=' + repr(original)
           + '\nCAPSULE_FULL=' + repr(capsule) + '\n' + raw)
    related.base.require(check(raw, '<native3707/543 exact data after template>') == 0,
                         'complete native namespace')
    compile(raw, '<native3707/543 unchanged actual metadata>', 'exec')
    return raw


def native_summary(value):
    return adapted(template.native_summary, {})(value)


def whole():
    return adapted(template.whole, {'validate': validate, 'server_source': server_source})()


def qualify():
    return adapted(template.qualify, {'validate': validate, 'independent_server': independent_server})()


def native():
    raw = inspect.getsource(template.native)
    for old, new in RENAMES:
        raw = raw.replace(old, new)
    raw = raw.replace('pg3402-oracle-boundary-native-qualified-v1', 'pg3402-oracle-boundary-native-qualified-v2')
    namespace = {**template.__dict__, 'validate': validate, 'native_build': native_build,
                 'native_summary': native_summary}
    exec(compile(raw, '<native3707 new-only v2 transport>', 'exec'), namespace)
    return namespace['native']()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('action', choices=['whole', 'qualify', 'native'])
    raise SystemExit({'whole': whole, 'qualify': qualify, 'native': native}[parser.parse_args().action]())
