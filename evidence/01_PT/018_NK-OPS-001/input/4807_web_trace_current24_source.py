"""Safe source and original-whole-fixture admission only, not a product runtime."""
from pathlib import Path
import datetime,hashlib,json,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=load(b/'evidence/PG27620-caddy-context24-normal-v1/manifest.json');final=load(b/'evidence/PG27632-caddy-context24-independent-v1/manifest.json');audit=load(b/'evidence/PG37746-web-request-trace-applicability-v1/source-dependency-applicability.json');assert audit['actualExit']==0
main=old['apiMainSources'];tests=old['apiTestSources'];assert len(main)==20 and len(tests)==5
for n in main+tests:
    s=(r/n).read_text();assert sha(r/n)==final['inputHashes'][n]
    assert not any(x in s for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','ProcessBuilder','DriverManager','DataSource','Class.forName','setAccessible','@BeforeAll','java.net.Socket'])
    if 'java.nio.file' in s:
        assert Path(n).name=='WebRequestTraceTest.java' and '/src/test/java/' in n
        assert 'nk.pt.repository' in s and 'Files.list(controllers)' in s
sdk={n:h for n,h in old['dependencies'].items() if '/toolchain/m2/repository/' in n}
previous=[n for n in sdk if '/commons-logging/' in n];assert len(previous)==1
sdk.pop(previous[0]);current=load(b/'evidence/PG37690-web-enum-eight-source-closure-v1/manifest.json')['sdkHashes'];sdk.update(current)
assert all(sha(Path(n))==h for n,h in sdk.items())
counts=[];expected=[]
for n in tests:
    text=(r/n).read_text();methods=re.findall(r'@Test\s*(?:@Timeout\([^\n]+\)\s*)?void (\w+)\s*\(',text)
    counts.append(dict(path=n,tests=len(methods),sha256=sha(r/n)));expected.extend(dict(classname=n.split('/src/test/java/')[1][:-5].replace('/','.'),name=x+'()') for x in methods)
assert expected==old['expectedCases'] and len(expected)==24 and sorted(x['tests'] for x in counts)==[1,3,5,5,10]
fixtures={n:sha(r/n) for n in old['inputHashes'] if '/controller/' in n or n.endswith('/config/WebMvcConfiguration.java')};assert len(fixtures)==14
out=b/'evidence/PG37756-web-trace-current24-source-v1';assert not out.exists();out.mkdir()
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),mainSources=main,testSources=counts,expectedCases=expected,sdkHashes=sdk,sourceHashes={n:sha(r/n) for n in main+tests},readonlyFixtureHashes=fixtures,readonlySourceInventoryNotExecutablePermission=True,wholeOriginal24OracleUnchanged=True,commonsLoggingCurrentVersion='1.4.0',actualRootVmDbNativeKeysAuthorityActions=0,heldClassfileActions=0,productTestsExecuted=0,newAcceptance=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,main=20,wholeFixtures=5,expectedTests=24,readonlyFixtures=14))
