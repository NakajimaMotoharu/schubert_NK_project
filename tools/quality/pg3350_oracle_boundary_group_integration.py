"""One necessary integration of four Test-only changes, whole3704/542/1643/native28."""
import argparse
import ast
import inspect
import json
import subprocess

from pyflakes.api import check

import pg3330_stream_group_integration as prior
import pg3348_related_boundary_group as related
import pg3252_cycle_group_native_rejoin as native_base
from pg3274_header_group_full_six import rebase

ROOT, SOURCE, W, engine = prior.ROOT, prior.SOURCE, prior.W, prior.engine


def validate_tests(snapshot):
    full = related.validate(snapshot)
    for path, count in [
        ('src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/file/MediaDescriptorValidatorTest.java', 7),
        ('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningStopPassTest.java', 10)]:
        raw = subprocess.check_output(['git', 'show', snapshot + ':' + path], cwd=ROOT, text=True)
        related.require(raw.count('@Test\n') == count, 'exact one new method in each existing suite')
    return full


def validate(snapshot):
    validate_tests(snapshot)
    proof = json.loads((W / 'pg3348-related-boundary-group-v1/manifest.safe.json').read_bytes())
    r = proof['result']
    related.require(proof['actualExit'] == r['actualExit'] == r['mavenExit'] == r['staticSixModules'] == r['FESFlakyNotRun'] == 0
                    and r['productionSource'] == SOURCE and r['tests'] == 44 and r['suites'] == 7
                    and r['mainClasses'] == 1643 and r['allMainResourcesDebugSameBytes'] is True, 'actual44/7/staticSix0/all1643 same-byte required')
    related.require(not subprocess.check_output(['git', 'diff', r['sourceSnapshot'], snapshot, '--', *engine.SCOPE], cwd=ROOT), 'exact actually related-tested all inputs required')


def server_source(head, digest):
    return rebase(prior.server_source(head, digest), 'PG3330', 'PG3350', 3702, 3704)


def independent_server():
    tree = ast.parse(rebase(prior.independent_server(), 'PG3330', 'PG3350', 3702, 3704))
    expected = {'protocol': ((85, 17, 174), (86, 17, 174)), 'batch': ((1299, 173, 568), (1300, 173, 568))}
    hits = dict.fromkeys(expected, 0)
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value in expected and isinstance(value, ast.Tuple):
                    old, new = expected[key.value]
                    if ast.literal_eval(value) == old:
                        value.elts = [ast.Constant(x) for x in new]; hits[key.value] += 1
    related.require(all(n == 1 for n in hits.values()), 'two exact independent changed-module tuples')
    tree = ast.fix_missing_locations(tree); compile(tree, '<independent whole3704>', 'exec')
    raw = ast.unparse(tree)
    related.require(check(raw, '<independent3704 namespace>') == 0, 'complete namespace required')
    return raw


def native_build(*args):
    # Rebase template code BEFORE actual metadata is embedded. Historical wrappers
    # require their own old test count and must not rewrite any actual input counter.
    function = rebase(inspect.getsource(native_base.build), 'PG3248', 'PG3350', 3697, 3704).replace('PG3252', 'PG3354')
    namespace = dict(native_base.__dict__)
    exec(compile(function, '<native28 new count before actual data binding>', 'exec'), namespace)
    raw = namespace['build'](*args)
    tree = ast.parse(raw)
    bindings = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body
                if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id in ['FULL', 'ORIGINAL_FULL', 'CAPSULE_FULL']}
    related.require(bindings == {'FULL': args[0], 'ORIGINAL_FULL': args[1], 'CAPSULE_FULL': args[2]}, 'all actual metadata bound unchanged after template transformations')
    raw = ast.unparse(tree)
    related.require(check(raw, '<whole3704/native28 namespace>') == 0, 'complete native namespace required')
    return raw


def native_summary(value):
    r = value['result']
    expected = {'actualExit': 0, 'qualifiedFullTests': 3704, 'qualifiedNativeStreams': 28,
                'distinctSessions': 28, 'mainClassesIdentical': 1643,
                'allResourceMetaMembersIdentical': 79, 'productionSource': SOURCE}
    related.require(value['actualExit'] == 0 and all(r[k] == v for k, v in expected.items()), 'genuine current3704/native28 result required')
    return {'actualExit': 0, 'tests': r['qualifiedFullTests'], 'streams': r['qualifiedNativeStreams'],
            'sameMain': r['mainClassesIdentical'], 'sameResources': r['allResourceMetaMembersIdentical'],
            'remaining': {k: sum(v[k]['missed'] for v in r['moduleCounters'].values()) for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']},
            'manifestSha256': value['manifestSha256'], 'formalAccepted': False}


def whole():
    raw = inspect.getsource(engine.main).replace('PG2798', 'PG3350').replace('pg2798', 'pg3350').replace('3680', '3704')
    raw = raw.replace('3673 retained plus five independently real-DB Session methods and two owner-admission methods; changed JDBC Main;542suite1643',
                      '3702 retained plus Media independent UTF8 max and Morning new interrupt; existing Exec/max oracles corrected; Main a9 unchanged;542suite1643')
    raw = raw.replace('BUG1251/YKT1017 changed JDBC null-resource Main and seven grouped tests require one fresh all-source/static regression; Source042 native not portable',
                      'BUG1291/1292 actual wrong implementation rejections and related44 require one whole3704; no Main/VM/sign/deploy/Root replay')
    namespace = {**engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server_source': server_source}
    exec(compile(raw, '<necessary whole3704 transport>', 'exec'), namespace)
    return namespace['main']()


def qualify():
    base = prior.prior_independent.engine
    raw = inspect.getsource(base.main).replace('pg2800-jdbc-null-fixed-full-qualified-v1', 'pg3352-oracle-boundary-full-qualified-v1').replace('pg2798-server-six-v1', 'pg3350-server-six-v1').replace('PG2798', 'PG3350')
    namespace = {**base.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server': independent_server}
    exec(compile(raw, '<independent whole3704 transport>', 'exec'), namespace)
    return namespace['main']()


def native():
    base = prior.prior_native.previous
    raw = inspect.getsource(base.main).replace('pg3276-header-group-full-qualified-v1', 'pg3352-oracle-boundary-full-qualified-v1').replace('pg3278-header-group-native-qualified-v1', 'pg3354-oracle-boundary-native-qualified-v1')
    namespace = {**base.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'build': native_build, 'public_summary': native_summary}
    exec(compile(raw, '<whole3704/native28 transport>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['whole', 'qualify', 'native'])
    raise SystemExit({'whole': whole, 'qualify': qualify, 'native': native}[parser.parse_args().action]())
