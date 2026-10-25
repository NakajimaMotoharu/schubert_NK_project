"""Freeze ten existing and three new pure API value tests, eight whole Main source units."""
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
OUT = data.BASE / 'PG9752-outbox-value-preflight-v1'
PREFIX = 'src/schubert-nk-api/'
PACKAGE = 'dev/codex/schubert/nk/api/messaging/outbound/'
TYPES = {'OutboxPolicyTest':4,'OutboxModelTest':4,'OutboxDlqMetadataTest':2}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE / 'PG9750-outbox-report-six-compile-v1/manifest.json',
        '7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96')
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    old = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/manifest.json',
        'd73ffe203a58ca9fab7f19f0b4baa7b2588fb25ad7e13c75c0c6411f5a719a18')
    bindings = data.read_checked(data.BASE / 'PG9592-current-test-method-post-v1/method-declaration-bindings.json',old['bindingsSha256'])
    paths = {PREFIX + 'src/test/java/dev/codex/schubert/nk/storage/' + n + '.java' for n in TYPES}
    rows = [r for r in bindings if r['path'] in paths]
    assert len(rows) == 10 and Counter(r['className'].rpartition('.')[2] for r in rows) == Counter(TYPES)
    cases = []
    for row in rows:
        assert row['annotationKind'] == 'org.junit.jupiter.api.Test' and row['compiledDescriptor'] == '()V' and row['parameterCount'] == 0
        assert hashes[row['path']] == row['sourceSha256']
        target = NORMAL / PREFIX / 'target/test-classes' / (row['className'].replace('.','/') + '.class')
        assert data.sha(target.read_bytes()) == row['physicalClassSha256']
        cases.append(dict(className=row['className'],method=row['method'],path=row['path'],sourceSha256=hashes[row['path']],
            normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=old['source'],oldDynamicResultTransferred=False))
    test_dir = NORMAL / PREFIX / 'target/test-classes'
    new_name = PACKAGE + 'OutboxDispatchReportBoundaryTest'
    new_path = PREFIX + 'src/test/java/' + new_name + '.java'
    new_methods = ('acceptsZeroAndExactMaximumWithoutNarrowingValidCounts','rejectsWrappedSumsInEveryComponentPosition','rejectsEveryNegativeComponentAndNonWrappingMismatch')
    import re
    content = (ROOT / new_path).read_text()
    assert re.findall(r'@Test\s+void\s+(\w+)\s*\(\)',content) == list(new_methods)
    target = test_dir / (new_name + '.class')
    command = [str(ROOT.parent / 'toolchain/jdk-25.0.4/bin/javap'),'-p','-s',str(target)]
    check = subprocess.run(command,capture_output=True,text=True,timeout=30,check=False)
    assert check.returncode == 0 and not check.stderr
    for name in new_methods:
        assert re.search(r'void ' + re.escape(name) + r'\(\);\s+descriptor: \(\)V',check.stdout)
        cases.append(dict(className=new_name.replace('/','.'),method=name,path=new_path,sourceSha256=hashes[new_path],
            normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=SOURCE,oldDynamicResultTransferred=False))
    assert len(cases) == 13

    internal_tests = {r['className'].replace('.','/') for r in cases}
    physical_tests = {str(p):data.sha(p.read_bytes()) for p in test_dir.rglob('*.class')
        if any(p.relative_to(test_dir).as_posix()[:-6] == n or p.relative_to(test_dir).as_posix()[:-6].startswith(n + '$') for n in internal_tests)}
    assert physical_tests
    jar = Path(normal['jars']['api']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['storage']['sha256']
    subjects = {PACKAGE + n for n in ('OutboxDestination','OutboxRetrySchedule','OutboxEntry','OutboxRequest','OutboxDlqMetadata','OutboxDispatchReport','OutboxIntegrityException','OutboxSendException')}
    with zipfile.ZipFile(jar) as archive:
        main = {n:data.sha(archive.read(n)) for n in archive.namelist()
            if n.endswith('.class') and any(n[:-6] == s or n[:-6].startswith(s + '$') for s in subjects)}
    assert len(main) == 8
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'cases.json',sorted(cases,key=lambda r:(r['className'],r['method'])))
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,expectedTests=13,expectedSuites=4,
        normalManifestSha256='7b1c2b2e67dab622cc3e905e1c04ac5819a587f90992c404cf6cab3f0ceebb96',
        casesSha256=data.sha((OUT / 'cases.json').read_bytes()),caseCounts=dict(Counter(r['className'] for r in cases)),
        physicalTestFiles=physical_tests,fixtureFiles={},physicalMainClasses=main,allCurrentSourceInputHashes=hashes,
        declarationReuseNotProductPtTransfer=True,newDeclarationCommand=command,newDeclarationExit=check.returncode,
        newDeclarationStdoutSha256=data.sha(check.stdout.encode()),newDeclarationSourceMethods=list(new_methods),
        productTestsExecuted=0,newTestIds=3,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,expectedTests=13,expectedSuites=4,mainClasses=8,manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
