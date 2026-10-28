"""Fixed whole nine pure login-policy methods; new four-file preflight already zero."""
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'e49eb0cc84c62ace468cf389938b23f3e56ba520'
BEFORE = '4a3fad244f21530547fdc79b16f9ea3af0ca13af'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/'
OUT = data.BASE/'PG12936-login-policy-plan-v1'

def main():
    invocation = capture(__file__); assert not OUT.exists()
    before = data.read_checked(data.BASE/'PG12920-coordinator-corrected-six-compile-v1/manifest.json','14e6f1dce556fe58dc1ecdea73c0b65ab6dbc45d82625601eae1732378e239cc')
    pre = data.read_checked(data.BASE/'PG12934-login-policy-preflight-v1/manifest.json','31453c489d31fc82eecac8b632865888c22476ccf94bd8cd2f1dfa567e9fe4b2')
    assert before['source'] == pre['baseSource'] == BEFORE and before['actualExit'] == before['testsExecuted'] == pre['actualExit'] == 0
    assert all(x['findings'] == x['processingErrors'] == 0 for x in pre['reports'].values())
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in before['begin']['inputHashes'].items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in pre['candidateSourceHashes'].items())
    changed = subprocess.check_output(['git','diff','--name-only','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT).decode().split('\0')[:-1]
    assert changed == [TEST+'LoginAttemptSequenceTest.java']
    reviewed = {MAIN+x+'.java':pre['candidateSourceHashes'][MAIN+x+'.java'] for x in ['LoginAttemptState','LoginAttemptKind']}
    whole = {}; cases = []
    for name,count in [('LoginAttemptStateTest',5),('LoginAttemptSequenceTest',4)]:
        path = TEST+name+'.java'; text = (data.ROOT/path).read_text()
        assert not any(word in text for word in ['@Before','@After','@Disabled','@ExtendWith','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','Class.forName','System.getenv','System.setProperty','setAccessible','PasswordHasher','AuthenticationService','LoginAttemptRepository','TemporaryInfrastructureException','WebStartupException'])
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(',text); assert len(methods) == len(set(methods)) == count
        whole[path] = pre['candidateSourceHashes'][path]
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=m,path=path,sourceSha256=whole[path]) for m in methods)
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2395_P007失敗窓時系列_単体テスト仕様書.md'
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceBefore=BEFORE,invocation=invocation,
        totalCorrections=0,sourceChanges=[dict(path=changed[0],kind='NEW_TEST_ONLY',sha256=whole[changed[0]])],
        eligibilityClosureSourceHashes=reviewed,wholeTestSourceHashes=whole,supportTestSourceHashes={},cases=cases,
        originalTests=9,originalSuites=2,newTestIds=4,existingTests=5,sameExecRequired=True,oldExecUnion=False,
        specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),
        preflightManifestSha256='31453c489d31fc82eecac8b632865888c22476ccf94bd8cd2f1dfa567e9fe4b2',
        judgement='WHOLE_NINE_IMMUTABLE_LOGIN_WINDOW_VALUES_NO_CLOCK_READ_IDENTITY_SESSION_CREDENTIAL_DB_OR_NETWORK',
        productTestsExecuted=0,newAccepted=0,whole451Accepted=False,externalActions=0))
    print(json.dumps(dict(actualExit=0,cases=len(cases),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))

if __name__ == '__main__': main()
