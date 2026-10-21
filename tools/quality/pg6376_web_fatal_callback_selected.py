"""One meaningful fatal-callback Test on unchanged Main; related runtime10 + baseline12."""
import json
import subprocess
import pg6360_web_startup_red as previous
from pg5940_private_lock_compile import ROOT, BASE, sha

OLD = 'da11b6296d1eee646e379c3f7ca569b8a24be7e6'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebLogApplicationRuntimeTest.java'


def inventory():
    base = previous.previous.previous.prior
    cases = {m: set(v) for m, v in base.engine.CASES.items()}
    cases['web'].add('web.bootstrap.WebLogApplicationRuntimeTest')
    counts = {base.engine.PACKAGE+n: len(base.source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((base.engine.PACKAGE+n).replace('.', '/')+'.java')))
              for m, names in cases.items() for n in names}
    if (sum(counts.values()), len(counts)) != (22, 8):
        raise ValueError('actual runtime10 + original baseline12/8 suites, no old54 PASS arithmetic')
    return cases, counts


def runner():
    raw = previous.runner()
    for before, after in (
        ('runner_source(20,10,target_count=16)', 'runner_source(22,8,target_count=15)'),
        ('pg6360-web-startup-red-v1', 'pg6376-web-fatal-callback-selected-v1'),
        ('def run_red():', 'def run_selected():'),
        ("scope['targets']['web'].extend(('web/bootstrap/WebProcessLifetime','web/bootstrap/WebLogApplicationRuntime'))",
         "scope['targets']['web'].append('web/bootstrap/WebLogApplicationRuntime')")):
        if raw.count(before) != 1:
            raise ValueError('one explicit22 fatal callback binding '+before)
        raw = raw.replace(before, after, 1)
    return raw


def guard_source(source):
    if subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines() != [TEST]:
        raise ValueError('one new Runtime Test only, every Main and other oracle fixed')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('existing gates/Current unchanged')


def prior54():
    path = BASE/'PG6372-web-startup-retry-qualification-v1/manifest.json'
    if sha(path) != '2a9e57d2a1da1ca2520af978526b0fc9b5f1b1081678f9dfe6481823e1f494d3':
        raise ValueError('immutable original54 qualification')
    value = json.loads(path.read_bytes())
    if not (value['source'] == OLD and value['actualExit'] == 0 and (value['tests'], value['suites']) == (54, 15)):
        raise ValueError('genuine original54 only, no repeat')


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed Test/operator first')
    prior54(); guard_source('HEAD')
    scope = {**vars(previous.previous.previous.prior), 'inventory': inventory}
    exec(compile(runner(), '<new22 ordinary fatal callback>', 'exec'), scope)
    return scope['run_selected']()


if __name__ == '__main__':
    raise SystemExit(main())
