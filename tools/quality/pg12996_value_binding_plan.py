"""Freeze two distinct whole new memory Tests, never extract held original tests."""
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

SOURCE = '94eeea264b449e5826f292c746a9cd4655b3122a'
BEFORE = '762568bb0338749c9549ec937cc2c79e84418836'
ROOT = 'src/schubert-nk-api/src/'
PACKAGE = '/java/dev/codex/schubert/nk/api/application/'
OUT = data.BASE/'PG12996-value-binding-plan-v1'

def tokens(s): return [m.group() for m in LEX.finditer(s) if not m.group().startswith(('//','/*'))]

def inverse(old,new):
    ts = tokens(new); decl = tokens('private static final String AUDIO_LOGICAL_ID = "700";')
    hits = [i for i in range(len(ts)) if ts[i:i+len(decl)] == decl]; assert len(hits) == 1
    i = hits[0]; del ts[i:i+len(decl)]
    assert ts.count('AUDIO_LOGICAL_ID') == 6
    assert [('"700"' if x == 'AUDIO_LOGICAL_ID' else x) for x in ts] == tokens(old)

def main():
    invocation = capture(__file__); assert not OUT.exists()
    n = data.read_checked(data.BASE/'PG12974-query-binding-six-compile-v1/manifest.json','f3134ed6a743744068faa3c45142bb6a558ab5526aeccebad9e8d3d1b0ca005d')
    p = data.read_checked(data.BASE/'PG12994-value-binding-preflight-v2/manifest.json','2f2df02a4403be1446e8d0c4482e73fcd19f7be2340831980f9087f37463be9f')
    assert n['source'] == p['baseSource'] == BEFORE and n['actualExit'] == n['testsExecuted'] == p['actualExit'] == 0
    assert all(v['findings'] == v['processingErrors'] == 0 for v in p['reports'].values())
    assert all(data.sha((data.ROOT/path).read_bytes()) == digest for path,digest in n['begin']['inputHashes'].items())
    assert all(data.sha((data.ROOT/path).read_bytes()) == digest for path,digest in p['candidateSourceHashes'].items())
    cases = []; whole = {}; support = {}; main_hashes = {}
    for part,name,count in [('media','MediaRequestDescriptorBindingTest',4),('scenario','ScenarioScriptFileBindingTest',2)]:
        path = ROOT+'test'+PACKAGE+part+'/'+name+'.java'; text = (data.ROOT/path).read_text()
        assert not any(x in text for x in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','System.getenv','System.setProperty','getConnection(','setAccessible','Repository','TemporaryInfrastructureException','WebStartupException','.query(','.canonical('])
        methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(',text)
        assert len(methods) == len(set(methods)) == text.count('@Test') == count
        whole[path] = data.sha(text.encode())
        cases.extend(dict(className=path.split('/java/',1)[1][:-5].replace('/','.'),method=m,path=path,sourceSha256=whole[path]) for m in methods)
        prefix = ROOT+'test'+PACKAGE+part+'/'+('MediaRequestFixture' if part == 'media' else 'ScenarioRequestFixture')+'.java'
        fixture = (data.ROOT/prefix).read_text()
        assert not any(x in fixture for x in ['Repository','java.nio.file','java.net.','java.sql.','ProcessBuilder','getConnection(','TemporaryInfrastructureException','WebStartupException'])
        support[prefix] = p['candidateSourceHashes'][prefix]
        subject = ROOT+'main'+PACKAGE+part+'/'+('MediaRequest' if part == 'media' else 'ScenarioRequest')+'.java'
        main_hashes[subject] = p['candidateSourceHashes'][subject]
    changed = subprocess.check_output(['git','diff','--name-only','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT).decode().split('\0')[:-1]
    assert changed == sorted(whole)
    old = (data.BASE/'PG12993-value-binding-style-before-v1/candidate.java.txt').read_text()
    new = (data.ROOT/changed[0]).read_text(); inverse(old,new); negative = []
    for a,b in [('AUDIO_LOGICAL_ID = "700"','AUDIO_LOGICAL_ID = "701"'),('audio("701", disposition)','audio("702", disposition)'),('assertEquals(1, descriptor.byteLength())','assertEquals(2, descriptor.byteLength())'),('000000000700','000000000701'),('"audio/ogg"','"audio/wav"'),('List.of("ANMREQ01"','List.of("XXXREQ01"')]:
        assert a in new
        try: inverse(old,new.replace(a,b,1))
        except AssertionError: negative.append(a)
        else: raise AssertionError('non-equivalent test oracle accepted')
    spec = 'evidence/01_PT/018_NK-OPS-001/2401_P008P009独立値束縛_単体テスト仕様書.md'
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceBefore=BEFORE,invocation=invocation,
        totalCorrections=1,candidateStyleCorrectionNotBaseline=True,originalCandidateTokenCount=len(tokens(old)),inverseNegativeVectors=negative,
        sourceChanges=[dict(path=path,kind='NEW_TEST_ONLY',sha256=whole[path]) for path in changed],
        eligibilityClosureSourceHashes=main_hashes,wholeTestSourceHashes=whole,supportTestSourceHashes=support,cases=cases,
        originalTests=6,originalSuites=2,newTestIds=6,existingTests=0,heldOriginalTests=6,sameExecRequired=True,oldExecUnion=False,
        specificationPath=spec,specificationSha256=data.sha((data.ROOT/spec).read_bytes()),
        judgement='WHOLE_NEW_SIX_DISTINCT_VALUE_BINDING_TESTS_PURE_TWO_FIXTURES_PUBLIC_MESSAGE_UUID_NO_REPOSITORY_QUERY_JCE_OR_FILES',
        productTestsExecuted=0,newAccepted=0,whole451Accepted=False,externalActions=0))
    print(json.dumps(dict(actualExit=0,cases=len(cases),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))

if __name__ == '__main__': main()
