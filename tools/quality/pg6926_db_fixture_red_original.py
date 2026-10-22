"""Qualify two original constructor-leak failures and owned residual stops, no test/job replay."""
import json
import os
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pathlib import PurePosixPath
import pg6922_db_fixture_selected as profile
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg5966_api_sql_selected import source_test_names
from pg5732_enum48_selected import PACKAGE

METHOD = 'dbfix1633002KnownStartedSetupSqlFailureCannotLeaveUnpublishedOwner'
MESSAGE = 'confirmed started fixture must stop before constructor failure escapes ==> expected: <false> but was: <true>'
MODES = {
 'red-bootstrap': ('bootstrap', 'api.logging.ApiLogFixtureOwnershipTest', 'PT-DBFIX-1633-A02'),
 'red-batch': ('batch', 'batch.repository.BatchFixtureOwnershipTest', 'PT-DBFIX-1633-B02')}


def production_main(inputs):
    # BUG-1634: archive also contains the separate Characterization harness.
    return {p: h for p, h in inputs.items() if p.startswith('src/') and '/src/main/java/' in p and p.endswith('.java')}


def inspect_failure(tree, cls, tid):
    if tree.get('name') != cls:
        raise ValueError('exact new fixture Test suite')
    cases = tree.findall('testcase')
    failed = []
    for c in cases:
        problems = [n for n in c if n.tag in ('failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError')]
        if problems:
            failed.append((c.get('name').removesuffix('()'), problems))
    if len(cases) != 3 or len(failed) != 1 or failed[0][0] != METHOD or len(failed[0][1]) != 1:
        raise ValueError('SQL leak failure only, config and full24 normal cases passed')
    failure = failed[0][1][0]
    if failure.tag != 'failure' or failure.get('type') != 'org.opentest4j.AssertionFailedError' or failure.get('message') != MESSAGE:
        raise ValueError('actual PID-still-present assertion, not wrong SQL oracle or cleanup failure')
    marker = tid + ' ownedResidualStop=true'
    lines = [s for n in tree.iter('system-out') for s in (n.text or '').splitlines() if s.startswith(tid + ' ownedResidualStop=')]
    if lines != [marker]:
        raise ValueError('one owned residual stop0 and PID disappearance marker; do not infer cleanup')
    return dict(testId=tid, method=METHOD, result='FAILED_EXPECTED_CONSTRUCTOR_OWNER_LEAK', exceptionType=failure.get('type'),
      message=MESSAGE, fixtureOnlyResidualStopConfirmed=True, cleanupMarker=marker, normalAndConfigCasesPassed=2)


