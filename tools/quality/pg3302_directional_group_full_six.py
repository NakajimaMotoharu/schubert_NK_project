"""One necessary integration of Protocol directional oracle fixes; Main a9 unchanged."""
import hashlib
import inspect
import json
import subprocess

import pg2798_jdbc_null_fixed_full_six as engine
import pg3274_header_group_full_six as previous

ROOT, SOURCE, W = previous.ROOT, previous.SOURCE, previous.W
CHANGED = {
    'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/codec/PayloadGoldenVectorTest.java',
    'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalogTest.java',
    'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/IndependentNamedFieldOracle.java',
    'src/schubert-nk-protocol/src/test/resources/protocol/named-accessors-independent.tsv'}


def validate(snapshot):
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT)
    old = json.loads((W / 'pg3276-header-group-full-qualified-v1/manifest.safe.json').read_bytes())
    related = json.loads((W / 'pg3300-directional-protocol-qualified-v1/manifest.safe.json').read_bytes())
    if old['actualExit'] != 0 or old['result']['tests'] != 3701 or old['result']['productionSource'] != SOURCE:
        raise ValueError('actual old3701 preserved required')
    changed = set(git('diff', '--name-only', old['result']['sourceSnapshot'], snapshot, '--', *engine.SCOPE).decode().splitlines())
    if changed != CHANGED:
        raise ValueError('exact four Test/helper/independent resource changes and no Main/settings required')
    result = related['result']
    if related['actualExit'] != 0 or any(result[k] != v for k, v in {'actualMavenExit': 0, 'originalWrapperExit': 0, 'tests': 85, 'suites': 17, 'mainClasses': 174, 'staticIssues': 0, 'FESFlakyNotRun': 0, 'productionSource': SOURCE}.items()):
        raise ValueError('actual independently qualified Protocol85 required')
    if any(result['coverage'][k]['missed'] != 0 for k in ['LINE', 'METHOD', 'CLASS', 'BRANCH']):
        raise ValueError('all Protocol counters100 required')
    for name in CHANGED:
        if hashlib.sha256(git('show', snapshot + ':' + name)).digest() != hashlib.sha256(git('show', result['testSource'] + ':' + name)).digest():
            raise ValueError('exact actual Protocol85 Test/resource bytes required')
    tests = 'src/schubert-nk-protocol/src/test/java/dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalogTest.java'
    if git('show', snapshot + ':' + tests).decode().count('@Test\n') != 6 or git('show', old['result']['sourceSnapshot'] + ':' + tests).decode().count('@Test\n') != 5:
        raise ValueError('one new actual JUnit method, no new suite required')


def server_source(head, digest):
    raw = previous.server_source(head, digest)
    return previous.rebase(raw, 'PG3274', 'PG3302', 3701, 3702)


def main():
    raw = inspect.getsource(engine.main).replace('PG2798', 'PG3302').replace('pg2798', 'pg3302').replace('3680', '3702')
    raw = raw.replace('3673 retained plus five independently real-DB Session methods and two owner-admission methods; changed JDBC Main;542suite1643',
                      '3701 retained plus one independent69type-295component-79optional method and existing concurrent fixed-byte oracle; unchanged a9 Main;542suite1643')
    raw = raw.replace('BUG1251/YKT1017 changed JDBC null-resource Main and seven grouped tests require one fresh all-source/static regression; Source042 native not portable',
                      'BUG1285/1288 two independently demonstrated oracle gaps; actual Protocol85 and two mutation rejections require one whole3702; no VM/sign/deploy/Root replay')
    namespace = {**engine.__dict__, 'SOURCE': SOURCE, 'validate': validate, 'server_source': server_source}
    exec(compile(raw, '<one directional whole3702>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())
