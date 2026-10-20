"""Normal fullWeb913 plus8 guards for22 expression changes, no deployed runtime operations."""
import json
import subprocess
from collections import Counter
import pg5966_api_sql_selected as previous
from pg5940_private_lock_compile import ROOT, BASE, sha
from pg5970_api_sql1021_public import SOURCE as OLD
from static_disposition_overlay import load

PLAN = BASE/'PG5974-web-form22-plan-v1/manifest.json'
PLAN_SHA = '9e6b5dc20ef4a767993b9f21725ab6b66200affc7810504e7d42c8a8cddc136b'


def inventory():
    if sha(PLAN) != PLAN_SHA:
        raise ValueError('original12 source/22 expression declaration')
    plan = json.loads(PLAN.read_bytes()); counts = Counter(r['class'] for r in plan['plannedWebCaseReferences'])
    cases = {**previous.engine.CASES, 'web': {name.removeprefix(previous.engine.PACKAGE) for name in counts}}
    for module, classes in cases.items():
        for relative in classes:
            name = previous.engine.PACKAGE+relative
            actual = previous.source_test_names(ROOT/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.', '/')+'.java'))
            if module != 'web':
                counts[name] = 3 if module == 'protocol' else 1
            if len(actual) != counts[name]:
                raise ValueError('actual unchanged Test source methods and fullWeb semantic inventory')
    if len(counts) != 149 or sum(counts.values()) != 921:
        raise ValueError('913 Web plus8 guards/149 exact suites')
    targets = {'web': [r['path'].split('/src/main/java/dev/codex/schubert/nk/')[1][:-5] for r in plan['sourcePlans']]}
    return cases, dict(counts), targets


def prerequisites():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed code/operator first')
    plan = json.loads(PLAN.read_bytes()); paths = {r['path'] for r in plan['sourcePlans']}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if set(subprocess.check_output(['git', 'diff', '--name-only', OLD, head, '--', 'src'], cwd=ROOT, text=True).splitlines()) != paths or len(paths) != 12 or any(sha(ROOT/r['path']) != r['predictedAfterSha256'] for r in plan['sourcePlans']):
        raise ValueError('only exact12 predicted Main changes;Test/oracle/resources unchanged')
    if subprocess.check_output(['git', 'diff', OLD, head, '--', 'pom.xml', '.mvn', 'mvnw', 'program/characterization', 'tools/quality/static'], cwd=ROOT):
        raise ValueError('same quality/build/compatibility gates')
    rows = load(BASE/'PG5972-sql-static-dispositions-v1/manifest.json', 'dac135f64f921f7b4391414eb5d76434f38fdb7c49ff3a78133ba132d70fd2c9', OLD)
    ids = {i for r in plan['sourcePlans'] for i in r['findingIds']}; selected = [r for r in rows if r['findingId'] in ids]
    if len(selected) != 22 or any(r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' for r in selected):
        raise ValueError('all22 genuinely unreviewed conditions before PG')


def runner_source():
    raw = previous.runner_source()
    for old, new in (('!=1021 or len(expected)!=175', '!=921 or len(expected)!=149'), ("'expectedTests':1021", "'expectedTests':921"),
                     ('len(target_counters)==16', 'len(target_counters)==12'),
                     ("'NORMAL_API_SQL_SELECTED1021',apiCases=1010,guardCases=11", "'NORMAL_WEB_FORM_SELECTED921',webCases=913,guardCases=8")):
        if raw.count(old) != 1:
            raise ValueError('one fullWeb921 current runner binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<normal Web913 plus8 guards>', 'exec')
    return raw


def main():
    prerequisites(); cases, counts, targets = inventory()
    scope = {**vars(previous.engine), 'SLOT': 'pg5976-web-form-selected921-v1', 'CASES': cases, 'COUNTS': counts, 'TARGETS': targets, 'test_names': previous.source_test_names}
    exec(compile(runner_source(), '<Web921 ordinary fixture PT>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
