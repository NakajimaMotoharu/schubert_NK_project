"""Whole public DTO5 only; exact API12/protocol5 payload and static/source binding admission."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg27326-public-command-value5-profile-v1';O=B/'evidence/PG27327-public-command-value5-preflight-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();pp=B/'evidence/PG27326-public-command-value5-profile-v1/manifest.json';m=load(pp);assert m['actualExit']==0 and m['expectedTests']==5 and m['newDefinitions']==5 and m['publicDtoConstructorsOnly'] and not m['privateOpaqueResultOrSnapshotConstructed']
assert all(sha(R/p)==h for p,h in m['inputHashes'].items())
for folder,key in [('component','physicalClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
assert len(m['physicalClassHashes'])==17 and len(m['apiExactReadClassEntries'])==12 and len(m['protoExactReadClassEntries'])==5 and m['apiWholeJarHashedOrOtherEntryPayloadRead'] is False
normal=load(R/m['normalMain']['path']);assert sha(R/m['normalMain']['path'])==m['normalMain']['sha256'] and normal['actualExit']==0 and normal['testsExecuted'] is False
for p in m['apiMainSources']+m['protoMainSources']:assert normal['begin']['inputHashes'][p]==m['inputHashes'][p]
for p in m['apiExactReadClassEntries']:assert normal['normalPhysicalClassHashes']['api:'+p]==m['physicalClassHashes'][p]
for p in m['protoExactReadClassEntries']:assert normal['normalPhysicalClassHashes']['protocol:'+p]==m['physicalClassHashes'][p]
for p,h in m['dependencies'].items():assert sha(Path(p))==h
sp=B/'evidence/PG27328-public-command-value5-static-v1/manifest.json';st=load(sp);assert st['inputHashes']==m['inputHashes'] and st['actualExit']==0 and not st['rawFindings'] and not st['processingErrors'] and st['checkstyleFindings']==0
for manifest,stages in [(pp,m['stages']),(sp,st['stages'])]:
 for label,v in stages.items():
  assert v['actualExit']==0 and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(manifest.parent/(label+'.'+stream))==v[stream+'Sha256']
ns=B/'evidence/PG22106-api-stop-static-independent-input-v1/six-static.json';v=load(ns);assert sha(ns)=='0580a14592d3fc00820183034c584208e45b002802d2e3e173b5f752c7cf19f2'
for module,names in [('api',m['apiExactReadClassEntries']),('protocol',m['protoExactReadClassEntries'])]:
 sb=Path(v['reports'][module]['path']);assert sha(sb)==v['reports'][module]['sha256'];rt=ET.parse(sb).getroot();assert not any(rt.findall('.//'+tag) for tag in ['BugInstance','MissingClass','Error']);stats={x.get('class') for x in rt.findall('.//ClassStats')};assert {x[:-6].replace('/','.') for x in names if not x.endswith('package-info.class')}<=stats
style=B/'evidence/PG22122-current7aed-lineage-style-v1/manifest.json';ms=load(style);assert ms['actualExit']==ms['applicableViolations']==ms['unclassified']==ms['checkstyle']==0;arts=style.parent/'artifacts.json';assert sha(arts)==ms['files']['artifacts.json'];rows={x['path']:x for x in load(arts)}
for p in m['apiMainSources']+m['protoMainSources']:assert rows[p]['sha256']==m['inputHashes'][p]
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(x.endswith('/'+h+'.class') for x in m['physicalClassHashes'] for h in held)
for p in m['apiTestSources']:assert not any(x in (R/p).read_text() for x in held+['Snapshot','setAccessible','getDeclaredConstructor','QuestionCommandServiceTest.','@BeforeAll','@TempDir','DataSource','DriverManager','ProcessBuilder','.cancel(','.logicalDelete(','.apply('])
scan=B/'evidence/PG27322-question-command-contract-v1/dto-reference-scan.json';s=load(scan)
for p,h in s['matchingPublicSourceFiles'].items():assert sha(R/p)==h
O.mkdir();out=dict(actualExit=0,inputHashes=m['inputHashes'],prepare=ref(pp),normalStatic=ref(ns),mainStyle=ref(style),testStyle=ref(sp),originalWholeDbFixtureSourceUnchanged=ref(scan),expectedTests=5,fullPhysicalClasses=17,newDefinitions=5,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,pmdRawFindings=0,manualSuppressionAdded=False,actualBackendOrHeldClassActions=0,heldFixturesExtractedOrRewritten=False,privateOpaqueResultOrSnapshotConstructed=False,publicDtoOnlyNormalPtNotHeldPtReplacement=True,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,fullReportExpectedPartial=True,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'))))
