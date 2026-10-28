"""Whole seventeen business cases; exact original tokens after only two finally wrappers."""
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

SOURCE = '4a3fad244f21530547fdc79b16f9ea3af0ca13af'
BEFORE = '5590eee0d766fdd48e56d95f6b33ce729accbd00'
MAIN = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/'
CHANGED = TEST+'JmsRequestReplyClientTest.java'
NEW = TEST+'JmsRequestReplyCleanupTest.java'
OUT = data.BASE/'PG12918-coordinator-corrected-plan-v1'

def tokens(s):
    return [m.group() for m in LEX.finditer(s) if not m.group().startswith(('//','/*'))]

def replace(ts,old,new):
    a,b = tokens(old),tokens(new)
    found = [i for i in range(len(ts)) if ts[i:i+len(a)] == a]
    assert len(found) == 1
    i = found[0]
    return ts[:i]+b+ts[i+len(a):]

def require(old,new):
    t = tokens(new)
    positions = [i for i,x in enumerate(t) if x == 'currentInstant']
    assert len(positions) == 4 and all(t[i+1] != '(' for i in positions)
    t = ['instant' if x == 'currentInstant' else x for x in t]
    t = replace(t,'waiting.start(); try {','waiting.start();')
    t = replace(t,'} finally { waiting.interrupt(); waiting.join(2_000); }','')
    t = replace(t,'try (ExecutorService executor = Executors.newFixedThreadPool(maximum)) { try {','try (ExecutorService executor = Executors.newFixedThreadPool(maximum)) {')
    t = replace(t,'} finally { release.countDown(); }','')
    assert t == tokens(old)

def main():
    invocation = capture(__file__); assert not OUT.exists()
    n = data.read_checked(data.BASE/'PG12892-reply-terminal-six-compile-v1/manifest.json','f018c19fbaabdc7de2253f8b12a57c86a532177ea40fc9b5448b461aa20ce532')
    assert n['source'] == BEFORE and n['actualExit'] == n['testsExecuted'] == 0
    before = subprocess.check_output(['git','show',BEFORE+':'+CHANGED],cwd=data.ROOT,text=True)
    current = (data.ROOT/CHANGED).read_text(); require(before,current)
    negatives = []
    for a,b in [('waiting.start();',''),('waiting.interrupt();',''),('waiting.join(2_000);','waiting.join(2_001);'),('release.countDown();','release.countDown(); release.countDown();'),('sent.await(2, TimeUnit.SECONDS)','sent.await(1, TimeUnit.SECONDS)'),('new byte[] {7}','new byte[] {8}'),('public Instant instant()','public Instant currentInstant()'),('return currentInstant.get();','return NOW;')]:
        bad = current.replace(a,b,1); assert bad != current
        try: require(before,bad)
        except AssertionError: negatives.append(a)
        else: raise AssertionError('changed original oracle/control accepted')
    changed = subprocess.check_output(['git','diff','--name-only','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT).decode().split('\0')[:-1]
    assert set(changed) == {CHANGED,NEW}
    hashes = n['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes()) == digest for path,digest in hashes.items() if path != CHANGED)
    reviewed = {MAIN+name+'.java':data.sha((data.ROOT/(MAIN+name+'.java')).read_bytes()) for name in ['JmsRequestReplyClient','JmsRequestReplyException','ReplyCorrelationRegistry','PendingReply','JmsRequestSender']}
    topology = 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/BrokerTopology.java'
    reviewed[topology] = hashes[topology]
    cases = []; whole = {}
    for name,count in [('JmsRequestReplyClientTest',8),('ReplyCorrelationRegistryTest',5),('JmsRequestReplyCleanupTest',4)]:
        path = TEST+name+'.java'; text = (data.ROOT/path).read_text()
        assert not any(word in text for word in ['@Before','@After','@Disabled','@ExtendWith','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','Class.forName','System.getenv','System.setProperty','setAccessible','TemporaryInfrastructureException','WebStartupException'])
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(',text); assert len(methods) == len(set(methods)) == count
        whole[path] = data.sha(text.encode())
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=m,path=path,sourceSha256=whole[path]) for m in methods)
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2393_P005同期失敗後回復_単体テスト仕様書.md'
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceBefore=BEFORE,invocation=invocation,
        totalCorrections=2,sourceChanges=[dict(path=CHANGED,beforeSha256=hashes[CHANGED],sha256=whole[CHANGED],kind='FINALLY_AND_FOUR_FIELD_IDENTIFIERS_ONLY'),dict(path=NEW,sha256=whole[NEW],kind='NEW_TEST_ONLY')],
        eligibilityClosureSourceHashes=reviewed,wholeTestSourceHashes=whole,supportTestSourceHashes={},cases=cases,
        originalTests=17,originalSuites=3,newTestIds=4,existingTests=13,sameExecRequired=True,oldExecUnion=False,
        metadataNegativeVectors=len(negatives),nonVacuousNegativeLabels=negatives,originalWholeTokensPreserved=2404,
        compileTimeConstantOnly='LayoutDefinition.HEADER_LENGTH=256; no executable layout call',
        specificationPath=str(spec.relative_to(data.ROOT)),specificationSha256=data.sha(spec.read_bytes()),
        judgement='WHOLE17_MEMORY_CALLBACK_CLOCK_EXCEPTIONS_BOUNDED_OWNED_WORKERS_NO_JMS_PROVIDER_OR_EXTERNAL',
        productTestsExecuted=0,newAccepted=0,whole451Accepted=False,externalActions=0))
    print(json.dumps(dict(actualExit=0,cases=len(cases),negatives=len(negatives),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))

if __name__ == '__main__': main()
