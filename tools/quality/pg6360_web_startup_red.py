"""New20 purpose-red on all unchanged Main; dummy startup owner only, never an actual runtime."""
import json
import subprocess
import pg6348_web_lifetime_selected as previous
from pg5940_private_lock_compile import BASE, sha

ROOT = previous.ROOT
OLD = '3deda4c271af68172b2d060c18c56e27a1968d2a'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebStartupRetentionTest.java'


def inventory():
    cases, _ = previous.inventory()
    cases['web'].add('web.bootstrap.WebStartupRetentionTest')
    base = previous.previous.prior
    counts = {base.engine.PACKAGE+n: len(base.source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((base.engine.PACKAGE+n).replace('.', '/')+'.java')))
              for m, names in cases.items() for n in names}
    if (sum(counts.values()), len(counts)) != (20, 10):
        raise ValueError('actual original18 plus two independently declared tests, not five child modes as extra tests')
    return cases, counts


def runner():
    raw = previous.runner()
    for before, after in (
        ('runner_source(18,9,target_count=15)', 'runner_source(20,10,target_count=16)'),
        ('pg6348-web-lifetime-selected-v1', 'pg6360-web-startup-red-v1'),
        ('def run_selected():', 'def run_red():'),
        ("scope['targets']['web'].append('web/bootstrap/WebProcessLifetime')",
         "scope['targets']['web'].extend(('web/bootstrap/WebProcessLifetime','web/bootstrap/WebLogApplicationRuntime'))")):
        if raw.count(before) != 1:
            raise ValueError('one explicit new20 reproduction binding '+before)
        raw = raw.replace(before, after, 1)
    return raw


def guard_source(source):
    if subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [TEST]:
        raise ValueError('one new Test only, all Main and prior independent oracles unchanged')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('build/static/Current fixed')


def prior18():
    path = BASE/'PG6350-web-lifetime-qualification-v1/manifest.json'
    if sha(path) != 'fb7279b4a9133049b535475703d2eb52f76c7f9c2c5fc040a2c25369fb7d3b71':
        raise ValueError('immutable original18 qualification before new Test')
    value = json.loads(path.read_bytes())
    if not (value['source'] == OLD and value['actualExit'] == 0 and (value['tests'], value['suites']) == (18, 9) and value['changedPhysical'] == []):
        raise ValueError('genuine prior18/all Main, never replay its PT')


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed independent Test/operator first')
    prior18(); guard_source('HEAD')
    scope = {**vars(previous.previous.prior), 'inventory': inventory}
    exec(compile(runner(), '<new-only dummy startup dependency reproduction>', 'exec'), scope)
    return scope['run_red']()


if __name__ == '__main__':
    raise SystemExit(main())
