"""Frozen pure DTO Test/class/source binding; no target execution or lifecycle discovery."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
LABEL = 'PG9812-cleanup-values-six-compile-v1'
NORMAL = ROOT.parent / 'pgpt-runs/PG379' / LABEL.lower() / 'snapshot'
OUT = data.BASE / 'PG9813-cleanup-values-preflight-v1'
SUBJECTS = {'dev/codex/schubert/nk/batch/repository/' + n for n in
    ('CleanupReason','CleanupChunk','LogCleanupProgress')} | {'dev/codex/schubert/nk/batch/cleanup/LogCleanupSummary'}
METHODS = ('summaryUsesFixedDeltasAndCumulativeWarning','summaryRejectsEachInvalidComponent',
    'progressRetainsValuesAndRejectsNulls','chunkRequiresZeroCountsForEveryRejectedReason')
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/cleanup/LogCleanupValueContractTest.java'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    manifest = data.BASE / LABEL / 'manifest.json'
    normal_sha = data.sha(manifest.read_bytes())
    normal = json.loads(manifest.read_bytes())
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT / p).read_bytes()) == data.sha((NORMAL / p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','show',SOURCE + ':' + TEST],cwd=ROOT) == (ROOT / TEST).read_bytes()
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    content = (ROOT / TEST).read_text()
    assert tuple(re.findall(r'@Test\s+void\s+(\w+)\s*\(\)',content)) == METHODS
    assert not any(v in content for v in ('BeforeAll','BeforeEach','AfterAll','AfterEach','TempDir','java.sql','java.nio.file','java.net','TemporaryInfrastructureException','WebStartupException'))
    binary = 'dev.codex.schubert.nk.batch.cleanup.LogCleanupValueContractTest'
    target = NORMAL / 'src/schubert-nk-batch/target/test-classes' / (binary.replace('.','/') + '.class')
    command = [str(ROOT.parent / 'toolchain/jdk-25.0.4/bin/javap'),'-p','-s',str(target)]
    result = subprocess.run(command,capture_output=True,text=True,timeout=30,check=False)
    assert result.returncode == 0 and not result.stderr
    assert all(re.search(r'void ' + re.escape(m) + r'\(\);\s+descriptor: \(\)V',result.stdout) for m in METHODS)
    files = {str(target):data.sha(target.read_bytes())}
    cases = [dict(className=binary,method=m,path=TEST,sourceSha256=hashes[TEST],normalTestClassSha256=files[str(target)],declarationOriginSource=SOURCE,oldDynamicResultTransferred=False) for m in METHODS]
    jar = Path(normal['jars']['batch']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['batch']['sha256']
    with zipfile.ZipFile(jar) as archive:
        mains = {name:data.sha(archive.read(name)) for name in archive.namelist()
            if name.endswith('.class') and any(name[:-6] == s or name[:-6].startswith(s + '$') for s in SUBJECTS)}
    assert set(mains) == {s + '.class' for s in SUBJECTS}
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'cases.json',cases)
    data.write(OUT / 'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,normalManifestSha256=normal_sha,
        expectedTests=4,expectedSuites=1,caseCounts=dict(Counter(r['className'] for r in cases)),casesSha256=data.sha((OUT / 'cases.json').read_bytes()),
        physicalTestFiles=files,fixtureFiles={},physicalMainClasses=mains,completeMainSourceUnits=sorted(SUBJECTS),
        allCurrentSourceInputHashes=hashes,newDeclarationReceipt=dict(command=command,actualExit=0,stdoutSha256=data.sha(result.stdout.encode())),
        actualDatabaseActions=0,actualVmActions=0,graph9TargetReferenced=False,oldDynamicResultsTransferred=False,
        productTestsExecuted=0,newTestIds=4,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,expectedTests=4,suites=1,mainClasses=len(mains),manifestSha256=data.sha((OUT / 'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
