from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';CW=R.parent/'pgpt-runs/PG379/pg27390-session29-normal-v1';W=R.parent/'pgpt-runs/PG379/pg27414-session-v2-12-profile-v1';O=B/'evidence/PG27418-session-v2-12-preflight-v1';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();pp=B/'evidence/PG27414-session-v2-12-profile-v1/manifest.json';m=ld(pp);assert m['actualExit']==0 and m['expectedTests']==12 and len(m['selectedClasses'])==2
for p,h in m['inputHashes'].items():assert sha(R/p)==h
for p,h in m['dependencies'].items():assert sha(Path(p))==h
for root,key in [(CW/'component','physicalClassHashes'),(W/'test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(root)):sha(p) for p in root.rglob('*.class')}
assert len(m['physicalClassHashes'])==192
prior=B/'evidence/PG27398-session29-preflight-v1/manifest.json';pf=ld(prior);assert pf['actualExit']==0 and all(pf[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs']);oldNormal=ld(R/m['currentNormalMain']['path']);assert sha(R/m['currentNormalMain']['path'])==m['currentNormalMain']['sha256'] and oldNormal['actualExit']==0
for p,h in m['inputHashes'].items():
 if p!=m['apiTestSources'][1]:assert oldNormal['inputHashes'][p]==h==pf['inputHashes'][p]
assert oldNormal['physicalClassHashes']==m['physicalClassHashes'];n='dev/codex/schubert/nk/web/session/SessionAttributeCodecTest.class';assert m['testClassHashes'][n]==oldNormal['testClassHashes'][n]
fixPath=B/'evidence/PG27412-session-v2-finite-source-v1/manifest.json';fx=ld(fixPath);assert fx['actualExit']==0 and fx['originalAllAssertionsInverseExact'] and sha(R/fx['path'])==fx['newSha256'];s=(R/fx['path']).read_text();inverse=s
for pair in reversed(fx['changes']):assert inverse.count(pair['after'])==1;inverse=inverse.replace(pair['after'],pair['before'])
assert hashlib.sha256(inverse.encode()).hexdigest()==fx['oldSha256']
sp=B/'evidence/PG27416-session-v2-12-static-v1/manifest.json';st=ld(sp);assert st['actualExit']==0 and st['inputHashes']==m['inputHashes'] and not st['processingErrors'] and st['checkstyleFindings']==0;expected={('CloseResource','167'),('DoNotThrowExceptionInFinally','179'),*[('DoNotUseThreads',x) for x in ['167','172','180','181']]};assert {(x['rule'],x['line']) for x in st['rawFindings']}==expected
classified=[]
for x in st['rawFindings']:
 reason={'CloseResource':'OwnedexecutorfinallyshutdownNow/await10, TWRclosewouldrestoreunboundedjoin.','DoNotThrowExceptionInFinally':'FailuretojoinownJUnitworker mustfailtest, neverpresumePASS/resourcesfree.','DoNotUseThreads':'StandaloneJUnit owned10workers/Future20/finallyawait10, notJ2EE/container/serverthread.'}[x['rule']];classified.append(dict(**x,disposition='NOT_APPLICABLE_EXPLICIT_JUNIT_CONTEXT_NO_SUPPRESSION',reason=reason))
for manifest,stages in [(pp,m['stages']),(sp,st['stages'])]:
 for label,v in stages.items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(manifest.parent/(label+'.'+stream))==v[stream+'Sha256']
held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'];assert not any(n.endswith('/'+h+'.class') for n in m['physicalClassHashes'] for h in held)
O.mkdir();v=dict(actualExit=0,inputHashes=m['inputHashes'],prepare=ref(pp),exactUnchangedMainAndJsonStyle=ref(prior),finiteOriginalAssertions=ref(fixPath),newV2TestStyle=ref(sp),classified=classified,expectedTests=12,newDefinitions=0,fullPhysicalClasses=192,MainRebuilt=False,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,pmdRawFindings=6,manualSuppressionAdded=False,actualBackendOrHeldClassActions=0,heldFixturesExtractedOrRewritten=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,fullReportExpectedPartial=True,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'))))
