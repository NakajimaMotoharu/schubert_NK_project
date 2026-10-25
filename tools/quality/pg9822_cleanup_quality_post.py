"""Independent current-source proof join and untouched-byte audit; no product execution."""
import json
from pathlib import Path
import re
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
OUT = data.BASE / 'PG9822-cleanup-quality-post-v1'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/cleanup/LogCleanupValueContractTest.java'
PINS = {
    'PG9812-cleanup-values-six-compile-v1':'e074d972cbaf56b94ba4d25a77e7368b4f53ccd91489be0fbc27f07ef3975c95',
    'PG9813-cleanup-values-preflight-v1':'5f1a770473711ca42f1374d40e0456dd41580919d89d762e6520f161b9ca8344',
    'PG9814-cleanup-values-host-v2':'3aba49441d549d8bc492dc4b063b230ab464772bb8554eedc83ff0cafa6a1944',
    'PG9816-cleanup-values-post-v1':'dcb4e2ecd05ff765c58269d572d016dee84a7516b8a8878a443f36a0b4f3ea94',
    'PG9818-cleanup-new-test-static-v1':'adcb5717bbf2b560ef70ceb3a231198d6d36ca1e1fdd98831f2aec427a56da71',
    'PG9820-cleanup-values-static-v1':'875fd84bb698c4f05eaeb46fe67628844723c17227aca1ca8b367d93e309f24e'}


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
    proofs = {n:data.read_checked(data.BASE / n / 'manifest.json',h) for n,h in PINS.items()}
    assert all(v['source'] == SOURCE and v['actualExit'] == 0 for v in proofs.values())
    normal = proofs['PG9812-cleanup-values-six-compile-v1']
    before = data.read_checked(data.BASE / 'PG9792-batch-boundary-six-compile-v1/manifest.json',
        'aadb6fcfee66e10f1e6357493ac5c15d60babe72570dc506b87e522f9a238a86')
    assert before['actualExit'] == 0 and before['source'] == '58913ab374ef54d138fa3fad8c80cccd03d87c10'
    hashes = normal['begin']['inputHashes']
    assert set(hashes) - set(before['begin']['inputHashes']) == {TEST}
    assert all(hashes[p] == h for p,h in before['begin']['inputHashes'].items())
    assert all(data.sha((ROOT / p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    old_entries,current_entries = entries(before['jars']),entries(normal['jars'])
    assert old_entries == current_entries and sum(n.endswith('.class') for v in current_entries.values() for n in v) == 1843
    old_snap = Path(before['jars']['batch']['path']).parents[3]
    snap = Path(normal['jars']['batch']['path']).parents[3]
    old_tests = {str(p.relative_to(old_snap)):data.sha(p.read_bytes()) for p in old_snap.glob('src/*/target/test-classes/**/*.class')}
    new_tests = {str(p.relative_to(snap)):data.sha(p.read_bytes()) for p in snap.glob('src/*/target/test-classes/**/*.class')}
    assert len(old_tests) == 1915 and len(new_tests) == 1916 and all(new_tests.get(p) == h for p,h in old_tests.items())
    assert set(new_tests) - set(old_tests) == {TEST.replace('src/test/java/','target/test-classes/').removesuffix('.java') + '.class'}
    prepared = proofs['PG9813-cleanup-values-preflight-v1']
    post = proofs['PG9816-cleanup-values-post-v1']
    assert post['actualTests'] == 4 and post['suites'] == 1 and post['physicalMainClassCount'] == post['four100ExecutableClassCount'] == 4
    assert post['selectedSourceUnitFour100'] and not post['coverageUnion'] and not post['exclusionsAdded']
    assert all(v['findings'] == v['processingErrors'] == 0 for v in proofs['PG9818-cleanup-new-test-static-v1']['reports'].values())
    static = proofs['PG9820-cleanup-values-static-v1']
    assert static['allInputMainClasses'] == 4 and static['results']['batch']['physicalClasses'] == prepared['physicalMainClasses']
    assert static['results']['batch']['findings'] == static['results']['batch']['processingErrors'] == 0
    failure = data.read_checked(data.BASE / 'PG9814-cleanup-values-host-v1/manifest.json',
        'c47222d159197293adfbdebdf5a2ac50fea454ce5c0fb25fe63a17be32c2b2e5')
    assert failure['actualExit'] == 1 and not failure['cases'] and not failure['xmlHashes']
    fixed = (ROOT / 'tools/quality/architecture/CleanupValueJunitLauncherV2.java').read_text()
    assert 'EXPECTED_TESTS = 4;' in fixed and 'EXPECTED_SUITES = 1;' in fixed
    assert 'expected.size() != EXPECTED_TESTS || methods.size() != EXPECTED_SUITES' in fixed
    assert fixed.count('== EXPECTED_TESTS') == 4
    original = (ROOT / 'tools/quality/architecture/BatchBoundaryJunitLauncher.java').read_text()
    assert 'expected.size() != 20 || methods.size() != 4' in original
    methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(\)',(ROOT / TEST).read_text())
    assert len(methods) == 4
    universe = {p for p in hashes if p.endswith('.java') and '/java/' in p}
    assert len(universe) == 1795 and sum('/src/main/java/' in p for p in universe) == 965
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,proofManifestHashes=PINS,
        allMainClassBytesUnchanged=1843,wholeSixMainJarUncompressedEntriesIdentical=True,
        oldTestClassBytesUnchanged=1915,currentTestClasses=1916,changedSourceHashes={TEST:hashes[TEST]},
        actualTests=4,suites=1,physicalSubjectClasses=4,subjectFour100=True,counters=post['selectedSourceUnitCounters'],
        newTestIds={m:'PT-BAT-CLEANVALUE' + str(i).zfill(3) for i,m in enumerate(methods,3)},
        originalToolFailurePreserved=True,toolFixNamedCountGuards=True,originalBatchLauncherNotAffected=True,
        bug='BUG1764',horizontalReview='YKT1515',oldDynamicResultsTransferred=False,coverageUnion=False,
        productTestsExecutedByPost=0,actualExternalOperations=0,graph9Operations=0,
        javaPaths=1795,mainPaths=965,testPaths=830,newOwnerRegistryUpdated=False,
        newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,newTestIds=4,allMainClassBytesUnchanged=1843,
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
