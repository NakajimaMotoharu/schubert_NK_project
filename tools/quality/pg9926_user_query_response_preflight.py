"""Freeze only four standalone response Test methods; no DB/Test/JCE/thread/application execution."""
import json
from pathlib import Path
import re
import subprocess
import zipfile

import g07_host_class_provenance_inputs as data
from classfile_code_metadata import decode
from host_tool_invocation import capture, verify

ROOT = data.ROOT
SOURCE = '716ed961c5ae4edb543edefdf29f37fe6cf959ba'
NORMAL = ROOT.parent/'pgpt-runs/PG379/pg9924-user-query-response-six-compile-v1/snapshot'
OUT = data.BASE/'PG9926-user-query-response-preflight-v1'
SUBJECT = 'dev/codex/schubert/nk/api/application/admin/UserQueryRequest'
BINARY = 'dev.codex.schubert.nk.api.application.admin.UserQueryResponseBoundaryTest'
METHODS = (
    'val001LiteralSearchAndEmptyResponseHonorInterfaceConstants',
    'val002PageIdentityAndSizeRejectTypedFailures',
    'val003RecordCountsAndPaginationCannotDisagree',
    'val004LayoutDataAndDetailTargetAreBoundToOriginalRequest')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal_path = data.BASE/'PG9924-user-query-response-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    assert normal['source'] == SOURCE and normal['actualExit'] == 0 and normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((ROOT/p).read_bytes()) == data.sha((NORMAL/p).read_bytes()) == h for p,h in hashes.items())
    assert not subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT)
    path = 'src/schubert-nk-api/src/test/java/'+BINARY.replace('.','/')+'.java'
    text = (ROOT/path).read_text()
    assert tuple(re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)) == METHODS
    assert not any(marker in text for marker in (
        'BeforeAll','BeforeEach','AfterAll','AfterEach','TempDir','Disabled','ExtendWith','RegisterExtension',
        'java.sql','java.net','java.nio.file','javax.crypto','jakarta.jms','UserQueryRequestTest.',
        'UserMutationRequestTest.','ApiLogDatabaseFixture','UserApplicationFixture','TemporaryInfrastructureException',
        'WebStartupException','.canonical(','.query(','Executors','new Thread','Class.forName','getDeclared'))
    assert 'new byte[96]' in text and '"000001050"' in text and '"000000000003"' in text
    assert 'System.arraycopy(pageAndSize, 0, data, 77, pageAndSize.length)' in text
    assert 'assertThrows(RuntimeException.class' not in text
    target = NORMAL/'src/schubert-nk-api/target/test-classes'/(BINARY.replace('.','/')+'.class')
    declaration = decode(target.read_bytes(),BINARY.replace('.','/')+'.class')
    assert declaration['sourceFile'] == 'UserQueryResponseBoundaryTest.java'
    for method in METHODS:
        found = [m for m in declaration['methods'] if m['name'] == method and m['descriptor'] == '()V' and m['hasCode']]
        assert len(found) == 1
    physical_test = {str(p):data.sha(p.read_bytes()) for p in target.parent.glob('UserQueryResponseBoundaryTest*.class')}
    assert set(physical_test) == {str(target)}
    jar = Path(normal['jars']['api']['path'])
    assert data.sha(jar.read_bytes()) == normal['jars']['api']['sha256']
    with zipfile.ZipFile(jar) as archive:
        physical_main = {n:data.sha(archive.read(n)) for n in archive.namelist() if n == SUBJECT+'.class' or n.startswith(SUBJECT+'$')}
    assert set(physical_main) == {SUBJECT+'.class'}
    cases = [dict(className=BINARY,method=m,path=path,sourceSha256=hashes[path],
        normalTestClassSha256=data.sha(target.read_bytes()),declarationOriginSource=SOURCE,oldDynamicResultTransferred=False) for m in METHODS]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'cases.json',cases)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),expectedTests=4,expectedSuites=1,
        caseCounts={BINARY:4},casesSha256=data.sha((OUT/'cases.json').read_bytes()),physicalTestFiles=physical_test,
        physicalMainClasses=physical_main,completeMainSourceUnits=[SUBJECT],allCurrentSourceInputHashes=hashes,
        standaloneFixtureSourceReviewed=True,sharedDbFixturesInvoked=False,graph9TargetReferenced=False,
        keyCloseValidationRetried=False,productTestsExecuted=0,newTestIds=4,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,tests=4,suites=1,mainClasses=1,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
