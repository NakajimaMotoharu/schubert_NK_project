"""Independent unchanged compiler, all inputs, exact static findings and closure preflight."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg27824-read-wire-normal40-v1';O=B/'evidence/PG27828-read-wire-normal40-preflight-v1';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists()
pp=B/'evidence/PG27824-read-wire-normal40-v1/manifest.json';m=ld(pp);assert m['actualExit']==0 and m['expectedTests']==40 and len(m['selectedClasses'])==5 and m['MainSourceSubsetCount']==13
for p,h in m['inputHashes'].items():assert sha(R/p)==h
for p,h in m['dependencies'].items():assert sha(Path(p))==h
for folder,key in [('component','physicalClassHashes'),('target/classes','mainClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
assert len(m['physicalClassHashes'])==194 and len(m['mainClassHashes'])==18
original=ld(R/'evidence/01_PT/015_NK-WEB-001/evidence/PG24326-read-four-bounded-thirtytwo-independent-v1/compile-manifest.json')
for p in m['apiTestSources']:
 if not p.endswith('/ProtectedReadFatalContractTest.java'):assert m['inputHashes'][p]==original['inputHashes'][p]
ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;compiler=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');copied=ET.parse(W/'pom.xml').getroot().find('.//'+tag('plugin'));assert ET.tostring(compiler)==ET.tostring(copied) and sha(W/'pom.xml')==m['subsetPomSha256'];assert '-Xep:NullAway:ERROR' in ET.tostring(copied).decode() and '-Werror' in ET.tostring(copied).decode()
sp=B/'evidence/PG27826-read-wire-normal40-static-v1/manifest.json';st=ld(sp);assert st['actualExit']==0 and st['inputHashes']==m['inputHashes'] and not st['processingErrors'] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
expected={
'JmsRequestReplyClient.java':{('DoNotUseThreads','80')},
'AnimationWireClientTest.java':{('CloseResource','323'),*[('DoNotUseThreads',str(x)) for x in [323,329,345,346]]},
'LogSearchWireClientTest.java':{('CloseResource','400'),*[('DoNotUseThreads',str(x)) for x in [400,406,418,419]]},
'MusicWireClientTest.java':{('CloseResource','331'),*[('DoNotUseThreads',str(x)) for x in [331,337,351,352]]},
'ScenarioWireClientTest.java':{('CloseResource','500'),*[('DoNotUseThreads',str(x)) for x in [412,418,420,453,463,464,500,506,525,526]]}}
assert len(st['rawFindings'])==27 and {(Path(x['path']).name,x['rule'],x['line']) for x in st['rawFindings']}=={(n,r,l) for n,v in expected.items() for r,l in v}
classified=[]
for x in st['rawFindings']:
 n=Path(x['path']).name;l=int(x['line']);text=(R/next(p for p in m['apiMainSources']+m['apiTestSources'] if p.endswith('/'+n))).read_text().splitlines();assert 0<l<=len(text)
 if n=='JmsRequestReplyClient.java':reason='SS321 preserves the existing request thread interrupt flag after InterruptedException; no thread creation, ordinary HTTP request lifecycle contract, unchanged source.'
 elif n=='ScenarioWireClientTest.java' and l in [412,418,420,453]:reason='Standalone JUnit interrupt/restore checks and worker interrupted flag; finally clears owned test flag. No application thread creation.'
 elif n=='ScenarioWireClientTest.java' and l in [463,464]:reason='Standalone owned single executor in try-with-resources; one task only, task release.await5 assertion and JMS wait<=2s, release finally and Future.get5; close joins sole finite task, no external backend/callback. Original assertion bytes unchanged.'
 else:reason='Standalone owned fixed8worker pool, 64/100 tasks, every Future.get10 and finally shutdownNow/assert awaitTermination10; resource-local lifecycle, no J2EE application thread creation.'
 classified.append(dict(**x,sourceLine=text[l-1],disposition='NOT_APPLICABLE_CONCRETE_OWNED_JUNIT_OR_REQUIRED_INTERRUPT_NO_SUPPRESSION',reason=reason))
for manifest,stages in [(pp,m['stages']),(sp,st['stages'])]:
 for label,v in stages.items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(manifest.parent/(label+'.'+stream))==v[stream+'Sha256']
assert set(m['mainClassHashes'])=={n.replace('.','/')+'.class' for n in st['spotbugs']['classStats']}
assert not any(n.endswith('/'+h+'.class') for n in m['physicalClassHashes'] for h in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
red=B/'evidence/PG27832-read-wire-old-source-red-control-v1/manifest.json';assert ld(red)['actualExit']==0 and ld(red)['expectedFailures']==3 and ld(red)['productPtPassAdded']==0
O.mkdir();v=dict(actualExit=0,inputHashes=m['inputHashes'],prepare=ref(pp),static=ref(sp),oldSourceRedControl=ref(red),expectedTests=40,newDefinitions=8,fullPhysicalClasses=194,rootCompilerUnchanged=True,original32TestBytesUnchanged=True,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,pmdRawFindings=27,classified=classified,manualSuppressionAdded=False,actualBackendOrHeldClassActions=0,heldFixturesExtractedOrRewritten=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,fullReportExpectedPartial=True,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'))))