def main():
    oldpath = BASE / 'PG6890-current4213-cases/qualification.json'
    if sha(oldpath) != '80ad328f6e4f20d2f53f0e6ac4c314c1f698842a7b9b031b14d47592d19123ce':
        raise ValueError('frozen old full identity map only')
    old = json.loads(oldpath.read_bytes())
    rows, source, archive_hash = [], None, None
    for mode, (module, short, tid) in MODES.items():
        run = W / profile.SLOTS[mode]
        mp, bp = run / 'manifest.safe.json', run / 'begin.safe.json'
        m, b = [json.loads(p.read_bytes()) for p in (mp, bp)]
        profile.guard(b['source'])
        if not (m['source'] == b['source'] and m['actualExit'] == m['mavenActualExit'] == 1 and m['phaseExits'] == [0, 0, 1]
          and m['sourceFixed'] and not m['selectedQualified'] and m['targetCounters'] == {} and m['targetFour100'] is None
          and m['failedOrSkipped'] == [[PACKAGE + short, METHOD]] and m['allPhysicalMainSha256'] == old['allPhysicalMainSha256']
          and not any(m['staticIssues'].values())):
            raise ValueError('genuine failed original with same1669 Main, no synthetic coverage or other failures')
        archive = run / 'source.tar'
        if sha(archive) != b['archiveSha256']:
            raise ValueError('exact original source archive')
        inputs = {}
        with tarfile.open(archive) as tar:
            for item in tar:
                if item.isdir():
                    continue
                p = PurePosixPath(item.name)
                if not item.isfile() or p.is_absolute() or '..' in p.parts or item.name in inputs:
                    raise ValueError('unique regular archived input')
                import hashlib
                digest = hashlib.sha256(tar.extractfile(item).read()).hexdigest()
                if sha(run / 'source' / item.name) != digest:
                    raise ValueError('every original input fixed')
                inputs[item.name] = digest
        current_main = production_main(inputs)
        if current_main != old['allSourceHashes'] or len(current_main) != 851:
            raise ValueError('all851 Main unchanged')
        if source is not None and (source != b['source'] or archive_hash != b['archiveSha256']):
            raise ValueError('both original red source/archive exactly same')
        source, archive_hash = b['source'], b['archiveSha256']
        definitions, _ = profile.inventory(mode)
        expected = {PACKAGE + n: source_test_names(run / ('source/src/schubert-nk-' + mod + '/src/test/java') / ((PACKAGE + n).replace('.', '/') + '.java')) for mod, names in definitions.items() for n in names}
        actual, xmls = {}, {}
        for mod in definitions:
            directory = run / ('source/src/schubert-nk-' + mod + '/target/surefire-reports')
            for xp in directory.glob('TEST-*.xml'):
                t = ET.parse(xp).getroot()
                cls = t.get('name')
                if cls in actual or cls not in expected:
                    raise ValueError('one declared original suite only')
                names = [c.get('name').removesuffix('()') for c in t.findall('testcase')]
                if len(set(names)) != len(names) or set(names) != set(expected[cls]):
                    raise ValueError('complete original class case inventory')
                actual[cls] = names
                xmls[cls] = sha(xp)
        if sum(map(len, actual.values())) != m['tests'] or len(actual) != m['suites']:
            raise ValueError('actual XML totals, not declared or arithmetic PASS')
        xp = run / ('source/src/schubert-nk-' + module + '/target/surefire-reports/TEST-' + PACKAGE + short + '.xml')
        counterexample = inspect_failure(ET.parse(xp).getroot(), PACKAGE + short, tid)
        target_path = 'src/schubert-nk-' + module + '/src/test/java/' + (PACKAGE + short).replace('.', '/') + '.java'
        rows.append(dict(mode=mode, source=source, originalManifestSha256=sha(mp), originalTestXmlSha256=sha(xp),
          testPath=target_path, testSourceSha256=inputs[target_path], **counterexample, actualTests=m['tests'], actualSuites=m['suites'],
          notRunTests=sum(len(v) for k, v in expected.items() if k not in actual), notRunSuites=len(expected) - len(actual),
          staticModulesCompleted=sorted(m['staticIssues']), allActualXmlSha256=xmls))
    if subprocess.check_output(['git', 'diff', source, '--', 'src', 'pom.xml', '.mvn', 'mvnw', 'tools/quality/static', 'program/characterization'], cwd=ROOT):
        raise ValueError('both source/test/oracle/gates fixed until reader completes')
    value = dict(readerActualExit=0, originalActualExit=1, source=source, sourceArchiveSha256=archive_hash,
      fixtureCounterexamples=2, rows=rows, all851MainByteExact=True, all1669PhysicalMainByteExact=True,
      wholeReplayed=False, testsExecutedByReader=0, buildReissued=False, vmActions=0, actualServiceActions=0,
      formalAccepted=False, acceptedLeafDelta=0, effortPercent=None, ptAlternativeCompleted=0,
      toolSha256=sha(ROOT / 'tools/quality/pg6926_db_fixture_red_original.py'))
    out = BASE / 'PG6926-db-fixture-red-original-v1'
    os.umask(0o077)
    out.mkdir()
    p = out / 'manifest.json'
    with p.open('x') as f:
        json.dump(value, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(readerActualExit=0, manifestSha256=sha(p), fixtureCounterexamples=2, source=source)))


if __name__ == '__main__':
    main()
