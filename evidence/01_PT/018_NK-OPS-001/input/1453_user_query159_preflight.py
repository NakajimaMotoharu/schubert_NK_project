"""Current159 complete whitelist/byte/style admission, zero runtime operations."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg27052-user-query159-profile-v1';O=B/'evidence/PG27056-user-query159-preflight-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists()
prepare=B/'evidence/PG27052-user-query159-profile-v1/manifest.json';m=load(prepare);assert m['actualExit']==0 and m['expectedTests']==159
assert all(sha(R/p)==h for p,h in m['inputHashes'].items());assert len(m['physicalClassHashes'])==192 and m['physicalClassHashes']=={str(p.relative_to(W/'component')):sha(p) for p in (W/'component').rglob('*.class')}
assert m['testClassHashes']=={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')}
assert m['apiWholeJarHashedOrOtherEntryPayloadRead'] is False and len(m['apiExactReadClassEntries'])==11
normal=load(R/m['normalMain']['path']);assert sha(R/m['normalMain']['path'])==m['normalMain']['sha256'] and normal['actualExit']==0 and normal['testsExecuted'] is False
for p in m['apiMainSources']:assert normal['begin']['inputHashes'][p]==m['inputHashes'][p]
for n in m['apiExactReadClassEntries']:assert normal['normalPhysicalClassHashes']['api:'+n]==m['physicalClassHashes'][n]
for p,h in m['dependencies'].items():assert sha(Path(p))==h
stage=m['stages']['test-compile'];assert stage['actualExit']==0 and not stage['timedOut']
for stream in ['stdout','stderr']:assert sha(prepare.parent/('test-compile.'+stream))==stage[stream+'Sha256']
style=B/'evidence/PG27054-user-query159-static-v1/manifest.json';s=load(style);assert s['actualExit']==0 and s['inputHashes']==m['inputHashes'] and not s['processingErrors'] and s['checkstyleFindings']==0
expected={('UserQueryCanonicalCoreTest.java','CloseResource','67'),('UserQuerySqlContractTest.java','UseProperClassLoader','309'),('UserQuerySqlContractTest.java','UseConcurrentHashMap','317')}
assert len(s['rawFindings'])==3 and {(Path(x['path']).name,x['rule'],x['line']) for x in s['rawFindings']}==expected
reasons={'CloseResource':'canonical.fields().get borrows a field owned by surrounding canonical TWR; closing borrowed field here would violate ownership, outer canonical closes all fields.','UseProperClassLoader':'Standalone JUnit public JDK-interface proxy, no JavaEE container or application classloader isolation.','UseConcurrentHashMap':'One fixture map confined to synchronous sequential JDBC interface callbacks; no thread/executor/parallel stream.'}
classified=[dict(**x,disposition='NOT_APPLICABLE_EXPLICIT_TEST_CONTEXT',reason=reasons[x['rule']]) for x in s['rawFindings']]
for label,stage in s['stages'].items():
 assert stage['actualExit']==(4 if label=='pmd' else 0) and not stage['timedOut']
 for stream in ['stdout','stderr']:assert sha(style.parent/(label+'.'+stream))==stage[stream+'Sha256']
normalStatic=B/'evidence/PG22106-api-stop-static-independent-input-v1/six-static.json';ns=load(normalStatic);assert sha(normalStatic)=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2'
sb=Path(ns['reports']['api']['path']);assert sha(sb)==ns['reports']['api']['sha256'];root=ET.parse(sb).getroot();assert not any(root.findall('.//'+tag) for tag in ['BugInstance','MissingClass','Error'])
stats={x.get('class') for x in root.findall('.//ClassStats')};assert {n.removesuffix('.class').replace('/','.') for n in m['apiExactReadClassEntries'] if not n.endswith('/package-info.class')}<=stats
mainStyle=B/'evidence/PG22122-current7aed-lineage-style-v1/manifest.json';ms=load(mainStyle);assert ms['actualExit']==ms['applicableViolations']==ms['unclassified']==ms['checkstyle']==0
arts=mainStyle.parent/'artifacts.json';assert sha(arts)==ms['files']['artifacts.json'];rows={x['path']:x for x in load(arts)}
for p in m['apiMainSources']:assert rows[p]['sha256']==m['inputHashes'][p]
canon=load(R/m['canonicalProof']['path']);assert sha(R/m['canonicalProof']['path'])==m['canonicalProof']['sha256'] and canon['actualExit']==canon['staticApplicable']==0
assert all(m['physicalClassHashes'][p]==h for p,h in canon['physicalClassHashes'].items())
assert all(m['inputHashes'][p]==h for p,h in canon['inputHashes'].items())
protoPost=B/'evidence/PG26312-protocol-unicode-full130-independent-v1/manifest.json';pp=load(protoPost);assert pp['actualExit']==0 and pp['tests']==130 and all(pp['static'][k]==0 for k in ['applicable','unclassified','checkstyle','processingErrors','spotbugsBugs','spotbugsMissing','spotbugsErrors'])
pt=load(R/m['protoTest']['path']);assert sha(R/m['protoTest']['path'])==m['protoTest']['sha256']
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']
assert not any(n.endswith('/'+h+'.class') for n in m['physicalClassHashes'] for h in held)
for p in m['apiTestSources']:assert not any(x in (R/p).read_text() for x in held+['@BeforeAll','@TempDir','DriverManager','DataSource','getConnection(','ProcessBuilder','Class.forName('])
# Main repository names a fatal helper on unexecuted error paths; no actual held payload exists.
# Do not claim pure-value-only or complete Repository/error-branch acceptance.
O.mkdir();v=dict(actualExit=0,inputHashes=m['inputHashes'],dependencies=m['dependencies'],prepare=ref(prepare),normalStatic=ref(normalStatic),mainStyle=ref(mainStyle),canonicalProof=m['canonicalProof'],currentProtocolPost=ref(protoPost),testStyle=ref(style),classified=classified,expectedTests=159,fullPhysicalClasses=192,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,pmdRawFindings=3,pmdRawExit=4,suppressionAdded=False,actualJdbcBackendConnected=False,repositoryExceptionalBranchesNotAccepted=True,heldActualClassBinaryOrBackendActions=0,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expectedTests=159,fullPhysical=192,manifest=ref(O/'manifest.json'))))
