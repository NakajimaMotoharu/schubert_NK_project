"""Fixed whole in-memory business PT scope, with original evidence/history not replayed."""
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = '5590eee0d766fdd48e56d95f6b33ce729accbd00'
BEFORE = '105fd644e90918945607b3ac3e4962843c7762bf'
PREFIX = 'src/schubert-nk-web/src/'
MAIN = PREFIX + 'main/java/dev/codex/schubert/nk/web/messaging/'
TEST = PREFIX + 'test/java/dev/codex/schubert/nk/web/messaging/'
OUT = data.BASE / 'PG12894-reply-terminal-plan-v1'

def main():
    invocation = capture(__file__)
    assert not OUT.exists()
    changed = subprocess.check_output(['git', 'diff', '--name-only', '-z', BEFORE, SOURCE, '--', 'src', 'pom.xml', '.mvn', 'mvnw'], cwd=data.ROOT).decode().split('\0')[:-1]
    assert changed == [TEST + 'ReplyCorrelationTerminalRaceTest.java']
    n = data.read_checked(data.BASE/'PG12870-pure-health-lifecycle-six-compile-v1/manifest.json', 'bc906632f1a362e7d688ac472784c1e4438008421799f7fec927dad8c818b52a')
    assert n['source'] == BEFORE and n['actualExit'] == n['testsExecuted'] == 0
    hashes = n['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes()) == digest for path, digest in hashes.items())
    reviewed = {MAIN+name+'.java': data.sha((data.ROOT/(MAIN+name+'.java')).read_bytes()) for name in ['ReplyCorrelationRegistry', 'PendingReply']}
    whole = {}; cases = []
    for name, count in [('ReplyCorrelationRegistryTest', 5), ('ReplyCorrelationTerminalRaceTest', 4)]:
        path = TEST+name+'.java'; text = (data.ROOT/path).read_text()
        assert not any(word in text for word in ['@Before', '@After', '@Disabled', '@ExtendWith', '@TempDir', 'java.net.', 'java.sql.', 'java.nio.file', 'ProcessBuilder', 'Class.forName', 'System.getenv', 'System.setProperty', 'setAccessible', 'TemporaryInfrastructureException', 'WebStartupException'])
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(', text)
        assert len(methods) == len(set(methods)) == count
        whole[path] = data.sha(text.encode())
        cases.extend(dict(className=path.split('/java/', 1)[1][:-5].replace('/', '.'), method=method, path=path, sourceSha256=whole[path]) for method in methods)
    design = 'documents/300_SS/320_メッセージング/321_Artemis物理構成・JMS設定設計.md'
    official = subprocess.check_output(['git', 'show', 'origin/main:'+design], cwd=data.ROOT)
    assert b'ConcurrentHashMap<UUID, PendingReply>' in official
    spec = data.ROOT/'evidence/01_PT/018_NK-OPS-001/2391_P005応答終端競合_単体テスト仕様書.md'
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json', dict(actualExit=0, source=SOURCE, sourceBefore=BEFORE, invocation=invocation,
        totalCorrections=0, originalTests=9, originalSuites=2, newTestIds=4, existingTests=5,
        eligibilityClosureSourceHashes=reviewed, wholeTestSourceHashes=whole, supportTestSourceHashes={},
        sourceChanges=[dict(path=changed[0], kind='NEW_TEST_ONLY', sha256=whole[changed[0]])], cases=cases,
        officialDesign=dict(path=design, ref='origin/main', sha256=data.sha(official)),
        specificationPath=str(spec.relative_to(data.ROOT)), specificationSha256=data.sha(spec.read_bytes()),
        sameExecRequired=True, oldExecUnion=False, productTestsExecuted=0, newAccepted=0,
        judgement='WHOLE_NINE_PURE_MEMORY_REGISTRY_TERMINAL_ARBITRATION_WITH_FINITE_OWNED_WORKERS',
        historicalE7AcceptanceNotNewCredit=True, allOriginalMainTestInputsUnchanged=True,
        externalActions=0, whole451Accepted=False, effortPercent=None))
    print(json.dumps(dict(actualExit=0, cases=len(cases), manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))

if __name__ == '__main__':
    main()
