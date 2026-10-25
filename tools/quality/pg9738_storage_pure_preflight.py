"""Freeze exact pure resource tests and two complete Main source units; never execute native/storage IO."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = 'fd3d04df5710ca28f0e34f919cbc103e569a607b'
NORMAL = ROOT.parent / 'pgpt-runs/PG379/pg9694-semantic-direct-fixed-six-compile-v1/snapshot'
OUT = data.BASE / 'PG9738-storage-pure-preflight-v1'
PREFIX = 'src/schubert-nk-storage/'
TYPES = {'ResourceScopeTest':8,'FactoryResourceScopeTest':18,'ExceptionValueContractTest':1}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE / 'PG9694-semantic-direct-fixed-six-compile-v1/manifest.json',
        '7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a')
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    old = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/manifest.json',
        'd73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    bindings = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/method-declaration-bindings.json',old['bindingsSha256'])
    paths = {PREFIX + 'src/test/java/dev/codex/schubert/nk/storage/' + n + '.java' for n in TYPES}
    rows = [r for r in bindings if r['path'] in paths]
    assert len(rows) == 27 and Counter(r['className'].rpartition('.')[2] for r in rows) == Counter(TYPES)
    cases = []
    for row in rows:
        assert row['annotationKind'] == 'org.junit.jupiter.api.Test' and row['compiledDescriptor'] == '()V' and row['parameterCount'] == 0
        assert hashes[row['path']] == row['sourceSha256']
        target = NORMAL / PREFIX / 'target/test-classes' / (row['className'].replace('.','/') + '.class')
        assert data.sha(target.read_bytes()) == row['physicalClassSha256']
        cases.append(dict(className=row['className'],method=row['method'],path=row['path'],sourceSha256=hashes[row['path']],
            normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=old['source'],oldDynamicResultTransferred=False))
    test_dir = NORMAL / PREFIX / 'target/test-classes'
    internal_tests = {r['className'].replace('.','/') for r in cases}
    physical_tests = {str(p):data.sha(p.read_bytes()) for p in test_dir.rglob('*.class')
        if any(p.relative_to(test_dir).as_posix()[:-6] == n or p.relative_to(test_dir).as_posix()[:-6].startswith(n + '$') for n in internal_tests)}
    assert physical_tests
    jar = Path(normal['jars']['storage']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['storage']['sha256']
    subjects = {'dev/codex/schubert/nk/storage/ResourceScope','dev/codex/schubert/nk/storage/StorageIoException'}
    with zipfile.ZipFile(jar) as archive:
        main = {n:data.sha(archive.read(n)) for n in archive.namelist()
            if n.endswith('.class') and any(n[:-6] == s or n[:-6].startswith(s + '$') for s in subjects)}
    assert len(main) == 7
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'cases.json',sorted(cases,key=lambda r:(r['className'],r['method'])))
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,expectedTests=27,expectedSuites=3,
        normalManifestSha256='7d2e18f86d2bc9e5c61473da8b8924aa7c6668bf8903541d5502902d2dac1d7a',
        casesSha256=data.sha((OUT / 'cases.json').read_bytes()),caseCounts=dict(Counter(r['className'] for r in cases)),
        physicalTestFiles=physical_tests,fixtureFiles={},physicalMainClasses=main,allCurrentSourceInputHashes=hashes,
        declarationReuseNotProductPtTransfer=True,productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,expectedTests=27,expectedSuites=3,mainClasses=7,manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
