"""Whole ordinary JDBC proxy profile admission; no backend, driver, actual4 or partial Test extraction."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg27232-web-receipt12-profile-v1';O=B/'evidence/PG27233-web-receipt12-preflight-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();pp=B/'evidence/PG27232-web-receipt12-profile-v1/manifest.json';m=load(pp);assert m['actualExit']==0 and m['expectedTests']==12
assert all(sha(R/p)==h for p,h in m['inputHashes'].items())
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
assert len(m['physicalClassHashes'])==7 and m['apiWholeJarHashedOrOtherEntryPayloadRead'] is False
n=load(R/m['normalMain']['path']);assert sha(R/m['normalMain']['path'])==m['normalMain']['sha256'] and n['actualExit']==0 and n['testsExecuted'] is False
for p in m['apiMainSources']:assert n['begin']['inputHashes'][p]==m['inputHashes'][p]
for p,h in m['physicalClassHashes'].items():assert n['normalPhysicalClassHashes']['web:'+p]==h
for p,h in m['dependencies'].items():assert sha(Path(p))==h
p=R/m['apiTestSources'][0];old=subprocess.check_output(['git','show','adfcd9f778100624aac179f36690f5165f46f911:'+str(p.relative_to(R))],text=True);s=p.read_text()
a='''    try (var workers = Executors.newFixedThreadPool(2)) {
      var first =''';b='''    var workers = Executors.newFixedThreadPool(2);
    try {
      var first =''';x='''    }
    assertEquals(2, fixture.connections.size());
    assertNotSame(fixture.connections.getFirst(), fixture.connections.getLast());''';y='''    } finally {
      workers.shutdownNow();
      if (!workers.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("receipt reference workers did not terminate");
      }
    }
    assertEquals(2, fixture.connections.size());
    assertNotSame(fixture.connections.getFirst(), fixture.connections.getLast());''';assert s.count(b)==s.count(y)==1 and s.replace(b,a).replace(y,x)==old
p=R/m['apiTestSources'][1];assert sha(p)==hashlib.sha256(subprocess.check_output(['git','show','adfcd9f778100624aac179f36690f5165f46f911:'+str(p.relative_to(R))])).hexdigest()
sp=B/'evidence/PG27236-web-receipt12-static-v1/manifest.json';st=load(sp);assert st['inputHashes']==m['inputHashes'] and st['actualExit']==0 and not st['processingErrors'] and st['checkstyleFindings']==0
expected={('ReceiptFailureGraph329Test.java','AvoidLiteralsInIfCondition','141'),*[('ReceiptFailureGraph329Test.java','UseProperClassLoader',x) for x in ['173','186','216','237']],('ReceiptReferencePortTest.java','CloseResource','364'),('ReceiptReferencePortTest.java','DoNotThrowExceptionInFinally','374'),('ReceiptReferencePortTest.java','UseConcurrentHashMap','523'),('ReceiptReferencePortTest.java','UseProperClassLoader','594'),*[('ReceiptReferencePortTest.java','DoNotUseThreads',x) for x in ['364','366','367','375','376']]};assert len(expected)==14 and {(Path(x['path']).name,x['rule'],x['line']) for x in st['rawFindings']}==expected
classified=[]
for x in st['rawFindings']:
 if x['rule']=='UseProperClassLoader':reason='ProxyexplicitJDBCinterfaceclassloader forstandaloneJUnit; noJ2EE/container/contextloader needed ordesired, no alternativeaccessroute.'
 elif x['rule']=='AvoidLiteralsInIfCondition':reason='Closed0/1/2 cause/suppressed/next graphfixture independentmapping; notproductionbusinessmagic.'
 elif x['rule']=='UseConcurrentHashMap':reason='Statementbindingsmap confinedtooneprivateConn, eachparallelreadcreatesdifferentConn/Statement/ResultSet; no concurrentwrites tosameMap.'
 elif x['rule']=='CloseResource':reason='OwnedexecutorfinallyshutdownNow/await10, revertingtoTWRwouldrestoreunboundedclose.'
 elif x['rule']=='DoNotThrowExceptionInFinally':reason='Ownedworkerterminationfailure mustfailJUnit, never masksproductfailureasPASS; noapplicationexceptionpolicy change.'
 else:reason='StandalonewholeJUnit privateinterfaceproxies withFuture5/finallyawait10; no server/backend access.'
 classified.append(dict(**x,disposition='NOT_APPLICABLE_EXPLICIT_ORDINARY_TEST_CONTEXT',reason=reason))
for manifest,stages in [(pp,m['stages']),(sp,st['stages'])]:
 for label,v in stages.items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(manifest.parent/(label+'.'+stream))==v[stream+'Sha256']
ns=B/'evidence/PG22106-api-stop-static-independent-input-v1/six-static.json';v=load(ns);assert sha(ns)=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2';sb=Path(v['reports']['web']['path']);assert sha(sb)==v['reports']['web']['sha256'];rt=ET.parse(sb).getroot();assert not any(rt.findall('.//'+tag) for tag in ['BugInstance','MissingClass','Error']);stats={x.get('class') for x in rt.findall('.//ClassStats')};assert {x[:-6].replace('/','.') for x in m['apiExactReadClassEntries'] if not x.endswith('package-info.class')}<=stats
style=B/'evidence/PG22122-current7aed-lineage-style-v1/manifest.json';ms=load(style);assert ms['actualExit']==ms['applicableViolations']==ms['unclassified']==ms['checkstyle']==0;arts=style.parent/'artifacts.json';assert sha(arts)==ms['files']['artifacts.json'];rows={x['path']:x for x in load(arts)}
for p in m['apiMainSources']:assert rows[p]['sha256']==m['inputHashes'][p]
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(x.endswith('/'+h+'.class') for x in m['physicalClassHashes'] for h in held)
O.mkdir();out=dict(actualExit=0,inputHashes=m['inputHashes'],prepare=ref(pp),normalStatic=ref(ns),mainStyle=ref(style),testStyle=ref(sp),classified=classified,expectedTests=12,fullPhysicalClasses=7,originalNineOraclesByteInverse=True,graphThreeUnchanged=True,newDefinitions=0,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,pmdRawFindings=14,manualSuppressionAdded=False,actualBackendOrHeldClassActions=0,wholeControllerOrDbFixturesExtracted=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'))))
