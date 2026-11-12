from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg27600-trace-menu24-normal-v1';O=B/'evidence/PG27608-trace-menu24-preflight-v1';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();pp=B/'evidence/PG27600-trace-menu24-normal-v1/manifest.json';m=ld(pp);assert m['actualExit']==0 and m['expectedTests']==24 and len(m['selectedClasses'])==5 and m['MainSourceSubsetCount']==20
for p,h in m['inputHashes'].items():assert sha(R/p)==h
for p,h in m['dependencies'].items():assert sha(Path(p))==h
for folder,key in [('component','physicalClassHashes'),('target/classes','mainClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
assert len(m['physicalClassHashes'])==199 and len(m['mainClassHashes'])==23;assert len(m['dependencies'])>3 and not any('schubert-nk-web-' in p or 'schubert-nk-api-' in p or 'postgresql-' in p or 'artemis-' in p for p in m['dependencies'])
ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;original=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');copied=ET.parse(W/'pom.xml').getroot().find('.//'+tag('plugin'));assert ET.tostring(original)==ET.tostring(copied) and sha(W/'pom.xml')==m['subsetPomSha256'];assert '-Xep:NullAway:ERROR' in ET.tostring(copied).decode() and '-Werror' in ET.tostring(copied).decode()
sp=B/'evidence/PG27602-trace-menu24-static-v1/manifest.json';st=ld(sp);assert st['actualExit']==0 and st['inputHashes']==m['inputHashes'] and not st['processingErrors'] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors']);expected={('WebRequestTrace.java','AvoidUsingVolatile','64'),('WebRequestTrace.java','CloseResource','137'),*[('WebRequestTrace.java','DoNotUseThreads',x) for x in ['188','194','202']],*[('WebRequestTrace.java','CompareObjectsWithEquals',x) for x in ['202','205']],('MenuAuditContractTest.java','UseProperClassLoader','107'),('MenuAuditContractTest.java','CloseResource','145'),*[('MenuAuditContractTest.java','DoNotUseThreads',x) for x in ['145','147','149','150']],*[('WebRequestTraceTest.java','CloseResource',x) for x in ['280','309']],*[('WebRequestTraceTest.java','DoNotUseThreads',x) for x in ['280','282','286','293','294','309','315','334','335']]};assert len(expected)==24 and {(Path(x['path']).name,x['rule'],x['line']) for x in st['rawFindings']}==expected
classified=[]
for x in st['rawFindings']:
 if Path(x['path']).name=='WebRequestTrace.java':
  if x['rule']=='AvoidUsingVolatile':reason='Immutable Optional<TopBar> snapshot requires servlet dispatch publication visibility; single read/write, no compound volatile state. Atomic flags own independent CAS.'
  elif x['rule']=='CloseResource':reason='businessIdentifiers borrows CURRENT.get scope. It must notclose caller-owned lexical scope; enter/owner finally owns close.'
  elif x['rule']=='CompareObjectsWithEquals':reason='Thread owner and active Scope must be same object identity; logical equality would weaken lexical owner/order invariant.'
  else:reason='Only records Thread.currentThread identity and compares it; no thread creation/start/server worker inside product.'
 elif x['rule']=='UseProperClassLoader':reason='StandaloneJUnit Model interface Proxy exact declaring SDKloader, not J2EE/container applicationloader.'
 elif x['rule']=='CloseResource':reason='OwnedJUnit executor explicitlyfinallyshutdownNow/actualawait10 asserted; TWR wouldreintroduceunboundedclose.'
 else:reason='StandaloneJUnit private worker fixtures, Future5/10 andfinallyactualawait10; no server/DB/native threads or inheritable scope.'
 classified.append(dict(**x,disposition='NOT_APPLICABLE_EXPLICIT_CONTRACT_CONTEXT_NO_SUPPRESSION',reason=reason))
wholeProof={}
for p in m['apiTestSources']:
 if Path(p).name in ['MenuAuditContractTest.java','WebRequestTraceTest.java']:
  assert sha(R/p)==hashlib.sha256(__import__('subprocess').check_output(['git','show','43d4489fda4018505827c8f125f93ef501c92e14:'+p])).hexdigest();wholeProof[p]=dict(sha256=sha(R/p),wholeBodyReviewed=True,allOriginalAssertionsUnchanged=True)
assert len(wholeProof)==2


for manifest,stages in [(pp,m['stages']),(sp,st['stages'])]:
 for label,v in stages.items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(manifest.parent/(label+'.'+stream))==v[stream+'Sha256']
assert set(m['mainClassHashes'])=={n.replace('.','/')+'.class' for n in st['spotbugs']['classStats']}
style=B/'evidence/PG22122-current7aed-lineage-style-v1/manifest.json';ms=ld(style);assert ms['actualExit']==ms['applicableViolations']==ms['unclassified']==ms['checkstyle']==0;arts=style.parent/'artifacts.json';assert sha(arts)==ms['files']['artifacts.json'];rows={x['path']:x for x in ld(arts)}
for p in m['apiMainSources']:
 if Path(p).name not in ['WebRequestTrace.java','WebRequestContext.java','CaddyClientAddressResolver.java','CaddyTransportContextFilter.java']:assert rows[p]['sha256']==m['inputHashes'][p]
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(n.endswith('/'+h+'.class') for n in m['physicalClassHashes'] for h in held);assert not any(any(x in (R/p).read_text() for x in held+['@BeforeAll','@TempDir','DriverManager','DataSource','ProcessBuilder']) for p in m['apiTestSources']);normal=ld(B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json')
for p in m['apiTestSources']:
 if Path(p).name not in ['WebRequestTraceFatalContractTest.java']:assert m['inputHashes'][p]==hashlib.sha256(__import__('subprocess').check_output(['git','show','43d4489fda4018505827c8f125f93ef501c92e14:'+p])).hexdigest()
O.mkdir();v=dict(actualExit=0,inputHashes=m['inputHashes'],prepare=ref(pp),testAndChangedMainStatic=ref(sp),unchangedMainStyle=ref(style),wholeCurrentFixtures=wholeProof,threePrivateWorkersAlreadyFinite=True,classified=classified,expectedTests=24,fullPhysicalClasses=199,newDefinitions=5,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,pmdRawFindings=24,manualSuppressionAdded=False,actualBackendOrHeldClassActions=0,heldFixturesExtractedOrRewritten=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,fullReportExpectedPartial=True,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'))))
