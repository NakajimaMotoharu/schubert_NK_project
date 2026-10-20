"""PG-D453 ordinary affected965/162; finite local fixtures, never current/VM recovery."""
import inspect
import subprocess
import pg5732_enum48_selected as engine
from pg5966_api_sql_selected import source_test_names
from pg5984_web_form_selected_v2 import node_environment

ROOT = engine.ROOT
OLD = 'bc0cac2f6a7055b938f581e8cd163db398f8a656'
MAIN = (
    'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient.java',
    'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/WebBrokerContexts.java')
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/ArtemisManagementEncoderBoundaryTest.java'


def inventory():
    cases = {m: set(v) for m, v in engine.CASES.items()}
    for module, pattern in (('web', '**/*Test.java'), ('batch', 'dev/codex/schubert/nk/batch/mq/*Test.java')):
        root = ROOT/('src/schubert-nk-'+module+'/src/test/java')
        cases[module] |= {p.relative_to(root).as_posix()[:-5].replace('/', '.').removeprefix(engine.PACKAGE) for p in root.glob(pattern)}
    counts = {engine.PACKAGE+c: len(source_test_names(ROOT/('src/schubert-nk-'+m+'/src/test/java')/((engine.PACKAGE+c).replace('.', '/')+'.java'))) for m, cs in cases.items() for c in cs}
    if (len(counts), sum(counts.values())) != (162, 965):
        raise ValueError('declared Web913/batch46/other6,all162 actual named suites')
    targets = {'batch': ['batch/mq/ArtemisManagementReadinessClient'], 'web': ['web/messaging/WebBrokerContexts']}
    return cases, counts, targets


def runner_source():
    raw = inspect.getsource(engine.main)
    changes = {
        "count=3 if module=='protocol'else 4 if module=='web'else 1": 'count=COUNTS[name]',
        'sum(map(len,expected.values()))!=12 or len(expected)!=7': 'sum(map(len,expected.values()))!=965 or len(expected)!=162',
        "'expectedTests':12": "'expectedTests':965",
        "method=case.get('name','').removesuffix('()')": "method=case.get('name','').split('(',1)[0]",
        'len(physical)==1664': 'len(physical)==1667',
        "os.pathsep+os.environ['PATH'],MAVEN_OPTS": 'os.pathsep+NODE_PATH,MAVEN_OPTS',
        "'actualExit':next((v for v in exits if v),0)": "'actualExit':0 if done else 1,'mavenActualExit':next((v for v in exits if v),0)",
        "target100=len(target_counters)==14 and all(all(c[k]['missed']==0 and c[k]['covered']>0 for k in('LINE','METHOD','CLASS'))and c['BRANCH']['missed']==0 for c in target_counters.values())": "target100=len(target_counters)==2 and all(c[k]['missed']==0 and c[k]['covered']>0 for c in target_counters.values() for k in('LINE','METHOD','CLASS','BRANCH'))",
    }
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one explicit affected965 runner binding: '+old)
        raw = raw.replace(old, new, 1)
    compile(raw, '<affected965 true XML/counters>', 'exec')
    return raw


def main():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed operator/source before PT')
    changed = subprocess.check_output(['git', 'diff', '--name-only', OLD, 'HEAD', '--', 'src'], cwd=ROOT, text=True).splitlines()
    if set(changed) != {*MAIN, TEST} or subprocess.check_output(['git', 'diff', OLD, 'HEAD', '--', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('exact two Main/three new Test methods;unchanged build/static/Current gates')
    # Only ordinary compile/package/JUnit in a new owned snapshot. No remote/privileged operation.
    cases, counts, targets = inventory()
    scope = {**vars(engine), 'SLOT': 'pg6026-error-boundary-selected965-v1', 'NODE_PATH': node_environment(),
             'CASES': cases, 'COUNTS': counts, 'TARGETS': targets, 'test_names': source_test_names}
    exec(compile(runner_source(), '<approved finite affected fixtures>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
