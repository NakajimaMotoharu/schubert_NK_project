"""Pure graph declaration/current artifact binding; no target execution."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = 'e598a81bb4200b4e4930278b31479ff927aa025f'
NORMAL = ROOT.parent / 'pgpt-runs/PG379/pg9750-outbox-report-six-compile-v1/snapshot'
OUT = data.BASE / 'PG9772-pure-failure-graph-preflight-v1'
TYPES = {
    'dev.codex.schubert.nk.api.error.TemporaryFailureGraph329Test':('api',3),
    'dev.codex.schubert.nk.api.error.ApiStartupGraph330Test':('api',3),
    'dev.codex.schubert.nk.web.bootstrap.WebStartupGraph330Test':('web',3)}
SUBJECTS = {
    'api':'dev/codex/schubert/nk/api/error/TemporaryInfrastructureException',
    'web':'dev/codex/schubert/nk/web/bootstrap/WebStartupException'}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_hash = '7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96'
    normal = data.read_checked(data.BASE / 'PG9750-outbox-report-six-compile-v1/manifest.json',normal_hash)
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    old = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/manifest.json',
        'd73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    bindings = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/method-declaration-bindings.json',old['bindingsSha256'])
    rows = [r for r in bindings if r['className'] in TYPES]
    assert len(rows) == 9 and Counter(r['className'] for r in rows) == Counter({n:v[1] for n,v in TYPES.items()})
    cases = []
    files = {}
    for row in rows:
        module,_ = TYPES[row['className']]
        prefix = 'src/schubert-nk-' + module + '/'
        assert row['path'] == prefix + 'src/test/java/' + row['className'].replace('.','/') + '.java'
        assert row['annotationKind'] == 'org.junit.jupiter.api.Test' and row['compiledDescriptor'] == '()V' and row['parameterCount'] == 0
        assert hashes[row['path']] == row['sourceSha256']
        test_dir = NORMAL / prefix / 'target/test-classes'
        name = row['className'].replace('.','/')
        target = test_dir / (name + '.class')
        assert data.sha(target.read_bytes()) == row['physicalClassSha256']
        for p in target.parent.glob(target.stem + '*.class'):
            if p.stem == target.stem or p.stem.startswith(target.stem + '$'):
                files[str(p)] = data.sha(p.read_bytes())
        cases.append(dict(className=row['className'],method=row['method'],path=row['path'],sourceSha256=hashes[row['path']],
            normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=old['source'],oldDynamicResultTransferred=False))
    main_classes = {}
    for module,subject in SUBJECTS.items():
        jar = Path(normal['jars'][module]['path'])
        assert data.sha(jar.read_bytes()) == normal['jars'][module]['sha256']
        with zipfile.ZipFile(jar) as archive:
            entries = {n:data.sha(archive.read(n)) for n in archive.namelist()
                if n.endswith('.class') and (n[:-6] == subject or n[:-6].startswith(subject + '$'))}
            assert entries and not (set(entries) & set(main_classes))
            main_classes.update(entries)
    assert len(main_classes) == 2 and len(files) == 7
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'cases.json',sorted(cases,key=lambda r:(r['className'],r['method'])))
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,expectedTests=9,expectedSuites=3,
        normalManifestSha256=normal_hash,casesSha256=data.sha((OUT / 'cases.json').read_bytes()),
        caseCounts=dict(Counter(r['className'] for r in cases)),physicalTestFiles=files,
        fixtureFiles={},physicalMainClasses=main_classes,allCurrentSourceInputHashes=hashes,
        requiredModules=list(SUBJECTS),normalTestClassDirectories=[str(NORMAL / ('src/schubert-nk-' + m) / 'target/test-classes') for m in SUBJECTS],
        oldDynamicResultsTransferred=False,productTestsExecuted=0,newTestIds=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,expectedTests=9,suites=3,mainClasses=2,manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
