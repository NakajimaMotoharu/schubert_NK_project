"""Independent full unchanged root rules after preliminary style; exact7fresh/3cached Main closure."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as ET,zipfile
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg27922-question-pure18-normal-v1';O=B/'evidence/PG27926-question-pure18-preflight-v1';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();pp=B/'evidence/PG27922-question-pure18-normal-v1/manifest.json';m=ld(pp);assert m['actualExit']==0 and m['expectedTests']==18 and len(m['selectedClasses'])==2 and m['MainSourceSubsetCount']==7
for p,h in m['inputHashes'].items():assert sha(R/p)==h
for p,h in m['dependencies'].items():assert sha(Path(p))==h
for folder,key in [('component','physicalClassHashes'),('target/classes','mainClassHashes'),('test-classes','testClassHashes')]:assert m[key]=={str(p.relative_to(W/folder)):sha(p) for p in (W/folder).rglob('*.class')}
assert len(m['physicalClassHashes'])==186 and len(m['mainClassHashes'])==7
cp=R/m['reusedRootPrepare']['path'];cache=ld(cp);assert sha(cp)==m['reusedRootPrepare']['sha256'];cf=R/m['reusedRootPreflight']['path'];cachedStatic=ld(cf);assert sha(cf)==m['reusedRootPreflight']['sha256'] and cachedStatic['actualExit']==0 and all(cachedStatic[k]==0 for k in ['staticApplicable','unclassified','processingErrors','checkstyle','spotbugs'])
names=['form/UserCreateForm','view/TopBarViewModel','session/SessionPrincipal'];cache3={'dev/codex/schubert/nk/web/'+n+'.class':cache['mainClassHashes']['dev/codex/schubert/nk/web/'+n+'.class'] for n in names}
for n in names:
 p='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/'+n+'.java';assert sha(R/p)==cache['inputHashes'][p]==m['inputHashes'][p]
with zipfile.ZipFile(W/'cached-user-pure3.jar') as archive:
 assert set(archive.namelist())==set(cache3)
 for n,h in cache3.items():assert hashlib.sha256(archive.read(n)).hexdigest()==h==m['physicalClassHashes'][n]
package='dev/codex/schubert/nk/web/session/package-info.class';assert m['mainClassHashes'][package]==cache['mainClassHashes'][package]
style=R/m['preliminaryStyle']['path'];pre=ld(style);assert sha(style)==m['preliminaryStyle']['sha256'] and pre['preliminaryOnly'] and not pre['fullQualityGateSatisfied'] and pre['expandedOracleTokensIdentical'] and pre['wrongLiteralNegativeRejected']
assert all(pre['inputHashes'][p]==m['inputHashes'][p] for p in m['apiTestSources'])
ns='http://maven.apache.org/POM/4.0.0';ET.register_namespace('',ns);tag=lambda n:'{'+ns+'}'+n;compiler=next(p for p in ET.parse(R/'pom.xml').getroot().findall('.//'+tag('plugin')) if p.findtext(tag('artifactId'))=='maven-compiler-plugin');copied=ET.parse(W/'pom.xml').getroot().find('.//'+tag('plugin'));assert ET.tostring(compiler)==ET.tostring(copied) and sha(W/'pom.xml')==m['subsetPomSha256'];assert hashlib.sha256(ET.tostring(copied)).hexdigest()==cache['rootCompilerSha256'] and '-Xep:NullAway:ERROR' in ET.tostring(copied).decode() and '-Werror' in ET.tostring(copied).decode()
sp=B/'evidence/PG27924-question-pure18-static-v1/manifest.json';st=ld(sp);assert st['actualExit']==0 and st['inputHashes']==m['inputHashes'] and not st['processingErrors'] and st['checkstyleFindings']==0 and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors']);assert st['freshPmdSourcePaths']==m['apiMainSources']+m['apiTestSources'];assert '--rulesets' in st['stages']['pmd']['command'] and str(R/'tools/quality/static/pmd.xml') in st['stages']['pmd']['command']
assert sha(R/'tools/quality/static/pmd.xml')==hashlib.sha256(subprocess.check_output(['git','show','1634e3884a7b645f50b3552642ed4a1844736ab5:tools/quality/static/pmd.xml'])).hexdigest()
test=R/next(p for p in m['apiTestSources'] if p.endswith('/QuestionSubmitFormTest.java'));lines=test.read_text().splitlines();anchors={'pool':'var executor = Executors.newFixedThreadPool(8);','submit':'.submit(','stop':'executor.shutdownNow();','join':'assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));'};positions={}
for k,t in anchors.items():
 found=[str(i+1) for i,line in enumerate(lines) if t in line];assert len(found)==1;positions[k]=found[0]
expected={('CloseResource',positions['pool']),*[('DoNotUseThreads',x) for x in positions.values()]};assert len(st['rawFindings'])==5 and {(x['rule'],x['line']) for x in st['rawFindings']}==expected and all(Path(x['path']).name=='QuestionSubmitFormTest.java' for x in st['rawFindings']);classified=[dict(**x,disposition='NOT_APPLICABLE_OWNED_STANDALONE_JUNIT_NO_SUPPRESSION',reason='One owned fixed8worker pool/100tasks, every Future.get30/finallyshutdownNow/assertawait10; no application/backend threads') for x in st['rawFindings']]
for manifest,stages in [(pp,m['stages']),(sp,st['stages'])]:
 for label,v in stages.items():
  assert v['actualExit']==(4 if label=='pmd' else 0) and not v['timedOut']
  for stream in ['stdout','stderr']:assert sha(manifest.parent/(label+'.'+stream))==v[stream+'Sha256']
assert set(m['mainClassHashes'])=={n.replace('.','/')+'.class' for n in st['spotbugs']['classStats']}
assert not any(n.endswith('/'+h+'.class') for n in m['physicalClassHashes'] for h in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
O.mkdir();v=dict(actualExit=0,inputHashes=m['inputHashes'],prepare=ref(pp),static=ref(sp),preliminaryStyle=ref(style),fullRootRulesCheckedAfterCompile=True,rootRulesUnchangedSha256=sha(R/'tools/quality/static/pmd.xml'),reusedRootPrepare=ref(cp),reusedRootPreflight=ref(cf),reusedPhysicalClasses=3,freshMain7IncludesSamePackageInfo=True,expectedTests=18,newDefinitions=0,fullPhysicalClasses=186,rootCompilerUnchanged=True,staticApplicable=0,unclassified=0,processingErrors=0,checkstyle=0,spotbugs=0,pmdRawFindings=5,classified=classified,independentSourceAnchors=positions,manualSuppressionAdded=False,actualBackendOrHeldClassActions=0,heldFixturesExtractedOrRewritten=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,fullReportExpectedPartial=True,verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,manifest=ref(O/'manifest.json'))))
