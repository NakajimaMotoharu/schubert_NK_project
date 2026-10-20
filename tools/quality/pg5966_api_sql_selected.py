"""Normal fullAPI1010 plus11 guards for exact21 constant expressions; no deployed operations."""
import inspect
import json
import re
import subprocess
from collections import Counter
import pg5732_enum48_selected as engine
from pg5940_private_lock_compile import ROOT, BASE, sha
from static_disposition_overlay import load

OLD = '288062f3960a0a50ec82685da3b407f0c9e2934e'
PLAN = BASE/'PG5964-api-sql21-plan-v1/manifest.json'
PLAN_SHA = '56b461725810f8a706b0c1e9dd092dabf68f631a99593462bc01b7ca9784c2b8'


def ordinary_names(text):
    # Lexical source inventory only. Annotation strings/comments/text blocks cannot add Tests
    # or terminate nested annotation parentheses. No source is executed or rewritten here.
    token = re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_$][A-Za-z0-9_$]*|[^\s]')
    tokens = []
    for m in token.finditer(text):
        value = m.group()
        if value.startswith(('//', '/*')):
            continue
        tokens.append('LITERAL' if value.startswith(('"', "'")) else value)
    def annotation(at):
        end = at+1
        while end+1 < len(tokens) and tokens[end+1] == '.':
            end += 2
        name = tokens[end]; end += 1
        if end < len(tokens) and tokens[end] == '(':
            depth = 1; end += 1
            while end < len(tokens) and depth:
                if tokens[end] == '(':
                    depth += 1
                elif tokens[end] == ')':
                    depth -= 1
                end += 1
            if depth:
                raise ValueError('annotation arguments must close')
        return name, end
    names = []
    for i, value in enumerate(tokens):
        if value != '@':
            continue
        name, end = annotation(i)
        if name in ('Disabled', 'ParameterizedTest', 'RepeatedTest', 'TestFactory', 'Nested'):
            raise ValueError('explicit ordinary unskipped Test inventory only')
        if name != 'Test':
            continue
        while end < len(tokens) and tokens[end] == '@':
            _name, end = annotation(end)
        while end < len(tokens) and tokens[end] in ('public', 'final'):
            end += 1
        if tokens[end] != 'void' or re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*', tokens[end+1]) is None or tokens[end+2] != '(':
            raise ValueError('one ordinary named void method for each actual Test annotation')
        names.append(tokens[end+1])
    if not names or len(set(names)) != len(names):
        raise ValueError('nonempty unique source method identities')
    return set(names)


def source_test_names(path):
    return ordinary_names(path.read_text())


def inventory():
    if sha(PLAN) != PLAN_SHA:
        raise ValueError('immutable21/16 source declaration')
    plan = json.loads(PLAN.read_bytes()); counts = Counter(r['class'] for r in plan['plannedApiCaseReferences'])
    cases = {**engine.CASES, 'api': {name.removeprefix(engine.PACKAGE) for name in counts}}
    for module, classes in cases.items():
        for relative in classes:
            name = engine.PACKAGE+relative
            actual = source_test_names(ROOT/('src/schubert-nk-'+module+'/src/test/java')/(name.replace('.', '/')+'.java'))
            if module != 'api':
                counts[name] = 3 if module == 'protocol' else 4 if module == 'web' else 1
            if len(actual) != counts[name]:
                raise ValueError('all actual unchanged named Test source inventories')
    if len(counts) != 175 or sum(counts.values()) != 1021:
        raise ValueError('full API1010/169 plus six-module guards11/6 only')
    targets = {'api': [r['path'].split('/src/main/java/dev/codex/schubert/nk/')[1][:-5] for r in plan['sourcePlans']]}
    return cases, dict(counts), targets


def prerequisites():
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT):
        raise ValueError('clean committed code/operator before normal PT')
    plan = json.loads(PLAN.read_bytes()); declared = {r['path'] for r in plan['sourcePlans']}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    changed = subprocess.check_output(['git', 'diff', '--name-only', OLD, head, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if set(changed) != declared or any(sha(ROOT/r['path']) != r['predictedAfterSha256'] for r in plan['sourcePlans']):
        raise ValueError('only16 exact declared Main source changes; Test/oracle unchanged')
    if subprocess.check_output(['git', 'diff', OLD, head, '--', 'pom.xml', '.mvn', 'mvnw', 'program/characterization', 'tools/quality/static'], cwd=ROOT):
        raise ValueError('build/quality/compatibility gates unchanged')
    prior = load(BASE/'PG5950-current-static3973-v1/manifest.json', '4603ed2df17049305c082ca233c9979702d898aa0fd76305ce4e0b1cba48675f', OLD)
    ids = {i for r in plan['sourcePlans'] for i in r['findingIds']}
    chosen = [r for r in prior if r['findingId'] in ids]
    if len(chosen) != 21 or any(r['status'] != 'NOT_REVIEWED_CURRENT_SOURCE' for r in chosen):
        raise ValueError('no already-classified warning as new PG')


def runner_source():
    raw = inspect.getsource(engine.main)
    changes = {
        "count=3 if module=='protocol'else 4 if module=='web'else 1": 'count=COUNTS[name]',
        'sum(map(len,expected.values()))!=12 or len(expected)!=7': 'sum(map(len,expected.values()))!=1021 or len(expected)!=175',
        "'expectedTests':12": "'expectedTests':1021",
        "method=case.get('name','').removesuffix('()')": "method=case.get('name','').split('(',1)[0]",
        'len(physical)==1664': 'len(physical)==1666',
        "'actualExit':next((v for v in exits if v),0)": "'actualExit':0 if done else 1,'mavenActualExit':next((v for v in exits if v),0)",
        "target100=len(target_counters)==14 and all(all(c[k]['missed']==0 and c[k]['covered']>0 for k in('LINE','METHOD','CLASS'))and c['BRANCH']['missed']==0 for c in target_counters.values())": "target100=len(target_counters)==16 and all(c[k]['missed']==0 and c[k]['covered']>0 for c in target_counters.values() for k in('LINE','METHOD','CLASS','BRANCH'))",
        "with(out/'manifest.safe.json').open('x')as f:": "value.update(executionKind='NORMAL_API_SQL_SELECTED1021',apiCases=1010,guardCases=11,noDeployedRuntimeOperation=True,oldSuccessImported=False)\n    with(out/'manifest.safe.json').open('x')as f:"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one complete current1021 selected runner binding')
        raw = raw.replace(old, new, 1)
    compile(raw, '<normal1010 API plus11 guard>', 'exec')
    return raw


def main():
    prerequisites(); cases, counts, targets = inventory()
    scope = {**vars(engine), 'SLOT': 'pg5966-api-sql-selected1021-v1', 'CASES': cases, 'COUNTS': counts, 'TARGETS': targets, 'test_names': source_test_names}
    exec(compile(runner_source(), '<normal API SQL1010 plus11guard>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
