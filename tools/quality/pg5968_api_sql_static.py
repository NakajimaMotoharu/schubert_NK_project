"""Independent16 source/whole1666/publicABI/raw21 static after normal1021; no PT invocation."""
import inspect
import hashlib
import json
import subprocess
from collections import Counter
import pg5942_private_lock_static as previous
from pg5940_private_lock_compile import ROOT, W, TC, sha
from pg5966_api_sql_selected import PLAN, PLAN_SHA, OLD


def plan():
    if sha(PLAN) != PLAN_SHA:
        raise ValueError('original16 source/21 condition declaration')
    return json.loads(PLAN.read_bytes())


def validate_source(source, root):
    declaration = plan(); paths = {r['path'] for r in declaration['sourcePlans']}
    changed = subprocess.check_output(['git', 'diff', '--name-only', OLD, source, '--', 'src'], cwd=ROOT, text=True).splitlines()
    if set(changed) != paths or len(paths) != 16 or subprocess.check_output(['git', 'diff', OLD, source, '--', 'pom.xml', '.mvn', 'mvnw', 'program/characterization', 'tools/quality/static'], cwd=ROOT):
        raise ValueError('only16 declared Main; Test/SQL/resources/gates unchanged')
    before = json.loads((W/'pg5942-private-lock-static-v1/manifest.safe.json').read_bytes()); expected = dict(before['allSourceHashes'])
    for row in declaration['sourcePlans']:
        if expected[row['path']] != row['beforeSha256']:
            raise ValueError('actual before source hash')
        expected[row['path']] = row['predictedAfterSha256']
    actual = {p.relative_to(root).as_posix(): sha(p) for p in root.glob('src/*/src/main/java/**/*.java')}
    if actual != expected or len(actual) != 851:
        raise ValueError('all851 actual source hashes and16 exact predicted changes')
    return actual


def physical_changes(old, new):
    owners = {'api:'+r['path'].split('/src/main/java/')[1][:-5]+'.class' for r in plan()['sourcePlans']}
    changed = {k for k in old.keys() & new.keys() if old[k] != new[k]}
    if len(old) != 1666 or set(new) != set(old) or not owners <= changed or any(not any(k == o or k.startswith(o[:-6]+'$') for o in owners) for k in changed):
        raise ValueError('all1666/16 required outer and only their nested/debug classes can change')
    return sorted(changed)


def expected_rules(before, actual):
    expected = Counter(before); expected['AvoidLiteralsInIfCondition'] -= 21
    if expected != Counter(actual) or expected['AvoidLiteralsInIfCondition'] < 0:
        raise ValueError('exact21 literal removals; no suppressed/lost/unexpected other diagnostics')


def debug_proof(before, current, changed):
    owners = {'api:'+r['path'].split('/src/main/java/')[1][:-5]+'.class' for r in plan()['sourcePlans']}
    nested = sorted(set(changed)-owners)
    if not nested:
        return dict(classes=[], bytecodeAndPrivateDescriptorsEqual=True, disassemblySha256=None)
    names = [k.split(':', 1)[1][:-6].replace('/', '.') for k in nested]
    def disassemble(root):
        return subprocess.check_output([str(TC/'jdk-25.0.4/bin/javap'), '-c', '-p', '-s', '-classpath', str(root/'src/schubert-nk-api/target/classes'), *names])
    a, b = disassemble(before), disassemble(current)
    if a != b:
        raise ValueError('undeclared nested executable difference must not be called debug-only')
    return dict(classes=nested, bytecodeAndPrivateDescriptorsEqual=True, disassemblySha256=hashlib.sha256(b).hexdigest())


def runner_source():
    raw = inspect.getsource(previous.main)
    changes = {
        "if current['actualExit'] != 0 or current['testsExecuted'] != 0 or any(current['staticSixModules'].values()):": "if current['actualExit'] != 0 or not current['selectedQualified'] or (current['tests'],current['suites']) != (1021,175) or current['failedOrSkipped'] or not current['targetFour100'] or any(current['staticIssues'].values()):",
        "'pg5914-api-expression-static-v1/manifest.safe.json'": "'pg5942-private-lock-static-v1/manifest.safe.json'",
        "'PG5914-api-expression-static-v1/manifest.json'": "'PG5942-private-lock-static-v1/manifest.json'",
        '318d3783a5bfa4fe9a3920b252d3449eca01b9131c925758eadf13f8289548b4': 'fba315bab4168d6150638c7a21b5209dfce88b0f97951e456ed3d52d33edbda5',
        'pg5912-api-expression-selected35-v1/source': 'pg5940-private-lock-compile-v1/source',
        'pg5914-api-expression-static-v1/aux-classpath.txt': 'pg5942-private-lock-static-v1/aux-classpath.txt',
        'rawDiagnosticsRemovedByPg=93': 'rawDiagnosticsRemovedByPg=21',
        'compileManifestSha256=sha(cp)': 'selectedManifestSha256=sha(cp)',
        "target = BASE/'PG5942-private-lock-static-v1'": "target = BASE/'PG5968-api-sql-static-v1'"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one SQL21 static binding: '+old)
        raw = raw.replace(old, new, 1)
    old = '    for name in (\'pmd.xml\', \'checkstyle.xml\'):'
    if raw.count(old) != 1:
        raise ValueError('one independent debug proof point')
    raw = raw.replace(old, '    debug = debug_proof(previous, snapshot, changed)\n'+old, 1)
    old = 'existingPublicAbiUnchanged=True,'
    if raw.count(old) != 1:
        raise ValueError('one actual ABI evidence field')
    raw = raw.replace(old, 'existingPublicAbiUnchanged=True, debugOnlyProof=debug,', 1)
    compile(raw, '<all851 SQL21 raw static>', 'exec')
    return raw


def main():
    scope = {**vars(previous), 'OLD': OLD, 'COMPILE': 'pg5966-api-sql-selected1021-v1', 'SLOT': 'pg5968-api-sql-static-v1',
             'plan': plan, 'validate_source': validate_source, 'physical_changes': physical_changes, 'expected_rules': expected_rules, 'debug_proof': debug_proof}
    exec(compile(runner_source(), '<all851 API21 static>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
