"""PG-D453 all-source/static/physical/ABI proof; no PT or service operation."""
import inspect
import json
import subprocess
from collections import Counter
import pg5942_private_lock_static as engine
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6026_error_boundary_selected import OLD, MAIN, TEST
from pg5910_storage_static_rebind import ordered_pairs

SOURCE = 'b2ecccf326088d397a071bb205dddbc2dc44ea1e'
NEW_INTERFACE = 'batch:dev/codex/schubert/nk/batch/mq/ArtemisManagementReadinessClient$OperationEncoder.class'
OWNERS = {p.split('/')[1].removeprefix('schubert-nk-')+':'+p.split('/src/main/java/')[1][:-5]+'.class' for p in MAIN}


def validate_source(source, root):
    if source != SOURCE or set(subprocess.check_output(['git', 'diff', '--name-only', OLD, SOURCE, '--', 'src'], cwd=ROOT, text=True).splitlines()) != {*MAIN, TEST}:
        raise ValueError('exact current two Main and one new independent Test source')
    old = json.loads((W/'pg6008-api-bounds-static-v1/manifest.safe.json').read_bytes())
    expected = dict(old['allSourceHashes'])
    for p in MAIN:
        expected[p] = sha(ROOT/p)
    actual = {p.relative_to(root).as_posix(): sha(p) for p in root.glob('src/*/src/main/java/**/*.java')}
    if actual != expected or len(actual) != 851:
        raise ValueError('all851 actual Main;no unrelated edits')
    for name in ('src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'):
        if subprocess.check_output(['git', 'diff', SOURCE, '--', name], cwd=ROOT):
            raise ValueError('current source/Test/quality gate frozen')
    return actual


def physical_changes(old, new):
    changed = {k for k in old.keys() & new.keys() if old[k] != new[k]}
    if (len(old), len(new)) != (1666, 1667) or set(new)-set(old) != {NEW_INTERFACE} or set(old)-set(new) or not OWNERS <= changed:
        raise ValueError('two changed owners and one declared package-private interface only')
    if any(not any(k == o or k.startswith(o[:-6]+'$') for o in OWNERS) for k in changed):
        raise ValueError('no unrelated compiled byte changes')
    return sorted(changed | {NEW_INTERFACE})


def expected_rules(before, actual):
    expected = Counter(before)
    # Four repeated checked boundaries become one. Six Error alternatives vanish;
    # three Runtime + three Exception duplicate catches also vanish. Five interrupt
    # discriminators move from catch bodies to a single ordinary classifier method.
    expected['AvoidCatchingGenericException'] -= 12
    expected['AvoidInstanceofChecksInCatchClause'] -= 5
    expected['DoNotUseThreads'] -= 4
    if expected != Counter(actual):
        raise ValueError('expected six Error and duplicate boundaries only;inspect retained raw reports')


def validate_diagnostics(rows):
    oldpath = BASE/'PG6008-api-bounds-static-v1/findings.json'
    public = json.loads((BASE/'PG6008-api-bounds-static-v1/manifest.json').read_bytes())
    if sha(oldpath) != 'dfbc2f42d66219d30b4d6d75709b06011717ab0d8f036358e0e32a29c7ec35a3' or public['source'] != OLD:
        raise ValueError('original1348 raw inventory fixed')
    before = json.loads(oldpath.read_bytes()); pairs = ordered_pairs(before, rows)
    if any(r['sourcePath'] not in MAIN and r['findingId'] not in pairs for r in rows):
        raise ValueError('all unmodified files retain complete ordered diagnostic sequences')
    left = Counter(r['sourcePath'] for r in before if r['sourcePath'] not in MAIN)
    right = Counter(r['sourcePath'] for r in rows if r['sourcePath'] not in MAIN)
    if left != right:
        raise ValueError('no missing unaffected file or warning')


def runner_source():
    raw = inspect.getsource(engine.main)
    changes = {
        "'pg5914-api-expression-static-v1/manifest.safe.json'": "'pg6008-api-bounds-static-v1/manifest.safe.json'",
        "'PG5914-api-expression-static-v1/manifest.json'": "'PG6008-api-bounds-static-v1/manifest.json'",
        '318d3783a5bfa4fe9a3920b252d3449eca01b9131c925758eadf13f8289548b4': '7c3a5d7b6e4a2246b8a73bdbb74c19a12ffdb010349ac27ca8af0bd623f43bbf',
        "if current['actualExit'] != 0 or current['testsExecuted'] != 0 or any(current['staticSixModules'].values()):": "if current['actualExit'] != 1 or current['mavenActualExit'] != 1 or current['selectedQualified'] or current['phaseExits'] != [0,1] or (current['tests'],current['suites']) != (965,162) or not current['exactInventory'] or current['failedOrSkipped'] or not current['targetFour100'] or current['staticIssues'] != dict(protocol=0,storage=0,bootstrap=0,api=0,web=0,batch=3) or sha(cp) != '9ecd53b6a1aa5380db0c8420f38323e9d2282871d68f146e636a9d03e088ab6f':",
        "physical != current['allPhysicalMainSha256']": "physical != current['allPhysicalMainSha256'] or len(physical)!=1667",
        "'pg5912-api-expression-selected35-v1/source'": "'pg6006-api-bounds-selected1021-v1/source'",
        "public_signatures(previous, changed) != public_signatures(snapshot, changed)": "public_signatures(previous, [k for k in changed if k != NEW_INTERFACE]) != public_signatures(snapshot, [k for k in changed if k != NEW_INTERFACE])",
        'pg5914-api-expression-static-v1/aux-classpath.txt': 'pg6008-api-bounds-static-v1/aux-classpath.txt',
        'physicalMain=1666': 'physicalMain=1667',
        'actualAuxClasses=1666': 'actualAuxClasses=1667',
        'unchangedPhysicalClasses=1666-len(changed)': 'unchangedPhysicalClasses=1667-len(changed)',
        'rawDiagnosticsRemovedByPg=93': 'rawDiagnosticsRemovedByPg=21',
        'compileManifestSha256=sha(cp)': 'selectedManifestSha256=sha(cp)',
        'existingPublicAbiUnchanged=True,': "existingPublicAbiUnchanged=True, originalSelectedOverallExit=1, originalSelectedOverallAccepted=False, originalSpotBugsIssues=current['staticIssues'], unresolvedBug='BUG1526',",
        "expected_rules(old['ruleCounts'], Counter(r['rule'] for r in rows))": "expected_rules(old['ruleCounts'], Counter(r['rule'] for r in rows))\n    validate_diagnostics(rows)",
        "target = BASE/'PG5942-private-lock-static-v1'": "target = BASE/'PG6028-error-boundary-static-v2'",
    }
    for old, new in changes.items():
        count = 2 if old == 'physicalMain=1666' else 1
        if raw.count(old) != count:
            raise ValueError('one exact two-boundary static binding: '+old)
        raw = raw.replace(old, new, count)
    compile(raw, '<two-source all851/1667 static>', 'exec')
    return raw


def main():
    scope = {**vars(engine), 'OLD': OLD, 'COMPILE': 'pg6026-error-boundary-selected965-v1',
             'SLOT': 'pg6028-error-boundary-static-v2', 'NEW_INTERFACE': NEW_INTERFACE,
             'validate_source': validate_source, 'physical_changes': physical_changes,
             'validate_diagnostics': validate_diagnostics, 'expected_rules': expected_rules,
             'plan': lambda: {'sourcePlans': [{'path': p} for p in MAIN]}}
    exec(compile(runner_source(), '<static only no PT>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    main()
