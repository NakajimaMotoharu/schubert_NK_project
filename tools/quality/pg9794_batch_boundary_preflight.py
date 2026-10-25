"""Bind reviewed disjoint batch value methods to current source/classes, no target execution."""
from collections import Counter
import json
import re
from pathlib import Path
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '58913ab374ef54d138fa3fad8c80cccd03d87c10'
NORMAL = ROOT.parent / 'pgpt-runs/PG379/pg9792-batch-boundary-six-compile-v1/snapshot'
OUT = data.BASE / 'PG9794-batch-boundary-preflight-v1'
MODULE = 'batch'
PREFIX = 'src/schubert-nk-batch/'
PACKAGE = 'dev/codex/schubert/nk/batch/repository/'
TYPES = {'BatchStepValuesTest':8,'CleanupStepValuesTest':8}
SUBJECTS = {PACKAGE + n for n in ('BatchRun','BatchStep','BatchStepAttempt','BatchStepResult',
    'MaintenanceActivation','CleanupCounts','CleanupKind','CleanupStepChunk')} | {'dev/codex/schubert/nk/batch/cleanup/StepCleanupSummary'}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_sha = 'aadb6fcfee66e10f1e6357493ac5c15d60babe72570dc506b87e522f9a238a86'
    normal = data.read_checked(data.BASE / 'PG9792-batch-boundary-six-compile-v1/manifest.json',normal_sha)
    assert normal['source'] == SOURCE and normal['actualExit'] == 0 and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    prior = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/manifest.json',
        'd73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    declarations = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/method-declaration-bindings.json',prior['bindingsSha256'])
    binary_types = {PACKAGE.replace('/','.') + n:count for n,count in TYPES.items()}
    rows = [r for r in declarations if r['className'] in binary_types]
    assert len(rows) == 16 and Counter(r['className'] for r in rows) == Counter(binary_types)
    test_dir = NORMAL / PREFIX / 'target/test-classes'
    cases = []
    files = {}
    for row in rows:
        name = row['className'].replace('.','/')
        assert row['path'] == PREFIX + 'src/test/java/' + name + '.java'
        assert row['annotationKind'] == 'org.junit.jupiter.api.Test' and row['compiledDescriptor'] == '()V' and row['parameterCount'] == 0
        assert hashes[row['path']] == row['sourceSha256']
        target = test_dir / (name + '.class')
        assert data.sha(target.read_bytes()) == row['physicalClassSha256']
        for file in target.parent.glob(target.stem + '*.class'):
            if file.stem == target.stem or file.stem.startswith(target.stem + '$'):
                files[str(file)] = data.sha(file.read_bytes())
        cases.append(dict(className=row['className'],method=row['method'],path=row['path'],sourceSha256=hashes[row['path']],
            normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=prior['source'],oldDynamicResultTransferred=False))
    new_methods = {
        'BatchRunValueBoundaryTest':('cutoffBoundsNullsAndFixedRunDiagnostic','activationNullsValueAccessorsAndFixedDiagnostic'),
        'CleanupValueBoundaryTest':('countsAcceptExactBoundsAndRejectEachInconsistentComponent','cleanupMetadataMatchesIndependentDdlNamesAndChunkLimits')}
    new_declarations = []
    for simple, methods in new_methods.items():
        binary = PACKAGE.replace('/','.') + simple
        relative = PREFIX + 'src/test/java/' + PACKAGE + simple + '.java'
        content = (ROOT / relative).read_text()
        assert re.findall(r'@Test\s+void\s+(\w+)\s*\(\)',content) == list(methods)
        target = test_dir / (PACKAGE + simple + '.class')
        command = [str(ROOT.parent / 'toolchain/jdk-25.0.4/bin/javap'),'-p','-s',str(target)]
        result = subprocess.run(command,capture_output=True,text=True,timeout=30,check=False)
        assert result.returncode == 0 and not result.stderr
        for method in methods:
            assert re.search(r'void ' + re.escape(method) + r'\(\);\s+descriptor: \(\)V',result.stdout)
            cases.append(dict(className=binary,method=method,path=relative,sourceSha256=hashes[relative],
                normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=SOURCE,oldDynamicResultTransferred=False))
        files[str(target)] = data.sha(target.read_bytes())
        new_declarations.append(dict(path=relative,methods=list(methods),command=command,actualExit=result.returncode,
            stdoutSha256=data.sha(result.stdout.encode())))
    assert len(cases) == 20
    jar = Path(normal['jars'][MODULE]['path'])
    assert data.sha(jar.read_bytes()) == normal['jars'][MODULE]['sha256']
    with zipfile.ZipFile(jar) as archive:
        mains = {name:data.sha(archive.read(name)) for name in archive.namelist()
            if name.endswith('.class') and any(name[:-6] == s or name[:-6].startswith(s + '$') for s in SUBJECTS)}
        history = PACKAGE + 'BatchRunRepository$History.class'
        history_sha = data.sha(archive.read(history))
    assert all(s + '.class' in mains for s in SUBJECTS) and len(SUBJECTS) == 9
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'cases.json',sorted(cases,key=lambda r:(r['className'],r['method'])))
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=normal_sha,
        expectedTests=20,expectedSuites=4,caseCounts=dict(Counter(r['className'] for r in cases)),
        casesSha256=data.sha((OUT / 'cases.json').read_bytes()),physicalTestFiles=files,fixtureFiles={},
        physicalMainClasses=mains,completeMainSourceUnits=sorted(SUBJECTS),allCurrentSourceInputHashes=hashes,
        relatedDiagnosticRecord=dict(className=history,sha256=history_sha,wholeRepositoryQualificationInferred=False),
        requiredModules=[MODULE],normalTestClassDirectories=[str(test_dir)],
        graph9TargetReferenced=False,oldDynamicResultsTransferred=False,productTestsExecuted=0,
        newTestIds=4,newDeclarationReceipts=new_declarations,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,expectedTests=20,suites=4,mainClasses=len(mains),
        manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
