"""All851/1666/ABI and unsuppressed raw42 proof after ordinary Web24/921; never executes PT."""
import hashlib
import json
import subprocess
from collections import Counter
import pg5978_web_form_static as previous
from pg5940_private_lock_compile import ROOT, W, TC, sha
from pg5990_web_contract_selected import PLAN, PLAN_SHA, OLD


def plan():
    if sha(PLAN) != PLAN_SHA:
        raise ValueError('immutable24/42 Web declaration')
    return json.loads(PLAN.read_bytes())


def validate_source(source, root):
    data = plan(); paths = {r['path'] for r in data['sourcePlans']}
    if len(paths) != 24 or set(subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()) != paths:
        raise ValueError('only24 declared Main source changes')
    if subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'program/characterization', 'tools/quality/static'], cwd=ROOT):
        raise ValueError('no Test/oracle/template/SQL/quality gate change')
    before = json.loads((W/'pg5978-web-form-static-v1/manifest.safe.json').read_bytes()); expected = dict(before['allSourceHashes'])
    if before['source'] != OLD or before['actualExit'] != 0:
        raise ValueError('actual same-source baseline851/1666')
    for row in data['sourcePlans']:
        if expected[row['path']] != row['beforeSha256']:
            raise ValueError('exact current original source')
        expected[row['path']] = row['predictedAfterSha256']
    actual = {p.relative_to(root).as_posix(): sha(p) for p in root.glob('src/*/src/main/java/**/*.java')}
    if actual != expected or len(actual) != 851:
        raise ValueError('all851 source and24 predicted changes fixed')
    return actual


def physical_changes(old, new):
    owners = {'web:'+r['path'].split('/src/main/java/')[1][:-5]+'.class' for r in plan()['sourcePlans']}
    changed = {k for k in old.keys() & new.keys() if old[k] != new[k]}
    if len(old) != 1666 or set(new) != set(old) or not owners <= changed or any(not any(k == o or k.startswith(o[:-6]+'$') for o in owners) for k in changed):
        raise ValueError('all1666/24 required outer; only those nested/debug changes allowed')
    return sorted(changed)


def expected_rules(before, actual):
    expected = Counter(before); expected['AvoidLiteralsInIfCondition'] -= 42
    if expected != Counter(actual) or expected['AvoidLiteralsInIfCondition'] < 0:
        raise ValueError('exact42 raw literal removal only; no exclusions/lost other diagnostics')


def debug_proof(before, current, changed):
    owners = {'web:'+r['path'].split('/src/main/java/')[1][:-5]+'.class' for r in plan()['sourcePlans']}; nested = sorted(set(changed)-owners)
    if not nested:
        return dict(classes=[], bytecodeAndPrivateDescriptorsEqual=True, disassemblySha256=None)
    names = [k.split(':', 1)[1][:-6].replace('/', '.') for k in nested]
    def disassemble(root):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-c', '-p', '-s', '-classpath', str(root/'src/schubert-nk-web/target/classes'), *names])
    a, b = disassemble(before), disassemble(current)
    if a != b:
        raise ValueError('unexpected nested executable/descriptor changes; keep unresolved')
    return dict(classes=nested, bytecodeAndPrivateDescriptorsEqual=True, disassemblySha256=hashlib.sha256(b).hexdigest())


def runner_source():
    raw = previous.runner_source()
    changes = {
        "'pg5968-api-sql-static-v1/manifest.safe.json'": "'pg5978-web-form-static-v1/manifest.safe.json'",
        "'PG5968-api-sql-static-v1/manifest.json'": "'PG5978-web-form-static-v1/manifest.json'",
        'f888e1a0817b7fc77521410df29c89c8fa95a7a3d5d4b3e17196d6be09e0d454': '61143deb9c99e713be46e913ba885e700125268f0e069535d3a143f59d4404c9',
        'pg5966-api-sql-selected1021-v1/source': 'pg5984-web-form-selected921-v2/source',
        'pg5968-api-sql-static-v1/aux-classpath.txt': 'pg5978-web-form-static-v1/aux-classpath.txt',
        'rawDiagnosticsRemovedByPg=22': 'rawDiagnosticsRemovedByPg=42',
        "target = BASE/'PG5978-web-form-static-v1'": "target = BASE/'PG5992-web-contract-static-v1'"}
    for old,new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one exact Web42 static binding: '+old)
        raw = raw.replace(old,new,1)
    compile(raw,'<Web42 all851 static>','exec')
    return raw


def main():
    scope = {**vars(previous.previous.previous), 'OLD': OLD, 'COMPILE': 'pg5990-web-contract-selected921-v1', 'SLOT': 'pg5992-web-contract-static-v1',
             'plan': plan, 'validate_source': validate_source, 'physical_changes': physical_changes, 'expected_rules': expected_rules, 'debug_proof': debug_proof}
    exec(compile(runner_source(), '<Web42 all-source static>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
