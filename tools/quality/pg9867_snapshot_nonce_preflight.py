"""Freeze exactly the seven codec methods plus two new nonce-failure methods, without execution."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '21d7c30425e7aa9ce435e808035a94fa4d75c93b'
LABEL = 'PG9866-snapshot-nonce-six-compile-v1'
NORMAL = ROOT.parent/'pgpt-runs/PG379'/LABEL.lower()/'snapshot'
OUT = data.BASE/'PG9867-snapshot-nonce-preflight-v1'
SUBJECT = 'dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec'
CATALOG = {
    'ResponseSnapshotCodecTest':('scope002QuestionScopeFrameMatchesIndependentCompressionAadAndJceCiphertext',
        'fixedNonceCiphertextMatchesIndependentCompressionAndAadVector',
        'zeroAndMaximumPlaintextRoundTripAndEveryLengthBoundaryIsGuarded',
        'currentPreviousUnknownTamperAndEveryAadMutationDenyClosed',
        'malformedTruncatedTrailingDictionaryAndCompressionBombStreamsAreRejected',
        'identitySnapshotKeyAndLifecycleContractsRejectNullAndInvalidValues',
        'unavailableAesProviderProducesTypedBoundedFailure'),
    'ResponseSnapshotNonceFailureTest':('rngscope001RuntimeFailureClearsOwnedNonceAndPreservesIdentity',
        'rngscope002ErrorClearsOwnedNonceAndPreservesIdentity')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    manifest = data.BASE/LABEL/'manifest.json'
    normal_sha = data.sha(manifest.read_bytes())
    normal = json.loads(manifest.read_bytes())
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    files,cases,receipts = {},[],[]
    for simple,methods in CATALOG.items():
        binary = 'dev.codex.schubert.nk.api.idempotency.'+simple
        path = 'src/schubert-nk-api/src/test/java/'+binary.replace('.','/')+'.java'
        text = (ROOT/path).read_text()
        assert tuple(re.findall(r'@Test\s+void\s+(\w+)\s*\(\)',text)) == methods
        assert not any(t in text for t in ('BeforeAll','BeforeEach','AfterAll','AfterEach','TempDir','java.sql','java.nio.file','java.net',
            'TemporaryInfrastructureException','WebStartupException','Disabled'))
        target = NORMAL/'src/schubert-nk-api/target/test-classes'/(binary.replace('.','/')+'.class')
        command = [str(ROOT.parent/'toolchain/jdk-25.0.4/bin/javap'),'-p','-s',str(target)]
        result = subprocess.run(command,capture_output=True,text=True,timeout=30,check=False)
        assert result.returncode == 0 and not result.stderr
        assert all(re.search(r'void '+re.escape(m)+r'\(\);\s+descriptor: \(\)V',result.stdout) for m in methods)
        receipts.append(dict(command=command,actualExit=result.returncode,stdoutSha256=data.sha(result.stdout.encode())))
        for item in target.parent.glob(simple+'*.class'):
            if item.stem == simple or item.stem.startswith(simple+'$'):
                assert item.resolve() == item and not item.is_symlink()
                files[str(item)] = data.sha(item.read_bytes())
        for method in methods:
            cases.append(dict(className=binary,method=method,path=path,sourceSha256=hashes[path],
                normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=SOURCE,oldDynamicResultTransferred=False))
    jar = Path(normal['jars']['api']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['api']['sha256']
    with zipfile.ZipFile(jar) as archive:
        mains = {n:data.sha(archive.read(n)) for n in archive.namelist()
            if n == SUBJECT+'.class' or (n.startswith(SUBJECT+'$') and n.endswith('.class'))}
    assert set(mains) == {SUBJECT+'.class'} and len(cases) == 9 and len(CATALOG) == 2
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=normal_sha,
        expectedTests=9,expectedSuites=2,caseCounts=dict(Counter(r['className'] for r in cases)),
        casesSha256=data.sha((OUT/'cases.json').read_bytes()),physicalTestFiles=files,fixtureFiles={},physicalMainClasses=mains,
        completeMainSourceUnits=[SUBJECT],allCurrentSourceInputHashes=hashes,newDeclarationReceipts=receipts,
        actualDatabaseActions=0,actualVmActions=0,graph9TargetReferenced=False,oldDynamicResultsTransferred=False,
        productTestsExecuted=0,newTestIds=2,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=9,suites=2,physicalTestFiles=len(files),mainClasses=1,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
