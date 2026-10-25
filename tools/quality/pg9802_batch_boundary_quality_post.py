"""Bind actual batch20/counters/new-Test checks; compare immutable prior static byte inputs only."""
import json
from pathlib import Path
import re
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '58913ab374ef54d138fa3fad8c80cccd03d87c10'
OUT = data.BASE / 'PG9802-batch-boundary-quality-post-v1'
NEW = {
    'BatchRunValueBoundaryTest':('WBS-P017-02',{
        'cutoffBoundsNullsAndFixedRunDiagnostic':'PT-BAT-RUNVALUE001',
        'activationNullsValueAccessorsAndFixedDiagnostic':'PT-BAT-RUNVALUE002'}),
    'CleanupValueBoundaryTest':('WBS-P017-07',{
        'countsAcceptExactBoundsAndRejectEachInconsistentComponent':'PT-BAT-CLEANVALUE001',
        'cleanupMetadataMatchesIndependentDdlNamesAndChunkLimits':'PT-BAT-CLEANVALUE002'})}
PREFIX = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/'


def entries(jars):
    result = {}
    for module,value in jars.items():
        path = Path(value['path'])
        assert data.sha(path.read_bytes()) == value['sha256']
        with zipfile.ZipFile(path) as archive:
            result[module] = {n:data.sha(archive.read(n)) for n in archive.namelist() if not n.endswith('/')}
    return result


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    before = data.read_checked(data.BASE / 'PG9750-outbox-report-six-compile-v1/manifest.json',
        '7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96')
    normal = data.read_checked(data.BASE / 'PG9792-batch-boundary-six-compile-v1/manifest.json',
        'aadb6fcfee66e10f1e6357493ac5c15d60babe72570dc506b87e522f9a238a86')
    assert before['actualExit'] == normal['actualExit'] == 0 and normal['source'] == SOURCE
    assert before['source'] == 'e598a81bb4200b4e4930278b31479ff927aa025f' and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in hashes.items())
    changed = {p for p,h in hashes.items() if before['begin']['inputHashes'].get(p) != h}
    assert changed == {PREFIX + n + '.java' for n in NEW}
    assert set(before['begin']['inputHashes']) | changed == set(hashes)
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    old_entries, current_entries = entries(before['jars']), entries(normal['jars'])
    assert old_entries == current_entries and sum(n.endswith('.class') for rows in current_entries.values() for n in rows) == 1843
    byte_equivalence = {m:dict(entries=len(rows),entryHashMapSha256=data.sha(json.dumps(rows,sort_keys=True).encode()),
        oldJarSha256=before['jars'][m]['sha256'],currentJarSha256=normal['jars'][m]['sha256']) for m,rows in current_entries.items()}
    old_snap = Path(before['jars']['batch']['path']).parents[3]
    snap = Path(normal['jars']['batch']['path']).parents[3]
    old_tests = {p.relative_to(old_snap).as_posix():data.sha(p.read_bytes()) for p in old_snap.glob('src/*/target/test-classes/**/*.class')}
    new_tests = {p.relative_to(snap).as_posix():data.sha(p.read_bytes()) for p in snap.glob('src/*/target/test-classes/**/*.class')}
    assert len(old_tests) == 1913 and len(new_tests) == 1915 and all(new_tests.get(p) == h for p,h in old_tests.items())
    assert set(new_tests) - set(old_tests) == {p.replace('src/test/java/','target/test-classes/').removesuffix('.java') + '.class' for p in changed}
    pins = {
        'PG9796-batch-boundary-host-v1':'07de2e9687c0c97d7e5ddf99590e60c60124418750e6fcd23ba5ee9be21fcd4b',
        'PG9798-batch-boundary-post-v1':'a87b3769564811857af87bf65851732994369b6860da7193acc31bfd56a74c47',
        'PG9800-batch-new-test-static-v1':'c600b440e197fb54e721924a640a3035581fb60ddb4da08de53f678a44d8f25f'}
    proofs = {n:data.read_checked(data.BASE / n / 'manifest.json',h) for n,h in pins.items()}
    assert all(p['actualExit'] == 0 and p['source'] == SOURCE for p in proofs.values())
    post = proofs['PG9798-batch-boundary-post-v1']
    assert post['actualTests'] == 20 and post['suites'] == 4 and post['four100ExecutableClassCount'] == 12
    assert post['selectedSourceUnitFour100'] and not post['coverageUnion'] and not post['exclusionsAdded']
    assert all(v['findings'] == v['processingErrors'] == 0 for v in proofs['PG9800-batch-new-test-static-v1']['reports'].values())
    static = data.read_checked(data.BASE / 'PG9788-batch-value-static-v1/manifest.json',
        '1c5b60cd8a2d302db816568e1ac1b0b3d56dd9f82146c6e6653d94b49af03470')
    prepared = data.read_checked(data.BASE / 'PG9794-batch-boundary-preflight-v1/manifest.json',
        'c2570ba3680acbad1edfbea0efdf22802d5c31d500d068cf329f7ac810e0c841')
    assert static['actualExit'] == 0 and static['source'] == before['source'] and static['allInputMainClasses'] == 12
    assert static['results']['batch']['physicalClasses'] == prepared['physicalMainClasses']
    old_internal = {v['path']:m for m,v in before['jars'].items()}
    for path,h in static['results']['batch']['dependencyHashes'].items():
        assert data.sha(Path(path).read_bytes()) == h
        if path in old_internal:
            assert old_entries[old_internal[path]] == current_entries[old_internal[path]]
        else:
            assert Path(path).is_relative_to(ROOT.parent / 'toolchain/m2/repository')
    new_rows = []
    for simple,(owner,methods) in NEW.items():
        path = PREFIX + simple + '.java'
        text = (ROOT / path).read_text()
        assert re.findall(r'@Test\s+void\s+(\w+)\s*\(\)',text) == list(methods)
        new_rows.append(dict(path=path,sha256=hashes[path],canonicalOwner=owner,canonicalCostOwner=owner,
            methodTestIds=methods,currentOwnerRegistryUpdated=False))
    ddl_paths = ['src/schubert-nk-api/src/main/resources/db/migration/' + n for n in (
        'V005__gin_functions_views_and_grants.sql','V012__durable_inbox_inspection_progress.sql',
        'V014__durable_log_cleanup_progress.sql','V026__web_receipt_references.sql')]
    ddl = '\n'.join((ROOT / p).read_text() for p in ddl_paths)
    test = (ROOT / PREFIX / 'CleanupValueBoundaryTest.java').read_text()
    functions = re.findall(r'"(schubert\.maintenance_cleanup_[a-z_]+)"',test)
    assert len(functions) == len(set(functions)) == 9
    assert all(re.search(r'CREATE(?: OR REPLACE)? FUNCTION ' + re.escape(name) + r'\s*\(',ddl) for name in functions)
    assert 'int[] limits = {1000, 1000, 1000, 1000, 10000, 1000, 1000, 1000, 1000};' in test
    universe = {p for p in hashes if p.endswith('.java') and '/java/' in p}
    assert len(universe) == 1794 and sum('/src/main/java/' in p for p in universe) == 965
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,proofManifestHashes=pins,
        changedSourceHashes={p:hashes[p] for p in changed},newTestSources=new_rows,newTestIds=4,
        wholeSixMainJarUncompressedEntriesIdentical=byte_equivalence,allMainClassesUnchanged=1843,
        oldTestClasses=1913,currentTestClasses=1915,oldTestClassBytesUnchanged=True,
        actualSelectedTests=20,actualSelectedSuites=4,physicalSelectedMainClasses=12,
        selectedCoverage=post['selectedSourceUnitCounters'],selectedFourCounter100=True,
        mainStaticOriginalSource=static['source'],mainStaticOriginalRun='PG9788-batch-value-static-v1',
        mainStaticProofSha256='1c5b60cd8a2d302db816568e1ac1b0b3d56dd9f82146c6e6653d94b49af03470',
        mainStaticResultNotRerunOnCurrentSource=True,unchangedClassResourceManifestAndExternalTypeBytesOnly=True,
        oldDynamicResultsTransferred=False,oldExecUnion=False,independentDdlNames=functions,
        ddlSourceHashes={p:hashes[p] for p in ddl_paths},sqlExecuted=0,productTestsExecutedByPost=0,
        graph9Operations=0,externalRuntimeOperations=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,
        fullBatchModuleAccepted=False,javaPaths=1794,mainPaths=965,testPaths=829,currentOwnerRegistryUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,currentSelectedTests=20,mainClassesUnchanged=1843,newTestClasses=2,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
