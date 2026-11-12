"""Exact cache/root/settings and per-finding independent ordinary-test applicability."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg27796-log-whole40-normal-v1';O=B/'evidence/PG27800-log-whole40-preflight-v1';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();pp=B/'evidence/PG27796-log-whole40-normal-v1/manifest.json';m=ld(pp);assert m['actualExit']==0 and m['expectedTests']==40 and len(m['selectedClasses'])==5 and m['MainSourceSubsetCount']==4
for p,h in m['inputHashes'].items():assert sha(R/p)==h
for p,h in m['dependencies'].items():assert sha(Path(p))==h
for folder,key in [('component','physicalClassHashes'),('target/classes','mainClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
assert len(m['physicalClassHashes'])==220 and len(m['mainClassHashes'])==9
prior=R/m['reusedRootTwenty']['path'];old=ld(prior);assert sha(prior)==m['reusedRootTwenty']['sha256'];oldW=R.parent/'pgpt-runs/PG379/pg27600-trace-menu24-normal-v1';assert old['mainClassHashes']=={str(p.relative_to(oldW/'target/classes')):sha(p) for p in (oldW/'target/classes').rglob('*.class')}
for p in old['apiMainSources']:assert old['inputHashes'][p]==m['inputHashes'][p]
musicPath=R/m['reusedMusicNine']['path'];music=ld(musicPath);musicW=R.parent/'pgpt-runs/PG379/pg27742-music-whole14-normal-v1';assert sha(musicPath)==m['reusedMusicNine']['sha256'];assert music['mainClassHashes']=={str(p.relative_to(musicW/'target/classes')):sha(p) for p in (musicW/'target/classes').rglob('*.class')}
for p in music['apiMainSources']:assert music['inputHashes'][p]==m['inputHashes'][p]
musicPf=B/'evidence/PG27746-music-whole14-preflight-v1/manifest.json';mp=ld(musicPf);assert mp['actualExit']==0 and mp['prepare']['sha256']==sha(musicPath) and all(mp[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs'])
priorPf=B/'evidence/PG27608-trace-menu24-preflight-v1/manifest.json';pf=ld(priorPf);assert pf['actualExit']==0 and pf['prepare']['sha256']==sha(prior) and all(pf[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs'])
ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;original=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');copied=ET.parse(W/'pom.xml').getroot().find('.//'+tag('plugin'));assert ET.tostring(original)==ET.tostring(copied) and sha(W/'pom.xml')==m['subsetPomSha256'];assert '-Xep:NullAway:ERROR' in ET.tostring(copied).decode() and '-Werror' in ET.tostring(copied).decode()
sp=B/'evidence/PG27798-log-whole40-static-v1/manifest.json';st=ld(sp);assert st['actualExit']==0 and st['inputHashes']==m['inputHashes'] and not st['processingErrors'] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
expected=set()
for name,close,threads in [('LogSearchFormTest.java','279',['279','285','303','304']),('LogSearchResultsViewModelTest.java','332',['332','338','352','353']),('LogSearchViewModelTest.java','357',['357','363','385','386']),('LogSearchTemplateTest.java','445',['445','451','474','475']),('PageViewModelTest.java','122',['122','127','131','132'])]:
 expected.add((name,'CloseResource',close));expected.update((name,'DoNotUseThreads',x) for x in threads)
assert len(st['rawFindings'])==25 and {(Path(x['path']).name,x['rule'],x['line']) for x in st['rawFindings']}==expected
classified=[]
for x in st['rawFindings']:
 reason='Standalone JUnit privately owns fixed8workers/64or100tasks. OriginalFuture.get10 and finallyshutdownNow+assert awaitTermination10; replacing with ExecutorService.close would reintroduce unbounded ownership.' if x['rule']=='CloseResource' else 'Standalone host JUnit owned workers, not J2EE business threads; every worker uses immutable DTO/public synthetic fixture, original bounded Future10 and finallyshutdown/await10 retained.'
 classified.append(dict(**x,disposition='NOT_APPLICABLE_EXPLICIT_ORDINARY_TEST_CONTEXT_NO_SUPPRESSION',reason=reason))
for manifest,stages in [(pp,m['stages']),(sp,st['stages'])]:
 for label,v in stages.items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(manifest.parent/(label+'.'+stream))==v[stream+'Sha256']
assert set(m['mainClassHashes'])=={n.replace('.','/')+'.class' for n in st['spotbugs']['classStats']}
for p in m['resourceSources']:
 for base in [W/'resources',W/'web-fixture/src/main/resources']:assert sha(base/p.split('/src/main/resources/')[1])==m['inputHashes'][p]
assert not any(n.endswith('/'+h+'.class') for n in m['physicalClassHashes'] for h in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
O.mkdir();v=dict(actualExit=0,inputHashes=m['inputHashes'],prepare=ref(pp),freshNineMainAndWholeTwoTestStatic=ref(sp),reusedRootTwenty=ref(prior),reusedRootIndependentPreflight=ref(priorPf),reusedMusicNine=ref(musicPath),reusedMusicIndependentPreflight=ref(musicPf),classified=classified,expectedTests=40,newDefinitions=0,fullPhysicalClasses=220,rootCompilerUnchanged=True,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,pmdRawFindings=25,manualSuppressionAdded=False,actualBackendOrHeldClassActions=0,heldFixturesExtractedOrRewritten=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,fullReportExpectedPartial=True,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'))))
