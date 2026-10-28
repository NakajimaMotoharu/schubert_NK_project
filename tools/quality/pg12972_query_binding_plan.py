"""Freeze whole original2/new4 value/codec methods; actual query/DB remains unexecuted."""
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '762568bb0338749c9549ec937cc2c79e84418836'
BEFORE = 'c1d9b6e4b27b236ed8b40724f0701d2a2216237b'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionQueryRequest.java'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/'
OUT = data.BASE/'PG12972-query-binding-plan-v1'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    n = data.read_checked(data.BASE/'PG12956-public-receipt-six-compile-v1/manifest.json','77e300fe384740d96d4b43accfc0859384c6e65d3fd8cac2da1d55a4ce1e0bf0')
    p = data.read_checked(data.BASE/'PG12970-query-binding-preflight-v1/manifest.json','f8e2f65216af67ba757a4dce2e32bff48fb951587b6054dd29953650401f7f3d')
    assert n['source'] == p['baseSource'] == BEFORE and n['actualExit'] == n['testsExecuted'] == 0
    assert p['actualExit'] == 1 and p['reports']['pmd']['findings'] == 2 and p['reports']['checkstyle']['findings'] == 0
    assert all(data.sha((data.ROOT/path).read_bytes()) == digest for path,digest in n['begin']['inputHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == digest for path,digest in p['candidateSourceHashes'].items())
    changes = subprocess.check_output(['git','diff','--name-only','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT).decode().split('\0')[:-1]
    assert changes == [TEST+'QuestionQueryResponseBindingTest.java']
    cases = []; whole = {}
    for name,count in [('QuestionQueryRequestTest',2),('QuestionQueryResponseBindingTest',4)]:
        path = TEST+name+'.java'; text = (data.ROOT/path).read_text()
        assert not any(x in text for x in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','System.getenv','System.setProperty','getConnection(','setAccessible','TemporaryInfrastructureException','WebStartupException'])
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)
        assert len(methods) == len(set(methods)) == text.count('@Test') == count
        whole[path] = data.sha(text.encode())
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=m,path=path,sourceSha256=whole[path]) for m in methods)
    verify(invocation); OUT.mkdir()
    spec = 'evidence/01_PT/018_NK-OPS-001/2399_P013照会応答束縛_単体テスト仕様書.md'
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceBefore=BEFORE,invocation=invocation,
        totalCorrections=0,sourceChanges=[dict(path=changes[0],kind='NEW_TEST_ONLY',sha256=whole[changes[0]])],
        eligibilityClosureSourceHashes={MAIN:p['candidateSourceHashes'][MAIN]},wholeTestSourceHashes=whole,supportTestSourceHashes={},cases=cases,
        originalTests=6,originalSuites=2,newTestIds=4,existingTests=2,sameExecRequired=True,oldExecUnion=False,
        specificationPath=spec,specificationSha256=data.sha((data.ROOT/spec).read_bytes()),
        judgement='WHOLE_SIX_RESPONSE_VALUES_AND_EXISTING_LP_JCE_SYNTHETIC_ZERO_KEY_ONLY_NO_DATABASE_INVOCATION',
        productTestsExecuted=0,newAccepted=0,whole451Accepted=False,externalActions=0))
    print(json.dumps(dict(actualExit=0,cases=len(cases),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))

if __name__ == '__main__': main()
