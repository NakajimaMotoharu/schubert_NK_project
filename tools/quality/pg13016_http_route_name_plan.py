"""Exact private Main name and outer Test TWR inverse; fixed whole6 and classpath resource."""
import json
import re
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from public_java_digest_provenance import LEX

SOURCE = '2f4290e7e511ea30224d087f78d44964d3488919'
BEFORE = '94eeea264b449e5826f292c746a9cd4655b3122a'
MAIN = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/HttpMetricContract.java'
TEST = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/monitoring/HttpMetricContractTest.java'
RESOURCE = 'src/schubert-nk-web/src/test/resources/monitoring/http-route-labels.txt'
RESOURCE_SHA = '1777c4710e6448bdb459d5fd2beccf389f57ec4ea9effdca171cdbd6888d5331'
OUT = data.BASE/'PG13016-http-route-name-plan-v1'

def tokens(s): return [m.group() for m in LEX.finditer(s) if not m.group().startswith(('//','/*'))]

def require_main(old,new):
    ts = tokens(new); assert ts.count('ROUTES_BY_TEMPLATE') == 2 and tokens(old).count('INDEX') == 2
    assert [('INDEX' if x == 'ROUTES_BY_TEMPLATE' else x) for x in ts] == tokens(old)

def require_test(old,new):
    ts = tokens(new); needle = ['try','(','executor',')','{']
    hits = [i for i in range(len(ts)) if ts[i:i+5] == needle]; assert len(hits) == 1
    i = hits[0]; depth = 1; j = i+5
    while depth:
        assert j < len(ts)
        if ts[j] == '{': depth += 1
        elif ts[j] == '}': depth -= 1
        j += 1
    assert j < len(ts); del ts[j-1]; del ts[i:i+5]
    assert ts == tokens(old)

def main():
    invocation = capture(__file__); assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG12998-value-binding-six-compile-v1/manifest.json','f391201e726c7e4ad28b86b4e8d5ef332e2c06cfdca02d4df05529f332f8e730')
    pre = data.read_checked(data.BASE/'PG13014-http-route-name-preflight-v2/manifest.json','70461a031e27a8c36a6fb1ffb36d7d4d9e1567ea5d79f092ddaf6fc7d3a41c7d')
    assert normal['source'] == pre['baseSource'] == BEFORE and normal['actualExit'] == normal['testsExecuted'] == 0
    assert pre['actualExit'] == 1 and pre['reports']['pmd']['findings'] == 4 and pre['reports']['checkstyle']['findings'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items() if p not in {MAIN,TEST})
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in pre['candidateSourceHashes'].items())
    changed = subprocess.check_output(['git','diff','--name-only','-z',BEFORE,SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=data.ROOT).decode().split('\0')[:-1]
    assert changed == [MAIN,TEST]
    originals = data.BASE/'PG13013-http-route-originals-v1'; record = json.loads((originals/'manifest.json').read_bytes())
    assert record['source'] == BEFORE and record['actualExit'] == record['productTestsExecuted'] == 0
    old_main = (originals/'HttpMetricContract.java.txt').read_text(); old_test = (originals/'HttpMetricContractTest.java.txt').read_text()
    assert data.sha(old_main.encode()) == record['originalSourceHashes'][MAIN] == normal['begin']['inputHashes'][MAIN] == '28fd83122a743c9393311d37c6e288c7a4851ad22a4d2312f59c2fb27b8fd4c3'
    assert data.sha(old_test.encode()) == record['originalSourceHashes'][TEST] == normal['begin']['inputHashes'][TEST]
    main_text = (data.ROOT/MAIN).read_text(); test_text = (data.ROOT/TEST).read_text()
    require_main(old_main,main_text); require_test(old_test,test_text)
    labels = []
    for text,original,check,old,new in [
        (main_text,old_main,require_main,'ROUTES_BY_TEMPLATE','OTHER_LOOKUP'),
        (main_text,old_main,require_main,'UNKNOWN);','ROOT);'),
        (main_text,old_main,require_main,'"nk_http_requests_total"','"other"'),
        (test_text,old_test,require_test,'index < 64','index < 63'),
        (test_text,old_test,require_test,'executor.shutdownNow()','executor.shutdown()'),
        (test_text,old_test,require_test,'awaitTermination(10, TimeUnit.SECONDS)','awaitTermination(9, TimeUnit.SECONDS)')]:
        assert old in text
        try: check(original,text.replace(old,new,1))
        except AssertionError: labels.append(old)
        else: raise AssertionError('non-equivalent code/oracle accepted')
    assert not any(word in test_text for word in ['@Before','@After','@ExtendWith','@Disabled','@TempDir','java.net.','java.sql.','java.nio.file','ProcessBuilder','System.getenv','System.setProperty','Class.forName','TemporaryInfrastructureException','WebStartupException'])
    assert test_text.count('getResourceAsStream(') == 1 and '"/monitoring/http-route-labels.txt"' in test_text
    assert data.sha((data.ROOT/RESOURCE).read_bytes()) == normal['begin']['inputHashes'][RESOURCE] == RESOURCE_SHA
    methods = re.findall(r'@Test\s+void\s+(\w+)\s*\(',test_text); assert len(methods) == len(set(methods)) == test_text.count('@Test') == 6
    cases = [dict(className='dev.codex.schubert.nk.web.monitoring.HttpMetricContractTest',method=m,path=TEST,sourceSha256=pre['candidateSourceHashes'][TEST]) for m in methods]
    spec = 'evidence/01_PT/018_NK-OPS-001/2404_HTTP私有index命名_製造単体仕様.md'
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,sourceBefore=BEFORE,invocation=invocation,totalCorrections=2,
        sourceChanges=[dict(path=p,sha256=pre['candidateSourceHashes'][p]) for p in changed],
        originalTokenCounts=dict(main=len(tokens(old_main)),test=len(tokens(old_test))),inverseNegativeVectors=labels,
        originalsManifestSha256=data.sha((originals/'manifest.json').read_bytes()),
        eligibilityClosureSourceHashes={MAIN:pre['candidateSourceHashes'][MAIN]},wholeTestSourceHashes={TEST:pre['candidateSourceHashes'][TEST]},supportTestSourceHashes={},
        reviewedResourceHashes={RESOURCE:RESOURCE_SHA},cases=cases,originalTests=6,originalSuites=1,newTestIds=0,existingTests=6,sameExecRequired=True,oldExecUnion=False,
        specificationPath=spec,specificationSha256=data.sha((data.ROOT/spec).read_bytes()),
        judgement='PRIVATE_MAIN_FIELD_TWO_IDENTIFIERS_AND_OUTER_TEST_TWR_ONLY_WHOLE_SIX_MEMORY_WITH_ONE_FIXED_CLASSPATH_RESOURCE',
        productTestsExecuted=0,newAccepted=0,whole451Accepted=False,externalActions=0))
    print(json.dumps(dict(actualExit=0,cases=len(cases),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))

if __name__ == '__main__': main()
