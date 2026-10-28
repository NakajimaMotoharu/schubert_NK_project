"""Whole12 public receipt cases, exact candidate-token inverse and reviewed one-file trace."""
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX
import public_receipt_trace_contract as contract

SOURCE = 'c1d9b6e4b27b236ed8b40724f0701d2a2216237b'
BEFORE = 'e49eb0cc84c62ace468cf389938b23f3e56ba520'
MAIN = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/'
TEST = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/'
NEW = TEST+'QuestionReceiptRecoveryTest.java'
OUT = data.BASE/'PG12954-public-receipt-plan-v1'
METHOD = re.compile(r'@Test\s+(?:@DisplayName\([^\n]+\)\s+)?void\s+(\w+)\s*\(')

def tokens(s): return [m.group() for m in LEX.finditer(s) if not m.group().startswith(('//','/*'))]

def require(old,new):
    ts = tokens(new)
    for name,value in [('PARTIAL_FAILURE_DRAW','13'),('LAST_FAILURE_DRAW','25')]:
        decl = tokens('private static final int '+name+' = '+value+';')
        ix = [i for i in range(len(ts)) if ts[i:i+len(decl)] == decl]; assert len(ix) == 1
        i = ix[0]; ts = ts[:i]+ts[i+len(decl):]; assert ts.count(name) == 1
        ts = [v for x in ts for v in (tokens(value) if x == name else [x])]
    assert ts == tokens(old)

def main():
    invocation = capture(__file__); assert not OUT.exists()
    before = data.read_checked(data.BASE/'PG12938-login-policy-six-compile-v1/manifest.json','f65a05a93b6a857e21602222b5a9f5287a92b185cf6b540792c5bf8d7a10cac2')
    pre = data.read_checked(data.BASE/'PG12952-public-receipt-preflight-v2/manifest.json','4d6ed75f78c3ef5116a7d7a73223f53e6bf33e79e9ddd9b62cf51be83274d128')
    assert before['source'] == pre['baseSource'] == BEFORE and before['actualExit'] == before['testsExecuted'] == pre['actualExit'] == 0
    assert pre['reports']['pmd']['findings'] == 6 and pre['reports']['checkstyle']['findings'] == 0
    assert all(x['processingErrors'] == 0 for x in pre['reports'].values()) and not pre['rawGatePassed']
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in before['begin']['inputHashes'].items())
    assert all(data.sha((data.ROOT/p).read_bytes()) == digest for p,digest in pre['candidateSourceHashes'].items())
    changed = subprocess.check_output(['git','diff','--name-only','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT).decode().split('\0')[:-1]
    assert changed == [NEW]
    original = data.ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG12951-public-receipt-style-before-v1'
    oldm = json.loads((original/'manifest.json').read_bytes())
    old = (original/oldm['originalBody']).read_text(); assert data.sha(old.encode()) == oldm['candidateSha256']
    new = (data.ROOT/NEW).read_text(); require(old,new); labels = []
    for a,b in [('PARTIAL_FAILURE_DRAW = 13','PARTIAL_FAILURE_DRAW = 14'),('LAST_FAILURE_DRAW = 25','LAST_FAILURE_DRAW = 24'),('draw == PARTIAL_FAILURE_DRAW','draw == LAST_FAILURE_DRAW'),('return draw % 32;','return 31;'),('"EFGHJKMNPQRSTVWXYZ01234567"','"ZFGHJKMNPQRSTVWXYZ01234567"'),('.get(5, TimeUnit.SECONDS)','.get(1, TimeUnit.SECONDS)')]:
        bad = new.replace(a,b,1); assert bad != new
        try: require(old,bad)
        except AssertionError: labels.append(a)
        else: raise AssertionError('wrong candidate control/golden accepted')
    reviewed = {MAIN+n+'.java':pre['candidateSourceHashes'][MAIN+n+'.java'] for n in ['QuestionReceiptId','QuestionReceiptIdGenerator']}
    whole = {}; cases = []
    expected = {'QuestionReceiptIdTest':['exactAlphabet','lengthBoundaries','characterBoundaries','independentRandomVector','randomFailure','nullAndFactory','concurrentCalls','equalityAndPublicEvidence'],
        'QuestionReceiptRecoveryTest':['everyFailedDrawReleasesTheGeneratorForAnotherThread','invalidIndicesDoNotPoisonTheNextCandidate','discardedPartialAlphabetDoesNotPrefixTheNextCandidate','lastDrawErrorKeepsIdentityAndStillUnlocks']}
    for name,methods in expected.items():
        path = TEST+name+'.java'; text = (data.ROOT/path).read_text()
        assert METHOD.findall(text) == methods and text.count('@Test') == len(methods)
        assert not any(word in text for word in ['@Before','@After','@Disabled','@ExtendWith','@TempDir','java.net.','java.sql.','ProcessBuilder','Class.forName','System.getenv','System.setProperty','Security.addProvider','Security.setProperty','setAccessible','TemporaryInfrastructureException','WebStartupException'])
        if 'java.nio.file' in text:
            assert contract.reviewed(path,text)
            assert not contract.reviewed(path+'.other',text) and not contract.reviewed(path,text+'\n// modified')
        whole[path] = pre['candidateSourceHashes'][path]
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=m,path=path,sourceSha256=whole[path]) for m in methods)
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2397_P011公開受付ID生成回復_単体テスト仕様書.md'
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceBefore=BEFORE,invocation=invocation,
        totalCorrections=2,candidateStyleCorrectionsOnly=True,globalPriorSourceCorrectionsAdded=0,
        sourceChanges=[dict(path=NEW,kind='NEW_TEST_ONLY',sha256=whole[NEW],originalCandidateSha256=oldm['candidateSha256'])],
        eligibilityClosureSourceHashes=reviewed,wholeTestSourceHashes=whole,supportTestSourceHashes={},cases=cases,
        originalTests=12,originalSuites=2,newTestIds=4,existingTests=8,sameExecRequired=True,oldExecUnion=False,
        metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,originalCandidateTokens=732,
        ownedPublicTrace=dict(path=contract.FILE,sha256=data.sha(contract.EXPECTED),fixedBytes=contract.EXPECTED.decode(),sourceTestSha256=contract.TEST_SHA),
        standardEntropyFactoryScope='Existing public-ID format test only; no secret/key/session/provider configuration or raw random output persistence',
        specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),
        judgement='WHOLE12_PUBLIC_IDENTIFIER_FIXED_PROVIDER_RECOVERY_STANDARD_PUBLIC_FACTORY_ONE_OWNED_PUBLIC_TRACE',
        productTestsExecuted=0,newAccepted=0,whole451Accepted=False,externalBusinessActions=0))
    print(json.dumps(dict(actualExit=0,cases=len(cases),negativeVectors=len(labels),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))

if __name__ == '__main__': main()
